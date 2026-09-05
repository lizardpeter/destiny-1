#!/usr/bin/env python3
"""Loss-preserving GLB merger for independently validated D1 world layers.

Unlike a scene-library round trip, this merges glTF 2.0 JSON/BIN structures
without decoding/re-encoding meshes, materials or embedded images.  That makes
it suitable for composing already-validated D1 layer adapters while preserving
portable PBR textures and normals byte-for-byte inside each source layer.

Supported input contract:
- GLB 2.0;
- exactly one JSON chunk and at most one BIN chunk;
- at most one GLB buffer, with no external buffer URI;
- standard glTF 2.0 index relationships plus KHR_lights_punctual.

The merger fails closed on unsupported top-level extensions instead of silently
corrupting extension-owned indices.
"""
from __future__ import annotations
import argparse, copy, hashlib, json, struct
from pathlib import Path

MAGIC=b'glTF'; VERSION=2; JSON_CHUNK=0x4E4F534A; BIN_CHUNK=0x004E4942


def digest(p:Path)->str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()


def parse_layer(s:str):
    if '=' not in s: raise argparse.ArgumentTypeError('layer must be NAME=PATH')
    n,p=s.split('=',1)
    if not n or not p: raise argparse.ArgumentTypeError('layer must be NAME=PATH')
    return n,Path(p)


def parse_count(s:str):
    if '=' not in s: raise argparse.ArgumentTypeError('logical-count must be NAME=N')
    n,v=s.split('=',1); return n,int(v,0)


def pad4(b:bytes,fill:bytes=b'\x00')->bytes:
    return b + fill*((-len(b))&3)


def read_glb(path:Path):
    raw=path.read_bytes()
    if len(raw)<12: raise ValueError(f'{path}: short GLB')
    magic,ver,total=struct.unpack_from('<4sII',raw,0)
    if magic!=MAGIC or ver!=VERSION or total!=len(raw):
        raise ValueError(f'{path}: invalid GLB header magic={magic!r} version={ver} declared={total} actual={len(raw)}')
    off=12; js=None; binb=b''; extras=[]
    while off<total:
        if off+8>total: raise ValueError(f'{path}: truncated chunk header')
        n,typ=struct.unpack_from('<II',raw,off);off+=8
        if off+n>total: raise ValueError(f'{path}: truncated chunk payload')
        payload=raw[off:off+n];off+=n
        if typ==JSON_CHUNK:
            if js is not None: raise ValueError(f'{path}: multiple JSON chunks')
            js=json.loads(payload.rstrip(b' \t\r\n\x00').decode('utf-8'))
        elif typ==BIN_CHUNK:
            if binb: raise ValueError(f'{path}: multiple BIN chunks')
            binb=payload
        else:
            extras.append((typ,payload))
    if js is None: raise ValueError(f'{path}: missing JSON chunk')
    if extras: raise ValueError(f'{path}: unsupported non-JSON/BIN chunks {[hex(t) for t,_ in extras]}')
    buffers=js.get('buffers',[])
    if len(buffers)>1: raise ValueError(f'{path}: multiple buffers unsupported')
    if buffers:
        if buffers[0].get('uri') is not None: raise ValueError(f'{path}: external/data URI buffer unsupported')
        want=int(buffers[0].get('byteLength',0))
        if want>len(binb): raise ValueError(f'{path}: buffer byteLength {want} > BIN chunk {len(binb)}')
        # Strip only GLB chunk alignment padding; source bufferView offsets are
        # relative to the declared buffer byteLength, not padded chunk length.
        binb=binb[:want]
    elif binb:
        raise ValueError(f'{path}: BIN chunk present without buffer declaration')
    return js,binb


def write_glb(path:Path,doc:dict,binb:bytes):
    doc=copy.deepcopy(doc)
    if binb:
        doc['buffers']=[{'byteLength':len(binb)}]
    else:
        doc.pop('buffers',None)
    jb=json.dumps(doc,separators=(',',':'),ensure_ascii=False).encode('utf-8')
    jb=pad4(jb,b' '); bb=pad4(binb,b'\x00')
    total=12+8+len(jb)+(8+len(bb) if binb else 0)
    out=bytearray(struct.pack('<4sII',MAGIC,VERSION,total))
    out+=struct.pack('<II',len(jb),JSON_CHUNK)+jb
    if binb: out+=struct.pack('<II',len(bb),BIN_CHUNK)+bb
    path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(out)


def remap_material_texture_indices(mat:dict,tex_off:int):
    # Standard material textureInfo locations.
    p=mat.get('pbrMetallicRoughness') or {}
    for k in ('baseColorTexture','metallicRoughnessTexture'):
        if isinstance(p.get(k),dict) and 'index' in p[k]: p[k]['index']+=tex_off
    for k in ('normalTexture','occlusionTexture','emissiveTexture'):
        if isinstance(mat.get(k),dict) and 'index' in mat[k]: mat[k]['index']+=tex_off

    # KHR material extensions all use ordinary textureInfo objects.  Walk only
    # under material.extensions and remap dicts that structurally look like a
    # textureInfo (index plus optional texCoord/extensions/scale/strength).
    def walk(x):
        if isinstance(x,dict):
            if 'index' in x and isinstance(x['index'],int) and set(x).issubset({'index','texCoord','extensions','scale','strength'}):
                x['index']+=tex_off
            for v in x.values(): walk(v)
        elif isinstance(x,list):
            for v in x: walk(v)
    walk(mat.get('extensions',{}))


def node_local_matrix(n:dict):
    if 'matrix' in n:
        a=n['matrix']
        if len(a)!=16: raise ValueError('node matrix must contain 16 values')
        # glTF serializes matrices column-major.
        return [[float(a[c*4+r]) for c in range(4)] for r in range(4)]
    t=[float(x) for x in n.get('translation',[0,0,0])]
    q=[float(x) for x in n.get('rotation',[0,0,0,1])]
    sc=[float(x) for x in n.get('scale',[1,1,1])]
    x,y,z,w=q
    # quaternion -> 3x3, then scale columns (T*R*S)
    r=[[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],
       [2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],
       [2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]]
    m=[[r[i][j]*sc[j] for j in range(3)]+[t[i]] for i in range(3)]
    m.append([0.,0.,0.,1.]);return m


def mmul(a,b):
    return [[sum(a[i][k]*b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]


def transform_point(m,p):
    v=[p[0],p[1],p[2],1.0]
    q=[sum(m[i][j]*v[j] for j in range(4)) for i in range(4)]
    if q[3] and abs(q[3]-1.0)>1e-12: return [q[i]/q[3] for i in range(3)]
    return q[:3]


def scene_bounds(doc:dict):
    nodes=doc.get('nodes',[]); meshes=doc.get('meshes',[]); acc=doc.get('accessors',[]); scenes=doc.get('scenes',[])
    if not scenes:return None
    si=int(doc.get('scene',0))
    if si<0 or si>=len(scenes):return None
    lo=[float('inf')]*3;hi=[float('-inf')]*3;anyp=False
    I=[[1.,0.,0.,0.],[0.,1.,0.,0.],[0.,0.,1.,0.],[0.,0.,0.,1.]]
    def visit(ni,parent,stack):
        nonlocal anyp
        if ni<0 or ni>=len(nodes): raise ValueError(f'node index OOB {ni}')
        if ni in stack: raise ValueError('node cycle in active scene')
        n=nodes[ni];world=mmul(parent,node_local_matrix(n));stack=stack|{ni}
        mi=n.get('mesh')
        if mi is not None:
            if mi<0 or mi>=len(meshes): raise ValueError(f'mesh index OOB {mi}')
            for prim in meshes[mi].get('primitives',[]):
                ai=(prim.get('attributes') or {}).get('POSITION')
                if ai is None: continue
                if ai<0 or ai>=len(acc): raise ValueError(f'POSITION accessor OOB {ai}')
                a=acc[ai];mn=a.get('min');mx=a.get('max')
                if not mn or not mx or len(mn)<3 or len(mx)<3: continue
                for x in (float(mn[0]),float(mx[0])):
                    for y in (float(mn[1]),float(mx[1])):
                        for z in (float(mn[2]),float(mx[2])):
                            p=transform_point(world,[x,y,z]);anyp=True
                            for k in range(3):lo[k]=min(lo[k],p[k]);hi[k]=max(hi[k],p[k])
        for ch in n.get('children',[]) or []: visit(ch,world,stack)
    for root in scenes[si].get('nodes',[]) or []: visit(root,I,set())
    return [lo,hi] if anyp else None


def merge_layers(layers:list[tuple[str,Path]],logical:dict[str,int]):
    src=[]
    for name,path in layers:
        if not path.exists(): raise SystemExit(f'{name}: missing {path}')
        doc,binb=read_glb(path)
        src.append((name,path,doc,binb))

    out={
        'asset':{'version':'2.0','generator':'destiny-1 d1_world_layer_merge.py loss-preserving GLB merger'},
        'scene':0,'scenes':[{'name':'D1 merged world layers','nodes':[]}],
    }
    lists=('bufferViews','accessors','samplers','images','textures','materials','meshes','cameras','skins','animations','nodes')
    for k in lists: out[k]=[]
    out_bin=bytearray(); rows=[]
    used=[]; required=[]
    top_lights=[]

    for li,(name,path,d,binb) in enumerate(src):
        # Fail closed for unsupported top-level extension payloads.  The known
        # lights extension is an indexed top-level list and is explicitly merged.
        top_ext=d.get('extensions',{}) or {}
        bad_ext=sorted(set(top_ext)-{'KHR_lights_punctual'})
        if bad_ext: raise SystemExit(f'{name}: unsupported top-level extensions {bad_ext}')

        # Source offsets before appending anything from this layer.
        off={k:len(out[k]) for k in lists}
        light_off=len(top_lights)
        base_bin=(len(out_bin)+3)&~3
        if base_bin>len(out_bin): out_bin+=b'\x00'*(base_bin-len(out_bin))
        out_bin+=binb

        # Buffer views first: all GLB source views point at source buffer 0.
        for bv0 in d.get('bufferViews',[]):
            bv=copy.deepcopy(bv0);bv['buffer']=0;bv['byteOffset']=base_bin+int(bv.get('byteOffset',0));out['bufferViews'].append(bv)
        for a0 in d.get('accessors',[]):
            a=copy.deepcopy(a0)
            if 'bufferView' in a: a['bufferView']+=off['bufferViews']
            sp=a.get('sparse')
            if sp:
                if 'bufferView' in sp.get('indices',{}): sp['indices']['bufferView']+=off['bufferViews']
                if 'bufferView' in sp.get('values',{}): sp['values']['bufferView']+=off['bufferViews']
            out['accessors'].append(a)
        out['samplers'].extend(copy.deepcopy(d.get('samplers',[])))
        for im0 in d.get('images',[]):
            im=copy.deepcopy(im0)
            if 'bufferView' in im: im['bufferView']+=off['bufferViews']
            out['images'].append(im)
        for t0 in d.get('textures',[]):
            t=copy.deepcopy(t0)
            if 'sampler' in t: t['sampler']+=off['samplers']
            if 'source' in t: t['source']+=off['images']
            # EXT_texture_webp / KHR_texture_basisu source indices.
            for en in ('EXT_texture_webp','KHR_texture_basisu'):
                e=(t.get('extensions') or {}).get(en)
                if isinstance(e,dict) and 'source' in e: e['source']+=off['images']
            out['textures'].append(t)
        for m0 in d.get('materials',[]):
            m=copy.deepcopy(m0);remap_material_texture_indices(m,off['textures']);out['materials'].append(m)
        for mesh0 in d.get('meshes',[]):
            mesh=copy.deepcopy(mesh0)
            for p in mesh.get('primitives',[]):
                if 'indices' in p: p['indices']+=off['accessors']
                if 'material' in p: p['material']+=off['materials']
                if isinstance(p.get('attributes'),dict):
                    for k,v in list(p['attributes'].items()): p['attributes'][k]=v+off['accessors']
                for target in p.get('targets',[]) or []:
                    for k,v in list(target.items()): target[k]=v+off['accessors']
                # Draco points at one bufferView and attribute IDs internal to
                # Draco data; only the bufferView index is glTF-global.
                dr=(p.get('extensions') or {}).get('KHR_draco_mesh_compression')
                if isinstance(dr,dict) and 'bufferView' in dr: dr['bufferView']+=off['bufferViews']
            out['meshes'].append(mesh)
        out['cameras'].extend(copy.deepcopy(d.get('cameras',[])))
        for s0 in d.get('skins',[]):
            s=copy.deepcopy(s0)
            if 'inverseBindMatrices' in s: s['inverseBindMatrices']+=off['accessors']
            if 'skeleton' in s: s['skeleton']+=off['nodes']
            s['joints']=[j+off['nodes'] for j in s.get('joints',[])]
            out['skins'].append(s)
        for a0 in d.get('animations',[]):
            a=copy.deepcopy(a0)
            for smp in a.get('samplers',[]):
                smp['input']+=off['accessors'];smp['output']+=off['accessors']
            for ch in a.get('channels',[]):
                tgt=ch.get('target') or {}
                if 'node' in tgt: tgt['node']+=off['nodes']
            out['animations'].append(a)

        lights=((top_ext.get('KHR_lights_punctual') or {}).get('lights') or [])
        top_lights.extend(copy.deepcopy(lights))
        for n0 in d.get('nodes',[]):
            n=copy.deepcopy(n0)
            if 'mesh' in n: n['mesh']+=off['meshes']
            if 'camera' in n: n['camera']+=off['cameras']
            if 'skin' in n: n['skin']+=off['skins']
            if 'children' in n: n['children']=[x+off['nodes'] for x in n['children']]
            le=((n.get('extensions') or {}).get('KHR_lights_punctual'))
            if isinstance(le,dict) and 'light' in le: le['light']+=light_off
            out['nodes'].append(n)

        scenes=d.get('scenes',[])
        if scenes:
            si=int(d.get('scene',0))
            if si<0 or si>=len(scenes): raise SystemExit(f'{name}: invalid active scene index {si}')
            roots=[x+off['nodes'] for x in scenes[si].get('nodes',[])]
        else:
            # No scene object: make all parentless nodes roots.
            child={x for n in d.get('nodes',[]) for x in n.get('children',[])}
            roots=[off['nodes']+i for i in range(len(d.get('nodes',[]))) if i not in child]
        out['scenes'][0]['nodes'].extend(roots)
        used.extend(d.get('extensionsUsed',[]) or []); required.extend(d.get('extensionsRequired',[]) or [])

        rows.append({
            'name':name,'input':str(path),'input_bytes':path.stat().st_size,'input_sha256':digest(path),
            'logical_source_records':logical.get(name),
            'inventory':{k:len(d.get(k,[])) for k in ('bufferViews','accessors','samplers','images','textures','materials','meshes','cameras','skins','animations','nodes')},
            'active_scene_roots':len(roots),'bin_bytes':len(binb),
        })

    if top_lights:
        out['extensions']={'KHR_lights_punctual':{'lights':top_lights}}
        used.append('KHR_lights_punctual')
    if used: out['extensionsUsed']=sorted(set(used))
    if required: out['extensionsRequired']=sorted(set(required))
    for k in lists:
        if not out[k]: out.pop(k,None)
    return out,bytes(out_bin),rows


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--layer',action='append',type=parse_layer,required=True)
    ap.add_argument('--logical-count',action='append',type=parse_count,default=[])
    ap.add_argument('--out',type=Path,required=True);ap.add_argument('--report',type=Path,required=True)
    a=ap.parse_args(); logical=dict(a.logical_count); names=[n for n,_ in a.layer]
    if len(set(names))!=len(names): raise SystemExit('duplicate layer name')
    unknown=sorted(set(logical)-set(names))
    if unknown: raise SystemExit('logical counts supplied for unknown layers: '+','.join(unknown))

    doc,binb,rows=merge_layers(a.layer,logical);write_glb(a.out,doc,binb)
    chk,chkbin=read_glb(a.out)
    inv={k:len(chk.get(k,[])) for k in ('bufferViews','accessors','samplers','images','textures','materials','meshes','cameras','skins','animations','nodes')}
    mesh_nodes=sum(1 for n in chk.get('nodes',[]) if 'mesh' in n)
    bounds=scene_bounds(chk)
    sums={k:sum(r['inventory'][k] for r in rows) for k in inv}
    if inv!=sums: raise SystemExit(f'output inventory mismatch output={inv} expected={sums}')
    if len(chkbin)!=len(binb): raise SystemExit(f'output BIN length mismatch {len(chkbin)} != {len(binb)}')
    rep={
        'schema_version':2,'status':'D1_WORLD_LAYER_GLB_LOSS_PRESERVING_MERGE','layers':rows,'layer_count':len(rows),
        'logical_source_records_total':sum(logical.values()),'inventory':inv,
        'geometry_nodes':mesh_nodes,'geometry_variants':inv['meshes'],'bounds':bounds,
        'embedded_images':inv['images'],'textures':inv['textures'],'materials':inv['materials'],
        'glb':str(a.out),'glb_bytes':a.out.stat().st_size,'glb_sha256':digest(a.out),'bin_bytes':len(binb),
        'policy':'GLB JSON/BIN structures are merged directly. Mesh/accessor/material/texture/image payloads are not decoded or re-exported; each source layer keeps its embedded binary bytes exactly as a contiguous BIN subrange. Index relationships are remapped only as required by glTF composition.',
    }
    a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(rep,indent=2)+'\n');print(json.dumps(rep,indent=2));return 0

if __name__=='__main__': raise SystemExit(main())
