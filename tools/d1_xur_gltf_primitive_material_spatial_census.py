#!/usr/bin/env python3
"""Exact primitive/material spatial census for the calibrated Xur GLB carrier.

Outputs every triangle primitive with source material/PS ownership and POSITION
accessor bounds.  The optional high-Z subset is a geometric query only; it does
not assign anatomy or gameplay semantics.
"""
from __future__ import annotations
import argparse,hashlib,json,struct
from pathlib import Path

def read_glb_json(path:Path)->dict:
 raw=path.read_bytes()
 if raw[:4]!=b'glTF' or struct.unpack_from('<I',raw,4)[0]!=2: raise ValueError('not glTF2 GLB')
 n,t=struct.unpack_from('<II',raw,12)
 if t!=0x4E4F534A: raise ValueError('JSON chunk missing')
 return json.loads(raw[20:20+n].decode('utf-8').rstrip(' \t\r\n\0'))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('glb',type=Path);ap.add_argument('-o','--output',type=Path,required=True)
 ap.add_argument('--high-z',type=float,default=1.35)
 a=ap.parse_args();d=read_glb_json(a.glb);viol=[]
 mats=d.get('materials') or []; accs=d.get('accessors') or []
 rows=[]
 for mi,m in enumerate(d.get('meshes') or []):
  for pi,p in enumerate(m.get('primitives') or []):
   pos=(p.get('attributes') or {}).get('POSITION')
   if pos is None: viol.append(f'mesh{mi}:prim{pi}:no_position');continue
   ac=accs[int(pos)];mn=ac.get('min');mx=ac.get('max')
   if not (isinstance(mn,list) and isinstance(mx,list) and len(mn)>=3 and len(mx)>=3):
    viol.append(f'mesh{mi}:prim{pi}:no_bounds');continue
   mati=int(p.get('material',-1));mm=mats[mati] if 0<=mati<len(mats) else {}
   ex=mm.get('extras') or {};idx=p.get('indices');ia=accs[int(idx)] if idx is not None else None
   row={
    'mesh_index':mi,'mesh_name':m.get('name'),'primitive_index':pi,
    'material_index':mati,'material':str(ex.get('d1_material_taghash') or '').upper(),
    'vertex_shader':str(ex.get('d1_vertex_shader') or '').upper(),
    'pixel_shader':str(ex.get('d1_pixel_shader') or '').upper(),
    'native_texture_bindings':ex.get('d1_native_texture_bindings') or [],
    'position_min':[float(x) for x in mn[:3]],'position_max':[float(x) for x in mx[:3]],
    'position_center':[(float(mn[i])+float(mx[i]))*.5 for i in range(3)],
    'position_extent':[float(mx[i])-float(mn[i]) for i in range(3)],
    'vertex_count':int(ac.get('count',0)),'index_count':None if ia is None else int(ia.get('count',0)),
    'triangle_count':None if ia is None or int(p.get('mode',4))!=4 else int(ia.get('count',0))//3,
    'primitive_extras':p.get('extras'),'mesh_extras':m.get('extras')
   }
   rows.append(row)
 rows.sort(key=lambda r:(-r['position_max'][2],r['mesh_index'],r['primitive_index']))
 hi=[r for r in rows if r['position_max'][2]>=a.high_z]
 out={'schema_version':1,'status':'D1_XUR_GLTF_PRIMITIVE_MATERIAL_SPATIAL_CENSUS_EXACT' if not viol else 'D1_XUR_GLTF_PRIMITIVE_MATERIAL_SPATIAL_CENSUS_VIOLATIONS',
      'glb_sha256':hashlib.sha256(a.glb.read_bytes()).hexdigest(),'primitive_count':len(rows),
      'high_z_query':a.high_z,'high_z_primitive_count':len(hi),'high_z_rows':hi,'rows':rows,'violations':viol,
      'policy':'POSITION accessor bounds and glTF material ownership only. high_z is a numeric spatial query and is not an anatomy/visibility semantic.'}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'status':out['status'],'primitive_count':len(rows),'high_z_primitive_count':len(hi),
   'high_z_summary':[{'material':r['material'],'ps':r['pixel_shader'],'mesh':r['mesh_name'],'prim':r['primitive_index'],'min':r['position_min'],'max':r['position_max'],'triangles':r['triangle_count']} for r in hi],
   'violations':viol},indent=2))
 return 0 if not viol else 2
if __name__=='__main__':raise SystemExit(main())
