#!/usr/bin/env python3
"""Fast structural character candidate index for the 337 base D1 package families.

Consumes the exact universal base member catalog rather than re-walking all 2,105
physical namespaces.  It reads only the current base generation's Tiger header and
entry table, SHA-1 validates that table, and emits the same candidate-row shape used
by d1_remote_character_corpus_probe.py.

This is an acceleration path, not a completeness substitute: localized/special
namespaces remain covered by the separate 2,105-member census.
"""
from __future__ import annotations

import argparse,collections,hashlib,io,json
from pathlib import Path

from d1_pkg_probe import parse_header,parse_entries
from d1_split_tar_extract import SplitHttpTar

ENTITY_RESOURCE='80800861';ENTITY_MODEL='80801AB5';ANIMATION_CLIP='808005A1';ANIMATION_WRAPPER='8080222A';POST_ANIMATION_CONTROL='80802C0E'
INTERESTING=(ENTITY_RESOURCE,ENTITY_MODEL,ANIMATION_CLIP,ANIMATION_WRAPPER,POST_ANIMATION_CONTROL)


def classify(c):
    er=c.get(ENTITY_RESOURCE,0);m=c.get(ENTITY_MODEL,0);a=c.get(ANIMATION_CLIP,0)+c.get(ANIMATION_WRAPPER,0)+c.get(POST_ANIMATION_CONTROL,0)
    if er and m and a:return 'model_resource_animation_candidate'
    if er and a:return 'resource_animation_candidate'
    if m and er:return 'model_resource_candidate'
    if m and a:return 'model_animation_candidate'
    if a:return 'animation_bank_candidate'
    if m:return 'model_bank_candidate'
    if er:return 'entity_resource_bank'
    return 'no_articulated_signature'


def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument('catalog',type=Path);ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--base-url',default='https://crypt.cohae.dev/destiny/ps4/packages/latest');ap.add_argument('--part-count',type=int,default=10)
    a=ap.parse_args();cat=json.loads(a.catalog.read_text())
    if cat.get('schema')!='d1_remote_package_member_catalog/v1':raise ValueError('wrong catalog schema')
    fams=cat.get('families') or {};base=a.base_url.rstrip('/');arc=SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1,a.part_count+1)],retries=6,timeout=90)
    rows=[];violations=[];classes=collections.Counter();ref_totals=collections.Counter()
    for n,(pkg,members) in enumerate(sorted(fams.items()),1):
        if not members:continue
        winner=max(members,key=lambda x:(int(x.get('header_patch_id',0)),int(x.get('filename_generation',0)),x['name']))
        try:
            hb=arc.read_at(int(winner['data_offset']),0x140);h=parse_header(io.BytesIO(hb))
            if f"{int(h['pkg_id']):04X}"!=pkg.upper():raise ValueError(f'header package {int(h["pkg_id"]):04X} != catalog {pkg}')
            count=int(h['entry_table_count']);off=int(h['entry_table_offset']);size=count*16
            if off+size>int(winner['size']):raise ValueError('entry table exceeds physical member')
            raw=arc.read_at(int(winner['data_offset'])+off,size);got=hashlib.sha1(raw).hexdigest();exp=str(h['entry_table_hash']).lower()
            if got!=exp:raise ValueError(f'entry table SHA1 {got}!={exp}')
            entries=parse_entries(raw,int(h['pkg_id']));refs=collections.Counter(str(e['reference']).upper() for e in entries)
            counts={x:int(refs.get(x,0)) for x in INTERESTING};cl=classify(counts);classes[cl]+=1
            for k,v in counts.items():ref_totals[k]+=v
            physical=[{'name':x['name'],'data_offset':int(x['data_offset']),'size':int(x['size']),
                       'filename_generation':int(x.get('filename_generation',0)),'header_patch_id':int(x.get('header_patch_id',0))} for x in members]
            rows.append({'namespace_key':f'base:{pkg.upper()}','kind':'base','locale':None,'package_id':pkg.upper(),
                         'current_member':winner['name'],'current_patch_id':int(h['patch_id']),'current_generation':int(winner.get('filename_generation',0)),
                         'language':h['language'],'language_code':int(h['language_code']),'entry_count':len(entries),'signature_counts':counts,
                         'classification':cl,'articulated_signature':cl!='no_articulated_signature',
                         'strong_character_payload_candidate':cl in {'model_resource_animation_candidate','resource_animation_candidate','model_animation_candidate'},
                         'physical_members':physical})
        except Exception as ex:violations.append({'package_id':pkg,'error':repr(ex)})
        if n%25==0 or n==len(fams):print(f'BASE FAMILIES {n}/{len(fams)} candidates={sum(x["articulated_signature"] for x in rows)} strong={sum(x["strong_character_payload_candidate"] for x in rows)}',flush=True)
    candidates=[x for x in rows if x['articulated_signature']];strong=[x for x in rows if x['strong_character_payload_candidate']]
    out={'schema':'d1_remote_character_candidate_index/v1','status':'D1_CHARACTER_CANDIDATE_INDEX_COMPLETE' if not violations else 'D1_CHARACTER_CANDIDATE_INDEX_PARTIAL',
         'scope':'base_337_fast','source':{'catalog':str(a.catalog),'catalog_sha256':hashlib.sha256(a.catalog.read_bytes()).hexdigest(),'physical_member_count':int(cat.get('physical_member_count',0))},
         'namespace_family_count':len(rows),'current_family_rows':rows,'articulated_signature_family_count':len(candidates),
         'strong_character_payload_candidate_count':len(strong),'namespace_candidate_counts':{'base':len(candidates)},
         'classification_counts':dict(classes),'signature_reference_totals':dict(ref_totals),'articulated_signature_families':candidates,
         'strong_character_payload_candidates':strong,'violations':violations,
         'policy':'Base-package acceleration census only. Exact Tiger reference classes route payload analysis; package names do not establish character semantics. Full 2,105 namespace completeness remains separately audited.'}
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ('status','namespace_family_count','articulated_signature_family_count','strong_character_payload_candidate_count','classification_counts','signature_reference_totals')},indent=2))
    return 0 if not violations else 2
if __name__=='__main__':raise SystemExit(main())
