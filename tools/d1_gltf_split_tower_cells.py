#!/usr/bin/env python3
"""Split the merged ten-cell Tower GLB into compact exact per-cell GLBs.

The merged scene names every root placement node `cellNN_*`. This adapter keeps
only the selected cells and recursively closes their glTF dependencies
(meshes/materials/textures/images/accessors/bufferViews), then compacts the BIN
chunk without changing any referenced bytes. It is an inspection/handoff
adapter; source geometry and texture payload bytes are not transformed.
"""
from __future__ import annotations

import argparse, copy, hashlib, json, mmap, struct
from pathlib import Path

GLB_MAGIC=0x46546C67; JSON_CHUNK=0x4E4F534A; BIN_CHUNK=0x004E4942

def cli():
    ap=argparse.ArgumentParser()
    ap.add_argument('src',type=Path)
    ap.add_argument('--out-dir',type=Path,required=True)
    ap.add_argument('--cell',type=int,action='append',required=True)
    ap.add_argument('--report',type=Path,required=True)
    return ap.parse_args()

def sha256(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(8<<20),b''): h.update(b)
    return h.hexdigest()

def write_glb(path,doc,binout):
    jb=json.dumps(doc,separators=(',',':'),ensure_ascii=False).encode('utf-8'); jb+=b' '*((-len(jb))%4)
    binout.extend(b'\0'*((-len(binout))%4))
    total=12+8+len(jb)+8+len(binout)
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('wb') as g:
        g.write(struct.pack('<III',GLB_MAGIC,2,total)); g.write(struct.pack('<II',len(jb),JSON_CHUNK)); g.write(jb); g.write(struct.pack('<II',len(binout),BIN_CHUNK)); g.write(binout)

def main():
    a=cli(); cells=sorted(set(a.cell))
    if any(x<0 or x>9 for x in cells): raise SystemExit('cell must be 0..9')
    with a.src.open('rb') as f:
        mm=mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ)
        magic,ver,total=struct.unpack_from('<III',mm,0)
        if magic!=GLB_MAGIC or ver!=2 or total!=len(mm): raise SystemExit('invalid GLB2 header')
        jlen,jtyp=struct.unpack_from('<II',mm,12)
        if jtyp!=JSON_CHUNK: raise SystemExit('first chunk is not JSON')
        doc=json.loads(mm[20:20+jlen].decode('utf-8').rstrip(' \t\r\n\x00'))
        boff=20+jlen; blen,btyp=struct.unpack_from('<II',mm,boff)
        if btyp!=BIN_CHUNK: raise SystemExit('second chunk is not BIN')
        bdata=boff+8
        rows=[]
        for ci in cells:
            prefix=f'cell{ci:02d}_'
            node_ids=[i for i,n in enumerate(doc.get('nodes',[])) if str(n.get('name','')).startswith(prefix)]
            if not node_ids: raise SystemExit(f'cell {ci:02d}: no nodes')
            mesh_ids=sorted({doc['nodes'][i]['mesh'] for i in node_ids if 'mesh' in doc['nodes'][i]})
            acc_ids=set(); mat_ids=set()
            for mid in mesh_ids:
                for p in doc['meshes'][mid].get('primitives',[]):
                    if 'material' in p: mat_ids.add(p['material'])
                    if 'indices' in p: acc_ids.add(p['indices'])
                    acc_ids.update(p.get('attributes',{}).values())
                    for tgt in p.get('targets',[]): acc_ids.update(tgt.values())
            mat_ids=sorted(mat_ids); acc_ids=sorted(acc_ids)
            tex_ids=set()
            for mid in mat_ids:
                m=doc['materials'][mid]
                for k in ('normalTexture','occlusionTexture','emissiveTexture'):
                    x=m.get(k)
                    if isinstance(x,dict) and 'index' in x: tex_ids.add(x['index'])
                p=m.get('pbrMetallicRoughness') or {}
                for k in ('baseColorTexture','metallicRoughnessTexture'):
                    x=p.get(k)
                    if isinstance(x,dict) and 'index' in x: tex_ids.add(x['index'])
            tex_ids=sorted(tex_ids)
            img_ids=sorted({doc['textures'][i]['source'] for i in tex_ids if 'source' in doc['textures'][i]})
            samp_ids=sorted({doc['textures'][i]['sampler'] for i in tex_ids if 'sampler' in doc['textures'][i]})
            bv_ids=set()
            for aid in acc_ids:
                x=doc['accessors'][aid]
                if 'bufferView' in x: bv_ids.add(x['bufferView'])
                sp=x.get('sparse') or {}
                for q in ('indices','values'):
                    if 'bufferView' in (sp.get(q) or {}): bv_ids.add(sp[q]['bufferView'])
            for iid in img_ids:
                x=doc['images'][iid]
                if 'bufferView' in x: bv_ids.add(x['bufferView'])
            bv_ids=sorted(bv_ids)

            nm={o:i for i,o in enumerate(node_ids)}; meshmap={o:i for i,o in enumerate(mesh_ids)}
            matmap={o:i for i,o in enumerate(mat_ids)}; accmap={o:i for i,o in enumerate(acc_ids)}
            texmap={o:i for i,o in enumerate(tex_ids)}; imgmap={o:i for i,o in enumerate(img_ids)}
            sampmap={o:i for i,o in enumerate(samp_ids)}; bvmap={o:i for i,o in enumerate(bv_ids)}

            binout=bytearray(); bvs=[]
            for old in bv_ids:
                bv=copy.deepcopy(doc['bufferViews'][old]); start=int(bv.get('byteOffset',0)); ln=int(bv['byteLength'])
                binout.extend(b'\0'*((-len(binout))%4)); bv['buffer']=0; bv['byteOffset']=len(binout)
                binout.extend(mm[bdata+start:bdata+start+ln]); bvs.append(bv)

            nodes=[]
            for old in node_ids:
                n=copy.deepcopy(doc['nodes'][old])
                if 'mesh' in n: n['mesh']=meshmap[n['mesh']]
                if 'children' in n: n['children']=[nm[x] for x in n['children'] if x in nm]
                nodes.append(n)
            meshes=[]
            for old in mesh_ids:
                m=copy.deepcopy(doc['meshes'][old])
                for p in m.get('primitives',[]):
                    if 'material' in p: p['material']=matmap[p['material']]
                    if 'indices' in p: p['indices']=accmap[p['indices']]
                    p['attributes']={k:accmap[v] for k,v in p.get('attributes',{}).items()}
                    if 'targets' in p: p['targets']=[{k:accmap[v] for k,v in t.items()} for t in p['targets']]
                meshes.append(m)
            materials=[]
            for old in mat_ids:
                m=copy.deepcopy(doc['materials'][old])
                for k in ('normalTexture','occlusionTexture','emissiveTexture'):
                    if k in m and 'index' in m[k]: m[k]['index']=texmap[m[k]['index']]
                p=m.get('pbrMetallicRoughness') or {}
                for k in ('baseColorTexture','metallicRoughnessTexture'):
                    if k in p and 'index' in p[k]: p[k]['index']=texmap[p[k]['index']]
                materials.append(m)
            accessors=[]
            for old in acc_ids:
                x=copy.deepcopy(doc['accessors'][old])
                if 'bufferView' in x: x['bufferView']=bvmap[x['bufferView']]
                sp=x.get('sparse') or {}
                for q in ('indices','values'):
                    if 'bufferView' in (sp.get(q) or {}): sp[q]['bufferView']=bvmap[sp[q]['bufferView']]
                accessors.append(x)
            textures=[]
            for old in tex_ids:
                x=copy.deepcopy(doc['textures'][old])
                if 'source' in x: x['source']=imgmap[x['source']]
                if 'sampler' in x: x['sampler']=sampmap[x['sampler']]
                textures.append(x)
            images=[]
            for old in img_ids:
                x=copy.deepcopy(doc['images'][old])
                if 'bufferView' in x: x['bufferView']=bvmap[x['bufferView']]
                images.append(x)
            samplers=[copy.deepcopy(doc['samplers'][i]) for i in samp_ids] if doc.get('samplers') else []

            outdoc={'asset':copy.deepcopy(doc['asset']),'scene':0,'scenes':[{'name':f'Tower cell {ci:02d}','nodes':list(range(len(nodes)))}],
                    'nodes':nodes,'meshes':meshes,'materials':materials,'accessors':accessors,'bufferViews':bvs,'buffers':[{'byteLength':len(binout)}]}
            if textures: outdoc['textures']=textures
            if images: outdoc['images']=images
            if samplers: outdoc['samplers']=samplers
            for k in ('extensionsUsed','extensionsRequired'):
                if k in doc: outdoc[k]=copy.deepcopy(doc[k])
            out=a.out_dir/f'TOWER_CELL_{ci:02d}.glb'; write_glb(out,outdoc,binout)
            rows.append({'cell':ci,'file':out.name,'bytes':out.stat().st_size,'sha256':sha256(out),'nodes':len(nodes),'meshes':len(meshes),'materials':len(materials),'textures':len(textures),'images':len(images),'accessors':len(accessors),'buffer_views':len(bvs)})
        mm.close()
    rep={'status':'D1_TOWER_COMPACT_CELL_SPLIT_COMPLETE','source':a.src.name,'source_sha256':sha256(a.src),'cells':rows,'policy':'Selected cell root nodes and their exact glTF dependencies only; referenced BIN/image bytes copied unchanged into compact offsets.'}
    a.report.parent.mkdir(parents=True,exist_ok=True); a.report.write_text(json.dumps(rep,indent=2)+'\n'); print(json.dumps(rep,indent=2))

if __name__=='__main__': main()
