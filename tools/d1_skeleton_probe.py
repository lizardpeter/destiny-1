#!/usr/bin/env python3
"""Probe final-era Destiny 1 ROI EntitySkeleton resources.

D1 entities reference outer EntityResource tags (class 0x80800861).  A skeleton
EntityResource is identified by its +0x10 ResourcePointer resolving to class
0x808006BD.  Its +0x18 ResourcePointer resolves to skeleton-info class
0x8080049A, whose D1 layout contains hierarchy and object-space transform arrays.

The class/field map is source-derived from Charm until a resident skeleton is
acquired; pointer and array mechanics are shared Tiger structures already used
by the project's binary-validated model parser.
"""
from __future__ import annotations
import argparse, json, struct, sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_entry_extract import EntryReader
from d1_entity_resource_probe import (
    ENTITY_RESOURCE_CLASS, D1_SKELETON_DISCRIMINATOR, D1_SKELETON_INFO,
    parse_resource, resource_ptr,
)
from d1_entity_model_probe import rel_array

SKELETON_INFO_SIZE=0xE0
NODE_SIZE=0x10
TRANSFORM_SIZE=0x20
INDEX_SIZE=0x02
NODE_ARRAY_OFF=0x88
DEFAULT_TRANSFORM_ARRAY_OFF=0x98
INVERSE_TRANSFORM_ARRAY_OFF=0xA8
RANGE_INDEX_ARRAY_OFF=0xB8
INNER_INDEX_ARRAY_OFF=0xC8

def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def i32(b,o): return struct.unpack_from('<i',b,o)[0]
def i16(b,o): return struct.unpack_from('<h',b,o)[0]
def f4(b,o): return list(struct.unpack_from('<4f',b,o))

def parse_array(b:bytes,o:int,elem_size:int,parser):
    count,off,_=rel_array(b,o,elem_size)
    if count==0: return {'count':0,'offset':off,'items':[]}
    if off<0 or off+count*elem_size>len(b):
        raise ValueError(f'array {o:#x} out of bounds: count={count}, offset={off:#x}, elem={elem_size:#x}, len={len(b):#x}')
    return {'count':count,'offset':off,'items':[parser(b,off+i*elem_size) for i in range(count)]}

def parse_node(b,o):
    return {'node_hash':f'{u32(b,o):08X}','parent_node_index':i32(b,o+4),
            'first_child_node_index':i32(b,o+8),'next_sibling_node_index':i32(b,o+0xC)}

def parse_transform(b,o):
    rot=f4(b,o); trans=f4(b,o+0x10)
    return {'rotation':rot,'translation':trans[:3],'scale':trans[3],'translation_scale_raw':trans}

def parse_index(b,o): return i16(b,o)

def parse_skeleton_info(b:bytes,base:int)->dict:
    if base<0 or base+SKELETON_INFO_SIZE>len(b):
        raise ValueError(f'skeleton-info struct out of bounds: {base:#x}+{SKELETON_INFO_SIZE:#x}>{len(b):#x}')
    arrays={
        'node_hierarchy':parse_array(b,base+NODE_ARRAY_OFF,NODE_SIZE,parse_node),
        'default_object_space_transforms':parse_array(b,base+DEFAULT_TRANSFORM_ARRAY_OFF,TRANSFORM_SIZE,parse_transform),
        'default_inverse_object_space_transforms':parse_array(b,base+INVERSE_TRANSFORM_ARRAY_OFF,TRANSFORM_SIZE,parse_transform),
        'range_index_map':parse_array(b,base+RANGE_INDEX_ARRAY_OFF,INDEX_SIZE,parse_index),
        'inner_index_map':parse_array(b,base+INNER_INDEX_ARRAY_OFF,INDEX_SIZE,parse_index),
    }
    n=arrays['node_hierarchy']['count']
    arrays['count_invariants']={
        'default_transform_count_matches_nodes':arrays['default_object_space_transforms']['count']==n,
        'inverse_transform_count_matches_nodes':arrays['default_inverse_object_space_transforms']['count']==n,
    }
    bones=[]
    if all(arrays['count_invariants'].values()):
        for i,node in enumerate(arrays['node_hierarchy']['items']):
            bones.append({'index':i,**node,
                          'default_object_space_transform':arrays['default_object_space_transforms']['items'][i],
                          'default_inverse_object_space_transform':arrays['default_inverse_object_space_transforms']['items'][i]})
    return {'base_offset':base,'source_schema_class':f'{D1_SKELETON_INFO:08X}',**arrays,'bones':bones}

def parse_skeleton_resource(b:bytes)->dict:
    outer=parse_resource(b)
    if outer['unk10'].get('class_hash')!=f'{D1_SKELETON_DISCRIMINATOR:08X}':
        raise ValueError(f'not a D1 skeleton EntityResource: discriminator={outer["unk10"].get("class_hash")}')
    p=outer['unk18']
    if p.get('class_hash')!=f'{D1_SKELETON_INFO:08X}':
        raise ValueError(f'unexpected skeleton-info class: {p.get("class_hash")}')
    base=p['target_offset']
    return {'entity_resource':outer,'skeleton_info':parse_skeleton_info(b,base)}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('pkg',type=Path); ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--tag-hash',action='append')
    ap.add_argument('-o','--output',type=Path)
    a=ap.parse_args(); r=EntryReader(a.pkg,a.runtime)
    wanted={x.upper().removeprefix('0X') for x in a.tag_hash or []}
    resources=[]
    for e in r.entries:
        if e['type']!=16 or e['subtype']!=0 or e['reference'].upper()!=ENTITY_RESOURCE_CLASS: continue
        if wanted and e['tag_hash'].upper() not in wanted: continue
        row={'tag_hash':e['tag_hash'],'entry_index':e['index'],'size':e['file_size'],'available':r.available(e['index'])}
        if row['available']:
            try:
                outer=parse_resource(r.entry(e['index']),r.h['platform']); row['semantic_role']=outer['semantic_role']
                if outer['semantic_role']=='entity_skeleton': row.update(parse_skeleton_resource(r.entry(e['index'])))
            except Exception as ex: row['error']=repr(ex)
        resources.append(row)
    skeletons=[x for x in resources if x.get('semantic_role')=='entity_skeleton']
    rep={'package':str(r.pkg),'platform':r.h['platform'],'outer_class_hash':ENTITY_RESOURCE_CLASS,
         'skeleton_discriminator_class':f'{D1_SKELETON_DISCRIMINATOR:08X}',
         'skeleton_info_class':f'{D1_SKELETON_INFO:08X}',
         'entity_resources_scanned':len(resources),'resident_resources':sum(x['available'] for x in resources),
         'resident_skeleton_resources':len(skeletons),'resources':resources}
    text=json.dumps(rep,indent=2)
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(text+'\n'); print('wrote',a.output)
    else: print(text)
if __name__=='__main__':main()
