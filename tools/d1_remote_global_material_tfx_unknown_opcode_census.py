#!/usr/bin/env python3
"""Archive-wide exact D1 ROI material TFX census for unknown opcodes 0x4A/0x4B.

This probe is deliberately broader than Xur. It enumerates every current PS4
FileEntry whose exact Reference is 80801AD7, recovers the material payload,
parses both TFX stages with the source-closed ROI material layout, and records
every Unk4a/Unk4b occurrence together with exact operand, shader, TFX program,
serialized CBuffer bounds/value, and local opcode context.

The goal is discrimination by retail corpus behavior. It does not rename either
opcode from analogy. A semantic promotion must survive this archive-wide census.
"""
from __future__ import annotations
import argparse,collections,hashlib,json,sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
if str(HERE) not in sys.path: sys.path.insert(0,str(HERE))

from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_investment_parent_probe import RemoteLogicalPackage
from d1_split_tar_extract import SplitHttpTar
from d1_material_decode import parse_material
from d1_tfx_program_inventory import disassemble as disassemble_tfx

MAT_CLASS='80801AD7'
TARGET_NAMES={'Unk4a','Unk4b'}

def norm(x:object)->str:return str(x).upper().removeprefix('0X').zfill(8)

def stage_dis(p:dict,stage:str)->dict:
    raw=bytes.fromhex(p[f'{stage}_tfx_bytecode']['bytes_hex'])
    b1=[x.get('value') for x in p[f'{stage}_tfx_bytecode_constants']['items']]
    b2=[x.get('value') for x in p[f'{stage}_cbuffers']['items']]
    return {
        'raw':raw,'sha256':hashlib.sha256(raw).hexdigest(),
        'ops':disassemble_tfx(raw,b1,b2).get('ops') or [],
        'private_constants':b1,'cbuffers':b2,
        'shader':norm(p['vertex_shader'] if stage=='vs' else p['pixel_shader'])
    }

def context(ops:list[dict],i:int,radius:int=5)->list[dict]:
    out=[]
    for j in range(max(0,i-radius),min(len(ops),i+radius+1)):
        q=ops[j]
        out.append({
            'relative':j-i,'index':j,'offset':q.get('offset'),'name':q.get('name'),
            'raw':q.get('raw'),'operand_bytes':q.get('operand_bytes'),
            'extern_name':q.get('extern_name'),'extern_element':q.get('extern_element'),
            'constant_index':q.get('constant_index'),'constant_start':q.get('constant_start'),
            'd1_unk42_u8':q.get('d1_unk42_u8'),
        })
    return out

def operand_u8(op:dict)->int|None:
    b=op.get('operand_bytes') or []
    return int(b[0]) if b else None

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--member-catalog',type=Path,action='append',required=True)
    ap.add_argument('--base-url',required=True)
    ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()

    catalogs=load_catalogs(a.member_catalog)
    arc=SplitHttpTar([f"{a.base_url.rstrip('/')}/packages.tar.{i:03d}" for i in range(1,a.part_count+1)],retries=6,timeout=120)

    violations=[]
    material_count=0
    parsed_count=0
    occurrence_rows=[]
    program_rows={}
    package_material_counts=collections.Counter()
    ref_count=0

    for n,(pkg_text,members) in enumerate(sorted(catalogs.items()),1):
        pkg=int(pkg_text,16) if isinstance(pkg_text,str) else int(pkg_text)
        try:
            v=RemoteLogicalPackage(arc,members,a.runtime)
        except Exception as ex:
            violations.append(f'{pkg:04X}:open:{ex!r}')
            continue
        mats=[e for e in v.entries if norm(e.get('reference','FFFFFFFF'))==MAT_CLASS]
        package_material_counts[f'{pkg:04X}']=len(mats)
        material_count+=len(mats)
        for e in mats:
            h=norm(e['tag_hash']);ref_count+=1
            try:
                b=v.entry(int(e['index']))
                p=parse_material(b,'PS4')
                parsed_count+=1
            except Exception as ex:
                violations.append(f'{h}:material_parse:{ex!r}')
                continue
            for stage in ('vs','ps'):
                try:
                    sd=stage_dis(p,stage)
                except Exception as ex:
                    violations.append(f'{h}:{stage}:tfx:{ex!r}')
                    continue
                pkey=f"{stage}:{sd['sha256']}"
                pr=program_rows.setdefault(pkey,{
                    'stage':stage,'tfx_sha256':sd['sha256'],'byte_count':len(sd['raw']),
                    'bytecode_hex':sd['raw'].hex(),'shaders':set(),'materials':set(),
                    'occurrences':[],'opcode_names':[x.get('name') for x in sd['ops']],
                })
                pr['shaders'].add(sd['shader']);pr['materials'].add(h)
                prior_42=[]
                for i,op in enumerate(sd['ops']):
                    name=op.get('name')
                    if name=='Unk42':
                        q=op.get('d1_unk42_u8')
                        if q is not None: prior_42.append(int(q))
                    if name not in TARGET_NAMES: continue
                    operand=operand_u8(op)
                    cbuf_count=len(sd['cbuffers'])
                    row={
                        'material':h,'package_id':f'{pkg:04X}','entry_index':int(e['index']),
                        'stage':stage,'shader':sd['shader'],'tfx_sha256':sd['sha256'],
                        'opcode':name,'opcode_hex':'4A' if name=='Unk4a' else '4B',
                        'operand_u8':operand,
                        'cbuffer_vec4_count':cbuf_count,
                        'operand_in_serialized_cbuffer_range':operand is not None and operand<cbuf_count,
                        'serialized_cbuffer_vec4_at_operand':sd['cbuffers'][operand] if operand is not None and operand<cbuf_count else None,
                        'private_constant_vec4_count':len(sd['private_constants']),
                        'prior_0x42_targets':list(prior_42),
                        'last_prior_0x42_target':prior_42[-1] if prior_42 else None,
                        'operand_equals_last_prior_0x42_target':bool(prior_42 and operand==prior_42[-1]),
                        'operand_was_any_prior_0x42_target':operand in prior_42 if operand is not None else False,
                        'context':context(sd['ops'],i),
                    }
                    occurrence_rows.append(row)
                    pr['occurrences'].append({
                        'opcode':name,'operand_u8':operand,'op_index':i,
                        'prior_0x42_targets':list(prior_42),
                        'context':context(sd['ops'],i)
                    })
        if n%25==0 or n==len(catalogs):
            print(f'MATERIAL_TFX_PACKAGES {n}/{len(catalogs)} materials={material_count} parsed={parsed_count} unknown_ops={len(occurrence_rows)}',flush=True)

    # JSON-normalize program sets.
    programs=[]
    for k,r in sorted(program_rows.items()):
        if not r['occurrences']: continue
        r=dict(r);r['shaders']=sorted(r['shaders']);r['materials']=sorted(r['materials'])
        r['material_count']=len(r['materials']);r['shader_count']=len(r['shaders'])
        programs.append(r)

    by_opcode=collections.Counter(r['opcode'] for r in occurrence_rows)
    by_stage_opcode=collections.Counter(f"{r['stage']}:{r['opcode']}" for r in occurrence_rows)
    operands=collections.defaultdict(collections.Counter)
    shaders=collections.defaultdict(collections.Counter)
    prior_same=collections.Counter()
    in_cbuffer=collections.Counter()
    contexts=collections.Counter()
    for r in occurrence_rows:
        operands[r['opcode']][str(r['operand_u8'])]+=1
        shaders[r['opcode']][r['shader']]+=1
        prior_same[r['opcode']]+=int(r['operand_equals_last_prior_0x42_target'])
        in_cbuffer[r['opcode']]+=int(r['operand_in_serialized_cbuffer_range'])
        names=tuple(x['name'] for x in r['context'])
        contexts[f"{r['opcode']}|{'/'.join(names)}"]+=1

    out={
      'schema_version':1,
      'status':'D1_ROI_GLOBAL_MATERIAL_TFX_UNKNOWN_OPCODE_CENSUS_EXACT' if not violations else 'D1_ROI_GLOBAL_MATERIAL_TFX_UNKNOWN_OPCODE_CENSUS_VIOLATIONS',
      'material_class':MAT_CLASS,
      'package_family_count':len(catalogs),
      'material_entry_count':material_count,
      'parsed_material_count':parsed_count,
      'unknown_opcode_occurrence_count':len(occurrence_rows),
      'unknown_opcode_program_count':len(programs),
      'opcode_histogram':dict(by_opcode),
      'stage_opcode_histogram':dict(by_stage_opcode),
      'operand_histograms':{k:dict(v) for k,v in sorted(operands.items())},
      'shader_histograms':{k:dict(v) for k,v in sorted(shaders.items())},
      'operand_equals_last_prior_0x42_counts':dict(prior_same),
      'operand_in_serialized_cbuffer_range_counts':dict(in_cbuffer),
      'context_signature_histogram':dict(contexts),
      'package_material_counts':dict(package_material_counts),
      'programs':programs,
      'occurrences':occurrence_rows,
      'violations':violations,
      'policy':'Exact current D1 PS4 material Reference census and source-closed ROI material/TFX parsing. 0x4A and 0x4B remain syntactically named Unk4a/Unk4b; corpus patterns are evidence for later promotion, not semantic names by themselves.'
    }
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in [
      'status','package_family_count','material_entry_count','parsed_material_count',
      'unknown_opcode_occurrence_count','unknown_opcode_program_count','opcode_histogram',
      'stage_opcode_histogram','operand_histograms','operand_equals_last_prior_0x42_counts',
      'operand_in_serialized_cbuffer_range_counts','violations']},indent=2))
    return 0 if not violations else 2

if __name__=='__main__':raise SystemExit(main())
