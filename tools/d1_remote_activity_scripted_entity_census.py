#!/usr/bin/env python3
"""Enumerate D1 scripted-entity tables owned by one exact activity root.

This is the remote/split-TAR counterpart to the local activity + scripted identity
census. It follows only SF603 resources reachable from the supplied D1 named
SUnkActivity_ROI root, then source-closes their EntityResource role:

SUnkActivity_ROI -> ... -> S6E078080 -> SE9058080 -> S22428080[] ->
SF6038080 / 808003F6 +0x0C EntityResource / 80800861 ->
SBC078080 / 808007BC -> SA7058080 / 808005A7 +0x68 ->
SD9128080 / 808012D9 -> scripted groups/records + S2B138080 locations.

The SD912 `Locations` array is decoded literally from Charm's ROI schema as
S2B138080, stride 0x30: Location Vector4 at +0x00 and Rotation Vector4 at +0x10.
The remaining 0x10-byte tail of each record is preserved as raw hex. This tool does
not infer which location belongs to which scripted entity when a table contains more
than one record/location. A table with exactly one entity record and exactly one
location is reported as a singleton co-owned pair, not promoted to a hidden pointer.

D912 SMapDataEntry records are scripted overlay records, not redundant copies of the
runtime placement table. Retail King\'s Fall, Wrath, strike and Plaguelands evidence
shows records with the same WorldID and exact transform as a runtime placement while
serializing a different EntitySK. Such a record is preserved as
WORLDID_TRANSFORM_MATCH_ENTITY_DIFFERS. It is not an ownership failure and the two
EntitySK hashes are never aliased. A scripted EntityName may attach to a runtime
placement only when WorldID and EntitySK both agree.

No package-neighborhood or visual inference is used. A scripted table is admitted
only when its SF603 is serialized beneath the selected activity and the shared
EntityResource parser identifies the exact 808007BC -> 808005A7 role.
"""
from __future__ import annotations

import argparse,collections,json,struct,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))

from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_split_tar_extract import SplitHttpTar
from d1_remote_activity_placements import RemoteCorpus,gather_activity_sources
import d1_world_activity_entity_table_census as act
import d1_world_activity_entity_resource_census as place
import d1_world_scripted_entity_identity_census as scripted
from d1_entity_resource_probe import parse_resource,ENTITY_RESOURCE_CLASS

F603='808003F6'; SENTITY='80800734'; NULLS={'00000000','FFFFFFFF'}
FALSE_OWNER_EQUIVALENCE='named_script_record_entity_owner_mismatch'
PINNED_SOURCE=(
 'MontagueM/Charm@50d36ee1f9ecadad7522504c20b1f3f9c97e30af '
 'Tiger/Schema/Activity/ActivityStructsROI.cs + Tiger/Schema/Static/StaticMapData.cs')

def norm(x):return str(x).upper().removeprefix('0X').zfill(8)
def u32(b,o):return struct.unpack_from('<I',b,o)[0]

def runtime_placements(c,tables,f603s,viol):
 direct=[place.parse_direct_table(c,h) for h in tables]
 collapsed=[place.parse_f603(c,h) for h in f603s]
 for t in direct:viol.extend(f"{t['map_data_table']}:{x}" for x in t.get('violations',[]))
 # A scripted-table SF603 legitimately does not use the ordinary S2E->SDD placement path.
 # Only preserve true violations; collapse_reason is not a violation.
 for t in collapsed:viol.extend(f"{t['f603']}:{x}" for x in t.get('violations',[]))
 rows=[e for t in direct for e in t.get('entries',[])]+[e for t in collapsed for e in t.get('entries',[])]
 real=[x for x in rows if norm(x.get('entity_hash','FFFFFFFF')) not in NULLS]
 unique,_=place.runtime_placement_view(real,viol)
 return direct,collapsed,unique

def normalize_scripted_overlay_semantics(t):
 """Replace the old false EntitySK-equivalence assertion with explicit relations.

 The local parser historically treated a named D912 record whose EntitySK differed
 from the runtime placement at the same WorldID as malformed. Cross-activity retail
 evidence proves that is a normal scripted-overlay shape. We retain every serialized
 hash and match bit, remove only that obsolete assertion, and classify the relation.
 """
 t['violations']=[x for x in t.get('violations',[]) if FALSE_OWNER_EQUIVALENCE not in x]
 for g in t.get('groups',[]):
  g['violations']=[x for x in g.get('violations',[]) if FALSE_OWNER_EQUIVALENCE not in x]
  for r in g.get('records',[]):
   r['violations']=[x for x in r.get('violations',[]) if FALSE_OWNER_EQUIVALENCE not in x]
   pm=r.get('placement_match')
   if not isinstance(pm,dict):
    r['scripted_runtime_relation']='NO_RUNTIME_PLACEMENT_EVIDENCE'
    r['placement_identity_attachment_eligible']=False
    continue
   world=bool(pm.get('world_id_exists'))
   entity=bool(pm.get('entity_matches'))
   transform=bool(pm.get('transform_matches'))
   if not world:
    relation='WORLDID_NOT_IN_RUNTIME_PLACEMENTS'
   elif entity and transform:
    relation='WORLDID_ENTITY_TRANSFORM_MATCH'
   elif entity:
    relation='WORLDID_ENTITY_MATCH_TRANSFORM_DIFFERS'
   elif transform:
    relation='WORLDID_TRANSFORM_MATCH_ENTITY_DIFFERS'
   else:
    relation='WORLDID_MATCH_ENTITY_AND_TRANSFORM_DIFFER'
   pm['relation']=relation
   r['scripted_runtime_relation']=relation
   # The source contract requires WorldID + EntitySK for identity attachment.
   # Transform equality remains an independent validation signal.
   r['placement_identity_attachment_eligible']=bool(world and entity)
   r['placement_identity_transform_exact']=bool(world and entity and transform)
 return t

def attach_locations(c,t):
 """Decode SD912.Locations without assigning them to entity records."""
 h=norm(t['scripted_entity_table']); b,src=c.payload(h)
 arr=t.get('locations_array') or {}
 out=[]
 if b is None:
  t.setdefault('violations',[]).append('D912_location_payload_unavailable')
  t['locations']=out;return
 if not arr.get('ok'):
  t['locations']=out;return
 for i in range(int(arr.get('count',0))):
  o=int(arr['absolute'])+i*0x30
  if o<0 or o+0x30>len(b):
   t.setdefault('violations',[]).append(f'location[{i}]:S2B138080_oob')
   continue
  out.append({
   'index':i,'record_offset':o,
   'location':scripted.f4(b,o),
   'rotation':scripted.f4(b,o+0x10),
   'tail_20_30_hex':b[o+0x20:o+0x30].hex(),
  })
 t['locations']=out
 t['location_count']=len(out)
 records=t.get('records',[])
 if len(records)==1 and len(out)==1:
  r=records[0]
  t['singleton_entity_location_pair']={
   'entity_hash':r.get('entity_hash'),'type_string_hash':r.get('type_string_hash'),
   'world_id_hex':r.get('world_id_hex'),'location':out[0]['location'],'rotation':out[0]['rotation'],
   'status':'one_entity_record_and_one_location_in_same_source_owned_D912_table',
  }

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--activity-hash',required=True);ap.add_argument('--activity-name',required=True)
 ap.add_argument('--activity-class',default='80800616')
 ap.add_argument('--member-catalog',type=Path,action='append',required=True)
 ap.add_argument('--base-url',required=True);ap.add_argument('--part-count',type=int,default=10)
 ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('-o','--output',type=Path,required=True)
 a=ap.parse_args()
 catalogs=load_catalogs(a.member_catalog)
 arc=SplitHttpTar([f"{a.base_url.rstrip('/')}/packages.tar.{i:03d}" for i in range(1,a.part_count+1)],retries=6,timeout=90)
 c=RemoteCorpus(arc,catalogs,a.runtime)
 ah=norm(a.activity_hash)
 named={'tag_hash':ah,'name':a.activity_name,'aliases':[a.activity_name],'index':0,'named_table_indices':[0],
        'class_hash_raw_uint':norm(a.activity_class),'class_hash_canonical':norm(a.activity_class),'source_package_id':None}
 viol=[]
 activity=act.parse_activity(c,named,viol)
 tables,f603s,parents,s6es,unresolved=gather_activity_sources(activity)
 direct,collapsed,unique=runtime_placements(c,tables,f603s,viol)
 pindex={x['world_id_hex']:x for x in unique}
 owners=[];table_hashes=[]
 role_counts=collections.Counter()
 for fh in f603s:
  fm=c.entry_meta(fh);fb,fsrc=c.payload(fh)
  row={'f603':fh,'f603_meta':fm,'payload_source':fsrc,'violations':[]}
  if fm is None or norm(fm.get('reference',''))!=F603 or fb is None or len(fb)<0x10:
   row['violations'].append('F603_missing_class_or_payload');owners.append(row);continue
  erh=norm(f'{u32(fb,0x0C):08X}');row['entity_resource']=erh
  em=c.entry_meta(erh);eb,esrc=c.payload(erh);row['entity_resource_meta']=em;row['entity_resource_payload_source']=esrc
  if erh in NULLS or em is None or norm(em.get('reference',''))!=ENTITY_RESOURCE_CLASS or eb is None:
   row['violations'].append('EntityResource_missing_class_or_payload');owners.append(row);continue
  try:er=parse_resource(eb,'PS4')
  except Exception as ex:row['violations'].append('EntityResource_parse:'+repr(ex));owners.append(row);continue
  row['entity_resource_parse']=er;role_counts[er.get('semantic_role','unknown')]+=1
  th=er.get('scripted_entity_table_tag_hash')
  if er.get('semantic_role')=='scripted_entity_table_owner':
   if not th or norm(th) in NULLS:row['violations'].append('scripted_owner_missing_D912_tag')
   else:
    th=norm(th);row['scripted_entity_table']=th;table_hashes.append(th)
    tm=c.entry_meta(th);row['scripted_entity_table_meta']=tm
    if tm is None or norm(tm.get('reference',''))!='808012D9':row['violations'].append('scripted_D912_missing_or_class_mismatch')
  owners.append(row)
  viol.extend(f'{fh}:{x}' for x in row['violations'])
 table_hashes=sorted(set(table_hashes))
 parsed=[normalize_scripted_overlay_semantics(scripted.parse_d912(c,h,pindex)) for h in table_hashes]
 for t in parsed:attach_locations(c,t)
 for t in parsed:viol.extend(f"{t['scripted_entity_table']}:{x}" for x in t.get('violations',[]))
 records=[r for t in parsed for r in t.get('records',[])]
 locations=[{'d912':t['scripted_entity_table'],**x} for t in parsed for x in t.get('locations',[])]
 singleton_pairs=[{'d912':t['scripted_entity_table'],**t['singleton_entity_location_pair']} for t in parsed if t.get('singleton_entity_location_pair')]
 families=collections.Counter(t.get('script_family_string_hash') for t in parsed if t.get('script_family_string_hash') not in (None,*NULLS))
 types=collections.Counter(r.get('type_string_hash') for r in records if r.get('type_string_hash') not in (None,*NULLS))
 names=collections.Counter(r.get('entity_name_string_hash') for r in records if r.get('entity_name_string_hash') not in (None,*NULLS))
 entities=collections.Counter(r.get('entity_hash') for r in records if r.get('entity_hash') not in (None,*NULLS))
 relations=collections.Counter(r.get('scripted_runtime_relation','UNCLASSIFIED') for r in records)
 matched=[r for r in records if r.get('placement_identity_attachment_eligible')]
 named_records=[r for r in records if r.get('entity_name_string_hash') not in (None,*NULLS)]
 named_unattached=[r for r in named_records if not r.get('placement_identity_attachment_eligible')]
 out={'schema':'d1_remote_activity_scripted_entity_census/v3',
      'status':'D1_REMOTE_ACTIVITY_SCRIPTED_ENTITY_CENSUS_COMPLETE' if not viol else 'D1_REMOTE_ACTIVITY_SCRIPTED_ENTITY_CENSUS_WITH_VIOLATIONS',
      'pinned_source':PINNED_SOURCE,'activity':{'tag_hash':ah,'name':a.activity_name,'class_hash':norm(a.activity_class)},
      'unique_resource_parents':parents,'unique_s6e_resources':s6es,'unique_map_data_tables':tables,
      'unique_f603_entity_resources':f603s,'unresolved_dependency_hashes':unresolved,
      'runtime_placement_count':len(unique),'f603_count':len(f603s),'entity_resource_role_counts':dict(role_counts),
      'scripted_owner_f603_count':sum(1 for x in owners if (x.get('entity_resource_parse') or {}).get('semantic_role')=='scripted_entity_table_owner'),
      'unique_scripted_table_count':len(table_hashes),'unique_scripted_tables':table_hashes,
      'scripted_record_count':len(records),'scripted_location_count':len(locations),
      'singleton_entity_location_pair_count':len(singleton_pairs),'singleton_entity_location_pairs':singleton_pairs,
      'placement_matched_scripted_record_count':len(matched),
      'named_scripted_record_count':len(named_records),'named_scripted_record_unattached_count':len(named_unattached),
      'scripted_runtime_relation_counts':dict(relations),
      'script_family_string_hash_counts':dict(families),'type_string_hash_counts':dict(types),
      'entity_name_string_hash_counts':dict(names),'scripted_entity_hash_counts':dict(entities),
      'owners':owners,'scripted_tables':parsed,'violations':viol,
      'policy':('Only scripted tables beneath the supplied exact activity root are admitted. SF603 ownership, EntityResource role, SA705 +0x68 D912 edge, scripted records, and S2B138080 location arrays are serialized retail data. D912 EntitySK may intentionally differ from the runtime placement EntitySK at the same WorldID/transform; both hashes are preserved and never aliased. Scripted names attach to runtime placement identity only when WorldID and EntitySK agree. Locations are not assigned to entity records when multiplicity makes ownership ambiguous. Names remain StringHashes until exact preimages are recovered.')}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n')
 print('STATUS',out['status'],'ACTIVITY',ah,'F603',len(f603s),'SCRIPTED_OWNERS',out['scripted_owner_f603_count'],'TABLES',len(table_hashes),'RECORDS',len(records),'LOCATIONS',len(locations),'SINGLETON_PAIRS',len(singleton_pairs),'VIOLATIONS',len(viol))
 print('RELATIONS',dict(relations));print('FAMILIES',dict(families));print('TYPES',dict(types));print('NAME_HASHES',dict(names));print('ENTITIES',dict(entities));print('D912',table_hashes)
 return 0 if not viol else 2

if __name__=='__main__':raise SystemExit(main())
