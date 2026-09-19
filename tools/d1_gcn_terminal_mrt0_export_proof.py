#!/usr/bin/env python3
"""Prove terminal MRT0 channel classes for exact D1 GCN pixel shaders.

AMD GCN3 EXP documentation defines COMPR=1 MRT export as packed 16-bit data:
VSRC0 carries R,G and VSRC1 carries B,A. CLRX prints those enabled packed
sources twice in its four-lane syntax (e.g. vX,vX,vY,vY).

This analyzer traces the terminal v_cvt_pkrtz_f16_f32 instructions feeding a
compressed MRT0 export and classifies each channel as exact ZERO, exact ONE, or
COMPUTED. It intentionally does not symbolically name computed values.

Primary architecture source:
https://www.amd.com/content/dam/amd/en/documents/radeon-tech-docs/instruction-set-architectures/gcn3-instruction-set-architecture.pdf
Chapter 11 EXP: COMPR=1 exports 16-bit components; EN[0] enables VSRC0 R,G and
EN[2] enables VSRC1 B,A.
"""
from __future__ import annotations
import argparse,json,re
from pathlib import Path

ADDR=re.compile(r'/\*([0-9A-Fa-f]+):[^*]*\*/\s*(.*?)\s*$')
MOV=re.compile(r'^v_mov_b32\s+(v\d+),\s*(.+)$')
PACK=re.compile(r'^v_cvt_pkrtz_f16_f32\s+(v\d+),\s*([^,]+),\s*(.+)$')
EXP=re.compile(r'^exp\s+mrt0,\s*([^,]+),\s*([^,]+),\s*([^,]+),\s*([^\s]+)(.*)$')

def classify_operand(op:str, defs:dict[str,dict]):
    op=op.strip()
    if op in ('0','0.0'): return {'class':'ZERO','source':op}
    if op in ('1.0','1'): return {'class':'ONE','source':op}
    if re.fullmatch(r'v\d+',op):
        d=defs.get(op)
        if d and d['kind']=='mov':
            val=d['value']
            if val in ('0','0.0'): return {'class':'ZERO','source':op,'definition':d}
            if val in ('1','1.0'): return {'class':'ONE','source':op,'definition':d}
        return {'class':'COMPUTED','source':op,'definition':d}
    return {'class':'COMPUTED','source':op}

def analyze(path:Path):
    defs={}; packs={}; export=None
    for ln,line in enumerate(path.read_text(errors='replace').splitlines(),1):
        m=ADDR.search(line)
        if not m: continue
        addr=m.group(1).upper(); asm=m.group(2).strip()
        mm=MOV.match(asm)
        if mm:
            defs[mm.group(1)]={'kind':'mov','value':mm.group(2).strip(),'address':addr,'line':ln,'assembly':asm}
            continue
        pm=PACK.match(asm)
        if pm:
            dst=pm.group(1); a=pm.group(2).strip(); b=pm.group(3).strip()
            row={'kind':'pack_f16x2','src_lo':a,'src_hi':b,'address':addr,'line':ln,'assembly':asm,
                 'lo':classify_operand(a,defs),'hi':classify_operand(b,defs)}
            defs[dst]=row; packs[dst]=row
            continue
        em=EXP.match(asm)
        if em and 'done' in em.group(5) and 'compr' in em.group(5):
            ops=[em.group(i).strip() for i in range(1,5)]
            export={'address':addr,'line':ln,'operands':ops,'suffix':em.group(5).strip(),'assembly':asm}
    if not export: raise ValueError('terminal compressed MRT0 export not found')
    # With CLRX compressed syntax, enabled VSRC0 appears as operands 0/1 and
    # enabled VSRC1 as 2/3. Require duplicates so the mapping is unambiguous.
    if export['operands'][0]!=export['operands'][1] or export['operands'][2]!=export['operands'][3]:
        raise ValueError(f"unexpected compressed operand duplication {export['operands']}")
    rg=defs.get(export['operands'][0]); ba=defs.get(export['operands'][2])
    if not rg or rg.get('kind')!='pack_f16x2': raise ValueError('RG source is not terminal f16x2 pack')
    if not ba or ba.get('kind')!='pack_f16x2': raise ValueError('BA source is not terminal f16x2 pack')
    channels={'R':rg['lo'],'G':rg['hi'],'B':ba['lo'],'A':ba['hi']}
    return {
      'shader':path.stem.removeprefix('PS_').removesuffix('_GFX700').upper(),
      'export':export,'rg_pack':rg,'ba_pack':ba,'channels':channels,
      'channel_classes':{k:v['class'] for k,v in channels.items()},
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--disasm',type=Path,action='append',required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    rows=[]; violations=[]
    for p in a.disasm:
        try: rows.append(analyze(p))
        except Exception as ex: violations.append(f'{p.name}:{ex}')
    out={
      'schema':'d1_gcn_terminal_mrt0_export_proof/v1',
      'status':'D1_GCN_TERMINAL_MRT0_EXPORT_EXACT' if rows and not violations else 'D1_GCN_TERMINAL_MRT0_EXPORT_PARTIAL',
      'architecture_contract':{
        'isa':'AMD GCN3',
        'compressed_mrt_vsrc0':'R,G packed f16',
        'compressed_mrt_vsrc1':'B,A packed f16',
        'source':'AMD GCN3 ISA Chapter 11 EXP',
      },
      'shader_count':len(rows),'shaders':rows,'violations':violations,
      'semantic_boundary':'Exact constant/computed channel classification only; COMPUTED channels remain unnamed.',
    }
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'status':out['status'],'shaders':[(r['shader'],r['channel_classes']) for r in rows],'violations':violations},indent=2))
    return 0 if out['status']=='D1_GCN_TERMINAL_MRT0_EXPORT_EXACT' else 2

if __name__=='__main__': raise SystemExit(main())
