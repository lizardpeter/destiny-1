#!/usr/bin/env python3
"""Lift the exact acyclic D1 PS 808EE505 value block at instructions 404..435.

The block is target-specific and fail-closed. Material PS-b0 scalars loaded at
400/402/403 are folded only through exact cbuffer provenance. ISA operations are
accepted only when the source-semantics proof closes them. Legacy DX9 multiply/MAC
remain explicit operators. Values defined before instruction 404 remain INPUT nodes.
Instructions 416 and 418 are waits and are preserved as non-value anchors.
"""
from __future__ import annotations
import argparse,json,struct
from pathlib import Path


class DAG:
    def __init__(self):self.nodes=[];self.inputs={}
    def node(self,op,args=(),**meta):
        i=len(self.nodes);self.nodes.append({'id':i,'op':op,'args':list(args),**meta});return i
    def inp(self,name):
        if name not in self.inputs:self.inputs[name]=self.node('INPUT',(),name=name)
        return self.inputs[name]
    def const(self,v,**meta):return self.node('CONST',(),value=float(v),**meta)


def f32hex(t):return struct.unpack('<f',struct.pack('<I',int(t,16)&0xffffffff))[0]


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--ir',type=Path,required=True)
    ap.add_argument('--cbuffer-provenance',type=Path,required=True)
    ap.add_argument('--vop-semantics',type=Path,required=True)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args();viol=[];payload={}
    ir=json.load(open(a.ir));cb=json.load(open(a.cbuffer_provenance));vs=json.load(open(a.vop_semantics))
    try:
        assert ir['status']=='D1_GCN_STRUCTURAL_IR_COMPLETE' and int(ir.get('schema_version',0))>=2
        assert ir['shader']=='808EE505' and ir['instruction_count']==456
        assert cb['status']=='D1_GCN_CBUFFER_PROVENANCE_EXACT' and not cb['violations']
        assert cb['shader']=='808EE505' and cb['material']=='80D777B6'
        assert vs['status']=='D1_GCN_VOP_SEMANTICS_SOURCE_PROVEN' and not vs['violations'] and int(vs.get('schema_version',0))>=4
        s=vs['semantics']
        required={
          'v_add_f32':('ADD','D = S0 + S1'),
          'v_log_f32':('LOG2','D = log2(S0)'),
          'v_mul_legacy_f32':('LEGACY_MUL_DX9','D = legacy_mul_dx9(S0,S1)'),
          'v_mul_f32':('MUL','D = S0 * S1'),
          'v_mac_legacy_f32':('LEGACY_MAC_DX9','D_new = legacy_mul_dx9(S0,S1) + D_old'),
          'v_exp_f32':('EXP2','D = pow(2.0, S0)'),
          'v_mov_b32':('BITWISE_MOV32','D.u = S0.u'),
          'v_mac_f32':('MAC','D_new = S0 * S1 + D_old'),
          's_mov_b32':('BITWISE_MOV32','D.u = S0.u'),
          'v_rsq_clamp_f32':('RSQ_CLAMP_MAXFLOAT','D = clamp_to_signed_max_float(1.0 / sqrt(S0))'),
          'v_mad_f32':('MAD','D = S0 * S1 + S2'),
          'v_madak_f32':('MADAK','D = S0 * S1 + K'),
          'float_clamp':('CLAMP_0_1','D = clamp(D, 0.0, 1.0)'),
        }
        for k,(op,eq) in required.items():assert s[k]['operation']==op and s[k]['equation']==eq,(k,s.get(k))
        assert s['v_mul_legacy_f32']['zero_rule']=='0.0*x = 0.0'
        assert s['v_mac_legacy_f32']['legacy_product']=='AMDGPUfmul_legacy'
        assert s['v_madak_f32']['constant_kind']=='32_BIT_INLINE_CONSTANT'

        ins=ir['instructions']
        expected={
          400:('s_buffer_load_dwordx4',['s[0:3]','s[20:23]','0x5c']),
          401:('s_waitcnt',['lgkmcnt(0)']),
          402:('s_buffer_load_dword',['s3','s[20:23]','0x60']),
          403:('s_buffer_load_dwordx2',['s[4:5]','s[20:23]','0x64']),
          404:('v_add_f32',['v8','-v8','1.0 clamp']),
          405:('v_log_f32',['v8','v8']),
          406:('v_mul_legacy_f32',['v10','v9','v9']),
          407:('v_mul_f32',['v8','s2','v8']),
          408:('v_mac_legacy_f32',['v10','v11','v11']),
          409:('v_exp_f32',['v8','v8']),
          410:('v_mov_b32',['v12','s0']),
          411:('v_mac_legacy_f32',['v10','v2','v2']),
          412:('v_mac_f32',['v12','s1','v8']),
          413:('v_mov_b32',['v8','0x3ec00000']),
          414:('s_mov_b32',['s0','0x3e000000']),
          415:('v_rsq_clamp_f32',['v10','v10']),
          416:('s_waitcnt',['lgkmcnt(0)']),
          417:('v_mul_f32',['v6','v6','v12']),
          418:('s_waitcnt',['lgkmcnt(0)']),
          419:('v_mul_f32',['v3','s3','v3']),
          420:('v_mul_f32',['v4','s3','v4']),
          421:('v_mul_f32',['v5','s3','v5']),
          422:('v_mov_b32',['v12','s5']),
          423:('v_mac_f32',['v8','s0','v20']),
          424:('v_mul_legacy_f32',['v2','v2','v10']),
          425:('v_mul_legacy_f32',['v11','v11','v10']),
          426:('v_mul_legacy_f32',['v9','v9','v10']),
          427:('v_mad_f32',['v10','v26','s4','v12']),
          428:('v_mad_f32',['v14','v13','s4','v12']),
          429:('v_mac_f32',['v12','s4','v15']),
          430:('v_mul_f32',['v3','v6','v3']),
          431:('v_mul_f32',['v4','v6','v4']),
          432:('v_mul_f32',['v5','v6','v5']),
          433:('v_madak_f32',['v2','v8','v2','0x3f000000']),
          434:('v_madak_f32',['v6','v8','v11','0x3f000000']),
          435:('v_madak_f32',['v8','v8','v9','0x3f000000']),
        }
        for i,(op,o) in expected.items():
            x=ins[i];assert x['opcode']==op and x['operands']==o,(i,x['opcode'],x['operands'])

        byload={int(q['instruction']):q for q in cb['loads']}
        for i in (400,402,403):
            assert i in byload and byload[i]['resolution']=='EXACT_MATERIAL_PS_B0',byload.get(i)
        q400,q402,q403=byload[400],byload[402],byload[403]
        assert q400['destination_sgprs']==['s0','s1','s2','s3']
        assert [x['raw_hex'] for x in q400['material_values']]==['0000403f','0000803e','00004040','00000000']
        assert q402['destination_sgprs']==['s3'] and q402['material_values'][0]['raw_hex']=='0000403f'
        assert q403['destination_sgprs']==['s4','s5'] and [x['raw_hex'] for x in q403['material_values']]==['0000803f','0000803f']

        dag=DAG();st={}
        def get(r):
            if r not in st:st[r]=dag.inp(r)
            return st[r]
        def setr(r,n):st[r]=n
        def cbuf(reg,mv,load_i):return dag.const(mv['value'],source='MATERIAL_PS_B0',load_instruction=load_i,register=reg,vec4_index=mv['vec4_index'],component=mv['component'],raw_hex=mv['raw_hex'])
        for reg,mv in zip(q400['destination_sgprs'],q400['material_values']):setr(reg,cbuf(reg,mv,400))
        setr('s3',cbuf('s3',q402['material_values'][0],402))
        for reg,mv in zip(q403['destination_sgprs'],q403['material_values']):setr(reg,cbuf(reg,mv,403))

        one=dag.const(1.0,source='INLINE_LITERAL',instruction=404)
        negv8=dag.node('NEG',[get('v8')],instruction=404)
        setr('v8',dag.node('CLAMP_0_1',[dag.node('ADD',[negv8,one],instruction=404)],instruction=404))
        setr('v8',dag.node('LOG2',[get('v8')],instruction=405))
        setr('v10',dag.node('LEGACY_MUL_DX9',[get('v9'),get('v9')],instruction=406,zero_rule='0.0*x = 0.0'))
        setr('v8',dag.node('MUL',[get('s2'),get('v8')],instruction=407))
        setr('v10',dag.node('LEGACY_MAC_DX9',[get('v11'),get('v11'),get('v10')],instruction=408,legacy_product='AMDGPUfmul_legacy'))
        setr('v8',dag.node('EXP2',[get('v8')],instruction=409))
        setr('v12',get('s0'))
        setr('v10',dag.node('LEGACY_MAC_DX9',[get('v2'),get('v2'),get('v10')],instruction=411,legacy_product='AMDGPUfmul_legacy'))
        setr('v12',dag.node('MAC',[get('s1'),get('v8'),get('v12')],instruction=412))
        setr('v8',dag.const(f32hex('0x3ec00000'),source='INLINE_LITERAL',raw_hex='0x3ec00000',instruction=413))
        setr('s0',dag.const(f32hex('0x3e000000'),source='INLINE_LITERAL',raw_hex='0x3e000000',instruction=414))
        setr('v10',dag.node('RSQ_CLAMP_MAXFLOAT',[get('v10')],instruction=415))
        setr('v6',dag.node('MUL',[get('v6'),get('v12')],instruction=417))
        setr('v3',dag.node('MUL',[get('s3'),get('v3')],instruction=419))
        setr('v4',dag.node('MUL',[get('s3'),get('v4')],instruction=420))
        setr('v5',dag.node('MUL',[get('s3'),get('v5')],instruction=421))
        setr('v12',get('s5'))
        setr('v8',dag.node('MAC',[get('s0'),get('v20'),get('v8')],instruction=423))
        setr('v2',dag.node('LEGACY_MUL_DX9',[get('v2'),get('v10')],instruction=424,zero_rule='0.0*x = 0.0'))
        setr('v11',dag.node('LEGACY_MUL_DX9',[get('v11'),get('v10')],instruction=425,zero_rule='0.0*x = 0.0'))
        setr('v9',dag.node('LEGACY_MUL_DX9',[get('v9'),get('v10')],instruction=426,zero_rule='0.0*x = 0.0'))
        setr('v10',dag.node('MAD',[get('v26'),get('s4'),get('v12')],instruction=427))
        setr('v14',dag.node('MAD',[get('v13'),get('s4'),get('v12')],instruction=428))
        setr('v12',dag.node('MAC',[get('s4'),get('v15'),get('v12')],instruction=429))
        setr('v3',dag.node('MUL',[get('v6'),get('v3')],instruction=430))
        setr('v4',dag.node('MUL',[get('v6'),get('v4')],instruction=431))
        setr('v5',dag.node('MUL',[get('v6'),get('v5')],instruction=432))
        half=dag.const(f32hex('0x3f000000'),source='INLINE_LITERAL',raw_hex='0x3f000000',instruction=433)
        setr('v2',dag.node('MADAK',[get('v8'),get('v2'),half],instruction=433,constant_raw_hex='0x3f000000'))
        setr('v6',dag.node('MADAK',[get('v8'),get('v11'),half],instruction=434,constant_raw_hex='0x3f000000'))
        setr('v8',dag.node('MADAK',[get('v8'),get('v9'),half],instruction=435,constant_raw_hex='0x3f000000'))

        value_indices=[i for i in range(404,436) if i not in (416,418)]
        roots={r:st[r] for r in sorted(st) if r.startswith('v')}
        payload={
          'shader':'808EE505','material':'80D777B6','instruction_range':[404,435],
          'prerequisite_material_load_instructions':[400,402,403],
          'value_instruction_indices':value_indices,
          'non_value_anchors':[{'instruction':416,'kind':'WAIT','opcode':'s_waitcnt'},{'instruction':418,'kind':'WAIT','opcode':'s_waitcnt'}],
          'material_constants':{
            '400':{r:mv for r,mv in zip(q400['destination_sgprs'],q400['material_values'])},
            '402':{'s3':q402['material_values'][0]},
            '403':{r:mv for r,mv in zip(q403['destination_sgprs'],q403['material_values'])},
          },
          'node_count':len(dag.nodes),'nodes':dag.nodes,'input_roots':dict(sorted(dag.inputs.items())),
          'output_register_roots':roots,
          'source_semantics':{k:s[k] for k in required},
          'semantic_boundary':{
            'instructions_404_435_value_arithmetic':'EXACT_SOURCE_SEMANTICS',
            'material_scalars_400_403':'EXACT_MATERIAL_PS_B0',
            'legacy_multiply_and_mac':'EXACT_DISTINCT_DX9_OPERATORS',
            'waits_416_418':'NON_VALUE_ANCHORS',
            'pre_404_vgpr_values':'EXPLICIT_SYMBOLIC_INPUTS',
            'destiny_visual_roles':'WITHHELD'
          }
        }
        assert len(value_indices)==30
    except Exception as e:viol.append(repr(e))
    out={'schema_version':1,'status':'D1_GCN_STRAIGHTLINE_404_435_EXPRESSION_EXACT' if payload and not viol else 'D1_GCN_STRAIGHTLINE_404_435_EXPRESSION_PARTIAL','expression':payload,'violations':viol,'policy':'Only the exact acyclic 404..435 target block is promoted. Source-proven legacy semantics remain distinct; incoming values are symbolic and no visual/material role is guessed.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'status':out['status'],'node_count':payload.get('node_count') if payload else None,'value_instruction_count':len(payload.get('value_instruction_indices',[])) if payload else None,'input_count':len(payload.get('input_roots',{})) if payload else None,'violations':viol},indent=2));return 0 if not viol else 2
if __name__=='__main__':raise SystemExit(main())
