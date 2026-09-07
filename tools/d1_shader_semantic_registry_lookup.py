#!/usr/bin/env python3
"""Lookup reusable D1 native shader semantics by exact bounded GCN SHA-256.

This is deliberately fail-closed. A serialized shader TagHash, visual similarity,
or character identity is never sufficient to reuse a semantic handler.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

STATUS='D1_NATIVE_SHADER_SEMANTIC_REGISTRY_V1_EXACT'

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--registry',type=Path,default=Path('evidence/d1_native_shader_semantic_registry_v1.json'))
    ap.add_argument('--gcn-sha256',required=True)
    ap.add_argument('--stage',required=True,choices=('vs','ps'))
    ap.add_argument('--out',type=Path)
    a=ap.parse_args()
    d=json.loads(a.registry.read_text())
    violations=[]
    if d.get('status')!=STATUS: violations.append(f"registry status {d.get('status')!r} != {STATUS!r}")
    if d.get('registry_key')!='bounded_native_gcn_sha256': violations.append('unsupported registry key')
    if d.get('violations'): violations.append('registry has violations')
    rows=d.get('entries') or []
    if len(rows)!=d.get('entry_count'): violations.append('entry_count mismatch')
    keys=[(r.get('stage'),r.get('gcn_sha256')) for r in rows]
    if len(keys)!=len(set(keys)): violations.append('duplicate stage+GCN key')
    key=(a.stage,a.gcn_sha256.lower())
    matches=[r for r in rows if (r.get('stage'),str(r.get('gcn_sha256','')).lower())==key]
    if violations:
        out={'schema_version':1,'status':'D1_SHADER_SEMANTIC_REGISTRY_LOOKUP_INVALID','match':None,'violations':violations};rc=2
    elif len(matches)==1:
        out={'schema_version':1,'status':'D1_SHADER_SEMANTIC_REGISTRY_EXACT_MATCH','match':matches[0],
             'reuse_policy':d['reuse_contract'],'violations':[]};rc=0
    elif not matches:
        out={'schema_version':1,'status':'D1_SHADER_SEMANTIC_REGISTRY_NO_EXACT_MATCH','match':None,
             'requested':{'stage':a.stage,'gcn_sha256':a.gcn_sha256.lower()},
             'policy':'Do not reuse a semantic handler. Reverse and validate this exact bounded native GCN program first.',
             'violations':[]};rc=3
    else:
        out={'schema_version':1,'status':'D1_SHADER_SEMANTIC_REGISTRY_AMBIGUOUS','match':None,'violations':['multiple exact matches']};rc=2
    text=json.dumps(out,indent=2)+'\n'
    if a.out:
        a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(text)
    print(text,end='')
    return rc
if __name__=='__main__': raise SystemExit(main())
