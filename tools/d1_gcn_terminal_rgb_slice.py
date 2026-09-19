#!/usr/bin/env python3
"""Backward-slice exact D1 GCN terminal MRT0 RGB dependencies.

For compressed MRT0 exports, the first packed register carries R/G and the
second carries B/A. This tool resolves the two v_cvt_pkrtz_f16_f32 producers
feeding the terminal export and slices R, G and B independently.

Inputs are exact image-resource and constant-buffer provenance reports plus the
pinned native disassembly. No material or lighting semantic is assigned.

Two slices are emitted per channel:
* value_slice stops at texture-sample values;
* coordinate_expanded_slice also follows texture-coordinate VGPR dependencies.

The latter is intentionally conservative because encoded coordinate VGPR ranges
can contain lanes unused by a particular image opcode.
"""
from __future__ import annotations
import argparse,json,re
from pathlib import Path

ADDR=re.compile(r'/\*([0-9A-Fa-f]+):[^*]*\*/\s*(\w+)\s+(.*)$')
REG=re.compile(r'\b([vs]\d+)\b')
VRANGE=re.compile(r'^v\[(\d+):(\d+)\]$')

def norm(x):return str(x).upper().removeprefix('0X').zfill(8)
def splitops(rest):return [x.strip() for x in rest.split(',')]
def firsttok(s):return s.split()[0] if s.split() else ''
def expand_v(tok):
    m=VRANGE.match(tok)
    if m:return [f'v{i}' for i in range(int(m.group(1)),int(m.group(2))+1)]
    return [tok] if re.fullmatch(r'v\d+',tok) else []

class Graph:
    def __init__(self):
        self.nodes={};self.current={};self.implicit={};self.next_id=0
    def node(self,kind,**kw):
        i=self.next_id;self.next_id+=1;self.nodes[i]={'id':i,'kind':kind,**kw};return i
    def src(self,tok):
        tok=firsttok(tok)
        if re.fullmatch(r'[vs]\d+',tok):
            if tok in self.current:return self.current[tok]
            if tok not in self.implicit:self.implicit[tok]=self.node('unknown_register',register=tok)
            return self.implicit[tok]
        return self.node('literal',value=tok)
    def define(self,reg,kind,sources=None,**kw):
        i=self.node(kind,register=reg,sources=list(sources or []),**kw);self.current[reg]=i;return i

def summary(g,root,stop_at_texture):
    reach=set();stack=[root]
    while stack:
        x=stack.pop()
        if x in reach:continue
        reach.add(x);n=g.nodes[x]
        if stop_at_texture and n['kind']=='texture_sample':continue
        stack.extend(n.get('sources',[]))
    cbuf={};textures=set();attrs=set();unknown=set();literals=set();ops=set()
    for i in reach:
        n=g.nodes[i];k=n['kind']
        if k=='cbuffer':cbuf.setdefault(str(n['api_slot']),set()).add(int(n['dword']))
        elif k=='texture_sample':textures.add((str(n['texture_index']),n['channel']))
        elif k=='interpolant':attrs.add(str(n.get('attribute')))
        elif k=='unknown_register':unknown.add(n['register'])
        elif k=='literal':literals.add(str(n['value']))
        elif k=='vector_op':ops.add((str(n.get('address')),str(n.get('mnemonic'))))
    return {
        'reachable_node_count':len(reach),
        'cbuffer_dwords':{k:sorted(v) for k,v in sorted(cbuf.items(),key=lambda x:int(x[0]))},
        'texture_sample_channels':[{'texture_index':t,'channel':ch} for t,ch in sorted(textures,key=lambda x:(int(x[0]),x[1]))],
        'interpolants':sorted(attrs),
        'unknown_registers':sorted(unknown),
        'literals':sorted(literals),
        'native_vector_ops':[{'address':a,'mnemonic':m} for a,m in sorted(ops)],
    }

def analyze(shader,path,image_row,cbuffer_row):
    image_by={str(x.get('address')).upper():x for x in image_row.get('instructions',[]) if x.get('address')}
    cbuf_by={str(x.get('address')).upper():x for x in cbuffer_row.get('loads',[]) if x.get('address')}
    lines=path.read_text(errors='replace').splitlines()

    export=None
    for line in lines:
        m=ADDR.search(line)
        if not m:continue
        addr,mn,rest=m.group(1).upper(),m.group(2),m.group(3)
        if mn=='exp' and rest.startswith('mrt0,') and re.search(r'\bcompr\b',rest):
            ops=splitops(rest)
            if len(ops)<5:raise ValueError(f'{shader}: malformed compressed MRT0 export')
            export={'address':addr,'rg_register':firsttok(ops[1]),'ba_register':firsttok(ops[3])}
    if export is None:raise ValueError(f'{shader}: compressed terminal MRT0 export not found')

    g=Graph();pack_roots={}
    for line in lines:
        m=ADDR.search(line)
        if not m:continue
        addr,mn,rest=m.group(1).upper(),m.group(2),m.group(3);ops=splitops(rest)

        if addr in cbuf_by:
            rec=cbuf_by[addr]
            for r,dw in zip(rec.get('destination',[]),rec.get('dword_indices',[])):
                g.define(f's{int(r)}','cbuffer',api_slot=int(rec['api_slot']),dword=int(dw),address=addr)
            continue

        if mn=='s_mov_b32' and len(ops)>=2:
            d=firsttok(ops[0])
            if re.fullmatch(r's\d+',d):g.define(d,'scalar_mov',[g.src(ops[1])],address=addr)
            continue

        if mn.startswith('image_') and addr in image_by:
            rec=image_by[addr];dests=expand_v(firsttok(ops[0]));channels=list(rec.get('dmask_channels') or '')
            resources=[x.get('texture_index') for x in rec.get('resources',[]) if x.get('texture_index') is not None]
            if len(resources)!=1:raise ValueError(f'{shader}@{addr}: image resource provenance not singular: {resources}')
            coords=[]
            if len(ops)>=2:
                rt=firsttok(ops[1]);rr=VRANGE.match(rt)
                if rr:coords=[g.src(f'v{i}') for i in range(int(rr.group(1)),int(rr.group(2))+1)]
                else:coords=[g.src(t) for t in REG.findall(ops[1]) if t.startswith('v')]
            if len(dests)!=len(channels):raise ValueError(f'{shader}@{addr}: destination/dmask width mismatch {dests}/{channels}')
            for reg,ch in zip(dests,channels):
                g.define(reg,'texture_sample',coords,texture_index=int(resources[0]),channel=ch,address=addr)
            continue

        if mn.startswith('v_interp_') and len(ops)>=2:
            d=firsttok(ops[0]);attr=next((x for x in ops if 'attr' in x),None)
            if re.fullmatch(r'v\d+',d):g.define(d,'interpolant',attribute=attr,address=addr)
            continue

        if mn.startswith('v_') and ops:
            d=firsttok(ops[0]);dests=expand_v(d)
            if not dests:continue
            srcids=[]
            if mn.startswith('v_mac'):srcids.append(g.src(d))
            for op in ops[1:]:
                toks=REG.findall(op)
                if toks:srcids.extend(g.src(t) for t in toks)
                else:
                    t=firsttok(op)
                    if t and (t[0].isdigit() or t[0] in '+-' or t.startswith('0x')):srcids.append(g.src(t))
            prepack=None
            if mn=='v_cvt_pkrtz_f16_f32' and len(ops)>=3:
                prepack=(g.src(ops[1]),g.src(ops[2]))
            for reg in dests:
                nid=g.define(reg,'vector_op',srcids,mnemonic=mn,address=addr,assembly=line.strip())
                if prepack is not None and reg in (export['rg_register'],export['ba_register']):
                    pack_roots[reg]={'low':prepack[0],'high':prepack[1],'pack_node':nid,'address':addr}

    rg=pack_roots.get(export['rg_register']);ba=pack_roots.get(export['ba_register'])
    if not rg:raise ValueError(f"{shader}: R/G pack producer not found for {export['rg_register']}")
    if not ba:raise ValueError(f"{shader}: B/A pack producer not found for {export['ba_register']}")
    roots={'R':rg['low'],'G':rg['high'],'B':ba['low']}
    channels={}
    for ch,root in roots.items():
        channels[ch]={
            'root_node':root,
            'value_slice':summary(g,root,True),
            'coordinate_expanded_slice':summary(g,root,False),
        }
    # union exact value-level leaves for convenient family comparisons
    union_cbuf={};union_tex=set();union_attr=set();union_unknown=set()
    for ch in ('R','G','B'):
        s=channels[ch]['value_slice']
        for api,dws in s['cbuffer_dwords'].items():union_cbuf.setdefault(api,set()).update(dws)
        union_tex.update((x['texture_index'],x['channel']) for x in s['texture_sample_channels'])
        union_attr.update(s['interpolants']);union_unknown.update(s['unknown_registers'])
    return {
        'shader':shader,'disassembly':str(path),
        'terminal_mrt0_export_address':export['address'],
        'terminal_packed_rg_register':export['rg_register'],
        'terminal_packed_ba_register':export['ba_register'],
        'channels':channels,
        'rgb_value_union':{
            'cbuffer_dwords':{k:sorted(v) for k,v in sorted(union_cbuf.items(),key=lambda x:int(x[0]))},
            'texture_sample_channels':[{'texture_index':t,'channel':ch} for t,ch in sorted(union_tex,key=lambda x:(int(x[0]),x[1]))],
            'interpolants':sorted(union_attr),'unknown_registers':sorted(union_unknown),
        },
        'semantic_boundary':'NUMERICAL_NATIVE_RGB_DATAFLOW_ONLY_NO_COLOR_ROLE_LIGHTING_ROLE_OR_PASS_ORDER_ASSIGNED',
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
            p=a.disasm_dir/f'PS_{h}_GFX700.s'
            if not p.exists():raise FileNotFoundError(p)
            rows.append(analyze(h,p,iby[h],cby[h]))
        except Exception as ex:violations.append(f'{h}: {ex}')
    out={
        'schema':'d1_gcn_terminal_rgb_slice/v1',
        'status':'D1_GCN_TERMINAL_RGB_SLICE_EXACT' if len(rows)==len(a.shader) and not violations else 'D1_GCN_TERMINAL_RGB_SLICE_PARTIAL',
        'shader_count':len(rows),'shaders':rows,'violations':violations,
        'policy':'R/G and B roots are recovered from the two exact packed-half producers feeding terminal compressed MRT0. value_slice stops at exact texture sample values; coordinate_expanded_slice follows coordinate registers conservatively. Cbuffer leaves require exact Sony ImmConstBuffer provenance. No RGB/light/pass semantic is inferred.',
    }
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'status':out['status'],'shaders':[{'shader':x['shader'],'rgb_value_union':x['rgb_value_union']} for x in rows],'violations':violations},indent=2))
    return 0 if out['status']=='D1_GCN_TERMINAL_RGB_SLICE_EXACT' else 2

if __name__=='__main__':raise SystemExit(main())
