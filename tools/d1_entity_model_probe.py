#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, struct, sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_entry_extract import EntryReader

D1_ENTITY_MODEL_CLASS='80801AB5'
MESH_SIZE=0xA0
PART_SIZE=0x24


def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def s16(b,o): return struct.unpack_from('<h',b,o)[0]
def u64s(b,o): return struct.unpack_from('<q',b,o)[0]
def f2(b,o): return list(struct.unpack_from('<2f',b,o))
def f4(b,o): return list(struct.unpack_from('<4f',b,o))

def rel_array(b, o, elem_size):
    count=u32(b,o)
    rel=u64s(b,o+8)
    # Charm DynamicArray<T>: RelativePointer base is pointer field position o+8;
    # AddExtraOffset(0x10).
    abs_off=(o+8)+rel+0x10
    return count,abs_off,elem_size

def parse_part(b,o):
    material=u32(b,o)
    variant=s16(b,o+4)
    primitive=s16(b,o+6)
    index_offset=u32(b,o+8)
    index_count=u32(b,o+0x0c)
    unk10=u32(b,o+0x10)
    unk14=u32(b,o+0x14)
    external_identifier=s16(b,o+0x18)
    unk1a=b[o+0x1a]
    unk1b=b[o+0x1b]
    flags_d1=s16(b,o+0x1c)
    dye=b[o+0x1e]
    lod=b[o+0x1f]
    unk20=b[o+0x20]
    lod_run=b[o+0x21]
    tail=b[o+0x22:o+0x24]
    return {
        'material':f'{material:08X}','variant_shader_index':variant,'primitive_type':primitive,
        'index_offset':index_offset,'index_count':index_count,'unk10':unk10,'unk14':unk14,
        'external_identifier':external_identifier,'unk1a':unk1a,'unk1b':unk1b,
        'flags_d1':flags_d1,'gear_dye_change_color_index':dye,'lod':lod,
        'unk20':unk20,'lod_run':lod_run,'tail_hex':tail.hex(),
    }

def parse_mesh(b,o,platform):
    v1,v2,weights,unk,indices=struct.unpack_from('<5I',b,o+0x30)
    part_count,part_off,_=rel_array(b,o+0x48,PART_SIZE)
    if part_off+part_count*PART_SIZE > len(b):
        raise ValueError(f'parts array out of bounds: {part_off:#x}+{part_count}*{PART_SIZE:#x} > {len(b):#x}')
    parts=[parse_part(b,part_off+i*PART_SIZE) for i in range(part_count)]
    d={
        'offset':o,'model_scale':f4(b,o),'model_translation':f4(b,o+0x10),
        'texcoord_scale':f2(b,o+0x20),'texcoord_translation':f2(b,o+0x28),
        'vertices1':f'{v1:08X}','vertices2':f'{v2:08X}','old_weights':f'{weights:08X}',
        'unk_resource':f'{unk:08X}','indices':f'{indices:08X}','zero_or_unknown_44':u32(b,o+0x44),
        'part_count':part_count,'parts_offset':part_off,'parts':parts,
    }
    # Charm source models D1 as 30 shorts at 0x58. Real XboxOne evidence in
    # xboxone_arch_cabal_0059_1 instead has 20 sensible stage offsets at 0x58,
    # then a fixed 20-char NUL-terminated code at 0x80, then 12 zero bytes.
    if platform=='XboxOne':
        d['stage_part_offsets']=list(struct.unpack_from('<20h',b,o+0x58))
        raw=b[o+0x80:o+0x94]
        d['stage_code_raw_hex']=raw.hex()
        d['stage_code']=raw.split(b'\0',1)[0].decode('ascii','replace')
        d['tail_94_a0_hex']=b[o+0x94:o+0xA0].hex()
    else:
        d['stage_part_offsets_source_derived']=list(struct.unpack_from('<30h',b,o+0x58))
        d['tail_94_a0_hex']=b[o+0x94:o+0xA0].hex()
    return d

def parse_model(b,platform):
    if len(b)<0x44: raise ValueError('entry too small for D1 SEntityModel header')
    mesh_count,mesh_off,_=rel_array(b,0x10,MESH_SIZE)
    if mesh_off+mesh_count*MESH_SIZE > len(b):
        raise ValueError(f'mesh array out of bounds: {mesh_off:#x}+{mesh_count}*{MESH_SIZE:#x} > {len(b):#x}')
    return {
        'declared_file_size':struct.unpack_from('<Q',b,0)[0],
        'actual_file_size':len(b),'mesh_count':mesh_count,'meshes_offset':mesh_off,
        'unk20':f4(b,0x20),'unk30':f'{struct.unpack_from("<Q",b,0x30)[0]:016X}',
        'unk_flags38':f'{struct.unpack_from("<Q",b,0x38)[0]:016X}',
        'meshes':[parse_mesh(b,mesh_off+i*MESH_SIZE,platform) for i in range(mesh_count)],
    }

def hash_entry_map(r): return {e['tag_hash'].upper():e for e in r.entries}

def annotate_resources(r,m):
    by=hash_entry_map(r)
    for mesh in m['meshes']:
        res={}
        for field in ('vertices1','vertices2','old_weights','indices'):
            h=mesh[field]
            if h=='FFFFFFFF':
                res[field]={'tag_hash':h,'present':False}
                continue
            e=by.get(h)
            if not e:
                res[field]={'tag_hash':h,'present':False}
                continue
            rr={'tag_hash':h,'present':True,'entry_index':e['index'],'type':e['type'],'subtype':e['subtype'],
                'size':e['file_size'],'reference':e['reference'],'available':r.available(e['index'])}
            linked=by.get(e['reference'].upper())
            if linked:
                rr['payload_entry_index']=linked['index']; rr['payload_size']=linked['file_size']; rr['payload_available']=r.available(linked['index'])
            res[field]=rr
        mesh['resources']=res

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('pkg',type=Path); ap.add_argument('--runtime',type=Path,required=True)
    g=ap.add_mutually_exclusive_group(required=False); g.add_argument('--entry',type=int); g.add_argument('--tag-hash')
    ap.add_argument('--all-resident',action='store_true'); ap.add_argument('-o','--output',type=Path)
    a=ap.parse_args(); r=EntryReader(a.pkg,a.runtime)
    candidates=[]
    for e in r.entries:
        if e['type']==16 and e['subtype']==0 and e['reference'].upper()==D1_ENTITY_MODEL_CLASS:
            if a.entry is not None and e['index']!=a.entry: continue
            if a.tag_hash and e['tag_hash'].upper()!=a.tag_hash.upper().removeprefix('0X'): continue
            if a.all_resident and not r.available(e['index']): continue
            candidates.append(e)
    if not candidates: raise SystemExit('no matching resident s_entity_model entries')
    out=[]
    for e in candidates:
        if not r.available(e['index']):
            out.append({'entry_index':e['index'],'tag_hash':e['tag_hash'],'available':False}); continue
        b=r.entry(e['index']); m=parse_model(b,r.h['platform']); annotate_resources(r,m)
        out.append({'entry_index':e['index'],'tag_hash':e['tag_hash'],'class_hash':e['reference'],'available':True,**m})
    rep={'package':str(r.pkg),'platform':r.h['platform'],'class_hash':D1_ENTITY_MODEL_CLASS,'models':out}
    text=json.dumps(rep,indent=2)
    if a.output: a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(text+'\n'); print('wrote',a.output)
    else: print(text)

if __name__=='__main__': main()
