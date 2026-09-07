#!/usr/bin/env python3
"""Cross-entity calibration for D1 Tower S152 placement configuration vs model switch banks.

Proof boundary:
- SD912 / SMapDataEntry / S152B / S4E2A layouts are source-pinned D1 ROI schemas.
- SEntity -> Resource[] -> EntityResource -> model parent is source-validated ownership.
- model-parent +0x50 switch-bank shape is accepted only when the existing exact D1
  structural invariants produce one 0x18-container candidate with nested 8-byte pairs.
- Exact pair correspondence is measured across independent placements/entities.

This tool deliberately does NOT infer the logical operator of FE1A descriptor list A/B,
does NOT infer that every S152 record is a material switch input, and does NOT open
Xur E6/E7/E8 merely from pair equality.
"""
from __future__ import annotations

import argparse, collections, hashlib, json, struct, sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
if str(HERE) not in sys.path: sys.path.insert(0,str(HERE))

from d1_entity_resource_probe import ENTITY_RESOURCE_CLASS, parse_resource
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_activity_placements import RemoteCorpus
from d1_remote_model_parent_permutation_layout_probe import early_dynamic_headers, test_switch_container_candidate
from d1_remote_s_entity_resource_package_find import S_ENTITY_REF, parse_entity_resources
from d1_split_tar_extract import SplitHttpTar

SD912='808012D9'; SMAP=0x80800406; S152=0x80802B15; S4E2A=0x80802A4E
NULLS={0,0xFFFFFFFF}

def norm(x): return str(x).upper().removeprefix('0X').zfill(8)
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def i32(b,o): return struct.unpack_from('<i',b,o)[0]
def q64(b,o): return struct.unpack_from('<q',b,o)[0]
def le32(v): return struct.pack('<I',v)

def resource_ptr(b,field):
    if field<0 or field+8>len(b): raise ValueError(f'ResourcePointer field OOB 0x{field:X}')
    rel=q64(b,field)
    if rel==0:return {'null':True,'field_offset':field,'relative':0}
    target=field+rel
    if target<4 or target>len(b): raise ValueError(f'ResourcePointer target OOB field=0x{field:X} target=0x{target:X}')
    return {'null':False,'field_offset':field,'relative':rel,'target_offset':target,'class_hash':f'{u32(b,target-4):08X}'}

def dyn(b,field,stride):
    if field<0 or field+0x10>len(b):raise ValueError(f'DynamicArray header OOB 0x{field:X}')
    count=i32(b,field); rel=q64(b,field+8)
    if count<0 or count>100000:raise ValueError(f'implausible DynamicArray count {count} at 0x{field:X}')
    start=field+8+rel+0x10 if count else None
    if count and (start<4 or start+count*stride>len(b)):raise ValueError(f'DynamicArray payload OOB field=0x{field:X} count={count} start={start}')
    return {'field_offset':field,'count':count,'relative':rel,'element_start':start,'stride':stride}

def decode_s152(b,base):
    a=dyn(b,base+0x10,8)
    if a['count'] and u32(b,a['element_start']-4)!=S4E2A:
        raise ValueError(f'S152 element class != S4E2A at 0x{base:X}')
    rows=[]
    for i in range(a['count']):
        o=a['element_start']+i*8
        rows.append({'index':i,'offset':o,'pair':[f'{u32(b,o):08X}',f'{u32(b,o+4):08X}'],
                     'unk00_tiger_hash':f'{u32(b,o):08X}','type_string_hash':f'{u32(b,o+4):08X}'})
    return {'base_offset':base,'array':a,'records':rows}

def discover_smap_placements(c,owner):
    meta=c.entry_meta(owner); b,src=c.payload(owner)
    if meta is None or b is None:raise ValueError(f'{owner}: payload unavailable')
    if norm(meta.get('reference','0'))!=SD912:raise ValueError(f'{owner}: reference {meta.get("reference")} != SD912')
    out=[]; needle=le32(SMAP); pos=0
    while True:
        m=b.find(needle,pos)
        if m<0:break
        pos=m+1
        if m%4:continue
        start=m+4
        if start+0x90>len(b):continue
        entity=f'{u32(b,start):08X}'
        em=c.entry_meta(entity)
        if em is None or norm(em.get('reference','0'))!=S_ENTITY_REF:continue
        try:dr=resource_ptr(b,start+0x88)
        except Exception:continue
        row={'owner':owner,'owner_source':src,'smap_class_marker_offset':m,'smap_offset':start,'entity_hash':entity,'data_resource':dr,'s152':None}
        if not dr['null'] and dr.get('class_hash')==f'{S152:08X}': row['s152']=decode_s152(b,dr['target_offset'])
        out.append(row)
    return out

def resolve_model_bank(c,entity):
    meta=c.entry_meta(entity); eb,esrc=c.payload(entity)
    if meta is None or eb is None:raise ValueError(f'{entity}: entity payload unavailable')
    if norm(meta.get('reference','0'))!=S_ENTITY_REF:raise ValueError(f'{entity}: not SEntity')
    resources=parse_entity_resources(eb); models=[]; errors=[]
    for rr in resources:
        rh=norm(rr['resource_hash'])
        if int(rh,16) in NULLS:continue
        rm=c.entry_meta(rh)
        if rm is None or norm(rm.get('reference','0'))!=ENTITY_RESOURCE_CLASS:continue
        rb,rsrc=c.payload(rh)
        if rb is None:
            errors.append({'resource_hash':rh,'error':'payload unavailable'});continue
        try:p=parse_resource(rb,'PS4')
        except Exception as ex:
            errors.append({'resource_hash':rh,'error':repr(ex)});continue
        if p.get('semantic_role')!='entity_model':continue
        parent=p.get('unk18') or {}; base=parent.get('target_offset')
        row={'resource_hash':rh,'resource_sha256':hashlib.sha256(rb).hexdigest(),'resource_source':rsrc,
             'model_tag_hash':norm(p.get('embedded_model_tag_hash','FFFFFFFF')),
             'parent_class':parent.get('class_hash'),'parent_offset':base,'switch_bank_exact':False,'switch_pairs':[]}
        if parent.get('class_hash')=='80801A9C' and isinstance(base,int):
            tests=[test_switch_container_candidate(rb,h) for h in early_dynamic_headers(rb,base)]
            exact=[x for x in tests if x.get('all_outer_elements_have_valid_nested_pair_array') and x.get('inner_pair_total',0)>0]
            exact=[x for x in exact if x.get('parent_relative_offset')==0x50]
            if len(exact)==1:
                sw=exact[0]; pairs=[]
                for r in sw.get('inner_pair_rows',[]):
                    for pair in r.get('pairs',[]):pairs.append({'switch_record_index':int(r['outer_index']),'pair':[norm(pair[0]),norm(pair[1])]})
                row.update({'switch_bank_exact':True,'switch_record_count':int(sw['outer_count']),'switch_pair_count':len(pairs),'switch_pairs':pairs})
            else: row['switch_shape_candidate_count_at_0x50']=len(exact)
        models.append(row)
    return {'entity_hash':entity,'entity_source':esrc,'resource_count':len(resources),'model_resources':models,'errors':errors}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--scripted-owner',action='append',required=True);ap.add_argument('--member-catalog',type=Path,action='append',required=True);ap.add_argument('--base-url',required=True);ap.add_argument('--part-count',type=int,default=10);ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('-o','--output',type=Path,required=True);a=ap.parse_args()
    cats=load_catalogs(a.member_catalog);arc=SplitHttpTar([f'{a.base_url.rstrip("/")}/packages.tar.{i:03d}' for i in range(1,a.part_count+1)],retries=6,timeout=90);c=RemoteCorpus(arc,cats,a.runtime)
    violations=[];placements=[]
    for raw in a.scripted_owner:
        h=norm(raw)
        try:placements.extend(discover_smap_placements(c,h))
        except Exception as ex:violations.append(f'{h}:{ex!r}')
    s152=[p for p in placements if p.get('s152')]
    entities=sorted({p['entity_hash'] for p in s152});entity_rows={}
    for e in entities:
        try:entity_rows[e]=resolve_model_bank(c,e)
        except Exception as ex:entity_rows[e]={'entity_hash':e,'error':repr(ex)};violations.append(f'{e}:{ex!r}')

    calibration=[];pair_stats=collections.defaultdict(lambda:{'placement_records':0,'own_bank_exact_matches':0,'own_bank_reverse_matches':0,'entities':set(),'model_resources':set()})
    exact_model_entity_count=0
    for e,r in entity_rows.items():
        exact_models=[m for m in r.get('model_resources',[]) if m.get('switch_bank_exact')]
        if len(exact_models)==1:exact_model_entity_count+=1
    for p in s152:
        er=entity_rows.get(p['entity_hash'],{}); exact_models=[m for m in er.get('model_resources',[]) if m.get('switch_bank_exact')]
        row={'owner':p['owner'],'smap_offset':p['smap_offset'],'entity_hash':p['entity_hash'],'configuration_records':p['s152']['records'],'model_resource_count':len(er.get('model_resources',[])),'exact_switch_bank_model_count':len(exact_models),'record_matches':[]}
        if len(exact_models)==1:
            m=exact_models[0]; bank={tuple(x['pair']) for x in m['switch_pairs']}; rev={(b,a) for a,b in bank}
            row['model_resource_hash']=m['resource_hash'];row['model_tag_hash']=m['model_tag_hash'];row['switch_record_count']=m['switch_record_count'];row['switch_pair_count']=m['switch_pair_count']
            for rec in p['s152']['records']:
                pair=tuple(rec['pair']); exact=pair in bank; reverse=pair in rev
                matches=[x['switch_record_index'] for x in m['switch_pairs'] if tuple(x['pair'])==pair]
                row['record_matches'].append({'record_index':rec['index'],'pair':list(pair),'exact_pair_in_own_model_switch_bank':exact,'reverse_pair_in_own_model_switch_bank':reverse,'matching_switch_record_indices':sorted(set(matches))})
                key='/'.join(pair);s=pair_stats[key];s['placement_records']+=1;s['own_bank_exact_matches']+=int(exact);s['own_bank_reverse_matches']+=int(reverse);s['entities'].add(p['entity_hash']);s['model_resources'].add(m['resource_hash'])
        calibration.append(row)

    # Corpus control: for every observed configuration pair, count how many independently
    # resolved exact model banks contain it. This prevents a ubiquitous hash pair from
    # masquerading as entity-specific consumer evidence.
    unique_banks={}
    for er in entity_rows.values():
        for m in er.get('model_resources',[]):
            if m.get('switch_bank_exact'):unique_banks[m['resource_hash']]={tuple(x['pair']) for x in m['switch_pairs']}
    for key,s in pair_stats.items():
        pair=tuple(key.split('/'));s['unique_entity_count']=len(s.pop('entities'));s['unique_own_model_resource_count']=len(s.pop('model_resources'));s['all_resolved_model_banks_containing_pair']=sum(pair in b for b in unique_banks.values());s['resolved_model_bank_count']=len(unique_banks)

    idx=collections.Counter();idx_match=collections.Counter();idx_total=collections.Counter()
    for row in calibration:
        for x in row.get('record_matches',[]):idx_total[x['record_index']]+=1;idx_match[x['record_index']]+=int(x['exact_pair_in_own_model_switch_bank'])
    by_index={str(i):{'comparable_records':idx_total[i],'exact_own_bank_matches':idx_match[i],'match_fraction':(idx_match[i]/idx_total[i] if idx_total[i] else None)} for i in sorted(idx_total)}
    xur_pair=['26170C92','4AC210DE'];xur_rows=[x for x in calibration for r in x.get('record_matches',[]) if r['pair']==xur_pair]
    xur_exact=sum(r['exact_pair_in_own_model_switch_bank'] for x in calibration for r in x.get('record_matches',[]) if r['pair']==xur_pair)
    out={'schema':'d1_remote_tower_placement_permutation_calibration/v1','status':'D1_TOWER_PLACEMENT_PERMUTATION_CROSS_ENTITY_CALIBRATION' if not violations else 'D1_TOWER_PLACEMENT_PERMUTATION_CALIBRATION_VIOLATIONS','scripted_owners':[norm(x) for x in a.scripted_owner],'smap_placement_count':len(placements),'s152_placement_count':len(s152),'unique_s152_entity_count':len(entities),'entities_with_exact_single_model_switch_bank':exact_model_entity_count,'unique_exact_model_switch_bank_count':len(unique_banks),'record_index_correspondence':by_index,'pair_correspondence':dict(sorted(pair_stats.items())),'xur_26170C92_4AC210DE':{'comparable_placement_count':len(xur_rows),'exact_own_model_switch_bank_match_count':xur_exact},'entity_model_resolution':list(entity_rows.values()),'calibration_rows':calibration,'violations':violations,'proof':{'s152_is_source_typed_placement_configuration':True,'cross_entity_pair_correspondence_measured':True,'material_permutation_consumer_semantics_proven':False,'descriptor_A_B_evaluation_semantics_proven':False},'gates':{'E6_80C885E6_live_selection_proven':False,'E7_80C885E7_live_selection_proven':False,'E8_80C885E8_live_selection_proven':False},'policy':'Exact S152 configuration/model-switch-bank correspondence is calibration evidence. It is not promoted to executable consumer semantics without an independently closed D1 read/evaluation path. Descriptor list A/B logic remains unknown; E6/E7/E8 remain fail-closed.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ('status','smap_placement_count','s152_placement_count','unique_s152_entity_count','entities_with_exact_single_model_switch_bank','unique_exact_model_switch_bank_count','record_index_correspondence','xur_26170C92_4AC210DE','violations','proof','gates')},indent=2));return 0 if not violations else 2
if __name__=='__main__':raise SystemExit(main())
