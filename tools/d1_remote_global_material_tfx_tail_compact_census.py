#!/usr/bin/env python3
"""Compact archive-wide D1 ROI material TFX census for the 0x48..0x54 tail block.

This deliberately avoids a per-occurrence multi-gigabyte report.  It scans every
current PS4 material (Reference 80801AD7), disassembles both VS and PS TFX stages
with the source-/retail-closed ROI framing, and records only aggregate structural
evidence useful for discriminating the remaining D1 tail opcodes.

No semantic name is promoted from opcode number or later-game lineage.
"""
from __future__ import annotations
import argparse,collections,hashlib,json,struct,sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
if str(HERE) not in sys.path: sys.path.insert(0,str(HERE))

from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_investment_parent_probe import RemoteLogicalPackage
from d1_split_tar_extract import SplitHttpTar
from d1_material_decode import parse_material
from d1_tfx_program_inventory import disassemble as disassemble_tfx

MAT_CLASS='80801AD7'
TARGET_HEX={f'{x:02X}' for x in range(0x48,0x55)}
XUR_PROGRAM_SHA='de39e4a77d2ac5c967dfa1b488259976c0f62177f3633a2ef142e770a173fda3'

def norm(x): return str(x).upper().removeprefix('0X').zfill(8)

def stage_dis(p,stage):
    raw=bytes.fromhex(p[f'{stage}_tfx_bytecode']['bytes_hex'])
    b1=[x.get('value') for x in p[f'{stage}_tfx_bytecode_constants']['items']]
    b2=[x.get('value') for x in p[f'{stage}_cbuffers']['items']]
    q=disassemble_tfx(raw,b1,b2)
    return {
      'raw':raw,'sha256':hashlib.sha256(raw).hexdigest(),
      'ops':q.get('ops') or [],'complete':q.get('complete') is True,
      'shader':norm(p['vertex_shader'] if stage=='vs' else p['pixel_shader']),
      'cbuf_count':len(b2),'private_count':len(b1),
    }

def ophex(op):
    x=str(op.get('opcode') or '').upper()
    return x if len(x)==2 else None

def operand_key(op):
    b=op.get('operand_bytes') or []
    return '-'.join(f'{int(x):02X}' for x in b) if b else '<none>'

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--member-catalog',type=Path,action='append',required=True)
    ap.add_argument('--base-url',required=True)
    ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()

    cats=load_catalogs(a.member_catalog)
    arc=SplitHttpTar([f"{a.base_url.rstrip('/')}/packages.tar.{i:03d}" for i in range(1,a.part_count+1)],retries=6,timeout=120)

    violations=[];incomplete_programs=[];material_count=0;parsed_count=0;stage_count=0
    occ=collections.Counter(); stage_hist=collections.defaultdict(collections.Counter)
    operand_hist=collections.defaultdict(collections.Counter)
    prev_hist=collections.defaultdict(collections.Counter)
    next_hist=collections.defaultdict(collections.Counter)
    prev2_hist=collections.defaultdict(collections.Counter)
    next2_hist=collections.defaultdict(collections.Counter)
    position_hist=collections.defaultdict(collections.Counter)
    shader_hist=collections.defaultdict(collections.Counter)
    cbuf_relation=collections.defaultdict(collections.Counter)
    cooccurrence=collections.defaultdict(collections.Counter)
    program_sig=collections.defaultdict(collections.Counter)
    program_count_by_tail_set=collections.Counter()
    package_material_counts=collections.Counter()
    xur_program_rows=[]
    # D1 ROI stage-tail dwords immediately preceding each stage Vector4Container.
    # Keep these syntactic until corpus relations + independent schema evidence agree.
    gap_offsets={'vs':[0x90,0x94,0x98,0x9C,0xA0,0xA4,0xA8],
                 'ps':[0x310,0x314,0x318,0x31C,0x320,0x324,0x328]}
    gap_hist=collections.defaultdict(collections.Counter)
    op4a_gap_relation=collections.defaultdict(collections.Counter)
    op4a_operand_by_stage=collections.defaultdict(collections.Counter)

    for n,(pkg_text,members) in enumerate(sorted(cats.items()),1):
        pkg=int(pkg_text,16) if isinstance(pkg_text,str) else int(pkg_text)
        try:
            v=RemoteLogicalPackage(arc,members,a.runtime)
        except Exception as ex:
            violations.append(f'{pkg:04X}:open:{ex!r}');continue
        mats=[e for e in v.entries if norm(e.get('reference','FFFFFFFF'))==MAT_CLASS]
        package_material_counts[f'{pkg:04X}']=len(mats);material_count+=len(mats)
        for e in mats:
            h=norm(e['tag_hash'])
            try:
                mb=v.entry(int(e['index']));p=parse_material(mb,'PS4');parsed_count+=1
            except Exception as ex:
                violations.append(f'{h}:material_parse:{ex!r}');continue
            for stage in ('vs','ps'):
                try: sd=stage_dis(p,stage)
                except Exception as ex:
                    violations.append(f'{h}:{stage}:tfx:{ex!r}');continue
                stage_count+=1
                if not sd['complete']:
                    incomplete_programs.append({'material':h,'stage':stage,'shader':sd['shader'],'tfx_sha256':sd['sha256'],'tfx_hex':sd['raw'].hex()})
                    continue
                ops=sd['ops']
                has4a=any(ophex(o)=='4A' for o in ops)
                for off in gap_offsets[stage]:
                    val=struct.unpack_from('<I',mb,off)[0]
                    key=f'{stage}:0x{off:X}'
                    gap_hist[key][str(val)]+=1
                    rel=op4a_gap_relation[key]
                    rel['complete_rows']+=1
                    rel['has_4A']+=int(has4a)
                    rel['field_eq_5']+=int(val==5)
                    rel['both']+=int(has4a and val==5)
                    rel['false_positive_field5_without_4A']+=int((not has4a) and val==5)
                    rel['false_negative_4A_without_field5']+=int(has4a and val!=5)
                for o in ops:
                    if ophex(o)=='4A':
                        bb=o.get('operand_bytes') or []
                        if len(bb)==1:op4a_operand_by_stage[stage][str(int(bb[0]))]+=1
                tail_indices=[i for i,o in enumerate(ops) if ophex(o) in TARGET_HEX]
                tail_set=tuple(sorted({ophex(ops[i]) for i in tail_indices}))
                if tail_set: program_count_by_tail_set['+'.join(tail_set)]+=1
                for i in tail_indices:
                    o=ops[i];hx=ophex(o);name=str(o.get('name') or hx)
                    occ[hx]+=1;stage_hist[hx][stage]+=1
                    operand_hist[hx][operand_key(o)]+=1
                    shader_hist[hx][sd['shader']]+=1
                    prev=ophex(ops[i-1]) if i>0 else '<START>'
                    nxt=ophex(ops[i+1]) if i+1<len(ops) else '<END>'
                    prev2='>'.join(ophex(x) or str(x.get('name')) for x in ops[max(0,i-2):i]) or '<START>'
                    next2='>'.join(ophex(x) or str(x.get('name')) for x in ops[i+1:i+3]) or '<END>'
                    prev_hist[hx][prev]+=1;next_hist[hx][nxt]+=1
                    prev2_hist[hx][prev2]+=1;next2_hist[hx][next2]+=1
                    if i==0: position_hist[hx]['start']+=1
                    if i==len(ops)-1: position_hist[hx]['end']+=1
                    if 0<i<len(ops)-1: position_hist[hx]['middle']+=1
                    b=o.get('operand_bytes') or []
                    if len(b)==1:
                        q=int(b[0])
                        cbuf_relation[hx]['operand_lt_cbuf']+=int(q<sd['cbuf_count'])
                        cbuf_relation[hx]['operand_ge_cbuf']+=int(q>=sd['cbuf_count'])
                        cbuf_relation[hx]['operand_lt_private']+=int(q<sd['private_count'])
                        cbuf_relation[hx]['operand_ge_private']+=int(q>=sd['private_count'])
                    for other in tail_set:
                        if other!=hx: cooccurrence[hx][other]+=1
                    sig=f'{prev}|{hx}:{operand_key(o)}|{nxt}'
                    program_sig[hx][sig]+=1
                if sd['sha256']==XUR_PROGRAM_SHA:
                    xur_program_rows.append({
                      'material':h,'package_id':f'{pkg:04X}','stage':stage,'shader':sd['shader'],
                      'bytecode_hex':sd['raw'].hex(),'op_names':[x.get('name') for x in ops],
                      'ops':[{'opcode':ophex(x),'name':x.get('name'),'operand_bytes':x.get('operand_bytes'),
                              'constant_index':x.get('constant_index'),'d1_unk42_u8':x.get('d1_unk42_u8')} for x in ops],
                    })
        if n%25==0 or n==len(cats):
            print(f'TAIL_CENSUS_PACKAGES {n}/{len(cats)} materials={material_count} parsed={parsed_count} stages={stage_count} tail_occ={sum(occ.values())}',flush=True)

    def topmap(src,k,limit=40):
        return dict(src[k].most_common(limit))
    rows={}
    for hx in sorted(TARGET_HEX):
        rows[hx]={
          'name_from_pinned_D1_table':None,
          'occurrence_count':occ[hx],
          'stage_histogram':dict(stage_hist[hx]),
          'operand_histogram_top':topmap(operand_hist,hx,80),
          'position_histogram':dict(position_hist[hx]),
          'previous_opcode_top':topmap(prev_hist,hx),
          'next_opcode_top':topmap(next_hist,hx),
          'previous_two_opcode_top':topmap(prev2_hist,hx),
          'next_two_opcode_top':topmap(next2_hist,hx),
          'shader_histogram_top':topmap(shader_hist,hx,30),
          'one_byte_operand_range_relation':dict(cbuf_relation[hx]),
          'tail_opcode_cooccurrence':dict(cooccurrence[hx]),
          'local_signature_top':topmap(program_sig,hx,60),
        }
    # Preserve pinned parser names exactly as observed in disassembly by finding a representative.
    # Names are syntactic labels only.
    name_map={
      '48':'Unk48','49':'Unk49','4A':'Unk4a','4B':'Unk4b','4C':'Unk4c',
      '4D':'PushObjectChannelVector','4E':'Unk4e','4F':'Unk4f','50':'Unk50',
      '51':'Unk51','52':'Unk52','53':'Unk53','54':'Unk54'
    }
    for hx,nm in name_map.items(): rows[hx]['name_from_pinned_D1_table']=nm

    out={
      'schema_version':1,
      'status':'D1_ROI_GLOBAL_MATERIAL_TFX_TAIL_COMPACT_CENSUS_EXACT' if not violations else 'D1_ROI_GLOBAL_MATERIAL_TFX_TAIL_COMPACT_CENSUS_VIOLATIONS',
      'material_class':MAT_CLASS,
      'package_family_count':len(cats),'material_entry_count':material_count,'parsed_material_count':parsed_count,
      'stage_program_count':stage_count,'tail_opcode_range':'0x48..0x54',
      'tail_opcode_occurrence_count':sum(occ.values()),
      'rows':rows,
      'program_tail_set_histogram':dict(program_count_by_tail_set.most_common()),
      'package_material_counts':dict(package_material_counts),
      'incomplete_program_count':len(incomplete_programs),
      'incomplete_programs':incomplete_programs,
      'gap_field_histograms':{k:dict(v) for k,v in sorted(gap_hist.items())},
      'op4a_gap_relations':{k:dict(v) for k,v in sorted(op4a_gap_relation.items())},
      'op4a_operand_histogram_by_stage':{k:dict(v) for k,v in sorted(op4a_operand_by_stage.items())},
      'xur_80876865_exact_program_rows':xur_program_rows,
      'proof_boundary':{
        'semantic_names_promoted_from_census':False,
        'D1_0x4A_runtime_source_identity_proven':False,
        'D1_0x4B_runtime_source_identity_proven':False,
        'incomplete_programs_are_reported_not_silently_dropped':True,
        'gap_field_semantic_names_proven':False,
        'later_strategy_opcode_numbers_used_as_authority':False,
      },
      'violations':violations,
      'policy':'Aggregate retail corpus structure only. Pinned D1 labels are preserved, but unknown tail opcodes and unnamed ROI gap fields remain syntactic until runtime/source ownership is independently closed. Incomplete bytecode programs are explicitly reported and excluded only from opcode/gap relation tests that require complete framing.'
    }
    if parsed_count!=material_count: violations.append(f'parsed_material_count:{parsed_count}!={material_count}')
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({
      'status':out['status'],'material_entry_count':material_count,'parsed_material_count':parsed_count,
      'tail_opcode_occurrence_count':out['tail_opcode_occurrence_count'],
      'opcode_counts':{k:v['occurrence_count'] for k,v in rows.items()},
      'stage_histograms':{k:v['stage_histogram'] for k,v in rows.items()},
      'xur_exact_program_row_count':len(xur_program_rows),
      'incomplete_program_count':len(incomplete_programs),
      'op4a_gap_key_relations':{k:dict(v) for k,v in op4a_gap_relation.items() if k in ('vs:0xA0','ps:0x320')},
      'violations':violations[:20],
    },indent=2))
    return 0 if not violations else 2

if __name__=='__main__': raise SystemExit(main())
