#!/usr/bin/env python3
"""Promote only source-closed structural forms from a failed candidate replay.

The raw candidate replay is intentionally left unchanged and fail-closed. This gate
recomputes every program from its emitted Structural IR, keeps parse accounting separate
from architecture admission, and admits only exact forms present in a separately frozen
GFX7 structural extension backed by an authoritative ISA source.
"""
from __future__ import annotations
import argparse, collections, hashlib, json, sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import d1_gcn_structural_candidate_compare_v1 as raw
import d1_gcn_shader_corpus_structural_census as core

EXT_SCHEMA="d1_gcn_source_closed_structural_extension/v1"
EXT_STATUS="D1_GCN_SOURCE_CLOSED_STRUCTURAL_EXTENSION_EXACT"
SCHEMA="d1_gcn_source_closed_structural_promotion/v1"
STATUS="D1_GCN_SOURCE_CLOSED_STRUCTURAL_PROMOTION_EXACT"


def sha256_file(p:Path)->str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()


def form_key(row:dict)->tuple:
    return raw.baseline_form_key(row)


def load_extension(p:Path):
    d=json.loads(p.read_text())
    if d.get('schema')!=EXT_SCHEMA or d.get('status')!=EXT_STATUS or d.get('violations'):
        raise SystemExit('zero-violation source-closed structural extension required')
    b=d.get('semantic_boundary') or {}
    if b.get('scope')!='GFX7_STRUCTURAL_ARCHITECTURE_ONLY' or b.get('localshader_specific_decoder') is not False:
        raise SystemExit('invalid structural extension boundary')
    if int(b.get('shader_expression_semantics_promoted',-1))!=0:
        raise SystemExit('semantic promotion is forbidden in structural extension')
    forms={}
    for i,x in enumerate(d.get('approved_forms') or []):
        k=form_key(x.get('form') or {})
        if k in forms: raise SystemExit(f'duplicate extension form:{i}')
        if not x.get('source_closed_reason'): raise SystemExit(f'missing source closure reason:{i}')
        forms[k]=x
    if not forms: raise SystemExit('empty structural extension')
    return d,forms


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--raw-replay',type=Path,required=True)
    ap.add_argument('--baseline-census',type=Path,required=True)
    ap.add_argument('--source-closed-extension',type=Path,required=True)
    ap.add_argument('--ir-dir',type=Path,required=True)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()

    r=json.loads(a.raw_replay.read_text())
    if r.get('schema')!=raw.SCHEMA:
        raise SystemExit(f'unsupported raw replay schema:{r.get("schema")!r}')
    base=json.loads(a.baseline_census.read_text())
    if base.get('schema')!=raw.BASELINE_SCHEMA or base.get('status')!=raw.BASELINE_STATUS or base.get('violations'):
        raise SystemExit('exact baseline structural census required')
    ext,ext_rows=load_extension(a.source_closed_extension)
    bc=base.get('census') or {}
    base_ops={str(x['opcode']) for x in bc.get('opcodes') or []}
    base_forms={form_key(x) for x in bc.get('structural_forms') or []}
    base_widths={int(x['bytes']) for x in bc.get('encoding_widths') or []}
    base_rules={str(x['rule']) for x in bc.get('classification_rules') or []}
    base_cfg={raw.baseline_cfg_key(x) for x in bc.get('cfg_forms') or []}
    ext_forms=set(ext_rows); ext_ops={x[0] for x in ext_forms}; ext_widths={x[1] for x in ext_forms}; ext_rules={x[6] for x in ext_forms}
    admitted_ops=base_ops|ext_ops; admitted_forms=base_forms|ext_forms
    admitted_widths=base_widths|ext_widths; admitted_rules=base_rules|ext_rules

    violations=[]; rows=[]; parse_exact=0; admitted_exact=0; ins_total=0; byte_total=0
    all_ops=collections.Counter(); all_forms=collections.Counter(); all_widths=collections.Counter(); all_rules=collections.Counter(); all_cfg=collections.Counter(); ext_use=collections.Counter()
    allowed_raw_prefixes=('unsupported_opcodes:','unsupported_structural_forms:','unsupported_encoding_widths:','unsupported_classification_rules:')
    for rec in r.get('programs') or []:
        sha=str(rec.get('gcn_sha256','')).lower(); code_bytes=int(rec.get('gcn_bytes',0))
        row={'gcn_sha256':sha,'gcn_bytes':code_bytes,'parse_violations':[],'architecture_violations':[]}
        if any(not str(x).startswith(allowed_raw_prefixes) for x in (rec.get('violations') or [])):
            row['parse_violations'].append(f'raw_replay_nonarchitecture_violation:{rec.get("violations")}')
        c=rec.get('clrx') or {}; s=rec.get('structural_ir') or {}
        if c.get('returncode')!=0 or c.get('stderr_bytes')!=0 or c.get('contains_s_endpgm') is not True:
            row['parse_violations'].append(f'raw_clrx_not_exact:{c}')
        if s.get('returncode')!=0:
            row['parse_violations'].append(f'raw_structural_ir_not_exact:{s.get("returncode")}')
        ip=a.ir_dir/f'{sha}.json'
        if not ip.is_file(): row['parse_violations'].append('structural_ir_missing')
        if not row['parse_violations']:
            ir=json.loads(ip.read_text())
            row['parse_violations']+=raw.validate_accounting(ir,code_bytes)
            row['parse_violations']+=raw.validate_cfg(ir)
        if row['parse_violations']:
            violations += [f'{sha}:parse:{x}' for x in row['parse_violations']]; rows.append(row); continue

        parse_exact+=1; byte_total+=code_bytes
        ins=ir.get('instructions') or []; ins_total+=len(ins)
        ops=collections.Counter(str(x['opcode']) for x in ins)
        forms=collections.Counter(core.form_key(x) for x in ins)
        widths=collections.Counter(len(str(x['encoding_hex']))//2 for x in ins)
        rules=collections.Counter(core.classification_rule(x) for x in ins)
        cfg=raw.cfg_signature(ir)
        all_ops.update(ops); all_forms.update(forms); all_widths.update(widths); all_rules.update(rules); all_cfg[cfg]+=1
        for k,n in forms.items():
            if k in ext_forms: ext_use[k]+=n
        bad_ops=sorted(set(ops)-admitted_ops); bad_forms=sorted(set(forms)-admitted_forms,key=str)
        bad_widths=sorted(set(widths)-admitted_widths); bad_rules=sorted(set(rules)-admitted_rules)
        if bad_ops: row['architecture_violations'].append(f'unsupported_opcodes:{bad_ops}')
        if bad_forms: row['architecture_violations'].append(f'unsupported_structural_forms:{len(bad_forms)}')
        if bad_widths: row['architecture_violations'].append(f'unsupported_encoding_widths:{bad_widths}')
        if bad_rules: row['architecture_violations'].append(f'unsupported_classification_rules:{bad_rules}')
        row['source_closed_forms_used']=[core.form_payload(x) for x in sorted(set(forms)&ext_forms,key=str)]
        row['cfg_signature_novel_vs_baseline']=cfg not in base_cfg
        if row['architecture_violations']:
            violations += [f'{sha}:architecture:{x}' for x in row['architecture_violations']]
        else: admitted_exact+=1
        rows.append(row)

    for k,x in ext_rows.items():
        want=int(x.get('observed_instruction_count',-1)); got=int(ext_use.get(k,0))
        if got!=want: violations.append(f'extension_observed_count:{core.form_payload(k)}:{got}!={want}')

    base_new_ops=sorted(set(all_ops)-base_ops); base_new_forms=sorted(set(all_forms)-base_forms,key=str)
    bad_ops=sorted(set(all_ops)-admitted_ops); bad_forms=sorted(set(all_forms)-admitted_forms,key=str)
    bad_widths=sorted(set(all_widths)-admitted_widths); bad_rules=sorted(set(all_rules)-admitted_rules)
    if set(base_new_forms)-ext_forms: violations.append('aggregate_baseline_frontier_not_fully_source_closed')
    if set(base_new_ops)-ext_ops: violations.append('aggregate_new_opcode_not_source_closed')
    planned=len(r.get('programs') or [])
    out={
      'schema':SCHEMA,
      'status':STATUS if not violations and parse_exact==planned and admitted_exact==planned else 'D1_GCN_SOURCE_CLOSED_STRUCTURAL_PROMOTION_WITH_VIOLATIONS',
      'inputs':{
        'raw_replay':str(a.raw_replay),'raw_replay_sha256':sha256_file(a.raw_replay),
        'baseline_census':str(a.baseline_census),'baseline_census_sha256':sha256_file(a.baseline_census),
        'source_closed_extension':str(a.source_closed_extension),'source_closed_extension_sha256':sha256_file(a.source_closed_extension),
      },
      'coverage':{
        'planned_unique_gcn_programs':planned,'exact_parse_accounted_unique_gcn_programs':parse_exact,
        'architecture_admitted_unique_gcn_programs':admitted_exact,'instruction_count':ins_total,'encoded_bytes':byte_total,
        'candidate_opcode_count':len(all_ops),'candidate_structural_form_count':len(all_forms),
      },
      'architecture':{
        'frozen_baseline_opcode_count':len(base_ops),'frozen_baseline_structural_form_count':len(base_forms),
        'source_closed_extension_form_count':len(ext_forms),'source_closed_extension_opcodes':sorted(ext_ops),
        'combined_admitted_opcode_count':len(admitted_ops),'combined_admitted_structural_form_count':len(admitted_forms),
        'candidate_novel_vs_baseline_opcodes':base_new_ops,
        'candidate_novel_vs_baseline_structural_forms':[core.form_payload(x) for x in base_new_forms],
        'source_closed_extension_usage':[{'form':core.form_payload(k),'instruction_count':int(ext_use.get(k,0))} for k in sorted(ext_forms,key=str)],
        'unapproved_opcodes':bad_ops,'unapproved_structural_forms':[core.form_payload(x) for x in bad_forms],
        'unapproved_encoding_widths':bad_widths,'unapproved_classification_rules':bad_rules,
        'candidate_cfg_signature_count':len(all_cfg),'novel_cfg_signature_combination_count':len(set(all_cfg)-base_cfg),
      },
      'programs':rows,'violations':violations,
      'semantic_boundary':{
        'gfx7_parser_changed':False,'localshader_specific_decoder':False,
        'promoted_scope':'STRUCTURAL_OPCODE_AND_OPERAND_FORM_ONLY','shader_expression_semantics_promoted':0,
        'tessellation_pipeline_ownership_promoted':0,'lds_layout_semantics_promoted':0,
      },
      'policy':'The raw replay remains fail-closed. This gate admits only exact normalized structural forms independently proven by the authoritative GFX7 ISA extension. Parse accounting, CFG validity and exact byte coverage are rechecked from every emitted IR. No LocalShader-specific decoder or higher-level shader semantics are introduced.'
    }
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(out,indent=2)+'\n')
    print('STATUS',out['status'],'PARSE',f'{parse_exact}/{planned}','ADMITTED',f'{admitted_exact}/{planned}','INSTRUCTIONS',ins_total,'BYTES',byte_total,'NEW_OPCODES',base_new_ops,'NEW_FORMS',len(base_new_forms),'VIOLATIONS',len(violations))
    for x in violations[:100]: print('VIOLATION',x)
    return 0 if out['status']==STATUS else 2

if __name__=='__main__': raise SystemExit(main())
