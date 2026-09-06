#!/usr/bin/env python3
"""Build a locale-aware D1 PS4 Tiger entry index over all physical package namespaces.

Inputs:
  * exact current packages.txt;
  * the published base Activity index (1,275 ordinary members / 337 families);
  * d1_complete_physical_location_index/v1 (all 2,105 physical members);
  * the conservative export-class registry.

Logical identity is deliberately namespace-qualified:
  base:<pkgid>
  locale:<pkgid>:<locale>
  special:<physical family stem>

This prevents English/French/Japanese/etc. packages sharing a Tiger package id from
being collapsed into one logical resource namespace. Unknown classes are preserved.
No payload bodies are decompressed; only package headers and metadata tables are read.
"""
from __future__ import annotations

import argparse,csv,hashlib,io,json,re,sqlite3
from collections import Counter,defaultdict
from pathlib import Path

from d1_pkg_probe import parse_header,parse_entries,parse_named
from d1_split_tar_extract import SplitHttpTar
from d1_remote_everything_index import load_registry,classify

ENTRY_STRIDE=16;NAMED_STRIDE=68
LOCALE_LANG={'en':1,'fr':2,'it':3,'de':4,'sp':5,'jpn':6,'pt':7}
SPECIAL_GEN_RX=re.compile(r'^(.*)_([0-9]+)\.pkg$',re.I)


def sha1(b:bytes)->str:return hashlib.sha1(b).hexdigest()
def norm(s:str)->str:return str(s).upper().removeprefix('0X').zfill(8)


def special_key(name:str)->tuple[str,int]:
    m=SPECIAL_GEN_RX.match(Path(name).name)
    if not m:raise ValueError(f'cannot split special package generation: {name}')
    return f'special:{m.group(1)}',int(m.group(2))


def namespace_row(m:dict)->dict:
    kind=m['kind'];name=Path(m['name']).name
    if kind=='base':
        return {'namespace_kind':'base','namespace_key':f"base:{m['package_id']}",'locale':None,
                'filename_package_id':m['package_id'],'filename_generation':int(m['generation'])}
    if kind=='localized':
        loc=str(m['locale']).lower();return {'namespace_kind':'localized','namespace_key':f"locale:{m['package_id']}:{loc}",
                'locale':loc,'filename_package_id':m['package_id'],'filename_generation':int(m['generation'])}
    if kind=='special':
        k,g=special_key(name);return {'namespace_kind':'special','namespace_key':k,'locale':None,
                                     'filename_package_id':None,'filename_generation':g}
    raise ValueError(f'{name}: unknown namespace kind {kind!r}')


def make_db(path:Path)->sqlite3.Connection:
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():path.unlink()
    db=sqlite3.connect(path);db.executescript('''
    PRAGMA journal_mode=OFF; PRAGMA synchronous=OFF; PRAGMA temp_store=MEMORY;
    CREATE TABLE meta(key TEXT PRIMARY KEY,value TEXT NOT NULL);
    CREATE TABLE physical_packages(
      package_row INTEGER PRIMARY KEY,name TEXT NOT NULL UNIQUE,
      namespace_kind TEXT NOT NULL,namespace_key TEXT NOT NULL,locale TEXT,
      package_id TEXT NOT NULL,filename_package_id TEXT,filename_generation INTEGER NOT NULL,
      header_patch_id INTEGER NOT NULL,platform TEXT NOT NULL,platform_code INTEGER NOT NULL,
      language TEXT NOT NULL,language_code INTEGER NOT NULL,
      tar_header_offset INTEGER NOT NULL,data_offset INTEGER NOT NULL,size INTEGER NOT NULL,
      entry_table_count INTEGER,entry_table_offset INTEGER,entry_table_sha1_expected TEXT,
      named_tag_table_count INTEGER,named_tag_table_offset INTEGER,named_tag_table_sha1_expected TEXT,
      is_current INTEGER NOT NULL CHECK(is_current IN(0,1))
    );
    CREATE TABLE entry_occurrences(
      occurrence_id INTEGER PRIMARY KEY,package_row INTEGER NOT NULL,
      package_name TEXT NOT NULL,namespace_kind TEXT NOT NULL,namespace_key TEXT NOT NULL,locale TEXT,
      package_id TEXT NOT NULL,package_generation INTEGER NOT NULL,package_patch_id INTEGER NOT NULL,
      is_current INTEGER NOT NULL CHECK(is_current IN(0,1)),entry_index INTEGER NOT NULL,
      tag_hash TEXT NOT NULL,reference TEXT NOT NULL,type INTEGER NOT NULL,subtype INTEGER NOT NULL,
      entry_b TEXT NOT NULL,file_size INTEGER NOT NULL,starting_block INTEGER NOT NULL,starting_block_offset INTEGER NOT NULL,
      class_label TEXT,export_route TEXT NOT NULL,standalone_export INTEGER NOT NULL CHECK(standalone_export IN(0,1)),
      classification_source TEXT,semantic_status TEXT NOT NULL,route_tool TEXT,
      UNIQUE(package_row,entry_index)
    );
    CREATE TABLE named_tag_occurrences(
      occurrence_id INTEGER PRIMARY KEY,package_row INTEGER NOT NULL,package_name TEXT NOT NULL,
      namespace_kind TEXT NOT NULL,namespace_key TEXT NOT NULL,locale TEXT,package_id TEXT NOT NULL,
      is_current INTEGER NOT NULL CHECK(is_current IN(0,1)),named_index INTEGER NOT NULL,
      tag_hash TEXT NOT NULL,class_hash TEXT NOT NULL,name TEXT,UNIQUE(package_row,named_index)
    );
    CREATE TABLE violations(violation_id INTEGER PRIMARY KEY,package_name TEXT,stage TEXT NOT NULL,detail TEXT NOT NULL);
    CREATE INDEX idx_phys_namespace ON physical_packages(namespace_key,is_current);
    CREATE INDEX idx_entry_ns_tag ON entry_occurrences(namespace_key,tag_hash);
    CREATE INDEX idx_entry_ref ON entry_occurrences(reference);
    CREATE INDEX idx_entry_route ON entry_occurrences(export_route,is_current);
    CREATE INDEX idx_entry_current ON entry_occurrences(is_current);
    CREATE INDEX idx_named_ns_tag ON named_tag_occurrences(namespace_key,tag_hash);
    CREATE VIEW current_entries AS SELECT * FROM entry_occurrences WHERE is_current=1;
    CREATE VIEW current_logical_resources AS
      SELECT namespace_key,tag_hash,COUNT(*) occurrence_count,
             COUNT(DISTINCT package_name) package_occurrence_count,
             GROUP_CONCAT(DISTINCT reference) reference_values,
             GROUP_CONCAT(DISTINCT export_route) export_routes,
             MAX(class_label) class_label,MAX(standalone_export) any_standalone_export
      FROM entry_occurrences WHERE is_current=1 GROUP BY namespace_key,tag_hash;
    ''');return db


def header_from_remote(arc:SplitHttpTar,m:dict)->dict:
    b=arc.read_at(int(m['data_offset']),0x140);h=parse_header(io.BytesIO(b))
    if int(h['version'])!=24:raise ValueError(f"version {h['version']} != 24")
    if h['platform']!='PS4':raise ValueError(f"platform {h['platform']} != PS4")
    return h


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--package-list',type=Path,required=True);ap.add_argument('--activity-index',type=Path,required=True)
    ap.add_argument('--location-index',type=Path,required=True);ap.add_argument('--registry',type=Path,required=True)
    ap.add_argument('--sqlite',type=Path,required=True);ap.add_argument('--summary',type=Path,required=True);ap.add_argument('--queue',type=Path,required=True)
    ap.add_argument('--base-url',default='https://crypt.cohae.dev/destiny/ps4/packages/latest');ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--retries',type=int,default=6);ap.add_argument('--timeout',type=int,default=120)
    a=ap.parse_args();registry=load_registry(a.registry)

    pbytes=a.package_list.read_bytes();psha=hashlib.sha256(pbytes).hexdigest()
    activity=json.loads(a.activity_index.read_text());loc=json.loads(a.location_index.read_text())
    if activity.get('status')!='D1_REMOTE_ACTIVITY_INDEX_COMPLETE':raise ValueError('Activity index not complete')
    if loc.get('status')!='D1_COMPLETE_PHYSICAL_LOCATION_INDEX_EXACT':raise ValueError('complete location index not exact')
    if psha!=(activity.get('source') or {}).get('package_list_sha256') or psha!=(loc.get('source') or {}).get('package_list_sha256'):
        raise ValueError('package-list SHA mismatch across inputs')
    wanted={Path(x.strip()).name for x in pbytes.decode('utf-8',errors='replace').splitlines() if x.strip().lower().endswith('.pkg')}
    members=list(loc['members']);byname={Path(x['name']).name:x for x in members}
    if set(byname)!=wanted or len(byname)!=len(members):raise ValueError('complete location member set != packages.txt')

    base_meta={}
    for _pkg,rows in (activity.get('package_families') or {}).items():
        for r in rows:base_meta[Path(r['name']).name]=r
    current_base={Path(x['name']).name for x in activity.get('current_packages',[])}
    if len(current_base)!=int(activity.get('current_package_count',-1)):raise ValueError('Activity current-base count mismatch')

    base=a.base_url.rstrip('/');arc=SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1,a.part_count+1)],retries=a.retries,timeout=a.timeout)
    if arc.sizes!=[int(x) for x in loc['source']['part_sizes']]:raise ValueError('split TAR part sizes changed')

    rows=[];viol=[];header_reads=0
    # Base superseded members reuse already-validated Activity header metadata;
    # current base members are reread because their entry-table fields are needed.
    for n,m in enumerate(members,1):
        ns=namespace_row(m);name=Path(m['name']).name;kind=ns['namespace_kind'];h=None
        need_header=(kind!='base' or name in current_base)
        try:
            if need_header:
                h=header_from_remote(arc,m);header_reads+=1
            else:
                bm=base_meta.get(name)
                if bm is None:raise ValueError('base member absent from exact Activity metadata')
                h={'pkg_id':int(bm['package_id'],16),'patch_id':int(bm['header_patch_id']),
                   'platform':'PS4','platform_code':int(bm['platform_code']),
                   'language':'None' if int(bm['language_code'])==0 else f"Code({bm['language_code']})",'language_code':int(bm['language_code']),
                   'entry_table_count':None,'entry_table_offset':None,'entry_table_hash':None,
                   'named_tag_table_count':int(bm.get('named_tag_table_count',0)),'named_tag_table_offset':int(bm.get('named_tag_table_offset',0)),
                   'named_tag_table_hash':str(bm.get('named_tag_table_hash',''))}
            pkg=f"{int(h['pkg_id']):04X}"
            if ns['filename_package_id'] is not None and pkg!=ns['filename_package_id']:
                raise ValueError(f'filename package {ns["filename_package_id"]} != header {pkg}')
            if kind=='localized':
                expected_lang=LOCALE_LANG.get(ns['locale'])
                if expected_lang is None or int(h['language_code'])!=expected_lang:
                    raise ValueError(f'locale {ns["locale"]} expects language {expected_lang}, header has {h["language_code"]}')
            row={**ns,'name':name,'package_id':pkg,'header_patch_id':int(h['patch_id']),
                 'platform':h['platform'],'platform_code':int(h['platform_code']),'language':h['language'],'language_code':int(h['language_code']),
                 'tar_header_offset':int(m['tar_header_offset']),'data_offset':int(m['data_offset']),'size':int(m['size']),
                 'entry_table_count':h.get('entry_table_count'),'entry_table_offset':h.get('entry_table_offset'),'entry_table_sha1_expected':h.get('entry_table_hash'),
                 'named_tag_table_count':h.get('named_tag_table_count'),'named_tag_table_offset':h.get('named_tag_table_offset'),'named_tag_table_sha1_expected':h.get('named_tag_table_hash'),
                 'is_current':False}
            rows.append(row)
        except Exception as ex:viol.append({'package_name':name,'stage':'header','detail':repr(ex)})
        if n%200==0 or n==len(members):print(f'HEADER_METADATA {n}/{len(members)} remote_reads={header_reads}',flush=True)
    if len(rows)!=len(members):raise SystemExit(f'header metadata failed for {len(members)-len(rows)} physical packages: {viol[:20]}')

    groups=defaultdict(list)
    for i,r in enumerate(rows):groups[r['namespace_key']].append(i)
    for key,ids in groups.items():
        if key.startswith('base:'):
            candidates=[i for i in ids if rows[i]['name'] in current_base]
            if len(candidates)!=1:raise ValueError(f'{key}: expected exactly one Activity current base member, got {candidates}')
            winner=candidates[0]
        else:
            winner=max(ids,key=lambda i:(rows[i]['header_patch_id'],rows[i]['filename_generation'],rows[i]['name']))
        rows[winner]['is_current']=True
    current_rows=[r for r in rows if r['is_current']]

    # Every current row must have an exact reread header; base current already does,
    # locale/special all do. This is the only set whose entry tables are indexed.
    db=make_db(a.sqlite)
    try:
        db.executemany('INSERT INTO meta VALUES(?,?)',[
          ('schema','d1_remote_everything_index/v2'),('packages_txt_sha256',psha),('physical_member_count',str(len(rows))),
          ('namespace_count',str(len(groups))),('remote_header_read_count',str(header_reads))])
        for i,r in enumerate(rows):
            db.execute('INSERT INTO physical_packages VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(
              i,r['name'],r['namespace_kind'],r['namespace_key'],r['locale'],r['package_id'],r['filename_package_id'],r['filename_generation'],
              r['header_patch_id'],r['platform'],r['platform_code'],r['language'],r['language_code'],r['tar_header_offset'],r['data_offset'],r['size'],
              r['entry_table_count'],r['entry_table_offset'],r['entry_table_sha1_expected'],r['named_tag_table_count'],r['named_tag_table_offset'],
              r['named_tag_table_sha1_expected'],int(r['is_current'])))

        refc=Counter();typec=Counter();routec=Counter();classc=Counter();nsc=Counter();kind_entry=Counter();named_count=0
        entry_total=0;occ=0;noc=0
        for n,r in enumerate(current_rows,1):
            et_count=int(r['entry_table_count'] or 0);et_off=int(r['entry_table_offset'] or 0);et_n=et_count*ENTRY_STRIDE
            if et_off<0 or et_off+et_n>r['size']:
                viol.append({'package_name':r['name'],'stage':'entry_table','detail':f'bounds {et_off}+{et_n}>{r["size"]}'});continue
            try:et=arc.read_at(r['data_offset']+et_off,et_n)
            except Exception as ex:viol.append({'package_name':r['name'],'stage':'entry_table','detail':repr(ex)});continue
            if sha1(et)!=str(r['entry_table_sha1_expected']).lower():
                viol.append({'package_name':r['name'],'stage':'entry_table','detail':'SHA1 mismatch'});continue
            entries=parse_entries(et,int(r['package_id'],16));entry_total+=len(entries)
            prow=rows.index(r)
            for e in entries:
                c=classify(e,registry);ref=norm(e['reference']);key=f"{e['type']}:{e['subtype']}"
                db.execute('INSERT INTO entry_occurrences VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(
                  occ,prow,r['name'],r['namespace_kind'],r['namespace_key'],r['locale'],r['package_id'],r['filename_generation'],r['header_patch_id'],1,
                  e['index'],e['tag_hash'].upper(),ref,e['type'],e['subtype'],e['entry_b'].upper(),e['file_size'],e['starting_block'],e['starting_block_offset'],
                  c['class_label'],c['export_route'],int(c['standalone_export']),c['classification_source'],c['semantic_status'],c['route_tool']));occ+=1
                refc[ref]+=1;typec[key]+=1;routec[c['export_route']]+=1;nsc[r['namespace_key']]+=1;kind_entry[r['namespace_kind']]+=1
                if c['class_label']:classc[c['class_label']]+=1

            nt_count=int(r['named_tag_table_count'] or 0);nt_off=int(r['named_tag_table_offset'] or 0);nt_n=nt_count*NAMED_STRIDE
            if nt_count:
                if nt_off<0 or nt_off+nt_n>r['size']:
                    viol.append({'package_name':r['name'],'stage':'named_table','detail':f'bounds {nt_off}+{nt_n}>{r["size"]}'});continue
                try:nt=arc.read_at(r['data_offset']+nt_off,nt_n)
                except Exception as ex:viol.append({'package_name':r['name'],'stage':'named_table','detail':repr(ex)});continue
                expected=str(r['named_tag_table_sha1_expected']).lower()
                if expected and sha1(nt)!=expected:
                    viol.append({'package_name':r['name'],'stage':'named_table','detail':'SHA1 mismatch'});continue
                for q in parse_named(nt):
                    db.execute('INSERT INTO named_tag_occurrences VALUES(?,?,?,?,?,?,?,?,?,?,?)',(
                      noc,prow,r['name'],r['namespace_kind'],r['namespace_key'],r['locale'],r['package_id'],1,q['index'],q['tag_hash'].upper(),q['class_hash'].upper(),q.get('name')))
                    noc+=1;named_count+=1
            if n%50==0 or n==len(current_rows):print(f'CURRENT_TABLES {n}/{len(current_rows)} entries={entry_total}',flush=True)

        for v in viol:db.execute('INSERT INTO violations(package_name,stage,detail) VALUES(?,?,?)',(v.get('package_name'),v['stage'],v['detail']))
        db.commit()
        logical=db.execute('SELECT COUNT(*) FROM current_logical_resources').fetchone()[0]
        standalone=sum(v for k,v in routec.items() if k in {str(x.get('export_route')) for x in (registry.get('reference_classes') or {}).values() if x.get('standalone_export')} | {str(x.get('export_route')) for x in (registry.get('type_subtype_classes') or {}).values() if x.get('standalone_export')})
        unknown=routec.get('unknown',0)
        kinds=Counter(r['namespace_kind'] for r in rows);current_kinds=Counter(r['namespace_kind'] for r in current_rows)
        summary={'schema':'d1_remote_everything_index/v2','status':'D1_REMOTE_EVERYTHING_INDEX_V2_COMPLETE' if not viol else 'D1_REMOTE_EVERYTHING_INDEX_V2_WITH_VIOLATIONS',
          'source':{'packages_txt_sha256':psha,'physical_location_index_sha256':hashlib.sha256(a.location_index.read_bytes()).hexdigest(),
                    'activity_index_sha256':hashlib.sha256(a.activity_index.read_bytes()).hexdigest(),'remote_header_reads':header_reads},
          'physical_member_count':len(rows),'namespace_count':len(groups),'namespace_kind_physical_counts':dict(kinds),
          'current_namespace_count':len(current_rows),'current_namespace_kind_counts':dict(current_kinds),
          'current_entry_count':entry_total,'current_logical_resource_count':logical,'current_named_tag_count':named_count,
          'current_reference_counts':dict(refc.most_common()),'current_type_subtype_counts':dict(typec.most_common()),
          'current_export_route_counts':dict(routec.most_common()),'current_class_label_counts':dict(classc.most_common()),
          'current_entry_namespace_kind_counts':dict(kind_entry),'current_unknown_entry_count':unknown,
          'violations':viol,
          'policy':'All 2,105 physical packages are represented. Current logical selection is namespace-aware, so localized variants sharing a Tiger package id remain distinct. Unknown classes remain explicit.'}
        a.summary.parent.mkdir(parents=True,exist_ok=True);a.summary.write_text(json.dumps(summary,indent=2)+'\n')
        fields=['package_name','namespace_kind','namespace_key','locale','package_id','entry_index','tag_hash','reference','type','subtype','file_size','class_label','export_route','standalone_export','semantic_status','route_tool']
        with a.queue.open('w',newline='',encoding='utf-8') as f:
            w=csv.writer(f,delimiter='\t');w.writerow(fields)
            for q in db.execute('SELECT package_name,namespace_kind,namespace_key,locale,package_id,entry_index,tag_hash,reference,type,subtype,file_size,class_label,export_route,standalone_export,semantic_status,route_tool FROM current_entries ORDER BY namespace_key,entry_index'):
                w.writerow(q)
        print(json.dumps({k:summary[k] for k in ('status','physical_member_count','namespace_count','current_namespace_count','current_namespace_kind_counts','current_entry_count','current_logical_resource_count','current_named_tag_count','current_export_route_counts','current_unknown_entry_count')},indent=2))
        return 0 if not viol else 2
    finally:db.close()

if __name__=='__main__':raise SystemExit(main())
