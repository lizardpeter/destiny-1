#!/usr/bin/env python3
"""Census exact PS4 ROI material peers for pixel shader 8087670E.

Scans every available SMaterial_ROI entry in supplied physical package snapshots,
decodes only the binary material schema, and records exact t# bindings for all
materials using the target shader. No missing-resource/default binding is inferred.
"""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import d1_tower_map_schema_validate_v5 as v5
from d1_material_decode import parse_material

MAT_CLASS='80801AD7'; TARGET_PS='8087670E'
def norm(x):return str(x).upper().removeprefix('0X').zfill(8)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--snapshot',type=Path,action='append',required=True);ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 c=v5.v3.base.Corpus([p.resolve() for p in a.snapshot],a.runtime.resolve())
 rows=[];mat_total=0;decode_errors=[]
 for p,r in c.readers:
  for e in r.entries:
   if norm(e.get('reference',''))!=MAT_CLASS:continue
   mat_total+=1
   if not r.available(e['index']):continue
   try:b=r.entry(e['index']);m=parse_material(b,'PS4')
   except Exception as ex:
    decode_errors.append({'snapshot':p.name,'tag_hash':norm(e.get('tag_hash','')),'index':int(e['index']),'error':repr(ex)});continue
   if norm(m.get('pixel_shader',''))!=TARGET_PS:continue
   rows.append({
    'snapshot':p.name,'package_id':f"{int(r.h['pkg_id']):04X}",'entry_index':int(e['index']),'material':norm(e['tag_hash']),
    'file_size':int(e['file_size']),'pixel_shader':norm(m['pixel_shader']),'vertex_shader':norm(m['vertex_shader']),
    'material_state':{'unk08':m['unk08'],'unk0c':m['unk0c'],'unk10':m['unk10'],'unk20_hex':m['unk20_hex']},
    'ps_texture_count':int(m['ps_textures']['count']),
    'ps_textures':[{'texture_index':int(x['texture_index']),'texture':norm(x['texture'])} for x in m['ps_textures']['items']],
    'ps_sampler_count':int(m['ps_samplers']['count']),
    'ps_sampler_first_dwords':[norm(x['first_dword_hex']) for x in m['ps_samplers']['items']],
    'ps_tfx_bytes_hex':m['ps_tfx_bytecode']['bytes_hex'],
   })
 rows.sort(key=lambda x:(x['material'],x['snapshot']))
 unique=sorted({x['material'] for x in rows});maps={}
 for h in unique:
  sigs={tuple((x['texture_index'],x['texture']) for x in r['ps_textures']) for r in rows if r['material']==h}
  maps[h]=[list(map(list,s)) for s in sorted(sigs)]
 t4_rows=[r for r in rows if any(x['texture_index']==4 for x in r['ps_textures'])]
 missing_t4=[r for r in rows if not any(x['texture_index']==4 for x in r['ps_textures'])]
 out={'schema_version':1,'status':'D1_PS_8087670E_PEER_MATERIAL_CENSUS_EXACT' if rows else 'D1_PS_8087670E_PEER_MATERIAL_CENSUS_NO_HITS','scanned_material_entry_count':mat_total,'decode_error_count':len(decode_errors),'decode_errors':decode_errors,'physical_occurrence_count':len(rows),'unique_material_count':len(unique),'unique_materials':unique,'rows':rows,'per_material_texture_maps':maps,'t4_serialized_occurrence_count':len(t4_rows),'t4_serialized_rows':t4_rows,'t4_absent_occurrence_count':len(missing_t4),'t4_absent_rows':missing_t4,'policy':'Physical package/material census only. Absence of serialized t4 is not interpreted as a default resource value.'}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k] for k in ['status','scanned_material_entry_count','decode_error_count','physical_occurrence_count','unique_material_count','unique_materials','t4_serialized_occurrence_count','t4_absent_occurrence_count']},indent=2));return 0 if rows else 2
if __name__=='__main__':raise SystemExit(main())
