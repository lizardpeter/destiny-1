#!/usr/bin/env python3
"""Summarize a d1_everything_family_census without assigning semantics.

The output is a triage aid for reverse engineering world/package structure. It groups
physical class/reference hashes and aligned literal TagHash co-references by source
and target reference class. Frequency is *not* treated as semantic proof.
"""
from __future__ import annotations
import argparse, csv, json
from collections import Counter, defaultdict
from pathlib import Path


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('census',type=Path)
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args(); args.out.mkdir(parents=True,exist_ok=True)
    d=json.load(open(args.census))
    occ=d['physical_occurrences']; union={x['tag_hash']:x for x in d['union_entries']}
    by_tag=defaultdict(list)
    for i,o in enumerate(occ): by_tag[o['tag_hash']].append((i,o))

    class_stats=defaultdict(lambda:{'occurrences':0,'resources':set(),'sizes':Counter(),'types':Counter(),'resident':0,'literal_out':0,'literal_in':0})
    for o in occ:
        s=class_stats[o['reference']]; s['occurrences']+=1; s['resources'].add(o['tag_hash']); s['sizes'][o['file_size']]+=1
        s['types'][f"{o['type']}:{o['subtype']}"]+=1; s['resident']+=int(o['available'])

    matrix=Counter(); source_target_resources=defaultdict(set); offset_patterns=defaultdict(Counter)
    for e in d.get('literal_edges',[]):
        so=occ[e['source_occurrence_index']]
        src_ref=so['reference']
        target=e['target_tag_hash']
        target_refs=union.get(target,{}).get('references',[]) or ['UNKNOWN']
        class_stats[src_ref]['literal_out'] += e['count']
        for tr in target_refs:
            class_stats[tr]['literal_in'] += e['count']
            matrix[(src_ref,tr)] += e['count']
            source_target_resources[(src_ref,tr)].add((so['tag_hash'],target))
            for off in e.get('aligned_offsets',[]): offset_patterns[(src_ref,tr)][off] += 1

    class_rows=[]
    for ref,s in class_stats.items():
        class_rows.append({
            'reference':ref,
            'known_label':d.get('known_reference_labels',{}).get(ref,''),
            'physical_occurrences':s['occurrences'],
            'unique_resources':len(s['resources']),
            'resident_occurrences':s['resident'],
            'aligned_literal_out_hits':s['literal_out'],
            'aligned_literal_in_hits':s['literal_in'],
            'type_subtypes':dict(s['types'].most_common()),
            'common_sizes':s['sizes'].most_common(12),
        })
    class_rows.sort(key=lambda x:(-x['aligned_literal_out_hits'],-x['unique_resources'],x['reference']))

    matrix_rows=[]
    for (sr,tr),hits in matrix.most_common():
        pairs=source_target_resources[(sr,tr)]
        matrix_rows.append({
            'source_reference':sr,
            'source_label':d.get('known_reference_labels',{}).get(sr,''),
            'target_reference':tr,
            'target_label':d.get('known_reference_labels',{}).get(tr,''),
            'literal_hit_count':hits,
            'distinct_source_target_resource_pairs':len(pairs),
            'common_aligned_offsets':offset_patterns[(sr,tr)].most_common(20),
            'policy':'triage/co-reference only; frequency and offset regularity do not establish semantic ownership'
        })

    # Focus views are useful but still evidence-only.
    known_targets={'80801AB5','80800734','80800861','808005A1','808006BD','8080049A','808008B2','8080222A'}
    edges_to_known=[x for x in matrix_rows if x['target_reference'] in known_targets]

    out={
        'source':str(args.census),
        'policy':'This report ranks/aggregates raw class and aligned-literal evidence only. It makes no class-name, owner, placement, map-chunk, material, or animation assignment.',
        'class_count':len(class_rows),
        'reference_classes':class_rows,
        'reference_matrix':matrix_rows,
        'edges_to_previously_validated_classes':edges_to_known,
    }
    (args.out/'reference_matrix.json').write_text(json.dumps(out,indent=2)+'\n')
    with (args.out/'reference_classes.csv').open('w',newline='') as f:
        fields=['reference','known_label','physical_occurrences','unique_resources','resident_occurrences','aligned_literal_out_hits','aligned_literal_in_hits','type_subtypes','common_sizes']
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for r in class_rows:
            q=r.copy();q['type_subtypes']=json.dumps(q['type_subtypes'],separators=(',',':'));q['common_sizes']=json.dumps(q['common_sizes'],separators=(',',':'));w.writerow(q)
    with (args.out/'reference_matrix.csv').open('w',newline='') as f:
        fields=['source_reference','source_label','target_reference','target_label','literal_hit_count','distinct_source_target_resource_pairs','common_aligned_offsets','policy']
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for r in matrix_rows:
            q=r.copy();q['common_aligned_offsets']=json.dumps(q['common_aligned_offsets'],separators=(',',':'));w.writerow(q)
    print(json.dumps({'class_count':len(class_rows),'matrix_pairs':len(matrix_rows),'edges_to_validated_classes':len(edges_to_known)},indent=2))
    return 0

if __name__=='__main__': raise SystemExit(main())
