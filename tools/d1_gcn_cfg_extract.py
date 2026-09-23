#!/usr/bin/env python3
"""Extract an exact structural CFG from CLRX D1 PS4 GCN disassembly.

This tool is intentionally control-flow structural, not semantic. It:
- parses exact instruction addresses and labels;
- splits basic blocks at branch targets and post-branch fallthroughs;
- records conditional/unconditional branch and fallthrough edges;
- records backward edges as loop/backedge candidates;
- records scalar EXEC-mask operations inside each block.

It does not interpret branch predicates, lane merge values, or shader semantics.
"""
from __future__ import annotations
import argparse,hashlib,json,re
from pathlib import Path

INS=re.compile(r'/\*([0-9A-Fa-f]+):[^*]*\*/\s*(\w+)\s*(.*)$')
LABEL=re.compile(r'^\s*(\.L[0-9A-Za-z_]+):\s*$')
TARGET=re.compile(r'(\.L[0-9A-Za-z_]+)')
COND_PREFIX='s_cbranch'
UNCOND={'s_branch'}
TERMINAL={'s_endpgm','s_setpc_b64'}
EXEC_OP_PREFIX=('s_and_saveexec','s_or_saveexec','s_xor_saveexec','s_andn2_saveexec','s_orn2_saveexec')
EXEC_DIRECT={'s_and_b64','s_andn2_b64','s_or_b64','s_orn2_b64','s_xor_b64','s_xnor_b64','s_mov_b64','s_wqm_b64'}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--disasm',type=Path,required=True);ap.add_argument('--shader',required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 lines=a.disasm.read_text(errors='replace').splitlines()
 pending=[];instructions=[];label_to_addr={}
 for line in lines:
  lm=LABEL.match(line)
  if lm:
   pending.append(lm.group(1));continue
  m=INS.search(line)
  if not m:continue
  addr=int(m.group(1),16);mn=m.group(2);rest=m.group(3).strip()
  for lab in pending:label_to_addr[lab]=addr
  pending=[]
  instructions.append({'address':addr,'address_hex':f'{addr:012X}','mnemonic':mn,'operands':rest,'assembly':line.strip()})
 if not instructions:raise SystemExit('no instructions parsed')
 addr_index={x['address']:i for i,x in enumerate(instructions)}
 leaders={instructions[0]['address']}
 branch_rows=[]
 for idx,ins in enumerate(instructions):
  mn=ins['mnemonic'];iscond=mn.startswith(COND_PREFIX);isun=mn in UNCOND
  if iscond or isun:
   tm=TARGET.search(ins['operands'])
   if not tm:raise SystemExit(f"branch target label missing at {ins['address_hex']}: {ins['assembly']}")
   lab=tm.group(1)
   if lab not in label_to_addr:raise SystemExit(f'unresolved branch label {lab}')
   target=label_to_addr[lab];leaders.add(target)
   fall=instructions[idx+1]['address'] if idx+1<len(instructions) else None
   if fall is not None:leaders.add(fall)
   branch_rows.append({'address':ins['address'],'address_hex':ins['address_hex'],'mnemonic':mn,'target_label':lab,'target_address':target,'target_address_hex':f'{target:012X}','fallthrough_address':fall,'fallthrough_address_hex':f'{fall:012X}' if fall is not None else None,'conditional':iscond})
 leaders=sorted(leaders)
 blocks=[]
 for bi,start in enumerate(leaders):
  end_limit=leaders[bi+1] if bi+1<len(leaders) else None
  rows=[x for x in instructions if x['address']>=start and (end_limit is None or x['address']<end_limit)]
  if not rows:continue
  last=rows[-1];edges=[]
  br=next((x for x in branch_rows if x['address']==last['address']),None)
  if br:
   edges.append({'kind':'branch_true_or_unconditional','target':br['target_address'],'target_hex':br['target_address_hex']})
   if br['conditional'] and br['fallthrough_address'] is not None:
    edges.append({'kind':'fallthrough','target':br['fallthrough_address'],'target_hex':br['fallthrough_address_hex']})
  elif last['mnemonic'] not in TERMINAL:
   nxt=next((x for x in leaders if x>start),None)
   if nxt is not None:edges.append({'kind':'fallthrough','target':nxt,'target_hex':f'{nxt:012X}'})
  execops=[]
  for x in rows:
   mn=x['mnemonic'];op=x['operands'].lower()
   if mn.startswith(EXEC_OP_PREFIX) or (mn in EXEC_DIRECT and ('exec' in op or mn=='s_wqm_b64')):
    execops.append({'address_hex':x['address_hex'],'mnemonic':mn,'operands':x['operands']})
  blocks.append({'id':bi,'start':start,'start_hex':f'{start:012X}','end':last['address'],'end_hex':last['address_hex'],'instruction_count':len(rows),'instructions':rows,'edges':edges,'exec_mask_operations':execops})
 block_starts={x['start'] for x in blocks}
 violations=[]
 for b in blocks:
  for e in b['edges']:
   if e['target'] not in block_starts:violations.append(f"edge {b['start_hex']} -> {e['target_hex']} is not a block start")
 backedges=[]
 for b in blocks:
  for e in b['edges']:
   if e['target']<=b['start']:
    backedges.append({'source_block_start':b['start'],'source_block_start_hex':b['start_hex'],'source_end_hex':b['end_hex'],'target':e['target'],'target_hex':e['target_hex'],'kind':e['kind']})
 norm='\n'.join(f"{x['address_hex']} {x['mnemonic']} {x['operands']}" for x in instructions)
 out={'schema':'d1_gcn_structural_cfg/v1','status':'D1_GCN_STRUCTURAL_CFG_EXACT' if not violations else 'D1_GCN_STRUCTURAL_CFG_PARTIAL',
      'shader':str(a.shader).upper(),'disassembly':str(a.disasm),'instruction_count':len(instructions),'basic_block_count':len(blocks),
      'branch_count':len(branch_rows),'backedge_count':len(backedges),'backedges':backedges,'labels':{k:f'{v:012X}' for k,v in sorted(label_to_addr.items())},
      'blocks':blocks,'normalized_instruction_sha256':hashlib.sha256(norm.encode()).hexdigest(),'violations':violations,
      'semantic_boundary':{'addresses_labels_edges':'EXACT_DISASSEMBLY_STRUCTURE','backedge':'EXACT_ADDRESS_ORDER_RELATION','branch_predicate':'WITHHELD','EXEC_lane_value_semantics':'NOT_INTERPRETED_HERE'},
      'policy':'CFG edges and EXEC-mask instruction locations are structural facts. Predicate/lane value semantics require a separate family proof.'}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'status':out['status'],'instructions':len(instructions),'blocks':len(blocks),'branches':len(branch_rows),'backedges':backedges,'violations':violations},indent=2))
 return 0 if out['status']=='D1_GCN_STRUCTURAL_CFG_EXACT' else 2
if __name__=='__main__':raise SystemExit(main())
