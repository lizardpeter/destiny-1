#!/usr/bin/env python3
"""Test how D1 baked-static 0x40 matrices compose with packed model quantization.

Requires a validator-passing static-map report, an exact static<->s_entity_model
cross-representation report, and shipped snapshots. For exact matches this factors
D(q)=diag(model_scale)*q+model_translation out of each shipped static matrix and
tests whether the remainder is an ordinary affine similarity transform. Both raw
and transposed matrix conventions are measured; no visual fit is used.
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_tower_map_schema_validate import Corpus


def norm(s): return str(s).upper().removeprefix('0X').zfill(8)

def matrix_records(data: bytes, count: int):
    if len(data) != count*0x40:
        raise ValueError(f'transform backing {len(data)} != {count}*0x40')
    v=np.frombuffer(data,dtype='<f4').reshape(count,4,4).astype(np.float64)
    if not np.isfinite(v).all(): raise ValueError('non-finite matrix value')
    return v

def signature(match: dict):
    s=np.asarray((match.get('model_scale') or [])[:3],dtype=np.float64)
    t=np.asarray((match.get('model_translation') or [])[:3],dtype=np.float64)
    if s.shape!=(3,) or t.shape!=(3,) or np.any(np.abs(s)<1e-12): return None
    return {'model_tag_hash':norm(match['model_tag_hash']),'model_scale':s,'model_translation':t,
            'vertex_stride0':match.get('vertex_stride0'),'vertex_stride1':match.get('vertex_stride1'),
            'vertex_count':match.get('vertex_count')}

def sig_key(s):
    return (tuple(np.round(s['model_scale'],12)),tuple(np.round(s['model_translation'],12)),
            s['vertex_stride0'],s['vertex_stride1'],s['vertex_count'])

def factor_metrics(M: np.ndarray, s: np.ndarray, t: np.ndarray):
    # If M maps packed q -> world and D maps q -> ordinary model-local, M=I*D.
    D=np.eye(4,dtype=np.float64); D[:3,:3]=np.diag(s); D[:3,3]=t
    I=M @ np.linalg.inv(D)
    L=I[:3,:3]
    sv=np.linalg.svd(L,compute_uv=False)
    uniform=float(np.mean(sv))
    anis=float((np.max(sv)-np.min(sv))/max(abs(uniform),1e-15))
    R=L/uniform if abs(uniform)>1e-15 else L
    ortho=float(np.linalg.norm(R.T@R-np.eye(3),ord='fro'))
    affine=float(np.max(np.abs(I[3]-np.array([0.,0.,0.,1.]))))
    det=float(np.linalg.det(R))
    return {'factored_matrix':I.tolist(),'affine_bottom_row_residual':affine,
            'linear_singular_values':[float(x) for x in sv],'uniform_instance_scale':uniform,
            'similarity_anisotropy':anis,'normalized_orthogonality_residual':ortho,
            'normalized_determinant':det,'abs_normalized_determinant_minus_one':abs(abs(det)-1.0),
            'translation':[float(x) for x in I[:3,3]]}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--snapshot',type=Path,action='append',required=True)
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--validation-json',type=Path,required=True)
    ap.add_argument('--crosscheck-json',type=Path,required=True)
    ap.add_argument('--static-map-data',required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args(); h=norm(a.static_map_data)
    val=json.loads(a.validation_json.read_text()); cross=json.loads(a.crosscheck_json.read_text())
    parents=[x for x in val.get('static_map_data',[]) if norm(x.get('hash','0'))==h and x.get('ok')]
    if len(parents)!=1: raise SystemExit(f'{h}: expected one passing validator row, got {len(parents)}')
    d1=parents[0]['d1_validation']
    if not d1.get('ok'): raise SystemExit('D1 child not validator-passing')
    if norm(cross.get('static_map_data','0'))!=h: raise SystemExit('crosscheck static-map mismatch')

    c=Corpus([p.resolve() for p in a.snapshot],a.runtime.resolve())
    th=norm(d1['instance_transforms']); tb,tsrc=c.payload(th)
    if tb is None: raise SystemExit(f'instance transform payload {th} unavailable')
    mats=matrix_records(tb,int(d1['instance_count']))

    exact={}; conflicts=[]
    for r in cross.get('records',[]):
        if r.get('match_kind')!='EXACT_BUFFER_RANGE_PRIMITIVE_LOD': continue
        uniq={}
        for m in r.get('matches',[]):
            s=signature(m)
            if s is not None: uniq[sig_key(s)]=s
        key=(norm(r['static_table']),int(r['static_mesh_index']))
        if len(uniq)==1: exact[key]=next(iter(uniq.values()))
        elif len(uniq)>1: conflicts.append({'table':key[0],'static_mesh_index':key[1],'signatures':len(uniq)})
    if conflicts: raise SystemExit(f'crosscheck has conflicting decode signatures: {conflicts}')

    rows=[]
    for table in d1['static_tables']:
        tableh=norm(table['hash'])
        for info in table['info_entries']:
            key=(tableh,int(info['static_index'])); s=exact.get(key)
            if not s: continue
            start=int(info['transform_index']); count=int(info['instance_count'])
            for ti in range(start,start+count):
                raw=mats[ti]
                rows.append({'table':tableh,'info_index':int(info['index']),'static_mesh_index':key[1],
                    'transform_index':ti,'model_tag_hash':s['model_tag_hash'],
                    'model_scale':[float(x) for x in s['model_scale']],
                    'model_translation':[float(x) for x in s['model_translation']],
                    'vertex_stride0':s['vertex_stride0'],'vertex_stride1':s['vertex_stride1'],
                    'raw_matrix':raw.tolist(),
                    'metrics':{'raw':factor_metrics(raw,s['model_scale'],s['model_translation']),
                               'transposed':factor_metrics(raw.T,s['model_scale'],s['model_translation'])}})
    if not rows: raise SystemExit('no exact matched placement records to evaluate')

    def ag(conv):
        out={'count':len(rows)}
        for k in ('affine_bottom_row_residual','similarity_anisotropy','normalized_orthogonality_residual','abs_normalized_determinant_minus_one'):
            v=np.asarray([r['metrics'][conv][k] for r in rows],dtype=np.float64)
            out[k]={'min':float(v.min()),'median':float(np.median(v)),'p95':float(np.quantile(v,.95)),'max':float(v.max())}
        return out
    agg={'raw':ag('raw'),'transposed':ag('transposed')}
    def strong(x):
        return x['affine_bottom_row_residual']['max']<1e-5 and x['similarity_anisotropy']['max']<1e-4 and x['normalized_orthogonality_residual']['max']<5e-4
    passing=[k for k,v in agg.items() if strong(v)]
    if len(passing)==1:
        conclusion={'status':'QUANTIZATION_COMPOSITION_CONFIRMED_FOR_MATCHED_RECORDS','matrix_convention':passing[0],
                    'statement':'For every evaluated exact static/model cross-match, factoring ordinary model quantization from the shipped static matrix leaves a numerical similarity transform.'}
    elif len(passing)==0:
        conclusion={'status':'HYPOTHESIS_NOT_CONFIRMED','matrix_convention':None,
                    'statement':'Neither tested matrix convention met the strict affine/similarity residual thresholds.'}
    else:
        conclusion={'status':'ORIENTATION_AMBIGUOUS','matrix_convention':None,
                    'statement':'Both conventions met the strict thresholds; orientation needs another independent invariant.'}
    bymodel={}
    for model in sorted({r['model_tag_hash'] for r in rows}):
        rr=[r for r in rows if r['model_tag_hash']==model]
        bymodel[model]={'placement_evaluations':len(rr),'transform_indices':sorted({r['transform_index'] for r in rr})}
    rep={'evidence_status':'ALGEBRAIC_STATIC_QUANTIZATION_TEST','static_map_data':h,
         'd1_static_map_data':norm(d1['hash']),'instance_transforms':th,'instance_transform_source':tsrc,
         'exact_static_model_signatures':len(exact),'placement_evaluations':len(rows),'models':bymodel,
         'aggregate':agg,'conclusion':conclusion,'rows':rows,
         'policy':{'visual_fit':'not used','promotion_thresholds':{'affine_bottom_row_max':1e-5,'similarity_anisotropy_max':1e-4,'normalized_orthogonality_max':5e-4},
                   'scope':'A passing result proves composition only for records with independent exact s_entity_model decode signatures; unmatched static records remain unproven.'}}
    a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(rep,indent=2)+'\n')
    print(json.dumps({k:rep[k] for k in ('evidence_status','static_map_data','exact_static_model_signatures','placement_evaluations','models','aggregate','conclusion')},indent=2))
    return 0 if conclusion['status'].startswith('QUANTIZATION_COMPOSITION_CONFIRMED') else 2
if __name__=='__main__': raise SystemExit(main())
