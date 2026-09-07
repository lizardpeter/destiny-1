#!/usr/bin/env python3
"""Traverse one exact D1 SUnkActivity_ROI to its runtime entity placements remotely.

This is the HTTP-range counterpart of d1_world_activity_entity_table_census.py +
d1_world_activity_entity_resource_census.py. The caller supplies an exact current
named-tag identity (TagHash, name, class 80800616). Every child FileHash is routed
through its encoded Tiger package id against a verified package-member catalog.

The output preserves both serialized placement references and the WorldID-collapsed
runtime view. Optional entity-name output is joined only by exact s_entity FileHash
from d1_remote_entity_names_resolve.py.
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))

from d1_filehash import package_hex
from d1_investment_arrangement_probe import filehash_pkg_index
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_investment_parent_probe import RemoteLogicalPackage
from d1_split_tar_extract import SplitHttpTar
import d1_world_activity_entity_table_census as act
import d1_world_activity_entity_resource_census as placements

NULLS={'00000000','FFFFFFFF'}


def norm(x):return str(x).upper().removeprefix('0X').zfill(8)
def package_of(h):return filehash_pkg_index(int(norm(h),16))[0]
def package_id_text(h):
    h=norm(h)
    return None if h in NULLS else package_hex(h).lower()

# The shared local parser predates the cross-bank FileHash proof. Its pkgid helper is
# metadata only, but patch it here so every remote universal manifest reports the same
# source-validated package provenance that is used for actual payload routing.
act.pkgid=package_id_text


class RemoteCorpus:
    def __init__(self,arc,catalogs,runtime):
        self.arc=arc;self.catalogs=catalogs;self.runtime=runtime;self.views={};self.maps={};self.payload_cache={}
    def view(self,pkg):
        if pkg not in self.catalogs:raise KeyError(f'package {pkg:04X} absent from verified catalog')
        if pkg not in self.views:self.views[pkg]=RemoteLogicalPackage(self.arc,self.catalogs[pkg],self.runtime)
        return self.views[pkg]
    def map(self,pkg):
        if pkg not in self.maps:self.maps[pkg]={e['tag_hash'].upper():e for e in self.view(pkg).entries}
        return self.maps[pkg]
    def entry_meta(self,h):
        h=norm(h)
        if h in NULLS:return None
        try:return self.map(package_of(h)).get(h)
        except Exception:return None
    def payload(self,h):
        h=norm(h)
        if h in NULLS:return None,None
        if h in self.payload_cache:return self.payload_cache[h]
        try:
            pkg=package_of(h);v=self.view(pkg);e=self.map(pkg).get(h)
            if e is None:r=(None,None)
            else:r=(v.entry(e['index']),v.view.name)
        except Exception:r=(None,None)
        self.payload_cache[h]=r;return r


def summarize_names(path):
    if path is None:return {}
    d=json.loads(path.read_text());out={}
    for e in d.get('entities',[]):
        names=[]
        for n in e.get('names',[]):
            for r in n.get('resolved',[]):
                if r.get('ok') and r.get('string') is not None and r['string'] not in names:names.append(r['string'])
        out[norm(e['entity_hash'])]={'resolved_names':names,'name_evidence':e.get('names',[]),'models':e.get('models',[]),'skeletons':e.get('skeletons',[])}
    return out


def gather_activity_sources(parsed):
    tables=[];f603=[];parents=[];s6es=[];unresolved=[]
    for loc in parsed.get('locations',[]):
        for eg in loc.get('activity_entity_groups',[]):
            p=eg.get('resource_parent') or {};ph=p.get('hash')
            if ph:parents.append(ph)
            if ph and not (p.get('target') or {}).get('exists'):unresolved.append(ph)
            ch=p.get('child') or {}
            if ch.get('hash') and ch.get('meta') is None:unresolved.append(ch['hash'])
            for g in p.get('groups',[]):
                for rr in g.get('resources',[]):
                    if rr.get('hash'):s6es.append(rr['hash'])
                    if not (rr.get('target') or {}).get('exists') and rr.get('hash'):unresolved.append(rr['hash'])
                    for st in rr.get('stages',[]):
                        t=st.get('map_data_table') or {};th=t.get('hash')
                        if th and norm(th) not in NULLS:
                            tables.append(norm(th))
                            if not t.get('exists'):unresolved.append(th)
                        for er in st.get('entity_resource_tables',[]):
                            eh=er.get('hash')
                            if eh and norm(eh) not in NULLS:
                                f603.append(norm(eh))
                                if not er.get('exists'):unresolved.append(eh)
    return sorted(set(tables)),sorted(set(f603)),sorted(set(parents)),sorted(set(s6es)),sorted(set(norm(x) for x in unresolved if x and norm(x) not in NULLS))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--activity-hash',required=True)
    ap.add_argument('--activity-name',required=True)
    ap.add_argument('--activity-class',default='80800616')
    ap.add_argument('--member-catalog',type=Path,action='append',required=True)
    ap.add_argument('--base-url',required=True);ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--entity-names',type=Path)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()
    catalogs=load_catalogs(a.member_catalog);arc=SplitHttpTar([f"{a.base_url.rstrip('/')}/packages.tar.{i:03d}" for i in range(1,a.part_count+1)],retries=6,timeout=90)
    c=RemoteCorpus(arc,catalogs,a.runtime)
    ah=norm(a.activity_hash);named={'tag_hash':ah,'name':a.activity_name,'aliases':[a.activity_name],'index':0,'named_table_indices':[0],
        'class_hash_raw_uint':norm(a.activity_class),'class_hash_canonical':norm(a.activity_class),'source_package_id':f'{package_of(ah):04X}'}
    violations=[];parsed=act.parse_activity(c,named,violations)
    tables,f603,parents,s6es,unresolved=gather_activity_sources(parsed)
    direct=[placements.parse_direct_table(c,h) for h in tables];collapsed=[placements.parse_f603(c,h) for h in f603]
    for t in direct:violations.extend(f"{t['map_data_table']}:{x}" for x in t.get('violations',[]))
    for t in collapsed:violations.extend(f"{t['f603']}:{x}" for x in t.get('violations',[]))
    rows=[e for t in direct for e in t.get('entries',[])]+[e for t in collapsed for e in t.get('entries',[])]
    real=[x for x in rows if norm(x['entity_hash']) not in NULLS]
    runtime,dups=placements.runtime_placement_view(real,violations)
    name_map=summarize_names(a.entity_names)
    for x in runtime:
        nm=name_map.get(norm(x['entity_hash']),{})
        x['resolved_names']=nm.get('resolved_names',[]);x['name_evidence']=nm.get('name_evidence',[])
        x['known_models']=nm.get('models',[]);x['known_skeletons']=nm.get('skeletons',[])
        m=c.entry_meta(x['entity_hash']);x['entity_reference']=None if m is None else norm(m.get('reference'))
    entity_counts=collections.Counter(norm(x['entity_hash']) for x in runtime)
    unique_entity_hashes=sorted(entity_counts)
    named_counts=collections.Counter(n for x in runtime for n in x.get('resolved_names',[]))
    out={'schema':'d1_remote_activity_placements/v1','status':'D1_REMOTE_ACTIVITY_PLACEMENTS_COMPLETE' if not violations else 'D1_REMOTE_ACTIVITY_PLACEMENTS_WITH_VIOLATIONS',
         'activity':{'tag_hash':ah,'name':a.activity_name,'class_hash':norm(a.activity_class),'package_id':f'{package_of(ah):04X}'},
         'activity_parse':parsed,'unique_resource_parents':parents,'unique_s6e_resources':s6es,'unique_map_data_tables':tables,'unique_f603_entity_resources':f603,
         'unresolved_dependency_hashes':unresolved,'serialized_placement_count':len(real),'runtime_placement_count':len(runtime),'duplicate_serialized_reference_count':dups,
         'unique_entity_count':len(entity_counts),'unique_entity_hashes':unique_entity_hashes,'runtime_entity_counts':dict(entity_counts),'resolved_name_counts':dict(named_counts),
         'runtime_placements':runtime,'direct_tables':direct,'f603_tables':collapsed,'violations':violations,
         'policy':'Named activity identity is supplied from the exact current D1 named-tag table. All activity/table/entity edges and WorldIDs are serialized retail data. Names are joined only by exact s_entity FileHash; no proximity or visual inference. Package provenance uses the source-validated banked D1 Tiger FileHash decoder.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n')
    print('STATUS',out['status'],'ACTIVITY',ah,a.activity_name,'TABLES',len(tables),'F603',len(f603),'SERIALIZED',len(real),'RUNTIME',len(runtime),'UNIQUE_ENTITIES',len(entity_counts),'VIOLATIONS',len(violations))
    print('NAMES',dict(named_counts))
    for h,n in entity_counts.most_common():
        rows2=[x for x in runtime if norm(x['entity_hash'])==h];names=sorted({z for x in rows2 for z in x.get('resolved_names',[])})
        print('ENTITY',h,'COUNT',n,'NAMES',names,'MODELS',rows2[0].get('known_models'),'SKELETONS',[(s.get('resource_hash'),s.get('node_count')) for s in rows2[0].get('known_skeletons',[])])
    return 0 if not violations else 2

if __name__=='__main__':raise SystemExit(main())
