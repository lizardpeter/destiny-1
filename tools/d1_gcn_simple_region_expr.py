#!/usr/bin/env python3
"""Lift a proven simple D1 GCN EXEC region into a destination-neutral expression DAG.

Scope is intentionally bounded: one saveexec/complement/restore region already marked
EXACT_SIMPLE_LANE_MERGE by d1_gcn_exec_region_ir. The two arms are evaluated from the
same incoming register state and joined with explicit SELECT nodes. Supported float
arithmetic, exact image samples, source-proven material cbuffer scalars, EXP2 and
floating clamp are lifted. Unknown incoming values remain named INPUT nodes.

Loops, nested EXEC regions, unsupported instructions and guessed material meanings are
rejected rather than silently approximated.
"""
from __future__ import annotations
import argparse,json,re,struct
from pathlib import Path

VRANGE=re.compile(r'^v\[(\d+):(\d+)\]$');SRANGE=re.compile(r'^s\[(\d+):(\d+)\]$');REG=re.compile(r'^[vs]\d+$')

class DAG:
    def __init__(self):self.nodes=[];self.cache={}
    def node(self,op,args=(),**meta):
        key=(op,tuple(args),json.dumps(meta,sort_keys=True,separators=(',',':')))
        if op in ('CONST','INPUT') and key in self.cache:return self.cache[key]
        i=len(self.nodes);self.nodes.append({'id':i,'op':op,'args':list(args),**meta});self.cache[key]=i;return i
    def const(self,v,**meta):return self.node('CONST',(),value=float(v),**meta)
    def inp(self,name):return self.node('INPUT',(),name=name)

def f32hex(t):return struct.unpack('<f',struct.pack('<I',int(t,16)&0xffffffff))[0]
def expand_range(t):
    m=VRANGE.match(t) or SRANGE.match(t)
    if not m:return [t]
    p=t[0];return [f'{p}{i}' for i in range(int(m.group(1)),int(m.group(2))+1)]
def stripmods(t):
    t=t.strip();clamp=False
    if t.endswith(' clamp'):t=t[:-6].rstrip();clamp=True
    neg=t.startswith('-');t=t[1:] if neg else t
    return t,neg,clamp

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--ir',type=Path,required=True);ap.add_argument('--exec-regions',type=Path,required=True);ap.add_argument('--cbuffer-provenance',type=Path,required=True);ap.add_argument('--vop-semantics',type=Path,required=True);ap.add_argument('--region-id',type=int,required=True);ap.add_argument('-o','--output',type=Path,required=True);a=ap.parse_args()
    ir=json.load(open(a.ir));er=json.load(open(a.exec_regions));cb=json.load(open(a.cbuffer_provenance));vs=json.load(open(a.vop_semantics));viol=[];payload={}
    try:
        assert ir['status']=='D1_GCN_STRUCTURAL_IR_COMPLETE' and int(ir.get('schema_version',0))>=2
        assert er['status']=='D1_GCN_EXEC_REGION_IR_COMPLETE' and not er['violations'] and er['shader']==ir['shader']
        assert cb['status']=='D1_GCN_CBUFFER_PROVENANCE_EXACT' and not cb['violations'] and cb['shader']==ir['shader']
        assert vs['status']=='D1_GCN_VOP_SEMANTICS_SOURCE_PROVEN' and not vs['violations']
        assert vs['semantics']['v_exp_f32']['operation']=='EXP2' and vs['semantics']['float_clamp']['operation']=='CLAMP_0_1'
        region=next((r for r in er['regions'] if int(r['region_id'])==a.region_id),None);assert region is not None
        assert region['promotion']=='EXACT_SIMPLE_LANE_MERGE' and not region['nested_saveexec_instructions'] and not region['loop_intersections']
        assert region['then_range'] and region['else_range'],'IF_THEN_ELSE region required'
        ins=ir['instructions'];dag=DAG();entry={};sample_nodes=[];unsupported=[]
        cbi={int(r['instruction']):r for r in cb['loads'] if r.get('resolution')=='EXACT_MATERIAL_PS_B0'}
        def get(st,r):
            if r not in st:st[r]=dag.inp(r)
            return st[r]
        def source(st,t,float_context=True):
            base,neg,cl=stripmods(t)
            if REG.match(base):n=get(st,base)
            elif base.lower().startswith('0x'):
                n=dag.const(f32hex(base) if float_context else int(base,16),raw_literal=base)
            else:
                try:n=dag.const(float(base))
                except:n=dag.inp(base)
            if neg:n=dag.node('NEG',[n])
            return n,cl
        def coord_nodes(st,t):return [get(st,r) for r in expand_range(t)]
        def eval_arm(lo,hi):
            st=dict(entry)
            for x in ins[lo:hi+1]:
                op=x['opcode'];o=x['operands'];idx=x['index']
                if idx in cbi:
                    r=cbi[idx];vals=r['material_values'];dregs=r['destination_sgprs'];assert len(vals)==len(dregs)
                    for dr,mv in zip(dregs,vals):st[dr]=dag.const(mv['value'],source='MATERIAL_PS_B0',scalar_index=r['offset_dwords']+dregs.index(dr),vec4_index=mv['vec4_index'],component=mv['component'],raw_hex=mv['raw_hex'])
                    continue
                if 'image' in x:
                    z=x['image'];chs=str(z.get('dmask_channels') or '')
                    dests=expand_range(o[0]);coord=coord_nodes(st,o[1]) if len(o)>1 else []
                    if len(chs)!=len(dests):
                        if len(chs)==1 and len(dests)==1:pass
                        else:raise ValueError(f'{idx}: image destination/dmask width unsupported {dests}/{chs}')
                    for j,dst in enumerate(dests):
                        n=dag.node('SAMPLE',coord,texture_indices=z.get('textures',[]),sampler_indices=z.get('samplers',[]),channel=chs[j] if j<len(chs) else None,instruction=idx,address=x['address_hex'],coordinate_operand=o[1] if len(o)>1 else None)
                        st[dst]=n;sample_nodes.append(n)
                    continue
                if op in ('s_waitcnt','s_load_dwordx4','s_load_dwordx8','s_cbranch_execz','s_andn2_b64','s_mov_b64'):continue
                if not o:continue
                dst=o[0]
                if op=='v_mov_b32':st[dst]=source(st,o[1],True)[0]
                elif op=='v_add_f32':st[dst]=dag.node('ADD',[source(st,o[1])[0],source(st,o[2])[0]])
                elif op=='v_mul_f32':st[dst]=dag.node('MUL',[source(st,o[1])[0],source(st,o[2])[0]])
                elif op=='v_sub_f32':st[dst]=dag.node('SUB',[source(st,o[1])[0],source(st,o[2])[0]])
                elif op=='v_subrev_f32':st[dst]=dag.node('SUB',[source(st,o[2])[0],source(st,o[1])[0]])
                elif op=='v_max_f32':st[dst]=dag.node('MAX',[source(st,o[1])[0],source(st,o[2])[0]])
                elif op=='v_mac_f32':st[dst]=dag.node('ADD',[get(st,dst),dag.node('MUL',[source(st,o[1])[0],source(st,o[2])[0]])])
                elif op=='v_exp_f32':
                    src,cl=source(st,o[1]);n=dag.node('EXP2',[src],source_semantic='V_EXP_F32')
                    if cl:n=dag.node('CLAMP_0_1',[n],source_semantic='FLOAT_CLAMP')
                    st[dst]=n
                else:unsupported.append({'instruction':idx,'opcode':op,'operands':o})
            return st
        # Seed only when used; both arms then see the same INPUT node ids through DAG caching.
        then=eval_arm(*region['then_range']);els=eval_arm(*region['else_range'])
        if unsupported:raise ValueError(f'unsupported instructions in simple region: {unsupported}')
        pred=region['predicate'];lhs=source(entry,pred['lhs'])[0];rhs=source(entry,pred['rhs'])[0]
        pnode=dag.node('CMP',[lhs,rhs],operator=pred['operator'],instruction=pred['instruction'],expression=pred['expression'])
        merges={}
        for m in region['lane_merges']:
            r=m['register'];merges[r]=dag.node('SELECT',[pnode,get(then,r),get(els,r)],predicate_expression=pred['expression'])
        pats=region.get('promoted_patterns') or [];factor_roots=[]
        for p in pats:
            if p['kind']=='CONDITIONAL_MULTIPLY_OR_PASSTHROUGH':factor_roots.append({'register':p['factor_register'],'node':get(then,p['factor_register'])})
        payload={'shader':ir['shader'],'region_id':region['region_id'],'predicate_node':pnode,'predicate':pred,'node_count':len(dag.nodes),'nodes':dag.nodes,
                 'sample_node_ids':sorted(set(sample_nodes)),'sample_count':len(sample_nodes),'lane_merge_roots':merges,'promoted_factor_roots':factor_roots,
                 'then_range':region['then_range'],'else_range':region['else_range'],'source_semantics':vs['semantics'],
                 'semantic_boundary':{'incoming_registers':'EXPLICIT_INPUT_NODES','simple_region_arithmetic':'EXACT','image_coordinates':'EXACT_REGISTER_EXPRESSION_OR_INPUT','loop_values':'OUT_OF_SCOPE','nested_exec':'OUT_OF_SCOPE','material_roles':'UNASSIGNED'}}
    except Exception as e:viol.append(repr(e))
    out={'schema_version':1,'status':'D1_GCN_SIMPLE_REGION_EXPRESSION_DAG_EXACT' if payload and not viol else 'D1_GCN_SIMPLE_REGION_EXPRESSION_DAG_PARTIAL','expression':payload,'violations':viol,
         'policy':'Only an EXEC region already proven simple is lifted. Unsupported instructions, loops and nested EXEC fail closed. Samples keep native t#/sampler provenance; incoming values stay symbolic. EXP2/clamp semantics must come from the pinned ISA source proof.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':out['status'],'shader':payload.get('shader') if payload else None,'region_id':payload.get('region_id') if payload else None,'node_count':payload.get('node_count') if payload else None,'sample_count':payload.get('sample_count') if payload else None,'lane_merge_roots':payload.get('lane_merge_roots') if payload else None,'promoted_factor_roots':payload.get('promoted_factor_roots') if payload else None,'violations':viol},indent=2));return 0 if not viol else 2
if __name__=='__main__':raise SystemExit(main())
