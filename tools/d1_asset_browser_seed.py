#!/usr/bin/env python3
"""Build the compact data seed consumed by the D1 HTML asset browser.

The weapon side is derived from d1_weapon_manifest_join output; map/world roots
come from the archive package census. Public/preserved D1 manifest data is only
presentation enrichment (name/icon/type) and is intentionally not used to
change reverse-engineering resolution status.
"""
from __future__ import annotations
import argparse,csv,json
from pathlib import Path


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--weapon-manifests',type=Path,required=True)
    ap.add_argument('--map-roots',type=Path,required=True)
    ap.add_argument('--archive-inventory',type=Path,required=True)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()
    wr=json.loads(a.weapon_manifests.read_text())
    ar=json.loads(a.archive_inventory.read_text())
    with a.map_roots.open(newline='',encoding='utf-8') as f: maps=list(csv.DictReader(f))
    weapons=[]
    for m in wr['manifests']:
        eq=m.get('equipping') or {}; vis=m.get('visual') or {}; pat=m.get('internal_weapon_pattern') or {}; st=m.get('status') or {}
        arr=[]
        for x in vis.get('arrangements',[]):
            arr.append({'index':x.get('art_arrangement_index'),'entityData':x.get('entity_data_hashes',[]),'entityParents':x.get('entity_parent_hashes',[]),'unresolvedSlots':len(x.get('unresolved_entity_slots',[]))})
        weapons.append({
            'hash':m['inventory_item_hash'],'decimal':int(m['inventory_item_hash'],16),
            'itemFile':(m.get('inventory_definition') or {}).get('file_hash'),
            'arrangementIndices':[x.get('art_arrangement_index') for x in eq.get('art_arrangements',[])],
            'arrangements':arr,'patternIndex':eq.get('weapon_pattern_index'),
            'weaponTypeHash':pat.get('weapon_type_hash'),'patternHash':pat.get('pattern_hash'),'patternEntity':pat.get('pattern_entity'),
            'visualReady':bool(st.get('visual_entity_selection_resolved')),'internalReady':bool(st.get('weapon_pattern_resolved')),
            'sharedReady':bool(st.get('shared_viewmodel_context_resolved')),'fullReady':bool(st.get('resolution_complete_for_current_graph')),
            'unresolved':[x.get('edge') for x in m.get('unresolved_edges',[]) if x.get('edge')],
            'sharedProfile':(m.get('shared_viewmodel') or {}).get('profile'),
        })
    families=[{'prefix':x['prefix'],'members':x['physical_members'],'tokens':x.get('tokens',[])} for x in ar.get('families',[])]
    out={'schema':'d1_asset_browser_seed/v1','counts':{
        'physicalPackages':ar['physical_package_count'],'logicalPackageIds':ar['unique_package_id_count'],'logicalPrefixes':ar['logical_prefix_count'],
        'weaponCandidates':len(weapons),'visualReady':sum(x['visualReady'] for x in weapons),'internalReady':sum(x['internalReady'] for x in weapons),
        'sharedReady':sum(x['sharedReady'] for x in weapons),'fullReady':sum(x['fullReady'] for x in weapons),'mapRoots':len(maps)},
        'weapons':weapons,'maps':maps,'families':families,
        'policy':'Archive/Tiger relationships determine resolution status. Historical D1 manifest names/icons are presentation enrichment only.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out['counts'],indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
