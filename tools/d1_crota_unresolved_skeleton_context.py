#!/usr/bin/env python3
"""Extract exact structural context for Crota skeleton nodes lacking lineage names.

Consumes d1_crota_named_skeleton_usage/v1 and emits only the unresolved-name nodes,
including exact hierarchy, skin, selected-clip motion and runtime-control evidence.

This is deliberately not a naming heuristic. It exists so unknown FNV-1 hashes can
be reasoned about structurally without inventing anatomy.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

EXPECTED={'0E355AA8','A485F9B8','A91E97AF','57F11E8A'}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--named-usage',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    d=json.loads(a.named_usage.read_text());v=[]
    if d.get('status')!='D1_CROTA_NAMED_SKELETON_USAGE_EXACT_JOIN' or d.get('violations'):
        v.append('named skeleton usage not exact')
    rows=d.get('nodes') or []
    byidx={int(x['index']):x for x in rows}
    unresolved=[x for x in rows if not x.get('bungie_name')]
    got={str(x.get('node_hash')) for x in unresolved}
    if got!=EXPECTED:v.append(f'unresolved hash set drift {sorted(got)} != {sorted(EXPECTED)}')

    outrows=[]
    for x in unresolved:
        i=int(x['index']);pi=x.get('parent_node_index')
        parent=byidx.get(int(pi)) if pi is not None and int(pi)>=0 else None
        children=[q for q in rows if q.get('parent_node_index') is not None and int(q['parent_node_index'])==i]
        outrows.append({
            'index':i,'node_hash':x['node_hash'],
            'parent':None if parent is None else {
                'index':int(parent['index']),'node_hash':parent['node_hash'],
                'bungie_name':parent.get('bungie_name'),
            },
            'children':[{
                'index':int(q['index']),'node_hash':q['node_hash'],
                'bungie_name':q.get('bungie_name'),
            } for q in children],
            'first_child_node_index':x.get('first_child_node_index'),
            'next_sibling_node_index':x.get('next_sibling_node_index'),
            'structural_pattern':x.get('structural_pattern'),
            'skin_reference_count':int(x.get('skin_reference_count',0)),
            'skin_mesh_indices':x.get('skin_mesh_indices') or [],
            'dynamic_any_clip_instances':int(x.get('dynamic_any_clip_instances',0)),
            'dynamic_scale_clip_instances':int(x.get('dynamic_scale_clip_instances',0)),
            'dynamic_rotation_clip_instances':int(x.get('dynamic_rotation_clip_instances',0)),
            'dynamic_translation_clip_instances':int(x.get('dynamic_translation_clip_instances',0)),
            'runtime_controls':x.get('runtime_controls') or [],
            'has_shared_prefix_control':bool(x.get('has_shared_prefix_control')),
            'has_target_only_suffix_control':bool(x.get('has_target_only_suffix_control')),
            'fnv1_name_status':'UNRESOLVED_IN_PINNED_LINEAGE_TABLE',
        })
    out={
        'schema':'d1_crota_unresolved_skeleton_context/v1',
        'status':'D1_CROTA_UNRESOLVED_SKELETON_CONTEXT_EXACT' if len(outrows)==4 and not v else 'D1_CROTA_UNRESOLVED_SKELETON_CONTEXT_PARTIAL',
        'skeleton_resource':d.get('skeleton_resource'),
        'unresolved_node_count':len(outrows),
        'nodes':outrows,'violations':v,
        'evidence_boundary':{
            'node_hash_hierarchy':'EXACT_RETAIL_ENTITYSKELETON',
            'skin_motion_control_usage':'EXACT_RETAIL_STRUCTURAL_OBSERVATION',
            'human_readable_name':'WITHHELD',
            'anatomical_or_gameplay_role':'WITHHELD',
        },
        'policy':'Unknown node hashes remain unknown. Parent/child adjacency, skin references, selected-clip motion and runtime-control mappings may constrain future reverse-hash work but do not themselves justify an anatomical name.',
    }
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'status':out['status'],'nodes':outrows,'violations':v},indent=2))
    return 0 if out['status']=='D1_CROTA_UNRESOLVED_SKELETON_CONTEXT_EXACT' else 2

if __name__=='__main__':raise SystemExit(main())
