#!/usr/bin/env python3
"""Lift the exact acyclic D1 PS 808EE505 value block at instructions 230..263.

The block reconstructs two raster-interpolated attr vectors, applies exact scalar
MUL/MAC arithmetic, then evaluates fourteen v_madmk_f32 operations. Raster
interpolation coefficients remain explicit symbolic renderer inputs; they are not
replaced by guessed barycentrics or material constants. Incoming VGPR/SGPR values are
also explicit INPUT nodes. The target instruction stream is asserted byte-for-byte at
the opcode/operand level before any expression is promoted.
"""
from __future__ import annotations
import argparse, json, struct
from pathlib import Path


class DAG:
    def __init__(self):
        self.nodes=[]; self.inputs={}; self.cache={}
    def node(self,op,args=(),**meta):
        key=(op,tuple(args),json.dumps(meta,sort_keys=True,separators=(',',':')))
        if op in ('INPUT','CONST') and key in self.cache:return self.cache[key]
        i=len(self.nodes); self.nodes.append({'id':i,'op':op,'args':list(args),**meta}); self.cache[key]=i; return i
    def inp(self,name,**meta):
        key=(name,json.dumps(meta,sort_keys=True,separators=(',',':')))
        if key not in self.inputs:self.inputs[key]=self.node('INPUT',(),name=name,**meta)
        return self.inputs[key]
    def const_hex(self,h,instruction):
        v=struct.unpack('<f',struct.pack('<I',int(h,16)&0xffffffff))[0]
        return self.node('CONST',(),value=float(v),raw_hex=h.lower(),scalar_type='F32',instruction=instruction)


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--ir',type=Path,required=True)
    ap.add_argument('--vop-semantics',type=Path,required=True)
    ap.add_argument('--madmk-semantics',type=Path,required=True)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()
    ir=json.load(open(a.ir)); vs=json.load(open(a.vop_semantics)); ms=json.load(open(a.madmk_semantics)); viol=[]; payload={}
    try:
        assert ir['status']=='D1_GCN_STRUCTURAL_IR_COMPLETE' and int(ir.get('schema_version',0))>=2
        assert ir['shader']=='808EE505' and ir['instruction_count']==456
        assert vs['status']=='D1_GCN_VOP_SEMANTICS_SOURCE_PROVEN' and not vs['violations']
        s=vs['semantics']
        assert s['v_interp_p1_f32']['operation']=='INTERP_P1'
        assert s['v_interp_p1_f32']['equation']=='D = P10(attribute) * IJ + P0(attribute)'
        assert s['v_interp_p2_f32']['operation']=='INTERP_P2'
        assert s['v_interp_p2_f32']['equation']=='D_new = P20(attribute) * IJ + D_old'
        assert s['v_interp_p1_f32']['text_operand_order']=='IJ_VGPR_FIRST_ATTRIBUTE_SECOND'
        assert s['v_interp_p2_f32']['text_operand_order']=='IJ_VGPR_FIRST_ATTRIBUTE_SECOND'
        assert s['v_mul_f32']['operation']=='MUL' and s['v_mul_f32']['equation']=='D = S0 * S1'
        assert s['v_mac_f32']['operation']=='MAC' and s['v_mac_f32']['equation']=='D_new = S0 * S1 + D_old'
        assert ms['status']=='D1_GCN_V_MADMK_F32_SEMANTICS_SOURCE_PROVEN' and not ms['violations']
        msem=ms['semantics']
        assert msem['operation']=='MADMK' and msem['equation']=='D = S0 * K + S1'
        assert msem['constant_kind']=='32_BIT_INLINE_CONSTANT'
        assert msem['input_output_modifiers']=='NOT_SUPPORTED'

        expected={
          230:('v_interp_p1_f32',['v11','v0','attr1.x']),231:('v_interp_p2_f32',['v11','v1','attr1.x']),
          232:('v_interp_p1_f32',['v24','v0','attr1.y']),233:('v_interp_p2_f32',['v24','v1','attr1.y']),
          234:('v_interp_p1_f32',['v25','v0','attr1.z']),235:('v_interp_p2_f32',['v25','v1','attr1.z']),
          236:('v_mul_f32',['v26','s46','v25']),237:('v_mac_f32',['v26','s45','v24']),238:('v_mac_f32',['v26','s44','v11']),
          239:('v_interp_p1_f32',['v27','v0','attr2.x']),240:('v_interp_p2_f32',['v27','v1','attr2.x']),
          241:('v_interp_p1_f32',['v28','v0','attr2.y']),242:('v_interp_p2_f32',['v28','v1','attr2.y']),
          243:('v_interp_p1_f32',['v29','v0','attr2.z']),244:('v_interp_p2_f32',['v29','v1','attr2.z']),
          245:('v_mul_f32',['v30','s46','v29']),246:('v_mac_f32',['v30','s45','v28']),247:('v_mac_f32',['v30','s44','v27']),
          248:('v_mul_f32',['v26','v7','v26']),249:('v_mul_f32',['v7','v7','v30']),
          250:('v_madmk_f32',['v30','v26','0x3f6147ae','v13']),251:('v_madmk_f32',['v31','v7','0x3f6147ae','v15']),
          252:('v_madmk_f32',['v32','v26','0x3f451eb8','v13']),253:('v_madmk_f32',['v33','v7','0x3f451eb8','v15']),
          254:('v_madmk_f32',['v34','v26','0x3f28f5c3','v13']),255:('v_madmk_f32',['v35','v7','0x3f28f5c3','v15']),
          256:('v_madmk_f32',['v36','v26','0x3f0ccccd','v13']),257:('v_madmk_f32',['v37','v7','0x3f0ccccd','v15']),
          258:('v_madmk_f32',['v38','v26','0x3ee147ae','v13']),259:('v_madmk_f32',['v39','v7','0x3ee147ae','v15']),
          260:('v_madmk_f32',['v40','v26','0x3ea8f5c3','v13']),261:('v_madmk_f32',['v41','v7','0x3ea8f5c3','v15']),
          262:('v_madmk_f32',['v13','v26','0x3e6147ae','v13']),263:('v_madmk_f32',['v7','v7','0x3e6147ae','v15']),
        }
        ins=ir['instructions']
        assert sorted(expected)==list(range(230,264))
        for i,(op,operands) in expected.items():
            x=ins[i]; assert x['opcode']==op and x['operands']==operands,(i,x['opcode'],x['operands'])
            assert not x['opcode'].startswith('s_cbranch') and 'exec' not in x.get('defs',[])

        dag=DAG(); st={}
        def get(r):
            if r not in st:st[r]=dag.inp(r,kind='INCOMING_REGISTER')
            return st[r]
        def setr(r,n):st[r]=n
        def coeff(kind,attr):return dag.inp(f'RASTER:{kind}:{attr}',kind='RASTER_INTERPOLATION_COEFFICIENT',coefficient=kind,attribute=attr)
        def interp_p1(dst,ij,attr,idx):
            mul=dag.node('MUL',[coeff('P10',attr),get(ij)],instruction=idx,source_semantic='INTERP_P1')
            setr(dst,dag.node('ADD',[mul,coeff('P0',attr)],instruction=idx,source_semantic='INTERP_P1',attribute=attr,ij_register=ij))
        def interp_p2(dst,ij,attr,idx):
            mul=dag.node('MUL',[coeff('P20',attr),get(ij)],instruction=idx,source_semantic='INTERP_P2')
            setr(dst,dag.node('ADD',[mul,get(dst)],instruction=idx,source_semantic='INTERP_P2',attribute=attr,ij_register=ij))

        for i in range(230,264):
            x=ins[i]; op=x['opcode']; o=x['operands']
            if op=='v_interp_p1_f32':interp_p1(o[0],o[1],o[2],i)
            elif op=='v_interp_p2_f32':interp_p2(o[0],o[1],o[2],i)
            elif op=='v_mul_f32':setr(o[0],dag.node('MUL',[get(o[1]),get(o[2])],instruction=i,source_semantic='V_MUL_F32'))
            elif op=='v_mac_f32':setr(o[0],dag.node('MAC',[get(o[1]),get(o[2]),get(o[0])],instruction=i,source_semantic='V_MAC_F32',equation='S0*S1+D_old'))
            elif op=='v_madmk_f32':
                k=dag.const_hex(o[2],i)
                setr(o[0],dag.node('MADMK',[get(o[1]),k,get(o[3])],instruction=i,source_semantic='V_MADMK_F32',constant_raw_hex=o[2].lower()))
            else:raise ValueError((i,op,o))

        value_indices=list(range(230,264))
        outputs={r:st[r] for r in sorted(st) if r.startswith('v')}
        incoming=sorted(n['name'] for n in dag.nodes if n['op']=='INPUT' and n.get('kind')=='INCOMING_REGISTER')
        raster=sorted(n['name'] for n in dag.nodes if n['op']=='INPUT' and n.get('kind')=='RASTER_INTERPOLATION_COEFFICIENT')
        assert incoming==['s44','s45','s46','v0','v1','v13','v15','v7'],incoming
        assert len(raster)==18 and raster[0].startswith('RASTER:')
        assert len(value_indices)==34
        payload={
          'shader':'808EE505','material':'80D777B6','instruction_range':[230,263],
          'value_instruction_indices':value_indices,'node_count':len(dag.nodes),'nodes':dag.nodes,
          'input_roots':{'incoming_registers':incoming,'raster_interpolation_coefficients':raster},
          'output_register_roots':outputs,
          'source_semantics':{
            'v_interp_p1_f32':s['v_interp_p1_f32'],'v_interp_p2_f32':s['v_interp_p2_f32'],
            'v_mul_f32':s['v_mul_f32'],'v_mac_f32':s['v_mac_f32'],'v_madmk_f32':msem},
          'semantic_boundary':{
            'instructions_230_263_value_arithmetic':'EXACT_SOURCE_SEMANTICS',
            'raster_coefficients':'EXPLICIT_SYMBOLIC_RENDERER_INPUTS',
            'incoming_registers':'EXPLICIT_SYMBOLIC_INPUTS',
            'v_madmk_inline_constants':'EXACT_F32_BIT_PATTERNS',
            'destiny_visual_roles':'WITHHELD','portable_barycentric_reconstruction':'WITHHELD'},
        }
    except Exception as exc:viol.append(repr(exc))
    out={'schema_version':1,'status':'D1_GCN_STRAIGHTLINE_230_263_EXPRESSION_EXACT' if payload and not viol else 'D1_GCN_STRAIGHTLINE_230_263_EXPRESSION_PARTIAL','expression':payload,'violations':viol,'policy':'Only the exact acyclic 230..263 target block is promoted. Raster interpolation coefficients and incoming registers stay explicit symbolic renderer inputs; no material or visual role is guessed.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'status':out['status'],'node_count':payload.get('node_count') if payload else None,'value_instruction_count':len(payload.get('value_instruction_indices',[])) if payload else None,'input_roots':payload.get('input_roots') if payload else None,'violations':viol},indent=2))
    return 0 if not viol else 2


if __name__=='__main__':raise SystemExit(main())
