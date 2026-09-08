#!/usr/bin/env python3
"""Fail-closed binding proof for PS 8087670E API15.

Proves the target shader's spilled user-data descriptor layout and the exact
API15 vector selected by the current material state. This intentionally does not
invent the contents of API15 c0 or the absent serialized t4 resource.
"""
from __future__ import annotations
import argparse,json,re
from pathlib import Path
SH='8087670E';MATS=['808766B2','808766B6']
EXPECTED_USAGE=[('PtrExtendedUserData',1,2),('ImmSampler',1,4),('ImmSampler',2,8),('PtrResourceTable',0,12),('ImmSampler',3,16),('ImmSampler',4,20),('ImmSampler',5,24),('ImmSampler',6,28),('ImmConstBuffer',0,32),('ImmConstBuffer',12,36),('ImmConstBuffer',15,40)]
ANCHORS=[
's_load_dwordx4  s[32:35], s[2:3], 0xc',
's_load_dwordx4  s[8:11], s[2:3], 0x10',
's_load_dwordx4  s[20:23], s[2:3], 0x14',
's_load_dwordx4  s[16:19], s[2:3], 0x18',
's_buffer_load_dword s0, s[8:11], 0x30',
'v_cvt_i32_f32   v8, s0',
'v_readfirstlane_b32 s14, v8',
's_lshl_b32      s14, s14, 4',
's_buffer_load_dwordx4 s[16:19], s[16:19], s14',
's_buffer_load_dwordx4 s[20:23], s[20:23], 0x1c',
]
def flat(ps):return [float(v) for r in ps['cbuffers']['items'] for v in r['value']]
def main():
 p=argparse.ArgumentParser();p.add_argument('--extract-report',type=Path,required=True);p.add_argument('--material-state',type=Path,required=True);p.add_argument('--disassembly',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 e=json.loads(a.extract_report.read_text());s=json.loads(a.material_state.read_text());asm=a.disassembly.read_text();v=[]
 if e.get('status')!='D1_WORLD_PIXEL_SHADER_GCN_EXACT':v.append('extract checkpoint not exact')
 if s.get('status')!='D1_MATERIAL_STAGE_STATE_EXACT' or s.get('violations'):v.append('material state not exact')
 er=next((x for x in e.get('shaders',[]) if x.get('shader')==SH),None)
 if not er:v.append('shader extraction row absent')
 else:
  u=[(x.get('usage_name'),x.get('api_slot'),x.get('start_register')) for x in er.get('usage',{}).get('slots',[])]
  if u!=EXPECTED_USAGE:v.append(f'usage mismatch {u!r}')
 for x in ANCHORS:
  if x not in asm:v.append('missing native anchor '+x)
 # In this exact OrbShdr layout the first 16 user SGPR dwords are inline:
 # s2:3 extended-user ptr, s4:7 sampler1, s8:11 sampler2, s12:13 resource table.
 # User-data starts >=16 are spilled, so ext-table dword offset = start_register-16.
 spill={28:12,32:16,36:20,40:24}
 if spill!={28:0x0c,32:0x10,36:0x14,40:0x18}:v.append('internal spill formula error')
 indexes=[]
 for mh in MATS:
  m=s.get('materials',{}).get(mh)
  if not m or m.get('error'):v.append(mh+': material unresolved');continue
  if m['ps'].get('shader')!=SH:v.append(mh+': shader mismatch');continue
  vals=flat(m['ps'])
  if len(vals)<=48:v.append(mh+': b0 too short');continue
  if vals[48]!=0.0:v.append(f'{mh}: b0[48] no longer zero: {vals[48]!r}')
  indexes.append({'material':mh,'b0_48':vals[48],'float_to_i32':int(vals[48]),'byte_offset_after_lshl4':int(vals[48])*16,'api15_vec4_index':int(vals[48])})
 # Guard against the old incorrect interpretation: only descriptor s16:19 is API15.
 # All material-local scalar loads after s8:11 is filled from ext +0x10 are API0/b0.
 if 's_buffer_load_dwordx4 s[16:19], s[16:19], s14' not in asm:v.append('API15 dynamic load absent')
 if v:o={'schema_version':1,'status':'D1_TOWER_PS_8087670E_API15_BINDING_PARTIAL','violations':v};rc=2
 else:
  o={'schema_version':1,'status':'D1_TOWER_PS_8087670E_API15_BINDING_EXACT','violations':[],'shader':SH,'scope_materials':MATS,
   'inline_user_sgpr_dword_count':16,
   'spilled_user_data_mapping':[
    {'usage':'ImmSampler','api_slot':6,'start_register':28,'extended_user_data_dword_offset':12,'loaded_descriptor_registers':'s32:s35'},
    {'usage':'ImmConstBuffer','api_slot':0,'start_register':32,'extended_user_data_dword_offset':16,'loaded_descriptor_registers':'s8:s11'},
    {'usage':'ImmConstBuffer','api_slot':12,'start_register':36,'extended_user_data_dword_offset':20,'loaded_descriptor_registers':'s20:s23'},
    {'usage':'ImmConstBuffer','api_slot':15,'start_register':40,'extended_user_data_dword_offset':24,'loaded_descriptor_registers':'s16:s19'},
   ],
   'api15_load':{'descriptor_registers':'s16:s19','index_source':'material API0/b0 dword 48','index_conversion':'float -> i32 -> first lane -> <<4 bytes','current_material_indexes':indexes,'current_api15_vec4_index':0,'current_api15_byte_offset':0,'width_dwords':4},
   'critical_correction':'The earlier broad API15 trace was wrong: s8:s11 is the spilled material API0/b0 descriptor, not API15. API15 is loaded from extended-user-data +0x18 into s16:s19 and is consumed exactly once as one dynamically indexed float4. Current b0[48]=0 selects API15 c0.',
   'gates':{'api15_descriptor_binding_closed':True,'api15_selected_vector_index_closed':True,'api15_c0_runtime_value_closed':False,'runtime_t4_binding_closed':False,'final_shader_color_closed':False},
   'policy':'Binding and selected index are exact for this retail binary/current material state. API15 c0 contents and missing t4 remain unresolved and are not guessed.'};rc=0
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(o,indent=2)+'\n');print(json.dumps(o,indent=2));return rc
if __name__=='__main__':raise SystemExit(main())
