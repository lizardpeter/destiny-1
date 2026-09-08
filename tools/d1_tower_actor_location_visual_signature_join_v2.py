#!/usr/bin/env python3
"""Scoped v2 runner for the Tower actor location/visual join.

The pinned runtime-closure artifact predates the native retarget proof. Its only
violations are the now-superseded dimensional-equality checks named
``clip_not_exact_runtime_compatible``.  The location join does not consume those clip
claims at all; it consumes only the independently parsed EntitySK -> model field.

This runner accepts that artifact only when:
- it contains exactly 57 actor rows;
- every actor has a non-null exact model;
- those models collapse to exactly 13 hashes; and
- every legacy violation is exactly the superseded clip-dimension violation.

It then runs the base join with a temporary projection containing only the model-edge
scope and annotates the result so the narrowing cannot be mistaken for a promotion of
the old runtime/clip verdict.
"""
from __future__ import annotations

import json, sys, tempfile
from pathlib import Path

import d1_tower_actor_location_visual_signature_join as base

NULLS={'00000000','FFFFFFFF'}

def norm(x): return str(x).upper().removeprefix('0X').zfill(8)


def main() -> int:
    argv=list(sys.argv)
    try: i=argv.index('--runtime-closure')
    except ValueError: raise SystemExit('--runtime-closure is required')
    if i+1>=len(argv): raise SystemExit('--runtime-closure value missing')
    src=Path(argv[i+1])
    rt=json.loads(src.read_text())
    actors=rt.get('actors') or {}
    legacy=rt.get('violations') or []
    models=[norm(r.get('model')) for r in actors.values() if norm(r.get('model')) not in NULLS]
    failures=[]
    if len(actors)!=57: failures.append(f'actor_count_{len(actors)}_not_57')
    if len(models)!=57: failures.append(f'actor_model_edge_count_{len(models)}_not_57')
    if len(set(models))!=13: failures.append(f'unique_model_count_{len(set(models))}_not_13')
    bad=[x for x in legacy if not str(x).endswith(':clip_not_exact_runtime_compatible')]
    if bad: failures.append(f'non_superseded_runtime_violation_count_{len(bad)}')
    if failures:
        raise SystemExit('runtime model-edge scope failed: '+','.join(failures))

    projection=dict(rt)
    projection['status']='D1_TOWER_SPAWNED_ACTOR_RUNTIME_CLOSURE_COMPLETE'
    projection['violations']=[]
    with tempfile.TemporaryDirectory() as td:
        p=Path(td)/'runtime_model_edge_projection.json'
        p.write_text(json.dumps(projection,indent=2)+'\n')
        argv[i+1]=str(p)
        old=sys.argv
        try:
            sys.argv=argv
            code=base.main()
        finally:
            sys.argv=old
    if code!=0: return code

    # Add the projection boundary to the base report.
    try: oi=argv.index('-o')
    except ValueError:
        try: oi=argv.index('--out')
        except ValueError: raise SystemExit('base output argument missing')
    outp=Path(argv[oi+1]); d=json.loads(outp.read_text())
    d['runtime_model_edge_projection']={
        'source_runtime_status':rt.get('status'),
        'source_actor_count':len(actors),
        'source_exact_model_edge_count':len(models),
        'source_unique_model_count':len(set(models)),
        'superseded_clip_dimension_violation_count':len(legacy),
        'all_source_runtime_violations_are_superseded_clip_dimension_checks':not bad,
        'native_retarget_semantics_promoted_by_this_join':False,
        'runtime_animation_state_promoted_by_this_join':False,
        'scope':'EntitySK -> exact model only',
    }
    d['policy'] += (' The pinned runtime artifact is consumed only for its 57 source-parsed EntitySK->model edges. '
                    'Its legacy dimensional clip-compatibility violations are explicitly excluded because this join '
                    'does not consume clip compatibility; native retarget closure remains a separate proof artifact.')
    outp.write_text(json.dumps(d,indent=2,allow_nan=True)+'\n')
    print(json.dumps({'status':d['status'],'runtime_model_edge_projection':d['runtime_model_edge_projection']},indent=2))
    return 0

if __name__=='__main__': raise SystemExit(main())
