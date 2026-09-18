#!/usr/bin/env python3
"""Fail-closed D1 PS4 texture exporter.

This is the production strict-chain entry point over d1_texture_export.py.  It
keeps the established byte/format export implementation but replaces the
legacy adjacency-based backing traversal with the source-closed resolver from
d1_texture_backing_chain_v1 before any export is attempted.

No semantic name is assigned to 65:1 or 5:1 here.
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import d1_texture_export as legacy
from d1_texture_backing_chain_v1 import resolve_texture_backing


def strict_follow_backing(global_by, header_entry):
    """Legacy-compatible adapter backed only by proven chain shapes."""
    first, backing, _mode = resolve_texture_backing(global_by, header_entry)
    return first, backing


def install_strict_chain_gate():
    """Install the gate used by legacy.export_reader's global lookup."""
    legacy.follow_backing = strict_follow_backing


def strict_manifest_violations(rep:dict)->list[str]:
    """Return fail-closed production violations for a completed legacy report."""
    out=[]
    missing=[str(x).upper() for x in rep.get('missing_requested') or []]
    if missing:
        out.append('missing_requested:'+','.join(sorted(missing)))
    for row in rep.get('textures') or []:
        h=str(row.get('header','UNKNOWN')).upper()
        if row.get('available') is False:
            out.append(f'{h}:header_unavailable')
            continue
        if row.get('error'):
            out.append(f"{h}:row_error:{row['error']}")
            continue
        n=int(row.get('array_size',1) or 1)
        if n==1:
            if not row.get('dds'):
                out.append(f'{h}:missing_dds')
        elif n==6:
            if len(row.get('face_dds') or [])!=6:
                out.append(f'{h}:incomplete_cube_dds')
        else:
            out.append(f'{h}:unsupported_array_size:{n}')
    return out


def export_reader(*args, **kwargs):
    install_strict_chain_gate()
    kwargs['strict_backing_size']=True
    rep=legacy.export_reader(*args, **kwargs)
    violations=strict_manifest_violations(rep)
    rep['schema']='d1_texture_export_v2/v1'
    rep['status']='D1_TEXTURE_EXPORT_V2_EXACT' if not violations else 'D1_TEXTURE_EXPORT_V2_REJECTED'
    rep['strict_chain_gate']='PROVEN_SHAPES_ONLY'
    rep['strict_backing_size']=True
    rep['violations']=violations
    # legacy.export_reader writes first; replace it with the authoritative v2
    # manifest so failure evidence remains durable for batch/CI consumers.
    outdir=kwargs.get('outdir')
    if outdir is None and len(args)>=2:
        outdir=args[1]
    if outdir is not None:
        Path(outdir).mkdir(parents=True,exist_ok=True)
        (Path(outdir)/'texture_manifest.json').write_text(json.dumps(rep,indent=2)+'\n')
    if violations:
        raise RuntimeError('strict texture export rejected: '+'; '.join(violations))
    return rep


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('pkg',type=Path)
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--dependency-pkg',type=Path,action='append',default=[])
    ap.add_argument('--tag-hash',action='append')
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    r=legacy.EntryReader(a.pkg,a.runtime)
    deps=[legacy.EntryReader(p,a.runtime) for p in a.dependency_pkg]
    rep=export_reader(r,a.out,tag_hashes=a.tag_hash,dependencies=deps)
    print(json.dumps({'package':rep['package'],
                      'logical_package_family':rep['logical_package_family'],
                      'dependencies':rep['dependency_packages'],
                      'texture_count':rep['texture_count'],
                      'missing_requested':rep['missing_requested']},indent=2))


if __name__=='__main__':
    main()
