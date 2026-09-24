#!/usr/bin/env python3
"""Focused retail D1 census for the remaining Xur-visible TFX producer 0x4A[4].

Scans all PS4 material resources and retains only complete stage programs that
contain opcode 0x4A with one-byte operand 4.  It aggregates:
- VS/PS split, shader families, material CBuffer/private-vector cardinalities;
- exact local opcode contexts and target stores;
- full-program SHA frequency;
- whether the Xur jaw program is structurally unique;
- the unnamed D1 material stage-tail dwords around the TFX/vector containers.

This is structural evidence only.  It does not assign a semantic runtime source
name to 0x4A.
"""
from __future__ import annotations
import argparse,collections,hashlib,json,struct,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_investment_parent_probe import RemoteLogicalPackage
from d1_split_tar_extract import SplitHttpTar
from d1_material_decode import parse_material
from d1_tfx_program_inventory import disassemble as disassemble_tfx

MAT_CLASS='80801AD7';TARGET_OPERAND=4
XUR_MATERIAL='80876865';XUR_SHADER='8087688E'
XUR_SHA='de39e4a77d2ac5c967dfa1b488259976c0f62177f3633a2ef142e770a173fda3'
GAPS={'vs':[0x90,0x94,0x98,0x9C,0xA0,0xA4,0xA8],
      'ps':[0x310,0x314,0x318,0x31C,0x320,0x324,0x328]}

def norm(x):return str(x).upper().removeprefix('0X').zfill(8)
def ophex(o):return str(o.get('opcode') or '').upper()
def stage_dis(p,stage):
 raw=bytes.fromhex(p[f'{stage}_tfx_bytecode']['bytes_hex'])
 b1=[x.get('value') for x in p[f'{stage}_tfx_bytecode_constants']['items']]
 b2=[x.get('value') for x in p[f'{stage}_cbuffers']['items']]
 q=disassemble_tfx(raw,b1,b2)
 return raw,q,b1,b2,norm(p['vertex_shader'] if stage=='vs' else p['pixel_shader'])

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--member-catalog',type=Path,action='append',required=True)
 ap.add_argument('--base-url',required=True);ap.add_argument('--part-count',type=int,default=10)
 ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('-o','--output',type=Path,required=True)
 a=ap.parse_args();cats=load_catalogs(a.member_catalog)
 arc=SplitHttpTar([f"{a.base_url.rstrip('/')}/packages.tar.{i:03d}" for i in range(1,a.part_count+1)],retries=6,timeout=120)
 viol=[];materials=0;parsed=0;complete_stages=0;hit_occ=0;hit_programs=0
 stage_hist=collections.Counter();shader_hist=collections.Counter();sha_hist=collections.Counter()
 cbuf_hist=collections.Counter();private_hist=collections.Counter();context_hist=collections.Counter()
 next_store_hist=collections.Counter();gap_hist={f'{s}:0x{o:X}':collections.Counter() for s,oo in GAPS.items() for o in oo}
 material_hits=collections.Counter();xur_rows=[];examples=[]
 for n,(pkg_text,members) in enumerate(sorted(cats.items()),1):
  pkg=int(pkg_text,16) if isinstance(pkg_text,str) else int(pkg_text)
  try:v=RemoteLogicalPackage(arc,members,a.runtime)
  except Exception as ex:viol.append(f'{pkg:04X}:open:{ex!r}');continue
  mats=[e for e in v.entries if norm(e.get('reference','FFFFFFFF'))==MAT_CLASS];materials+=len(mats)
  for e in mats:
   h=norm(e['tag_hash'])
   try:mb=v.entry(int(e['index']));p=parse_material(mb,'PS4');parsed+=1
   except Exception as ex:viol.append(f'{h}:parse:{ex!r}');continue
   for stage in ('vs','ps'):
    try:raw,q,b1,b2,shader=stage_dis(p,stage)
    except Exception as ex:viol.append(f'{h}:{stage}:{ex!r}');continue
    if q.get('complete') is not True:continue
    complete_stages+=1;ops=q.get('ops') or []
    idx=[]
    for i,o in enumerate(ops):
     if ophex(o)=='4A' and list(o.get('operand_bytes') or [])==[TARGET_OPERAND]:idx.append(i)
    if not idx:continue
    hit_programs+=1;hit_occ+=len(idx);stage_hist[stage]+=len(idx);shader_hist[shader]+=len(idx)
    sha=hashlib.sha256(raw).hexdigest();sha_hist[sha]+=1;cbuf_hist[str(len(b2))]+=len(idx);private_hist[str(len(b1))]+=len(idx);material_hits[h]+=len(idx)
    for off in GAPS[stage]:gap_hist[f'{stage}:0x{off:X}'][str(struct.unpack_from('<I',mb,off)[0])]+=len(idx)
    for i in idx:
     prev=ophex(ops[i-1]) if i else '<START>';nxt=ophex(ops[i+1]) if i+1<len(ops) else '<END>'
     prev2=ophex(ops[i-2]) if i>1 else '<START>';nxt2=ophex(ops[i+2]) if i+2<len(ops) else '<END>'
     context_hist[f'{prev2}>{prev}|4A:04|{nxt}>{nxt2}']+=1
     if nxt=='42':
      no=ops[i+1];next_store_hist[str(no.get('d1_unk42_u8'))]+=1
     row={'material':h,'package':f'{pkg:04X}','stage':stage,'shader':shader,'tfx_sha256':sha,
          'bytecode_hex':raw.hex(),'cbuf_count':len(b2),'private_count':len(b1),'op_index':i,
          'context':f'{prev2}>{prev}|4A:04|{nxt}>{nxt2}',
          'next_store':ops[i+1].get('d1_unk42_u8') if nxt=='42' else None,
          'gap_dwords':{f'0x{off:X}':struct.unpack_from('<I',mb,off)[0] for off in GAPS[stage]}}
      if h==XUR_MATERIAL or sha==XUR_SHA:xur_rows.append(row)
      if len(examples)<120:examples.append(row)
  if n%25==0 or n==len(cats):print(f'OP4A4_PACKAGES {n}/{len(cats)} materials={materials} parsed={parsed} hit_occ={hit_occ} hit_programs={hit_programs}',flush=True)
 if parsed!=materials:viol.append(f'parsed:{parsed}!={materials}')
 out={'schema_version':1,'status':'D1_GLOBAL_TFX_0X4A4_FOCUSED_CENSUS_EXACT' if not viol else 'D1_GLOBAL_TFX_0X4A4_FOCUSED_CENSUS_VIOLATIONS',
      'material_entry_count':materials,'parsed_material_count':parsed,'complete_stage_count':complete_stages,
      'operand':4,'occurrence_count':hit_occ,'program_count':hit_programs,'unique_material_count':len(material_hits),
      'stage_histogram':dict(stage_hist),'shader_histogram_top':dict(shader_hist.most_common(100)),
      'program_sha_histogram_top':dict(sha_hist.most_common(100)),'cbuf_count_histogram':dict(cbuf_hist),
      'private_count_histogram':dict(private_hist),'local_context_histogram':dict(context_hist.most_common()),
      'immediate_0x42_store_histogram':dict(next_store_hist),
      'gap_dword_histograms':{k:dict(v) for k,v in gap_hist.items()},
      'xur_rows':xur_rows,'example_rows':examples,
      'xur_program_uniqueness':{
        'xur_tfx_sha256':XUR_SHA,'program_sha_occurrence_count':sha_hist[XUR_SHA],
        'xur_material_hit_count':material_hits[XUR_MATERIAL],
        'xur_shader_hit_count':shader_hist[XUR_SHADER],
      },
      'proof_boundary':{'D1_0x4A_runtime_source_identity_proven':False,'semantic_name_promoted':False},
      'violations':viol,
      'policy':'Archive-wide structural census of exact 0x4A operand 4 only. No runtime producer semantic is inferred from frequency, shader family, gap dwords, or local opcode context.'}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({k:out[k] for k in ['status','occurrence_count','program_count','unique_material_count','stage_histogram','cbuf_count_histogram','private_count_histogram','immediate_0x42_store_histogram','xur_program_uniqueness','violations']},indent=2))
 return 0 if not viol else 2
if __name__=='__main__':raise SystemExit(main())
