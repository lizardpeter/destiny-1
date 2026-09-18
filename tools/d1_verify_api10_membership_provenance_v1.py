#!/usr/bin/env python3
"""Fail-closed verifier for the frozen LocalShader API10 membership producer chain."""
import argparse, hashlib, json
from pathlib import Path


def die(msg):
    raise SystemExit(f"FAIL: {msg}")


def sha256(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--manifest',type=Path,required=True)
    ap.add_argument('--usage',type=Path)
    ap.add_argument('--materials',type=Path)
    ap.add_argument('--membership',type=Path,required=True)
    a=ap.parse_args()
    m=json.loads(a.manifest.read_text())
    if m.get('schema')!='d1_localshader_api10_membership_provenance/v1' or m.get('status')!='SOURCE_CLOSED_EXACT': die('manifest identity/status')
    inputs=m.get('inputs',[])
    expected={x['name']:x['sha256'] for x in inputs}
    if len(expected)!=2 or len(inputs)!=2: die('input denominator')
    expected_ids={
      'D1_GCN_LOCALSHADER_TBUFFER_USAGE_BINDING_V1.json':10172731401,
      'D1_GCN_LOCALSHADER_API10_MATERIAL_CHAIN_V1.json':10529319011,
    }
    for x in inputs:
        if x.get('artifact_id')!=expected_ids.get(x.get('name')): die(f"artifact provenance drift: {x.get('name')}")
    for p,name in ((a.usage,'D1_GCN_LOCALSHADER_TBUFFER_USAGE_BINDING_V1.json'),(a.materials,'D1_GCN_LOCALSHADER_API10_MATERIAL_CHAIN_V1.json')):
        if p is not None and sha256(p)!=expected[name]: die(f'{name} hash drift')
    out=m.get('output',{})
    if out.get('artifact_id')!=10539900120: die('membership artifact id drift')
    if out.get('artifact_zip_sha256')!='b64ddfd28937c6d5adddf8464817da6f836fd32c1b3e20e1b51841ce3d185897': die('membership artifact zip digest drift')
    if sha256(a.membership)!=out['sha256']: die('membership byte hash drift')
    d=json.loads(a.membership.read_text())
    if d.get('schema')!='d1_gcn_localshader_api10_access_family_census/v2' or d.get('status')!='D1_GCN_LOCALSHADER_API10_ACCESS_FAMILY_CENSUS_EXACT' or d.get('violations'): die('membership status/schema')
    x=m['exact_denominators']; c=d.get('coverage',{})
    for k in ('program_count','wrapper_count','material_occurrence_count','program_instruction_histogram','material_instruction_histogram','descriptor_windows'):
        if c.get(k)!=x[k]: die(f'coverage drift: {k}')
    if len(d.get('families',[]))!=x['family_count']: die('family denominator')
    ps=d.get('programs',[])
    if len(ps)!=x['program_count'] or len({p.get('gcn_sha256') for p in ps})!=len(ps): die('program membership identity drift')
    expected_boundary={'runtime_writer':'WITHHELD','backing_allocation':'WITHHELD','engine_semantic':'WITHHELD'}
    if m.get('semantic_boundary')!=expected_boundary: die('manifest semantic boundary weakened')
    boundary=d.get('semantic_boundary',{})
    for k,v in expected_boundary.items():
        if boundary.get(k)!=v: die(f'membership semantic boundary weakened: {k}')
    print(json.dumps({'status':'D1_API10_MEMBERSHIP_PROVENANCE_EXACT','membership_sha256':sha256(a.membership),'program_count':len(ps),'family_count':len(d['families']),'semantic_boundary':expected_boundary},indent=2))

if __name__=='__main__': main()
