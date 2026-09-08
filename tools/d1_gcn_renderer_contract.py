#!/usr/bin/env python3
"""Join exact D1 material bindings and proven GCN control semantics into renderer IR.

The output is destination-neutral: Blender and Rust/WGSL consumers receive the same
texture/sampler identities, lane-selective control contracts and export-kill semantics.
Only facts already promoted by exact structural passes are joined here. Unresolved
loop/nested control remains explicit rather than being flattened into a guessed shader.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path


def norm(x):return str(x).upper().removeprefix('0X').zfill(8)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--stage',type=Path,required=True)
    ap.add_argument('--ir',type=Path,required=True)
    ap.add_argument('--exec-regions',type=Path,required=True)
    ap.add_argument('--kill-mask',type=Path,required=True)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args();viol=[];contract={}
    sd=json.load(open(a.stage));ir=json.load(open(a.ir));er=json.load(open(a.exec_regions));km=json.load(open(a.kill_mask))
    try:
        assert sd['status']=='D1_CORPUS_MATERIAL_STAGE_EXACT' and len(sd['materials'])==1
        assert ir['status']=='D1_GCN_STRUCTURAL_IR_COMPLETE' and int(ir.get('schema_version',0))>=2
        assert er['status']=='D1_GCN_EXEC_REGION_IR_COMPLETE' and not er['violations']
        assert km['status']=='D1_GCN_EXPORT_KILL_MASK_CONTRACT_COMPLETE' and not km['violations']
        m=sd['materials'][0];st=m['stage'];material=norm(m['material']);ps=norm(st['pixel_shader']);vs=norm(st['vertex_shader'])
        assert ir['shader']==er['shader']==km['shader']==ps and km['material']==material
        tex={int(x['texture_index']):norm(x['texture']) for x in st['ps_textures']['items']}
        assert len(tex)==st['ps_textures']['count']
        sam={int(x['index']):norm(x['first_dword_hex']) for x in st['ps_samplers']['items']}
        patterns=er.get('promoted_patterns') or []
        conditional=[]
        for p in patterns:
            if p['kind']!='CONDITIONAL_MULTIPLY_OR_PASSTHROUGH':continue
            r=er['regions'][p['region_id']];imgs=r['then_image_ops']
            tis=sorted({t for q in imgs for t in q['textures']});dmask=sorted({str(q.get('dmask_channels')) for q in imgs})
            if len(tis)!=1:raise ValueError(f'region {p["region_id"]}: conditional multiplier image texture domain {tis}')
            ti=tis[0];assert ti in tex
            conditional.append({
                'kind':'LANE_CONDITIONAL_MULTIPLIER','region_id':p['region_id'],'predicate':r['predicate'],
                'sample_texture_index':ti,'sample_texture_taghash':tex[ti],
                'sample_count':len(imgs),'sample_dmask_channels':dmask,
                'sample_instructions':[q['instruction'] for q in imgs],
                'factor_register':p['factor_register'],'outputs':p['outputs'],'equation':p['equation'],
                'proof_boundary':'Exact saveexec/complement/restore lane merge plus exact native image-resource provenance.'
            })
        kills=[]
        for k in km['contracts']:
            tis=[int(x) for x in k['predicate']['texture_indices']];assert len(tis)==1 and tis[0] in tex
            kills.append({
                'kind':'PERSISTENT_EXPORT_KILL','texture_index':tis[0],'texture_taghash':tex[tis[0]],
                'dmask_channels':k['predicate']['dmask_channels'],'threshold':k['predicate']['threshold'],
                'discard_when':k['discard_when'],'survive_when':k['survive_when'],
                'governed_exports':k['governed_exports'],'mask_register':k['mask_register'],
                'sample_instruction':k['predicate']['sample_instruction'],'compare_instruction':k['predicate']['compare_instruction']
            })
        contract={
            'material':material,'vertex_shader':vs,'pixel_shader':ps,
            'material_state4_hex':st['material_state4_hex'],'material_state4_u8':st['material_state4_u8'],'unk20':st['unk20'],
            'ps_texture_bindings':[{'texture_index':i,'texture_taghash':tex[i]} for i in sorted(tex)],
            'ps_sampler_bindings':[{'sampler_index':i,'sampler_taghash':sam[i]} for i in sorted(sam)],
            'interpolator_inputs':ir.get('interpolator_inputs',[]),'native_exports':ir.get('exports',[]),
            'multi_destination_overrides':ir.get('multi_destination_overrides',[]),
            'conditional_lane_operations':conditional,'persistent_export_kills':kills,
            'other_exact_simple_lane_merges':[{
                'region_id':r['region_id'],'predicate':r['predicate'],'lane_merges':r['lane_merges'],'promoted_patterns':r['promoted_patterns']
            } for r in er['regions'] if r['promotion']=='EXACT_SIMPLE_LANE_MERGE' and not any(x['region_id']==r['region_id'] for x in conditional)],
            'unresolved_control_regions':[{
                'region_id':r['region_id'],'predicate':r['predicate'],'nested_saveexec_instructions':r['nested_saveexec_instructions'],
                'loop_intersections':r['loop_intersections'],'reason':'nested/loop-carried lane values require the next symbolic dataflow layer'
            } for r in er['regions'] if r['promotion']=='STRUCTURAL_ONLY'],
        }
        assert conditional,'no promoted conditional lane operation'
        assert kills,'no persistent export kill contract'
    except Exception as ex:viol.append(repr(ex))
    out={'schema_version':1,'status':'D1_GCN_RENDERER_CONTRACT_EXACT_SUBSET' if contract and not viol else 'D1_GCN_RENDERER_CONTRACT_FAILED',
         'contract':contract,'violations':viol,
         'semantic_boundary':{
             'material_bindings':'EXACT','simple_lane_merges':'EXACT','persistent_export_kills':'EXACT',
             'loop_carried_values':'UNRESOLVED','nested_exec_values':'UNRESOLVED','full_mrt_expression_tree':'UNRESOLVED',
             'consumer_policy':'Blender and Rust/WGSL must consume the same contract; portable approximations must be explicitly labeled and must not replace native facts.'
         },
         'policy':'This file joins only already-proven material, image-resource and EXEC-control semantics. It is not a claim that the complete native pixel shader has been decompiled.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));return 0 if not viol else 2
if __name__=='__main__':raise SystemExit(main())
