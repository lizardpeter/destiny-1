#!/usr/bin/env python3
"""Backward-slice exact D1 GCN terminal MRT0 alpha dependencies.

Inputs are source-closed native disassembly plus exact image-resource and cbuffer
provenance reports.  For compressed MRT0 exports, VSRC1 carries packed B/A; this
tool locates the v_cvt_pkrtz_f16_f32 definition feeding that packed register and
starts from its high-half (A) source.

Two slices are emitted:
* value_slice stops at texture-sample results, exposing direct arithmetic inputs;
* coordinate_expanded_slice also follows the sampled-value coordinate VGPRs as a
  conservative dependency superset.

Texture-coordinate arity is intentionally not inferred from the encoded VGPR range,
so the expanded slice may retain unknown unused coordinate lanes.  The value slice
does not have that ambiguity.
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
 cbuf={};textures=set();attrs=set();unknown=set();literals=set()
 for i in reach:
  n=g.nodes[i];k=n['kind']
  if k=='cbuffer':cbuf.setdefault(str(n['api_slot']),set()).add(int(n['dword']))
  elif k=='texture_sample':textures.add((str(n['texture_index']),n['channel']))
  elif k=='interpolant':attrs.add(str(n.get('attribute')))
  elif k=='unknown_register':unknown.add(n['register'])
  elif k=='literal':literals.add(str(n['value']))
 return {
  'reachable_node_count':len(reach),
  'cbuffer_dwords':{k:sorted(v) for k,v in sorted(cbuf.items(),key=lambda x:int(x[0]))},
  'texture_sample_channels':[{'texture_index':t,'channel':ch} for t,ch in sorted(textures,key=lambda x:(str(x[0]),x[1]))],
  'interpolants':sorted(attrs),'unknown_registers':sorted(unknown),'literals':sorted(literals),
 }

def analyze(shader,path,image_row,cbuffer_row):
 image_by={str(x.get('address')).upper():x for x in image_row.get('instructions',[]) if x.get('address')}
 cbuf_by={str(x.get('address')).upper():x for x in cbuffer_row.get('loads',[]) if x.get('address')}
 lines=path.read_text(errors='replace').splitlines()
 ba_reg=None;export_address=None
 for line in lines:
  m=ADDR.search(line)
  if not m:continue
  addr,mn,rest=m.group(1).upper(),m.group(2),m.group(3)
  if mn=='exp' and rest.startswith('mrt0,') and re.search(r'\bcompr\b',rest):
   ops=splitops(rest)
   if len(ops)<5:raise ValueError(f'{shader}: malformed compressed MRT0 export')
   ba_reg=firsttok(ops[3]);export_address=addr
 if ba_reg is None:raise ValueError(f'{shader}: compressed terminal MRT0 export not found')

 g=Graph();alpha_root=None;alpha_pack=None
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
    if rr:
     coords=[g.src(f'v{i}') for i in range(int(rr.group(1)),int(rr.group(2))+1)]
    else:
     coords=[g.src(t) for t in REG.findall(ops[1]) if t.startswith('v')]
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
   pre_alpha=None
   if mn=='v_cvt_pkrtz_f16_f32' and d==ba_reg and len(ops)>=3:
    pre_alpha=g.src(ops[2])
   for reg in dests:
    nid=g.define(reg,'vector_op',srcids,mnemonic=mn,address=addr,assembly=line.strip())
    if reg==ba_reg and pre_alpha is not None:
     alpha_pack=nid;alpha_root=pre_alpha

 if alpha_root is None:raise ValueError(f'{shader}: packed alpha source definition not found for {ba_reg}')
 return {
  'shader':shader,'disassembly':str(path),'terminal_mrt0_export_address':export_address,
  'terminal_packed_ba_register':ba_reg,'terminal_alpha_root_node':alpha_root,'terminal_pack_node':alpha_pack,
  'value_slice':summary(g,alpha_root,True),
  'coordinate_expanded_slice':summary(g,alpha_root,False),
  'semantic_boundary':'NUMERICAL_NATIVE_DATAFLOW_ONLY_NO_ALPHA_ROLE_OR_PASS_ORDER_ASSIGNED',
 }

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--usage',type=Path,required=True);ap.add_argument('--cbuffer-usage',type=Path,required=True)
 ap.add_argument('--disasm-dir',type=Path,required=True);ap.add_argument('--shader',action='append',required=True)
 ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
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
 out={'schema':'d1_gcn_terminal_alpha_slice/v1',
      'status':'D1_GCN_TERMINAL_ALPHA_SLICE_EXACT' if len(rows)==len(a.shader) and not violations else 'D1_GCN_TERMINAL_ALPHA_SLICE_PARTIAL',
      'shader_count':len(rows),'shaders':rows,'violations':violations,
      'policy':'Starts from the high half packed into terminal compressed MRT0 BA. value_slice stops at exact image-sample results; coordinate_expanded_slice additionally follows the encoded coordinate VGPR range conservatively and may include unused coordinate lanes. Cbuffer leaves require exact Sony ImmConstBuffer provenance.'}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'status':out['status'],'shaders':[{ 'shader':x['shader'],'value_slice':x['value_slice'],'coordinate_expanded_slice':x['coordinate_expanded_slice']} for x in rows],'violations':violations},indent=2))
 return 0 if out['status']=='D1_GCN_TERMINAL_ALPHA_SLICE_EXACT' else 2

if __name__=='__main__':raise SystemExit(main())
