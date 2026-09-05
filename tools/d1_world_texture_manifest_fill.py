#!/usr/bin/env python3
"""Fill unresolved textures in an existing exact D1 world material manifest.

This is an incremental counterpart to the full census. It preserves every exact
material/shader/t# binding already recorded, re-resolves only texture rows that
currently carry an error, and writes newly decoded images into the supplied
texture directory. It is useful when dependency closure adds one or more package
families after a large texture set has already been exported.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import d1_tower_map_schema_validate_v5 as v5
from d1_world_material_texture_export import export_texture, pkg_id_from_tag


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--snapshot',type=Path,action='append',required=True)
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--manifest',type=Path,required=True)
    ap.add_argument('--texture-dir',type=Path,required=True)
    ap.add_argument('--out-manifest',type=Path,required=True)
    a=ap.parse_args();a.texture_dir.mkdir(parents=True,exist_ok=True)

    d=json.loads(a.manifest.read_text())
    c=v5.v3.base.Corpus([p.resolve() for p in a.snapshot],a.runtime.resolve())
    targets=sorted(h for h,r in d.get('textures',{}).items() if r.get('error'))
    before=len(targets);rows=[]
    for i,h in enumerate(targets,1):
        print(f'FILL {i}/{len(targets)} {h}',flush=True)
        nr=export_texture(c,h,a.texture_dir)
        d['textures'][h]=nr;rows.append(nr)

    missing=[h for h,r in d['textures'].items() if r.get('error')]
    d['decoded_texture_tags']=sum(1 for r in d['textures'].values() if not r.get('error'))
    d['texture_errors']=len(missing)
    d['png_outputs']=sum(1 for r in d['textures'].values() if r.get('png'))+sum(len([f for f in r.get('faces',[]) if f.get('png')]) for r in d['textures'].values())
    missing_pkg=Counter(pkg_id_from_tag(h) for h in missing)
    d['missing_texture_package_ids']=dict(sorted((k,v) for k,v in missing_pkg.items() if k is not None))
    d['incremental_fill']={
        'attempted':before,'remaining':len(missing),'filled':before-len(missing),
        'policy':'Only previously unresolved texture rows were re-resolved; material/shader/t# bindings were preserved unchanged.',
    }
    a.out_manifest.parent.mkdir(parents=True,exist_ok=True);a.out_manifest.write_text(json.dumps(d,indent=2)+'\n')
    print(json.dumps({'attempted':before,'filled':before-len(missing),'remaining':len(missing),'decoded_texture_tags':d['decoded_texture_tags'],'png_outputs':d['png_outputs'],'missing_texture_package_ids':d['missing_texture_package_ids']},indent=2))
    return 0 if not missing else 2

if __name__=='__main__':raise SystemExit(main())
