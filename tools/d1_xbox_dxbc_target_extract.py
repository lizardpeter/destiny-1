#!/usr/bin/env python3
"""Extract one exact final-era D1 Xbox material/pixel-shader DXBC pair.

This is a proof-preserving bridge for cross-platform shader comparison. It dumps
raw retail bytes plus structured metadata; it does not assign PS4/Xbox homolog
identity from register shape alone.
"""
from __future__ import annotations

import argparse, hashlib, json, struct, sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_entry_extract import EntryReader
from d1_material_decode import parse_material, parse_array_header
from d1_dxbc_probe import parse_shader_tag, XBOX_MATERIAL_CLASS, XBOX_SHADER_TAG_CLASS


def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def u64(b,o):return struct.unpack_from('<Q',b,o)[0]


def vec4_array(b:bytes,o:int)->dict:
    h=parse_array_header(b,o,16)
    count=int(h['count']); off=int(h['absolute_offset'])
    end=off+count*16
    if off<0 or end>len(b): raise ValueError(f'vec4 array {o:#x} out of bounds {off:#x}:{end:#x}/{len(b):#x}')
    raw=b[off:end]
    rows=[]
    for i in range(count):
        q=raw[i*16:(i+1)*16]
        rows.append({'float4':list(struct.unpack('<4f',q)),'u32_hex':[f'{x:08X}' for x in struct.unpack('<4I',q)]})
    return {'count':count,'absolute_offset':off,'payload_hex':raw.hex(),'vectors':rows}


def dxbc_chunks(dx:bytes)->list[dict]:
    if dx[:4]!=b'DXBC': raise ValueError('not DXBC')
    total=struct.unpack_from('<I',dx,0x18)[0]; n=struct.unpack_from('<I',dx,0x1c)[0]
    offs=struct.unpack_from('<'+'I'*n,dx,0x20)
    out=[]
    for i,o in enumerate(offs):
        four=dx[o:o+4].decode('ascii','replace'); size=struct.unpack_from('<I',dx,o+4)[0]
        raw=dx[o:o+8+size]
        out.append({'index':i,'fourcc':four,'offset':o,'payload_bytes':size,'chunk_bytes':len(raw),'sha256':sha(raw)})
    if total!=len(dx): raise ValueError(f'DXBC total {total} != extracted {len(dx)}')
    return out


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('pkg',type=Path);ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--material',default='808B3A48');ap.add_argument('--expect-ps',default='808B3A51')
    ap.add_argument('--out-dir',type=Path,required=True);ap.add_argument('--report',type=Path,required=True)
    a=ap.parse_args();a.out_dir.mkdir(parents=True,exist_ok=True)
    r=EntryReader(a.pkg,a.runtime)
    if r.h['platform']!='XboxOne': raise SystemExit(f'expected XboxOne, got {r.h["platform"]}')
    by={e['tag_hash'].upper():e for e in r.entries}
    mh=a.material.upper().removeprefix('0X');me=by.get(mh)
    if not me: raise SystemExit(f'material {mh} absent')
    if me['reference'].upper()!=XBOX_MATERIAL_CLASS: raise SystemExit(f'{mh}: class {me["reference"]}')
    if not r.available(me['index']): raise SystemExit(f'{mh}: material payload unavailable')
    mb=r.entry(me['index']);m=parse_material(mb,r.h['platform'])
    ps=m['pixel_shader'].upper();expected=a.expect_ps.upper().removeprefix('0X')
    if ps!=expected: raise SystemExit(f'pixel shader changed: {ps} != {expected}')
    pe=by.get(ps)
    if not pe or pe['reference'].upper()!=XBOX_SHADER_TAG_CLASS or not r.available(pe['index']):
        raise SystemExit(f'{ps}: exact shader tag unavailable/class mismatch')
    sb=r.entry(pe['index']);sh=parse_shader_tag(sb)
    n=int(u64(sb,8));dx=sb[0x30:0x30+n]
    if len(dx)!=n: raise SystemExit('DXBC length mismatch')

    mat_path=a.out_dir/f'{mh}_material.bin'; shader_path=a.out_dir/f'{ps}_shader_tag.bin'; dx_path=a.out_dir/f'{ps}.dxbc'
    mat_path.write_bytes(mb);shader_path.write_bytes(sb);dx_path.write_bytes(dx)
    chunks=dxbc_chunks(dx)
    for c in chunks:
        o=int(c['offset']);ln=8+int(c['payload_bytes'])
        (a.out_dir/f"{ps}_{c['index']:02d}_{c['fourcc']}.bin").write_bytes(dx[o:o+ln])

    rep={
      'schema_version':1,'status':'D1_XBOX_EXACT_DXBC_TARGET_EXTRACTED',
      'package':str(a.pkg),'platform':r.h['platform'],'package_size':a.pkg.stat().st_size,
      'material':mh,'material_entry_index':me['index'],'material_reference':me['reference'].upper(),
      'material_bytes':len(mb),'material_sha256':sha(mb),
      'vertex_shader':m['vertex_shader'].upper(),'pixel_shader':ps,'pixel_shader_entry_index':pe['index'],
      'pixel_shader_reference':pe['reference'].upper(),'shader_tag_bytes':len(sb),'shader_tag_sha256':sha(sb),
      'dxbc_bytes':len(dx),'dxbc_sha256':sha(dx),'dxbc':sh['dxbc'],'chunks':chunks,
      'ps_texture_tags':m['ps_textures']['items'],'ps_sampler_count':m['ps_samplers']['count'],
      'ps_tfx_bytecode':m['ps_tfx_bytecode'],'ps_tfx_constants':vec4_array(mb,0x2E0),
      'ps_cbuffers':vec4_array(mb,0x300),'ps_vector4_container':m['ps_vector4_container'].upper(),
      'policy':'Raw retail material/shader/DXBC bytes are canonical. Cross-platform homolog status is not inferred here.'
    }
    a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(rep,indent=2)+'\n')
    print(json.dumps({k:rep[k] for k in ('status','material','vertex_shader','pixel_shader','dxbc_bytes','dxbc_sha256','ps_sampler_count','ps_vector4_container')},indent=2))
    print('DECLARATIONS',json.dumps(rep['dxbc'].get('declarations'),indent=2))
    return 0
if __name__=='__main__':raise SystemExit(main())
