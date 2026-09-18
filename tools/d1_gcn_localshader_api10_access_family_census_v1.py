#!/usr/bin/env python3
"""Cross-corpus census of exact LocalShader API10 access-shape families.

Consumes the independently exact usage-binding and material-chain reports.  It
classifies only structural access counts + descriptor entry windows; it assigns
no backing-buffer or engine semantic meaning.
"""
import argparse,collections,json
from pathlib import Path
STATUS='D1_GCN_LOCALSHADER_API10_ACCESS_FAMILY_CENSUS_EXACT'
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--usage',type=Path,required=True);ap.add_argument('--materials',type=Path,required=True);ap.add_argument('-o','--out',type=Path,required=True);a=ap.parse_args();u=json.loads(a.usage.read_text());m=json.loads(a.materials.read_text());v=[]
 if u.get('status')!='D1_GCN_LOCALSHADER_TBUFFER_USAGE_BINDING_EXACT' or u.get('violations'):v.append('usage_not_exact')
 if m.get('status')!='D1_GCN_LOCALSHADER_API10_MATERIAL_CHAIN_EXACT' or m.get('violations'):v.append('material_chain_not_exact')
 ps=u.get('programs',[]); by={p.get('gcn_sha256'):p for p in ps}
 if len(ps)!=39:v.append(f'program_denominator:{len(ps)}')
 if sum(len(p.get('wrappers',[])) for p in ps)!=56:v.append('wrapper_denominator')
 mat=collections.Counter(); unknown=[]
 for b in m.get('bindings',[]):
  p=by.get(b.get('gcn_sha256'))
  if not p:unknown.append(b.get('gcn_sha256'));continue
  if b.get('descriptor_window')!=p.get('descriptor_window') or b.get('tbuffer_instruction_count')!=p.get('tbuffer_instruction_count'):v.append(f'cross_corpus_drift:{b.get("material")}');continue
  mat[(p['tbuffer_instruction_count'],p['descriptor_window'])]+=1
 if unknown:v.append(f'unknown_material_programs:{len(unknown)}')
 families=[]
 for n in sorted({p['tbuffer_instruction_count'] for p in ps}):
  for w in sorted({p['descriptor_window'] for p in ps if p['tbuffer_instruction_count']==n}):
   q=[p for p in ps if p['tbuffer_instruction_count']==n and p['descriptor_window']==w]
   families.append({'tbuffer_instruction_count':n,'descriptor_window':w,'program_count':len(q),'wrapper_count':sum(len(p['wrappers']) for p in q),'material_occurrence_count':mat[(n,w)],'gcn_sha256':sorted(p['gcn_sha256'] for p in q)})
 expected_counts={3:1,6:1,8:17,12:20}
 if collections.Counter(p['tbuffer_instruction_count'] for p in ps)!=collections.Counter(expected_counts):v.append('instruction_family_program_histogram_drift')
 # Counter(dict) is intentional: keys are counts, values are exact program multiplicities.
 mh=collections.Counter()
 for (n,w),c in mat.items():mh[n]+=c
 if dict(sorted(mh.items()))!={3:14,6:3,8:1320,12:2049}:v.append(f'material_family_histogram_drift:{dict(mh)}')
 out={'schema':'d1_gcn_localshader_api10_access_family_census/v1','status':STATUS if not v else 'D1_GCN_LOCALSHADER_API10_ACCESS_FAMILY_CENSUS_WITH_VIOLATIONS','coverage':{'program_count':len(ps),'wrapper_count':sum(len(p.get('wrappers',[])) for p in ps),'material_occurrence_count':sum(mat.values()),'instruction_count_families':[3,6,8,12],'descriptor_windows':sorted({p['descriptor_window'] for p in ps}),'program_instruction_histogram':{str(k):val for k,val in sorted(collections.Counter(p['tbuffer_instruction_count'] for p in ps).items())},'material_instruction_histogram':{str(k):val for k,val in sorted(mh.items())}},'families':families,'semantic_boundary':{'access_shape':'EXACT','descriptor_entry_window':'EXACT','runtime_writer':'WITHHELD','backing_allocation':'WITHHELD','engine_semantic':'WITHHELD'},'capture_strategy':'A runtime-writer capture corpus must cover both descriptor windows and all four exact TBUFFER-count families (3,6,8,12); a single API10 capture is not sufficient to generalize runtime ownership.','violations':v}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':out['status'],'coverage':out['coverage'],'violations':v},indent=2));return 0 if not v else 2
if __name__=='__main__':raise SystemExit(main())
