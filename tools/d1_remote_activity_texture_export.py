#!/usr/bin/env python3
"""Materialize exact PS4 textures from a D1 activity material dependency closure.

This is deliberately downstream of ``d1_remote_activity_material_dependency_closure``:
it does not rediscover material ownership or assign shader/PBR semantics. It consumes
the already-proven Texture2D header/backing identities, fetches the exact backing
payload from the universal retail corpus, validates top-level size, unswizzles PS4
GCN layout when required, and writes DDS plus PNG when the existing decoder supports
the native format.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))

from d1_texture_export import decode_header,expected_base_size,unswizzle_ps4,make_dds,FORMAT_NAME
from d1_dds_to_png import decode_dds
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_activity_placements import RemoteCorpus
from d1_split_tar_extract import SplitHttpTar


def norm(v:object)->str:return str(v).upper().removeprefix('0X').zfill(8)
def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()

def collect_textures(doc:dict)->dict[str,dict]:
 out={}
 for mr in doc.get('rows',[]):
  for stage in ('vertex','pixel'):
   for tr in mr.get('dependencies',{}).get(stage,{}).get('textures',[]):
    h=norm(tr['texture'])
    sig={'header_info':tr.get('header_info'),'final_payload_hash':tr.get('final_payload_hash'),
         'final_payload_type_subtype':tr.get('final_payload_type_subtype')}
    old=out.get(h)
    if old is not None and old!=sig:raise ValueError(f'conflicting exact texture closure rows for {h}: {old} vs {sig}')
    out[h]=sig
 return out

def main()->int:
 ap=argparse.ArgumentParser();ap.add_argument('--material-closure',type=Path,required=True)
 ap.add_argument('--member-catalog',type=Path,action='append',required=True);ap.add_argument('--base-url',required=True);ap.add_argument('--part-count',type=int,default=10)
 ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('--out-dir',type=Path,required=True);a=ap.parse_args()
 doc=json.loads(a.material_closure.read_text())
 if doc.get('schema')!='d1_remote_activity_material_dependency_closure/v1':raise SystemExit('unexpected material closure schema')
 if doc.get('status') not in {'D1_REMOTE_ACTIVITY_MATERIAL_DEPENDENCY_CLOSURE_COMPLETE','D1_REMOTE_ACTIVITY_MATERIAL_DEPENDENCY_CLOSURE_PARTIAL_VARIANT_FRONTIER'}:raise SystemExit('material closure has dependency violations')
 if doc.get('violations'):raise SystemExit('material closure contains violations')
 tex=collect_textures(doc);catalogs=load_catalogs(a.member_catalog);base=a.base_url.rstrip('/')
 arc=SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1,a.part_count+1)],retries=6,timeout=90);c=RemoteCorpus(arc,catalogs,a.runtime)
 a.out_dir.mkdir(parents=True,exist_ok=True);td=a.out_dir/'textures';td.mkdir(parents=True,exist_ok=True)
 rows=[];viol=[]
 for i,(h,proof) in enumerate(sorted(tex.items()),1):
  print('TEXTURE',i,'/',len(tex),h,flush=True);row={'texture':h,'proof':proof,'files':[],'violations':[]}
  hm=c.entry_meta(h);hb,hsrc=c.payload(h);row['header_source']=hsrc
  if hm is None or hb is None:row['violations'].append('header_unavailable')
  else:
   try:hdr=decode_header(hb)
   except Exception as ex:row['violations'].append('header_decode:'+repr(ex));hdr=None
   if hdr is not None:
    prior=proof.get('header_info') or {}
    for k in ('width','height','surface_format','array_size','flags1','flags2','flags3'):
     if k in prior and prior[k]!=hdr.get(k):row['violations'].append(f'header_drift:{k}:{prior[k]}!={hdr.get(k)}')
    row['header_info']=hdr;back=proof.get('final_payload_hash')
    if not back:row['violations'].append('no_proven_final_payload')
    else:
     back=norm(back);bm=c.entry_meta(back);raw,bsrc=c.payload(back);row['backing_hash']=back;row['backing_meta']=bm;row['backing_source']=bsrc
     if raw is None:row['violations'].append('backing_payload_unavailable')
     else:
      expected=expected_base_size(hdr['width'],hdr['height'],hdr['surface_format'],hdr['array_size']);row['expected_base_size']=expected;row['backing_bytes']=len(raw);row['backing_sha256']=sha(raw)
      if expected is None:row['violations'].append(f'unsupported_surface_format:{hdr["surface_format"]:#x}')
      elif len(raw)<expected:row['violations'].append(f'backing_short:{len(raw)}<{expected}')
      else:
       raw=raw[:expected];swizzled=((hdr['flags1']&0xC00)!=0x400) or hdr['array_size']==6;row['swizzled']=swizzled
       try:linear=unswizzle_ps4(raw,hdr['width'],hdr['height'],hdr['array_size'],hdr['surface_format']) if swizzled else raw
       except Exception as ex:row['violations'].append('unswizzle:'+repr(ex));linear=None
       if linear is not None:
        row['linear_bytes']=len(linear);row['linear_sha256']=sha(linear);fmt=FORMAT_NAME.get(hdr['surface_format'],f'GCN{hdr["surface_format"]:02X}');row['format_name']=fmt;stem=f'{h}_{hdr["width"]}x{hdr["height"]}_{fmt}'
        if hdr['array_size']==1:
         try:
          dds=make_dds(linear,hdr['width'],hdr['height'],hdr['surface_format']);dp=td/(stem+'.dds');dp.write_bytes(dds);row['files'].append({'kind':'dds','path':str(dp.relative_to(a.out_dir)),'bytes':len(dds),'sha256':sha(dds)})
          try:
           im=decode_dds(dp);pp=td/(stem+'.png');im.save(pp);pb=pp.read_bytes();row['files'].append({'kind':'png','path':str(pp.relative_to(a.out_dir)),'bytes':len(pb),'sha256':sha(pb)})
          except Exception as ex:row['png_error']=repr(ex)
         except Exception as ex:row['violations'].append('dds_export:'+repr(ex))
        elif hdr['array_size']==6:
         per=expected_base_size(hdr['width'],hdr['height'],hdr['surface_format'],1)
         if per is None or len(linear)<per*6:row['violations'].append('cubemap_face_sizing')
         else:
          for face in range(6):
           fb=linear[face*per:(face+1)*per]
           try:
            dds=make_dds(fb,hdr['width'],hdr['height'],hdr['surface_format'],1);dp=td/f'{stem}_face{face}.dds';dp.write_bytes(dds);row['files'].append({'kind':'dds','face':face,'path':str(dp.relative_to(a.out_dir)),'bytes':len(dds),'sha256':sha(dds)})
            try:
             im=decode_dds(dp);pp=td/f'{stem}_face{face}.png';im.save(pp);pb=pp.read_bytes();row['files'].append({'kind':'png','face':face,'path':str(pp.relative_to(a.out_dir)),'bytes':len(pb),'sha256':sha(pb)})
            except Exception as ex:row.setdefault('png_errors',[]).append({'face':face,'error':repr(ex)})
           except Exception as ex:row['violations'].append(f'face[{face}]_dds_export:'+repr(ex))
        else:row['violations'].append(f'unsupported_array_size:{hdr["array_size"]}')
  if row['violations']:viol.extend(f'{h}:{x}' for x in row['violations'])
  rows.append(row)
 out={'schema':'d1_remote_activity_texture_export/v1','status':'D1_REMOTE_ACTIVITY_TEXTURE_EXPORT_COMPLETE' if not viol else 'D1_REMOTE_ACTIVITY_TEXTURE_EXPORT_WITH_VIOLATIONS',
      'source_material_closure':str(a.material_closure),'texture_count':len(tex),'dds_file_count':sum(f['kind']=='dds' for r in rows for f in r['files']),'png_file_count':sum(f['kind']=='png' for r in rows for f in r['files']),
      'rows':rows,'violations':viol,'policy':'Only exact texture header/backing identities already proven by the material closure are exported. No material role or PBR semantic is inferred here.'}
 (a.out_dir/'texture_export_manifest.json').write_text(json.dumps(out,indent=2)+'\n');print('STATUS',out['status'],'TEXTURES',out['texture_count'],'DDS',out['dds_file_count'],'PNG',out['png_file_count'],'VIOLATIONS',len(viol));return 0 if not viol else 2

if __name__=='__main__':raise SystemExit(main())
