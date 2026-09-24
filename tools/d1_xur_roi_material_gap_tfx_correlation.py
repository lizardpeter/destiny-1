#!/usr/bin/env python3
"""Correlate the unnamed D1 ROI material stage gaps with exact TFX slot usage.

For the 54 active Xur materials in the pinned carrier, re-read each retail material
payload and compare:
- serialized stage CBuffer Vec4 count;
- maximum 0x42 write target + 1;
- maximum 0x4A read operand + 1;
- the seven unnamed dwords between the CBuffer DynamicArray header and the stage
  Vector4Container field.

No field meaning is assumed. The report ranks exact equality relations so an
output-capacity field can be promoted only if the corpus forces it.
"""
from __future__ import annotations
import argparse,collections,hashlib,json,struct,sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
if str(HERE) not in sys.path:sys.path.insert(0,str(HERE))
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_activity_placements import RemoteCorpus
from d1_split_tar_extract import SplitHttpTar
from d1_material_decode import parse_material
from d1_tfx_program_inventory import disassemble as disassemble_tfx

VS_GAP=list(range(0x90,0xAC,4))
PS_GAP=list(range(0x310,0x32C,4))
MAT_CLASS='80801AD7'

def norm(x):return str(x).upper().removeprefix('0X').zfill(8)
def u32(b,o):return struct.unpack_from('<I',b,o)[0]

def read_glb_json(path:Path)->dict:
    raw=path.read_bytes()
    if raw[:4]!=b'glTF' or struct.unpack_from('<I',raw,4)[0]!=2:raise ValueError('not GLB2')
    n,t=struct.unpack_from('<II',raw,12)
    if t!=0x4E4F534A:raise ValueError('first chunk not JSON')
    return json.loads(raw[20:20+n].decode('utf-8').rstrip(' \t\r\n\0'))

def active_materials(path:Path)->list[str]:
    d=read_glb_json(path);out=[]
    for m in d.get('materials') or []:
        h=norm((m.get('extras') or {}).get('d1_material_taghash','FFFFFFFF'))
        if h not in ('FFFFFFFF','00000000'):out.append(h)
    return sorted(set(out))

def stage_tfx(p:dict,stage:str):
    raw=bytes.fromhex(p[f'{stage}_tfx_bytecode']['bytes_hex'])
    b1=[x.get('value') for x in p[f'{stage}_tfx_bytecode_constants']['items']]
    b2=[x.get('value') for x in p[f'{stage}_cbuffers']['items']]
    q=disassemble_tfx(raw,b1,b2)
    if q.get('complete') is not True:raise ValueError(f'{stage}: incomplete TFX')
    w=[];r=[]
    for op in q.get('ops') or []:
        if op.get('name')=='Unk42':w.append(int(op['d1_unk42_u8']))
        elif op.get('name')=='Unk4a':r.append(int((op.get('operand_bytes') or [])[0]))
    cbn=len(b2)
    maxw=max(w,default=-1);maxr=max(r,default=-1)
    required=max(cbn,maxw+1,maxr+1)
    return {
      'cbuffer_vec4_count':cbn,
      'op42_targets':w,'op4a_operands':r,
      'max_op42_target':None if maxw<0 else maxw,
      'max_op4a_operand':None if maxr<0 else maxr,
      'required_slot_count_from_serialized_and_tfx':required,
      'tfx_sha256':hashlib.sha256(raw).hexdigest(),
      'tfx_hex':raw.hex(),
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--carrier',type=Path,required=True)
    ap.add_argument('--member-catalog',type=Path,action='append',required=True)
    ap.add_argument('--base-url',required=True);ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args();viol=[]
    mats=active_materials(a.carrier)
    if len(mats)!=54:viol.append(f'active_material_count:{len(mats)}!=54')
    cats=load_catalogs(a.member_catalog)
    arc=SplitHttpTar([f"{a.base_url.rstrip('/')}/packages.tar.{i:03d}" for i in range(1,a.part_count+1)],retries=6,timeout=90)
    c=RemoteCorpus(arc,cats,a.runtime)

    rows=[]
    equality=collections.defaultdict(lambda:collections.Counter())
    hist=collections.defaultdict(collections.Counter)
    stage_rows=collections.Counter()
    for mh in mats:
        try:
            meta=c.entry_meta(mh);b,src=c.payload(mh)
            if meta is None or b is None:raise ValueError('payload unavailable')
            if norm(meta.get('reference'))!=MAT_CLASS:raise ValueError(f'class {meta.get("reference")}')
            p=parse_material(b,'PS4')
            for stage,gapoffs in (('vs',VS_GAP),('ps',PS_GAP)):
                q=stage_tfx(p,stage);stage_rows[stage]+=1
                vals={f'0x{o:X}':u32(b,o) for o in gapoffs}
                req=q['required_slot_count_from_serialized_and_tfx'];cbn=q['cbuffer_vec4_count']
                for key,v in vals.items():
                    equality[f'{stage}:{key}']['equals_required']+=int(v==req)
                    equality[f'{stage}:{key}']['equals_cbuffer_count']+=int(v==cbn)
                    equality[f'{stage}:{key}']['rows']+=1
                    hist[f'{stage}:{key}'][str(v)]+=1
                rows.append({
                  'material':mh,'stage':stage,
                  'shader':p['vertex_shader'] if stage=='vs' else p['pixel_shader'],
                  'vector4_container':norm(p[f'{stage}_vector4_container']),
                  **q,'gap_dwords':vals,
                  'payload_sha256':hashlib.sha256(b).hexdigest(),
                })
        except Exception as ex:
            viol.append(f'{mh}:{ex!r}')

    target=[x for x in rows if x['material']=='80876865' and x['stage']=='ps']
    if len(target)!=1:viol.append(f'jaw_target_rows:{len(target)}')
    else:
        t=target[0]
        if t['cbuffer_vec4_count']!=4 or t['max_op4a_operand']!=4 or t['required_slot_count_from_serialized_and_tfx']!=5:
            viol.append('jaw target slot relation drift')
        if t['gap_dwords'].get('0x320')!=5 or t['gap_dwords'].get('0x324')!=16:
            viol.append(f"jaw gap drift:{t['gap_dwords']!r}")

    correlation=[]
    for k,cnt in sorted(equality.items()):
        n=cnt['rows']
        correlation.append({
          'field':k,'row_count':n,
          'equals_required_count':cnt['equals_required'],
          'equals_required_fraction':cnt['equals_required']/n if n else 0,
          'equals_cbuffer_count':cnt['equals_cbuffer_count'],
          'equals_cbuffer_count_fraction':cnt['equals_cbuffer_count']/n if n else 0,
          'value_histogram':dict(hist[k]),
        })
    correlation.sort(key=lambda x:(-x['equals_required_fraction'],-x['equals_cbuffer_count_fraction'],x['field']))

    out={
      'schema_version':1,
      'status':'D1_XUR_ROI_MATERIAL_GAP_TFX_CORRELATION_EXACT' if not viol else 'D1_XUR_ROI_MATERIAL_GAP_TFX_CORRELATION_VIOLATIONS',
      'carrier_sha256':hashlib.sha256(a.carrier.read_bytes()).hexdigest(),
      'active_material_count':len(mats),'stage_row_count':len(rows),'stage_histogram':dict(stage_rows),
      'gap_offsets':{'vs':[f'0x{x:X}' for x in VS_GAP],'ps':[f'0x{x:X}' for x in PS_GAP]},
      'correlations_ranked':correlation,
      'jaw_80876865_ps':target[0] if len(target)==1 else None,
      'rows':rows,
      'proof_boundary':{
        'gap_field_semantic_name_proven':False,
        'runtime_slot4_initial_value_proven':False,
        'correlation_is_structural_evidence_only':True,
      },
      'violations':viol,
      'policy':'Exact current Xur retail material bytes and TFX framing. A gap field is not named from correlation alone; promotion requires a deterministic cross-material relation plus independent engine/source evidence where available.'
    }
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({
      'status':out['status'],'active_material_count':len(mats),'stage_row_count':len(rows),
      'top_correlations':correlation[:12],
      'jaw':None if not target else {
        'cbuffer_count':target[0]['cbuffer_vec4_count'],'max4a':target[0]['max_op4a_operand'],
        'required':target[0]['required_slot_count_from_serialized_and_tfx'],'gap':target[0]['gap_dwords']
      },
      'violations':viol
    },indent=2))
    return 0 if not viol else 2
if __name__=='__main__':raise SystemExit(main())
