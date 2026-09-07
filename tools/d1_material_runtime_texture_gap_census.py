#!/usr/bin/env python3
"""Fail-closed census of native PS resource-table indices versus serialized material texture bindings.

Reusable for any D1 material corpus that already has exact material-stage state and
exact native GCN image-resource usage. It does not invent a default texture for a
missing serialized slot; gaps are emitted as runtime descriptor-completion frontiers.
"""
from __future__ import annotations
import argparse,json
from collections import Counter,defaultdict
from pathlib import Path

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--material-state',type=Path,required=True);ap.add_argument('--image-usage',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 st=json.loads(a.material_state.read_text());im=json.loads(a.image_usage.read_text());viol=[]
 if st.get('status')!='D1_MATERIAL_STAGE_STATE_EXACT':viol.append(f"material state status {st.get('status')!r}")
 if im.get('status')!='D1_GCN_IMAGE_RESOURCE_USAGE_EXACT':viol.append(f"image usage status {im.get('status')!r}")
 if im.get('unmatched_image_instruction_count')!=0:viol.append('image usage has unmatched instructions')
 by={r['shader']:r for r in im.get('shaders',[])}
 rows=[];gap_hist=Counter();shader_gaps=defaultdict(list);unused=[]
 for mh,m in sorted((st.get('materials') or {}).items()):
  ps=m['ps'];sh=ps['shader'];ir=by.get(sh)
  if ir is None:viol.append(f'{mh}: PS {sh} missing exact image-usage row');continue
  used=sorted(set(int(x) for x in ir.get('used_texture_indices',[])))
  bound_map={int(x['texture_index']):x['texture'] for x in ps['textures']['items']}
  bound=sorted(bound_map)
  missing=sorted(set(used)-set(bound));extra=sorted(set(bound)-set(used))
  if missing:
   for x in missing:gap_hist[str(x)]+=1
   shader_gaps[sh].append({'material':mh,'missing_texture_indices':missing,'serialized_texture_indices':bound,'native_used_texture_indices':used})
  if extra:unused.append({'material':mh,'shader':sh,'serialized_but_not_native_used_indices':extra})
  rows.append({'material':mh,'shader':sh,'native_used_texture_indices':used,'serialized_texture_indices':bound,'missing_runtime_indices':missing,'serialized_unused_indices':extra,'serialized_texture_bindings':{str(k):v for k,v in sorted(bound_map.items())}})
 if viol:
  out={'schema_version':1,'status':'D1_MATERIAL_RUNTIME_TEXTURE_GAP_CENSUS_PARTIAL','violations':viol};a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));return 2
 out={'schema_version':1,'status':'D1_MATERIAL_RUNTIME_TEXTURE_GAP_CENSUS_EXACT','material_count':len(rows),'shader_count':len({r['shader'] for r in rows}),'materials_with_complete_serialized_native_used_bindings':sum(not r['missing_runtime_indices'] for r in rows),'materials_with_runtime_binding_gaps':sum(bool(r['missing_runtime_indices']) for r in rows),'missing_index_histogram':dict(sorted(gap_hist.items())),'gap_shaders':{k:v for k,v in sorted(shader_gaps.items())},'serialized_but_not_native_used':unused,'rows':rows,'violations':[],'policy':'A gap means the exact GCN uses a resource-table index that is absent from the serialized material texture list. The runtime/default descriptor identity is not guessed. This report is reusable across D1 character, enemy, weapon, prop, and world material corpora once the same exact upstream checkpoints exist.'}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k] for k in ['status','material_count','shader_count','materials_with_complete_serialized_native_used_bindings','materials_with_runtime_binding_gaps','missing_index_histogram','gap_shaders','serialized_but_not_native_used','violations']},indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
