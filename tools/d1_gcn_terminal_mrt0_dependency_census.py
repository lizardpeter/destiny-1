#!/usr/bin/env python3
"""Generic exact terminal MRT0 dependency census for D1 PS4 GCN pixel shaders.

Supports both ordinary four-lane MRT0 exports and compressed half-packed MRT0 exports.
The dataflow graph joins:
* exact native image resource provenance;
* exact ImmConstBuffer provenance;
* interpolant and native vector/scalar arithmetic.

For compressed exports, v_cvt_pkrtz_f16_f32 producers are resolved so R/G/B/A are
sliced from their pre-pack float roots. For ordinary exports, the four export operands
are sliced directly from the register state at the terminal MRT0 export.

This tool is semantic-neutral: it reports exact leaves and arithmetic lineage but does
not call them albedo, lighting, roughness, emissive, etc.
"""
from __future__ import annotations
import argparse,json,re
from pathlib import Path

ADDR=re.compile(r'/\*([0-9A-Fa-f]+):[^*]*\*/\s*(\w+)\s+(.*)$')
REG=re.compile(r'\b([vs]\d+)\b')
VRANGE=re.compile(r'^v\[(\d+):(\d+)\]$')
CHANNELS=('R','G','B','A')
SPECIAL_REGS={'vcc','scc','exec'}

def norm(x):return str(x).upper().removeprefix('0X').zfill(8)
def splitops(rest):return [x.strip() for x in rest.split(',')]
def firsttok(s):return s.split()[0] if s.split() else ''
def expand_v(tok):
    m=VRANGE.match(tok)
    if m:return [f'v{i}' for i in range(int(m.group(1)),int(m.group(2))+1)]
    return [tok] if re.fullmatch(r'v\d+',tok) else []

class Graph:
    def __init__(self):
        self.nodes={};self.current={};self.implicit={};self.next_id=0;self.pack_roots={}
    def node(self,kind,**kw):
        i=self.next_id;self.next_id+=1;self.nodes[i]={'id':i,'kind':kind,**kw};return i
    def src(self,tok):
        tok=firsttok(tok)
        if tok.lower()=='off':return self.node('disabled_export_lane',value='off')
        if re.fullmatch(r'[vs]\d+',tok) or tok in SPECIAL_REGS:
            if tok in self.current:return self.current[tok]
            if tok not in self.implicit:self.implicit[tok]=self.node('unknown_register',register=tok)
            return self.implicit[tok]
        return self.node('literal',value=tok)
    def define(self,reg,kind,sources=None,**kw):
        i=self.node(kind,register=reg,sources=list(sources or []),**kw);self.current[reg]=i;return i

def summary(g,root,stop_at_texture=True):
    reach=set();stack=[root]
    while stack:
        x=stack.pop()
        if x in reach:continue
        reach.add(x);n=g.nodes[x]
        if stop_at_texture and n['kind']=='texture_sample':continue
        stack.extend(n.get('sources',[]))
    cbuf={};tex=set();attrs=set();unknown=set();literals=set();disabled=False;ops=[]
    for i in reach:
        n=g.nodes[i];k=n['kind']
        if k=='cbuffer':cbuf.setdefault(str(n['api_slot']),set()).add(int(n['dword']))
        elif k=='texture_sample':tex.add((int(n['texture_index']),str(n['channel']),str(n.get('address'))))
        elif k=='interpolant':attrs.add(str(n.get('attribute')))
        elif k=='unknown_register':unknown.add(n['register'])
        elif k=='literal':literals.add(str(n['value']))
        elif k=='disabled_export_lane':disabled=True
        elif k in ('vector_op','scalar_mov','predicate_op'):
            ops.append({'address':n.get('address'),'mnemonic':n.get('mnemonic'),'register':n.get('register')})
    return {
        'reachable_node_count':len(reach),
        'disabled_export_lane':disabled,
        'cbuffer_dwords':{k:sorted(v) for k,v in sorted(cbuf.items(),key=lambda x:int(x[0]))},
        'texture_sample_channels':[
            {'texture_index':t,'channel':ch,'sample_address':a}
            for t,ch,a in sorted(tex,key=lambda x:(x[0],x[1],x[2]))
        ],
        'interpolants':sorted(attrs),
        'unknown_registers':sorted(unknown),
        'literals':sorted(literals),
        'native_ops':sorted(ops,key=lambda x:(str(x['address']),str(x['register']))),
    }

def analyze(shader,path,image_row,cbuffer_row):
    image_by={str(x.get('address')).upper():x for x in image_row.get('instructions',[]) if x.get('address')}
    cbuf_by={str(x.get('address')).upper():x for x in cbuffer_row.get('loads',[]) if x.get('address')}
    g=Graph();terminal=None

    for line in path.read_text(errors='replace').splitlines():
        m=ADDR.search(line)
        if not m:continue
        addr,mn,rest=m.group(1).upper(),m.group(2),m.group(3)
        ops=splitops(rest)

        if addr in cbuf_by:
            rec=cbuf_by[addr]
            for r,dw in zip(rec.get('destination',[]),rec.get('dword_indices',[])):
                g.define(f's{int(r)}','cbuffer',api_slot=int(rec['api_slot']),dword=int(dw),address=addr)
            continue

        if mn=='s_mov_b32' and len(ops)>=2:
            d=firsttok(ops[0])
            if re.fullmatch(r's\d+',d):
                g.define(d,'scalar_mov',[g.src(ops[1])],mnemonic=mn,address=addr)
            continue

        if mn.startswith('image_') and addr in image_by:
            rec=image_by[addr];dests=expand_v(firsttok(ops[0]));chs=list(rec.get('dmask_channels') or '')
            resources=[int(x['texture_index']) for x in rec.get('resources',[]) if x.get('texture_index') is not None]
            if len(resources)!=1:raise ValueError(f'{shader}@{addr}: non-singular texture provenance {resources}')
            coords=[]
            if len(ops)>=2:
                rt=firsttok(ops[1]);rr=VRANGE.match(rt)
                if rr:coords=[g.src(f'v{i}') for i in range(int(rr.group(1)),int(rr.group(2))+1)]
                else:coords=[g.src(x) for x in REG.findall(ops[1]) if x.startswith('v')]
            if len(dests)!=len(chs):raise ValueError(f'{shader}@{addr}: image dest/dmask mismatch')
            for reg,ch in zip(dests,chs):
                g.define(reg,'texture_sample',coords,texture_index=resources[0],channel=ch,address=addr)
            continue

        if mn.startswith('v_interp_') and ops:
            d=firsttok(ops[0]);attr=next((x for x in ops if 'attr' in x),None)
            if re.fullmatch(r'v\d+',d):g.define(d,'interpolant',attribute=attr,address=addr)
            continue

        # Preserve explicit vector-predicate dataflow. This is required for
        # v_cmp_* -> v_cndmask_b32 chains that gate terminal colour.
        if mn.startswith('v_cmp') and ops:
            d=firsttok(ops[0])
            if d in SPECIAL_REGS:
                src=[]
                for op in ops[1:]:
                    rr=REG.findall(op)
                    if rr:src.extend(g.src(x) for x in rr)
                    else:
                        tok=firsttok(op)
                        if tok:src.append(g.src(tok))
                g.define(d,'predicate_op',src,mnemonic=mn,address=addr,assembly=line.strip())
                continue

        if mn.startswith('v_') and ops:
            d=firsttok(ops[0]);dests=expand_v(d)
            if dests:
                src=[]
                if mn.startswith('v_mac'):src.append(g.src(d))
                for op in ops[1:]:
                    rr=REG.findall(op)
                    if rr:src.extend(g.src(x) for x in rr)
                    else:
                        t=firsttok(op)
                        if t in SPECIAL_REGS:
                            src.append(g.src(t))
                        elif t and (t[0].isdigit() or t[0] in '+-' or t.startswith('0x')):
                            src.append(g.src(t))
                prepack=None
                if mn=='v_cvt_pkrtz_f16_f32' and len(ops)>=3:
                    prepack=(g.src(ops[1]),g.src(ops[2]))
                for reg in dests:
                    nid=g.define(reg,'vector_op',src,mnemonic=mn,address=addr,assembly=line.strip())
                    if prepack is not None:g.pack_roots[reg]={'low':prepack[0],'high':prepack[1],'node':nid,'address':addr}

        if mn=='exp' and rest.startswith('mrt0,'):
            eops=splitops(rest)
            if len(eops)<5:raise ValueError(f'{shader}@{addr}: malformed MRT0 export {rest}')
            terminal={'address':addr,'ops':[firsttok(x) for x in eops[1:5]],
                      'compressed':bool(re.search(r'\bcompr\b',rest)),'assembly':line.strip(),
                      'snapshot':dict(g.current),'pack_roots':dict(g.pack_roots)}

    if terminal is None:raise ValueError(f'{shader}: terminal MRT0 export missing')

    roots={}
    if terminal['compressed']:
        rg=terminal['ops'][0];ba=terminal['ops'][2]
        pr=terminal['pack_roots']
        if rg not in pr:raise ValueError(f'{shader}: compressed RG producer missing for {rg}')
        if ba not in pr:raise ValueError(f'{shader}: compressed BA producer missing for {ba}')
        roots={'R':pr[rg]['low'],'G':pr[rg]['high'],'B':pr[ba]['low'],'A':pr[ba]['high']}
    else:
        snap=terminal['snapshot']
        for ch,tok in zip(CHANNELS,terminal['ops']):
            if tok.lower()=='off':roots[ch]=g.node('disabled_export_lane',value='off')
            elif tok in snap:roots[ch]=snap[tok]
            else:roots[ch]=g.src(tok)

    channels={ch:{'root_node':roots[ch],'value_slice':summary(g,roots[ch],True),
                  'coordinate_expanded_slice':summary(g,roots[ch],False)} for ch in CHANNELS}
    union_tex=set();union_cbuf={};union_attr=set();unknown=set()
    for ch in CHANNELS:
        s=channels[ch]['value_slice']
        for api,dws in s['cbuffer_dwords'].items():union_cbuf.setdefault(api,set()).update(dws)
        union_tex.update((x['texture_index'],x['channel'],x['sample_address']) for x in s['texture_sample_channels'])
        union_attr.update(s['interpolants']);unknown.update(s['unknown_registers'])
    return {
        'shader':shader,'disassembly':str(path),
        'terminal_mrt0_export_address':terminal['address'],
        'terminal_mrt0_compressed':terminal['compressed'],
        'terminal_mrt0_operands':terminal['ops'],
        'channels':channels,
        'mrt0_value_union':{
            'cbuffer_dwords':{k:sorted(v) for k,v in sorted(union_cbuf.items(),key=lambda x:int(x[0]))},
            'texture_sample_channels':[
                {'texture_index':t,'channel':ch,'sample_address':a}
                for t,ch,a in sorted(union_tex,key=lambda x:(x[0],x[1],x[2]))
            ],
            'interpolants':sorted(union_attr),'unknown_registers':sorted(unknown),
        },
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--usage',type=Path,required=True)
    ap.add_argument('--cbuffer-usage',type=Path,required=True)
    ap.add_argument('--disasm-dir',type=Path,required=True)
    ap.add_argument('--shader',action='append',required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    u=json.loads(a.usage.read_text());c=json.loads(a.cbuffer_usage.read_text());v=[];rows=[]
    if u.get('status')!='D1_GCN_IMAGE_RESOURCE_USAGE_EXACT':v.append('image usage not exact')
    if c.get('status')!='D1_GCN_CBUFFER_USAGE_EXACT':v.append('cbuffer usage not exact')
    iby={norm(x['shader']):x for x in u.get('shaders',[])};cby={norm(x['shader']):x for x in c.get('shaders',[])}
    for raw in a.shader:
        h=norm(raw)
        try:
            p=a.disasm_dir/f'PS_{h}.s'
            if not p.exists():p=a.disasm_dir/f'PS_{h}_GFX700.s'
            if h not in iby:raise ValueError('image usage row missing')
            if h not in cby:raise ValueError('cbuffer usage row missing')
            if not p.exists():raise FileNotFoundError(p)
            rows.append(analyze(h,p,iby[h],cby[h]))
        except Exception as ex:v.append(f'{h}: {ex}')
    out={
        'schema':'d1_gcn_terminal_mrt0_dependency_census/v1',
        'status':'D1_GCN_TERMINAL_MRT0_DEPENDENCY_CENSUS_EXACT' if len(rows)==len(a.shader) and not v else 'D1_GCN_TERMINAL_MRT0_DEPENDENCY_CENSUS_PARTIAL',
        'shader_count':len(rows),'shaders':rows,'violations':v,
        'semantic_boundary':{
            'terminal_export_dataflow':'EXACT_NATIVE_GCN',
            'image_resources':'EXACT_SONY_USER_DATA_PROVENANCE',
            'constant_buffer_dwords':'EXACT_IMMCONSTBUFFER_PROVENANCE',
            'predicate_dependencies':'EXACT_FOR_EXPLICIT_VCC_SCC_EXEC_DATAFLOW',
            'human_material_or_lighting_roles':'WITHHELD',
        },
        'policy':'Reports exact terminal MRT0 numerical dependency leaves for both compressed and ordinary exports. It does not assign PBR/material/lighting semantics and does not claim coordinate-expanded image lanes are all consumed by hardware.',
    }
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'status':out['status'],'shaders':[
        {'shader':x['shader'],'compressed':x['terminal_mrt0_compressed'],'union':x['mrt0_value_union']}
        for x in rows],'violations':v},indent=2))
    return 0 if out['status']=='D1_GCN_TERMINAL_MRT0_DEPENDENCY_CENSUS_EXACT' else 2

if __name__=='__main__':raise SystemExit(main())
