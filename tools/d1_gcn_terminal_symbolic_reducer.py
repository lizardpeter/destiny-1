#!/usr/bin/env python3
"""Exact symbolic reducer for terminal D1 PS4 GCN MRT0 expressions.

The reducer interprets only a deliberately small, audited GFX700 instruction
subset. Exact image-resource provenance and ImmConstBuffer provenance are supplied
by the existing source-closed analyzers. Interpolants remain structural attr# leaves.

Unsupported operations are preserved as explicit UNSUPPORTED(...) nodes. A shader is
reported exact only when every terminal MRT0 expression is free of unsupported,
unknown, partial-interpolation, or opaque scalar-load leaves.

The output preserves native operation shape (mul/mac/mad/clamp/abs/rcp/rsq_clamp)
rather than assigning material, sky, light, or gameplay semantics.
"""
from __future__ import annotations
import argparse,hashlib,json,re,struct
from pathlib import Path

ADDR=re.compile(r'/\*([0-9A-Fa-f]+):[^*]*\*/\s*(\w+)\s+(.*)$')
VRANGE=re.compile(r'^v\[(\d+):(\d+)\]$')
SRANGE=re.compile(r'^s\[(\d+):(\d+)\]$')
CHANNELS=('R','G','B','A')
BAD_MARKERS=('UNKNOWN(','UNKNOWN_PREDICATE(','PARTIAL(','OPAQUE_SLOAD(','UNSUPPORTED(')

def norm(x): return str(x).upper().removeprefix('0X').zfill(8)
def splitops(s): return [x.strip() for x in s.split(',')]
def first(s): return s.split()[0] if s.split() else ''

def expand_v(tok):
    m=VRANGE.match(tok)
    if m:return [f'v{i}' for i in range(int(m.group(1)),int(m.group(2))+1)]
    return [tok] if re.fullmatch(r'v\d+',tok) else []

def expand_s(tok):
    m=SRANGE.match(tok)
    if m:return [f's{i}' for i in range(int(m.group(1)),int(m.group(2))+1)]
    return [tok] if re.fullmatch(r's\d+',tok) else []

def literal_hex_float(tok):
    try:return repr(struct.unpack('<f',int(tok,16).to_bytes(4,'little'))[0])
    except Exception:return tok

def source(tok,V,S):
    tok=tok.strip();neg=False;ab=False
    if tok.startswith('-abs(') and tok.endswith(')'):
        neg=True;ab=True;tok=tok[5:-1]
    elif tok.startswith('abs(') and tok.endswith(')'):
        ab=True;tok=tok[4:-1]
    elif tok.startswith('-'):
        neg=True;tok=tok[1:]
    tok=first(tok)
    if tok in V:e=V[tok]
    elif tok in S:e=S[tok]
    elif re.fullmatch(r'v\d+',tok):e=f'UNKNOWN({tok})'
    elif re.fullmatch(r's\d+',tok):e=f'UNKNOWN({tok})'
    elif tok.startswith('0x'):e=literal_hex_float(tok)
    else:e=tok
    if ab:e=f'abs({e})'
    if neg:e=f'neg({e})'
    return e

def op2(name,a,b,clamp=False,omod=None):
    e=f'{name}({a},{b})'
    if omod:e=f'mul({e},{omod})'
    if clamp:e=f'clamp({e})'
    return e

def expr_sha(e):return hashlib.sha256(e.encode()).hexdigest()

def analyze(shader,path,image_row,cbuffer_row):
    image_by={str(x.get('address')).upper():x for x in image_row.get('instructions',[]) if x.get('address')}
    cbuf_by={str(x.get('address')).upper():x for x in cbuffer_row.get('loads',[]) if x.get('address')}
    V={};S={};P={};packs={};terminal=None;unsupported=[]

    for raw in path.read_text(errors='replace').splitlines():
        m=ADDR.search(raw)
        if not m:continue
        addr,mn,rest=m.group(1).upper(),m.group(2),m.group(3).strip();ops=splitops(rest)

        if addr in cbuf_by:
            r=cbuf_by[addr]
            for reg,dw in zip(r.get('destination',[]),r.get('dword_indices',[])):
                S[f's{int(reg)}']=f'API{int(r["api_slot"])}[{int(dw)}]'
            continue

        if mn.startswith('s_load_dword'):
            for d in expand_s(first(ops[0])) if ops else []:
                S[d]=f'OPAQUE_SLOAD({addr},{d})'
            continue

        if mn=='s_mov_b32' and len(ops)>=2:
            d=first(ops[0])
            if re.fullmatch(r's\d+',d):S[d]=source(ops[1],V,S)
            continue

        if addr in image_by:
            r=image_by[addr];dests=expand_v(first(ops[0]));chs=list(r.get('dmask_channels') or '')
            tex=[int(x['texture_index']) for x in r.get('resources',[]) if x.get('texture_index') is not None]
            if len(tex)!=1:raise ValueError(f'{shader}@{addr}: non-singular image resource provenance {tex}')
            if len(dests)!=len(chs):raise ValueError(f'{shader}@{addr}: image destination/dmask mismatch {dests}/{chs}')
            for d,ch in zip(dests,chs):V[d]=f't{tex[0]}.{ch}'
            continue

        if mn=='v_interp_p1_f32':
            d=first(ops[0]);attr=next((x for x in ops if 'attr' in x),None)
            if re.fullmatch(r'v\d+',d):V[d]=f'PARTIAL({attr})'
            continue

        if mn=='v_interp_p2_f32':
            d=first(ops[0]);attr=next((x for x in ops if 'attr' in x),None)
            if re.fullmatch(r'v\d+',d):V[d]=attr or f'UNKNOWN_INTERP({addr})'
            continue

        if mn.startswith('v_cmp_') and len(ops)>=3:
            pred=first(ops[0]);a0=source(ops[1],V,S);a1=source(ops[2],V,S)
            cmpmap={
                'v_cmp_gt_f32':'gt','v_cmp_ge_f32':'ge','v_cmp_lt_f32':'lt',
                'v_cmp_le_f32':'le','v_cmp_eq_f32':'eq','v_cmp_neq_f32':'ne',
            }
            op=cmpmap.get(mn)
            if op is None:
                P[pred]=f'UNSUPPORTED({mn}@{addr})'
                unsupported.append({'address':addr,'mnemonic':mn,'assembly':raw.strip()})
            else:
                P[pred]=f'{op}({a0},{a1})'
            continue

        if mn=='v_cvt_pkrtz_f16_f32':
            d=first(ops[0]);lo=source(ops[1],V,S);hi=source(ops[2],V,S)
            packs[d]=(lo,hi);V[d]=f'pack({lo},{hi})'
            continue

        if mn=='exp' and rest.startswith('mrt0,'):
            if len(ops)<5:raise ValueError(f'{shader}@{addr}: malformed MRT0 export')
            terminal={'address':addr,'ops':[first(x) for x in ops[1:5]],'compressed':bool(re.search(r'\bcompr\b',rest))}
            continue

        if not mn.startswith('v_') or not ops:continue
        dests=expand_v(first(ops[0]))
        if not dests:continue

        clamp=(' clamp' in rest or rest.endswith('clamp'))
        omod='4.0' if ' mul:4' in rest else ('2.0' if ' mul:2' in rest else None)
        if mn in ('v_mov_b32','v_cvt_i32_f32'):
            e=source(ops[1],V,S)
            if mn=='v_cvt_i32_f32':e=f'i32({e})'
        elif mn in ('v_mul_f32','v_mul_legacy_f32'):
            e=op2('mul',source(ops[1],V,S),source(ops[2],V,S),clamp,omod)
        elif mn=='v_add_f32':
            e=op2('add',source(ops[1],V,S),source(ops[2],V,S),clamp,omod)
        elif mn=='v_sub_f32':
            e=op2('sub',source(ops[1],V,S),source(ops[2],V,S),clamp,omod)
        elif mn=='v_subrev_f32':
            e=op2('sub',source(ops[2],V,S),source(ops[1],V,S),clamp,omod)
        elif mn=='v_max_f32':
            e=op2('max',source(ops[1],V,S),source(ops[2],V,S),clamp,omod)
        elif mn=='v_min_f32':
            e=op2('min',source(ops[1],V,S),source(ops[2],V,S),clamp,omod)
        elif mn in ('v_mac_f32','v_mac_legacy_f32'):
            old=V.get(dests[0],f'UNKNOWN({dests[0]}_OLD)')
            e=f'mac({old},{source(ops[1],V,S)},{source(ops[2],V,S)})'
            if clamp:e=f'clamp({e})'
        elif mn in ('v_mad_f32','v_madak_f32'):
            e=f'mad({source(ops[1],V,S)},{source(ops[2],V,S)},{source(ops[3],V,S)})'
            if clamp:e=f'clamp({e})'
        elif mn=='v_rcp_f32':
            e=f'rcp({source(ops[1],V,S)})'
        elif mn=='v_rsq_clamp_f32':
            e=f'rsq_clamp({source(ops[1],V,S)})'
        elif mn=='v_sqrt_f32':
            e=f'sqrt({source(ops[1],V,S)})'
        elif mn=='v_exp_f32':
            e=f'exp2({source(ops[1],V,S)})'
        elif mn=='v_cndmask_b32':
            pred=first(ops[3]) if len(ops)>=4 else ''
            pe=P.get(pred,f'UNKNOWN_PREDICATE({pred})')
            e=f'select({pe},{source(ops[2],V,S)},{source(ops[1],V,S)})'
        else:
            e=f'UNSUPPORTED({mn}@{addr})'
            unsupported.append({'address':addr,'mnemonic':mn,'assembly':raw.strip()})
        for d in dests:V[d]=e

    if terminal is None:raise ValueError(f'{shader}: terminal MRT0 export missing')
    if terminal['compressed']:
        rg,ba=terminal['ops'][0],terminal['ops'][2]
        if rg not in packs:raise ValueError(f'{shader}: compressed RG pack producer missing for {rg}')
        if ba not in packs:raise ValueError(f'{shader}: compressed BA pack producer missing for {ba}')
        roots={'R':packs[rg][0],'G':packs[rg][1],'B':packs[ba][0],'A':packs[ba][1]}
    else:
        roots={ch:source(tok,V,S) for ch,tok in zip(CHANNELS,terminal['ops'])}

    unresolved={ch:[m for m in BAD_MARKERS if m in e] for ch,e in roots.items()}
    exact=(not unsupported and all(not x for x in unresolved.values()))
    return {
        'shader':shader,'terminal_mrt0_export_address':terminal['address'],
        'terminal_mrt0_compressed':terminal['compressed'],
        'terminal_expressions':roots,
        'terminal_expression_sha256':{ch:expr_sha(e) for ch,e in roots.items()},
        'terminal_unresolved_markers':unresolved,
        'unsupported_operations':unsupported,
        'exact_terminal_expression':exact,
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--usage',type=Path,required=True)
    ap.add_argument('--cbuffer-usage',type=Path,required=True)
    ap.add_argument('--disasm-dir',type=Path,required=True)
    ap.add_argument('--shader',action='append',required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    u=json.loads(a.usage.read_text());c=json.loads(a.cbuffer_usage.read_text());violations=[];rows=[]
    if u.get('status')!='D1_GCN_IMAGE_RESOURCE_USAGE_EXACT':violations.append('image usage not exact')
    if c.get('status')!='D1_GCN_CBUFFER_USAGE_EXACT':violations.append('cbuffer usage not exact')
    iby={norm(x['shader']):x for x in u.get('shaders',[])};cby={norm(x['shader']):x for x in c.get('shaders',[])}
    for raw in a.shader:
        h=norm(raw)
        try:
            if h not in iby:raise ValueError('image usage row missing')
            if h not in cby:raise ValueError('cbuffer usage row missing')
            p=a.disasm_dir/f'PS_{h}.s'
            if not p.exists():p=a.disasm_dir/f'PS_{h}_GFX700.s'
            if not p.exists():raise FileNotFoundError(p)
            r=analyze(h,p,iby[h],cby[h]);rows.append(r)
            if not r['exact_terminal_expression']:violations.append(f'{h}: terminal symbolic expression unresolved')
        except Exception as ex:violations.append(f'{h}: {ex}')
    out={
        'schema':'d1_gcn_terminal_symbolic_reducer/v1',
        'status':'D1_GCN_TERMINAL_SYMBOLIC_REDUCER_EXACT' if len(rows)==len(a.shader) and not violations else 'D1_GCN_TERMINAL_SYMBOLIC_REDUCER_PARTIAL',
        'shader_count':len(rows),'shaders':rows,'violations':violations,
        'semantic_boundary':{
            'symbolic_operations':'EXACT_NATIVE_GCN_OPERATION_SHAPE',
            'texture_leaves':'EXACT_IMAGE_RESOURCE_PROVENANCE',
            'cbuffer_leaves':'EXACT_IMMCONSTBUFFER_PROVENANCE',
            'interpolant_leaves':'EXACT_ATTR_REGISTER_IDENTITY',
            'human_semantics':'WITHHELD',
            'floating_point_reassociation':'NOT_PERFORMED',
        },
        'policy':'Expression strings preserve native operation nesting. No algebraic reassociation is performed. Exact status requires every terminal channel to avoid unsupported/unknown/partial/opaque leaves.',
    }
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'status':out['status'],'rows':[{
        'shader':x['shader'],'terminal':x['terminal_mrt0_export_address'],
        'sha256':x['terminal_expression_sha256'],
        'unresolved':x['terminal_unresolved_markers'],
        'unsupported':x['unsupported_operations'],
    } for x in rows],'violations':violations},indent=2))
    return 0 if out['status']=='D1_GCN_TERMINAL_SYMBOLIC_REDUCER_EXACT' else 2

if __name__=='__main__':raise SystemExit(main())
