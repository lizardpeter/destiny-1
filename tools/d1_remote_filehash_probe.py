#!/usr/bin/env python3
"""Probe arbitrary D1 FileHashes directly from the current split-TAR corpus.

For every requested FileHash this tool:
  1. derives the Tiger package id / file index from the hash;
  2. resolves only that package id's current physical siblings from packages.txt;
  3. locates the exact members in the checksum-addressed split TAR;
  4. builds the current logical package view with RemoteLogicalPackage;
  5. reads the exact target entry and records payload SHA-256/prefix;
  6. if the entry is EntityResource / 80800861, applies the shared source-pinned
     d1_entity_resource_probe parser;
  7. reports aligned dword values that resolve to real entries in the same mounted
     package family.

Package filenames are used only after package-id derivation to locate physical
siblings. They are not semantic asset ownership evidence.
"""
from __future__ import annotations

import argparse,hashlib,json,re,struct,sys
from collections import defaultdict
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_investment_arrangement_probe import filehash_pkg_index
from d1_remote_investment_parent_probe import RemoteLogicalPackage,parse_member
from d1_split_tar_extract import SplitHttpTar
from d1_entity_resource_probe import ENTITY_RESOURCE_CLASS,parse_resource

NULLS={'00000000','FFFFFFFF'}

def norm(x):
 x=str(x).upper().removeprefix('0X').zfill(8);int(x,16);return x

def current_family_names(package_list:Path,pkgid:int):
 token=f'{pkgid:04x}'
 names=[]
 for line in package_list.read_text(errors='replace').splitlines():
  name=Path(line.strip()).name
  if re.search(rf'_{token}_[0-9]+\.pkg$',name,re.I):names.append(name)
 return sorted(set(names))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--tag-hash',action='append',required=True)
 ap.add_argument('--package-list',type=Path,required=True);ap.add_argument('--runtime',type=Path,required=True)
 ap.add_argument('--base-url',default='https://crypt.cohae.dev/destiny/ps4/packages/latest');ap.add_argument('--part-count',type=int,default=10)
 ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 wanted=[norm(x) for x in a.tag_hash if norm(x) not in NULLS]
 by_pkg=defaultdict(list)
 for h in wanted:
  pkg,idx=filehash_pkg_index(int(h,16));by_pkg[pkg].append((h,idx))
 base=a.base_url.rstrip('/');arc=SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1,a.part_count+1)],retries=6,timeout=120)
 package_views={};package_rows={};viol=[]
 for pkg in sorted(by_pkg):
  names=current_family_names(a.package_list,pkg)
  pr={'package_id':f'{pkg:04X}','current_members':names,'member_locations':{},'violations':[]}
  if not names:
   pr['violations'].append('package_family_absent_from_packages_list');package_rows[pkg]=pr;continue
  found,headers=arc.find(set(names));pr['tar_headers_scanned']=headers
  missing=sorted(set(names)-set(found))
  if missing:pr['violations'].append('archive_members_missing:'+','.join(missing));package_rows[pkg]=pr;continue
  specs=[]
  for name in names:
   r=found[name];pr['member_locations'][name]=r;specs.append(parse_member(f"{name}:0x{int(r['data_offset']):X}:{int(r['size'])}"))
  try:
   view=RemoteLogicalPackage(arc,{m.patch_id:m for m in specs},a.runtime);package_views[pkg]=view
   pr['logical_view']=view.view.name;pr['entry_count']=len(view.entries);pr['block_count']=len(view.blocks)
  except Exception as ex:pr['violations'].append('logical_package_build:'+repr(ex))
  package_rows[pkg]=pr
  viol.extend(f'{pkg:04X}:{x}' for x in pr['violations'])
 rows=[]
 for h,idx in [(h,idx) for pkg in sorted(by_pkg) for h,idx in by_pkg[pkg]]:
  pkg,_=filehash_pkg_index(int(h,16));view=package_views.get(pkg);row={'tag_hash':h,'package_id':f'{pkg:04X}','file_index':idx,'violations':[]}
  if view is None:row['violations'].append('package_view_unavailable');rows.append(row);continue
  if idx>=len(view.entries):row['violations'].append('file_index_outside_current_entry_table');rows.append(row);continue
  e=view.entries[idx];row['entry']={k:e[k] for k in ('index','tag_hash','reference','type','subtype','file_size','starting_block','starting_block_offset') if k in e}
  row['entry']['tag_hash']=row['entry']['tag_hash'].upper();row['entry']['reference']=row['entry']['reference'].upper()
  if row['entry']['tag_hash']!=h:row['violations'].append('logical_tag_hash_mismatch');rows.append(row);continue
  try:b=view.entry(idx)
  except Exception as ex:row['violations'].append('payload_read:'+repr(ex));rows.append(row);continue
  row['payload_size']=len(b);row['payload_sha256']=hashlib.sha256(b).hexdigest();row['prefix128']=b[:128].hex();row['suffix64']=b[-64:].hex()
  if row['entry']['reference']==ENTITY_RESOURCE_CLASS:
   try:row['entity_resource']=parse_resource(b,'PS4')
   except Exception as ex:row['entity_resource_error']=repr(ex);row['violations'].append('entity_resource_parse:'+repr(ex))
  matches=[];end=len(b)-(len(b)%4)
  for off in range(0,end,4):
   v=struct.unpack_from('<I',b,off)[0];vpkg,vidx=filehash_pkg_index(v);vv=package_views.get(vpkg)
   if vv is None or vidx>=len(vv.entries):continue
   ve=vv.entries[vidx]
   if int(ve['tag_hash'],16)!=v:continue
   matches.append({'offset':off,'tag_hash':f'{v:08X}','reference':ve['reference'].upper(),'type':ve['type'],'subtype':ve['subtype'],'size':ve['file_size']})
  row['aligned_resolved_tag_matches']=matches
  # Preserve a small exact neighborhood from the logical entry table as structural context.
  nb=[]
  for j in range(max(0,idx-8),min(len(view.entries),idx+9)):
   ne=view.entries[j];nb.append({'relative_index':j-idx,'index':j,'tag_hash':ne['tag_hash'].upper(),'reference':ne['reference'].upper(),'type':ne['type'],'subtype':ne['subtype'],'size':ne['file_size']})
  row['neighborhood']=nb;rows.append(row);viol.extend(f'{h}:{x}' for x in row['violations'])
 out={'schema_version':1,'status':'D1_REMOTE_FILEHASH_PROBE_COMPLETE' if not viol else 'D1_REMOTE_FILEHASH_PROBE_PARTIAL',
      'requested':wanted,'package_count':len(by_pkg),'packages':[package_rows[p] for p in sorted(package_rows)],'entries':rows,'violations':viol,
      'policy':'Target identity comes only from Tiger FileHash package/index derivation and current logical package tables. Filenames locate derived package families but do not assign semantic ownership.'}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
 compact=[]
 for r in rows:
  er=r.get('entity_resource') or {};compact.append({'tag_hash':r['tag_hash'],'package_id':r['package_id'],'entry':r.get('entry'),
    'payload_size':r.get('payload_size'),'semantic_role':er.get('semantic_role'),'unk10_class':(er.get('unk10') or {}).get('class_hash'),
    'unk18_class':(er.get('unk18') or {}).get('class_hash'),'embedded_model_tag_hash':er.get('embedded_model_tag_hash'),
    'embedded_physics_model_tag_hash':er.get('embedded_physics_model_tag_hash'),'violations':r['violations']})
 print(json.dumps({'status':out['status'],'entries':compact,'violations':viol},indent=2));return 0 if not viol else 2
if __name__=='__main__':raise SystemExit(main())
