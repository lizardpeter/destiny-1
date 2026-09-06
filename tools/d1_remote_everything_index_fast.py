#!/usr/bin/env python3
"""Fast, fail-closed launcher for the D1 archive-wide everything index.

The underlying indexer normally discovers every physical package member by walking
the split TAR. The published Activity index already contains the exact same ordinary
package-member locations. This wrapper reuses those positions only when the exact
packages.txt SHA and complete ordinary member set match.

It also carries one compatibility correction for the original v1 index schema: the
view alias ``references`` is a SQLite reserved keyword. The SQL text is corrected to
``reference_values`` at executescript time without changing any table/entry data.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import d1_remote_everything_index as core


def _arg_value(flag:str)->str:
    try:i=sys.argv.index(flag)
    except ValueError:raise SystemExit(f'{flag} is required by fast wrapper')
    if i+1>=len(sys.argv):raise SystemExit(f'{flag} has no value')
    return sys.argv[i+1]


def _package_names(path:Path)->set[str]:
    return {Path(x.strip()).name for x in path.read_text(errors='replace').splitlines()
            if x.strip() and core.identity(Path(x.strip()).name) is not None}


def _install_sqlite_reserved_alias_fix()->None:
    real_connect=core.sqlite3.connect
    class Proxy:
        def __init__(self,*args,**kwargs):self._db=real_connect(*args,**kwargs)
        def executescript(self,sql):
            old='GROUP_CONCAT(DISTINCT reference) references,'
            new='GROUP_CONCAT(DISTINCT reference) reference_values,'
            if old not in sql:raise RuntimeError('expected v1 reserved references alias not found; remove compatibility patch')
            return self._db.executescript(sql.replace(old,new))
        def __getattr__(self,name):return getattr(self._db,name)
    core.sqlite3.connect=lambda *args,**kwargs:Proxy(*args,**kwargs)


def main()->int:
    loc_path=Path(_arg_value('--location-index'));pkg_path=Path(_arg_value('--package-list'))
    i=sys.argv.index('--location-index');del sys.argv[i:i+2]

    d=json.loads(loc_path.read_text())
    if int(d.get('schema_version',0))!=2 or d.get('status')!='D1_REMOTE_ACTIVITY_INDEX_COMPLETE':
        raise SystemExit(f'{loc_path}: not a complete v2 D1 Activity index')
    expected=str((d.get('source') or {}).get('package_list_sha256') or '').lower()
    actual=hashlib.sha256(pkg_path.read_bytes()).hexdigest()
    if expected!=actual:raise SystemExit(f'location-index packages.txt SHA mismatch: {expected} != {actual}')

    wanted=_package_names(pkg_path);locations={};duplicate=[];malformed=[]
    families=d.get('package_families') or {}
    for pkg,rows in families.items():
        for row in rows:
            name=Path(str(row.get('name',''))).name
            try:ho=int(row['tar_header_offset']);do=int(row['data_offset']);size=int(row['size'])
            except Exception as ex:malformed.append((pkg,name,repr(ex)));continue
            if not name or do!=ho+512 or size<0:malformed.append((pkg,name,ho,do,size));continue
            if name in locations:duplicate.append(name);continue
            locations[name]={'archive_name':name,'header_offset':ho,'data_offset':do,'size':size}
    if malformed:raise SystemExit(f'malformed location rows: {malformed[:10]}')
    if duplicate:raise SystemExit(f'duplicate physical package names in location index: {duplicate[:10]}')
    have=set(locations);missing=sorted(wanted-have);extra=sorted(have-wanted)
    if missing or extra:raise SystemExit(f'location-index member-set mismatch: missing={missing[:20]} extra={extra[:20]}')
    if len(have)!=int(d.get('physical_member_count',-1)):
        raise SystemExit(f'location count {len(have)} != indexed physical_member_count {d.get("physical_member_count")}')

    def exact_find(self,wanted_basenames:set[str],start_offset:int=0):
        if start_offset:raise ValueError('fast exact-location mode does not accept nonzero start_offset')
        missing2=sorted(set(wanted_basenames)-have)
        if missing2:raise KeyError(f'find requested names absent from exact location index: {missing2[:20]}')
        return {name:locations[name] for name in wanted_basenames},0

    core.SplitHttpTar.find=exact_find
    _install_sqlite_reserved_alias_fix()
    print(json.dumps({
        'status':'D1_EVERYTHING_EXACT_LOCATION_INDEX_ACCEPTED','location_index':str(loc_path),
        'packages_txt_sha256':actual,'physical_members':len(have),'package_families':len(families),
        'tar_header_walk_skipped':True,'sqlite_v1_reserved_alias_fixed':True,
        'policy':'Physical offsets reused only after exact package-list SHA/member-set validation; underlying indexer rereads/validates Tiger metadata tables.'
    },indent=2),flush=True)
    return core.main()

if __name__=='__main__':raise SystemExit(main())
