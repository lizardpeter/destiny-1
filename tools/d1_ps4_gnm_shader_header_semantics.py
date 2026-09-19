#!/usr/bin/env python3
"""Decode standard PS4 GNM shader-header semantic tables from exact D1 headers.

D1 PS4 shader FileEntry payloads are structurally consistent with the public
GnmVsShader / GnmPsShader layouts.  This decoder promotes the layout only when
the table counts, native OrbShdr usage count, and exact payload byte length are
self-consistent.

Public cross-check:
  https://ps4-opengnm.github.io/opengnm/reference/shaderbinary/
  https://ps4-opengnm.github.io/opengnm/reference/shader/

No semantic *meaning* (TEXCOORD/NORMAL/etc.) is assigned to an 8-bit semantic ID.
"""
from __future__ import annotations
import argparse,json,struct
from pathlib import Path

VS_FIXED=0x28
PS_FIXED=0x3C

def align4(x:int)->int: return (x+3)&~3

def common(b:bytes)->dict:
    if len(b)<8: raise ValueError('shader header shorter than GnmShaderCommonData')
    w=struct.unpack_from('<I',b,0)[0]
    return {
        'shader_size_low23':w & 0x7FFFFF,
        'is_using_srt':bool((w>>23)&1),
        'num_input_usage_slots_common':(w>>24)&0xFF,
        'embedded_constant_buffer_dqwords':struct.unpack_from('<H',b,4)[0],
        'scratch_size_per_thread_dwords':struct.unpack_from('<H',b,6)[0],
        'common_raw_hex':b[:8].hex(),
    }

def usage_slots(b:bytes,off:int,n:int)->list[dict]:
    end=off+n*4
    if end>len(b): raise ValueError('input usage slots out of bounds')
    out=[]
    for i in range(n):
        usage,api,reg,flags=struct.unpack_from('<4B',b,off+i*4)
        out.append({'index':i,'usage_type':usage,'api_slot':api,'start_register':reg,
                    'flags':flags,'raw_hex':b[off+i*4:off+i*4+4].hex()})
    return out

def vertex_inputs(b:bytes,off:int,n:int)->list[dict]:
    end=off+n*4
    if end>len(b): raise ValueError('vertex input semantic table out of bounds')
    return [{'index':i,'semantic':b[off+i*4],'vgpr':b[off+i*4+1],
             'size_in_elements':b[off+i*4+2],'reserved':b[off+i*4+3],
             'raw_hex':b[off+i*4:off+i*4+4].hex()} for i in range(n)]

def vertex_exports(b:bytes,off:int,n:int)->list[dict]:
    end=off+n*2
    if end>len(b): raise ValueError('vertex export semantic table out of bounds')
    out=[]
    for i in range(n):
        sem=b[off+i*2]; q=b[off+i*2+1]
        out.append({'index':i,'semantic':sem,'out_index':q&0x1F,
                    'reserved_bit5':(q>>5)&1,'export_f16':(q>>6)&3,
                    'raw_hex':b[off+i*2:off+i*2+2].hex()})
    return out

def pixel_inputs(b:bytes,off:int,n:int)->list[dict]:
    end=off+n*2
    if end>len(b): raise ValueError('pixel input semantic table out of bounds')
    out=[]
    for i in range(n):
        w=struct.unpack_from('<H',b,off+i*2)[0]
        out.append({'attr_index':i,'semantic':w&0xFF,'default_value':(w>>8)&3,
                    'is_flat_shaded':bool((w>>10)&1),'is_linear':bool((w>>11)&1),
                    'is_custom':bool((w>>12)&1),'reserved_high3':(w>>13)&7,
                    'raw_hex':b[off+i*2:off+i*2+2].hex()})
    return out

def decode(header:bytes,stage:str,orb_usage_count:int)->dict:
    stage=str(stage)
    c=common(header)
    violations=[]
    if c['num_input_usage_slots_common'] != orb_usage_count:
        violations.append(
            f"common usage count {c['num_input_usage_slots_common']} != OrbShdr {orb_usage_count}")
    if stage=='PixelShader':
        if len(header)<PS_FIXED: raise ValueError('PS header shorter than 0x3c')
        nsem=header[0x38]
        uoff=PS_FIXED
        soff=uoff+orb_usage_count*4
        expected=align4(soff+nsem*2)
        us=usage_slots(header,uoff,orb_usage_count)
        ps=pixel_inputs(header,soff,nsem)
        if expected!=len(header):
            violations.append(f'PS calculated size {expected:#x} != payload {len(header):#x}')
        if any(x['reserved_high3'] for x in ps):
            violations.append('PS semantic reserved bits are nonzero')
        return {'schema':'d1_ps4_gnm_shader_header/v1','stage':stage,'header_bytes':len(header),
                'common':c,'num_input_semantics':nsem,'input_usage_slots':us,
                'pixel_input_semantics':ps,'calculated_size':expected,
                'trailing_padding_hex':header[soff+nsem*2:].hex(),'violations':violations,
                'status':'D1_PS4_GNM_SHADER_HEADER_EXACT' if not violations else 'D1_PS4_GNM_SHADER_HEADER_PARTIAL'}
    if stage=='VertexShader':
        if len(header)<VS_FIXED: raise ValueError('VS header shorter than 0x28')
        nin=header[0x24];nout=header[0x25];gsmode=header[0x26];fetch=header[0x27]
        uoff=VS_FIXED
        ioff=uoff+orb_usage_count*4
        eoff=ioff+nin*4
        expected=align4(eoff+nout*2)
        us=usage_slots(header,uoff,orb_usage_count)
        vi=vertex_inputs(header,ioff,nin);ve=vertex_exports(header,eoff,nout)
        if expected!=len(header):
            violations.append(f'VS calculated size {expected:#x} != payload {len(header):#x}')
        if any(x['reserved'] for x in vi): violations.append('VS input semantic reserved byte nonzero')
        if any(x['reserved_bit5'] for x in ve): violations.append('VS export semantic reserved bit nonzero')
        sems=[x['semantic'] for x in ve]
        if len(sems)!=len(set(sems)): violations.append('duplicate VS export semantic IDs')
        outs=[x['out_index'] for x in ve]
        if len(outs)!=len(set(outs)): violations.append('duplicate VS export out indices')
        return {'schema':'d1_ps4_gnm_shader_header/v1','stage':stage,'header_bytes':len(header),
                'common':c,'num_input_semantics':nin,'num_export_semantics':nout,
                'gs_mode_or_num_input_semantics_cs':gsmode,'fetch_control':fetch,
                'input_usage_slots':us,'vertex_input_semantics':vi,'vertex_export_semantics':ve,
                'calculated_size':expected,'trailing_padding_hex':header[eoff+nout*2:].hex(),
                'violations':violations,
                'status':'D1_PS4_GNM_SHADER_HEADER_EXACT' if not violations else 'D1_PS4_GNM_SHADER_HEADER_PARTIAL'}
    raise ValueError(f'unsupported GNM semantic-table stage {stage!r}')

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('header',type=Path)
    ap.add_argument('--stage',choices=('PixelShader','VertexShader'),required=True)
    ap.add_argument('--orb-usage-count',type=int,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args();d=decode(a.header.read_bytes(),a.stage,a.orb_usage_count)
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(d,indent=2)+'\n')
    print(json.dumps(d,indent=2))
    return 0 if d['status']=='D1_PS4_GNM_SHADER_HEADER_EXACT' else 2

if __name__=='__main__': raise SystemExit(main())
