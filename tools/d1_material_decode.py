#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,struct,sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_entry_extract import EntryReader, decode_known
from d1_entity_model_probe import rel_array

PS4_MATERIAL_CLASS='80801AD7'
XBOX_MATERIAL_CLASS='80801C32'


def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def h32(b,o): return f'{u32(b,o):08X}'

def parse_texture_array(b,o):
    count,off,_=rel_array(b,o,8)
    if off<0 or off+count*8>len(b):
        raise ValueError(f'texture array {o:#x} out of bounds: count={count}, off={off:#x}, len={len(b):#x}')
    return {'count':count,'offset':off,'items':[{'texture_index':u32(b,off+i*8),'texture':h32(b,off+i*8+4)} for i in range(count)]}

def parse_array_header(b,o,elem_size=None):
    count,off,_=rel_array(b,o,elem_size or 1)
    return {'count':count,'offset':off,'elem_size':elem_size}

def parse_material(b,platform):
    if len(b)<0x330: raise ValueError('material entry too small for D1 ROI semantic fields')
    return {
      'declared_file_size':struct.unpack_from('<Q',b,0)[0], 'actual_file_size':len(b),
      'unk08':h32(b,0x08),'unk0c':h32(b,0x0c),'unk10':h32(b,0x10),
      'vertex_shader':h32(b,0x28),
      'vs_textures':parse_texture_array(b,0x38),
      'vs_tfx_bytecode':parse_array_header(b,0x50,1),
      'vs_samplers':parse_array_header(b,0x70,16),
      'vs_vector4_container':h32(b,0xAC),
      'pixel_shader':h32(b,0x2A8),
      'ps_textures':parse_texture_array(b,0x2B8),
      'ps_tfx_bytecode':parse_array_header(b,0x2D0,1),
      'ps_samplers':parse_array_header(b,0x2F0,16),
      'ps_vector4_container':h32(b,0x32C),
    }

def annotate(r, d):
    by={e['tag_hash'].upper():e for e in r.entries}
    for key in ('vertex_shader','vs_vector4_container','pixel_shader','ps_vector4_container'):
        h=d[key];e=by.get(h)
        d[key+'_entry']=None if not e else {'entry_index':e['index'],'type':e['type'],'subtype':e['subtype'],'reference':e['reference'],'size':e['file_size'],'available':r.available(e['index'])}
    for stage in ('vs_textures','ps_textures'):
        for item in d[stage]['items']:
            e=by.get(item['texture'])
            if not e:
                item['entry']=None;continue
            q={'entry_index':e['index'],'type':e['type'],'subtype':e['subtype'],'reference':e['reference'],'size':e['file_size'],'available':r.available(e['index'])}
            if r.available(e['index']):
                hdr=decode_known(e,r.entry(e['index']),r.h['platform'])
                for k in ('kind','dxgi_format','tile_mode','surface_format','width','height','depth','array_size','flags1','flags2','flags3'):
                    if k in hdr:q[k]=hdr[k]
            pe=by.get(e['reference'].upper())
            if pe:q['payload']={'tag_hash':pe['tag_hash'],'entry_index':pe['index'],'size':pe['file_size'],'available':r.available(pe['index'])}
            item['entry']=q

def main():
    ap=argparse.ArgumentParser();ap.add_argument('pkg',type=Path);ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('--tag-hash',action='append',required=True);ap.add_argument('-o','--output',type=Path)
    a=ap.parse_args();r=EntryReader(a.pkg,a.runtime);by={e['tag_hash'].upper():e for e in r.entries};out=[]
    expected=PS4_MATERIAL_CLASS if r.h['platform']=='PS4' else XBOX_MATERIAL_CLASS
    for raw in a.tag_hash:
        h=raw.upper().removeprefix('0X');e=by.get(h)
        if not e:out.append({'tag_hash':h,'present':False});continue
        if not r.available(e['index']):out.append({'tag_hash':h,'present':True,'available':False,'class_hash':e['reference']});continue
        b=r.entry(e['index']);d=parse_material(b,r.h['platform']);annotate(r,d)
        out.append({'tag_hash':h,'entry_index':e['index'],'class_hash':e['reference'],'expected_platform_material_class':expected,'available':True,**d})
    rep={'package':str(r.pkg),'platform':r.h['platform'],'materials':out};text=json.dumps(rep,indent=2)
    if a.output:a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(text+'\n');print('wrote',a.output)
    else:print(text)
if __name__=='__main__':main()
