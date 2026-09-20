#!/usr/bin/env python3
"""Trace Crota VS param1.xy to exact GNM vertex-input semantic VGPRs.

The PS8108E955 coordinate proof leaves t0's first two coordinate lanes as
attr1.x/attr1.y. d1_gnm_vs_ps_linkage proves attr1 is supplied by a VS param
through an exact raw semantic-ID match. This tool follows that VS param's native
GCN dataflow backward to the GnmVertexInputSemantic VGPR ranges.

Names such as TEXCOORD, UV, position, normal, or tangent are deliberately not
assigned. The strongest output is a raw semantic ID + input element lineage.
"""
from __future__ import annotations
import argparse,json,re
from pathlib import Path

ADDR=re.compile(r'/\*([0-9A-Fa-f]+):[^*]*\*/\s*(\w+)\s+(.*)$')
REG=re.compile(r'\b([vs]\d+)\b')
VRANGE=re.compile(r'^v\[(\d+):(\d+)\]$')
EXP=re.compile(r'^param(\d+)$')

def norm(x):return str(x).upper().removeprefix('0X').zfill(8)
def splitops(rest):return [x.strip() for x in rest.split(',')]
def firsttok(s):return s.split()[0] if s.split() else ''
def expand_v(tok):
    m=VRANGE.match(tok)
    if m:return [f'v{i}' for i in range(int(m.group(1)),int(m.group(2))+1)]
    return [tok] if re.fullmatch(r'v\d+',tok) else []

class Graph:
    def __init__(self,inputs):
        self.nodes={};self.current={};self.implicit={};self.next_id=0
        self.input_register_map={}
        for row in inputs:
            start=int(row['vgpr']);count=int(row['size_in_elements'])
            if count<=0:raise ValueError(f"input semantic {row['index']}: size_in_elements={count}")
            for j in range(count):
                reg=f'v{start+j}'
                if reg in self.input_register_map:
                    raise ValueError(f'overlapping vertex input VGPR {reg}')
                meta={
                    'input_index':int(row['index']),'semantic':int(row['semantic']),
                    'input_start_vgpr':start,'size_in_elements':count,
                    'element_index':j,'raw_hex':row.get('raw_hex'),
                }
                nid=self.node('vertex_input',register=reg,**meta)
                self.current[reg]=nid;self.input_register_map[reg]=meta
    def node(self,kind,**kw):
        i=self.next_id;self.next_id+=1;self.nodes[i]={'id':i,'kind':kind,**kw};return i
    def src(self,tok):
        tok=firsttok(tok)
        if re.fullmatch(r'[vs]\d+',tok):
            if tok in self.current:return self.current[tok]
            if tok not in self.implicit:
                self.implicit[tok]=self.node('unknown_register',register=tok)
            return self.implicit[tok]
        return self.node('literal',value=tok)
    def define(self,reg,kind,sources=None,**kw):
        nid=self.node(kind,register=reg,sources=list(sources or []),**kw)
        self.current[reg]=nid;return nid

def summary(g,roots):
    reach=set();stack=list(roots)
    while stack:
        n=stack.pop()
        if n in reach:continue
        reach.add(n);stack.extend(g.nodes[n].get('sources',[]))
    vin=[];unknown=set();scalar=set();literals=set();ops=[]
    for nid in reach:
        n=g.nodes[nid];k=n['kind']
        if k=='vertex_input':
            vin.append({
                'input_index':n['input_index'],'semantic':n['semantic'],
                'register':n['register'],'input_start_vgpr':n['input_start_vgpr'],
                'size_in_elements':n['size_in_elements'],'element_index':n['element_index'],
                'raw_hex':n.get('raw_hex'),
            })
        elif k=='unknown_register':
            (scalar if str(n['register']).startswith('s') else unknown).add(n['register'])
        elif k=='literal':literals.add(str(n['value']))
        elif k=='vector_op':
            ops.append({'address':n.get('address'),'mnemonic':n.get('mnemonic'),'register':n.get('register')})
    # dedupe stable
    seen=set();uniq=[]
    for x in sorted(vin,key=lambda x:(x['input_index'],x['element_index'],x['register'])):
        key=(x['input_index'],x['semantic'],x['register'],x['element_index'])
        if key not in seen:seen.add(key);uniq.append(x)
    return {
        'vertex_input_leaves':uniq,
        'vertex_input_semantic_ids':sorted({x['semantic'] for x in uniq}),
        'vertex_input_indices':sorted({x['input_index'] for x in uniq}),
        'unknown_vgpr_leaves':sorted(unknown),
        'scalar_register_leaves':sorted(scalar),
        'literals':sorted(literals),
        'vector_ops':sorted(ops,key=lambda x:(str(x['address']),x['register'])),
        'reachable_node_count':len(reach),
    }

def analyze(vs,path,header,target_param=1):
    inputs=header.get('vertex_input_semantics') or []
    if not inputs:raise ValueError(f'{vs}: no vertex input semantics')
    g=Graph(inputs);exports={}
    for line in path.read_text(errors='replace').splitlines():
        m=ADDR.search(line)
        if not m:continue
        addr,mn,rest=m.group(1).upper(),m.group(2),m.group(3)
        ops=splitops(rest)
        if mn=='exp' and ops:
            em=EXP.match(firsttok(ops[0]))
            if em:
                pidx=int(em.group(1));src=[]
                for op in ops[1:5]:
                    regs=[x for x in REG.findall(op) if x.startswith('v')]
                    if regs:src.append(g.src(regs[0]))
                    else:src.append(g.src(op))
                exports[pidx]={'address':addr,'assembly':line.strip(),'roots':src}
            continue
        if mn.startswith('v_') and ops:
            dest=firsttok(ops[0]);dests=expand_v(dest)
            if not dests:continue
            src=[]
            if mn.startswith('v_mac'):src.append(g.src(dest))
            for op in ops[1:]:
                regs=REG.findall(op)
                if regs:src.extend(g.src(x) for x in regs)
                else:
                    t=firsttok(op)
                    if t and (t[0].isdigit() or t[0] in '+-' or t.startswith('0x')):
                        src.append(g.src(t))
            for reg in dests:g.define(reg,'vector_op',src,address=addr,mnemonic=mn,assembly=line.strip())
            continue
        # Track common scalar moves enough to avoid falsely treating copied SGPRs as independent.
        if mn.startswith('s_') and ops:
            d=firsttok(ops[0])
            if re.fullmatch(r's\d+',d) and len(ops)>=2:
                src=[]
                for op in ops[1:]:
                    regs=REG.findall(op)
                    if regs:src.extend(g.src(x) for x in regs)
                    else:
                        t=firsttok(op)
                        if t:src.append(g.src(t))
                g.define(d,'scalar_op',src,address=addr,mnemonic=mn,assembly=line.strip())
    ex=exports.get(target_param)
    if ex is None:raise ValueError(f'{vs}: param{target_param} export not found')
    if len(ex['roots'])<2:raise ValueError(f'{vs}: param{target_param} has <2 export lanes')
    return {
        'vertex_shader':vs,
        'target_param_index':target_param,
        'target_export_address':ex['address'],
        'target_export_assembly':ex['assembly'],
        'x':summary(g,[ex['roots'][0]]),
        'y':summary(g,[ex['roots'][1]]),
        'xy':summary(g,ex['roots'][:2]),
        'vertex_input_semantics':inputs,
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--extract-report',type=Path,required=True)
    ap.add_argument('--linkage',type=Path,required=True)
    ap.add_argument('--disasm-dir',type=Path,required=True)
    ap.add_argument('--vertex-shader',action='append',required=True)
    ap.add_argument('--pixel-shader',default='8108E955')
    ap.add_argument('--attr-index',type=int,default=1)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    ex=json.loads(a.extract_report.read_text());lk=json.loads(a.linkage.read_text());violations=[];rows=[]
    if ex.get('status')!='D1_WORLD_PIXEL_SHADER_GCN_EXACT' or ex.get('error_count'):
        violations.append('shader extract not exact')
    if lk.get('status')!='D1_GNM_VS_PS_LINKAGE_EXACT' or lk.get('violations'):
        violations.append('VS/PS linkage not exact')
    by={norm(x['shader']):x for x in ex.get('shaders',[])}
    ps=norm(a.pixel_shader)
    links={(norm(x['vertex_shader']),norm(x['pixel_shader'])):x for x in lk.get('links',[])}
    for raw in a.vertex_shader:
        vs=norm(raw)
        try:
            sh=by[vs];gh=sh.get('gnm_header') or {}
            if gh.get('status')!='D1_PS4_GNM_SHADER_HEADER_EXACT' or gh.get('stage')!='VertexShader':
                raise ValueError('exact VertexShader GNM header absent')
            link=links.get((vs,ps))
            if not link:raise ValueError(f'{vs}:{ps}: exact linkage row absent')
            ar=[x for x in link.get('consumed_linkage',[]) if int(x['attr_index'])==a.attr_index]
            if len(ar)!=1:raise ValueError(f'attr{a.attr_index}: expected one linkage row, got {len(ar)}')
            if ar[0].get('vs_param_index') is None:raise ValueError(f'attr{a.attr_index}: no VS param producer')
            pidx=int(ar[0]['vs_param_index'])
            path=a.disasm_dir/f'PS_{vs}_GFX700.s'
            if not path.exists():path=a.disasm_dir/f'PS_{vs}.s'
            if not path.exists():raise FileNotFoundError(path)
            r=analyze(vs,path,gh,pidx)
            r['pixel_shader']=ps;r['pixel_attr_index']=a.attr_index
            r['raw_link_semantic_id']=int(ar[0]['semantic'])
            r['vs_param_index_from_linkage']=pidx
            # A surviving coordinate source is only called completely mapped when
            # x/y reach exact vertex-input rows and no unknown VGPR leaf remains.
            r['xy_vertex_input_lineage_complete']=bool(r['xy']['vertex_input_leaves']) and not r['xy']['unknown_vgpr_leaves']
            rows.append(r)
        except Exception as e:violations.append(f'{vs}:{e}')
    out={
        'schema':'d1_crota_vs_param_vertex_input_lineage/v1',
        'status':'D1_CROTA_VS_PARAM_VERTEX_INPUT_LINEAGE_EXACT' if len(rows)==len(a.vertex_shader) and not violations else 'D1_CROTA_VS_PARAM_VERTEX_INPUT_LINEAGE_PARTIAL',
        'rows':rows,'violations':violations,
        'semantic_boundary':{
            'PS_attr_to_VS_param':'EXACT_RAW_GNM_SEMANTIC_LINKAGE',
            'VS_param_to_vertex_input_vgprs':'EXACT_NATIVE_GCN_DATAFLOW',
            'vertex_input_semantic_id':'EXACT_GNM_HEADER',
            'vertex_stream_or_fetch_descriptor_identity':'WITHHELD',
            'TEXCOORD_UV_position_normal_names':'WITHHELD',
        },
        'policy':'GnmVertexInputSemantic size_in_elements is used as the exact VGPR span described by the standard PS4 GNM table. The result names only raw semantic IDs and element indices; source stream/fetch descriptors and human vertex semantics remain separate gates.',
    }
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'status':out['status'],'rows':[{
        'vs':r['vertex_shader'],'param':r['target_param_index'],'export':r['target_export_assembly'],
        'link_semantic':r['raw_link_semantic_id'],'x':r['x'],'y':r['y'],
        'xy_complete':r['xy_vertex_input_lineage_complete'],
    } for r in rows],'violations':violations},indent=2))
    return 0 if out['status']=='D1_CROTA_VS_PARAM_VERTEX_INPUT_LINEAGE_EXACT' else 2

if __name__=='__main__':raise SystemExit(main())
