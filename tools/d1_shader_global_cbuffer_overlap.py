#!/usr/bin/env python3
"""Cross-domain census of exact D1 PS4 ImmConstBuffer usage.

Inputs are exact shader-extract reports and d1_gcn_cbuffer_usage/v1 reports from
multiple renderer domains (for example Tower common surfaces, lights, and sky).

The tool aggregates:
* API-slot frequency by shader family and visible-material/light frequency weight;
* exact (API slot, dword) read frequency;
* per-domain and cross-domain intersections;
* shader signatures of constant-buffer reads.

This is structural evidence only.  Recurrence of API13[6] across different shader
families does not by itself name the engine field or prove a producer object.
"""
from __future__ import annotations
import argparse,collections,json
from pathlib import Path

def parse_pair(s):
    if '=' not in s:raise argparse.ArgumentTypeError('expected LABEL=PATH')
    k,p=s.split('=',1)
    if not k or not p:raise argparse.ArgumentTypeError('expected LABEL=PATH')
    return k,Path(p)

def norm(x):return str(x).upper().removeprefix('0X').zfill(8)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--extract',action='append',type=parse_pair,required=True)
    ap.add_argument('--cbuffer',action='append',type=parse_pair,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    extracts=dict(a.extract);cbuffers=dict(a.cbuffer);violations=[]
    if set(extracts)!=set(cbuffers):
        violations.append(f'label mismatch extract={sorted(extracts)} cbuffer={sorted(cbuffers)}')
    labels=sorted(set(extracts)&set(cbuffers))
    domains={}

    for label in labels:
        ex=json.loads(extracts[label].read_text())
        cb=json.loads(cbuffers[label].read_text())
        if ex.get('status')!='D1_WORLD_PIXEL_SHADER_GCN_EXACT' or ex.get('error_count'):
            violations.append(f'{label}: extract not exact')
        if cb.get('status')!='D1_GCN_CBUFFER_USAGE_EXACT' or cb.get('missing_usage'):
            violations.append(f'{label}: cbuffer report not exact')
        freq={norm(x['shader']):int(x.get('visible_material_count',0)) for x in ex.get('shaders',[]) if not x.get('error')}
        rows={norm(x['shader']):x for x in cb.get('shaders',[])}
        missing=sorted(set(freq)-set(rows))
        if missing:violations.append(f'{label}: cbuffer rows missing {missing}')

        slot_shaders=collections.defaultdict(set);slot_weight=collections.Counter()
        dw_shaders=collections.defaultdict(set);dw_weight=collections.Counter()
        signatures=collections.Counter();shader_rows=[]
        for sh,w in sorted(freq.items()):
            r=rows.get(sh)
            if r is None:continue
            slots={int(api):tuple(int(x) for x in dws) for api,dws in (r.get('api_slot_read_dwords') or {}).items()}
            sig=tuple((api,vals) for api,vals in sorted(slots.items()))
            signatures[sig]+=1
            for api,vals in slots.items():
                slot_shaders[api].add(sh);slot_weight[api]+=w
                for dw in vals:
                    dw_shaders[(api,dw)].add(sh);dw_weight[(api,dw)]+=w
            shader_rows.append({
                'shader':sh,'weight':w,
                'api_slot_read_dwords':{str(api):list(vals) for api,vals in sorted(slots.items())},
                'resolved_scalar_buffer_load_count':int(r.get('resolved_load_count',0)),
                'unresolved_scalar_buffer_load_count':int(r.get('unresolved_load_count',0)),
            })

        domains[label]={
            'shader_count':len(shader_rows),
            'weight_sum':sum(x['weight'] for x in shader_rows),
            'slot_rows':[{
                'api_slot':api,'shader_family_count':len(shs),'weight_sum':slot_weight[api],
                'shaders':sorted(shs),
            } for api,shs in sorted(slot_shaders.items())],
            'dword_rows':[{
                'api_slot':api,'dword':dw,'shader_family_count':len(shs),'weight_sum':dw_weight[(api,dw)],
                'shaders':sorted(shs),
            } for (api,dw),shs in sorted(dw_shaders.items())],
            'shader_rows':shader_rows,
        }

    # Convert each domain to sets for exact intersections.
    domain_sets={}
    for label,d in domains.items():
        domain_sets[label]={
            (int(x['api_slot']),int(x['dword'])) for x in d['dword_rows']
        }

    all_intersection=set.intersection(*(domain_sets[x] for x in labels)) if labels else set()
    pairwise=[]
    for i,a0 in enumerate(labels):
        for b in labels[i+1:]:
            inter=domain_sets[a0]&domain_sets[b]
            pairwise.append({
                'domains':[a0,b],
                'shared_api_dword_count':len(inter),
                'shared_api_dwords':[{'api_slot':x,'dword':y} for x,y in sorted(inter)],
            })

    # Recurrence matrix for every observed API/dword.
    universe=set().union(*(domain_sets[x] for x in labels)) if labels else set()
    recurrence=[]
    for api,dw in sorted(universe):
        present=[x for x in labels if (api,dw) in domain_sets[x]]
        detail={}
        for label in present:
            row=next(x for x in domains[label]['dword_rows'] if x['api_slot']==api and x['dword']==dw)
            detail[label]={'shader_family_count':row['shader_family_count'],'weight_sum':row['weight_sum']}
        recurrence.append({
            'api_slot':api,'dword':dw,'domain_count':len(present),'domains':present,'domain_stats':detail,
        })
    recurrence.sort(key=lambda x:(-x['domain_count'],-sum(v['weight_sum'] for v in x['domain_stats'].values()),x['api_slot'],x['dword']))

    out={
        'schema':'d1_shader_global_cbuffer_overlap/v1',
        'status':'D1_SHADER_GLOBAL_CBUFFER_OVERLAP_EXACT' if domains and not violations else 'D1_SHADER_GLOBAL_CBUFFER_OVERLAP_PARTIAL',
        'domain_count':len(domains),'domains':domains,
        'all_domain_shared_api_dwords':[{'api_slot':a0,'dword':d} for a0,d in sorted(all_intersection)],
        'pairwise_intersections':pairwise,
        'recurrence_rows':recurrence,
        'violations':violations,
        'semantic_boundary':{
            'api_slot_and_dword_reads':'EXACT_NATIVE_PROVENANCE',
            'cross_domain_recurrence':'EXACT_SET_RELATION',
            'engine_field_names':'WITHHELD',
            'producer_objects':'WITHHELD',
            'live_runtime_values':'WITHHELD',
        },
        'policy':'Cross-domain recurrence narrows likely renderer-global interfaces but never names a field or producer from slot/dword coincidence alone.',
    }
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({
        'status':out['status'],'domains':{k:{'shaders':v['shader_count'],'weight_sum':v['weight_sum']} for k,v in domains.items()},
        'all_domain_shared_api_dwords':out['all_domain_shared_api_dwords'],
        'top_recurrence':recurrence[:40],'violations':violations,
    },indent=2))
    return 0 if out['status']=='D1_SHADER_GLOBAL_CBUFFER_OVERLAP_EXACT' else 2

if __name__=='__main__':raise SystemExit(main())
