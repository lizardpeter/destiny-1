#!/usr/bin/env python3
"""Classify exact serialized Resource[] members of one or more D1 PS4 s_entity tags.

The tool reads the validated D1 s_entity Resource[] array and resolves each FileHash
only when its package family has a caller-supplied verified member catalog.  For
resolved class 0x80800861 EntityResources it applies the source-crosschecked
EntityResource parser and records the exact semantic discriminator/parent classes.
Unknown, unavailable, and uncatalogued resources remain explicit instead of being
named from adjacency or package conventions.

Logical package views are opened lazily.  This matters for the universal catalog:
an entity normally touches only a small subset of the retail package namespace, so
classification should not instantiate every package family before reading one
Resource[].  The lazy path is semantically identical to the earlier eager path but
makes the same source-proven classifier practical as a whole-game primitive.
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))

from d1_entity_resource_probe import ENTITY_RESOURCE_CLASS, parse_resource
from d1_investment_arrangement_probe import filehash_pkg_index
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_investment_parent_probe import RemoteLogicalPackage
from d1_remote_s_entity_resource_package_find import S_ENTITY_REF, parse_entity_resources
from d1_split_tar_extract import SplitHttpTar


def norm(s:str)->str: return s.upper().removeprefix('0X').zfill(8)


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--entity',action='append',required=True)
    ap.add_argument('--member-catalog',type=Path,action='append',required=True)
    ap.add_argument('--base-url',required=True)
    ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()

    entities=[norm(x) for x in a.entity]
    catalogs=load_catalogs(a.member_catalog)
    base=a.base_url.rstrip('/')
    arc=SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1,a.part_count+1)],retries=6,timeout=90)
    views={}
    def get_view(pkg:int):
        if pkg not in catalogs:
            return None
        if pkg not in views:
            views[pkg]=RemoteLogicalPackage(arc,catalogs[pkg],a.runtime)
        return views[pkg]

    rows=[]; errors=[]
    for eh in entities:
        pkg,idx=filehash_pkg_index(int(eh,16))
        v=get_view(pkg)
        if v is None:
            raise SystemExit(f'entity {eh}: package {pkg:04X} has no verified member catalog')
        if not (0<=idx<len(v.entries)): raise ValueError(f'{eh}: file index {idx} outside package entry table')
        e=v.entries[idx]
        if e['tag_hash'].upper()!=eh or e['reference'].upper()!=S_ENTITY_REF:
            raise ValueError(f'{eh}: resolved entry mismatch: {e}')
        resources=parse_entity_resources(v.entry(idx))
        classified=[]
        for r in resources:
            h=r['resource_hash'].upper(); rp=r['resource_package_id']; ri=r['resource_file_index']
            out={**r,'resolution_status':'uncatalogued_package','entry':None,'entity_resource':None}
            if rp is None:
                out['resolution_status']='null_or_invalid_hash'; classified.append(out); continue
            rv=get_view(rp)
            if rv is None:
                classified.append(out); continue
            if ri is None or not (0<=ri<len(rv.entries)):
                out['resolution_status']='file_index_out_of_range'; classified.append(out); continue
            re=rv.entries[ri]
            if re['tag_hash'].upper()!=h:
                out['resolution_status']='tag_hash_mismatch'
                out['entry']={'tag_hash':re['tag_hash'].upper(),'entry_index':ri,'reference':re['reference'].upper(),'type':re['type'],'subtype':re['subtype'],'file_size':re['file_size']}
                classified.append(out); continue
            out['entry']={'tag_hash':h,'entry_index':ri,'reference':re['reference'].upper(),'type':re['type'],'subtype':re['subtype'],'file_size':re['file_size']}
            out['resolution_status']='metadata_resolved'
            if re['type']==16 and re['subtype']==0 and re['reference'].upper()==ENTITY_RESOURCE_CLASS:
                try:
                    d=parse_resource(rv.entry(ri),'PS4')
                    out['entity_resource']=d
                    out['resolution_status']='entity_resource_parsed'
                except Exception as ex:
                    out['resolution_status']='entity_resource_parse_error'
                    errors.append({'entity_hash':eh,'resource_hash':h,'error':repr(ex)})
            classified.append(out)
        rows.append({'entity_hash':eh,'package_id':f'{pkg:04X}','entry_index':idx,'resource_count':len(resources),'resources':classified})

    # Compare positions across variants without assigning semantics.
    maxn=max((x['resource_count'] for x in rows),default=0)
    position_comparison=[]
    for i in range(maxn):
        vals=[]
        for x in rows:
            vals.append(x['resources'][i]['resource_hash'] if i<len(x['resources']) else None)
        position_comparison.append({'resource_index':i,'hashes':vals,'all_equal':len(set(vals))==1})

    status_counts={}
    role_counts={}
    for x in rows:
        for r in x['resources']:
            status_counts[r['resolution_status']]=status_counts.get(r['resolution_status'],0)+1
            er=r.get('entity_resource') or {}; role=er.get('semantic_role')
            if role: role_counts[role]=role_counts.get(role,0)+1
    rep={'schema':'d1_remote_entity_resource_classify/v2','entities':rows,
         'verified_catalog_package_ids':[f'{x:04X}' for x in sorted(catalogs)],
         'opened_package_ids':[f'{x:04X}' for x in sorted(views)],
         'opened_package_count':len(views),
         'position_comparison':position_comparison,'resolution_status_counts':status_counts,
         'entity_resource_role_counts':role_counts,'error_count':len(errors),'errors':errors,
         'policy':'Only exact s_entity Resource[] FileHashes and verified catalog resolution are classified. Semantic roles are emitted only when the validated EntityResource discriminator parser proves them; all other resources remain class hashes/unknowns. Package views are opened lazily with no change to FileHash routing or classification semantics.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(rep,indent=2)+'\n')
    print('ENTITIES',entities,'OPENED_PACKAGES',rep['opened_package_ids'])
    print('STATUS',status_counts);print('ENTITY_RESOURCE_ROLES',role_counts);print('ERRORS',len(errors))
    for i,p in enumerate(position_comparison):
        if not p['all_equal']: print('VARIANT_RESOURCE',i,p['hashes'])
    for x in rows:
        print('ENTITY',x['entity_hash'])
        for r in x['resources']:
            ent=r.get('entry') or {}; er=r.get('entity_resource') or {}
            print(' ',r['resource_index'],r['resource_hash'],r['resolution_status'],ent.get('reference'),er.get('semantic_role'))
    return 0

if __name__=='__main__': raise SystemExit(main())
