#!/usr/bin/env python3
"""Probe final-era D1 ROI EntityResource containers (class 0x80800861).

The outer structured tag class is 0x80800861 in Rise of Iron. This value is
NOT the ROI s_pattern_component class (ROI s_pattern_component is 0x80800715).
The first three fields after FileSize are ResourcePointer values. A Tiger
ResourcePointer stores a signed relative qword; the pointed structure's class
hash is serialized four bytes immediately before the pointed payload.
"""
from __future__ import annotations
import argparse, collections, json, struct, sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_entry_extract import EntryReader

ENTITY_RESOURCE_CLASS='80800861'
D1_MODEL_DISCRIMINATOR=0x80801A80
D1_MODEL_PARENT=0x80801A9C
D1_SKELETON_DISCRIMINATOR=0x808006BD
D1_SKELETON_INFO=0x8080049A
D1_PHYSICS_DISCRIMINATOR=0x80801A79
D1_PHYSICS_PARENT=0x80801BF6
D1_CHILDREN_DISCRIMINATOR=0x80802663
D1_CHILDREN_DATA=0x80802708
# Entity.Load generic-name branch: D2Class_357C8080 maps in D1 to E3138080.
D1_GENERIC_NAME_DISCRIMINATOR=0x808013E3
D1_GENERIC_NAME_PARENT=0x80801308       # D2Class_18808080 -> D1 08138080
D1_GENERIC_NAME_TAG_CLASS=0x808013F3    # D2Class_4D7E8080 -> D1 F3138080
# Entity.Load specific-name branch: D2Class_DA5E8080 maps in D1 to 9B208080.
D1_SPECIFIC_NAME_DISCRIMINATOR=0x8080209B
D1_SPECIFIC_NAME_PARENT=0x80802089      # D2Class_DB5E8080 -> D1 89208080
# Charm pinned D1 ROI ActivityStructsROI.cs:
# SBC078080 (BC078080) selects SA7058080 (A7058080), whose +0x68 field is
# Tag<SD9128080>. SD9128080 is the scripted-entity table schema.
D1_SCRIPTED_ENTITY_DISCRIMINATOR=0x808007BC
D1_SCRIPTED_ENTITY_PARENT=0x808005A7
D1_SCRIPTED_ENTITY_TABLE_CLASS=0x808012D9
D1_SCRIPTED_ENTITY_TABLE_OFFSET=0x68
# Charm pinned D1 ROI EntityStructs.cs + Audio/Dialogue.cs:
# SB9268080 (B9268080) selects SDA288080 (DA288080), whose +0x68 field is
# Entity? Unk68. DialogueD1 follows this entity and then walks its EntityResources
# to collect Wwise dialogue. This is a dialogue/audio ownership edge, not a
# generic runtime-spawn edge.
D1_DIALOGUE_ENTITY_DISCRIMINATOR=0x808026B9
D1_DIALOGUE_ENTITY_PARENT=0x808028DA
D1_DIALOGUE_ENTITY_OFFSET=0x68

KNOWN={
 D1_MODEL_DISCRIMINATOR:'entity_model_discriminator',D1_MODEL_PARENT:'entity_model_parent',
 D1_SKELETON_DISCRIMINATOR:'entity_skeleton_discriminator',D1_SKELETON_INFO:'entity_skeleton_info',
 D1_PHYSICS_DISCRIMINATOR:'entity_physics_discriminator',D1_PHYSICS_PARENT:'entity_physics_parent',
 D1_CHILDREN_DISCRIMINATOR:'entity_children_discriminator',D1_CHILDREN_DATA:'entity_children_data',
 D1_GENERIC_NAME_DISCRIMINATOR:'entity_generic_name_discriminator',D1_GENERIC_NAME_PARENT:'entity_generic_name_parent',
 D1_GENERIC_NAME_TAG_CLASS:'entity_generic_name_tag',
 D1_SPECIFIC_NAME_DISCRIMINATOR:'entity_specific_name_discriminator',D1_SPECIFIC_NAME_PARENT:'entity_specific_name_parent',
 D1_SCRIPTED_ENTITY_DISCRIMINATOR:'scripted_entity_table_discriminator',
 D1_SCRIPTED_ENTITY_PARENT:'scripted_entity_table_parent_SA7058080',
 D1_SCRIPTED_ENTITY_TABLE_CLASS:'scripted_entity_table_SD9128080',
 D1_DIALOGUE_ENTITY_DISCRIMINATOR:'dialogue_entity_discriminator_SB9268080',
 D1_DIALOGUE_ENTITY_PARENT:'dialogue_entity_parent_SDA288080',
}

def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def q64(b,o): return struct.unpack_from('<q',b,o)[0]

def resource_ptr(b,o):
    if o+8>len(b): return {'field_offset':o,'error':'field out of bounds'}
    rel=q64(b,o)
    if rel==0: return {'field_offset':o,'relative':0,'null':True}
    target=o+rel
    d={'field_offset':o,'relative':rel,'target_offset':target,'null':False}
    if target<4 or target>len(b): d['error']='target out of bounds'; return d
    cls=u32(b,target-4);d['class_hash']=f'{cls:08X}';d['class_name']=KNOWN.get(cls)
    return d

def parse_resource(b, platform=None):
    if len(b)<0x20: raise ValueError('EntityResource shorter than 0x20')
    d={'declared_file_size':struct.unpack_from('<Q',b,0)[0],'actual_file_size':len(b)}
    d['unk08']=resource_ptr(b,0x08);d['unk10']=resource_ptr(b,0x10);d['unk18']=resource_ptr(b,0x18)
    discr=d['unk10'].get('class_hash')
    d['semantic_role']={
        f'{D1_MODEL_DISCRIMINATOR:08X}':'entity_model',
        f'{D1_SKELETON_DISCRIMINATOR:08X}':'entity_skeleton',
        f'{D1_PHYSICS_DISCRIMINATOR:08X}':'entity_physics',
        f'{D1_CHILDREN_DISCRIMINATOR:08X}':'entity_children',
        f'{D1_GENERIC_NAME_DISCRIMINATOR:08X}':'entity_name_generic',
        f'{D1_SPECIFIC_NAME_DISCRIMINATOR:08X}':'entity_name_specific',
        f'{D1_SCRIPTED_ENTITY_DISCRIMINATOR:08X}':'scripted_entity_table_owner',
        f'{D1_DIALOGUE_ENTITY_DISCRIMINATOR:08X}':'dialogue_entity_owner',
    }.get(discr,'other_or_unknown')
    if d['semantic_role']=='entity_model':
        p=d['unk18'];t=p.get('target_offset');model_rel=0x1C4 if platform=='XboxOne' else 0x15C
        d['model_field_offset_in_parent']=model_rel
        if p.get('class_hash')==f'{D1_MODEL_PARENT:08X}' and isinstance(t,int) and t+model_rel+4<=len(b):
            d['embedded_model_tag_hash']=f'{u32(b,t+model_rel):08X}'
    elif d['semantic_role']=='entity_physics':
        p=d['unk18'];t=p.get('target_offset');model_rel=0x15C
        d['physics_model_field_offset_in_parent']=model_rel
        if p.get('class_hash')==f'{D1_PHYSICS_PARENT:08X}' and isinstance(t,int) and t+model_rel+4<=len(b):
            d['embedded_physics_model_tag_hash']=f'{u32(b,t+model_rel):08X}'
    elif d['semantic_role']=='entity_name_generic':
        # D1 D2Class_18808080: +0x278 Tag<D2Class_4D7E8080>.
        p=d['unk18'];t=p.get('target_offset');off=0x278;d['generic_name_tag_field_offset_in_parent']=off
        if p.get('class_hash')==f'{D1_GENERIC_NAME_PARENT:08X}' and isinstance(t,int) and t+off+4<=len(b):
            d['entity_name_tag_hash']=f'{u32(b,t+off):08X}'
            d['entity_name_tag_expected_class']=f'{D1_GENERIC_NAME_TAG_CLASS:08X}'
    elif d['semantic_role']=='entity_name_specific':
        # D1 D2Class_DB5E8080 has StringHash EntityName directly at +0x114.
        p=d['unk18'];t=p.get('target_offset');off=0x114;d['specific_name_field_offset_in_parent']=off
        if p.get('class_hash')==f'{D1_SPECIFIC_NAME_PARENT:08X}' and isinstance(t,int) and t+off+4<=len(b):
            d['entity_name_string_hash']=f'{u32(b,t+off):08X}'
    elif d['semantic_role']=='scripted_entity_table_owner':
        p=d['unk18'];t=p.get('target_offset');off=D1_SCRIPTED_ENTITY_TABLE_OFFSET
        d['scripted_entity_table_field_offset_in_parent']=off
        d['scripted_entity_table_expected_class']=f'{D1_SCRIPTED_ENTITY_TABLE_CLASS:08X}'
        if p.get('class_hash')==f'{D1_SCRIPTED_ENTITY_PARENT:08X}' and isinstance(t,int) and t+off+4<=len(b):
            d['scripted_entity_table_tag_hash']=f'{u32(b,t+off):08X}'
    elif d['semantic_role']=='dialogue_entity_owner':
        p=d['unk18'];t=p.get('target_offset');off=D1_DIALOGUE_ENTITY_OFFSET
        d['dialogue_entity_field_offset_in_parent']=off
        if p.get('class_hash')==f'{D1_DIALOGUE_ENTITY_PARENT:08X}' and isinstance(t,int) and t+off+4<=len(b):
            d['dialogue_entity_tag_hash']=f'{u32(b,t+off):08X}'
    return d

def main():
    ap=argparse.ArgumentParser();ap.add_argument('pkg',type=Path);ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('-o','--output',type=Path)
    a=ap.parse_args();r=EntryReader(a.pkg,a.runtime)
    allr=[e for e in r.entries if e['type']==16 and e['subtype']==0 and e['reference'].upper()==ENTITY_RESOURCE_CLASS]
    rows=[];roles=collections.Counter();disc=collections.Counter();p18=collections.Counter()
    for e in allr:
        row={'entry_index':e['index'],'tag_hash':e['tag_hash'],'size':e['file_size'],'available':r.available(e['index'])}
        if row['available']:
            try: row.update(parse_resource(r.entry(e['index']),r.h['platform']))
            except Exception as ex: row['error']=repr(ex)
            roles[row.get('semantic_role','parse_error')]+=1
            x=row.get('unk10',{}).get('class_hash');y=row.get('unk18',{}).get('class_hash')
            if x:disc[x]+=1
            if y:p18[y]+=1
        rows.append(row)
    rep={'package':str(r.pkg),'platform':r.h['platform'],'class_hash':ENTITY_RESOURCE_CLASS,
         'total_entries':len(allr),'resident_entries':sum(x['available'] for x in rows),
         'role_counts':dict(roles),'unk10_class_counts':dict(disc),'unk18_class_counts':dict(p18),'resources':rows}
    text=json.dumps(rep,indent=2)
    if a.output:a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(text+'\n');print('wrote',a.output)
    else:print(text)
if __name__=='__main__':main()
