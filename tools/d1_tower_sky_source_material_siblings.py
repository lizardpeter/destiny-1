#!/usr/bin/env python3
"""Find exact source-material sibling groups in the D1 Tower sky corpus.

Two pixel-shader families are source-material siblings only when their material
populations have identical multisets of:
- vertex shader identity;
- serialized PS texture-index -> texture bindings;
- PS sampler tag sequence;
- PS TFX bytecode;
- PS texture count.

This deliberately does not compare native GCN and does not assign semantic roles.
It is a prioritization proof for later native differential analysis.
"""
from __future__ import annotations
import argparse,collections,hashlib,json
from pathlib import Path

def norm(x):return str(x).upper().removeprefix('0X').zfill(8)

def material_signature(m):
    binds=tuple(sorted((int(x['texture_index']),norm(x['texture'])) for x in (m.get('bindings') or []) if x.get('stage')=='ps'))
    samplers=tuple(norm(x.get('first_dword_hex','FFFFFFFF')) for x in (((m.get('samplers') or {}).get('ps') or {}).get('items') or []))
    raw=bytes.fromhex((((m.get('tfx') or {}).get('ps') or {}).get('bytes_hex') or ''))
    return (
        norm(m.get('vertex_shader')),
        binds,
        samplers,
        hashlib.sha256(raw).hexdigest(),
        len(raw),
        int(m.get('ps_texture_count',0)),
    )

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--manifest',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    d=json.loads(a.manifest.read_text());v=[]
    if d.get('status')!='D1_WORLD_VISIBLE_MATERIAL_TEXTURE_EXPORT':v.append('manifest status drift')
    if int(d.get('visible_material_count',-1))!=74:v.append('visible material count drift')
    if int(d.get('unique_texture_tags',-1))!=44:v.append('texture count drift')
    freq={norm(k):int(x) for k,x in (d.get('pixel_shader_frequency') or {}).items()}
    if len(freq)!=43:v.append('shader family count drift')
    by=collections.defaultdict(list)
    for mh,m in (d.get('materials') or {}).items():
        sh=norm(m.get('pixel_shader'))
        by[sh].append((norm(mh),material_signature(m)))
    rows=[]
    groupmap=collections.defaultdict(list)
    for sh in sorted(freq):
        sigs=sorted(sig for _,sig in by.get(sh,[]))
        if len(sigs)!=freq[sh]:v.append(f'{sh}: material population drift')
        # exact population signature; material hash itself intentionally excluded.
        key=repr(sigs)
        groupmap[key].append(sh)
        rows.append({'shader':sh,'material_count':freq[sh],'materials':sorted(mh for mh,_ in by.get(sh,[])),'population_signature':key})
    groups=[]
    for key,shaders in groupmap.items():
        if len(shaders)<2:continue
        groups.append({
            'shader_family_count':len(shaders),
            'material_count_per_family':freq[shaders[0]],
            'total_material_rows':sum(freq[x] for x in shaders),
            'shaders':sorted(shaders),
            'exact_relation':'IDENTICAL_SOURCE_MATERIAL_POPULATION_SIGNATURE',
        })
    groups.sort(key=lambda x:(-x['total_material_rows'],-x['shader_family_count'],x['shaders']))
    out={
        'schema':'d1_tower_sky_source_material_siblings/v1',
        'status':'D1_TOWER_SKY_SOURCE_MATERIAL_SIBLINGS_EXACT' if len(rows)==43 and not v else 'D1_TOWER_SKY_SOURCE_MATERIAL_SIBLINGS_PARTIAL',
        'shader_family_count':len(rows),'sibling_group_count':len(groups),
        'sibling_shader_family_count':sum(x['shader_family_count'] for x in groups),
        'sibling_material_row_weight':sum(x['total_material_rows'] for x in groups),
        'groups':groups,'rows':rows,'violations':v,
        'semantic_boundary':{
            'source_population_equality':'EXACT',
            'native_gcn_equivalence':'NOT_TESTED_HERE',
            'paired_pass_identity':'WITHHELD',
            'human_sky_role':'WITHHELD',
        },
        'policy':'Sibling groups are exact equality of serialized material populations excluding material hash. They prioritize native differential analysis but do not imply the shaders have identical arithmetic or complementary semantic roles.',
    }
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'status':out['status'],'groups':groups,'violations':v},indent=2))
    return 0 if out['status']=='D1_TOWER_SKY_SOURCE_MATERIAL_SIBLINGS_EXACT' else 2
if __name__=='__main__':raise SystemExit(main())
