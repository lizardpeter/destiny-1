#!/usr/bin/env python3
"""Export exact D1 PS4 ROI textures by Texture TagHash.

This is the dependency-resolution counterpart to d1_world_material_texture_export.py.
It accepts any set of Texture TagHashes and a current package corpus, follows each
texture's exact resource chain, deswizzles the PS4 surface, and writes DDS/PNG.
No material-slot semantics are inferred.
"""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import d1_tower_map_schema_validate_v5 as v5
from d1_world_material_texture_export import export_texture,norm


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--snapshot',type=Path,action='append',required=True)
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--texture',action='append',default=[])
    ap.add_argument('--texture-json',type=Path,help='JSON with unresolved[] rows containing texture')
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()

    tags={norm(x) for x in a.texture}
    if a.texture_json:
        d=json.loads(a.texture_json.read_text())
        for x in d.get('unresolved',[]): tags.add(norm(x['texture']))
    if not tags: raise SystemExit('no texture tags supplied')

    a.out.mkdir(parents=True,exist_ok=True)
    texdir=a.out/'textures';texdir.mkdir(exist_ok=True)
    c=v5.v3.base.Corpus([p.resolve() for p in a.snapshot],a.runtime.resolve())
    rows={}
    for i,h in enumerate(sorted(tags),1):
        print(f'TEXTURE {i}/{len(tags)} {h}',flush=True)
        rows[h]=export_texture(c,h,texdir)
    failed={h:r for h,r in rows.items() if r.get('error')}
    rep={
      'status':'D1_TEXTURE_TAG_EXPORT_COMPLETE' if not failed else 'D1_TEXTURE_TAG_EXPORT_PARTIAL',
      'requested':len(tags),'resolved':len(tags)-len(failed),'failed':len(failed),
      'textures':rows,'failed_textures':failed,
      'policy':'Exact Texture TagHash/resource chain export only; no material semantic inference.'
    }
    (a.out/'texture_tag_export.json').write_text(json.dumps(rep,indent=2)+'\n')
    print(json.dumps({k:rep[k] for k in ('status','requested','resolved','failed')},indent=2))
    if failed:
        print('FAILED',[(h,r.get('error')) for h,r in failed.items()])
    return 0 if not failed else 2

if __name__=='__main__':raise SystemExit(main())
