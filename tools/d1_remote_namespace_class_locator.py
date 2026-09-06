#!/usr/bin/env python3
"""Locate exact D1 file-entry Reference classes across archive namespaces.

Unlike d1_remote_class_locator.py, this consumes the exact 2,105-member physical
location index and preserves base/localized/special namespace identity. It reads
only package headers and current logical entry tables; no payload is decompressed.
Localized namespaces are never collapsed into base even when Tiger package ids are
identical.
"""
from __future__ import annotations
import argparse,collections,hashlib,io,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_pkg_probe import parse_header,parse_entries
from d1_remote_character_candidate_index import namespace_key,key_text,generation
from d1_split_tar_extract import SplitHttpTar
ENTRY_STRIDE=16

def norm(x):return str(x).upper().removeprefix('0X').zfill(8)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--location-index',type=Path,required=True);ap.add_argument('--reference',action='append',required=True)
 ap.add_argument('--kind',choices=('base','localized','special'));ap.add_argument('--locale');ap.add_argument('--base-url',default='https://crypt.cohae.dev/destiny/ps4/packages/latest');ap.add_argument('--part-count',type=int,default=10)
 ap.add_argument('-o','--output',type=Path,required=True);ap.add_argument('--retries',type=int,default=6);ap.add_argument('--timeout',type=int,default=120);a=ap.parse_args()
 src=json.loads(a.location_index.read_text())
 if src.get('schema')!='d1_complete_physical_location_index/v1' or src.get('status')!='D1_COMPLETE_PHYSICAL_LOCATION_INDEX_EXACT':raise ValueError('location index is not exact')
 members=list(src.get('members') or []);targets={norm(x) for x in a.reference};base=a.base_url.rstrip('/')
 arc=SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1,a.part_count+1)],retries=a.retries,timeout=a.timeout)
 fam=collections.defaultdict(list);viol=[]
 for m in members:
  kind=str(m.get('kind') or '')
  if a.kind and kind!=a.kind:continue
  if a.locale and str(m.get('locale') or '').lower()!=a.locale.lower():continue
  name=Path(str(m['name'])).name;off=int(m['data_offset']);size=int(m['size'])
  try:h=parse_header(io.BytesIO(arc.read_at(off,0x140)))
  except Exception as ex:viol.append({'name':name,'stage':'header','error':repr(ex)});continue
  mm={**m,'package_id':f"{int(h['pkg_id']):04X}"}
  fam[key_text(namespace_key(mm))].append({'name':name,'kind':kind,'locale':m.get('locale'),'package_id':mm['package_id'],'data_offset':off,'size':size,'filename_generation':int(m.get('generation') if m.get('generation') is not None else generation(name)),'header_patch_id':int(h['patch_id']),'entry_table_count':int(h['entry_table_count']),'entry_table_offset':int(h['entry_table_offset']),'entry_table_sha1_expected':str(h['entry_table_hash']).lower(),'language':h['language'],'language_code':int(h['language_code'])})
 current=[]
 for key,rows in sorted(fam.items()):current.append((key,max(rows,key=lambda r:(r['header_patch_id'],r['filename_generation'],r['name'])),rows))
 hits=[];counts=collections.Counter()
 for i,(key,p,phys) in enumerate(current,1):
  n=p['entry_table_count']*ENTRY_STRIDE;o=p['entry_table_offset']
  try:raw=arc.read_at(p['data_offset']+o,n)
  except Exception as ex:viol.append({'namespace_key':key,'stage':'entry_table','error':repr(ex)});continue
  got=hashlib.sha1(raw).hexdigest()
  if got!=p['entry_table_sha1_expected']:viol.append({'namespace_key':key,'stage':'entry_table','error':f'sha1 {got} != {p["entry_table_sha1_expected"]}'});continue
  entries=parse_entries(raw,int(p['package_id'],16));refs=collections.Counter(e['reference'].upper() for e in entries)
  for ref in targets:
   if refs.get(ref):
    erows=[{'tag_hash':e['tag_hash'].upper(),'entry_index':int(e['index']),'type':int(e['type']),'subtype':int(e['subtype']),'file_size':int(e['file_size'])} for e in entries if e['reference'].upper()==ref]
    hits.append({'namespace_key':key,'kind':p['kind'],'locale':p.get('locale'),'package_id':p['package_id'],'current_member':p['name'],'reference':ref,'count':len(erows),'entries':erows,'physical_members':sorted([{'name':x['name'],'data_offset':x['data_offset'],'size':x['size'],'generation':x['filename_generation'],'patch_id':x['header_patch_id']} for x in phys],key=lambda x:(x['patch_id'],x['generation'],x['name']))});counts[ref]+=len(erows)
  if i%25==0 or i==len(current):print('SCANNED',i,'/',len(current),'HIT_NAMESPACES',len(hits),flush=True)
 out={'schema':'d1_remote_namespace_class_locator/v1','status':'D1_NAMESPACE_CLASS_LOCATOR_COMPLETE' if not viol else 'D1_NAMESPACE_CLASS_LOCATOR_PARTIAL','filters':{'kind':a.kind,'locale':a.locale},'physical_member_count_scanned':sum(len(x[2]) for x in current),'namespace_family_count':len(current),'target_references':sorted(targets),'hit_namespace_count':len(hits),'occurrence_counts':dict(counts),'hits':hits,'violations':viol,'policy':'Exact current logical namespace entry-table Reference identity only. Localized namespaces remain isolated even when FileHashes/package ids overlap.'}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k not in ('hits','violations')},indent=2));
 for h in hits:print('HIT',h['namespace_key'],h['current_member'],h['reference'],[x['tag_hash'] for x in h['entries']])
 return 0 if not viol else 2
if __name__=='__main__':raise SystemExit(main())
