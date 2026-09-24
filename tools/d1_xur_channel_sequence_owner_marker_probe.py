#!/usr/bin/env python3
"""Trace D1 Xur SEntity owners for object-channel/sequencer component evidence.

The remaining visible Xur material-TFX frontier is PS bytecode 4A 04 34 00 03
42 01 in inline jaw material 80876865.  This probe does not assign semantics to
0x4A.  It searches the exact source-owned Xur SEntities and their literal
backlink owners for D1 ROI component/resource class markers that are known from
independent schema work to participate in object-channel / sequence systems.

Evidence is deliberately split:
- literal aligned class/hash occurrences in source payloads;
- source/backlink ownership already proved elsewhere;
- no claim that a hit is consumed by material 80876865 unless a typed path is
  independently decoded.
"""
from __future__ import annotations
import argparse,collections,hashlib,json,struct,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_activity_placements import RemoteCorpus
from d1_split_tar_extract import SplitHttpTar

XURS=['80C7ACC8','80C885AA']
# D1 ROI / shared Tiger component/schema markers from independent tooling.
TARGETS={
 '808095B1':'object_channel_component_resource_type_candidate',
 '80809597':'object_channel_component_data_class_candidate',
 '808095A9':'object_channel_record_class_candidate',
 '80809479':'sequence_component_resource_type_candidate',
 '80808179':'sequence_data_class_candidate',
 '808091D1':'sequence_global_channel_node_class_candidate',
}
# Exact scripted placement owners already source-closed in the Xur owner probe.
OWNERS=['80C7A251','80C7A441','80C7A58F','80C7A719','80C7AC71','80C7AC81','80C7ACB9','80C7AD18','80C88185','80C8831B','80C88591','80C88888']

def norm(x):return str(x).upper().removeprefix('0X').zfill(8)
def aligned_hits(b,h):
 v=int(h,16);return [o for o in range(0,len(b)-(len(b)%4),4) if struct.unpack_from('<I',b,o)[0]==v]
def windows(b,offs,r=32):
 return [{'offset':o,'offset_hex':f'0x{o:X}','context_hex':b[max(0,o-r):min(len(b),o+4+r)].hex()} for o in offs]

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--member-catalog',type=Path,action='append',required=True)
 ap.add_argument('--base-url',required=True);ap.add_argument('--part-count',type=int,default=10)
 ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('-o','--output',type=Path,required=True)
 a=ap.parse_args();cats=load_catalogs(a.member_catalog)
 arc=SplitHttpTar([f"{a.base_url.rstrip('/')}/packages.tar.{i:03d}" for i in range(1,a.part_count+1)],retries=6,timeout=90)
 c=RemoteCorpus(arc,cats,a.runtime);rows=[];viol=[];hist=collections.Counter()
 for h in XURS+OWNERS:
  try:
   m=c.entry_meta(h);b,src=c.payload(h)
   if m is None or b is None:raise ValueError('payload unavailable')
   hits={}
   for t,label in TARGETS.items():
    oo=aligned_hits(b,t)
    if oo:
     hits[t]={'label':label,'count':len(oo),'hits':windows(b,oo)}
     hist[t]+=len(oo)
   rows.append({'tag_hash':h,'scope':'xur_sentity' if h in XURS else 'proved_xur_scripted_owner',
                'reference':norm(m.get('reference','0')),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),
                'source':src,'target_hits':hits})
  except Exception as ex:
   viol.append(f'{h}:{ex!r}');rows.append({'tag_hash':h,'error':repr(ex)})
 out={
  'schema_version':1,
  'status':'D1_XUR_CHANNEL_SEQUENCE_OWNER_MARKER_CENSUS_EXACT' if not viol else 'D1_XUR_CHANNEL_SEQUENCE_OWNER_MARKER_CENSUS_VIOLATIONS',
  'xur_entities':XURS,'proved_scripted_owners':OWNERS,'targets':TARGETS,
  'occurrence_histogram':dict(hist),'hit_payload_count':sum(bool(r.get('target_hits')) for r in rows),
  'rows':rows,'violations':viol,
  'proof_boundary':{
   'literal_aligned_occurrences_exact':True,
   'object_channel_or_sequence_component_typed_path_to_Xur_material_proven':False,
   'D1_0x4A_runtime_source_identity_proven':False,
  },
  'policy':'Literal source-owner marker census only. A hit is a search frontier, not consumer semantics; a miss excludes only direct aligned serialization in these payloads, not indirect component references.'
 }
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'status':out['status'],'occurrence_histogram':out['occurrence_histogram'],'hit_payload_count':out['hit_payload_count'],
                   'hit_rows':[{'tag_hash':r['tag_hash'],'scope':r.get('scope'),'reference':r.get('reference'),'targets':{k:v['count'] for k,v in r.get('target_hits',{}).items()}} for r in rows if r.get('target_hits')],
                   'violations':viol},indent=2))
 return 0 if not viol else 2
if __name__=='__main__':raise SystemExit(main())
