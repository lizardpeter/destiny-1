#!/usr/bin/env python3
"""Cross-platform D1 Xbox test for PS material TFX opcode 0x4A.

The PS4 Xur corpus proves 0x4A is a push-one operation but does not yet name its
source.  Xbox ROI keeps the same material/TFX architecture while pixel shaders
are DXBC, so b0's declared vector count is independently observable.

For every resident Xbox ROI material in one exact retail package this tool:
- decodes PS TFX and records every 0x4A operand;
- resolves material b0 storage (inline or external Vector4Container);
- parses the DXBC pixel shader and its declared b0 vec4 count;
- tests whether every 0x4A operand lies in the independently declared b0 domain;
- preserves the anonymous ROI tail dwords +0x310..+0x328 for cross-platform
  correlation with the PS4 Xur result.

This is a domain proof only.  Even perfect index agreement is not by itself a
machine-code proof that 0x4A loads b0; the semantic promotion is kept separate.
"""
from __future__ import annotations
import argparse,collections,json,struct,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))

from d1_entry_extract import EntryReader
from d1_material_decode import parse_material,checked_rel_array
from d1_dxbc_probe import (
    XBOX_MATERIAL_CLASS,XBOX_SHADER_TAG_CLASS,XBOX_VECTOR_CONTAINER_CLASS,
    parse_shader_tag,
)
from d1_vector_container_probe import xbox_count_from_metadata_size
from d1_tfx_program_inventory import disassemble

def u32(b,o): return struct.unpack_from('<I',b,o)[0]

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('pkg',type=Path)
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args();r=EntryReader(a.pkg,a.runtime);viol=[]
    if r.h.get('platform')!='XboxOne': raise SystemExit('XboxOne package required')
    by={e['tag_hash'].upper():e for e in r.entries}
    mats=[e for e in r.entries if e['type']==16 and e['subtype']==0 and e['reference'].upper()==XBOX_MATERIAL_CLASS and r.available(e['index'])]

    rows=[];operand_hist=collections.Counter();tail_hist={f'0x{x:X}':collections.Counter() for x in range(0x310,0x32C,4)}
    compared=0;in_domain=0;out_domain=0;shader_unavailable=0;parse_incomplete=0
    for e in mats:
        b=r.entry(e['index'])
        try:m=parse_material(b,'XboxOne')
        except Exception as ex:
            viol.append(f"{e['tag_hash']}:material:{ex!r}");continue
        raw=bytes.fromhex(m['ps_tfx_bytecode']['bytes_hex'])
        q=disassemble(raw)
        if q.get('complete') is not True:
            parse_incomplete+=1;continue
        operands=[int(op['operand_bytes'][0]) for op in q.get('ops') or [] if op.get('name')=='Unk4a']
        if not operands:continue
        for x in operands:operand_hist[str(x)]+=1
        tail={f'0x{x:X}':u32(b,x) for x in range(0x310,0x32C,4)}
        for k,v in tail.items():tail_hist[k][str(v)]+=1

        pe=by.get(m['pixel_shader'].upper())
        dxbc_b0=None;shader_error=None
        if not pe or not r.available(pe['index']) or pe['reference'].upper()!=XBOX_SHADER_TAG_CLASS:
            shader_unavailable+=1
        else:
            try:
                sh=parse_shader_tag(r.entry(pe['index']))
                dec=sh['dxbc']['declarations'] or {}
                b0=next((x for x in dec.get('cbuffers') or [] if int(x['register'])==0),None)
                dxbc_b0=None if b0 is None else int(b0['vec4_count'])
            except Exception as ex:shader_error=repr(ex)

        inline_count=int(m['ps_cbuffers']['count'])
        vh=m['ps_vector4_container'].upper()
        ve=by.get(vh)
        external_count=None
        if ve and ve['reference'].upper()==XBOX_VECTOR_CONTAINER_CLASS:
            external_count=xbox_count_from_metadata_size(int(ve['file_size']))
        material_b0_count=external_count if external_count is not None else inline_count
        storage='external_ps_vector4_container' if external_count is not None else 'inline_ps_cbuffers'

        row={
          'material':e['tag_hash'].upper(),'pixel_shader':m['pixel_shader'].upper(),
          'op4a_operands':operands,'op4a_occurrence_count':len(operands),
          'inline_ps_cbuffer_count':inline_count,'ps_vector4_container':vh,
          'external_vector_count':external_count,'material_b0_storage':storage,
          'material_b0_vec4_count':material_b0_count,'dxbc_b0_vec4_count':dxbc_b0,
          'tail_dwords':tail,'shader_error':shader_error,
        }
        if dxbc_b0 is not None:
            compared+=len(operands)
            row['material_b0_matches_dxbc_b0']=material_b0_count==dxbc_b0
            row['all_0x4A_operands_in_dxbc_b0_domain']=all(x<dxbc_b0 for x in operands)
            for x in operands:
                if x<dxbc_b0:in_domain+=1
                else:out_domain+=1
            if material_b0_count!=dxbc_b0:
                viol.append(f"{e['tag_hash']}:material_b0={material_b0_count}:dxbc_b0={dxbc_b0}")
        rows.append(row)

    out={
      'schema_version':1,
      'status':'D1_XBOX_PS_TFX_0X4A_B0_DOMAIN_CENSUS_EXACT' if not viol else 'D1_XBOX_PS_TFX_0X4A_B0_DOMAIN_CENSUS_VIOLATIONS',
      'package':str(a.pkg),'platform':r.h.get('platform'),
      'resident_material_count':len(mats),'material_rows_with_ps_0x4A':len(rows),
      'op4a_occurrence_count':sum(x['op4a_occurrence_count'] for x in rows),
      'op4a_operand_histogram':dict(sorted(operand_hist.items(),key=lambda kv:int(kv[0]))),
      'dxbc_domain_compared_occurrence_count':compared,
      'op4a_operand_in_dxbc_b0_domain_count':in_domain,
      'op4a_operand_outside_dxbc_b0_domain_count':out_domain,
      'all_compared_0x4A_operands_in_dxbc_b0_domain':compared>0 and out_domain==0,
      'tail_dword_histograms':{k:dict(v) for k,v in tail_hist.items()},
      'shader_unavailable_row_count':shader_unavailable,
      'tfx_incomplete_material_count':parse_incomplete,
      'rows':rows,'violations':viol,
      'proof_boundary':{
        'DXBC_b0_declaration_is_independent_of_TFX_parser':True,
        '0x4A_push_one_stack_effect_proven_elsewhere':True,
        '0x4A_exact_load_from_b0_semantic_identity_proven':False,
      },
      'policy':'Cross-platform index-domain evidence. Do not rename D1 0x4A solely from correlation; promote only after storage/runtime behavior independently agrees.'
    }
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in (
      'status','resident_material_count','material_rows_with_ps_0x4A','op4a_occurrence_count',
      'op4a_operand_histogram','dxbc_domain_compared_occurrence_count',
      'op4a_operand_in_dxbc_b0_domain_count','op4a_operand_outside_dxbc_b0_domain_count',
      'all_compared_0x4A_operands_in_dxbc_b0_domain','shader_unavailable_row_count',
      'tfx_incomplete_material_count','violations')},indent=2))
    return 0 if not viol else 2

if __name__=='__main__':raise SystemExit(main())
