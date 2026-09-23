#!/usr/bin/env python3
"""Exact native/provenance differential for selected D1 PS4 shader pairs.

Inputs are source-closed disassembly plus exact image, ImmConstBuffer, and terminal
MRT0 provenance reports.  The tool compares structure only and deliberately does
not assign pass/material meanings.

Useful for paired source-material families: it shows whether the native programs
are identical, share a long prefix/suffix, or diverge in resources/cbuffers/output
leaves while keeping every semantic label withheld.
"""
from __future__ import annotations
import argparse,collections,json,re
from pathlib import Path

INST=re.compile(r'/\*[0-9A-Fa-f]+:[^*]*\*/\s*([A-Za-z0-9_]+)\b')
def norm(x):return str(x).upper().removeprefix('0X').zfill(8)

def parse_disasm(p:Path):
    seq=[]
    for line in p.read_text(errors='replace').splitlines():
        m=INST.search(line)
        if m:seq.append(m.group(1))
    return seq

def common_prefix(a,b):
    n=0
    for x,y in zip(a,b):
        if x!=y:break
        n+=1
    return n

def common_suffix(a,b,prefix=0):
    n=0;mx=min(len(a),len(b))-prefix
    while n<mx and a[-1-n]==b[-1-n]:n+=1
    return n

def canon_image(r):
    return [{
        'address':x.get('address'),'opcode':x.get('opcode'),
        'textures':[int(q['texture_index']) for q in (x.get('resources') or [])],
        'samplers':[int(q['sampler_index']) for q in (x.get('samplers') or [])],
        'dmask':x.get('dmask_channels'),
    } for x in r.get('instructions',[])]

def canon_cbuffer(r):
    return {str(k):[int(x) for x in v] for k,v in sorted((r.get('api_slot_read_dwords') or {}).items(),key=lambda kv:int(kv[0]))}

def canon_slice(q):
    return {
        'disabled':bool(q.get('disabled_export_lane')),
        'cbuffer_dwords':{str(k):[int(x) for x in v] for k,v in sorted((q.get('cbuffer_dwords') or {}).items(),key=lambda kv:int(kv[0]))},
        'texture_sample_channels':sorted((int(x['texture_index']),str(x['channel']),str(x.get('sample_address'))) for x in q.get('texture_sample_channels',[])),
        'interpolants':sorted(str(x) for x in q.get('interpolants',[])),
        'unknown_registers':sorted(str(x) for x in q.get('unknown_registers',[])),
        'literals':sorted(str(x) for x in q.get('literals',[])),
    }

def canon_terminal(r):
    return {
        'address':r.get('terminal_mrt0_export_address'),
        'compressed':bool(r.get('terminal_mrt0_compressed')),
        'operands':r.get('terminal_mrt0_operands'),
        'channels':{ch:canon_slice((((r.get('channels') or {}).get(ch) or {}).get('value_slice') or {})) for ch in ('R','G','B','A')},
    }

def setdiff(a,b):
    sa=set(a);sb=set(b)
    return {'a_only':sorted(sa-sb),'b_only':sorted(sb-sa),'shared':sorted(sa&sb)}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--image-usage',type=Path,required=True)
    ap.add_argument('--cbuffer-usage',type=Path,required=True)
    ap.add_argument('--terminal-mrt0',type=Path,required=True)
    ap.add_argument('--disasm-dir',type=Path,required=True)
    ap.add_argument('--pair',action='append',required=True,help='A:B')
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    iu=json.loads(a.image_usage.read_text());cb=json.loads(a.cbuffer_usage.read_text());tm=json.loads(a.terminal_mrt0.read_text())
    violations=[];rows=[]
    if iu.get('status')!='D1_GCN_IMAGE_RESOURCE_USAGE_EXACT':violations.append('image usage not exact')
    if cb.get('status')!='D1_GCN_CBUFFER_USAGE_EXACT' or cb.get('missing_usage'):violations.append('cbuffer usage not exact')
    if tm.get('status')!='D1_GCN_TERMINAL_MRT0_DEPENDENCY_CENSUS_EXACT':violations.append('terminal MRT0 not exact')
    iby={norm(x['shader']):x for x in iu.get('shaders',[])}
    cby={norm(x['shader']):x for x in cb.get('shaders',[])}
    tby={norm(x['shader']):x for x in tm.get('shaders',[])}
    for spec in a.pair:
        try:
            aa,bb=(norm(x) for x in spec.split(':',1))
            for sh in (aa,bb):
                if sh not in iby or sh not in cby or sh not in tby:raise ValueError(f'{sh}: exact provenance row missing')
            pa=a.disasm_dir/f'PS_{aa}.s';pb=a.disasm_dir/f'PS_{bb}.s'
            if not pa.exists():pa=a.disasm_dir/f'PS_{aa}_GFX700.s'
            if not pb.exists():pb=a.disasm_dir/f'PS_{bb}_GFX700.s'
            if not pa.exists() or not pb.exists():raise FileNotFoundError(f'{pa} / {pb}')
            sa=parse_disasm(pa);sb=parse_disasm(pb);pre=common_prefix(sa,sb);suf=common_suffix(sa,sb,pre)
            ha=collections.Counter(sa);hb=collections.Counter(sb)
            imagea=canon_image(iby[aa]);imageb=canon_image(iby[bb])
            cba=canon_cbuffer(cby[aa]);cbb=canon_cbuffer(cby[bb])
            ta=canon_terminal(tby[aa]);tb=canon_terminal(tby[bb])
            rows.append({
                'a':aa,'b':bb,
                'native_instruction_count':{'a':len(sa),'b':len(sb)},
                'mnemonic_sequence_identical':sa==sb,
                'common_mnemonic_prefix_count':pre,'common_mnemonic_suffix_count':suf,
                'a_excess_mnemonics':{k:ha[k]-hb[k] for k in sorted(ha) if ha[k]>hb[k]},
                'b_excess_mnemonics':{k:hb[k]-ha[k] for k in sorted(hb) if hb[k]>ha[k]},
                'image_usage':{'a':imagea,'b':imageb,'identical':imagea==imageb},
                'cbuffer_usage':{'a':cba,'b':cbb,'identical':cba==cbb},
                'terminal_mrt0':{'a':ta,'b':tb,'identical':ta==tb},
                'exact_structural_relation':(
                    'NATIVE_MNEMONIC_AND_PROVENANCE_IDENTICAL'
                    if sa==sb and imagea==imageb and cba==cbb and ta==tb
                    else 'NATIVE_OR_PROVENANCE_DIFFERENTIAL'
                ),
                'semantic_boundary':'STRUCTURAL_DIFFERENTIAL_ONLY',
            })
        except Exception as ex:
            violations.append(f'{spec}: {ex}')
    out={
        'schema':'d1_shader_pair_provenance_differential/v1',
        'status':'D1_SHADER_PAIR_PROVENANCE_DIFFERENTIAL_EXACT' if len(rows)==len(a.pair) and not violations else 'D1_SHADER_PAIR_PROVENANCE_DIFFERENTIAL_PARTIAL',
        'pair_count':len(rows),'pairs':rows,'violations':violations,
        'policy':'Exact native/provenance comparison only. Source sibling status plus structural similarity does not establish complementary pass semantics, human sky roles, or portable equation equivalence.',
    }
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'status':out['status'],'pairs':[{
        'a':x['a'],'b':x['b'],'relation':x['exact_structural_relation'],
        'instructions':x['native_instruction_count'],'prefix':x['common_mnemonic_prefix_count'],'suffix':x['common_mnemonic_suffix_count'],
        'image_same':x['image_usage']['identical'],'cbuffer_same':x['cbuffer_usage']['identical'],'terminal_same':x['terminal_mrt0']['identical'],
        'a_excess':x['a_excess_mnemonics'],'b_excess':x['b_excess_mnemonics'],
    } for x in rows],'violations':violations},indent=2))
    return 0 if out['status']=='D1_SHADER_PAIR_PROVENANCE_DIFFERENTIAL_EXACT' else 2
if __name__=='__main__':raise SystemExit(main())
