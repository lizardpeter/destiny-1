#!/usr/bin/env python3
"""Retail proof for the D1 animation-control scalar/frame-count relationship.

The control decoder intentionally leaves the float at state-record +0x14 unnamed.
This proof joins exact selector records to exact decoded clip frame counts and tests
an observed fixed relationship without assigning a gameplay meaning to the state.

For single-selection records:
    frame_count - 1 == 30 * scalar_f32
within float32 tolerance.

Multi-selection records are reported separately because one scalar can govern a
range containing clips of different lengths. The pinned native parser's glTF export
also uses fps=30, which is recorded only as an independent lineage cross-check.
"""
from __future__ import annotations
import argparse,json,math
from pathlib import Path

RATIO=30.0
TOL=1e-5
PINNED_PARSER='SolUnshadowed/tiger-animation-parser@b9fdc3a43dd28118113275624fcc9054b75855f4'
PINNED_EXPORT_FACT='animation_export/gltf_export.py uses fps=30 and times=np.arange(frames)/fps'

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--options',type=Path,required=True)
    ap.add_argument('--motion',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    o=json.loads(a.options.read_text()); m=json.loads(a.motion.read_text())
    if o.get('schema')!='d1_remote_spawned_actor_animation_options/v3': raise SystemExit('options schema')
    if m.get('schema')!='d1_animation_motion_census/v1': raise SystemExit('motion schema')
    frames={r['clip']:int(r['frame_count']) for r in m.get('rows',[])}
    single=[]; multi=[]; violations=[]
    record_count=0
    for e in o.get('entities',[]):
      for ctl in e.get('controls',[]):
        for r in (ctl.get('state_table') or {}).get('records',[]):
          record_count+=1
          selected=r.get('selected_animations') or []
          if not selected: continue
          scalar=float(r['scalar_f32'])
          rr={
            'entity':e['entity'],'control':ctl['tag_hash'],
            'record_index':int(r['record_index']),'state_hash':r['state_hash'],
            'scalar_f32':scalar,'selection_count':len(selected),'selected':[]
          }
          for j,x in enumerate(selected):
            h=x['tag_hash']; fc=frames.get(h)
            if fc is None:
              violations.append(f"{e['entity']}:{ctl['tag_hash']}:{r['record_index']}:{h}: frame count unavailable")
              continue
            expected=(fc-1)/RATIO
            err=scalar-expected
            rr['selected'].append({
              'selection_ordinal':j,'clip':h,'frame_count':fc,
              'frame_intervals':fc-1,'scalar_expected_at_ratio_30':expected,
              'scalar_minus_expected':err,'matches_ratio_30':abs(err)<=TOL,
            })
          (single if len(selected)==1 else multi).append(rr)
    bad_single=[r for r in single if not r['selected'] or not r['selected'][0]['matches_ratio_30']]
    if bad_single: violations.append(f'{len(bad_single)} single-selection records violate 30:1 relation')
    # Multi-choice rows are not required to match every alternate. Record whether
    # the first/default serialized choice matches; do not invent alternate timing semantics.
    multi_first_bad=[r for r in multi if not r['selected'] or not r['selected'][0]['matches_ratio_30']]
    if multi_first_bad: violations.append(f'{len(multi_first_bad)} multi-selection records first choice violates 30:1 relation')
    errs=[abs(r['selected'][0]['scalar_minus_expected']) for r in single if r['selected']]
    out={
      'schema':'d1_animation_state_scalar_timing_proof/v1',
      'status':'D1_ANIMATION_STATE_SCALAR_TIMING_RATIO_EXACT' if single and not violations else 'D1_ANIMATION_STATE_SCALAR_TIMING_RATIO_PARTIAL',
      'ratio_frame_intervals_per_scalar_unit':RATIO,
      'tolerance':TOL,
      'state_record_count':record_count,
      'single_selection_record_count':len(single),
      'single_selection_matching_count':len(single)-len(bad_single),
      'single_selection_max_abs_error':max(errs,default=None),
      'multi_selection_record_count':len(multi),
      'multi_selection_first_choice_matching_count':len(multi)-len(multi_first_bad),
      'single_selection_records':single,
      'multi_selection_records':multi,
      'pinned_parser_crosscheck':{'source':PINNED_PARSER,'fact':PINNED_EXPORT_FACT},
      'semantic_boundary':{
        'frame_interval_to_scalar_ratio':'EXACT_RETAIL_CORRELATION',
        'parser_export_fps_30':'PINNED_LINEAGE_CROSSCHECK',
        'scalar_field_engine_name':'WITHHELD',
        'multi_choice_alternate_timing_semantics':'WITHHELD',
      },
      'violations':violations,
      'policy':'Promote only the exact 30 frame-intervals per scalar-unit correlation. The +0x14 scalar remains engine-unnamed, and a multi-choice record is not forced to equal the duration of every alternate clip.',
    }
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ('status','ratio_frame_intervals_per_scalar_unit','state_record_count','single_selection_record_count','single_selection_matching_count','single_selection_max_abs_error','multi_selection_record_count','multi_selection_first_choice_matching_count','violations')},indent=2))
    return 0 if out['status']=='D1_ANIMATION_STATE_SCALAR_TIMING_RATIO_EXACT' else 2

if __name__=='__main__': raise SystemExit(main())
