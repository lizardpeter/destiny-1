#!/usr/bin/env python3
"""Export D1 world material structure without decoding texture payloads.

This is the lightweight companion to d1_world_material_texture_export.py for
shader emulation work. It resolves only the selected Material records and keeps
exact shader, t#, sampler, TFX and VS/PS Vector4Container references. That makes
material constant recovery cheap and repeatable without re-decoding every image.
"""
from __future__ import annotations

import argparse, json, sys
from collections import Counter
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import d1_tower_map_schema_validate_v5 as v5
from d1_material_decode import parse_material

MAT_CLASS='80801AD7'
NULLS={'FFFFFFFF','00000000'}

def norm(h):return str(h).upper().removeprefix('0X').zfill(8)


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--snapshot',type=Path,action='append',required=True)
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--visual-json',type=Path,action='append',required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    visible=set()
    for p in a.visual_json:
        d=json.loads(p.read_text())
        for h,r in (d.get('materials') or {}).items():
            if r.get('visual'):visible.add(norm(h))
    c=v5.v3.base.Corpus([p.resolve() for p in a.snapshot],a.runtime.resolve())
    materials={};errors=[];psfreq=Counter();vsfreq=Counter();constrefs=Counter()
    for mh in sorted(visible):
        meta=c.entry_meta(mh);b,src=c.payload(mh);row={'material':mh,'meta':meta,'source':src}
        if not meta or norm(meta.get('reference',''))!=MAT_CLASS or b is None:
            row['error']='material unavailable/non-80801AD7';errors.append(mh);materials[mh]=row;continue
        try:
            p=parse_material(b,'PS4');ps=norm(p['pixel_shader']);vs=norm(p['vertex_shader']);psfreq[ps]+=1;vsfreq[vs]+=1
            vs_items=list(p['vs_textures']['items']);ps_items=list(p['ps_textures']['items'])
            vsc=norm(p['vs_vector4_container']);psc=norm(p['ps_vector4_container'])
            for h in (vsc,psc):
                if h not in NULLS:constrefs[h]+=1
            row.update({
                'declared_file_size':p['declared_file_size'],'actual_file_size':p['actual_file_size'],
                'unk08':p['unk08'],'unk0c':p['unk0c'],'unk10':p['unk10'],
                'vertex_shader':vs,'pixel_shader':ps,
                'vs_texture_count':p['vs_textures']['count'],'ps_texture_count':p['ps_textures']['count'],
                'vs_texture_tags':vs_items,'ps_texture_tags':ps_items,
                'textures':[{'stage':'vs',**x} for x in vs_items]+[{'stage':'ps',**x} for x in ps_items],
                'bindings':[{'stage':stage,'texture_index':int(x['texture_index']),'texture':norm(x['texture'])}
                            for stage,items in [('vs',vs_items),('ps',ps_items)] for x in items],
                'constants':{'vs_vector4_container':vsc,'ps_vector4_container':psc},
                'samplers':{'vs':p['vs_samplers'],'ps':p['ps_samplers']},
                'tfx':{'vs':p['vs_tfx_bytecode'],'ps':p['ps_tfx_bytecode']},
                'parsed_material_schema':'d1_material_decode.parse_material/PS4',
            })
        except Exception as ex:
            row['error']=repr(ex);errors.append(mh)
        materials[mh]=row
    out={'schema_version':1,'status':'D1_WORLD_MATERIAL_MANIFEST_COMPLETE' if not errors else 'D1_WORLD_MATERIAL_MANIFEST_PARTIAL',
         'visible_material_count':len(visible),'material_decode_errors':len(errors),'error_materials':errors,
         'pixel_shader_count':len(psfreq),'vertex_shader_count':len(vsfreq),'pixel_shader_frequency':dict(psfreq.most_common()),
         'unique_constant_container_count':len(constrefs),'constant_container_reference_counts':dict(constrefs),
         'materials':materials,
         'policy':'Exact selected D1 Material structure only. No texture payload decoding and no semantic role guesses.'}
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ('status','visible_material_count','material_decode_errors','pixel_shader_count','unique_constant_container_count')},indent=2))
    return 0 if not errors else 2
if __name__=='__main__':raise SystemExit(main())
