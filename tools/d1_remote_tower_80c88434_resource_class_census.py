#!/usr/bin/env python3
"""Exact ResourcePointer class census for the three Tower 80C88434 EntitySKs.

The generic EntityResource parser intentionally names only a small set of known
resource discriminators. This probe preserves every resource's exact +0x08/+0x10/+0x18
ResourcePointer class, target offset, and a bounded target-prefix window so remaining
resource families can be correlated against D1 source schemas without scanning
arbitrary payload integers as semantic links.

When --dump-dir is supplied, one byte-exact payload is also preserved for every
unique EntityResource hash. Repeated hashes are required to have identical SHA-256
before the census can be promoted.
"""
from __future__ import annotations
import argparse,collections,hashlib,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
if str(HERE) not in sys.path: sys.path.insert(0,str(HERE))
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_activity_placements import RemoteCorpus
from d1_remote_s_entity_resource_package_find import S_ENTITY_REF,parse_entity_resources
from d1_entity_resource_probe import ENTITY_RESOURCE_CLASS,parse_resource
from d1_split_tar_extract import SplitHttpTar

ENTITIES=['80C7A5AD','80C7ACC5','80C883CA']
def norm(x): return str(x).upper().removeprefix('0X').zfill(8)

def target_prefix(b:bytes,p:dict,n=0x100):
    t=p.get('target_offset')
    if not isinstance(t,int) or p.get('null') or p.get('error'): return None
    return {'target_offset':t,'class_hash':p.get('class_hash'),'class_name':p.get('class_name'),
            'prefix_start':t,'prefix_end':min(len(b),t+n),'prefix_hex':b[t:min(len(b),t+n)].hex()}

def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument('--member-catalog',type=Path,action='append',required=True)
    ap.add_argument('--base-url',required=True);ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('--dump-dir',type=Path)
    ap.add_argument('-o','--output',type=Path,required=True);a=ap.parse_args()
    if a.dump_dir: a.dump_dir.mkdir(parents=True,exist_ok=True)
    cats=load_catalogs(a.member_catalog);arc=SplitHttpTar([f'{a.base_url.rstrip("/")}/packages.tar.{i:03d}' for i in range(1,a.part_count+1)],retries=6,timeout=90);c=RemoteCorpus(arc,cats,a.runtime)
    violations=[];entities=[];unique={};dumped={}
    for eh in ENTITIES:
        em=c.entry_meta(eh);eb,esrc=c.payload(eh)
        if em is None or eb is None or norm(em.get('reference',''))!=S_ENTITY_REF:
            violations.append(f'{eh}: unavailable/class mismatch');continue
        try: rr=parse_entity_resources(eb)
        except Exception as ex: violations.append(f'{eh}: parse {ex!r}');continue
        rows=[]
        for q in rr:
            rh=norm(q['resource_hash']);rm=c.entry_meta(rh);rb,rsrc=c.payload(rh)
            row={'resource_index':int(q.get('resource_index',-1)),'resource_hash':rh,
                 'reference':None if rm is None else norm(rm.get('reference','FFFFFFFF')),
                 'source':str(rsrc) if rsrc else None,'byte_count':None if rb is None else len(rb)}
            if rm is None or rb is None or row['reference']!=ENTITY_RESOURCE_CLASS:
                row['error']='resource unavailable/class mismatch';violations.append(f'{eh}:{rh}: '+row['error'])
            else:
                try:
                    p=parse_resource(rb,'PS4');row['semantic_role']=p.get('semantic_role')
                    row['declared_file_size']=p.get('declared_file_size');row['payload_sha256']=hashlib.sha256(rb).hexdigest()
                    row['pointers']={k:{**p[k],'target_prefix':target_prefix(rb,p[k])} for k in ('unk08','unk10','unk18')}
                    row['embedded_model_tag_hash']=p.get('embedded_model_tag_hash')
                    if a.dump_dir:
                        old=dumped.get(rh)
                        if old is None:
                            fp=a.dump_dir/f'{rh}.bin';fp.write_bytes(rb)
                            dumped[rh]={'file':fp.name,'byte_count':len(rb),'sha256':row['payload_sha256'],'source':str(rsrc) if rsrc else None}
                        elif old['sha256']!=row['payload_sha256'] or old['byte_count']!=len(rb):
                            violations.append(f'{rh}: repeated payload differs while dumping')
                except Exception as ex: row['error']=repr(ex);violations.append(f'{eh}:{rh}:{ex!r}')
            rows.append(row)
            u=unique.setdefault(rh,{'resource_hash':rh,'occurrences':[]})
            u['occurrences'].append({'entity':eh,'resource_index':row['resource_index'],'row':row})
        entities.append({'entity_hash':eh,'source':str(esrc),'resource_count':len(rows),'resources':rows})
    # Require identical typed resource payload/class evidence wherever a hash repeats.
    class_counts=collections.Counter();role_counts=collections.Counter();unique_rows=[]
    for rh,u in sorted(unique.items()):
        rows=[x['row'] for x in u['occurrences']];ref=rows[0]
        sig=lambda r:(r.get('payload_sha256'),r.get('semantic_role'),tuple((k,(r.get('pointers') or {}).get(k,{}).get('class_hash')) for k in ('unk08','unk10','unk18')))
        if any(sig(r)!=sig(ref) for r in rows[1:]):violations.append(f'{rh}: repeated resource evidence differs')
        ptrs=ref.get('pointers') or {};disc=(ptrs.get('unk10') or {}).get('class_hash');parent=(ptrs.get('unk18') or {}).get('class_hash')
        class_counts[(disc,parent)]+=1;role_counts[ref.get('semantic_role')]+=1
        unique_rows.append({'resource_hash':rh,'occurrence_count':len(rows),'semantic_role':ref.get('semantic_role'),
                            'discriminator_class':disc,'parent_class':parent,'unk08_class':(ptrs.get('unk08') or {}).get('class_hash'),
                            'payload_sha256':ref.get('payload_sha256'),'byte_count':ref.get('byte_count'),'pointers':ptrs,
                            'dump':dumped.get(rh)})
    if a.dump_dir and len(dumped)!=len(unique_rows):
        violations.append(f'dumped {len(dumped)} payloads for {len(unique_rows)} unique resources')
    out={'schema_version':2,'status':'D1_TOWER_80C88434_RESOURCE_CLASS_CENSUS_EXACT' if not violations else 'D1_TOWER_80C88434_RESOURCE_CLASS_CENSUS_VIOLATIONS',
         'entity_hashes':ENTITIES,'entities':entities,'unique_resource_count':len(unique_rows),'unique_resources':unique_rows,
         'dumped_payload_count':len(dumped),'dump_manifest':dict(sorted(dumped.items())),
         'semantic_role_counts':dict(role_counts),'discriminator_parent_pair_counts':[
             {'discriminator_class':k[0],'parent_class':k[1],'unique_resource_count':v} for k,v in sorted(class_counts.items(),key=lambda kv:str(kv[0]))],
         'violations':violations,
         'policy':'ResourcePointer classes come only from exact relative-pointer targets in retail EntityResource payloads. Optional payload dumps are byte-exact source evidence and repeated hashes must agree by SHA-256. Prefix windows are discovery evidence for source-schema correlation; no unknown class is semantically named by this probe.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'status':out['status'],'unique_resource_count':len(unique_rows),'dumped_payload_count':len(dumped),'semantic_role_counts':dict(role_counts),'pairs':out['discriminator_parent_pair_counts'],'violations':violations},indent=2))
    return 0 if not violations else 2
if __name__=='__main__':raise SystemExit(main())
