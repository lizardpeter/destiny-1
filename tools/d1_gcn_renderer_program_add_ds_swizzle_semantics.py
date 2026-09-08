#!/usr/bin/env python3
"""Close the eight 808EE505 DS quad-permute instructions from pinned GCN sources."""
from __future__ import annotations
import argparse,collections,copy,hashlib,json,re
from pathlib import Path
GEM5_REV='f5c5a6e390f55dd5984977815bf9d0bd05da6945'
LLVM_REV='1462d6f99a0cdf8c99108cb32eb020efe6ba5f89'
TARGET=[63,64,65,66,74,75,76,77]
RX=re.compile(r'^ds_swizzle_b32\s+(v\d+),\s+(v\d+)\s+offset:(\d+)$')

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def contiguous(v):
 v=sorted(set(v));o=[]
 if not v:return o
 a=b=v[0]
 for x in v[1:]:
  if x==b+1:b=x
  else:o.append((a,b));a=b=x
 o.append((a,b));return o

def main()->int:
 ap=argparse.ArgumentParser();ap.add_argument('--program',type=Path,required=True);ap.add_argument('--ir',type=Path,required=True);ap.add_argument('--gem5-ds',type=Path,required=True);ap.add_argument('--llvm-sidefines',type=Path,required=True);ap.add_argument('--llvm-printer',type=Path,required=True);ap.add_argument('-o','--output',type=Path,required=True);a=ap.parse_args();viol=[];result={}
 try:
  base=json.load(open(a.program));ir=json.load(open(a.ir));p=base['program'];c=p['coverage']
  assert base['status']=='D1_GCN_RENDERER_PROGRAM_IR_EXACT_PARTIAL' and not base['violations']
  assert c['primary_resolution_counts']=={'CONTROL_EXACT':47,'EXPRESSION_EXACT':293,'INPUT_PROVENANCE_EXACT':70,'RECURRENCE_EXACT':36,'STRUCTURAL_ONLY':10};assert c['exact_nonstructural_instruction_count']==446
  assert ir['status']=='D1_GCN_STRUCTURAL_IR_COMPLETE' and ir['shader']=='808EE505' and ir['instruction_count']==456
  g=a.gem5_ds.read_text();sd=a.llvm_sidefines.read_text();pr=a.llvm_printer.read_text()
  assert 'RETURN_DATA = swizzle(vgpr_data, offset1:offset0).' in g
  for s in ['QUAD_PERM_ENC         = 0x8000','QUAD_PERM_ENC_MASK    = 0xFF00','LANE_MASK             = 0x3','LANE_SHIFT            = 2','LANE_NUM              = 4']:assert s in sd,s
  for s in ['(Imm & QUAD_PERM_ENC_MASK) == QUAD_PERM_ENC','for (unsigned I = 0; I < LANE_NUM; ++I)','formatDec(Imm & LANE_MASK)','Imm >>= LANE_SHIFT']:assert s in pr,s
  src={'gem5_ds':{'revision':GEM5_REV,'sha256':sha(a.gem5_ds)},'llvm_sidefines':{'revision':LLVM_REV,'sha256':sha(a.llvm_sidefines)},'llvm_inst_printer':{'revision':LLVM_REV,'sha256':sha(a.llvm_printer)}}
  out=copy.deepcopy(base);op=out['program'];rows=op['instruction_resolution'];ins=ir['instructions'];contracts=[]
  structural=[i for i,r in enumerate(rows) if r['primary_resolution']=='STRUCTURAL_ONLY'];assert structural==TARGET+[212,213],structural
  expected_offsets={63:0x8055,64:0x8000,65:0x8055,66:0x8000,74:0x80AA,75:0x8000,76:0x80AA,77:0x8000}
  for i in TARGET:
   x=ins[i];asm=x['assembly'].split('*/',1)[-1].strip();m=RX.fullmatch(asm);assert m,(i,asm);dst,srcv,dec=m.groups();imm=int(dec);assert imm==expected_offsets[i],(i,hex(imm))
   assert (imm & 0xFF00)==0x8000,(i,hex(imm));q=imm;selectors=[]
   for _ in range(4):selectors.append(q & 0x3);q >>= 2
   # Exact lane rule: each lane keeps its quad base and selects one of the four lanes from the low-byte 2-bit field for its lane-in-quad.
   r=rows[i];r['primary_resolution']='EXPRESSION_EXACT';r['evidence_tags']=sorted(set(r.get('evidence_tags',[])+['DS_SWIZZLE_QUAD_PERM_SOURCE_EXACT','GCN_CROSS_LANE_EXPRESSION_EXACT']))
   contracts.append({'instruction':i,'address':x['address_hex'],'assembly':asm,'destination':dst,'source':srcv,'offset':imm,'offset_hex':f'0x{imm:04X}','mode':'QUAD_PERM','lane_selectors':selectors,'expression':'D[lane] = S[(lane & ~3) | selector[lane & 3]]','source_provenance':src})
  assert [x['lane_selectors'] for x in contracts]==[[1,1,1,1],[0,0,0,0],[1,1,1,1],[0,0,0,0],[2,2,2,2],[0,0,0,0],[2,2,2,2],[0,0,0,0]]
  op['ds_swizzle_quad_perm_contracts']=contracts
  rem=[i for i,r in enumerate(rows) if r['primary_resolution']=='STRUCTURAL_ONLY'];assert rem==[212,213]
  counts=collections.Counter(r['primary_resolution'] for r in rows);oc=op['coverage'];oc['primary_resolution_counts']=dict(sorted(counts.items()));oc['exact_nonstructural_instruction_count']=456-counts['STRUCTURAL_ONLY'];oc['structural_only_instruction_count']=counts['STRUCTURAL_ONLY'];oc['ds_swizzle_semantics_promoted_instructions']=TARGET;oc['ds_swizzle_semantics_promoted_instruction_count']=8
  oc['structural_only_spans']=[{'start_instruction':212,'end_instruction':213,'instruction_count':2,'opcode_histogram':{'image_sample':2},'image_instructions':[212,213],'branch_instructions':[],'exec_write_instructions':[],'boundary':'STRUCTURAL_ONLY_IMAGE_SAMPLE_SEMANTICS_FRONTIER'}]
  expected={'CONTROL_EXACT':47,'EXPRESSION_EXACT':301,'INPUT_PROVENANCE_EXACT':70,'RECURRENCE_EXACT':36,'STRUCTURAL_ONLY':2};assert oc['primary_resolution_counts']==expected;assert oc['exact_nonstructural_instruction_count']==454
  out['schema_version']=max(9,int(out.get('schema_version',0)));out.setdefault('semantic_boundary',{})['ds_swizzle_quad_perm']='EXACT_ALL_8';out['semantic_boundary']['remaining_structural_frontier']='2_IMAGE_SAMPLE';result=out;result['violations']=[]
 except Exception as e:
  viol=[repr(e)];result={'schema_version':1,'status':'D1_GCN_RENDERER_DS_SWIZZLE_SEMANTICS_PARTIAL','violations':viol}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':result.get('status'),'coverage':result.get('program',{}).get('coverage',{}).get('primary_resolution_counts'),'exact_nonstructural':result.get('program',{}).get('coverage',{}).get('exact_nonstructural_instruction_count'),'violations':viol},indent=2));return 0 if not viol else 2
if __name__=='__main__':raise SystemExit(main())
