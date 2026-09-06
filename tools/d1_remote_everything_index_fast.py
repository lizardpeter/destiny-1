#!/usr/bin/env python3
"""Fast, fail-closed launcher for the D1 archive-wide everything index.

``d1_remote_everything_index.py`` normally discovers every physical package member
by walking the split TAR. The already-published archive-wide Activity index contains
the exact same physical location catalog. Repeating the TAR walk is unnecessary
when (and only when) that catalog was built from the exact same ``packages.txt``.

This wrapper validates:
  * the location index has the expected Activity-index schema/status;
  * its package-list SHA-256 equals the supplied current package list;
  * its flattened package-family member-name set equals the package-list member set;
  * every member has exact header/data offsets and physical size;
  * header_offset + 512 == data_offset for every ordinary TAR member.

It then substitutes only ``SplitHttpTar.find``. All package headers, entry tables and
named-tag tables are still reread and cryptographically validated by the underlying
everything indexer. Thus the prior index is used only as a byte-location accelerator,
never as semantic/classification evidence.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import d1_remote_everything_index as core


def _arg_value(flag: str) -> str:
    try:
        i=sys.argv.index(flag)
    except ValueError:
        raise SystemExit(f'{flag} is required by fast wrapper')
    if i+1>=len(sys.argv):raise SystemExit(f'{flag} has no value')
    return sys.argv[i+1]


def _package_names(path:Path)->set[str]:
    return {Path(x.strip()).name for x in path.read_text(errors='replace').splitlines()
            if x.strip() and core.identity(Path(x.strip()).name) is not None}


def main()->int:
    loc_path=Path(_arg_value('--location-index'))
    pkg_path=Path(_arg_value('--package-list'))
    # Remove wrapper-only argument before delegating to core argparse.
    i=sys.argv.index('--location-index');del sys.argv[i:i+2]

    d=json.loads(loc_path.read_text())
    if int(d.get('schema_version',0))!=2 or d.get('status')!='D1_REMOTE_ACTIVITY_INDEX_COMPLETE':
        raise SystemExit(f'{loc_path}: not a complete v2 D1 Activity index')
    source=d.get('source') or {}
    expected=str(source.get('package_list_sha256') or '').lower()
    actual=hashlib.sha256(pkg_path.read_bytes()).hexdigest()
    if expected!=actual:
        raise SystemExit(f'location-index packages.txt SHA mismatch: {expected} != {actual}')

    wanted=_package_names(pkg_path)
    locations={}
    duplicate=[]
    malformed=[]
    families=d.get('package_families') or {}
    for pkg,rows in families.items():
        for row in rows:
            name=Path(str(row.get('name',''))).name
            try:
                ho=int(row['tar_header_offset']);do=int(row['data_offset']);size=int(row['size'])
            except Exception as ex:
                malformed.append((pkg,name,repr(ex)));continue
            if not name or do!=ho+512 or size<0:
                malformed.append((pkg,name,ho,do,size));continue
            if name in locations:
                duplicate.append(name);continue
            locations[name]={'archive_name':name,'header_offset':ho,'data_offset':do,'size':size}
    if malformed:raise SystemExit(f'malformed location rows: {malformed[:10]}')
    if duplicate:raise SystemExit(f'duplicate physical package names in location index: {duplicate[:10]}')
    have=set(locations)
    missing=sorted(wanted-have);extra=sorted(have-wanted)
    if missing or extra:
        raise SystemExit(f'location-index member-set mismatch: missing={missing[:20]} extra={extra[:20]}')
    if len(have)!=int(d.get('physical_member_count',-1)):
        raise SystemExit(f'location count {len(have)} != indexed physical_member_count {d.get("physical_member_count")}')

    def exact_find(self,wanted_basenames:set[str],start_offset:int=0):
        if start_offset:
            raise ValueError('fast exact-location mode does not accept nonzero start_offset')
        missing2=sorted(set(wanted_basenames)-have)
        if missing2:raise KeyError(f'find requested names absent from exact location index: {missing2[:20]}')
        return {name:locations[name] for name in wanted_basenames},0

    core.SplitHttpTar.find=exact_find
    print(json.dumps({
        'status':'D1_EVERYTHING_EXACT_LOCATION_INDEX_ACCEPTED',
        'location_index':str(loc_path),'packages_txt_sha256':actual,
        'physical_members':len(have),'package_families':len(families),
        'tar_header_walk_skipped':True,
        'policy':'Physical offsets reused only after exact package-list SHA/member-set validation; underlying indexer rereads/validates Tiger metadata tables.'
    },indent=2),flush=True)
    return core.main()


if __name__=='__main__':raise SystemExit(main())
