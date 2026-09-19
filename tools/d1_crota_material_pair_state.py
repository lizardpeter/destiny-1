#!/usr/bin/env python3
"""Integrate exact Crota color/partner material state with paired native GCN.

The material pair identities were recovered from the same high-detail serialized
geometry ranges.  This tool revalidates them against current exact material-stage
state and paired GCN differential output.

It does not assume that a partner's alpha is an opacity semantic.  It records exact
material state, TFX, texture/sampler bindings and shader export/resource differences.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path

PAIRS={
 '8108E7A9':('8108E7AB','8108E955','8108E958'),
 '8108E7AA':('8108E7AC','8108E956','8108E959'),
 '8108E7B1':('809DD1DC','8108E953','80AAE1CD'),
 '8108E7B2':('8108E7B4','8108E955','8108E958'),
 '8108E7B3':('8108E7B5','8108E956','8108E959'),
}

def norm(x): return str(x).upper().removeprefix('0X').zfill(8)

def compact_stage(s):
    return {
      'shader':norm(s.get('shader')),
      'textures':[{'index':int(x['texture_index']),'texture':norm(x['texture'])} for x in (s.get('textures') or {}).get('items',[])],
      'samplers':[{
          'inline_index':int(x['inline_index']),
          'sampler_taghash':norm(x['sampler_taghash']),
          'inline_dwords_hex':x.get('inline_dwords_hex'),
      } for x in s.get('sampler_references',[])],
      'tfx_program_sha256':s.get('tfx_program_sha256'),
      'tfx_bytecode_hex':(s.get('tfx_bytecode') or {}).get('bytes_hex'),
      'private_constants':(s.get('tfx_private_constants') or {}).get('items',[]),
      'cbuffers':(s.get('cbuffers') or {}).get('items',[]),
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--stage-state',type=Path,required=True)
    ap.add_argument('--paired-gcn',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    st=json.loads(a.stage_state.read_text()); gd=json.loads(a.paired_gcn.read_text())
    violations=[]
    if st.get('status')!='D1_MATERIAL_STAGE_STATE_EXACT' or st.get('violations'):
        violations.append('material stage state is not exact')
    if gd.get('status')!='D1_GCN_PAIRED_SHADER_DIFFERENTIAL_EXACT' or gd.get('violations'):
        violations.append('paired GCN differential is not exact')
    mats={norm(k):v for k,v in (st.get('materials') or {}).items()}
    gpair={(norm(x['a']),norm(x['b'])):x for x in gd.get('pairs',[])}
    rows=[]
    for color,(partner,cps,pps) in PAIRS.items():
        cm=mats.get(color); pm=mats.get(partner)
        if not cm: violations.append(f'{color}: color material missing'); continue
        if not pm: violations.append(f'{partner}: partner material missing'); continue
        gotc=norm((cm.get('ps') or {}).get('shader')); gotp=norm((pm.get('ps') or {}).get('shader'))
        if gotc!=cps: violations.append(f'{color}: PS {gotc} != {cps}')
        if gotp!=pps: violations.append(f'{partner}: PS {gotp} != {pps}')
        diff=gpair.get((cps,pps))
        if not diff:
            violations.append(f'{cps}:{pps}: paired GCN differential missing')
        rows.append({
          'color_material':color,'partner_material':partner,
          'color_ps':cps,'partner_ps':pps,
          'color_material_state4_hex':cm.get('material_state4_hex'),
          'partner_material_state4_hex':pm.get('material_state4_hex'),
          'color_material_state4_u8':cm.get('material_state4_u8'),
          'partner_material_state4_u8':pm.get('material_state4_u8'),
          'state4_equal':cm.get('material_state4_hex')==pm.get('material_state4_hex'),
          'color_ps_state':compact_stage(cm['ps']),
          'partner_ps_state':compact_stage(pm['ps']),
          'paired_gcn_differential':diff,
        })
    out={
      'schema':'d1_crota_material_pair_state/v1',
      'status':'D1_CROTA_MATERIAL_PAIR_STATE_EXACT' if len(rows)==len(PAIRS) and not violations else 'D1_CROTA_MATERIAL_PAIR_STATE_PARTIAL',
      'pair_count':len(rows),'pairs':rows,'violations':violations,
      'semantic_boundary':{
          'serialized_pair_identity':'EXACT',
          'material_state_bytes':'EXACT_UNLESS_SEPARATELY_NAMED',
          'shader_resource_and_export_differential':'EXACT_STRUCTURAL',
          'partner_pass_engine_role':'WITHHELD_UNLESS_SEPARATELY_PROVEN',
          'runtime_scalar_values':'WITHHELD',
      },
      'policy':'Pairs are validated against current retail material payloads and exact GCN programs. No portable proxy scalar or texture role is promoted here.',
    }
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'status':out['status'],'pairs':[(x['color_material'],x['partner_material'],x['color_ps'],x['partner_ps'],x['color_material_state4_hex'],x['partner_material_state4_hex'],x['state4_equal']) for x in rows],'violations':violations},indent=2))
    return 0 if out['status']=='D1_CROTA_MATERIAL_PAIR_STATE_EXACT' else 2

if __name__=='__main__': raise SystemExit(main())
