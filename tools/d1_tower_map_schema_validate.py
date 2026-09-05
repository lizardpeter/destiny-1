#!/usr/bin/env python3
"""Validate source-derived Destiny 1 ROI map schemas against shipped Tiger bytes.

The candidate layouts in this file are intentionally marked SOURCE_DERIVED until the
invariants below pass on the supplied corpus.  They were transcribed from the public
Charm D1 Rise-of-Iron schema implementation and byte-order-normalized to this
project's canonical class-hash display.

This validator does not export a map.  It proves (or rejects) structural invariants:
- dynamic-array bounds and element sizes
- class-linked MapContainer / MapDataTable / static-map relationships
- D1 static table indices
- InstanceTransforms count * 0x40 backing size
- static mesh V0/V1/index FileHash triples resolving to actual Tiger entries
- static-info Material/Static/Transform indices staying in bounds

Passing these invariants upgrades specific layout facts from SOURCE_DERIVED toward
CONFIRMED_BINARY; semantic comments from external source remain hypotheses unless
independently demonstrated by our bytes.
"""
from __future__ import annotations

import argparse, json, math, re, struct, sys
from collections import Counter, defaultdict
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_entry_extract import EntryReader

C={
    's_entity':'80800734',
    'static_map_data':'808008B4',       # Charm B4088080
    'static_map_data_d1':'80801B75',    # Charm 751B8080
    'static_table':'80801A90',          # Charm 901A8080
    'bubble_definition':'808091E0',     # Charm E0918080
    'map_container':'80808A54',         # Charm 548A8080
    'map_data_table':'808009A2',        # Charm A2098080
    'occlusion_bounds':'80800583',      # Charm 83058080
}


def gen_of(p:Path)->int:
    m=re.search(r'_(\d+)\.pkg$',p.name)
    return int(m.group(1)) if m else -1


def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def i32(b,o): return struct.unpack_from('<i',b,o)[0]
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
def i16(b,o): return struct.unpack_from('<h',b,o)[0]
def f32s(b,o,n): return struct.unpack_from('<'+'f'*n,b,o)
def hx(v): return f'{v:08X}'

def dyn(b,off,elem_size):
    if off+0x10>len(b): return {'ok':False,'error':'header_oob','field_offset':off}
    count=i32(b,off); unk=u32(b,off+4); rel=struct.unpack_from('<q',b,off+8)[0]
    # Charm DynamicArray: RelativePointer base is pointer-field position (off+8),
    # then AddExtraOffset(0x10).
    absolute=off+8+rel+0x10
    end=absolute+max(count,0)*elem_size
    ok=count>=0 and absolute>=0 and end<=len(b)
    return {'ok':ok,'field_offset':off,'count':count,'unknown04':unk,'relative':rel,'absolute':absolute,'end':end,'elem_size':elem_size,'payload_size':len(b)}

class Corpus:
    def __init__(self,paths,runtime):
        self.readers=[]; self.occ=defaultdict(list)
        for p in sorted(paths,key=lambda x:(x.name,gen_of(x))):
            r=EntryReader(p,runtime); self.readers.append((p,r))
            for e in r.entries:
                self.occ[e['tag_hash'].upper()].append((gen_of(p),p,r,e))
        for h in self.occ: self.occ[h].sort(key=lambda x:x[0],reverse=True)
    def occurrences_by_ref(self,ref):
        out=[]
        for p,r in self.readers:
            for e in r.entries:
                if e['reference'].upper()==ref:
                    out.append((gen_of(p),p,r,e))
        return out
    def best(self,h,prefer_available=True):
        for x in self.occ.get(h.upper(),[]):
            if not prefer_available or x[2].available(x[3]['index']): return x
        return self.occ.get(h.upper(),[None])[0] if self.occ.get(h.upper()) else None
    def entry_meta(self,h):
        x=self.best(h,False)
        if not x: return None
        g,p,r,e=x
        return {'hash':h.upper(),'snapshot':p.name,'package_id':f"{int(r.h['pkg_id']):04X}",'entry_index':int(e['index']),'type':int(e['type']),'subtype':int(e['subtype']),'reference':e['reference'].upper(),'size':int(e['file_size']),'available':bool(r.available(e['index']))}
    def payload(self,h):
        for g,p,r,e in self.occ.get(h.upper(),[]):
            if not r.available(e['index']): continue
            try: return r.entry(e['index']), {'snapshot':p.name,'package_id':f"{int(r.h['pkg_id']):04X}",'entry_index':int(e['index']),'reference':e['reference'].upper(),'size':int(e['file_size'])}
            except Exception: pass
        return None,None


def resolve_class(c:Corpus,h,expected=None):
    m=c.entry_meta(h)
    if not m: return {'hash':h,'exists':False,'expected_reference':expected,'matches':False}
    return {**m,'exists':True,'expected_reference':expected,'matches': expected is None or m['reference']==expected}


def parse_static_table(c:Corpus,h,instance_total=None):
    b,src=c.payload(h)
    if b is None: return {'hash':h,'ok':False,'error':'payload_unavailable'}
    mats=dyn(b,0x08,0x08); meshes=dyn(b,0x18,0x18); infos=dyn(b,0x28,0x18)
    rep={'hash':h,'source':src,'payload_size':len(b),'arrays':{'materials':mats,'meshes':meshes,'infos':infos},'ok':all(x['ok'] for x in (mats,meshes,infos)),'mesh_entries':[],'info_entries':[],'violations':[]}
    if not rep['ok']:
        rep['violations'].append('dynamic_array_bounds'); return rep
    material_hashes=[]
    for i in range(mats['count']):
        o=mats['absolute']+i*8
        material_hashes.append(hx(u32(b,o+4)))
    rep['material_hashes']=material_hashes
    for i in range(meshes['count']):
        o=meshes['absolute']+i*0x18
        v0,v1,ind=(hx(u32(b,o+j)) for j in (0,4,8))
        row={'index':i,'vertices0':v0,'vertices1':v1,'indices':ind,'unk0C':u16(b,o+0xC),'detail_level':struct.unpack_from('<b',b,o+0xE)[0],'primitive_type':struct.unpack_from('<b',b,o+0xF)[0],'index_offset':u32(b,o+0x10),'index_count':u32(b,o+0x14)}
        row['targets']={k:c.entry_meta(v) for k,v in [('vertices0',v0),('vertices1',v1),('indices',ind)]}
        row['all_targets_exist']=all(row['targets'][k] is not None for k in row['targets'])
        ints=[int(v0,16),int(v1,16),int(ind,16)]
        row['consecutive_filehash_triple']=(ints[1]==ints[0]+1 and ints[2]==ints[1]+1)
        rep['mesh_entries'].append(row)
        if not row['all_targets_exist']: rep['violations'].append(f'mesh[{i}] unresolved buffer target')
    for i in range(infos['count']):
        o=infos['absolute']+i*0x18
        ic=i16(b,o); mi=i16(b,o+4); si=i16(b,o+8); ti=i16(b,o+0xA)
        row={'index':i,'instance_count':ic,'material_index':mi,'static_index':si,'transform_index':ti,
             'material_in_bounds':0<=mi<mats['count'],'static_in_bounds':0<=si<meshes['count'],
             'transform_in_bounds': instance_total is None or (ic>=0 and ti>=0 and ti+ic<=instance_total)}
        row['all_indices_in_bounds']=row['material_in_bounds'] and row['static_in_bounds'] and row['transform_in_bounds']
        rep['info_entries'].append(row)
        if not row['all_indices_in_bounds']: rep['violations'].append(f'info[{i}] index bounds')
    rep['summary']={'materials':mats['count'],'meshes':meshes['count'],'infos':infos['count'],'all_mesh_targets_exist':all(x['all_targets_exist'] for x in rep['mesh_entries']),'consecutive_mesh_triples':sum(x['consecutive_filehash_triple'] for x in rep['mesh_entries']),'all_info_indices_in_bounds':all(x['all_indices_in_bounds'] for x in rep['info_entries'])}
    rep['ok']=rep['ok'] and not rep['violations']
    return rep


def validate_static_data_d1(c:Corpus,h):
    b,src=c.payload(h)
    if b is None: return {'hash':h,'ok':False,'error':'payload_unavailable'}
    rep={'hash':h,'source':src,'payload_size':len(b),'ok':True,'violations':[]}
    if len(b)<0x90: return {**rep,'ok':False,'violations':['payload shorter than minimum field frontier']}
    instance_count=i32(b,0x20); transforms=hx(u32(b,0x24)); rep['instance_count']=instance_count; rep['instance_transforms']=transforms
    tmeta=c.entry_meta(transforms); rep['instance_transform_target']=tmeta
    tb,tsrc=c.payload(transforms); rep['instance_transform_payload_source']=tsrc
    if instance_count<0: rep['violations'].append('negative instance_count')
    if not tmeta: rep['violations'].append('instance transform FileHash unresolved')
    if tb is not None:
        rep['instance_transform_payload_size']=len(tb); rep['expected_transform_bytes']=max(instance_count,0)*0x40; rep['transform_size_exact']=len(tb)==max(instance_count,0)*0x40
        if not rep['transform_size_exact']: rep['violations'].append('InstanceTransforms payload size != InstanceCounts * 0x40')
        # sanity only: every matrix must be finite floats
        finite=True
        for o in range(0,min(len(tb),max(instance_count,0)*0x40),4):
            if not math.isfinite(struct.unpack_from('<f',tb,o)[0]): finite=False; break
        rep['transforms_all_finite']=finite
        if not finite: rep['violations'].append('non-finite transform float')
    else: rep['violations'].append('instance transform payload unavailable')
    arrays=[]; table_hashes=[]
    for n,off in enumerate((0x38,0x50,0x68,0x80),1):
        a=dyn(b,off,4); a['name']=f'statics{n}'; vals=[]
        if a['ok']:
            for i in range(a['count']): vals.append(hx(u32(b,a['absolute']+i*4)))
        a['values']=vals; a['resolved']=[resolve_class(c,x,C['static_table']) for x in vals]; arrays.append(a); table_hashes.extend(vals)
        if not a['ok']: rep['violations'].append(f'statics{n} dynamic array bounds')
        if any(not x['matches'] for x in a['resolved']): rep['violations'].append(f'statics{n} target class mismatch/unresolved')
    rep['static_arrays']=arrays; rep['static_table_hashes']=table_hashes
    rep['static_tables']=[parse_static_table(c,x,instance_count) for x in table_hashes]
    if any(not x.get('ok') for x in rep['static_tables']): rep['violations'].append('one or more static tables failed invariants')
    rep['summary']={'static_table_refs':len(table_hashes),'unique_static_tables':len(set(table_hashes)),'total_static_mesh_records':sum(x.get('summary',{}).get('meshes',0) for x in rep['static_tables']),'total_static_info_records':sum(x.get('summary',{}).get('infos',0) for x in rep['static_tables'])}
    rep['ok']=not rep['violations']; return rep


def validate_static_map_data(c:Corpus,h):
    b,src=c.payload(h)
    if b is None: return {'hash':h,'ok':False,'error':'payload_unavailable'}
    rep={'hash':h,'source':src,'payload_size':len(b),'ok':True,'violations':[]}
    if len(b)<0x34: rep['ok']=False; rep['violations'].append('short payload'); return rep
    d1=hx(u32(b,0x30)); rep['d1_static_map_data']=resolve_class(c,d1,C['static_map_data_d1'])
    if not rep['d1_static_map_data']['matches']: rep['violations'].append('D1StaticMapData +0x30 target mismatch/unresolved')
    rep['d1_validation']=validate_static_data_d1(c,d1) if rep['d1_static_map_data']['exists'] else None
    if rep['d1_validation'] and not rep['d1_validation']['ok']: rep['violations'].append('D1 static data invariants failed')
    rep['ok']=not rep['violations']; return rep


def validate_map_data_table(c:Corpus,h,max_entries=200000):
    b,src=c.payload(h)
    if b is None: return {'hash':h,'ok':False,'error':'payload_unavailable'}
    a=dyn(b,0x08,0x90); rep={'hash':h,'source':src,'payload_size':len(b),'data_entries_array':a,'ok':a['ok'],'violations':[],'entity_reference_counts':Counter(),'entries_sample':[]}
    if not a['ok']: rep['violations'].append('data entries dynamic-array bounds'); return rep
    if a['count']>max_entries: rep['ok']=False; rep['violations'].append('implausibly large count'); return rep
    finite=True; entity_class_matches=0; existing=0
    for i in range(a['count']):
        o=a['absolute']+i*0x90; eh=hx(u32(b,o)); rot=f32s(b,o+0x20,4); tr=f32s(b,o+0x30,4)
        em=c.entry_meta(eh); existing += int(em is not None); entity_class_matches += int(em is not None and em['reference']==C['s_entity'])
        finite &= all(math.isfinite(x) for x in rot+tr)
        if i<100: rep['entries_sample'].append({'index':i,'entity_hash':eh,'entity_target':em,'rotation':rot,'translation':tr})
    rep['summary']={'entry_count':a['count'],'entity_hashes_resolve':existing,'entity_hashes_class_s_entity':entity_class_matches,'transforms_all_finite':finite}
    if not finite: rep['violations'].append('non-finite placement transform')
    rep['ok']=not rep['violations']; return rep


def validate_map_container(c:Corpus,h):
    b,src=c.payload(h)
    if b is None: return {'hash':h,'ok':False,'error':'payload_unavailable'}
    a=dyn(b,0x18,4); vals=[]
    if a['ok']: vals=[hx(u32(b,a['absolute']+i*4)) for i in range(a['count'])]
    res=[resolve_class(c,x,C['map_data_table']) for x in vals]
    rep={'hash':h,'source':src,'payload_size':len(b),'map_data_tables_array':a,'map_data_table_hashes':vals,'targets':res,'ok':a['ok'] and all(x['matches'] for x in res),'violations':[]}
    if not a['ok']: rep['violations'].append('MapDataTables array bounds')
    if any(not x['matches'] for x in res): rep['violations'].append('MapDataTable class mismatch/unresolved')
    rep['tables']=[validate_map_data_table(c,x) for x in vals]
    if any(not x['ok'] for x in rep['tables']): rep['violations'].append('map data table invariant failure')
    rep['ok']=not rep['violations']; return rep


def validate_bubble(c:Corpus,h):
    b,src=c.payload(h)
    if b is None: return {'hash':h,'ok':False,'error':'payload_unavailable'}
    a=dyn(b,0x08,4); vals=[]
    if a['ok']: vals=[hx(u32(b,a['absolute']+i*4)) for i in range(a['count'])]
    res=[resolve_class(c,x,C['map_container']) for x in vals]
    rep={'hash':h,'source':src,'payload_size':len(b),'map_resources_array':a,'map_container_hashes':vals,'targets':res,'ok':a['ok'] and all(x['matches'] for x in res),'violations':[]}
    if not a['ok']: rep['violations'].append('MapResources array bounds')
    if any(not x['matches'] for x in res): rep['violations'].append('MapContainer class mismatch/unresolved')
    rep['containers']=[validate_map_container(c,x) for x in vals]
    if any(not x['ok'] for x in rep['containers']): rep['violations'].append('map container invariant failure')
    rep['ok']=not rep['violations']; return rep


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--snapshot',type=Path,action='append',required=True); ap.add_argument('--runtime',type=Path,required=True); ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args(); a.out.mkdir(parents=True,exist_ok=True); c=Corpus([x.resolve() for x in a.snapshot],a.runtime)
    counts={name:len(c.occurrences_by_ref(ref)) for name,ref in C.items()}
    static_maps=[]; seen=set()
    for _,_,_,e in c.occurrences_by_ref(C['static_map_data']):
        h=e['tag_hash'].upper()
        if h not in seen: seen.add(h); static_maps.append(validate_static_map_data(c,h))
    bubbles=[]; seenb=set()
    for _,_,_,e in c.occurrences_by_ref(C['bubble_definition']):
        h=e['tag_hash'].upper()
        if h not in seenb: seenb.add(h); bubbles.append(validate_bubble(c,h))
    static_d1=[]; seend=set()
    for _,_,_,e in c.occurrences_by_ref(C['static_map_data_d1']):
        h=e['tag_hash'].upper()
        if h not in seend: seend.add(h); static_d1.append(validate_static_data_d1(c,h))
    summary={
        'source_derived_class_occurrence_counts':counts,
        'unique_static_map_data_resources':len(static_maps),'static_map_data_all_pass':all(x['ok'] for x in static_maps) if static_maps else False,
        'unique_static_map_data_d1_resources':len(static_d1),'static_map_data_d1_all_pass':all(x['ok'] for x in static_d1) if static_d1 else False,
        'unique_bubble_definitions':len(bubbles),'bubble_all_pass':all(x['ok'] for x in bubbles) if bubbles else False,
        'total_static_mesh_records':sum(x.get('summary',{}).get('total_static_mesh_records',0) for x in static_d1),
        'static_mesh_records_with_all_targets':sum(sum(1 for t in x.get('static_tables',[]) for m in t.get('mesh_entries',[]) if m.get('all_targets_exist')) for x in static_d1),
        'consecutive_v0_v1_index_triples':sum(sum(t.get('summary',{}).get('consecutive_mesh_triples',0) for t in x.get('static_tables',[])) for x in static_d1),
    }
    report={'summary':summary,'class_candidates':C,'evidence_status':'SOURCE_DERIVED layout under binary validation','static_map_data':static_maps,'static_map_data_d1':static_d1,'bubble_definitions':bubbles,'policy':'Only invariant outcomes are binary evidence. External semantic names/comments are not promoted unless independently demonstrated.'}
    (a.out/'tower_map_schema_validation.json').write_text(json.dumps(report,indent=2,default=list)+'\n')
    print(json.dumps(summary,indent=2));

if __name__=='__main__': main()
