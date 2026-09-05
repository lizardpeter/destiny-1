#!/usr/bin/env python3
"""Summarize D1 Tower baked-static readiness without weakening ownership evidence.

Consumes a strict Tower static-map validator report (v1 or v2) plus the literal-
coherence map resource chain census. For legacy v1 reports, Vertices1 == FFFFFFFF
is reinterpreted using the narrow v2 rule: secondary V1 is optional only for that
exact sentinel; V0 and indices remain mandatory.

This does not re-parse package bytes. Therefore v1-derived passes are labelled as
"would pass v2 semantics", not fresh binary validation. MapDataEntry outer placement
ownership is also not promoted here; that still requires the +0x88 ResourcePointer
binary validator.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path

NULL = 'FFFFFFFF'

def norm(x): return str(x).upper().removeprefix('0X').zfill(8)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--validation-json',type=Path,required=True)
    ap.add_argument('--chain-census-json',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    v=json.loads(a.validation_json.read_text())
    c=json.loads(a.chain_census_json.read_text())
    d1rows={norm(x['hash']):x for x in v.get('static_map_data_d1',[])}

    cells=[]
    for table in c.get('strict_0x18_cadence_tables',[]):
        for dr in table.get('direct_d1_child_rows',[]):
            for child in dr.get('d1_children',[]):
                h=norm(child); r=d1rows.get(h)
                cell={
                    'map_data_table':norm(table['map_data_table']),
                    'snapshot':table.get('snapshot'),
                    'static_map_parent':norm(dr['parent']),
                    'static_map':norm(dr['static_map']),
                    'd1_static_map_data':h,
                    'literal_offset':dr.get('literal_offset'),
                    'ownership_status':'LITERAL_COHERENCE_ONLY_PENDING_MAPDATA_RESOURCEPOINTER_VALIDATION',
                }
                if not r:
                    cell.update(status='VALIDATOR_ROW_ABSENT',parseable=False)
                    cells.append(cell); continue

                tables=r.get('static_tables',[])
                total=good=bad=placements=ready_placements=blocked_placements=null_v1=0
                missing=[]
                for t in tables:
                    mesh_ready=[]
                    for m in t.get('mesh_entries',[]):
                        total+=1
                        tg=m.get('targets',{})
                        v0=norm(m.get('vertices0','0')); v1=norm(m.get('vertices1','0')); ind=norm(m.get('indices','0'))
                        v1_null=(v1==NULL); null_v1+=int(v1_null)
                        ok=(tg.get('vertices0') is not None and tg.get('indices') is not None and
                            (v1_null or tg.get('vertices1') is not None))
                        mesh_ready.append(ok)
                        if ok: good+=1
                        else:
                            bad+=1
                            if tg.get('vertices0') is None: missing.append(('vertices0',v0))
                            if (not v1_null) and tg.get('vertices1') is None: missing.append(('vertices1',v1))
                            if tg.get('indices') is None: missing.append(('indices',ind))
                    for info in t.get('info_entries',[]):
                        n=int(info.get('instance_count',0)); si=int(info.get('static_index',-1))
                        placements+=n
                        if 0 <= si < len(mesh_ready) and mesh_ready[si]: ready_placements+=n
                        else: blocked_placements+=n

                blockers=[x for x in r.get('violations',[]) if x!='one or more static tables failed invariants']
                all_info=all(i.get('all_indices_in_bounds',True) for t in tables for i in t.get('info_entries',[]))
                parseable=bool(tables) and all_info and not blockers
                if parseable and bad==0:
                    fresh_v2=all(t.get('validator_revision')=='v2_optional_vertices1_null_sentinel' for t in tables)
                    status='BINARY_VALIDATED_V2_READY' if fresh_v2 and r.get('ok') else 'WOULD_PASS_V2_SEMANTICS_FROM_PRESERVED_BINARY_REPORT'
                elif parseable:
                    status='DEPENDENCY_INCOMPLETE'
                else:
                    status='STRUCTURAL_OR_LAYOUT_BLOCKER'
                cell.update({
                    'status':status,'parseable':parseable,'legacy_validator_ok':bool(r.get('ok')),
                    'instance_count':r.get('instance_count'),'static_table_count':len(tables),
                    'mesh_records':total,'mesh_records_ready':good,'mesh_records_blocked':bad,
                    'mesh_ready_percent':(100.0*good/total if total else None),
                    'placed_geometry_references':placements,'placed_references_ready':ready_placements,
                    'placed_references_blocked':blocked_placements,
                    'placed_ready_percent':(100.0*ready_placements/placements if placements else None),
                    'null_vertices1_records':null_v1,
                    'unique_missing_required_targets':[{'field':f,'hash':hh} for f,hh in sorted(set(missing))],
                    'structural_blockers':blockers,
                })
                cells.append(cell)

    parse=[x for x in cells if x.get('parseable')]
    mt=sum(x.get('mesh_records',0) for x in parse); mg=sum(x.get('mesh_records_ready',0) for x in parse)
    pt=sum(x.get('placed_geometry_references',0) for x in parse); pg=sum(x.get('placed_references_ready',0) for x in parse)
    rep={
      'schema_version':1,
      'evidence_status':'READINESS_REINTERPRETATION_NOT_NEW_PACKAGE_VALIDATION',
      'policy':{
        'v1_null_v1_rule':'FFFFFFFF is accepted only for Vertices1; V0 and indices stay mandatory',
        'outer_placement':'not promoted; requires MapDataEntry +0x88 ResourcePointer binary validation',
        'partial_geometry':'ready counts indicate recoverable records/placements, not a claim that an incomplete cell is complete',
      },
      'summary':{
        'strict_map_tables':len(c.get('strict_0x18_cadence_tables',[])),
        'direct_d1_child_cells':len(cells),
        'parseable_cells':len(parse),
        'structural_or_layout_blockers':sum(x.get('status')=='STRUCTURAL_OR_LAYOUT_BLOCKER' for x in cells),
        'cells_with_all_required_buffers_under_v2_semantics':sum(x.get('mesh_records_blocked')==0 and x.get('parseable') for x in cells),
        'parseable_mesh_records':mt,'ready_mesh_records':mg,'ready_mesh_percent':100.0*mg/mt if mt else None,
        'parseable_placed_geometry_references':pt,'ready_placed_geometry_references':pg,
        'ready_placed_percent':100.0*pg/pt if pt else None,
      },
      'cells':cells,
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(rep,indent=2)+'\n')
    print(json.dumps(rep['summary'],indent=2))

if __name__=='__main__': main()
