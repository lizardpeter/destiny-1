#!/usr/bin/env python3
"""Probe exact D1 EntityResource FileHashes through a verified universal catalog.

This avoids re-discovering split-TAR members for every ownership trace. FileHash
package/index identity chooses the logical package, the verified catalog chooses its
physical members, and the shared source-pinned EntityResource parser decodes the
three ResourcePointers and known roles. The report also preserves every aligned u32
that resolves to a real current entry so unknown EntityResource schemas can be
closed without losing raw dependency evidence.
"""
from __future__ import annotations
import argparse,collections,hashlib,json,struct,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_crota_raid_candidate_probe import LazyExactHashResolver
from d1_entity_resource_probe import ENTITY_RESOURCE_CLASS,parse_resource
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_split_tar_extract import SplitHttpTar

NULLS={'00000000','FFFFFFFF'}
def norm(x):
 x=str(x).upper().removeprefix('0X').zfill(8);int(x,16);return x

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--tag-hash',action='append',required=True)
 ap.add_argument('--member-catalog',type=Path,action='append',required=True)
 ap.add_argument('--base-url',required=True);ap.add_argument('--part-count',type=int,default=10)
 ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('-o','--output',type=Path,required=True);a=ap.parse_args()
 cats=load_catalogs(a.member_catalog);base=a.base_url.rstrip('/')
 arc=SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1,a.part_count+1)],retries=6,timeout=90)
 r=LazyExactHashResolver(arc,cats,a.runtime);rows=[];viol=[]
 for h0 in dict.fromkeys(a.tag_hash):
  h=norm(h0);row={'tag_hash':h,'violations':[]}
  try:view,e=r.locate(h)
  except Exception as ex:row['violations'].append('locate:'+repr(ex));rows.append(row);continue
  row['package_id']=f"{int(view.h['pkg_id']):04X}";row['logical_view']=view.view.name
  row['entry']={k:e[k] for k in ('index','tag_hash','reference','type','subtype','file_size')};row['entry']['tag_hash']=row['entry']['tag_hash'].upper();row['entry']['reference']=row['entry']['reference'].upper()
  if row['entry']['reference']!=ENTITY_RESOURCE_CLASS:row['violations'].append('reference_not_80800861');rows.append(row);continue
  try:b=view.entry(e['index'])
  except Exception as ex:row['violations'].append('payload:'+repr(ex));rows.append(row);continue
  row['payload_size']=len(b);row['payload_sha256']=hashlib.sha256(b).hexdigest();row['prefix128']=b[:128].hex();row['suffix128']=b[-128:].hex()
  try:row['entity_resource']=parse_resource(b,'PS4')
  except Exception as ex:row['violations'].append('parse_resource:'+repr(ex))
  matches=[];end=len(b)-(len(b)%4)
  for off in range(0,end,4):
   v=struct.unpack_from('<I',b,off)[0];vh=f'{v:08X}'
   if vh in NULLS:continue
   try:vv,ve=r.locate(vh)
   except Exception:continue
   matches.append({'offset':off,'offset_hex':f'0x{off:X}','tag_hash':vh,'package_id':f"{int(vv.h['pkg_id']):04X}",'reference':ve['reference'].upper(),'type':int(ve['type']),'subtype':int(ve['subtype']),'size':int(ve['file_size'])})
  row['aligned_resolved_tag_matches']=matches
  # Record exact local byte neighborhoods around every resolved match without interpreting unknown fields.
  row['match_neighborhoods']=[{'offset':m['offset'],'tag_hash':m['tag_hash'],'start':max(0,m['offset']-32),'end':min(len(b),m['offset']+36),'bytes_hex':b[max(0,m['offset']-32):min(len(b),m['offset']+36)].hex()} for m in matches]
  rows.append(row);viol.extend(f'{h}:{x}' for x in row['violations'])
 out={'schema':'d1_remote_catalog_entity_resource_probe/v1','status':'D1_CATALOG_ENTITY_RESOURCE_PROBE_EXACT' if not viol else 'D1_CATALOG_ENTITY_RESOURCE_PROBE_PARTIAL','entries':rows,'violations':viol,
      'policy':'FileHash routing and current logical-package identity are exact. Known EntityResource roles come only from the shared source-pinned parser. Aligned resolved tags inside unknown schemas are preserved as literal dependencies, not assigned semantics.'}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n')
 for x in rows:
  er=x.get('entity_resource') or {};print('RESOURCE',x['tag_hash'],'PKG',x.get('package_id'),'ROLE',er.get('semantic_role'),'UNK10',(er.get('unk10') or {}).get('class_hash'),'UNK18',(er.get('unk18') or {}).get('class_hash'),'MATCHES',[(m['offset_hex'],m['tag_hash'],m['reference']) for m in x.get('aligned_resolved_tag_matches',[])])
 print('STATUS',out['status'],'VIOLATIONS',viol);return 0 if not viol else 2
if __name__=='__main__':raise SystemExit(main())
