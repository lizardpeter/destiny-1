#!/usr/bin/env python3
"""Join exact Crota duplicated color/partner parts to StagePartOffsets groups.

Inputs:
* exact D1 8108E5B7 stage/part census;
* exact serialized color/partner geometry-pair order proof.

This proves whether the two serialized copies of each exact geometry range occupy
the same StagePartOffsets-derived group.  Group identity is retained as an integer;
no D1 engine RenderStage enum name or actual draw order is assigned here.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--stage-census',type=Path,required=True)
    ap.add_argument('--pair-order',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    s=json.loads(a.stage_census.read_text());p=json.loads(a.pair_order.read_text())
    violations=[];rows=[]
    if s.get('status')!='D1_CROTA_MODEL_STAGE_PART_CENSUS_COMPLETE':
        violations.append('stage census not exact')
    if p.get('status')!='D1_CROTA_SERIALIZED_PAIR_ORDER_EXACT' or p.get('violations'):
        violations.append('pair-order proof not exact')

    parts={}
    for m in s.get('meshes',[]):
        mi=int(m['mesh_index'])
        for x in m.get('parts',[]):
            parts[(mi,int(x['part_index']))]=x

    for q in p.get('rows',[]):
        ck=(int(q['mesh_index']),int(q['color_part_index']))
        pk=(int(q['mesh_index']),int(q['partner_part_index']))
        c=parts.get(ck);r=parts.get(pk)
        if c is None or r is None:
            violations.append(f'{ck}/{pk}: stage part row missing');continue
        geom=q['geometry_key']
        expected=(int(geom['lod']),int(geom['index_offset']),int(geom['index_count']),int(geom['primitive_type']))
        cg=(int(c['lod']),int(c['index_offset']),int(c['index_count']),int(c['primitive_type']))
        rg=(int(r['lod']),int(r['index_offset']),int(r['index_count']),int(r['primitive_type']))
        if cg!=expected or rg!=expected:
            violations.append(f'{ck}/{pk}: geometry drift {cg}/{rg}!={expected}')
        rows.append({
            **q,
            'color_group_index':c.get('group_index'),
            'partner_group_index':r.get('group_index'),
            'same_stage_part_group':c.get('group_index')==r.get('group_index'),
            'color_flags_d1':c.get('flags_d1'),
            'partner_flags_d1':r.get('flags_d1'),
            'color_variant_shader_index':c.get('variant_shader_index'),
            'partner_variant_shader_index':r.get('variant_shader_index'),
        })

    same=sum(bool(x['same_stage_part_group']) for x in rows)
    out={
      'schema':'d1_crota_pair_stage_group_join/v1',
      'status':'D1_CROTA_PAIR_STAGE_GROUP_JOIN_EXACT' if len(rows)==14 and not violations else 'D1_CROTA_PAIR_STAGE_GROUP_JOIN_PARTIAL',
      'pair_instance_count':len(rows),
      'same_stage_part_group_count':same,
      'different_stage_part_group_count':len(rows)-same,
      'rows':rows,'violations':violations,
      'semantic_boundary':{
        'StagePartOffsets_group_membership':'EXACT_D1_SERIALIZED_STRUCTURE',
        'group_to_engine_RenderStage_name':'WITHHELD',
        'within_group_submission_order':'WITHHELD',
        'render_target_identity':'WITHHELD',
        'native_draw_order':'WITHHELD',
      },
      'policy':'This joins exact D1 serialized structures only. Equal StagePartOffsets group does not by itself prove runtime iteration order or target ownership.',
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'status':out['status'],'pairs':len(rows),'same_group':same,
                      'different_group':len(rows)-same,
                      'rows':[(x['mesh_index'],x['color_part_index'],x['partner_part_index'],
                               x['color_group_index'],x['partner_group_index'],x['same_stage_part_group']) for x in rows],
                      'violations':violations},indent=2))
    return 0 if out['status']=='D1_CROTA_PAIR_STAGE_GROUP_JOIN_EXACT' else 2

if __name__=='__main__':raise SystemExit(main())
