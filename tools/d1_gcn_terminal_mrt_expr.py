#!/usr/bin/env python3
"""Lift the exact terminal packed-MRT expression slice of D1 PS 808EE505.

This is deliberately target-specific and fail-closed. It promotes only the acyclic
value path at instructions 437..454 after verifying the exact native instruction
shape, exact material cbuffer value at instruction 436, source-proven AMDGPU value
semantics, native compressed-export flags, and the already-proven persistent kill
relationship. Runtime raster interpolation coefficients remain explicit context.
Compressed exports remain native ordered f16 pairs; RGBA/channel unpacking is not
invented.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path


class DAG:
    def __init__(self):
        self.nodes=[];self.inputs={}
    def node(self,op,args=(),**meta):
        i=len(self.nodes);self.nodes.append({'id':i,'op':op,'args':list(args),**meta});return i
    def inp(self,name):
        if name not in self.inputs:self.inputs[name]=self.node('INPUT',(),name=name)
        return self.inputs[name]
    def const(self,value,**meta):return self.node('CONST',(),value=float(value),**meta)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--ir',type=Path,required=True)
    ap.add_argument('--cbuffer-provenance',type=Path,required=True)
    ap.add_argument('--kill-mask',type=Path,required=True)
    ap.add_argument('--vop-semantics',type=Path,required=True)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args();viol=[];payload={}
    ir=json.load(open(a.ir));cb=json.load(open(a.cbuffer_provenance));km=json.load(open(a.kill_mask));vs=json.load(open(a.vop_semantics))
    try:
        assert ir['status']=='D1_GCN_STRUCTURAL_IR_COMPLETE' and int(ir.get('schema_version',0))>=2
        assert ir['shader']=='808EE505' and ir['instruction_count']==456
        assert cb['status']=='D1_GCN_CBUFFER_PROVENANCE_EXACT' and not cb['violations'] and cb['shader']=='808EE505'
        assert cb['material']=='80D777B6'
        assert km['status']=='D1_GCN_EXPORT_KILL_MASK_CONTRACT_COMPLETE' and not km['violations'] and km['shader']=='808EE505' and km['material']=='80D777B6'
        assert vs['status']=='D1_GCN_VOP_SEMANTICS_SOURCE_PROVEN' and not vs['violations'] and int(vs.get('schema_version',0))>=3
        s=vs['semantics']
        required={
            'v_mad_f32':('MAD','D = S0 * S1 + S2'),
            'v_mac_f32':('MAC','D_new = S0 * S1 + D_old'),
            'v_max_f32':('MAX','D = (S0 >= S1 ? S0 : S1)'),
            'float_clamp':('CLAMP_0_1','D = clamp(D, 0.0, 1.0)'),
            'v_interp_p1_f32':('INTERP_P1','D = P10(attribute) * IJ + P0(attribute)'),
            'v_interp_p2_f32':('INTERP_P2','D_new = P20(attribute) * IJ + D_old'),
            'v_cvt_pkrtz_f16_f32':('PACK_F16_RTZ','D = {f16_rtz(S1), f16_rtz(S0)}'),
            'exp_compr':('COMPRESSED_EXPORT_FLAG','EXP.compr means exported data is compressed'),
            'exp_done':('LAST_EXPORT_FLAG','EXP.done marks the last export operation'),
            'exp_vm':('VALID_EXEC_MASK_FLAG','EXP.vm marks the EXEC mask valid for the export'),
        }
        for k,(op,eq) in required.items():
            assert s[k]['operation']==op and s[k]['equation']==eq,(k,s.get(k))
        assert s['v_cvt_pkrtz_f16_f32']['native_pair_order']==['S1','S0']
        assert s['v_cvt_pkrtz_f16_f32']['rounding']=='TOWARD_ZERO'
        assert s['v_cvt_pkrtz_f16_f32']['portable_channel_mapping']=='WITHHELD'
        assert s['exp_compr']['channel_mapping']=='WITHHELD_NOT_STATED_BY_THIS_SOURCE'

        ins=ir['instructions']
        # Exact target-tail shape. Operand strings are native disassembly operands and
        # are checked before any value-level promotion is emitted.
        expected={
          436:('s_buffer_load_dword',['s0','s[20:23]','0x6d']),
          437:('v_mad_f32',['v7','v10','v3','v26']),
          438:('v_mac_f32',['v13','v14','v4']),
          439:('v_mac_f32',['v15','v12','v5']),
          440:('v_max_f32',['v2','v2','v2 clamp']),
          441:('v_max_f32',['v3','v6','v6 clamp']),
          442:('v_max_f32',['v4','v8','v8 clamp']),
          443:('v_interp_p1_f32',['v0','v0','attr0.w']),
          444:('s_waitcnt',['lgkmcnt(0)']),
          445:('v_mov_b32',['v5','s0']),
          446:('v_interp_p2_f32',['v0','v1','attr0.w']),
          447:('v_cvt_pkrtz_f16_f32',['v1','v2','v3']),
          448:('v_cvt_pkrtz_f16_f32',['v2','v4','v5']),
          449:('exp',['mrt1','v1','v1','v2','v2 compr']),
          450:('s_waitcnt',['expcnt(0)']),
          451:('s_mov_b64',['exec','s[48:49]']),
          452:('v_cvt_pkrtz_f16_f32',['v1','v7','v13']),
          453:('v_cvt_pkrtz_f16_f32',['v0','v15','v0']),
          454:('exp',['mrt0','v1','v1','v0','v0 done compr vm']),
          455:('s_endpgm',[]),
        }
        for i,(op,operands) in expected.items():
            x=ins[i];assert x['opcode']==op and x['operands']==operands,(i,x['opcode'],x['operands'])

        load=next(q for q in cb['loads'] if int(q['instruction'])==436)
        assert load['resolution']=='EXACT_MATERIAL_PS_B0' and load['destination_sgprs']==['s0']
        assert len(load['material_values'])==1
        mv=load['material_values'][0]
        assert mv['vec4_index']==27 and mv['component']=='y' and mv['raw_hex']=='c4c3033f'
        assert abs(float(mv['value'])-0.5147058963775635)<1e-12

        assert len(km['contracts'])==1
        kill=km['contracts'][0]
        governed={int(x['instruction']):x for x in kill['governed_exports']}
        assert set(governed)=={449,454}
        assert kill['predicate']['texture_indices']==[2] and kill['predicate']['threshold']==0.5

        dag=DAG();st={}
        def get(r):
            if r not in st:st[r]=dag.inp(r)
            return st[r]
        def setr(r,n):st[r]=n
        def clamp(n,instruction):return dag.node('CLAMP_0_1',[n],instruction=instruction,source_semantic='float_clamp')
        def pack(dst,s0,s1,instruction):
            # Source says D={f16(S1),f16(S0)}. Args intentionally follow that native
            # packed order, not source operand order and not an inferred RGBA order.
            n=dag.node('PACK_F16_RTZ',[get(s1),get(s0)],instruction=instruction,
                       source_operands={'S0':s0,'S1':s1},native_pair_order=['S1','S0'],
                       rounding='TOWARD_ZERO',compressed_export_intended_use=True,
                       portable_channel_mapping='WITHHELD')
            setr(dst,n);return n

        # 437 MAD.
        setr('v7',dag.node('MAD',[get('v10'),get('v3'),get('v26')],instruction=437))
        # 438/439 MAC retain old destination as the accumulator.
        setr('v13',dag.node('MAC',[get('v14'),get('v4'),get('v13')],instruction=438))
        setr('v15',dag.node('MAC',[get('v12'),get('v5'),get('v15')],instruction=439))
        # 440..442 max followed by the native floating clamp modifier.
        setr('v2',clamp(dag.node('MAX',[get('v2'),get('v2')],instruction=440),440))
        setr('v3',clamp(dag.node('MAX',[get('v6'),get('v6')],instruction=441),441))
        setr('v4',clamp(dag.node('MAX',[get('v8'),get('v8')],instruction=442),442))
        # Raster interpolation coefficients are runtime context, but the equations and
        # textual operand roles are source-proven.
        setr('v0',dag.node('INTERP_P1',[get('v0')],instruction=443,attribute='attr0.w',
                          equation=s['v_interp_p1_f32']['equation'],coefficients='RASTER_INTERPOLATION_CONTEXT'))
        mat=dag.const(mv['value'],instruction=436,source='MATERIAL_PS_B0',vec4_index=27,component='y',raw_hex=mv['raw_hex'])
        setr('s0',mat);setr('v5',mat)
        setr('v0',dag.node('INTERP_P2',[get('v1'),get('v0')],instruction=446,attribute='attr0.w',
                          equation=s['v_interp_p2_f32']['equation'],coefficients='RASTER_INTERPOLATION_CONTEXT',
                          args_meaning=['IJ','D_old']))
        p447=pack('v1','v2','v3',447);p448=pack('v2','v4','v5',448)
        mrt1={
          'instruction':449,'target':'mrt1','compr':True,'done':False,'vm':False,
          'native_operands':ins[449]['operands'][1:],
          'packed_value_roots':[p447,p448],
          'native_packed_registers':['v1','v2'],
          'governed_kill':governed[449],
          'portable_channel_mapping':'WITHHELD_NOT_SOURCE_CLOSED'
        }
        # Snapshot above is immutable because DAG ids preserve pre-overwrite values.
        p452=pack('v1','v7','v13',452);p453=pack('v0','v15','v0',453)
        mrt0={
          'instruction':454,'target':'mrt0','compr':True,'done':True,'vm':True,
          'native_operands':ins[454]['operands'][1:],
          'packed_value_roots':[p452,p453],
          'native_packed_registers':['v1','v0'],
          'governed_kill':governed[454],
          'portable_channel_mapping':'WITHHELD_NOT_SOURCE_CLOSED'
        }
        value_ins=[437,438,439,440,441,442,443,445,446,447,448,449,452,453,454]
        payload={
          'shader':'808EE505','material':'80D777B6','instruction_slice':[436,454],
          'material_constant_load':{'instruction':436,'destination':'s0','value':mv},
          'value_instruction_indices':value_ins,
          'non_value_tail_anchors':[
            {'instruction':444,'kind':'WAIT','opcode':'s_waitcnt'},
            {'instruction':450,'kind':'WAIT','opcode':'s_waitcnt'},
            {'instruction':451,'kind':'EXACT_EXEC_RESTORE','opcode':'s_mov_b64','equation':'EXEC = persistent export mask s[48:49]'},
          ],
          'node_count':len(dag.nodes),'nodes':dag.nodes,'input_roots':dict(sorted(dag.inputs.items())),
          'exports':[mrt1,mrt0],
          'source_semantics':{k:s[k] for k in required},
          'semantic_boundary':{
            'terminal_arithmetic':'EXACT_SOURCE_SEMANTICS',
            'material_scalar_436':'EXACT_MATERIAL_PS_B0',
            'raster_interpolation_equations':'SOURCE_EXACT_COEFFICIENTS_RUNTIME_CONTEXT',
            'packed_f16_native_pair_order':'SOURCE_EXACT',
            'packed_f16_rounding':'SOURCE_EXACT_TOWARD_ZERO',
            'compressed_export_relation':'SOURCE_AND_INSTRUCTION_EXACT',
            'persistent_export_kill_relation':'EXACT_PREVIOUSLY_PROVEN',
            'compressed_export_rgba_channel_unpacking':'WITHHELD_NOT_SOURCE_CLOSED',
            'pre_437_input_value_dataflow':'EXPLICIT_SYMBOLIC_INPUTS'
          }
        }
    except Exception as e:viol.append(repr(e))
    out={'schema_version':1,'status':'D1_GCN_TERMINAL_MRT_PACKED_EXPRESSION_EXACT' if payload and not viol else 'D1_GCN_TERMINAL_MRT_PACKED_EXPRESSION_PARTIAL','expression':payload,'violations':viol,
         'policy':'The terminal MRT slice is promoted only after exact target instruction-shape validation plus source-pinned operation semantics and exact material/kill provenance. Native compressed f16 pair order is preserved; RGBA/channel unpacking is withheld.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':out['status'],'shader':payload.get('shader') if payload else None,'node_count':payload.get('node_count') if payload else None,'value_instruction_count':len(payload.get('value_instruction_indices',[])) if payload else None,'exports':[x.get('target') for x in payload.get('exports',[])] if payload else None,'violations':viol},indent=2));return 0 if not viol else 2
if __name__=='__main__':raise SystemExit(main())
