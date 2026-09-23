#!/usr/bin/env python3
"""Classify recurrent D1 renderer cbuffer dwords by terminal MRT0 impact.

Consumes the exact cross-domain cbuffer-read overlap plus exact terminal MRT0
dependency reports for the same domains. For every recurrent (API slot,dword),
records whether the dword merely appears in native cbuffer reads or actually
reaches one or more terminal MRT0 lanes.

This is a dataflow prioritization proof only. A terminal-impacting API/dword is
not assigned an engine field name or producer object.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

def parse_pair(s):
    if '=' not in s:raise argparse.ArgumentTypeError('expected LABEL=PATH')
    k,p=s.split('=',1)
    if not k or not p:raise argparse.ArgumentTypeError('expected LABEL=PATH')
    return k,Path(p)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--overlap',type=Path,required=True)
    ap.add_argument('--terminal',action='append',type=parse_pair,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    ov=json.loads(a.overlap.read_text());terms={k:json.loads(p.read_text()) for k,p in a.terminal}
    v=[];rows=[]
    if ov.get('status')!='D1_SHADER_GLOBAL_CBUFFER_OVERLAP_EXACT' or ov.get('violations'):
        v.append('overlap input not exact')
    labels=sorted(ov.get('domains',{}))
    if set(labels)!=set(terms):v.append(f'domain mismatch overlap={labels} terminal={sorted(terms)}')
    for label,d in terms.items():
        if d.get('status')!='D1_GCN_TERMINAL_MRT0_DEPENDENCY_CENSUS_EXACT' or d.get('violations'):
            v.append(f'{label}: terminal MRT0 report not exact')
    weights={
        label:{str(x['shader']).upper():int(x['weight']) for x in (ov['domains'][label].get('shader_rows') or [])}
        for label in labels
    }
    tby={label:{str(x['shader']).upper():x for x in terms[label].get('shaders',[])} for label in labels}

    for r in ov.get('recurrence_rows',[]):
        if int(r.get('domain_count',0))<2:continue
        api=int(r['api_slot']);dw=int(r['dword']);impact={}
        for label in r['domains']:
            hits=[];weight=0
            for sh,tr in tby[label].items():
                chs={}
                for ch in ('R','G','B','A'):
                    q=(((tr.get('channels') or {}).get(ch) or {}).get('value_slice') or {})
                    if dw in {int(x) for x in (q.get('cbuffer_dwords') or {}).get(str(api),[])}:
                        chs[ch]=True
                if chs:
                    w=weights[label].get(sh,0);weight+=w
                    hits.append({'shader':sh,'weight':w,'channels':sorted(chs)})
            impact[label]={
                'terminal_shader_family_count':len(hits),
                'terminal_weight_sum':weight,
                'terminal_shaders':sorted(hits,key=lambda x:(-x['weight'],x['shader'])),
            }
        reading=set(r['domains'])
        terminal_domains={k for k,x in impact.items() if x['terminal_shader_family_count']>0}
        if not terminal_domains:cls='READ_ONLY_NO_TERMINAL_IMPACT'
        elif terminal_domains==reading:cls='TERMINAL_IMPACT_IN_ALL_READING_DOMAINS'
        else:cls='TERMINAL_IMPACT_IN_SUBSET_OF_READING_DOMAINS'
        rows.append({
            'api_slot':api,'dword':dw,'reading_domain_count':len(reading),
            'reading_domains':sorted(reading),'read_domain_stats':r['domain_stats'],
            'terminal_domain_count':len(terminal_domains),'terminal_domains':sorted(terminal_domains),
            'terminal_impact':impact,'impact_class':cls,
        })
    rows.sort(key=lambda x:(
        -x['terminal_domain_count'],
        -sum(q['terminal_weight_sum'] for q in x['terminal_impact'].values()),
        -x['reading_domain_count'],x['api_slot'],x['dword']))

    all3=[x for x in rows if x['reading_domain_count']==3]
    all3_readonly=[{'api_slot':x['api_slot'],'dword':x['dword']} for x in all3 if x['terminal_domain_count']==0]
    all3_terminal=[{'api_slot':x['api_slot'],'dword':x['dword'],'terminal_domains':x['terminal_domains']} for x in all3 if x['terminal_domain_count']>0]
    out={
        'schema':'d1_shader_global_cbuffer_terminal_impact/v1',
        'status':'D1_SHADER_GLOBAL_CBUFFER_TERMINAL_IMPACT_EXACT' if rows and not v else 'D1_SHADER_GLOBAL_CBUFFER_TERMINAL_IMPACT_PARTIAL',
        'domain_count':len(labels),'domains':labels,'recurrent_dword_count':len(rows),
        'all_three_domain_read_only_dwords':all3_readonly,
        'all_three_domain_terminal_impact_dwords':all3_terminal,
        'rows':rows,'violations':v,
        'semantic_boundary':{
            'cbuffer_read_recurrence':'EXACT_NATIVE_PROVENANCE',
            'terminal_mrt0_impact':'EXACT_NATIVE_DATAFLOW',
            'engine_field_names':'WITHHELD',
            'producer_objects':'WITHHELD',
            'live_runtime_values':'WITHHELD',
        },
        'policy':'Read recurrence and terminal impact are kept separate. A dword read by all domains but absent from terminal MRT0 dataflow is not promoted as a final-output control; a terminal-impacting dword still receives no human semantic or producer identity without independent evidence.',
    }
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({
        'status':out['status'],'all_three_read_only':all3_readonly,
        'all_three_terminal':all3_terminal,
        'top_terminal_rows':rows[:30],'violations':v,
    },indent=2))
    return 0 if out['status']=='D1_SHADER_GLOBAL_CBUFFER_TERMINAL_IMPACT_EXACT' else 2
if __name__=='__main__':raise SystemExit(main())
