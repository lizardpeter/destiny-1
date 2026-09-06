#!/usr/bin/env python3
"""Build a namespace-safe archive-wide D1 articulated-character candidate index.

This is phase 1 of corpus-wide Guardian/NPC/enemy export. It reads only exact Tiger
package headers and entry tables through HTTP ranges. No payload bodies are
retrieved and no package-name semantics are used to classify characters.

Input is the exact 2,105-member physical-location census. Physical members are
partitioned into independent logical namespaces:

  base       : (package id)
  localized  : (package id, locale)
  special    : exact special package family

Within each namespace family the current generation is chosen with the already
validated Tiger rule max(header.patch_id, filename generation, filename). This is
important because localized packages reuse package ids and therefore must never be
collapsed into the base package or another language.

A current family is surfaced for payload-level character analysis when its entry
table contains structural evidence relevant to articulated entities: EntityResource,
s_entity_model, animation clip/wrapper/control classes. This stage deliberately does
NOT call a package an NPC/enemy/Guardian. Those semantics require exact ownership or
investment/entity graph evidence in later phases.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import io
import json
import re
from pathlib import Path

from d1_pkg_probe import parse_entries, parse_header
from d1_split_tar_extract import SplitHttpTar

ENTITY_RESOURCE='80800861'
ENTITY_MODEL='80801AB5'
ANIMATION_CLIP='808005A1'
ANIMATION_WRAPPER='8080222A'
POST_ANIMATION_CONTROL='80802C0E'
INTERESTING=(ENTITY_RESOURCE,ENTITY_MODEL,ANIMATION_CLIP,ANIMATION_WRAPPER,POST_ANIMATION_CONTROL)
ENTRY_STRIDE=16
GEN_RX=re.compile(r'_([0-9]+)\.pkg$',re.I)


def generation(name:str)->int:
    m=GEN_RX.search(Path(name).name)
    return int(m.group(1)) if m else 0


def namespace_key(m:dict)->tuple:
    kind=str(m.get('kind') or '')
    pkg=str(m.get('package_id') or '').upper()
    if kind=='base':
        return ('base',pkg)
    if kind=='localized':
        return ('localized',pkg,str(m.get('locale') or '').lower())
    # Special package names do not obey normal FileHash-family naming. Keep each
    # special basename isolated unless a later schema proves a patch relationship.
    return ('special',Path(str(m['name'])).name)


def key_text(k:tuple)->str:
    return ':'.join(k)


def classify(counts:dict[str,int])->str:
    er=counts.get(ENTITY_RESOURCE,0)
    model=counts.get(ENTITY_MODEL,0)
    anim=counts.get(ANIMATION_CLIP,0)+counts.get(ANIMATION_WRAPPER,0)+counts.get(POST_ANIMATION_CONTROL,0)
    if er and model and anim:return 'model_resource_animation_candidate'
    if er and anim:return 'resource_animation_candidate'
    if model and er:return 'model_resource_candidate'
    if model and anim:return 'model_animation_candidate'
    if anim:return 'animation_bank_candidate'
    if model:return 'model_bank_candidate'
    if er:return 'entity_resource_bank'
    return 'no_articulated_signature'


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--location-index',type=Path,required=True)
    ap.add_argument('--base-url',default='https://crypt.cohae.dev/destiny/ps4/packages/latest')
    ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--retries',type=int,default=6)
    ap.add_argument('--timeout',type=int,default=120)
    a=ap.parse_args()

    src=json.loads(a.location_index.read_text())
    if src.get('schema')!='d1_complete_physical_location_index/v1' or src.get('status')!='D1_COMPLETE_PHYSICAL_LOCATION_INDEX_EXACT':
        raise ValueError('location index is not exact d1_complete_physical_location_index/v1')
    members=list(src.get('members') or [])
    expected=int((src.get('counts') or {}).get('complete_physical_members',-1))
    if len(members)!=expected or expected!=2105:
        raise ValueError(f'physical member count {len(members)} != exact census {expected}/2105')
    names=[Path(str(x['name'])).name for x in members]
    if len(names)!=len(set(names)):raise ValueError('duplicate physical package basename in location census')

    base=a.base_url.rstrip('/')
    arc=SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1,a.part_count+1)],retries=a.retries,timeout=a.timeout)
    expected_sizes=list((src.get('source') or {}).get('part_sizes') or [])
    if expected_sizes and arc.sizes!=expected_sizes:
        raise ValueError(f'split TAR part sizes changed: {arc.sizes} != {expected_sizes}')

    physical=[];violations=[]
    for i,m in enumerate(members,1):
        name=Path(str(m['name'])).name;off=int(m['data_offset']);size=int(m['size'])
        if size<0x140:
            violations.append({'name':name,'stage':'header','detail':f'physical size {size} < 0x140'});continue
        try:h=parse_header(io.BytesIO(arc.read_at(off,0x140)))
        except Exception as ex:
            violations.append({'name':name,'stage':'header','detail':repr(ex)});continue
        pkg=f"{int(h['pkg_id']):04X}"
        declared=str(m.get('package_id') or '').upper()
        if declared and declared!=pkg:
            violations.append({'name':name,'stage':'header','detail':f'location package id {declared} != Tiger {pkg}'})
        if h['platform']!='PS4':
            violations.append({'name':name,'stage':'header','detail':f'unexpected platform {h["platform"]}'})
        row={
          'name':name,'kind':m.get('kind'),'locale':m.get('locale'),'package_id':pkg,
          'filename_generation':int(m.get('generation') if m.get('generation') is not None else generation(name)),
          'header_patch_id':int(h['patch_id']),'language':h['language'],'language_code':int(h['language_code']),
          'data_offset':off,'size':size,'entry_table_count':int(h['entry_table_count']),
          'entry_table_offset':int(h['entry_table_offset']),'entry_table_sha1_expected':str(h['entry_table_hash']).lower(),
          'namespace_key':key_text(namespace_key({**m,'package_id':pkg})),
        }
        physical.append(row)
        if i%100==0 or i==len(members):print(f'HEADERS {i}/{len(members)}',flush=True)

    fam=collections.defaultdict(list)
    for r in physical:fam[r['namespace_key']].append(r)
    current=[]
    for k,rows in sorted(fam.items()):
        win=max(rows,key=lambda r:(r['header_patch_id'],r['filename_generation'],r['name']))
        current.append(win)

    ref_totals=collections.Counter();class_totals=collections.Counter();ns_candidate_counts=collections.Counter()
    rows=[]
    for i,p in enumerate(current,1):
        n=int(p['entry_table_count'])*ENTRY_STRIDE;o=int(p['entry_table_offset'])
        if o<0 or n<0 or o+n>int(p['size']):
            violations.append({'name':p['name'],'stage':'entry_table','detail':f'bounds {o}+{n}>{p["size"]}'});continue
        try:raw=arc.read_at(int(p['data_offset'])+o,n)
        except Exception as ex:
            violations.append({'name':p['name'],'stage':'entry_table','detail':repr(ex)});continue
        got=hashlib.sha1(raw).hexdigest()
        if got!=p['entry_table_sha1_expected']:
            violations.append({'name':p['name'],'stage':'entry_table','detail':f'sha1 {got} != {p["entry_table_sha1_expected"]}'});continue
        entries=parse_entries(raw,int(p['package_id'],16))
        refs=collections.Counter(str(e['reference']).upper() for e in entries)
        counts={h:int(refs.get(h,0)) for h in INTERESTING}
        cls=classify(counts)
        articulated=cls!='no_articulated_signature'
        strong=cls in {'model_resource_animation_candidate','resource_animation_candidate','model_animation_candidate'}
        kind=str(p.get('kind') or 'unknown')
        if articulated:ns_candidate_counts[kind]+=1
        for h,nc in counts.items():ref_totals[h]+=nc
        class_totals[cls]+=1
        rows.append({
          'namespace_key':p['namespace_key'],'kind':kind,'locale':p.get('locale'),'package_id':p['package_id'],
          'current_member':p['name'],'current_patch_id':p['header_patch_id'],'current_generation':p['filename_generation'],
          'language':p['language'],'language_code':p['language_code'],'entry_count':len(entries),
          'signature_counts':counts,'classification':cls,'articulated_signature':articulated,
          'strong_character_payload_candidate':strong,
          'physical_members':[{q:r[q] for q in ('name','data_offset','size','filename_generation','header_patch_id')} for r in sorted(fam[p['namespace_key']],key=lambda x:(x['header_patch_id'],x['filename_generation'],x['name']))]
        })
        if i%50==0 or i==len(current):print(f'TABLES {i}/{len(current)}',flush=True)

    candidates=[r for r in rows if r['articulated_signature']]
    strong=[r for r in rows if r['strong_character_payload_candidate']]
    out={
      'schema':'d1_remote_character_candidate_index/v1','status':'D1_CHARACTER_CANDIDATE_INDEX_COMPLETE' if not violations else 'D1_CHARACTER_CANDIDATE_INDEX_PARTIAL',
      'source':{'location_index':str(a.location_index),'location_index_sha256':hashlib.sha256(a.location_index.read_bytes()).hexdigest(),
                'base_url':a.base_url,'part_count':a.part_count,'physical_member_count':len(members)},
      'namespace_family_count':len(current),'current_family_rows':rows,
      'articulated_signature_family_count':len(candidates),'strong_character_payload_candidate_count':len(strong),
      'namespace_candidate_counts':dict(ns_candidate_counts),'classification_counts':dict(class_totals),
      'signature_reference_totals':dict(ref_totals),
      'articulated_signature_families':candidates,'strong_character_payload_candidates':strong,
      'violations':violations,
      'policy':(
        'This is a structural routing census only. Exact Tiger entry reference classes decide whether a package family enters '
        'payload-level articulated analysis. Package names and visual resemblance do not establish Guardian/NPC/enemy identity. '
        'Localized namespaces are isolated from base and from one another even when Tiger package ids/tag hashes overlap.'),
    }
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ('status','namespace_family_count','articulated_signature_family_count','strong_character_payload_candidate_count','namespace_candidate_counts','classification_counts','signature_reference_totals')},indent=2))
    return 0 if not violations else 2

if __name__=='__main__':raise SystemExit(main())
