#!/usr/bin/env python3
"""Fail-closed control-flow audit for straight-line D1 GCN symbolic reduction.

The generic terminal symbolic reducer models register dataflow but does not model
lane-wise CFG/EXEC merges.  This audit therefore separates shaders whose terminal
arithmetic can be interpreted with a straight-line register model from shaders that
contain path-selecting control constructs requiring a dedicated CFG-aware proof.

Allowed here:
- ordinary scalar/vector arithmetic;
- s_mov_b64 writes involving EXEC;
- s_wqm_b64 helper-lane expansion/restoration.

Unsafe for generic straight-line promotion:
- SOPP branches (s_branch / s_cbranch_* / PC-changing branches);
- VOP compare-X instructions that update EXEC directly;
- saveexec instructions;
- direct boolean writes to EXEC that create/select complementary lane masks.

This does not claim the unsafe shaders are semantically unresolved.  It only prevents
the straight-line reducer from over-promoting them.
"""
from __future__ import annotations
import argparse,json,re
from pathlib import Path

ADDR=re.compile(r'/\*([0-9A-Fa-f]+):[^*]*\*/\s*(\w+)\s+(.*)$')
SHADER_RE=re.compile(r'PS_([0-9A-Fa-f]{8})(?:_GFX700)?\.s$')

SAVEEXEC_PREFIXES=(
    's_and_saveexec','s_or_saveexec','s_xor_saveexec','s_andn2_saveexec',
    's_orn2_saveexec','s_nand_saveexec','s_nor_saveexec','s_xnor_saveexec',
)
DIRECT_EXEC_BOOL={'s_and_b64','s_andn2_b64','s_or_b64','s_orn2_b64','s_xor_b64','s_xnor_b64'}
PC_BRANCHES={'s_branch','s_setpc_b64','s_swappc_b64'}

def norm(x):return str(x).upper().removeprefix('0X').zfill(8)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--extract-report',type=Path,required=True)
    ap.add_argument('--disasm-dir',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()

    ex=json.loads(a.extract_report.read_text());violations=[];rows=[]
    if ex.get('status')!='D1_WORLD_PIXEL_SHADER_GCN_EXACT' or ex.get('error_count'):
        violations.append('shader extract report not exact')

    expected={norm(x['shader']):int(x.get('visible_material_count',0))
              for x in ex.get('shaders',[]) if not x.get('error')}

    found={}
    for p in sorted(a.disasm_dir.glob('PS_*.s')):
        m=SHADER_RE.match(p.name)
        if not m:continue
        sh=norm(m.group(1))
        if sh not in expected:continue
        hazards=[];audit=[]
        for line in p.read_text(errors='replace').splitlines():
            mm=ADDR.search(line)
            if not mm:continue
            addr,mn,rest=mm.group(1).upper(),mm.group(2),mm.group(3)
            rec={'address':addr,'mnemonic':mn,'assembly':line.strip()}
            reason=None
            if mn.startswith('s_cbranch') or mn in PC_BRANCHES:
                reason='SCALAR_CONTROL_FLOW_BRANCH'
            elif mn.startswith('v_cmpx_'):
                reason='VECTOR_COMPARE_WRITES_EXEC'
            elif mn.startswith(SAVEEXEC_PREFIXES):
                reason='SAVEEXEC_LANE_MASK'
            elif mn in DIRECT_EXEC_BOOL and re.search(r'\bexec\b',rest):
                reason='DIRECT_EXEC_BOOLEAN_MASK'
            if reason:
                rec['reason']=reason;hazards.append(rec)
            if 'exec' in line.lower() and mn.startswith('s_'):
                audit.append(rec)
        row={
            'shader':sh,
            'visible_material_count':expected[sh],
            'straightline_symbolic_safe':not hazards,
            'path_selecting_operation_count':len(hazards),
            'path_selecting_operations':hazards,
            'exec_related_scalar_operation_count':len(audit),
            'exec_related_scalar_operations':audit,
        }
        rows.append(row);found[sh]=row

    missing=sorted(set(expected)-set(found))
    if missing:violations.append(f'disassembly missing for {missing}')
    safe=[x for x in rows if x['straightline_symbolic_safe']]
    unsafe=[x for x in rows if not x['straightline_symbolic_safe']]
    out={
        'schema':'d1_gcn_straightline_controlflow_audit/v1',
        'status':'D1_GCN_STRAIGHTLINE_CONTROLFLOW_AUDIT_EXACT' if len(rows)==len(expected) and not violations else 'D1_GCN_STRAIGHTLINE_CONTROLFLOW_AUDIT_PARTIAL',
        'shader_family_count':len(rows),
        'visible_material_count_sum':sum(x['visible_material_count'] for x in rows),
        'straightline_safe_shader_family_count':len(safe),
        'straightline_safe_visible_material_count':sum(x['visible_material_count'] for x in safe),
        'cfg_required_shader_family_count':len(unsafe),
        'cfg_required_visible_material_count':sum(x['visible_material_count'] for x in unsafe),
        'safe_rows':safe,
        'cfg_required_rows':sorted(unsafe,key=lambda x:(-x['visible_material_count'],x['shader'])),
        'violations':violations,
        'semantic_boundary':{
            'instruction_detection':'EXACT_NATIVE_DISASSEMBLY',
            'straightline_safe':'NO_PATH_SELECTING_EXEC_OR_BRANCH_OPERATION_DETECTED',
            'cfg_required':'STRUCTURAL_REQUIREMENT_NOT_SEMANTIC_FAILURE',
            'branch_predicate_meaning':'WITHHELD',
            'lane_merge_equation':'NOT_MODELED_HERE',
        },
        'policy':'A CFG-required row is excluded from generic straight-line symbolic promotion even if a register-only reducer prints a marker-free terminal expression. Dedicated control-flow proof may later close it.',
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({
        'status':out['status'],
        'safe_families':len(safe),
        'safe_material_weight':out['straightline_safe_visible_material_count'],
        'cfg_required_families':len(unsafe),
        'cfg_required_material_weight':out['cfg_required_visible_material_count'],
        'cfg_required':[{
            'shader':x['shader'],'weight':x['visible_material_count'],
            'ops':[(q['address'],q['mnemonic'],q['reason']) for q in x['path_selecting_operations']]
        } for x in out['cfg_required_rows']],
        'violations':violations,
    },indent=2))
    return 0 if out['status']=='D1_GCN_STRAIGHTLINE_CONTROLFLOW_AUDIT_EXACT' else 2

if __name__=='__main__':
    raise SystemExit(main())
