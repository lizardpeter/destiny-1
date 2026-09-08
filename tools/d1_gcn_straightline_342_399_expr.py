#!/usr/bin/env python3
"""Lift the exact acyclic D1 PS 808EE505 cube/LOD value block at 342..399.

The proof boundary is target-specific. Exact material constants are folded only through
cbuffer provenance; immutable VOP semantics cover common arithmetic; a supplemental
source proof closes cube operations, modifiers and the CUBE _L address profile.
Descriptor loads and waits remain non-value anchors. Incoming pre-342 VGPR values are
explicit INPUT roots. No visual role is assigned to the cubemap.
"""
from __future__ import annotations
import argparse, json, struct
from pathlib import Path


class DAG:
    def __init__(self): self.nodes=[]; self.inputs={}
    def node(self,op,args=(),**meta):
        i=len(self.nodes);self.nodes.append({'id':i,'op':op,'args':list(args),**meta});return i
    def inp(self,name):
        if name not in self.inputs:self.inputs[name]=self.node('INPUT',(),name=name)
        return self.inputs[name]
    def const(self,v,**meta): return self.node('CONST',(),value=float(v),**meta)


def f32hex(t): return struct.unpack('<f',struct.pack('<I',int(t,16)&0xffffffff))[0]


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--ir',type=Path,required=True)
    ap.add_argument('--cbuffer-provenance',type=Path,required=True)
    ap.add_argument('--vop-semantics',type=Path,required=True)
    ap.add_argument('--cube-lod-semantics',type=Path,required=True)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args();viol=[];payload={}
    try:
        ir=json.load(open(a.ir));cb=json.load(open(a.cbuffer_provenance));vs=json.load(open(a.vop_semantics));cs=json.load(open(a.cube_lod_semantics))
        assert ir['status']=='D1_GCN_STRUCTURAL_IR_COMPLETE' and int(ir.get('schema_version',0))>=2
        assert ir['shader']=='808EE505' and ir['instruction_count']==456
        assert cb['status']=='D1_GCN_CBUFFER_PROVENANCE_EXACT' and not cb['violations'] and cb['material']=='80D777B6'
        assert vs['status']=='D1_GCN_VOP_SEMANTICS_SOURCE_PROVEN' and not vs['violations'] and int(vs.get('schema_version',0))>=4
        assert cs['status']=='D1_GCN_CUBE_LOD_SEMANTICS_SOURCE_PROVEN' and not cs['violations']
        cp=cs['proof'];assert cp['shader']=='808EE505' and cp['material']=='80D777B6'
        assert cp['texture5']=={'texture':'80AAFB08','resource_class':'CUBEMAP','shape':[256,256,6],'format_name':'BC1'}
        assert cp['semantic_boundary']['texture5_visual_material_role']=='WITHHELD'
        assert cp['semantic_boundary']['get_lod_fourth_native_lane']=='WITHHELD'

        s=vs['semantics'];x=cp['value_semantics']
        required_common={
          'v_mov_b32':'BITWISE_MOV32','s_mov_b32':'BITWISE_MOV32','v_mad_f32':'MAD',
          'v_mac_f32':'MAC','v_mul_f32':'MUL','v_add_f32':'ADD','float_clamp':'CLAMP_0_1',
          'v_mul_legacy_f32':'LEGACY_MUL_DX9','v_mac_legacy_f32':'LEGACY_MAC_DX9',
          'v_rsq_clamp_f32':'RSQ_CLAMP_MAXFLOAT','v_rcp_f32':'RCP','v_max_f32':'MAX'
        }
        for k,op in required_common.items(): assert s[k]['operation']==op,(k,s.get(k))
        required_cube={
          'v_sqrt_f32':'SQRT','v_subrev_f32':'SUBREV','v_mad_legacy_f32':'LEGACY_MAD_DX9',
          'v_cubema_f32':'CUBE_MAJOR_AXIS_X2','v_cubetc_f32':'CUBE_T','v_cubesc_f32':'CUBE_S',
          'v_cubeid_f32':'CUBE_FACE_ID','abs_modifier':'ABS','neg_modifier':'NEG','mul2_output_modifier':'OUTPUT_MUL2'
        }
        for k,op in required_cube.items(): assert x[k]['operation']==op,(k,x.get(k))

        ins=ir['instructions']
        expected={
          341:('s_buffer_load_dwordx2',['s[0:1]','s[20:23]','0x40']),
          342:('s_waitcnt',['lgkmcnt(0)']),343:('v_mov_b32',['v16','s1']),344:('v_mad_f32',['v17','v18','s0','v16']),
          345:('v_mac_f32',['v16','s0','v19']),346:('v_mul_f32',['v18','v17','v17']),347:('v_mac_f32',['v18','v16','v16']),
          348:('v_add_f32',['v18','-v18','1.0 clamp']),349:('v_mul_f32',['v19','v29','v16']),350:('v_sqrt_f32',['v18','v18']),
          351:('v_mul_f32',['v21','v28','v16']),352:('v_mac_f32',['v19','v25','v17']),353:('v_mul_f32',['v16','v27','v16']),
          354:('v_mac_f32',['v21','v24','v17']),355:('v_mac_f32',['v19','v18','v2']),356:('v_mac_f32',['v16','v11','v17']),
          357:('v_mac_f32',['v21','v18','v9']),358:('v_mul_legacy_f32',['v2','v19','v19']),359:('v_mac_f32',['v16','v18','v12']),
          360:('v_mac_legacy_f32',['v2','v21','v21']),361:('v_mac_legacy_f32',['v2','v16','v16']),362:('v_rsq_clamp_f32',['v2','v2']),
          363:('v_mul_legacy_f32',['v9','v19','v2']),364:('v_mul_legacy_f32',['v11','v21','v2']),365:('v_mul_f32',['v8','v8','v9']),
          366:('v_mul_legacy_f32',['v2','v16','v2']),367:('v_mac_f32',['v8','v10','v11']),368:('v_mac_f32',['v8','v14','v2']),
          369:('v_max_f32',['v10','v8','v8 mul:2']),370:('v_mul_f32',['v12','v2','v10']),371:('v_mul_f32',['v14','v11','v10']),
          372:('v_mul_f32',['v10','v9','v10']),373:('s_load_dwordx8',['s[4:11]','s[12:13]','0x28']),374:('s_load_dwordx4',['s[0:3]','s[2:3]','0xc']),
          375:('v_mad_legacy_f32',['v12','-v5','v6','v12']),376:('v_mad_legacy_f32',['v14','-v4','v6','v14']),
          377:('v_mad_legacy_f32',['v10','-v3','v6','v10']),378:('v_cubema_f32',['v3','v12','v14','v10']),
          379:('v_cubetc_f32',['v4','v12','v14','v10']),380:('v_cubesc_f32',['v5','v12','v14','v10']),381:('v_rcp_f32',['v3','abs(v3)']),
          382:('s_mov_b32',['s12','0x3fc00000']),383:('v_cubeid_f32',['v18','v12','v14','v10']),384:('v_mad_legacy_f32',['v17','v4','v3','s12']),
          385:('v_mad_legacy_f32',['v16','v5','v3','s12']),386:('s_waitcnt',['lgkmcnt(0)']),
          387:('image_get_lod',['v5','v[16:19]','s[4:11]','s[0:3] dmask:2']),
          388:('s_buffer_load_dwordx2',['s[12:13]','s[20:23]','0x58']),389:('s_buffer_load_dword',['s14','s[20:23]','0x54']),
          390:('s_buffer_load_dword',['s15','s[20:23]','0x50']),391:('s_waitcnt',['lgkmcnt(0)']),392:('v_mov_b32',['v10','s12']),
          393:('v_mov_b32',['v12','s14']),394:('v_mad_f32',['v10','v20','s13','v10 clamp']),395:('v_subrev_f32',['v12','s15','v12']),
          396:('v_mad_f32',['v10','v10','v12','s15']),397:('s_waitcnt',['vmcnt(0)']),398:('v_max_f32',['v19','v10','v5']),
          399:('image_sample_l',['v[3:6]','v[16:19]','s[4:11]','s[0:3] dmask:15'])
        }
        for i,(op,ops) in expected.items():
            q=ins[i];assert q['opcode']==op and q['operands']==ops,(i,q['opcode'],q['operands'])

        by={int(q['instruction']):q for q in cb['loads']}
        for i in (341,388,389,390): assert i in by and by[i]['resolution']=='EXACT_MATERIAL_PS_B0',by.get(i)
        q341,q388,q389,q390=by[341],by[388],by[389],by[390]
        assert q341['destination_sgprs']==['s0','s1'] and [z['raw_hex'] for z in q341['material_values']]==['00000040','000080bf']
        assert q388['destination_sgprs']==['s12','s13'] and [z['raw_hex'] for z in q388['material_values']]==['9899d93e','9a99c93f']
        assert q389['destination_sgprs']==['s14'] and q389['material_values'][0]['raw_hex']=='00000000'
        assert q390['destination_sgprs']==['s15'] and q390['material_values'][0]['raw_hex']=='0000a040'

        dag=DAG();st={}
        def get(r):
            if r not in st: st[r]=dag.inp(r)
            return st[r]
        def setr(r,n): st[r]=n
        def cbuf(reg,mv,load_i): return dag.const(mv['value'],source='MATERIAL_PS_B0',load_instruction=load_i,register=reg,vec4_index=mv['vec4_index'],component=mv['component'],raw_hex=mv['raw_hex'])
        for reg,mv in zip(q341['destination_sgprs'],q341['material_values']): setr(reg,cbuf(reg,mv,341))

        # 343..372: exact scalar/vector arithmetic immediately after b0[16].
        setr('v16',dag.node('BITWISE_MOV32',[get('s1')],instruction=343))
        setr('v17',dag.node('MAD',[get('v18'),get('s0'),get('v16')],instruction=344))
        setr('v16',dag.node('MAC',[get('s0'),get('v19'),get('v16')],instruction=345))
        setr('v18',dag.node('MUL',[get('v17'),get('v17')],instruction=346))
        setr('v18',dag.node('MAC',[get('v16'),get('v16'),get('v18')],instruction=347))
        one=dag.const(1.0,source='INLINE_LITERAL',instruction=348)
        neg=dag.node('NEG',[get('v18')],instruction=348)
        setr('v18',dag.node('CLAMP_0_1',[dag.node('ADD',[neg,one],instruction=348)],instruction=348))
        setr('v19',dag.node('MUL',[get('v29'),get('v16')],instruction=349))
        setr('v18',dag.node('SQRT',[get('v18')],instruction=350))
        setr('v21',dag.node('MUL',[get('v28'),get('v16')],instruction=351))
        setr('v19',dag.node('MAC',[get('v25'),get('v17'),get('v19')],instruction=352))
        setr('v16',dag.node('MUL',[get('v27'),get('v16')],instruction=353))
        setr('v21',dag.node('MAC',[get('v24'),get('v17'),get('v21')],instruction=354))
        setr('v19',dag.node('MAC',[get('v18'),get('v2'),get('v19')],instruction=355))
        setr('v16',dag.node('MAC',[get('v11'),get('v17'),get('v16')],instruction=356))
        setr('v21',dag.node('MAC',[get('v18'),get('v9'),get('v21')],instruction=357))
        setr('v2',dag.node('LEGACY_MUL_DX9',[get('v19'),get('v19')],instruction=358,zero_rule='0.0*x = 0.0'))
        setr('v16',dag.node('MAC',[get('v18'),get('v12'),get('v16')],instruction=359))
        setr('v2',dag.node('LEGACY_MAC_DX9',[get('v21'),get('v21'),get('v2')],instruction=360,zero_rule='0.0*x = 0.0'))
        setr('v2',dag.node('LEGACY_MAC_DX9',[get('v16'),get('v16'),get('v2')],instruction=361,zero_rule='0.0*x = 0.0'))
        setr('v2',dag.node('RSQ_CLAMP_MAXFLOAT',[get('v2')],instruction=362))
        setr('v9',dag.node('LEGACY_MUL_DX9',[get('v19'),get('v2')],instruction=363,zero_rule='0.0*x = 0.0'))
        setr('v11',dag.node('LEGACY_MUL_DX9',[get('v21'),get('v2')],instruction=364,zero_rule='0.0*x = 0.0'))
        setr('v8',dag.node('MUL',[get('v8'),get('v9')],instruction=365))
        setr('v2',dag.node('LEGACY_MUL_DX9',[get('v16'),get('v2')],instruction=366,zero_rule='0.0*x = 0.0'))
        setr('v8',dag.node('MAC',[get('v10'),get('v11'),get('v8')],instruction=367))
        setr('v8',dag.node('MAC',[get('v14'),get('v2'),get('v8')],instruction=368))
        mx=dag.node('MAX',[get('v8'),get('v8')],instruction=369)
        setr('v10',dag.node('OUTPUT_MUL2',[mx],instruction=369))
        setr('v12',dag.node('MUL',[get('v2'),get('v10')],instruction=370))
        setr('v14',dag.node('MUL',[get('v11'),get('v10')],instruction=371))
        setr('v10',dag.node('MUL',[get('v9'),get('v10')],instruction=372))

        # 373/374 descriptor loads are anchors. 375..385 construct native cube args.
        setr('v12',dag.node('LEGACY_MAD_DX9',[dag.node('NEG',[get('v5')],instruction=375),get('v6'),get('v12')],instruction=375,zero_rule='0.0*x = 0.0'))
        setr('v14',dag.node('LEGACY_MAD_DX9',[dag.node('NEG',[get('v4')],instruction=376),get('v6'),get('v14')],instruction=376,zero_rule='0.0*x = 0.0'))
        setr('v10',dag.node('LEGACY_MAD_DX9',[dag.node('NEG',[get('v3')],instruction=377),get('v6'),get('v10')],instruction=377,zero_rule='0.0*x = 0.0'))
        cube_xyz=(get('v12'),get('v14'),get('v10'))
        setr('v3',dag.node('CUBE_MAJOR_AXIS_X2',cube_xyz,instruction=378))
        setr('v4',dag.node('CUBE_T',cube_xyz,instruction=379))
        setr('v5',dag.node('CUBE_S',cube_xyz,instruction=380))
        setr('v3',dag.node('RCP',[dag.node('ABS',[get('v3')],instruction=381)],instruction=381))
        setr('s12',dag.node('BITWISE_MOV32',[dag.const(f32hex('0x3fc00000'),source='INLINE_LITERAL',raw_hex='0x3fc00000',instruction=382)],instruction=382))
        setr('v18',dag.node('CUBE_FACE_ID',cube_xyz,instruction=383))
        setr('v17',dag.node('LEGACY_MAD_DX9',[get('v4'),get('v3'),get('s12')],instruction=384,zero_rule='0.0*x = 0.0'))
        setr('v16',dag.node('LEGACY_MAD_DX9',[get('v5'),get('v3'),get('s12')],instruction=385,zero_rule='0.0*x = 0.0'))

        # GET_LOD logical cube args are source-closed as s,t,face; fourth native lane preserved only as metadata.
        native_getlod=[get(r) for r in ('v16','v17','v18','v19')]
        getlod=dag.node('IMAGE_GET_LOD_CUBE_Y',[get('v16'),get('v17'),get('v18')],instruction=387,texture_index=5,texture='80AAFB08',sampler_index=6,dmask='y',native_vaddr_roots=native_getlod,native_v19_meaning='WITHHELD')
        setr('v5',getlod)

        # Exact material LOD-remap constants loaded at 388..390.
        for reg,mv in zip(q388['destination_sgprs'],q388['material_values']): setr(reg,cbuf(reg,mv,388))
        setr('s14',cbuf('s14',q389['material_values'][0],389));setr('s15',cbuf('s15',q390['material_values'][0],390))
        setr('v10',dag.node('BITWISE_MOV32',[get('s12')],instruction=392))
        setr('v12',dag.node('BITWISE_MOV32',[get('s14')],instruction=393))
        setr('v10',dag.node('CLAMP_0_1',[dag.node('MAD',[get('v20'),get('s13'),get('v10')],instruction=394)],instruction=394))
        setr('v12',dag.node('SUBREV',[get('s15'),get('v12')],instruction=395,source_order='S1_MINUS_S0'))
        setr('v10',dag.node('MAD',[get('v10'),get('v12'),get('s15')],instruction=396))
        setr('v19',dag.node('MAX',[get('v10'),get('v5')],instruction=398))

        # CUBE _L source profile is exactly s,t,face,lod. Sample result remains native xyzw.
        sample=dag.node('IMAGE_SAMPLE_L_CUBE_RGBA',[get('v16'),get('v17'),get('v18'),get('v19')],instruction=399,texture_index=5,texture='80AAFB08',sampler_index=6,dmask='xyzw',logical_address_order=['s','t','face','lod'])
        for comp,reg in enumerate(('v3','v4','v5','v6')):
            setr(reg,dag.node('EXTRACT_NATIVE_COMPONENT',[sample],instruction=399,component=comp,channel='xyzw'[comp]))

        value_indices=list(range(343,373))+list(range(375,386))+[387]+list(range(392,397))+[398,399]
        assert len(value_indices)==49
        anchors=[
          {'instruction':342,'kind':'WAIT'},{'instruction':373,'kind':'RESOURCE_DESCRIPTOR_LOAD'},
          {'instruction':374,'kind':'SAMPLER_DESCRIPTOR_LOAD'},{'instruction':386,'kind':'WAIT'},
          {'instruction':388,'kind':'EXACT_MATERIAL_CBUFFER_LOAD'},{'instruction':389,'kind':'EXACT_MATERIAL_CBUFFER_LOAD'},
          {'instruction':390,'kind':'EXACT_MATERIAL_CBUFFER_LOAD'},{'instruction':391,'kind':'WAIT'},
          {'instruction':397,'kind':'WAIT'}]
        roots={r:st[r] for r in sorted(st) if r.startswith('v')}
        payload={
          'shader':'808EE505','material':'80D777B6','instruction_range':[342,399],
          'prerequisite_material_load_instructions':[341],
          'in_range_material_load_instructions':[388,389,390],
          'value_instruction_indices':value_indices,'non_value_anchors':anchors,
          'node_count':len(dag.nodes),'nodes':dag.nodes,'input_roots':dict(sorted(dag.inputs.items())),
          'output_register_roots':roots,
          'cube_texture':{'texture_index':5,'texture':'80AAFB08','resource_class':'CUBEMAP','shape':[256,256,6]},
          'cube_address_profile':cp['cube_address_profile'],
          'semantic_boundary':{
            'instructions_343_399_listed_values':'EXACT_SOURCE_SEMANTICS',
            'material_constants':'EXACT_MATERIAL_PS_B0',
            'cube_sample_l_address':'EXACT_S_T_FACE_LOD',
            'image_get_lod_fourth_native_lane':'PRESERVED_WITH_MEANING_WITHHELD',
            'descriptor_loads_and_waits':'NON_VALUE_ANCHORS',
            'pre_342_vgpr_values':'EXPLICIT_SYMBOLIC_INPUTS',
            'cubemap_visual_role':'WITHHELD'
          }
        }
    except Exception as e: viol.append(repr(e))
    out={'schema_version':1,'status':'D1_GCN_STRAIGHTLINE_342_399_EXPRESSION_EXACT' if payload and not viol else 'D1_GCN_STRAIGHTLINE_342_399_EXPRESSION_PARTIAL','expression':payload,'violations':viol,'policy':'Only the exact acyclic 342..399 value/MIMG path is promoted. Descriptor/wait anchors remain separate; the cubemap dimension/address profile is exact while its visual role remains withheld.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':out['status'],'node_count':payload.get('node_count'),'value_instruction_count':len(payload.get('value_instruction_indices',[])),'input_count':len(payload.get('input_roots',{})),'violations':viol},indent=2));return 0 if not viol else 2
if __name__=='__main__':raise SystemExit(main())
