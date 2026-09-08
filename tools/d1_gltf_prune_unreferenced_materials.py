#!/usr/bin/env python3
"""Prune unreferenced glTF Material table entries without touching binary data.

Only `mesh.primitives[*].material` references are rewritten. The tool refuses GLBs
whose material indices appear in material-variant extensions, because those would need
additional remapping. Geometry, accessors, nodes, skins, animations, bufferViews and
all non-JSON GLB chunks remain unchanged.
"""
from __future__ import annotations
import argparse,copy,hashlib,json
from pathlib import Path
from d1_gltf_apply_tower_actor_material_signatures import read_glb,write_glb,structural_fingerprint

def main():
 ap=argparse.ArgumentParser();ap.add_argument('input',type=Path);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--report',type=Path,required=True);a=ap.parse_args()
 doc,chunks=read_glb(a.input);viol=[]
 exts=set(doc.get('extensionsUsed') or [])|set(doc.get('extensionsRequired') or [])
 if 'KHR_materials_variants' in exts:viol.append('KHR_materials_variants_not_supported_for_prune')
 mats=list(doc.get('materials') or []);used=set()
 for mi,m in enumerate(doc.get('meshes',[])):
  for pi,p in enumerate(m.get('primitives',[])):
   if 'material' not in p:continue
   idx=int(p['material'])
   if idx<0 or idx>=len(mats):viol.append(f'mesh{mi}:prim{pi}:material_index_oob:{idx}')
   else:used.add(idx)
 if not viol:
  keep=sorted(used);remap={old:new for new,old in enumerate(keep)};before=structural_fingerprint(doc)
  outdoc=copy.deepcopy(doc);outdoc['materials']=[copy.deepcopy(mats[i]) for i in keep]
  for m in outdoc.get('meshes',[]):
   for p in m.get('primitives',[]):
    if 'material' in p:p['material']=remap[int(p['material'])]
  # structural_fingerprint intentionally excludes primitive material indices/material table.
  if structural_fingerprint(outdoc)!=before:viol.append('non_material_structure_changed')
 else:outdoc=doc;keep=[];remap={}
 nonjson_before=hashlib.sha256(b''.join(t+d for t,d in chunks[1:])).hexdigest()
 if not viol:
  write_glb(a.out,outdoc,chunks);check,c2=read_glb(a.out)
  nonjson_after=hashlib.sha256(b''.join(t+d for t,d in c2[1:])).hexdigest()
  if nonjson_after!=nonjson_before:viol.append('non_json_chunks_changed')
  if structural_fingerprint(check)!=structural_fingerprint(doc):viol.append('roundtrip_non_material_structure_changed')
 else:nonjson_after=None
 report={'schema_version':1,'status':'D1_GLTF_UNREFERENCED_MATERIALS_PRUNED' if not viol else 'D1_GLTF_UNREFERENCED_MATERIAL_PRUNE_VIOLATIONS','input':str(a.input),'output':str(a.out),'input_material_count':len(mats),'referenced_input_material_count':len(used),'output_material_count':len(outdoc.get('materials',[])) if not viol else None,'removed_material_count':len(mats)-len(used),'kept_old_indices':keep,'index_remap':{str(k):v for k,v in remap.items()},'non_json_chunks_sha256_before':nonjson_before,'non_json_chunks_sha256_after':nonjson_after,'violations':viol}
 a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({k:report[k] for k in ('status','input_material_count','referenced_input_material_count','output_material_count','removed_material_count','violations')},indent=2))
 return 0 if not viol else 2
if __name__=='__main__':raise SystemExit(main())
