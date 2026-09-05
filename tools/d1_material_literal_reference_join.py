#!/usr/bin/env python3
"""Join literal TagHash edges from a D1 census to exact texture/header metadata.

This is deliberately conservative: known fixed material fields are named only when
an existing byte-validated material decoder gives that exact field offset. Other
references remain serialized co-references, even when their targets are textures.
"""
from __future__ import annotations
import argparse, csv, json
from collections import defaultdict
from pathlib import Path

KNOWN_PS4_MATERIAL_FIXED_FIELDS = {
    0x28: 'vertex_shader',
    0xAC: 'vs_vector4_container',
    0x2A8: 'pixel_shader',
    0x32C: 'ps_vector4_container',
}

def norm(s: str) -> str:
    return str(s).upper().removeprefix('0X').zfill(8)

def semi(s: str):
    return [x for x in str(s).split(';') if x]

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--literal-edges', type=Path, required=True)
    ap.add_argument('--union-entries', type=Path, required=True)
    ap.add_argument('--texture-manifest', type=Path, action='append', default=[])
    ap.add_argument('--material', action='append', required=True)
    ap.add_argument('--out', type=Path, required=True)
    a=ap.parse_args()
    wanted={norm(x) for x in a.material}

    union={}
    with a.union_entries.open(newline='') as f:
        for r in csv.DictReader(f): union[norm(r['tag_hash'])]=r

    textures={}
    for p in a.texture_manifest:
        d=json.loads(p.read_text())
        for r in d.get('textures',[]):
            textures[norm(r['tag_hash'])]={
                'manifest':str(p), 'chosen_snapshot':r.get('chosen_snapshot'),
                'texture':r.get('texture'), 'portable_files':r.get('portable_files',[])
            }

    collapsed=defaultdict(lambda: {'snapshots':set(),'count':0})
    with a.literal_edges.open(newline='') as f:
        for r in csv.DictReader(f):
            src=norm(r['source_tag_hash'])
            if src not in wanted: continue
            target=norm(r['target_tag_hash'])
            offsets=tuple(int(x,16) for x in semi(r['aligned_offsets']))
            k=(src,target,offsets)
            collapsed[k]['snapshots'].add(r['source_snapshot'])
            collapsed[k]['count'] += int(r['count'])

    mats=[]
    for mh in sorted(wanted):
        meta=union.get(mh)
        refs=[]
        for (src,target,offsets),acc in sorted(collapsed.items()):
            if src!=mh: continue
            tm=union.get(target)
            rec={
                'target_tag_hash':target,
                'aligned_offsets':[f'0x{x:X}' for x in offsets],
                'physical_snapshots':sorted(acc['snapshots']),
                'total_literal_occurrences_across_snapshots':acc['count'],
                'target_type_subtypes':semi(tm['type_subtypes']) if tm else [],
                'target_references':semi(tm['references']) if tm else [],
                'target_metadata_conflicts_across_snapshots': None if not tm else tm['metadata_conflicts_across_snapshots']=='True',
            }
            if len(offsets)==1 and offsets[0] in KNOWN_PS4_MATERIAL_FIXED_FIELDS:
                rec['known_fixed_material_field']=KNOWN_PS4_MATERIAL_FIXED_FIELDS[offsets[0]]
                rec['field_evidence']='exact offset from tools/d1_material_decode.py'
            if target in textures:
                t=textures[target]
                q=t.get('texture') or {}
                rec['resolved_texture_header']={
                    'chosen_snapshot':t.get('chosen_snapshot'), 'format_name':q.get('format_name'),
                    'width':q.get('width'),'height':q.get('height'),'depth':q.get('depth'),
                    'array_size':q.get('array_size'),'stream':q.get('stream'),'backing':q.get('backing'),
                    'png':q.get('png')
                }
                rec['texture_semantic_policy']='serialized material->texture co-reference proven; stage/slot not assigned by this join'
            refs.append(rec)
        mats.append({
            'material_tag_hash':mh,
            'material_union_metadata': None if not meta else {
                'occurrence_count':int(meta['occurrence_count']),
                'resident_occurrence_count':int(meta['resident_occurrence_count']),
                'references':semi(meta['references']), 'type_subtypes':semi(meta['type_subtypes']),
                'file_sizes':semi(meta['file_sizes']),
                'metadata_conflicts_across_snapshots':meta['metadata_conflicts_across_snapshots']=='True',
                'payload_conflicts_across_snapshots':meta['payload_conflicts_across_snapshots']=='True'
            },
            'serialized_references':refs,
        })

    tex_edges=[]
    for m in mats:
        for r in m['serialized_references']:
            if 'resolved_texture_header' in r:
                tex_edges.append((m['material_tag_hash'],r['target_tag_hash'],tuple(r['aligned_offsets'])))
    fixed=[]
    for m in mats:
        for r in m['serialized_references']:
            if r.get('known_fixed_material_field'):
                fixed.append((m['material_tag_hash'],r['known_fixed_material_field'],r['target_tag_hash']))
    out={
        'evidence_status':'SERIALIZED_LITERAL_REFERENCE_JOIN',
        'material_count':len(mats),
        'materials_with_resolved_texture_literal':len({x[0] for x in tex_edges}),
        'unique_resolved_texture_headers':len({x[1] for x in tex_edges}),
        'resolved_texture_literal_edges':len(tex_edges),
        'known_fixed_field_edges':len(fixed),
        'materials':mats,
        'policy':{
            'literal_edges':'aligned literal TagHash equality is serialized co-reference evidence only',
            'fixed_fields':'only offsets already named by tools/d1_material_decode.py are promoted to shader/container semantics',
            'texture_stage_slot':'not inferred here; re-parse material dynamic arrays from shipped bytes before assigning stage or texture_index',
            'patches':'physical snapshots and payload-conflict flags are preserved rather than silently collapsed'
        }
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ('evidence_status','material_count','materials_with_resolved_texture_literal','unique_resolved_texture_headers','resolved_texture_literal_edges','known_fixed_field_edges')},indent=2))
    return 0
if __name__=='__main__': raise SystemExit(main())
