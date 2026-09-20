#!/usr/bin/env python3
"""Backward-slice exact D1 GCN image-sample coordinate producers.

For every exact image instruction, this tool snapshots the VGPR dataflow feeding
its encoded coordinate register range *before* the sample overwrites destination
VGPRs.  It joins exact image resource/sampler provenance and exact ImmConstBuffer
provenance.

Coordinates may themselves depend on a previous texture sample (for example an
indirection/distortion map).  Those prior sampled channels remain explicit leaves.

No UV set, normal-map, distortion, material-role, or coordinate semantic is
assigned.
"""
from __future__ import annotations
import argparse,json,re
from pathlib import Path

ADDR=re.compile(r'/\*([0-9A-Fa-f]+):[^*]*\*/\s*(\w+)\s+(.*)$')
REG=re.compile(r'\b([vs]\d+)\b')
VRANGE=re.compile(r'^v\[(\d+):(\d+)\]$')

def norm(x): return str(x).upper().removeprefix('0X').zfill(8)
def splitops(rest): return [x.strip() for x in rest.split(',')]
def firsttok(s): return s.split()[0] if s.split() else ''
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

def summarize(g,roots):
    reach=set();stack=list(roots)
    while stack:
        x=stack.pop()
        if x in reach:continue
        reach.add(x);stack.extend(g.nodes[x].get('sources',[]))
    cbuf={};tex=set();attrs=set();unknown=set();literals=set();ops=[]
    for i in reach:
        n=g.nodes[i];k=n['kind']
        if k=='cbuffer':cbuf.setdefault(str(n['api_slot']),set()).add(int(n['dword']))
        elif k=='texture_sample':tex.add((int(n['texture_index']),str(n['channel']),str(n.get('address'))))
        elif k=='interpolant':attrs.add(str(n.get('attribute')))
        elif k=='unknown_register':unknown.add(n['register'])
        elif k=='literal':literals.add(str(n['value']))
        elif k=='vector_op':ops.append({'address':n.get('address'),'mnemonic':n.get('mnemonic'),'register':n.get('register')})
    return {
        'reachable_node_count':len(reach),
        'cbuffer_dwords':{k:sorted(v) for k,v in sorted(cbuf.items(),key=lambda x:int(x[0]))},
        'prior_texture_sample_channels':[
            {'texture_index':t,'channel':ch,'sample_address':a}
            for t,ch,a in sorted(tex,key=lambda x:(x[0],x[1],x[2]))
        ],
        'interpolants':sorted(attrs),
        'unknown_registers':sorted(unknown),
        'literals':sorted(literals),
        'vector_ops':sorted(ops,key=lambda x:(str(x['address']),x['register'])),
    }

def analyze(shader,path,image_row,cbuffer_row):
    image_by={str(x.get('address')).upper():x for x in image_row.get('instructions',[]) if x.get('address')}
    cbuf_by={str(x.get('address')).upper():x for x in cbuffer_row.get('loads',[]) if x.get('address')}
    g=Graph();samples=[]
    for line in path.read_text(errors='replace').splitlines():
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
            rec=image_by[addr]
            if len(ops)<2:raise ValueError(f'{shader}@{addr}: malformed image op')
            coord_tok=firsttok(ops[1]); coord_regs=expand_v(coord_tok)
            if not coord_regs:
                coord_regs=[x for x in REG.findall(ops[1]) if x.startswith('v')]
            roots=[g.src(x) for x in coord_regs]
            resources=[int(x['texture_index']) for x in rec.get('resources',[]) if x.get('texture_index') is not None]
            samplers=[int(x['sampler_index']) for x in rec.get('samplers',[]) if x.get('sampler_index') is not None]
            if len(resources)!=1:raise ValueError(f'{shader}@{addr}: texture provenance {resources}')
            if len(samplers)!=1:raise ValueError(f'{shader}@{addr}: sampler provenance {samplers}')
            samples.append({
                'address':addr,'opcode':mn,
                'texture_index':resources[0],'sampler_index':samplers[0],
                'coordinate_operand':ops[1],
                'encoded_coordinate_registers':coord_regs,
                'coordinate_sources':summarize(g,roots),
                'assembly':line.strip(),
            })

            # Only after snapshotting coordinate provenance do sample outputs replace VGPRs.
            dests=expand_v(firsttok(ops[0]));channels=list(rec.get('dmask_channels') or '')
            if len(dests)!=len(channels):
                raise ValueError(f'{shader}@{addr}: dest/dmask mismatch {dests}/{channels}')
            for reg,ch in zip(dests,channels):
                g.define(reg,'texture_sample',roots,texture_index=resources[0],sampler_index=samplers[0],channel=ch,address=addr)
            continue

        if mn.startswith('v_interp_') and ops:
            d=firsttok(ops[0]);attr=next((x for x in ops if 'attr' in x),None)
            if re.fullmatch(r'v\d+',d):g.define(d,'interpolant',attribute=attr,address=addr)
            continue

        if mn.startswith('v_') and ops:
            d=firsttok(ops[0]);dests=expand_v(d)
            if not dests:continue
            src=[]
            if mn.startswith('v_mac'):src.append(g.src(d))
            for op in ops[1:]:
                toks=REG.findall(op)
                if toks:src.extend(g.src(t) for t in toks)
                else:
                    t=firsttok(op)
                    if t and (t[0].isdigit() or t[0] in '+-' or t.startswith('0x')):src.append(g.src(t))
            for reg in dests:g.define(reg,'vector_op',src,mnemonic=mn,address=addr,assembly=line.strip())

    if len(samples)!=int(image_row.get('image_instruction_count',-1)):
        raise ValueError(f"{shader}: sample count {len(samples)} != image usage {image_row.get('image_instruction_count')}")
    return {'shader':shader,'sample_count':len(samples),'samples':samples}

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
    iby={norm(x['shader']):x for x in u.get('shaders',[])}
    cby={norm(x['shader']):x for x in c.get('shaders',[])}
    for raw in a.shader:
        h=norm(raw)
        try:
            p=a.disasm_dir/f'PS_{h}_GFX700.s'
            if h not in iby:raise ValueError('image usage row missing')
            if h not in cby:raise ValueError('cbuffer usage row missing')
            if not p.exists():raise FileNotFoundError(p)
            rows.append(analyze(h,p,iby[h],cby[h]))
        except Exception as ex:v.append(f'{h}: {ex}')
    out={
        'schema':'d1_gcn_image_coordinate_slice/v1',
        'status':'D1_GCN_IMAGE_COORDINATE_SLICE_EXACT' if len(rows)==len(a.shader) and not v else 'D1_GCN_IMAGE_COORDINATE_SLICE_PARTIAL',
        'shader_count':len(rows),'shaders':rows,'violations':v,
        'semantic_boundary':{
            'texture_and_sampler_identity':'EXACT_SONY_USER_DATA_PROVENANCE',
            'coordinate_dataflow':'EXACT_NATIVE_GCN_REGISTER_DATAFLOW',
            'UV_or_vector_semantics':'WITHHELD',
            'sampler_material_role':'WITHHELD',
        },
        'policy':'Coordinates are captured from the exact VGPR state immediately before each image instruction. Prior sampled channels and cbuffer/interpolant leaves remain explicit. Encoded VGPR range width is not promoted as coordinate dimensionality.',
    }
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'status':out['status'],'shaders':[{
        'shader':x['shader'],
        'samples':[{
            'address':s['address'],'texture':s['texture_index'],'sampler':s['sampler_index'],
            'coord_regs':s['encoded_coordinate_registers'],
            'sources':s['coordinate_sources'],
        } for s in x['samples']]
    } for x in rows],'violations':v},indent=2))
    return 0 if out['status']=='D1_GCN_IMAGE_COORDINATE_SLICE_EXACT' else 2

if __name__=='__main__':raise SystemExit(main())
