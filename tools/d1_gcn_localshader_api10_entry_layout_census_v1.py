#!/usr/bin/env python3
"""Census exact OrbShdr entry layouts for LocalShader API10 programs.

Consumes only the already fail-closed LocalShader TBUFFER usage-binding report.  This
narrows the runtime-writer gate without assigning an engine semantic to API10: it proves
whether API10 is delivered as a direct ImmConstBuffer entry descriptor or through a
pointer-table InputUsageSlot.
"""
from __future__ import annotations
import argparse, collections, json
from pathlib import Path

INPUT_SCHEMA='d1_gcn_localshader_tbuffer_usage_binding/v1'
INPUT_STATUS='D1_GCN_LOCALSHADER_TBUFFER_USAGE_BINDING_EXACT'
SCHEMA='d1_gcn_localshader_api10_entry_layout_census/v1'
STATUS='D1_GCN_LOCALSHADER_API10_ENTRY_LAYOUT_CENSUS_EXACT'
EXPECTED_PROGRAMS=39
EXPECTED_WRAPPERS=56
EXPECTED_MATERIALS=3386
EXPECTED_LAYOUTS=2


def build(d:dict)->dict:
    violations=[]
    if d.get('schema')!=INPUT_SCHEMA or d.get('status')!=INPUT_STATUS or d.get('violations'):
        violations.append('input_not_exact')
    rows=[]
    for r in d.get('programs',[]):
        slots=[{'usage_type':int(x[0]),'api_slot':int(x[1]),'start_register':int(x[2]),'raw_hex':str(x[3])} for x in r.get('usage_signature',[])]
        api10=[x for x in slots if x['usage_type']==2 and x['api_slot']==10]
        try: start=int(str(r['descriptor_window']).split('[')[1].split(':')[0])
        except Exception: start=-1
        if len(api10)!=1 or api10[0]['start_register']!=start:
            violations.append(f"api10_descriptor_identity:{r.get('gcn_sha256')}")
        rows.append((r,slots))
    layouts={}
    for r,slots in rows:
        key='|'.join(x['raw_hex'] for x in slots)
        q=layouts.setdefault(key,{'program_count':0,'wrapper_count':0,'material_occurrence_count':0,'descriptor_windows':collections.Counter(),'slots':slots})
        q['program_count']+=1; q['wrapper_count']+=int(r['wrapper_count']); q['material_occurrence_count']+=int(r['material_occurrence_count']); q['descriptor_windows'][r['descriptor_window']]+=1
    cov={
      'api10_program_count':len(rows),
      'api10_wrapper_count':sum(int(r['wrapper_count']) for r,_ in rows),
      'api10_material_occurrence_count':sum(int(r['material_occurrence_count']) for r,_ in rows),
      'api10_usage_layout_count':len(layouts),
      'api10_direct_immconstbuffer_program_count':sum(any(x['usage_type']==2 and x['api_slot']==10 for x in s) for _,s in rows),
      'ptr_const_buffer_table_program_count':sum(any(x['usage_type']==0x16 for x in s) for _,s in rows),
      'ptr_resource_table_program_count':sum(any(x['usage_type']==0x13 for x in s) for _,s in rows),
      'ptr_extended_user_data_program_count':sum(any(x['usage_type']==0x1b for x in s) for _,s in rows),
    }
    if cov['api10_program_count']!=EXPECTED_PROGRAMS: violations.append(f"program_count:{cov['api10_program_count']}")
    if cov['api10_wrapper_count']!=EXPECTED_WRAPPERS: violations.append(f"wrapper_count:{cov['api10_wrapper_count']}")
    if cov['api10_material_occurrence_count']!=EXPECTED_MATERIALS: violations.append(f"material_count:{cov['api10_material_occurrence_count']}")
    if cov['api10_usage_layout_count']!=EXPECTED_LAYOUTS: violations.append(f"layout_count:{cov['api10_usage_layout_count']}")
    if cov['api10_direct_immconstbuffer_program_count']!=EXPECTED_PROGRAMS: violations.append('api10_not_direct_for_all_programs')
    if cov['ptr_const_buffer_table_program_count'] or cov['ptr_resource_table_program_count']: violations.append('unexpected_api_table_pointer_layout')
    out_layouts=[]
    for _,q in sorted(layouts.items()):
        q=dict(q); q['descriptor_windows']=dict(sorted(q['descriptor_windows'].items())); out_layouts.append(q)
    return {'schema':SCHEMA,'status':STATUS if not violations else 'D1_GCN_LOCALSHADER_API10_ENTRY_LAYOUT_CENSUS_WITH_VIOLATIONS','coverage':cov,'layouts':out_layouts,'violations':violations,'semantic_boundary':{'api10_delivery':'EXACT_DIRECT_IMMCONSTBUFFER_PROGRAM_ENTRY_USER_DATA' if not violations else 'NOT_PROMOTED','api10_table_indirection':'ABSENT_FROM_EXACT_API10_INPUT_USAGE_LAYOUTS' if not violations else 'NOT_PROMOTED','runtime_writer':'WITHHELD','backing_memory_semantics':'WITHHELD'},'policy':'InputUsageSlot identity plus exact unmutated entry-state provenance only. Absence of pointer-table usage narrows the runtime writer to direct user-data population; it does not identify the engine owner, backing address, buffer contents, or semantic role.'}


def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('usage',type=Path); ap.add_argument('-o','--output',type=Path,required=True); a=ap.parse_args()
    out=build(json.loads(a.usage.read_text())); a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(json.dumps({'status':out['status'],'coverage':out['coverage'],'violations':out['violations']},indent=2,sort_keys=True)); return 0 if out['status']==STATUS else 2
if __name__=='__main__': raise SystemExit(main())
