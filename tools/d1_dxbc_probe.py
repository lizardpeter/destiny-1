#!/usr/bin/env python3
"""Parse D1 Xbox One inline DXBC shader tags and correlate material bindings.

For final-era D1 Xbox One, observed material tags reference structured shader tags
(class 0x80801B7C). The tag begins with a 0x30-byte SShaderBytecode-style header
and stores a complete DXBC container inline at +0x30. This tool parses DXBC
chunks, signature semantics, and early resource declaration tokens, then compares
pixel-shader texture registers with STextureTag.TextureIndex values from the
material.
"""
from __future__ import annotations
import argparse, json, struct, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from d1_entry_extract import EntryReader
from d1_material_decode import parse_material, parse_array_header
from d1_vector_container_probe import xbox_count_from_metadata_size, parse_xbox_vector_container

XBOX_MATERIAL_CLASS = '80801C32'
XBOX_SHADER_TAG_CLASS = '80801B7C'
XBOX_VECTOR_CONTAINER_CLASS = '80801AA5'

RESOURCE_TYPES = {
    0x04001858: 'Texture2D',
    0x04002858: 'Texture3D',
    0x04003058: 'TextureCube',
}
SAMPLER = 0x0300005A
CBUFFERS = {0x04000059, 0x04000859}
BUFFER = 0x04000858
STOP_TOKENS = {0x02000068, 0x0300005F, 0x03001062, 0x03000065}

SEMANTIC_NAMES = {
    'POSITION','TEXCOORD','NORMAL','BINORMAL','TANGENT','BLENDINDICES','BLENDWEIGHT','COLOR',
    'SV_POSITION','SV_isFrontFace','SV_VertexID','SV_VERTEXID','SV_InstanceID','SV_TARGET','SV_Target'
}

def u32(b, o): return struct.unpack_from('<I', b, o)[0]
def u64(b, o): return struct.unpack_from('<Q', b, o)[0]

def parse_signature(dx: bytes, chunk_off: int) -> list[dict]:
    size = u32(dx, chunk_off + 4)
    data_off = chunk_off + 8
    if data_off + size > len(dx) or size < 8:
        return []
    count = u32(dx, data_off)
    out=[]
    for i in range(count):
        o=data_off+8+i*0x18
        if o+0x18>data_off+size: break
        name_rel, sem_idx, sysv, comp, reg = struct.unpack_from('<5I',dx,o)
        mask=dx[o+0x14]; rw=dx[o+0x15]
        no=data_off+name_rel
        if no<0 or no>=len(dx): name=''
        else:
            end=dx.find(b'\0',no, min(len(dx),data_off+size))
            if end<0:end=min(len(dx),data_off+size)
            name=dx[no:end].decode('ascii','replace')
        out.append({'semantic':name,'semantic_index':sem_idx,'system_value_type':sysv,
                    'component_type':comp,'register':reg,'mask':mask,'read_write_mask':rw})
    return out

def parse_declarations(dx: bytes, chunk_off: int) -> dict:
    size=u32(dx,chunk_off+4); data=dx[chunk_off+8:chunk_off+8+size]
    if len(data)<8 or len(data)%4: return {'textures':[],'samplers':[],'cbuffers':[],'buffers':[]}
    words=struct.unpack_from('<'+'I'*(len(data)//4),data)
    out={'shader_version_token':f'{words[0]:08X}','declared_word_count':words[1],
         'textures':[],'samplers':[],'cbuffers':[],'buffers':[]}
    i=2
    while i<len(words):
        w=words[i]
        if w in STOP_TOKENS:
            out['declaration_stop_token']=f'{w:08X}'
            break
        if w in RESOURCE_TYPES and i+3<len(words):
            out['textures'].append({'resource_type':RESOURCE_TYPES[w],'register':words[i+2]})
            i += 4; continue
        if w==SAMPLER and i+2<len(words):
            out['samplers'].append({'register':words[i+2]})
            i += 3; continue
        if w in CBUFFERS and i+3<len(words):
            out['cbuffers'].append({'register':words[i+2],'vec4_count':words[i+3]})
            i += 4; continue
        if w==BUFFER and i+3<len(words):
            out['buffers'].append({'register':words[i+2]})
            i += 4; continue
        i += 1
    return out

def parse_dxbc(dx: bytes) -> dict:
    if len(dx)<0x20 or dx[:4]!=b'DXBC': raise ValueError('not a DXBC container')
    total=u32(dx,0x18); n=u32(dx,0x1c)
    if total>len(dx): raise ValueError(f'DXBC total size {total} > available {len(dx)}')
    if 0x20+n*4>len(dx): raise ValueError('DXBC chunk table truncated')
    offsets=struct.unpack_from('<'+'I'*n,dx,0x20)
    chunks=[]; shex=None
    for off in offsets:
        if off+8>len(dx): raise ValueError(f'chunk offset {off:#x} out of bounds')
        four=dx[off:off+4].decode('ascii','replace'); size=u32(dx,off+4)
        item={'fourcc':four,'offset':off,'size':size}
        if four in ('ISGN','ISG1'): item['signatures']=parse_signature(dx,off)
        if four in ('OSGN','OSG1','OSG5'): item['signatures']=parse_signature(dx,off)
        if four in ('SHEX','SHDR'): shex=off
        chunks.append(item)
    return {'total_size':total,'chunk_count':n,'chunks':chunks,
            'declarations':parse_declarations(dx,shex) if shex is not None else None}

def parse_shader_tag(b: bytes) -> dict:
    if len(b)<0x30: raise ValueError('shader tag shorter than 0x30')
    declared_file=u64(b,0); bytecode_size=u64(b,8)
    if 0x30+bytecode_size>len(b): raise ValueError('inline DXBC extends beyond shader tag')
    dx=b[0x30:0x30+bytecode_size]
    return {'declared_file_size':declared_file,'actual_file_size':len(b),'bytecode_size':bytecode_size,
            'header_10_2f_hex':b[0x10:0x30].hex(),'dxbc':parse_dxbc(dx)}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('pkg',type=Path); ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--material',action='append',help='material TagHash; omit with --all-resident-materials')
    ap.add_argument('--all-resident-materials',action='store_true')
    ap.add_argument('-o','--output',type=Path)
    a=ap.parse_args(); r=EntryReader(a.pkg,a.runtime)
    by={e['tag_hash'].upper():e for e in r.entries}
    if r.h['platform']!='XboxOne': raise SystemExit('DXBC material correlation currently targets XboxOne')
    if a.all_resident_materials:
        mats=[e for e in r.entries if e['type']==16 and e['subtype']==0 and e['reference'].upper()==XBOX_MATERIAL_CLASS and r.available(e['index'])]
    elif a.material:
        mats=[]
        for h in a.material:
            e=by.get(h.upper().removeprefix('0X'))
            if e: mats.append(e)
    else: raise SystemExit('provide --material or --all-resident-materials')
    rows=[]; summary={'resident_materials_selected':len(mats),'pixel_shader_unavailable':0,'pixel_shader_compared':0,
                     'texture_register_exact':0,'texture_register_mismatch':0,
                     'sampler_count_exact':0,'sampler_count_mismatch':0,
                     'b0_compared':0,'b0_count_exact':0,'b0_count_mismatch':0}
    for e in mats:
        if not r.available(e['index']): continue
        m=parse_material(r.entry(e['index']),r.h['platform'])
        pe=by.get(m['pixel_shader'].upper())
        # In the ROI material layout, PS_CBuffers is the DynamicArray immediately
        # following PS_Samplers at +0x300. PSVector4Container is at +0x32C.
        inline_ps_cbuffers=parse_array_header(r.entry(e['index']),0x300,16)
        row={'material_tag_hash':e['tag_hash'],'material_entry_index':e['index'],'pixel_shader':m['pixel_shader'],
             'material_texture_indices':[x['texture_index'] for x in m['ps_textures']['items']],
             'material_sampler_count':m['ps_samplers']['count'],
             'inline_ps_cbuffer_count':inline_ps_cbuffers['count'],
             'ps_vector4_container':m['ps_vector4_container']}
        ve=by.get(m['ps_vector4_container'].upper())
        if ve and ve['reference'].upper()==XBOX_VECTOR_CONTAINER_CLASS:
            row['ps_vector4_container_entry']={'tag_hash':ve['tag_hash'],'entry_index':ve['index'],'size':ve['file_size'],
                'available':r.available(ve['index']),'metadata_vector_count':xbox_count_from_metadata_size(ve['file_size'])}
            if r.available(ve['index']):
                try: row['ps_vector4_container_entry']['decoded']=parse_xbox_vector_container(r.entry(ve['index']))
                except Exception as ex: row['ps_vector4_container_entry']['decode_error']=repr(ex)
        if not pe or not r.available(pe['index']):
            row['pixel_shader_available']=False; rows.append(row); summary['pixel_shader_unavailable']+=1; continue
        row['pixel_shader_available']=True; row['pixel_shader_entry_index']=pe['index']; row['pixel_shader_class']=pe['reference']
        if pe['reference'].upper()!=XBOX_SHADER_TAG_CLASS:
            row['shader_parse_error']=f'unexpected shader class {pe["reference"]}'; rows.append(row); continue
        try: sh=parse_shader_tag(r.entry(pe['index']))
        except Exception as ex:
            row['shader_parse_error']=repr(ex); rows.append(row); continue
        row['shader']=sh
        dec=sh['dxbc']['declarations'] or {'textures':[],'samplers':[],'cbuffers':[],'buffers':[]}
        shader_tex=[x['register'] for x in dec['textures']]
        shader_samp=[x['register'] for x in dec['samplers']]
        row['shader_texture_registers']=shader_tex; row['shader_sampler_registers']=shader_samp
        row['texture_register_exact']=sorted(row['material_texture_indices'])==sorted(shader_tex)
        row['sampler_count_exact']=row['material_sampler_count']==len(shader_samp)
        row['sampler_registers_contiguous_s1']=shader_samp==list(range(1,len(shader_samp)+1))
        # Pixel-stage material-owned constant data maps to DXBC cbuffer b0.
        # Prefer the external PSVector4Container when present; otherwise the
        # material's inline PS_CBuffers array supplies b0. Other cbuffer
        # registers (observed b12/b13) are separate/global inputs.
        b0=next((x for x in dec['cbuffers'] if x['register']==0),None)
        ext=row.get('ps_vector4_container_entry')
        if ext:
            material_b0_count=ext.get('metadata_vector_count'); b0_source='external_ps_vector4_container'
        else:
            material_b0_count=row['inline_ps_cbuffer_count']; b0_source='inline_ps_cbuffers'
        row['shader_b0_vec4_count']=None if b0 is None else b0['vec4_count']
        row['material_b0_source']=b0_source; row['material_b0_vec4_count']=material_b0_count
        row['non_b0_cbuffers']=[x for x in dec['cbuffers'] if x['register']!=0]
        row['b0_count_exact']=(b0 is None and material_b0_count==0) or (b0 is not None and material_b0_count==b0['vec4_count'])
        summary['pixel_shader_compared']+=1
        summary['texture_register_exact' if row['texture_register_exact'] else 'texture_register_mismatch']+=1
        summary['sampler_count_exact' if row['sampler_count_exact'] else 'sampler_count_mismatch']+=1
        summary['b0_compared']+=1
        summary['b0_count_exact' if row['b0_count_exact'] else 'b0_count_mismatch']+=1
        rows.append(row)
    rep={'package':str(r.pkg),'platform':r.h['platform'],'summary':summary,'materials':rows}
    text=json.dumps(rep,indent=2)
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(text+'\n'); print('wrote',a.output)
    else: print(text)
if __name__=='__main__': main()
