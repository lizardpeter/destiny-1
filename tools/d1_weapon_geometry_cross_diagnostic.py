#!/usr/bin/env python3
"""Cross-package proof diagnostic for D1 ROI entity models.

This extends d1_weapon_geometry_diagnostic.py to resolve model vertex/index
headers and their payload references across multiple logical Tiger package
families.  This is required by ordinary D1 weapon models whose mesh headers can
live in a gear package while stream headers/payloads live in globals packages.

The first package owns the entity/model being diagnosed.  Supply logical views
for any referenced families with repeatable --extra-pkg.  Each EntryReader still
uses the normal sibling-patch resolution inside its own package family.
"""
from __future__ import annotations

import argparse
import collections
import json
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_entry_extract import EntryReader, decode_known
from d1_entity_model_probe import parse_model
from d1_entity_resource_probe import parse_resource
from d1_weapon_geometry_diagnostic import DSU, bbox, snorm16, strip_to_triangles, resource_literal_refs


class MultiReader:
    def __init__(self, primary: Path, extras: list[Path], runtime: Path):
        self.readers = [EntryReader(primary, runtime)] + [EntryReader(p, runtime) for p in extras]
        self.primary = self.readers[0]
        self.by_hash: dict[str, tuple[EntryReader, dict]] = {}
        collisions = []
        for r in self.readers:
            for e in r.entries:
                h = e['tag_hash'].upper()
                old = self.by_hash.get(h)
                if old and old[0].h['pkg_id'] != r.h['pkg_id']:
                    collisions.append({'tag_hash':h,'pkg_a':old[0].h['pkg_id'],'pkg_b':r.h['pkg_id']})
                    continue
                self.by_hash[h] = (r, e)
        self.collisions = collisions

    def locate(self, tag_hash: str) -> tuple[EntryReader, dict]:
        h = tag_hash.upper().removeprefix('0X')
        try:
            return self.by_hash[h]
        except KeyError:
            raise KeyError(f'tag {h} is not present in supplied package snapshots')

    def bytes(self, tag_hash: str) -> tuple[EntryReader, dict, bytes]:
        r,e = self.locate(tag_hash)
        if not r.available(e['index']):
            raise RuntimeError(f"tag {tag_hash} is not resident in package {r.h['pkg_id']:04X}")
        return r,e,r.entry(e['index'])

    def linked(self, tag_hash: str) -> tuple[EntryReader, dict, bytes, EntryReader, dict, bytes]:
        hr,he,hb = self.bytes(tag_hash)
        pr,pe,pb = self.bytes(he['reference'])
        return hr,he,hb,pr,pe,pb


def source_row(r: EntryReader, e: dict) -> dict:
    return {
        'pkg_id': r.h['pkg_id'],
        'package': str(r.pkg),
        'tag_hash': e['tag_hash'].upper(),
        'entry_index': e['index'],
        'reference': e['reference'].upper(),
        'size': e['file_size'],
    }


def mesh_diagnostic(mr: MultiReader, mesh: dict, mesh_index: int) -> dict:
    r0,e0,h0,p0r,p0e,p0 = mr.linked(mesh['vertices1'])
    r1,e1,h1,p1r,p1e,p1 = mr.linked(mesh['vertices2'])
    ri,ei,hi,pir,pie,pi = mr.linked(mesh['indices'])
    dh0 = decode_known(e0, h0, r0.h['platform'])
    dh1 = decode_known(e1, h1, r1.h['platform'])
    dhi = decode_known(ei, hi, ri.h['platform'])
    stride0 = int(dh0.get('stride',0))
    stride1 = int(dh1.get('stride',0))
    if stride0 <= 0 or len(p0) % stride0:
        raise RuntimeError(f'mesh {mesh_index}: invalid position payload/stride {len(p0)}/{stride0}')

    rows0 = [struct.unpack_from('<' + 'h'*(stride0//2), p0, o) for o in range(0,len(p0),stride0)]
    scale = [float(x) for x in mesh['model_scale'][:3]]
    trans = [float(x) for x in mesh['model_translation'][:3]]
    positions = [tuple(snorm16(row[i])*scale[i]+trans[i] for i in range(3)) for row in rows0]
    raw_xyz = [tuple(int(row[i]) for i in range(3)) for row in rows0]
    fourth = [row[3] for row in rows0] if stride0 >= 8 else []
    fourth_counts = collections.Counter(fourth)

    is32 = bool(dhi.get('is32bit'))
    if is32:
        idx = list(struct.unpack('<' + 'I'*(len(pi)//4), pi)); restart=0xFFFFFFFF
    else:
        idx = list(struct.unpack('<' + 'H'*(len(pi)//2), pi)); restart=0xFFFF

    lod_ranges: dict[tuple[int,int,int], list[dict]] = {}
    for part in mesh['parts']:
        if int(part['lod']) != 1:
            continue
        k=(int(part['index_offset']),int(part['index_count']),int(part['primitive_type']))
        lod_ranges.setdefault(k,[]).append(part)
    triangles=[]; range_rows=[]
    for (off,count,primitive),parts in sorted(lod_ranges.items()):
        vals=idx[off:off+count]
        if primitive==5 and not is32:
            tris=strip_to_triangles(vals)
        elif primitive==3:
            tris=[tuple(vals[i:i+3]) for i in range(0,len(vals)-2,3)]
        else:
            tris=[]
        triangles.extend(tris)
        range_rows.append({
            'index_offset':off,'index_count':count,'primitive_type':primitive,
            'materials':sorted({p['material'] for p in parts}),
            'triangle_count':len(tris),'restart_markers':sum(v==restart for v in vals),
        })

    dsu=DSU()
    for a,b,c in triangles:
        if max(a,b,c) < len(positions):
            dsu.union(a,b); dsu.union(b,c)
    tri_by_root=collections.Counter(); verts_by_root=collections.defaultdict(set)
    for a,b,c in triangles:
        if max(a,b,c) >= len(positions): continue
        root=dsu.find(a); tri_by_root[root]+=1; verts_by_root[root].update((a,b,c))
    comps=[]
    for root,verts in verts_by_root.items():
        comps.append({
            'triangle_count':int(tri_by_root[root]),'vertex_count':len(verts),
            'vertex_index_minmax':[min(verts),max(verts)],
            'bbox_tiger_model_space':bbox([positions[v] for v in verts]),
        })
    comps.sort(key=lambda x:(-x['triangle_count'],-x['vertex_count']))
    used=sorted({v for tri in triangles for v in tri if v < len(positions)})

    return {
        'mesh_index':mesh_index,
        'model_scale':mesh['model_scale'],'model_translation':mesh['model_translation'],
        'texcoord_scale':mesh['texcoord_scale'],'texcoord_translation':mesh['texcoord_translation'],
        'position_stream':{
            'header_source':source_row(r0,e0),'header':dh0,'payload_source':source_row(p0r,p0e),
            'payload_size':len(p0),'vertex_count':len(rows0),
            'raw_xyz_min':[min(row[i] for row in raw_xyz) for i in range(3)],
            'raw_xyz_max':[max(row[i] for row in raw_xyz) for i in range(3)],
            'fourth_i16_unique_count':len(fourth_counts),
            'fourth_i16_minmax':[min(fourth),max(fourth)] if fourth else None,
            'fourth_i16_most_common':[[int(k),int(v)] for k,v in fourth_counts.most_common(32)],
            'decoded_bbox_all_tiger_model_space':bbox(positions),
            'decoded_bbox_lod1_used_tiger_model_space':bbox([positions[v] for v in used]),
        },
        'secondary_stream':{
            'header_source':source_row(r1,e1),'header':dh1,'payload_source':source_row(p1r,p1e),
            'payload_size':len(p1),'stride':stride1,
        },
        'index_stream':{
            'header_source':source_row(ri,ei),'header':dhi,'payload_source':source_row(pir,pie),
            'payload_size':len(pi),'index_count':len(idx),
        },
        'lod1_ranges':range_rows,
        'lod1_triangle_count_deduplicated_ranges':len(triangles),
        'lod1_used_vertex_count':len(used),
        'connected_component_count':len(comps),'connected_components':comps,
    }


def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument('pkg',type=Path)
    ap.add_argument('--extra-pkg',type=Path,action='append',default=[])
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--entity',required=True)
    ap.add_argument('--model',required=True)
    ap.add_argument('-o','--output',type=Path)
    a=ap.parse_args()

    mr=MultiReader(a.pkg,a.extra_pkg,a.runtime)
    primary=mr.primary
    entity_hash=a.entity.upper().removeprefix('0X'); model_hash=a.model.upper().removeprefix('0X')
    er,ee,eb=mr.bytes(entity_hash)
    if er is not primary:
        raise RuntimeError('target entity must belong to primary package')

    resource_entries=[e for e in primary.entries if e['type']==16 and e['subtype']==0 and e['reference'].upper()=='80800861']
    resource_hashes={e['tag_hash'].upper() for e in resource_entries}
    literal_hits=resource_literal_refs(eb,resource_hashes)
    linked_resource_hashes=sorted({x['tag_hash'] for x in literal_hits})
    resources=[]
    for h in linked_resource_hashes:
        rr,re,rb=mr.bytes(h)
        row=source_row(rr,re)
        try: row.update(parse_resource(rb,rr.h['platform']))
        except Exception as ex: row['error']=repr(ex)
        resources.append(row)

    mreader,me,mb=mr.bytes(model_hash)
    model=parse_model(mb,mreader.h['platform'])
    meshes=[mesh_diagnostic(mr,m,i) for i,m in enumerate(model['meshes'])]
    report={
        'primary_package':str(primary.pkg),
        'supplied_packages':[{'pkg_id':r.h['pkg_id'],'package':str(r.pkg),'entry_count':len(r.entries)} for r in mr.readers],
        'hash_collisions':mr.collisions,
        'entity':{'tag_hash':entity_hash,**source_row(er,ee),'entity_resource_literal_hits':literal_hits,'unique_entity_resources':linked_resource_hashes,'resources':resources},
        'model':{'tag_hash':model_hash,**source_row(mreader,me),'mesh_count':model['mesh_count'],'meshes':meshes},
        'guardrails':[
            'All cross-package stream provenance is recorded at both header and payload level.',
            'Connected components use only deduplicated LOD1 index ranges.',
            'SNORM16 XYZ * model scale + translation remains an explicit geometry-coordinate hypothesis.',
        ],
    }
    text=json.dumps(report,indent=2)+'\n'
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(text); print('wrote',a.output)
    else: print(text,end='')

if __name__=='__main__': main()
