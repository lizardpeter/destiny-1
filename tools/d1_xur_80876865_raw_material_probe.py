#!/usr/bin/env python3
"""Fresh raw D1 ROI decode of Xur material 80876865.

Purpose: close whether U4A[4] can be backed by any serialized material-local
Vector4 container or hidden adjacent ROI material field. No runtime semantic is
inferred from raw zeros/nulls.
"""
from __future__ import annotations
import argparse,hashlib,json,struct,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_activity_placements import RemoteCorpus
from d1_split_tar_extract import SplitHttpTar
from d1_material_decode import parse_material

TARGET='80876865'
NULL={'00000000','FFFFFFFF'}

def norm(x):return str(x).upper().removeprefix('0X').zfill(8)
def u32s(b,lo,hi):
    out=[]
    end=min(len(b),hi)
    for o in range(lo,end-(end-lo)%4,4):
        if o+4<=len(b):
            out.append({'offset':o,'offset_hex':f'0x{o:X}','u32_le':f'{struct.unpack_from("<I",b,o)[0]:08X}'})
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--member-catalog',type=Path,action='append',required=True)
    ap.add_argument('--base-url',required=True);ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args();viol=[]
    cats=load_catalogs(a.member_catalog)
    arc=SplitHttpTar([f"{a.base_url.rstrip('/')}/packages.tar.{i:03d}" for i in range(1,a.part_count+1)],retries=6,timeout=90)
    c=RemoteCorpus(arc,cats,a.runtime)
    meta=c.entry_meta(TARGET);b,src=c.payload(TARGET)
    if meta is None or b is None:raise SystemExit('target material unavailable')
    p=parse_material(b,'PS4')
    if norm(meta.get('reference'))!='80801AD7':viol.append('material class mismatch')
    if p['pixel_shader']!='8087688E':viol.append('pixel shader drift')
    if p['ps_tfx_bytecode']['bytes_hex']!='4a043400034201':viol.append('TFX drift')
    if p['ps_tfx_bytecode_constants']['count']!=1:viol.append('private constant count drift')
    if p['ps_cbuffers']['count']!=4:viol.append('ps cbuffer count drift')
    pvc=norm(p['ps_vector4_container']);vmeta=None;vpayload=None
    if pvc not in NULL:
        vmeta=c.entry_meta(pvc)
        vb,vsrc=c.payload(pvc)
        vpayload=None if vb is None else {'bytes':len(vb),'sha256':hashlib.sha256(vb).hexdigest(),'source':vsrc,'head_hex':vb[:128].hex()}
    # Preserve the exact raw ROI window and the DynamicArray headers.
    windows={
      'ps_stage_header_0x2A0_0x340':b[0x2A0:min(len(b),0x340)].hex(),
      'ps_tail_0x300_0x380':b[0x300:min(len(b),0x380)].hex(),
      'ps_tfx_array_header':b[0x2D0:0x2E0].hex(),
      'ps_private_array_header':b[0x2E0:0x2F0].hex(),
      'ps_sampler_array_header':b[0x2F0:0x300].hex(),
      'ps_cbuffer_array_header':b[0x300:0x310].hex(),
      'ps_vector4_container_field':b[0x32C:0x330].hex(),
    }
    out={
      'schema_version':1,
      'status':'D1_XUR_80876865_RAW_MATERIAL_EXACT' if not viol else 'D1_XUR_80876865_RAW_MATERIAL_VIOLATIONS',
      'material':TARGET,'metadata':meta,'payload_source':src,'payload_bytes':len(b),'payload_sha256':hashlib.sha256(b).hexdigest(),
      'pixel_shader':p['pixel_shader'],'ps_tfx':p['ps_tfx_bytecode'],
      'ps_private_constants':p['ps_tfx_bytecode_constants'],'ps_cbuffers':p['ps_cbuffers'],
      'ps_textures':p['ps_textures'],'ps_samplers':p['ps_samplers'],
      'ps_vector4_container':pvc,'ps_vector4_container_metadata':vmeta,'ps_vector4_container_payload':vpayload,
      'raw_windows':windows,'raw_dwords_0x2A0_0x380':u32s(b,0x2A0,0x380),
      'proof':{
        'ps_tfx_U4A4_program_exact':p['ps_tfx_bytecode']['bytes_hex']=='4a043400034201',
        'serialized_ps_cbuffer_vec4_count_is_4':p['ps_cbuffers']['count']==4,
        'serialized_slot4_absent':p['ps_cbuffers']['count']<=4,
        'ps_vector4_container_is_null':pvc in NULL,
        'textures_absent':p['ps_textures']['count']==0,
        'samplers_absent':p['ps_samplers']['count']==0,
        'runtime_U4A4_value_proven':False,
      },
      'consequence':'If exact, U4A[4] is not backed by the material\'s four serialized PS CBuffer vec4 rows, texture/sampler state, or a PS Vector4-container resource. Its slot-4 value must come from runtime expression/output initialization or another non-material-local runtime source.',
      'violations':viol,
      'policy':'Raw material ownership proof only. Null serialized backing does not imply a numeric runtime default.'
    }
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ['status','material','payload_bytes','pixel_shader','ps_vector4_container','proof','violations']},indent=2))
    return 0 if not viol else 2
if __name__=='__main__':raise SystemExit(main())
