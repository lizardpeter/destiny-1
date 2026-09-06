#!/usr/bin/env python3
"""Loss-preserving, path-independent GLB layer merger for D1 world adapters.

The earlier trimesh scene round-trip preserved geometry and transforms but
stripped embedded textures/images/material bindings. This tool edits glTF 2.0
JSON/BIN containers directly instead. The first GLB is the base and keeps all of
its indices/resources in place; later GLBs are appended with core glTF indices
remapped into the combined document.

Contract:
- GLB 2.0 inputs;
- one embedded BIN buffer per input, no external URI;
- base indices are never renumbered;
- appended default-scene roots are attached under one identity layer node;
- the entire original base BIN payload is an exact prefix of the output BIN;
- base core resource arrays are exact unchanged prefixes of the output arrays;
- output GLB bytes depend on input *content* and logical layer names, not temporary
  filesystem paths. Provenance embedded in a layer parent uses the input SHA-256,
  while human-readable paths remain report-only metadata.
"""
from __future__ import annotations

import argparse, copy, hashlib, json, struct
from pathlib import Path

MAGIC=0x46546C67
JSON_CHUNK=0x4E4F534A
BIN_CHUNK=0x004E4942
ARRAYS=('accessors','animations','bufferViews','cameras','images','materials','meshes','nodes','samplers','skins','textures')
PRESERVE_PREFIX=('accessors','animations','bufferViews','cameras','images','materials','meshes','nodes','samplers','skins','textures')


def digest(p:Path)->str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8<<20),b''): h.update(b)
    return h.hexdigest()


def bytes_digest(b:bytes)->str:
    return hashlib.sha256(b).hexdigest()


def json_digest(v)->str:
    return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()


def pad4(b:bytes,fill:bytes)->bytes:
    return b + fill*((-len(b))&3)


def read_glb(p:Path):
    raw=p.read_bytes()
    if len(raw)<20: raise ValueError(f'{p}: too short for GLB')
    magic,ver,total=struct.unpack_from('<III',raw,0)
    if magic!=MAGIC or ver!=2 or total!=len(raw): raise ValueError(f'{p}: invalid GLB header')
    pos=12;chunks=[]
    while pos<total:
        if pos+8>total: raise ValueError(f'{p}: truncated chunk header')
        ln,typ=struct.unpack_from('<II',raw,pos);pos+=8
        if pos+ln>total: raise ValueError(f'{p}: truncated chunk payload')
        chunks.append((typ,raw[pos:pos+ln]));pos+=ln
    if len(chunks)!=2 or chunks[0][0]!=JSON_CHUNK or chunks[1][0]!=BIN_CHUNK:
        raise ValueError(f'{p}: expected exactly JSON+BIN chunks')
    doc=json.loads(chunks[0][1].rstrip(b' \t\r\n\x00'))
    bufs=doc.get('buffers',[])
    if len(bufs)!=1 or bufs[0].get('uri') is not None: raise ValueError(f'{p}: expected one embedded buffer')
    declared=int(bufs[0].get('byteLength',-1));bin_chunk=chunks[1][1]
    if declared<0 or declared>len(bin_chunk) or len(bin_chunk)-declared>3:
        raise ValueError(f'{p}: embedded buffer length mismatch')
    return doc,bin_chunk[:declared]


def write_glb(p:Path,doc:dict,bin_data:bytes):
    d=copy.deepcopy(doc);d['buffers']=[{'byteLength':len(bin_data)}]
    jb=pad4(json.dumps(d,separators=(',',':'),ensure_ascii=False).encode(),b' ')
    bb=pad4(bin_data,b'\x00')
    total=12+8+len(jb)+8+len(bb)
    raw=bytearray(struct.pack('<III',MAGIC,2,total))
    raw+=struct.pack('<II',len(jb),JSON_CHUNK)+jb
    raw+=struct.pack('<II',len(bb),BIN_CHUNK)+bb
    p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)


def add_idx(o:dict,key:str,off:int):
    if key in o and o[key] is not None: o[key]=int(o[key])+off


def texinfo(x,off:int):
    if isinstance(x,dict): add_idx(x,'index',off)


def remap_material_extensions(ext:dict,tex_off:int):
    if not isinstance(ext,dict): return
    fields={
      'KHR_materials_clearcoat':['clearcoatTexture','clearcoatRoughnessTexture','clearcoatNormalTexture'],
      'KHR_materials_iridescence':['iridescenceTexture','iridescenceThicknessTexture'],
      'KHR_materials_sheen':['sheenColorTexture','sheenRoughnessTexture'],
      'KHR_materials_specular':['specularTexture','specularColorTexture'],
      'KHR_materials_transmission':['transmissionTexture'],
      'KHR_materials_volume':['thicknessTexture'],
      'KHR_materials_anisotropy':['anisotropyTexture'],
    }
    for en,keys in fields.items():
        e=ext.get(en)
        if isinstance(e,dict):
            for k in keys: texinfo(e.get(k),tex_off)


def counts(d:dict):
    x={k:len(d.get(k,[])) for k in ARRAYS};x['scenes']=len(d.get('scenes',[]))
    x['lights']=len((((d.get('extensions') or {}).get('KHR_lights_punctual') or {}).get('lights',[])))
    return x


def remap_doc(src:dict,off:dict,bin_off:int):
    d=copy.deepcopy(src)
    for x in d.get('bufferViews',[]):
        x['buffer']=0;x['byteOffset']=int(x.get('byteOffset',0))+bin_off
    for x in d.get('accessors',[]):
        add_idx(x,'bufferView',off['bufferViews']);sp=x.get('sparse')
        if isinstance(sp,dict):
            if isinstance(sp.get('indices'),dict): add_idx(sp['indices'],'bufferView',off['bufferViews'])
            if isinstance(sp.get('values'),dict): add_idx(sp['values'],'bufferView',off['bufferViews'])
    for x in d.get('images',[]): add_idx(x,'bufferView',off['bufferViews'])
    for x in d.get('textures',[]): add_idx(x,'sampler',off['samplers']);add_idx(x,'source',off['images'])
    for x in d.get('materials',[]):
        p=x.get('pbrMetallicRoughness')
        if isinstance(p,dict):
            texinfo(p.get('baseColorTexture'),off['textures']);texinfo(p.get('metallicRoughnessTexture'),off['textures'])
        for k in ('normalTexture','occlusionTexture','emissiveTexture'): texinfo(x.get(k),off['textures'])
        remap_material_extensions(x.get('extensions'),off['textures'])
    for x in d.get('meshes',[]):
        for p in x.get('primitives',[]):
            for k,v in list(p.get('attributes',{}).items()): p['attributes'][k]=int(v)+off['accessors']
            add_idx(p,'indices',off['accessors']);add_idx(p,'material',off['materials'])
            for t in p.get('targets',[]):
                for k,v in list(t.items()): t[k]=int(v)+off['accessors']
    for x in d.get('nodes',[]):
        add_idx(x,'camera',off['cameras']);add_idx(x,'mesh',off['meshes']);add_idx(x,'skin',off['skins'])
        if 'children' in x: x['children']=[int(v)+off['nodes'] for v in x['children']]
        e=x.get('extensions')
        if isinstance(e,dict) and isinstance(e.get('KHR_lights_punctual'),dict):
            add_idx(e['KHR_lights_punctual'],'light',off.get('lights',0))
    for x in d.get('skins',[]):
        add_idx(x,'inverseBindMatrices',off['accessors']);add_idx(x,'skeleton',off['nodes'])
        if 'joints' in x: x['joints']=[int(v)+off['nodes'] for v in x['joints']]
    for a in d.get('animations',[]):
        for s in a.get('samplers',[]): add_idx(s,'input',off['accessors']);add_idx(s,'output',off['accessors'])
        for c in a.get('channels',[]):
            t=c.get('target')
            if isinstance(t,dict): add_idx(t,'node',off['nodes'])
    return d


def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument('--base',type=Path,required=True)
    ap.add_argument('--layer',action='append',required=True,help='NAME=PATH')
    ap.add_argument('--out',type=Path,required=True);ap.add_argument('--report',type=Path,required=True)
    a=ap.parse_args()

    base,base_bin_data=read_glb(a.base);bin_data=base_bin_data;out=copy.deepcopy(base)
    if not out.get('scenes'): out['scenes']=[{'nodes':[]}];out['scene']=0
    scene_idx=int(out.get('scene',0));out['scenes'][scene_idx].setdefault('nodes',[])
    base_counts=counts(base);base_prefix_hashes={k:json_digest(base.get(k,[])) for k in PRESERVE_PREFIX};rows=[]

    for spec in a.layer:
        if '=' not in spec: raise SystemExit('--layer must be NAME=PATH')
        name,pstr=spec.split('=',1);p=Path(pstr);src,src_bin=read_glb(p);input_sha=digest(p)
        c0=counts(out);off={k:c0.get(k,0) for k in ARRAYS};off['lights']=c0.get('lights',0)
        aligned=(len(bin_data)+3)&~3
        if aligned!=len(bin_data): bin_data+=b'\x00'*(aligned-len(bin_data))
        bin_off=len(bin_data);bin_data+=src_bin;r=remap_doc(src,off,bin_off)
        lights=((((r.get('extensions') or {}).get('KHR_lights_punctual') or {}).get('lights',[])))
        if lights: out.setdefault('extensions',{}).setdefault('KHR_lights_punctual',{}).setdefault('lights',[]).extend(lights)
        for k in ARRAYS:
            vals=r.get(k,[])
            if vals: out.setdefault(k,[]).extend(vals)
        sidx=int(r.get('scene',0)) if r.get('scenes') else None
        roots=[] if sidx is None else [int(v)+off['nodes'] for v in r['scenes'][sidx].get('nodes',[])]
        parent={'name':f'D1_LAYER_{name}','children':roots,'extras':{
            'd1_layer':name,
            'source_glb_sha256':input_sha,
            'source_glb_bytes':p.stat().st_size,
        }}
        parent_i=len(out.get('nodes',[]));out.setdefault('nodes',[]).append(parent);out['scenes'][scene_idx]['nodes'].append(parent_i)
        for key in ('extensionsUsed','extensionsRequired'):
            if src.get(key):
                cur=out.setdefault(key,[])
                for v in src[key]:
                    if v not in cur: cur.append(v)
        # Paths are useful diagnostics but are deliberately report-only so temporary
        # runner directory/file names cannot alter the emitted GLB bytes.
        rows.append({'name':name,'input':str(p),'input_bytes':p.stat().st_size,'input_sha256':input_sha,
                     'input_counts':counts(src),'bin_payload_bytes':len(src_bin),'bin_offset':bin_off,
                     'scene_root_count':len(roots),'layer_parent_node':parent_i})

    write_glb(a.out,out,bin_data);check,check_bin=read_glb(a.out);final_counts=counts(check)
    if check_bin[:len(base_bin_data)]!=base_bin_data: raise SystemExit('base BIN payload is not an exact output prefix')
    prefix={}
    for k in PRESERVE_PREFIX:
        n=len(base.get(k,[]));got=check.get(k,[])[:n];same=(got==base.get(k,[]))
        prefix[k]={'count':n,'base_sha256':base_prefix_hashes[k],'output_prefix_sha256':json_digest(got),'exact':same}
        if not same: raise SystemExit(f'base {k} JSON prefix changed')
    rep={'schema_version':3,'status':'D1_GLTF_LAYER_MERGE_EXACT_BASE_PRESERVATION',
         'base':str(a.base),'base_bytes':a.base.stat().st_size,'base_sha256':digest(a.base),
         'base_counts':base_counts,'base_bin_payload_bytes':len(base_bin_data),'base_bin_sha256':bytes_digest(base_bin_data),
         'layers':rows,'final_counts':final_counts,'final_bin_payload_bytes':len(check_bin),
         'base_bin_exact_prefix':True,'base_json_exact_prefixes':prefix,
         'output':str(a.out),'output_bytes':a.out.stat().st_size,'output_sha256':digest(a.out),
         'determinism_contract':'Embedded merge metadata contains logical layer names plus source content SHA-256/byte length only; filesystem input paths are report-only.',
         'policy':'Base GLB resource arrays and BIN bytes remain exact prefixes; appended layer indices are remapped directly in glTF, with no material/image round-trip.'}
    a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(rep,indent=2)+'\n')
    print(json.dumps({k:rep[k] for k in ('status','base_counts','final_counts','base_bin_exact_prefix','output_bytes','output_sha256')},indent=2))
    return 0

if __name__=='__main__': raise SystemExit(main())
