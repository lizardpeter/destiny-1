#!/usr/bin/env python3
"""Exact differential census for paired D1 PS4 GCN pixel shaders.

This tool is intentionally semantic-neutral.  It compares frozen CLRX disassembly
and the exact resource-provenance output from d1_gcn_image_usage_analyze.py.

Useful facts promoted here:
* which exact t# resources each member consumes;
* exact image opcode/dmask differences;
* exact MRT export lane shape (live operand versus 'off');
* instruction-family and mnemonic histograms;
* shared/divergent native instruction structure.

It does not rename a pair as colour/attenuation, albedo/mask, etc.  Such semantic
labels require independent source or complete output-dataflow evidence.
"""
from __future__ import annotations
import argparse, collections, hashlib, json, re
from pathlib import Path

SHADER_RE=re.compile(r'PS_([0-9A-Fa-f]{8})(?:_GFX700)?\\.s
INST_RE=re.compile(r'/\*[0-9A-Fa-f]+:[^*]*\*/\s*([A-Za-z0-9_]+)\b')
EXP_RE=re.compile(r'\bexp\s+(mrt\d+|pos\d+|param\d+)\s+(.+)$')
ADDR_RE=re.compile(r'/\*([0-9A-Fa-f]+):')

def norm(x): return str(x).upper().removeprefix('0X').zfill(8)

def family(m):
    if m.startswith('image_'): return 'image'
    if m.startswith(('tbuffer_','buffer_')): return 'buffer'
    if m.startswith('s_load_'): return 'scalar_load'
    if m.startswith('s_buffer_'): return 'scalar_buffer'
    if m.startswith('s_') and ('branch' in m or m in {'s_cbranch_scc0','s_cbranch_scc1','s_branch'}): return 'branch'
    if m.startswith('s_'): return 'scalar_alu'
    if m.startswith('v_'): return 'vector_alu'
    if m == 'exp': return 'export'
    return 'other'

def parse_disasm(path:Path):
    rows=[]; exports=[]
    for ln,line in enumerate(path.read_text(errors='replace').splitlines(),1):
        m=INST_RE.search(line)
        if not m: continue
        mnemonic=m.group(1)
        a=ADDR_RE.search(line)
        rec={'line':ln,'address':a.group(1).upper() if a else None,'mnemonic':mnemonic,'family':family(mnemonic),'assembly':line.strip()}
        rows.append(rec)
        em=EXP_RE.search(line)
        if em:
            # CLRX prints four comma-separated export lanes; modifiers follow.
            tail=em.group(2).strip()
            raw_operands=[x.strip() for x in tail.split(',')[:4]]
            operands=[x.split()[0] if x.split() else '' for x in raw_operands]
            if len(operands) != 4:
                raise ValueError(f'{path.name}:{ln}: malformed export operands {raw_operands!r}')
            exports.append({
                'line':ln,'address':rec['address'],'target':em.group(1),
                'operands':operands,
                'raw_operands':raw_operands,
                'live_lanes':[i for i,x in enumerate(operands) if x.lower()!='off'],
                'compressed':bool(re.search(r'\bcompr\b',tail)),
                'done':bool(re.search(r'\bdone\b',tail)),
                'valid_mask':bool(re.search(r'\bvm\b',tail)),
                'assembly':line.strip(),
            })
    mn=collections.Counter(x['mnemonic'] for x in rows)
    fam=collections.Counter(x['family'] for x in rows)
    seq='\n'.join(x['mnemonic'] for x in rows).encode()
    return {
        'instruction_count':len(rows),
        'mnemonic_histogram':dict(sorted(mn.items())),
        'family_histogram':dict(sorted(fam.items())),
        'mnemonic_sequence_sha256':hashlib.sha256(seq).hexdigest(),
        'exports':exports,
        'instructions':rows,
    }

def usage_row(by,h):
    r=by.get(h)
    if r is None: raise ValueError(f'{h}: missing exact image-usage row')
    if int(r.get('unmatched_image_instruction_count',-1)) != 0:
        raise ValueError(f'{h}: unresolved image resource provenance')
    inst=r.get('instructions',[])
    signatures=[]
    for x in inst:
        resources=x.get('resources') or []
        samplers=x.get('samplers') or []
        signatures.append({
            'address':x.get('address'),
            'opcode':x.get('opcode'),
            'texture_indices':[int(y['texture_index']) for y in resources if y.get('texture_index') is not None],
            'sampler_indices':[int(y['sampler_index']) for y in samplers if y.get('sampler_index') is not None],
            'dmask':int(x.get('dmask',0)),
            'dmask_channels':x.get('dmask_channels'),
            'assembly':x.get('assembly'),
        })
    return {
        'image_instruction_count':int(r.get('image_instruction_count',0)),
        'used_texture_indices':[int(x) for x in r.get('used_texture_indices',[])],
        'texture_instruction_counts':r.get('texture_instruction_counts',{}),
        'sampler_instruction_counts':r.get('sampler_instruction_counts',{}),
        'image_opcodes':r.get('image_opcodes',{}),
        'image_instruction_signatures':signatures,
        'instructions':inst,
    }

def pair_row(a,b,ua,ub,da,db):
    ma=collections.Counter(da['mnemonic_histogram']); mb=collections.Counter(db['mnemonic_histogram'])
    shared={k:min(ma[k],mb[k]) for k in sorted(set(ma)|set(mb)) if min(ma[k],mb[k])}
    only_a={k:ma[k]-mb[k] for k in sorted(ma) if ma[k]>mb[k]}
    only_b={k:mb[k]-ma[k] for k in sorted(mb) if mb[k]>ma[k]}
    ta=set(ua['used_texture_indices']); tb=set(ub['used_texture_indices'])
    return {
        'a':a,'b':b,
        'resource_usage':{
            'a':ua,'b':ub,
            'shared_texture_indices':sorted(ta&tb),
            'a_only_texture_indices':sorted(ta-tb),
            'b_only_texture_indices':sorted(tb-ta),
        },
        'native_structure':{
            'a':{k:da[k] for k in ('instruction_count','mnemonic_histogram','family_histogram','mnemonic_sequence_sha256','exports')},
            'b':{k:db[k] for k in ('instruction_count','mnemonic_histogram','family_histogram','mnemonic_sequence_sha256','exports')},
            'shared_mnemonic_multiset':shared,
            'a_excess_mnemonics':only_a,
            'b_excess_mnemonics':only_b,
        },
        'semantic_boundary':'STRUCTURAL_DIFFERENTIAL_ONLY',
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--usage',type=Path,required=True)
    ap.add_argument('--disasm-dir',type=Path,required=True)
    ap.add_argument('--pair',action='append',required=True,help='A:B shader hashes')
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    u=json.loads(a.usage.read_text())
    if u.get('status')!='D1_GCN_IMAGE_RESOURCE_USAGE_EXACT':
        raise SystemExit('image usage input is not exact')
    by={norm(x['shader']):x for x in u.get('shaders',[])}
    dis={}
    for p in a.disasm_dir.glob('PS_*.s'):
        m=SHADER_RE.match(p.name)
        if m: dis[norm(m.group(1))]=parse_disasm(p)
    pairs=[]; violations=[]
    for spec in a.pair:
        try:
            x,y=(norm(z) for z in spec.split(':',1))
            if x not in dis or y not in dis: raise ValueError(f'{x}:{y}: disassembly missing')
            pairs.append(pair_row(x,y,usage_row(by,x),usage_row(by,y),dis[x],dis[y]))
        except Exception as ex:
            violations.append(f'{spec}:{ex}')
    out={
        'schema':'d1_gcn_paired_shader_differential/v1',
        'status':'D1_GCN_PAIRED_SHADER_DIFFERENTIAL_EXACT' if not violations else 'D1_GCN_PAIRED_SHADER_DIFFERENTIAL_PARTIAL',
        'pair_count':len(pairs),'pairs':pairs,'violations':violations,
        'policy':'Exact GCN structural/resource differential only. Export lane shape is syntax, not an engine material semantic. Pair roles remain unnamed unless separately proven.',
    }
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'status':out['status'],'pairs':[(x['a'],x['b'],x['resource_usage']['shared_texture_indices'],x['native_structure']['a']['exports'],x['native_structure']['b']['exports']) for x in pairs],'violations':violations},indent=2))
    return 0 if not violations else 2

if __name__=='__main__': raise SystemExit(main())
)
INST_RE=re.compile(r'/\*[0-9A-Fa-f]+:[^*]*\*/\s*([A-Za-z0-9_]+)\b')
EXP_RE=re.compile(r'\bexp\s+(mrt\d+|pos\d+|param\d+)\s+(.+)$')
ADDR_RE=re.compile(r'/\*([0-9A-Fa-f]+):')

def norm(x): return str(x).upper().removeprefix('0X').zfill(8)

def family(m):
    if m.startswith('image_'): return 'image'
    if m.startswith(('tbuffer_','buffer_')): return 'buffer'
    if m.startswith('s_load_'): return 'scalar_load'
    if m.startswith('s_buffer_'): return 'scalar_buffer'
    if m.startswith('s_') and ('branch' in m or m in {'s_cbranch_scc0','s_cbranch_scc1','s_branch'}): return 'branch'
    if m.startswith('s_'): return 'scalar_alu'
    if m.startswith('v_'): return 'vector_alu'
    if m == 'exp': return 'export'
    return 'other'

def parse_disasm(path:Path):
    rows=[]; exports=[]
    for ln,line in enumerate(path.read_text(errors='replace').splitlines(),1):
        m=INST_RE.search(line)
        if not m: continue
        mnemonic=m.group(1)
        a=ADDR_RE.search(line)
        rec={'line':ln,'address':a.group(1).upper() if a else None,'mnemonic':mnemonic,'family':family(mnemonic),'assembly':line.strip()}
        rows.append(rec)
        em=EXP_RE.search(line)
        if em:
            # CLRX prints four comma-separated export lanes; modifiers follow.
            tail=em.group(2).strip()
            raw_operands=[x.strip() for x in tail.split(',')[:4]]
            operands=[x.split()[0] if x.split() else '' for x in raw_operands]
            if len(operands) != 4:
                raise ValueError(f'{path.name}:{ln}: malformed export operands {raw_operands!r}')
            exports.append({
                'line':ln,'address':rec['address'],'target':em.group(1),
                'operands':operands,
                'raw_operands':raw_operands,
                'live_lanes':[i for i,x in enumerate(operands) if x.lower()!='off'],
                'compressed':bool(re.search(r'\bcompr\b',tail)),
                'done':bool(re.search(r'\bdone\b',tail)),
                'valid_mask':bool(re.search(r'\bvm\b',tail)),
                'assembly':line.strip(),
            })
    mn=collections.Counter(x['mnemonic'] for x in rows)
    fam=collections.Counter(x['family'] for x in rows)
    seq='\n'.join(x['mnemonic'] for x in rows).encode()
    return {
        'instruction_count':len(rows),
        'mnemonic_histogram':dict(sorted(mn.items())),
        'family_histogram':dict(sorted(fam.items())),
        'mnemonic_sequence_sha256':hashlib.sha256(seq).hexdigest(),
        'exports':exports,
        'instructions':rows,
    }

def usage_row(by,h):
    r=by.get(h)
    if r is None: raise ValueError(f'{h}: missing exact image-usage row')
    if int(r.get('unmatched_image_instruction_count',-1)) != 0:
        raise ValueError(f'{h}: unresolved image resource provenance')
    inst=r.get('instructions',[])
    signatures=[]
    for x in inst:
        resources=x.get('resources') or []
        samplers=x.get('samplers') or []
        signatures.append({
            'address':x.get('address'),
            'opcode':x.get('opcode'),
            'texture_indices':[int(y['texture_index']) for y in resources if y.get('texture_index') is not None],
            'sampler_indices':[int(y['sampler_index']) for y in samplers if y.get('sampler_index') is not None],
            'dmask':int(x.get('dmask',0)),
            'dmask_channels':x.get('dmask_channels'),
            'assembly':x.get('assembly'),
        })
    return {
        'image_instruction_count':int(r.get('image_instruction_count',0)),
        'used_texture_indices':[int(x) for x in r.get('used_texture_indices',[])],
        'texture_instruction_counts':r.get('texture_instruction_counts',{}),
        'sampler_instruction_counts':r.get('sampler_instruction_counts',{}),
        'image_opcodes':r.get('image_opcodes',{}),
        'image_instruction_signatures':signatures,
        'instructions':inst,
    }

def pair_row(a,b,ua,ub,da,db):
    ma=collections.Counter(da['mnemonic_histogram']); mb=collections.Counter(db['mnemonic_histogram'])
    shared={k:min(ma[k],mb[k]) for k in sorted(set(ma)|set(mb)) if min(ma[k],mb[k])}
    only_a={k:ma[k]-mb[k] for k in sorted(ma) if ma[k]>mb[k]}
    only_b={k:mb[k]-ma[k] for k in sorted(mb) if mb[k]>ma[k]}
    ta=set(ua['used_texture_indices']); tb=set(ub['used_texture_indices'])
    return {
        'a':a,'b':b,
        'resource_usage':{
            'a':ua,'b':ub,
            'shared_texture_indices':sorted(ta&tb),
            'a_only_texture_indices':sorted(ta-tb),
            'b_only_texture_indices':sorted(tb-ta),
        },
        'native_structure':{
            'a':{k:da[k] for k in ('instruction_count','mnemonic_histogram','family_histogram','mnemonic_sequence_sha256','exports')},
            'b':{k:db[k] for k in ('instruction_count','mnemonic_histogram','family_histogram','mnemonic_sequence_sha256','exports')},
            'shared_mnemonic_multiset':shared,
            'a_excess_mnemonics':only_a,
            'b_excess_mnemonics':only_b,
        },
        'semantic_boundary':'STRUCTURAL_DIFFERENTIAL_ONLY',
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--usage',type=Path,required=True)
    ap.add_argument('--disasm-dir',type=Path,required=True)
    ap.add_argument('--pair',action='append',required=True,help='A:B shader hashes')
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    u=json.loads(a.usage.read_text())
    if u.get('status')!='D1_GCN_IMAGE_RESOURCE_USAGE_EXACT':
        raise SystemExit('image usage input is not exact')
    by={norm(x['shader']):x for x in u.get('shaders',[])}
    dis={}
    for p in a.disasm_dir.glob('PS_*.s'):
        m=SHADER_RE.match(p.name)
        if m: dis[norm(m.group(1))]=parse_disasm(p)
    pairs=[]; violations=[]
    for spec in a.pair:
        try:
            x,y=(norm(z) for z in spec.split(':',1))
            if x not in dis or y not in dis: raise ValueError(f'{x}:{y}: disassembly missing')
            pairs.append(pair_row(x,y,usage_row(by,x),usage_row(by,y),dis[x],dis[y]))
        except Exception as ex:
            violations.append(f'{spec}:{ex}')
    out={
        'schema':'d1_gcn_paired_shader_differential/v1',
        'status':'D1_GCN_PAIRED_SHADER_DIFFERENTIAL_EXACT' if not violations else 'D1_GCN_PAIRED_SHADER_DIFFERENTIAL_PARTIAL',
        'pair_count':len(pairs),'pairs':pairs,'violations':violations,
        'policy':'Exact GCN structural/resource differential only. Export lane shape is syntax, not an engine material semantic. Pair roles remain unnamed unless separately proven.',
    }
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'status':out['status'],'pairs':[(x['a'],x['b'],x['resource_usage']['shared_texture_indices'],x['native_structure']['a']['exports'],x['native_structure']['b']['exports']) for x in pairs],'violations':violations},indent=2))
    return 0 if not violations else 2

if __name__=='__main__': raise SystemExit(main())
