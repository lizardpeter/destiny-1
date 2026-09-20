#!/usr/bin/env python3
"""Join frozen Tower API13 evidence to exact Crota API13 family boundary.

This is a cross-corpus structural proof only.  It establishes repeated use of
api13[6:7] as terminal RGB multipliers across independent exact PS4 shaders while
preserving the unresolved producer/live-value boundary.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

TOWER_SHADER='80CA0BE9'
CROTA_COLOR={'8108E953','8108E955','8108E956'}
CROTA_ALPHA={'8108E958','8108E959'}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--tower-checkpoint',type=Path,required=True)
    ap.add_argument('--crota-boundary',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    t=json.loads(a.tower_checkpoint.read_text())
    c=json.loads(a.crota_boundary.read_text())
    v=[]

    if t.get('schema')!='d1_ps4_api13_tower_census_checkpoint/v1':
        v.append('tower checkpoint schema drift')
    src=t.get('source') or {}
    if src.get('workflow_run_id')!=34053028846 or src.get('workflow_head_sha')!='2444074df7395d1692b1c3cba93a903f1063358c':
        v.append('tower census provenance drift')
    if src.get('artifact_digest')!='sha256:d52c83dc5a7a86fb81f5869ca62626a4d178df770b305f48fe7afc37f151a4c3':
        v.append('tower artifact digest drift')
    cen=t.get('census') or {}
    if cen.get('unique_shader_count')!=135 or cen.get('api13_shader_count')!=1 or cen.get('api13_shaders')!=[TOWER_SHADER]:
        v.append('tower census cardinality drift')
    if cen.get('api13_dword_load_histogram')!={'6':1,'7':1}:
        v.append('tower API13 dword census drift')
    peer=t.get('tower_peer_terminal_dataflow') or {}
    if peer.get('shader')!=TOWER_SHADER or peer.get('gcn_sha256')!='86282025ea6bbe21ca42153702d14fbf443b5f2d605cf96f5f15d11663170b70':
        v.append('tower peer native identity drift')
    if peer.get('producer_name_resolved') is not False or peer.get('runtime_values_resolved') is not False:
        v.append('tower unresolved boundary drift')

    if c.get('status')!='D1_CROTA_API13_FAMILY_BOUNDARY_EXACT' or c.get('violations'):
        v.append('Crota API13 boundary not exact')
    rows=c.get('rows') or []
    color={x['shader'] for x in rows if x.get('family')=='COLOR_RGB'}
    alpha={x['shader'] for x in rows if x.get('family')=='COMPUTED_ALPHA_PARTNER'}
    if color!=CROTA_COLOR:v.append(f'Crota color set drift {sorted(color)}')
    if alpha!=CROTA_ALPHA:v.append(f'Crota alpha set drift {sorted(alpha)}')
    for x in rows:
        if x.get('family')=='COLOR_RGB':
            if x.get('full_shader_api13_dwords')!=[6,7]:
                v.append(f"{x.get('shader')}: Crota API13 read-set drift")
            if any(q!=[6,7] for q in (x.get('terminal_channels_api13_dwords') or {}).values()):
                v.append(f"{x.get('shader')}: terminal RGB API13 drift")
        elif x.get('family')=='COMPUTED_ALPHA_PARTNER':
            if x.get('terminal_alpha_api13_dwords'):
                v.append(f"{x.get('shader')}: terminal alpha unexpectedly reaches API13")

    programs=[
        {'corpus':'Tower','shader':TOWER_SHADER,'terminal_relation':'RGB_SCALE','api13_dwords':[6,7],
         'evidence_class':'PINNED_EXACT_NATIVE_VALIDATOR_RESULT'},
    ] + [
        {'corpus':'Crota','shader':h,'terminal_relation':'RGB_SCALE','api13_dwords':[6,7],
         'evidence_class':'EXACT_NATIVE_DATAFLOW_SLICE'} for h in sorted(CROTA_COLOR)
    ]
    out={
        'schema':'d1_api13_cross_family_boundary/v1',
        'status':'D1_API13_CROSS_FAMILY_BOUNDARY_EXACT' if not v else 'D1_API13_CROSS_FAMILY_BOUNDARY_PARTIAL',
        'program_count':len(programs),
        'programs':programs,
        'independent_corpora':['Tower','Crota'],
        'shared_dwords':[6,7],
        'tower_census_context':{
            'unique_pixel_shader_count':cen.get('unique_shader_count'),
            'api13_consumer_count':cen.get('api13_shader_count'),
            'api13_consumers':cen.get('api13_shaders'),
        },
        'crota_partner_boundary':{
            'computed_alpha_partner_shaders':sorted(CROTA_ALPHA),
            'terminal_alpha_api13_dependency':False,
        },
        'observed_boundary':'Across one independent Tower peer and three Crota color shaders, api13[6:7] reaches terminal RGB. In the Crota paired computed-alpha shaders, API13 does not reach terminal alpha.',
        'violations':v,
        'semantic_boundary':{
            'api13_slot_and_dwords':'EXACT',
            'terminal_rgb_dependency':'EXACT_NATIVE_SHADER_DATAFLOW',
            'engine_producer_name':'WITHHELD',
            'live_ps4_values':'WITHHELD',
            'exposure_brightness_lighting_label':'WITHHELD',
        },
        'policy':'Cross-corpus repetition strengthens the terminal-RGB boundary but does not establish that API13 is universal across all shaders, nor identify its engine producer or live values.',
    }
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'status':out['status'],'programs':programs,
                      'tower_context':out['tower_census_context'],'violations':v},indent=2))
    return 0 if out['status']=='D1_API13_CROSS_FAMILY_BOUNDARY_EXACT' else 2

if __name__=='__main__':raise SystemExit(main())
