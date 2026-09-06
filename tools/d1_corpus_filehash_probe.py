#!/usr/bin/env python3
"""Probe exact D1 FileHashes through a supplied cross-package Corpus.

Unlike d1_remote_filehash_probe.py, package recovery is intentionally outside this
tool. Callers supply already checksum-validated physical snapshots. For each target
this records the current selected entry/payload, EntityResource parse when relevant,
and every aligned dword that resolves to a real current Corpus entry. This is useful
for tracing serialized owner/control/clip edges across package families without
assuming package adjacency.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import d1_tower_map_schema_validate_v5 as v5
from d1_entity_resource_probe import ENTITY_RESOURCE_CLASS,parse_resource

NULLS={'00000000','FFFFFFFF'}

def norm(x):
 x=str(x).upper().removeprefix('0X').zfill(8);int(x,16);return x

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--snapshot',type=Path,action='append',required=True)
 ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('--tag-hash',action='append',required=True)
 ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 c=v5.v3.base.Corpus([p.resolve() for p in a.snapshot],a.runtime.resolve())
 rows=[];viol=[]
 for raw in a.tag_hash:
  h=norm(raw);m=c.entry_meta(h);b,src=c.payload(h)
  row={'tag_hash':h,'meta':m,'payload_source':src,'violations':[],'aligned_resolved_tag_matches':[]}
  if m is None:row['violations'].append('entry_missing')
  elif b is None:row['violations'].append('payload_unavailable')
  else:
   row['payload_size']=len(b);row['payload_sha256']=hashlib.sha256(b).hexdigest();row['prefix128']=b[:128].hex();row['suffix64']=b[-64:].hex()
   if norm(m.get('reference',''))==ENTITY_RESOURCE_CLASS:
    try:row['entity_resource']=parse_resource(b,'PS4')
    except Exception as ex:row['violations'].append('entity_resource_parse:'+repr(ex))
   end=len(b)-(len(b)%4);hits=[]
   for off in range(0,end,4):
    v=struct.unpack_from('<I',b,off)[0];vh=f'{v:08X}'
    if vh in NULLS:continue
    vm=c.entry_meta(vh)
    if vm is None:continue
    hits.append({'offset':off,'tag_hash':vh,'reference':norm(vm.get('reference','FFFFFFFF')),
                 'type':vm.get('type'),'subtype':vm.get('subtype'),'size':vm.get('size'),
                 'snapshot':vm.get('snapshot'),'package_id':vm.get('package_id')})
   row['aligned_resolved_tag_matches']=hits
  viol.extend(f'{h}:{x}' for x in row['violations']);rows.append(row)
 out={'schema_version':1,'status':'D1_CORPUS_FILEHASH_PROBE_COMPLETE' if not viol else 'D1_CORPUS_FILEHASH_PROBE_PARTIAL',
      'requested':[norm(x) for x in a.tag_hash],'snapshot_count':len(a.snapshot),'entries':rows,'violations':viol,
      'policy':'Only exact current Corpus entries and aligned serialized dword FileHashes are reported. Cross-package resolution proves literal serialization but does not by itself assign gameplay semantics.'}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
 for r in rows:
  er=r.get('entity_resource') or {}
  print(json.dumps({'tag_hash':r['tag_hash'],'reference':None if r['meta'] is None else r['meta'].get('reference'),
    'payload_size':r.get('payload_size'),'unk10':(er.get('unk10') or {}).get('class_hash'),'unk18':(er.get('unk18') or {}).get('class_hash'),
    'resolved_hits':r.get('aligned_resolved_tag_matches',[]),'violations':r['violations']},indent=2))
 return 0 if not viol else 2
if __name__=='__main__':raise SystemExit(main())
