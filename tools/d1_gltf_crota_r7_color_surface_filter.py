#!/usr/bin/env python3
"""Build Crota Blender-facing color-surface views from the exact R6 GLB.

The R6 source GLB intentionally preserves all nine source-valid MostDetailed ranges.
Three of those ranges are native prepass/control geometry which geometrically overlaps
three color-pass ranges.  Drawing both as conventional glTF PBR surfaces causes
viewer z-fighting and false mottled coloration.

This adapter does not delete exact native resources.  It only removes the three
prepass mesh nodes from the active scene-root child list while retaining their nodes,
meshes, materials, textures, and native-shader extras in the GLB as unreachable proof
objects.  Six disjoint color-surface nodes remain visible.

For animation inspection it can also expose only one exact source-selected clip or
reorder that exact clip first.  No animation samples are changed.
"""
from __future__ import annotations
import argparse, hashlib, json, struct
from pathlib import Path

PREPASS_MATERIALS={'8108E667','8108E66B'}
VISIBLE_MATERIALS={'8108E7A9','8108E7AA','8108E7B1','8108E7B2','8108E7B3'}
VISIBLE_NODE_NAMES={
 '8108E5B7_mesh0_range0_19166',
 '8108E5B7_mesh0_range38347_12968',
 '8108E5B7_mesh2_range30_14',
 '8108E5B7_mesh2_range4254_14810',
 '8108E5B7_mesh2_range19667_2486',
 '8108E5B7_mesh2_range45583_4904',
}
HIDDEN_NODE_NAMES={
 '8108E5B7_mesh0_range19167_19179',
 '8108E5B7_mesh2_range26392_14800',
 '8108E5B7_mesh2_range41792_2479',
}
PREVIEW_CLIP='809D9D19'


def read_glb(p:Path):
 b=p.read_bytes();
 if b[:4]!=b'glTF': raise ValueError('not GLB')
 jl,jt=struct.unpack_from('<II',b,12)
 if jt!=0x4E4F534A: raise ValueError('missing JSON chunk')
 doc=json.loads(b[20:20+jl].decode().rstrip(' \x00'))
 bo=20+jl; bl,bt=struct.unpack_from('<II',b,bo)
 if bt!=0x004E4942: raise ValueError('missing BIN chunk')
 return doc,b[bo+8:bo+8+bl]

def write_glb(p:Path,d:dict,blob:bytes):
 j=json.dumps(d,separators=(',',':'),ensure_ascii=False).encode();j+=b' ' *((4-len(j)%4)%4)
 bb=blob+b'\x00'*((4-len(blob)%4)%4)
 out=bytearray(struct.pack('<4sII',b'glTF',2,12+8+len(j)+8+len(bb)))
 out+=struct.pack('<II',len(j),0x4E4F534A)+j+struct.pack('<II',len(bb),0x004E4942)+bb
 p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(out)

def mat_tag(doc,mesh_idx):
 prim=doc['meshes'][mesh_idx]['primitives'][0]; mi=prim.get('material')
 if mi is None:return None
 return str(doc['materials'][mi].get('extras',{}).get('d1_material_taghash','')).upper()

def main():
 ap=argparse.ArgumentParser();ap.add_argument('input',type=Path);ap.add_argument('--mode',choices=('none','one','all-preview-first'),required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--report',type=Path,required=True);a=ap.parse_args()
 doc,blob=read_glb(a.input)
 si=int(doc.get('scene',0)); roots=doc['scenes'][si].get('nodes',[])
 if len(roots)!=1: raise SystemExit(f'expected one portable scene root, got {roots}')
 root=roots[0]; rn=doc['nodes'][root]
 if rn.get('name')!='D1_ZUP_TO_GLTF_YUP': raise SystemExit('portable root drift')
 children=list(rn.get('children',[])); mesh_children=[x for x in children if doc['nodes'][x].get('mesh') is not None]
 if len(mesh_children)!=9: raise SystemExit(f'expected 9 exact source mesh nodes, got {len(mesh_children)}')
 visible=[]; hidden=[]
 for ni in mesh_children:
  n=doc['nodes'][ni]; name=str(n.get('name')); tag=mat_tag(doc,int(n['mesh']))
  if tag in PREPASS_MATERIALS:
   if name not in HIDDEN_NODE_NAMES: raise SystemExit(f'unexpected prepass node {name}/{tag}')
   hidden.append(ni)
  else:
   if tag not in VISIBLE_MATERIALS or name not in VISIBLE_NODE_NAMES: raise SystemExit(f'unexpected color node {name}/{tag}')
   visible.append(ni)
 if {doc['nodes'][x]['name'] for x in visible}!=VISIBLE_NODE_NAMES: raise SystemExit('visible node set drift')
 if {doc['nodes'][x]['name'] for x in hidden}!=HIDDEN_NODE_NAMES: raise SystemExit('hidden node set drift')
 rn['children']=[x for x in children if x not in hidden]
 # Animation packaging only. Samples/channels remain byte-identical in BIN.
 anims=list(doc.get('animations',[])); original_anim_count=len(anims)
 if a.mode=='none':
  doc['animations']=[]
 elif a.mode=='one':
  rows=[x for x in anims if str(x.get('extras',{}).get('d1OwnerSelectedClip','')).upper()==PREVIEW_CLIP]
  if len(rows)!=1: raise SystemExit(f'expected one preview clip, got {len(rows)}')
  doc['animations']=rows
 else:
  rows=[x for x in anims if str(x.get('extras',{}).get('d1OwnerSelectedClip','')).upper()==PREVIEW_CLIP]
  if len(rows)!=1 or len(anims)!=82: raise SystemExit('full animation source drift')
  target=rows[0]; doc['animations']=[target]+[x for x in anims if x is not target]
 doc.setdefault('asset',{}).setdefault('extras',{})['d1CrotaR7ColorSurfaceView']={
  'schema':'d1_crota_r7_color_surface_view/v1','model':'8108E5B7','visibleRangeCount':6,'hiddenNativePrepassRangeCount':3,
  'visibleTriangleCount':33750,'visibleMaterialTags':sorted(VISIBLE_MATERIALS),'hiddenPrepassMaterialTags':sorted(PREPASS_MATERIALS),
  'previewClip':PREVIEW_CLIP if a.mode!='none' else None,
  'policy':'All 9 exact native ranges remain serialized. Three overlapping prepass nodes are removed only from the active Blender scene to prevent false PBR z-fighting. Animation samples are unchanged.'}
 write_glb(a.out,doc,blob)
 outdoc,outblob=read_glb(a.out)
 if outblob!=blob: raise SystemExit('BIN chunk changed')
 if len([x for x in outdoc['nodes'][root].get('children',[]) if outdoc['nodes'][x].get('mesh') is not None])!=6: raise SystemExit('visible mesh-node count drift')
 expected={'none':0,'one':1,'all-preview-first':82}[a.mode]
 if len(outdoc.get('animations',[]))!=expected: raise SystemExit('animation count drift')
 if expected and str(outdoc['animations'][0].get('extras',{}).get('d1OwnerSelectedClip','')).upper()!=PREVIEW_CLIP: raise SystemExit('preview clip not first')
 rep={'schema':'d1_crota_r7_color_surface_filter/v1','status':'D1_CROTA_R7_COLOR_SURFACE_VIEW_COMPLETE','input':str(a.input),'output':str(a.out),'mode':a.mode,'source_mesh_nodes':9,'visible_mesh_nodes':6,'hidden_prepass_nodes':3,'visible_triangles':33750,'source_animation_count':original_anim_count,'output_animation_count':expected,'preview_clip':PREVIEW_CLIP if expected else None,'output_bytes':a.out.stat().st_size,'output_sha256':hashlib.sha256(a.out.read_bytes()).hexdigest(),'binary_unchanged':True}
 a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(rep,indent=2)+'\n');print(json.dumps(rep,indent=2))
if __name__=='__main__':main()
