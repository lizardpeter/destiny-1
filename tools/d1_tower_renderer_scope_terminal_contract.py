#!/usr/bin/env python3
"""Join exact D1 PS4 CBuffer scope names to Tower terminal-output impact.

Inputs:
* d1_ps4_cbuffer_scope_name_proof/v1
* d1_shader_global_cbuffer_terminal_impact/v1

The source proof promotes only the scope names:
  api12 -> View
  api13 -> Frame

The terminal-impact proof establishes exactly which dwords in those scopes survive
to Tower common/sky/light MRT0 outputs.  This adapter joins those facts without
promoting runtime writer, backing allocation, live values, or field-level names.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

EXPECTED = {
    12: {
        'source_name':'View',
        'terminal_dwords':{
            28:['common','sky'],
            29:['common','sky'],
            30:['common','sky'],
        },
        'nonterminal_guard':{31:[]},
    },
    13: {
        'source_name':'Frame',
        'terminal_dwords':{
            6:['common','sky'],
            7:['common','sky'],
        },
        'nonterminal_guard':{},
    },
}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--scope-proof',type=Path,required=True)
    ap.add_argument('--terminal-impact',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()

    sp=json.loads(a.scope_proof.read_text())
    ti=json.loads(a.terminal_impact.read_text())
    v=[]

    if sp.get('schema')!='d1_ps4_cbuffer_scope_name_proof/v1':
        v.append('scope proof schema drift')
    if sp.get('status')!='D1_PS4_CBUFFER_SCOPE_NAMES_CROSS_SOURCE_EXACT' or sp.get('violations'):
        v.append('scope proof not exact')
    if ti.get('status')!='D1_SHADER_GLOBAL_CBUFFER_TERMINAL_IMPACT_EXACT' or ti.get('violations'):
        v.append('terminal impact not exact')

    promoted=sp.get('promoted_scope_names') or {}
    rows=ti.get('rows') or ti.get('recurrence_rows') or []
    by={(int(x['api_slot']),int(x['dword'])):x for x in rows}

    scopes=[]
    for api in (12,13):
        cfg=EXPECTED[api]
        src=promoted.get(f'api{api}') or {}
        if src.get('source_name')!=cfg['source_name']:
            v.append(f'api{api}: source name drift {src.get("source_name")!r}')
        if src.get('name_status')!='SOURCE_CORRELATED_EXACT':
            v.append(f'api{api}: source name not exact')
        for key in ('runtime_writer','backing_allocation','live_values','field_names'):
            if src.get(key)!='WITHHELD':
                v.append(f'api{api}: unexpected promotion of {key}: {src.get(key)!r}')

        terminal=[]
        for dw,domains in sorted(cfg['terminal_dwords'].items()):
            r=by.get((api,dw))
            if not r:
                v.append(f'api{api}[{dw}]: terminal-impact row missing')
                continue
            got=list(r.get('terminal_domains') or [])
            if got!=domains:
                v.append(f'api{api}[{dw}]: terminal domains {got} != {domains}')
            if r.get('impact_class')!='TERMINAL_IMPACT_IN_ALL_READING_DOMAINS':
                v.append(f'api{api}[{dw}]: impact class drift {r.get("impact_class")}')
            terminal.append({
                'dword':dw,
                'terminal_domains':got,
                'reading_domains':r.get('reading_domains') or [],
                'read_domain_stats':r.get('read_domain_stats') or {},
                'terminal_impact':r.get('terminal_impact') or {},
                'field_name':'WITHHELD',
                'live_value':'WITHHELD',
            })

        guards=[]
        for dw,domains in sorted(cfg['nonterminal_guard'].items()):
            r=by.get((api,dw))
            if not r:
                v.append(f'api{api}[{dw}]: nonterminal guard row missing')
                continue
            got=list(r.get('terminal_domains') or [])
            if got!=domains:
                v.append(f'api{api}[{dw}]: guard terminal domains {got} != {domains}')
            guards.append({
                'dword':dw,'terminal_domains':got,
                'impact_class':r.get('impact_class'),
            })

        scopes.append({
            'api_slot':api,
            'source_scope_name':cfg['source_name'],
            'scope_name_status':'SOURCE_CORRELATED_EXACT',
            'terminal_dwords':terminal,
            'nonterminal_guards':guards,
            'runtime_writer':'WITHHELD',
            'descriptor_backing_allocation':'WITHHELD',
            'live_values':'WITHHELD',
            'field_names':'WITHHELD',
        })

    # Light is an exact negative boundary for View/Frame terminal use in this corpus.
    for api,dws in ((12,(28,29,30)),(13,(6,7))):
        for dw in dws:
            r=by.get((api,dw))
            if r and 'light' in (r.get('terminal_domains') or []):
                v.append(f'api{api}[{dw}]: unexpected light terminal impact')

    out={
        'schema':'d1_tower_renderer_scope_terminal_contract/v1',
        'status':'D1_TOWER_RENDERER_SCOPE_TERMINAL_CONTRACT_EXACT' if not v else 'D1_TOWER_RENDERER_SCOPE_TERMINAL_CONTRACT_PARTIAL',
        'domains':['common','light','sky'],
        'scopes':scopes,
        'negative_boundaries':{
            'api12_28_30_light_terminal_impact':False,
            'api13_6_7_light_terminal_impact':False,
            'api12_31_terminal_impact':False,
        },
        'violations':v,
        'semantic_boundary':{
            'api12_scope_name':'SOURCE_CORRELATED_EXACT_VIEW',
            'api13_scope_name':'SOURCE_CORRELATED_EXACT_FRAME',
            'terminal_dword_impact':'EXACT_NATIVE_GCN_DATAFLOW',
            'runtime_writer':'WITHHELD',
            'descriptor_backing_allocation':'WITHHELD',
            'live_values':'WITHHELD',
            'field_level_names':'WITHHELD',
            'portable_renderer_values':'WITHHELD',
        },
        'policy':'View/Frame are promoted only as source-correlated CBuffer scope names. Individual dword field meanings, producers, descriptor memory and live retail values remain withheld. Terminal impact is corpus-specific and does not imply universal use in every shader stage.',
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({
        'status':out['status'],
        'scopes':[{
            'api_slot':x['api_slot'],'source_scope_name':x['source_scope_name'],
            'terminal_dwords':[(q['dword'],q['terminal_domains']) for q in x['terminal_dwords']]
        } for x in scopes],
        'negative_boundaries':out['negative_boundaries'],
        'violations':v,
    },indent=2))
    return 0 if out['status']=='D1_TOWER_RENDERER_SCOPE_TERMINAL_CONTRACT_EXACT' else 2

if __name__=='__main__':
    raise SystemExit(main())
