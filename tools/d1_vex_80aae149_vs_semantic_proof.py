#!/usr/bin/env python3
"""Exact instruction-level semantic proof for D1 PS4 VS 80AAE149.

The proof is deliberately arithmetic/structural. It closes the rigid transform-
palette indexing and param0..param4 relationships but does not invent Bungie
field names for the API10/API11/API12 buffers or unresolved fetch-shader source
elements.
"""
from __future__ import annotations
import argparse,hashlib,json,re
from pathlib import Path

SHADER='80AAE149'
NATIVE='80AAE14A'
NATIVE_SHA='71f11fd1f403eb087ae2fa6d9051f0f4e0ae27f680208ae269bef11e84b39996'
GCN_SHA='e6f18138e330a9c6b3ddce2e71890b1bcda73f732c4f6007b4c788c0ff62f4c0'
GCN_BYTES=508
USAGE=[
 ('SubPtrFetchShader',0,0),
 ('PtrVertexBufferTable',0,2),
 ('PtrExtendedUserData',1,6),
 ('ImmConstBuffer',10,8),
 ('ImmConstBuffer',11,12),
 ('ImmConstBuffer',12,16),
]
ANCHORS=[
 'v_mov_b32       v0, 0x3dcccccd',
 's_mov_b32       s0, 0x46fffe00',
 'v_mac_f32       v0, s0, v7',
 'v_cvt_u32_f32   v0, v0',
 'v_mul_lo_u32    v0, v0, 3',
 'v_add_i32       v1, vcc, 1, v0',
 'v_add_i32       v2, vcc, 2, v0',
 'tbuffer_load_format_xyzw v[20:23], v0, s[8:11], 0 idxen format:[32_32_32_32,float]',
 'tbuffer_load_format_xyzw v[24:27], v1, s[8:11], 0 idxen format:[32_32_32_32,float]',
 'tbuffer_load_format_xyzw v[0:3], v2, s[8:11], 0 idxen format:[32_32_32_32,float]',
 's_load_dwordx4  s[0:3], s[6:7], 0x0',
 's_buffer_load_dwordx4 s[4:7], s[12:15], 0x14',
 's_buffer_load_dwordx4 s[8:11], s[0:3], 0xc',
 's_buffer_load_dwordx4 s[16:19], s[0:3], 0x0',
 's_buffer_load_dwordx4 s[20:23], s[0:3], 0x4',
 's_buffer_load_dwordx4 s[0:3], s[0:3], 0x8',
 'exp             pos0, v5, v11, v15, v23 done',
 's_buffer_load_dwordx4 s[0:3], s[12:15], 0x1c',
 's_buffer_load_dwordx4 s[4:7], s[12:15], 0x18',
 'v_mul_f32       v1, v6, v14',
 'v_mad_f32       v1, v4, v2, -v1',
 'v_mad_f32       v12, v6, v11, -v12',
 'v_mad_f32       v13, v5, v14, -v13',
 'v_mul_f32       v1, v19, v1',
 'v_mul_f32       v12, v19, v12',
 'v_mul_f32       v13, v19, v13',
 'exp             param0, v5, v4, v6, v0',
 'exp             param1, v11, v14, v2, v2',
 'exp             param2, v1, v12, v13, v8',
 'exp             param3, v15, v16, v15, v16',
 'exp             param4, v7, v10, v3, v8',
]

def norm(line:str)->str:
 line=re.sub(r'/\*.*?\*/','',line)
 return re.sub(r'\s+',' ',line.strip())

def reconstruct(text:str)->bytes:
 rows=[]
 for line in text.splitlines():
  m=re.match(r'/\*([0-9A-Fa-f]{12}):\s*([0-9A-Fa-f ]+)\*/',line.strip())
  if not m:continue
  addr=int(m.group(1),16)
  raw=b''.join(bytes.fromhex(w)[::-1] for w in m.group(2).split())
  rows.append((addr,raw))
 rows.sort();out=bytearray()
 for addr,raw in rows:
  if addr!=len(out):raise ValueError(f'non-contiguous code at {addr:#x}, expected {len(out):#x}')
  out.extend(raw)
 return bytes(out)

def main()->int:
 ap=argparse.ArgumentParser();ap.add_argument('--extract-report',type=Path,required=True);ap.add_argument('--disassembly',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 rep=json.loads(a.extract_report.read_text());text=a.disassembly.read_text(errors='replace');v=[]
 if rep.get('status')!='D1_WORLD_PIXEL_SHADER_GCN_EXACT' or rep.get('error_count')!=0:v.append('extract_not_exact')
 rows=rep.get('shaders') or [];row=rows[0] if len(rows)==1 else {}
 if len(rows)!=1:v.append(f'shader_row_count:{len(rows)}')
 if row.get('shader')!=SHADER:v.append('shader_identity')
 if row.get('native_shader')!=NATIVE:v.append('native_identity')
 if row.get('native_sha256')!=NATIVE_SHA:v.append('native_sha256')
 if (row.get('binary_info') or {}).get('stage')!='VertexShader':v.append('stage_not_vertex')
 if row.get('gcn_bytes')!=GCN_BYTES or row.get('gcn_sha256')!=GCN_SHA:v.append('gcn_identity')
 got=[(x.get('usage_name'),int(x.get('api_slot')),int(x.get('start_register'))) for x in ((row.get('usage') or {}).get('slots') or [])]
 if got!=USAGE:v.append(f'usage_layout:{got!r}')
 try:
  code=reconstruct(text);sha=hashlib.sha256(code).hexdigest()
 except Exception as ex:
  code=b'';sha=None;v.append(f'clrx_reconstruction:{ex!r}')
 if len(code)!=GCN_BYTES:v.append(f'clrx_length:{len(code)}')
 if sha!=GCN_SHA:v.append(f'clrx_sha:{sha}')
 lines=[norm(x) for x in text.splitlines() if norm(x)]
 cur=0;found=[]
 for q in ANCHORS:
  try:i=lines.index(q,cur)
  except ValueError:v.append('missing_or_out_of_order:'+q);continue
  found.append(q);cur=i+1
 exact=not v
 out={
  'schema':'d1_vex_80aae149_vs_semantic_proof/v1',
  'status':'D1_VEX_80AAE149_VERTEX_INTERFACE_EXACT' if exact else 'D1_VEX_80AAE149_VERTEX_INTERFACE_PARTIAL',
  'shader':SHADER,'native_shader':NATIVE,'native_sha256':NATIVE_SHA,'gcn_bytes':len(code),'gcn_sha256':sha,
  'orbshdr_usage':[{'usage_name':n,'api_slot':api,'start_register':start} for n,api,start in got],
  'rigid_palette_index':{
   'fetch_register':'v7',
   'exact_expression':'uint(0.1 + 32767.0 * fetch_v7)',
   'row_indices':['3*joint','3*joint+1','3*joint+2'],
   'descriptor':'ImmConstBuffer api10 / s[8:11]',
   'row_format':'float4 x 3',
   'role':'three-row rigid transform selected by the recovered integer index',
  } if exact else None,
  'position_chain':{
   'source_position_registers':['v4','v5','v6'],
   'api11_pre_palette_affine':[
    'local.x = api11[20] + api11[23] * fetch_v4',
    'local.y = api11[21] + api11[23] * fetch_v5',
    'local.z = api11[22] + api11[23] * fetch_v6',
   ],
   'palette_transform':'P.xyz = float3(dot(row0.xyz,local)+row0.w, dot(row1.xyz,local)+row1.w, dot(row2.xyz,local)+row2.w)',
   'param4':'float4(P.xyz,1)',
   'clip_position':'pos0 = column-major api12[0..15] affine/projective transform of float4(P.xyz,1)',
  } if exact else None,
  'basis_chain':{
   'basis0_source_registers':['v12','v13','v14'],
   'basis1_source_registers':['v16','v17','v18'],
   'basis0':'3x3 transform by the selected api10 rows; exported as param0.xyz',
   'basis1':'3x3 transform by the selected api10 rows; exported as param1.xyz',
   'basis2':'cross(param0.xyz,param1.xyz) * fetch_v19; exported as param2.xyz',
   'handedness_source_register':'v19',
   'param2_w':'1.0',
   'semantic_names':'WITHHELD_PENDING_FETCH_SHADER_SOURCE_MAPPING',
  } if exact else None,
  'coordinate_chain':{
   'source_registers':['v8','v9'],
   'x':'api11[26] + api11[24] * fetch_v8',
   'y':'api11[27] + api11[25] * fetch_v9',
   'param3':'float4(x,y,x,y)',
   'pixel_use':'attr3.xy is sampled as the base 2D material coordinate by both target pixel shaders',
  } if exact else None,
  'param0_w':{
   'equation':'saturate(api11[31] + api11[28]*param0.x + api11[29]*param0.y + api11[30]*param0.z)',
   'pixel_use_main':'80AAE14B forwards attr0.w to native MRT0 alpha',
   'engine_semantic':'WITHHELD',
  } if exact else None,
  'pixel_interface':{
   'attr0':'param0 = (basis0.xyz, api11 affine/clamped scalar)',
   'attr1':'param1 = (basis1.xyz, basis1.z)',
   'attr2':'param2 = (cross(basis0,basis1)*handedness, 1)',
   'attr3':'param3 = (coord.x,coord.y,coord.x,coord.y)',
   'attr4':'param4 = (pre-clip transformed position P.xyz,1)',
  } if exact else None,
  'unresolved':[
   'fetch-shader mapping from v4/v5/.../v19 to exact serialized vertex byte offsets/formats',
   'Bungie engine names for api10/api11/api12',
   'engine semantic name of param0.w scalar',
   'whether basis0/basis1 are named normal/tangent in Bungie source',
  ],
  'anchors':found,'violations':v,
  'policy':'Only exact retail OrbShdr metadata and ordered GFX700 instructions are promoted. Basis/position/coordinate arithmetic is exact; source element names and Bungie engine names remain withheld until the fetch shader/source layout is independently closed.'
 }
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));return 0 if exact else 2
if __name__=='__main__':raise SystemExit(main())
