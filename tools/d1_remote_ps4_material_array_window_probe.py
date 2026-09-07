#!/usr/bin/env python3
"""Probe exact D1 PS4 ROI Material dynamic-array headers around shader fields.

This is a structural reconnaissance tool. It resolves exact retail Material
payloads through the universal corpus, validates known texture/TFX/sampler array
headers using the established Charm DynamicArray relative-pointer rule, and
censuses every plausible 16-byte Vec4 array header in a caller-selected byte
window. Candidate arrays remain unnamed until schema/order/source evidence makes
one interpretation unique.
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_activity_placements import RemoteCorpus
from d1_split_tar_extract import SplitHttpTar

MAT_CLASS='80801AD7'


def norm(v:object)->str:return str(v).upper().removeprefix('0X').zfill(8)
def u32(b,o):return struct.unpack_from('<I',b,o)[0]
def i64(b,o):return struct.unpack_from('<q',b,o)[0]

def array_header(b:bytes,o:int,elem:int)->dict:
 count=u32(b,o);rel=i64(b,o+8);abs_off=(o+8)+rel+0x10;end=abs_off+count*elem
 return {'header_offset':o,'header_hex':b[o:o+16].hex().upper(),'count':count,'unknown_u32_at_plus4':u32(b,o+4),'relative_i64':rel,'absolute_offset':abs_off,'elem_size':elem,'end_offset':end,'in_bounds':0<=abs_off<=end<=len(b)}

def main()->int:
 ap=argparse.ArgumentParser();ap.add_argument('--material',action='append',required=True)
 ap.add_argument('--member-catalog',type=Path,action='append',required=True);ap.add_argument('--base-url',required=True);ap.add_argument('--part-count',type=int,default=10);ap.add_argument('--runtime',type=Path,required=True)
 ap.add_argument('--start',type=lambda x:int(x,0),default=0x2e0);ap.add_argument('--end',type=lambda x:int(x,0),default=0x340);ap.add_argument('-o','--output',type=Path,required=True);a=ap.parse_args()
 catalogs=load_catalogs(a.member_catalog);base=a.base_url.rstrip('/');arc=SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1,a.part_count+1)],retries=6,timeout=90);c=RemoteCorpus(arc,catalogs,a.runtime)
 rows=[];viol=[]
 for h in sorted({norm(x) for x in a.material}):
  r={'material':h,'violations':[]};m=c.entry_meta(h);r['meta']=m
  if m is None or norm(m.get('reference',''))!=MAT_CLASS:r['violations'].append('material_missing_or_class_mismatch');b=None
  else:
   try:b,src=c.payload(h);r['payload_source']=src
   except Exception as ex:b=None;r['violations'].append('payload:'+repr(ex))
  if b is not None:
   r['payload_bytes']=len(b)
   if not (0<=a.start<a.end<=len(b)):r['violations'].append(f'window_oob:{a.start:#x}:{a.end:#x}:{len(b):#x}')
   else:
    r['window']={'start':a.start,'end':a.end,'hex':b[a.start:a.end].hex().upper()}
    known={
      'ps_textures':array_header(b,0x2B8,8),
      'ps_tfx_bytecode':array_header(b,0x2D0,1),
      'ps_samplers':array_header(b,0x2F0,16),
    }
    r['known_arrays']=known
    for k,v in known.items():
     if not v['in_bounds']:r['violations'].append(f'{k}_known_array_oob')
    cand=[]
    for o in range(a.start,a.end-15,4):
     q=array_header(b,o,16)
     # A structural candidate needs a small nonzero count and an in-entry target.
     # Do not require alignment of target: retail relative arrays establish that.
     if 0<q['count']<=256 and q['in_bounds']:
      q['vec4_values']=[list(struct.unpack_from('<4f',b,q['absolute_offset']+i*16)) for i in range(q['count'])]
      cand.append(q)
    r['plausible_vec4_arrays']=cand
  if r['violations']:viol.extend(f'{h}:{x}' for x in r['violations'])
  rows.append(r)
 out={'schema':'d1_remote_ps4_material_array_window_probe/v1','status':'D1_REMOTE_PS4_MATERIAL_ARRAY_WINDOW_PROBE_COMPLETE' if not viol else 'D1_REMOTE_PS4_MATERIAL_ARRAY_WINDOW_PROBE_WITH_VIOLATIONS','window':[a.start,a.end],'materials':rows,'violations':viol,'policy':'Candidate Vec4 arrays are structural only. Known texture/TFX/sampler offsets validate the relative-pointer rule; no candidate is named as TFX constants or CBuffers without unique schema/source closure.'}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n');print('STATUS',out['status'],'MATERIALS',len(rows),'VIOLATIONS',len(viol));
 for r in rows:print('MATERIAL',r['material'],'KNOWN',[(k,v['count'],hex(v['absolute_offset'])) for k,v in r.get('known_arrays',{}).items()],'VEC4_CANDIDATES',[(hex(x['header_offset']),x['count'],hex(x['absolute_offset'])) for x in r.get('plausible_vec4_arrays',[])])
 return 0 if not viol else 2

if __name__=='__main__':raise SystemExit(main())
