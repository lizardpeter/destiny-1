#!/usr/bin/env python3
"""Build a PS4-native census of constant-buffer api12 usage.

Consumes exact reports from d1_gcn_constant_buffer_usage_analyze.py and optional
matching CLRX disassembly directories. The census records exact ImmConstBuffer
api12 scalar-buffer accesses and focuses on dwords 28,29,30 because the Crota
high-detail family consumes that contiguous xyz triple on terminal output paths.

No View/camera semantic is assigned by this tool. Such labels remain independent
lineage evidence until a D1 PS4 producer is recovered.
"""
from __future__ import annotations
import argparse,collections,json
from pathlib import Path

TARGET=(28,29,30)

def named_path(raw:str):
 if '=' not in raw:raise argparse.ArgumentTypeError('expected NAME=PATH')
 n,p=raw.split('=',1)
 if not n.strip():raise argparse.ArgumentTypeError('empty corpus name')
 return n.strip(),Path(p)

def covered(load):
 if load.get('dword_indices') is not None:
  return [int(x) for x in load.get('dword_indices') or []]
 off=load.get('static_offset')
 if off is None: off=load.get('offset_dwords')
 if off is None:return []
 w=int(load.get('width_dwords') or 1)
 return list(range(int(off),int(off)+w))

def schema_kind(doc):
 if doc.get('status')=='D1_GCN_CONSTANT_BUFFER_USAGE_ANALYZED':return 'direct'
 if doc.get('status')=='D1_GCN_CBUFFER_USAGE_EXACT':return 'provenance'
 return None

def api12_loads(shader_row,kind):
 if kind=='direct':
  for load in shader_row.get('loads',[]):
   cb=load.get('constant_buffer')
   if cb and int(cb.get('api_slot',-1))==12:
    yield load
 elif kind=='provenance':
  for load in shader_row.get('loads',[]):
   if int(load.get('api_slot',-1))==12:
    yield load

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--input',action='append',required=True,type=named_path)
 ap.add_argument('--disasm',action='append',default=[],type=named_path)
 ap.add_argument('--out',type=Path,required=True)
 a=ap.parse_args()
 ddirs=dict(a.disasm);violations=[];rows=[];unique=set()
 slot12_offsets=collections.Counter();target_hits={x:[] for x in TARGET}
 shader_loads=collections.defaultdict(list)
 docs=[]
 for corpus,path in a.input:
  d=json.loads(path.read_text());docs.append((corpus,d))
  kind=schema_kind(d)
  if kind is None:
   violations.append(f'{corpus}: unsupported usage status {d.get("status")}')
   continue
  for sh in d.get('shaders',[]):
   h=str(sh.get('shader') or '').upper()
   if not h:
    violations.append(f'{corpus}: row without shader');continue
   unique.add(h);local=[]
   lines=None;dd=ddirs.get(corpus)
   if dd is not None:
    p=dd/f'PS_{h}.s'
    if p.exists():lines=p.read_text(errors='replace').splitlines()
   for load in api12_loads(sh,kind):
    cov=covered(load)
    rec={
     'corpus':corpus,'shader':h,'source_usage_schema':kind,
     'line_number':load.get('line_number'),
     'line':load.get('line') or load.get('assembly'),
     'address':load.get('address'),
     'descriptor_start_register':load.get('descriptor_start_register'),
     'descriptor_registers':load.get('descriptor_registers'),
     'width_dwords':int(load.get('width_dwords') or 1),
     'static_offset':load.get('static_offset') if load.get('static_offset') is not None else load.get('offset_dwords'),
     'covered_dword_offsets':cov,
    }
    if lines is not None and load.get('line_number'):
     ln=int(load['line_number']);lo=max(0,ln-5);hi=min(len(lines),ln+4)
     rec['context']=lines[lo:hi]
    local.append(rec);shader_loads[h].append(rec)
    for x in cov:
     slot12_offsets[str(x)]+=1
     if x in target_hits:target_hits[x].append(rec)
   if local:rows.append({'corpus':corpus,'shader':h,'api12_load_count':len(local),'api12_loads':local})
 api12_shaders=sorted(shader_loads)
 target_shader_sets={x:{r['shader'] for r in target_hits[x]} for x in TARGET}
 all_target=sorted(set.intersection(*(target_shader_sets[x] for x in TARGET))) if all(target_shader_sets.values()) else []
 contiguous=[]
 for h in api12_shaders:
  for r in shader_loads[h]:
   cov=set(r['covered_dword_offsets'])
   if set(TARGET).issubset(cov):
    contiguous.append({
     'shader':h,'corpus':r['corpus'],'line_number':r['line_number'],
     'static_offset':r['static_offset'],'width_dwords':r['width_dwords'],
     'covered_dword_offsets':r['covered_dword_offsets'],'line':r['line'],
    })
 out={
  'schema':'d1_ps4_api12_census/v1',
  'status':'D1_PS4_API12_CENSUS_COMPLETE' if rows and not violations else 'D1_PS4_API12_CENSUS_PARTIAL',
  'corpora':[n for n,_ in a.input],
  'corpus_shader_row_count':sum(len(d.get('shaders',[])) for _,d in docs),
  'input_usage_schemas':{corpus:schema_kind(d) for corpus,d in docs},
  'unique_shader_count':len(unique),
  'api12_shader_count':len(api12_shaders),
  'api12_shaders':api12_shaders,
  'api12_dword_load_histogram':dict(sorted(slot12_offsets.items(),key=lambda x:int(x[0]))),
  'target_dwords':list(TARGET),
  'target_dword_hit_counts':{str(x):len(target_hits[x]) for x in TARGET},
  'target_dword_shader_counts':{str(x):len(target_shader_sets[x]) for x in TARGET},
  'shaders_covering_all_target_dwords':all_target,
  'shaders_covering_all_target_dword_count':len(all_target),
  'single_loads_covering_all_target_dwords':contiguous,
  'single_load_covering_all_target_dword_count':len(contiguous),
  'api12_rows':rows,
  'violations':violations,
  'semantic_boundary':{
   'api12_slot':'EXACT_SONY_INPUT_USAGE',
   'dword_offsets':'EXACT_GCN_SCALAR_BUFFER_LOADS',
   'descriptor_spill_tracking':'SUPPORTED_WHEN_INPUT_SCHEMA_IS_PROVENANCE',
   'dword_28_30_semantic':'WITHHELD',
   'View_scope_label':'EXTERNAL_LINEAGE_NOT_PROMOTED_BY_THIS_CENSUS',
   'camera_position_label':'EXTERNAL_LINEAGE_NOT_PROMOTED_BY_THIS_CENSUS',
  },
  'policy':'PS4-native OrbShdr InputUsageSlot plus exact CLRX scalar-buffer loads only. This census measures reuse of api12 and dwords 28-30; it does not assign a producer or semantic name.',
 }
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({
  'status':out['status'],'rows':out['corpus_shader_row_count'],'unique':len(unique),
  'api12_shader_count':len(api12_shaders),'target_dword_hit_counts':out['target_dword_hit_counts'],
  'shaders_covering_28_30':len(all_target),'single_load_covering_28_30':len(contiguous),
  'violations':violations,
 },indent=2))
 return 0 if out['status']=='D1_PS4_API12_CENSUS_COMPLETE' else 2

if __name__=='__main__':raise SystemExit(main())
