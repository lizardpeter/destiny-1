#!/usr/bin/env python3
from __future__ import annotations
import argparse, collections, json, re
from pathlib import Path

MAP_DATA_TABLE='808009A2'
STATIC_MAP_PARENT='80801AC6'
STATIC_MAP_DATA='808008B4'
STATIC_MAP_D1='80801B75'

def gen(name):
    m=re.search(r'_(\d+)\.pkg$',name)
    return int(m.group(1)) if m else -1

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('census',type=Path)
    ap.add_argument('-o','--out',type=Path,required=True)
    a=ap.parse_args(); d=json.loads(a.census.read_text())
    tag_refs=collections.defaultdict(set)
    for e in d['union_entries']:
        tag_refs[e['tag_hash']].update(x.upper() for x in e.get('references',[]))
    def iscls(tag,cls): return cls in tag_refs.get(tag,set())

    # Index physical literal edges by (snapshot, source).
    by_src=collections.defaultdict(list)
    for e in d['literal_edges']:
        by_src[(e['source_snapshot'],e['source_tag_hash'])].append(e)

    parent_static_pairs=set(); static_child_pairs=set()
    all_static={t for t,refs in tag_refs.items() if STATIC_MAP_DATA in refs}
    all_parent={t for t,refs in tag_refs.items() if STATIC_MAP_PARENT in refs}
    all_tables={t for t,refs in tag_refs.items() if MAP_DATA_TABLE in refs}

    for e in d['literal_edges']:
        s,t=e['source_tag_hash'],e['target_tag_hash']
        if iscls(s,STATIC_MAP_PARENT) and iscls(t,STATIC_MAP_DATA) and e.get('aligned_offsets')==[8]:
            parent_static_pairs.add((s,t))
        if iscls(s,STATIC_MAP_DATA) and iscls(t,STATIC_MAP_D1) and 0x30 in e.get('aligned_offsets',[]):
            static_child_pairs.add((s,t))

    static_to_parents=collections.defaultdict(set)
    for p,s in parent_static_pairs: static_to_parents[s].add(p)
    static_to_children=collections.defaultdict(set)
    for s,c in static_child_pairs: static_to_children[s].add(c)

    # For each table, select newest physical snapshot and summarize exact same-snapshot chains.
    table_occ=collections.defaultdict(set)
    for e in d['physical_occurrences']:
        if e['tag_hash'] in all_tables and e.get('available'):
            table_occ[e['tag_hash']].add(e['snapshot'])
    tables=[]
    for th in sorted(all_tables):
        snaps=sorted(table_occ.get(th,[]), key=lambda s:(gen(s),s))
        if not snaps: continue
        snap=snaps[-1]
        pedges=[]
        for e in by_src.get((snap,th),[]):
            if iscls(e['target_tag_hash'],STATIC_MAP_PARENT):
                for off in e.get('aligned_offsets',[]):
                    pedges.append((off,e['target_tag_hash']))
        pedges=sorted(set(pedges))
        if not pedges: continue
        rows=[]
        for off,p in pedges:
            sm=[]
            for e in by_src.get((snap,p),[]):
                if e.get('aligned_offsets')==[8] and iscls(e['target_tag_hash'],STATIC_MAP_DATA):
                    sm.append(e['target_tag_hash'])
            sm=sorted(set(sm))
            children={}
            for s in sm:
                cs=[]
                for e in by_src.get((snap,s),[]):
                    if 0x30 in e.get('aligned_offsets',[]) and iscls(e['target_tag_hash'],STATIC_MAP_D1):
                        cs.append(e['target_tag_hash'])
                children[s]=sorted(set(cs))
            rows.append({'literal_offset':off,'parent':p,'static_maps_at_parent_plus_0x08':sm,'d1_children_at_static_plus_0x30':children})
        offs=[x[0] for x in pedges]
        diffs=[b-a for a,b in zip(offs,offs[1:])]
        tables.append({
            'map_data_table':th,'snapshot':snap,'parent_literal_count':len(rows),
            'first_parent_literal_offset':offs[0] if offs else None,
            'last_parent_literal_offset':offs[-1] if offs else None,
            'strict_0x18_parent_literal_cadence':bool(len(offs)>=2 and all(x==0x18 for x in diffs)),
            'parent_literal_deltas':diffs,
            'rows':rows,
        })

    strict=[x for x in tables if x['strict_0x18_parent_literal_cadence']]
    exact_0250=next((x for x in tables if x['map_data_table']=='80CA0B0E'),None)
    out={
      'schema_version':1,
      'evidence_status':'LITERAL_COHERENCE_CENSUS_NOT_RESOURCE_POINTER_VALIDATION',
      'source_policy':'Class membership comes from physical entry reference hashes. Edges are aligned literal TagHash evidence only unless field offsets are independently validated. +0x08 parent and +0x30 child offsets are recorded as structural coherence, while MapDataEntry ResourcePointer ownership remains unpromoted until raw-pointer validation.',
      'classes':{'map_data_table':MAP_DATA_TABLE,'static_map_parent':STATIC_MAP_PARENT,'static_map_data':STATIC_MAP_DATA,'static_map_d1':STATIC_MAP_D1},
      'summary':{
        'unique_map_data_table_candidates':len(all_tables),
        'unique_static_map_parent_candidates':len(all_parent),
        'unique_static_map_data_candidates':len(all_static),
        'unique_parent_plus_0x08_static_map_pairs':len(parent_static_pairs),
        'static_maps_with_parent_plus_0x08':len(static_to_parents),
        'unique_static_plus_0x30_d1_child_pairs':len(static_child_pairs),
        'static_maps_with_direct_plus_0x30_d1_child':len(static_to_children),
        'latest_map_tables_with_parent_literals':len(tables),
        'latest_map_tables_with_strict_0x18_parent_literal_cadence':len(strict),
      },
      'static_maps':[
        {'static_map':s,'parent_count':len(static_to_parents.get(s,set())),'parents':sorted(static_to_parents.get(s,set())),
         'd1_children':sorted(static_to_children.get(s,set()))}
        for s in sorted(all_static)
      ],
      'map_tables':tables,
      'focus_80CA0B0E':exact_0250,
    }
    a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out['summary'],indent=2))
    if exact_0250:
        print('80CA0B0E',json.dumps({k:exact_0250[k] for k in exact_0250 if k!='rows'},indent=2))
        print('rows',json.dumps(exact_0250['rows'],indent=2))
if __name__=='__main__': main()
