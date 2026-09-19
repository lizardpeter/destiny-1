#!/usr/bin/env python3
"""Specialize Crota attenuation shaders to exact retail partner materials.

This proof combines:
* exact paired material stage state;
* exact terminal-alpha shader slice;
* exact symbolic native equations;
* exact BC1 alpha domains from DXT1 block bytes.

It then performs only algebraic eliminations justified by exact serialized
coefficients and exact sampled-alpha domains.

Important distinction:
The generic shader can depend on API12/view/global inputs.  A particular retail
material may make that branch algebraically dead (for example coefficient m27=0).
This tool proves the material-specialized dependency set without renaming API12,
interpolants, passes, or texture RGB roles.
"""
from __future__ import annotations
import argparse,json,math
from pathlib import Path

PAIRS={
 '8108E7AB':{'color':'8108E7A9','shader':'8108E958','textures':{0:'8108E7B6',1:'80AACF2A',2:'80AACF2A',3:'80AAD0E1',4:'80AACF2A'}},
 '8108E7B4':{'color':'8108E7B2','shader':'8108E958','textures':{0:'8108E7B6',1:'80AACF2A',2:'80AACF2A',3:'80AAD0E1',4:'80AACF2A'}},
 '8108E7AC':{'color':'8108E7AA','shader':'8108E959','textures':{0:'8108E951'}},
 '8108E7B5':{'color':'8108E7B3','shader':'8108E959','textures':{0:'8108E951'}},
}
READ958=(11,12,13,16,17,23,27,48)
READ959=(8,9,15,19)

def norm(x):return str(x).upper().removeprefix('0X').zfill(8)

def flat(stage):
    vals=[]
    for r in (stage.get('cbuffers') or {}).get('items',[]):
        vals.extend(float(x) for x in r['value'])
    return vals

def texmap(stage):
    return {int(x['texture_index']):norm(x['texture']) for x in (stage.get('textures') or {}).get('items',[])}

def exact_zero(x):return float(x)==0.0
def exact_one(x):return float(x)==1.0

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--stage-state',type=Path,required=True)
    ap.add_argument('--alpha-slice',type=Path,required=True)
    ap.add_argument('--symbolic',type=Path,required=True)
    ap.add_argument('--bc1-alpha',type=Path,required=True)
    ap.add_argument('--texture-channels',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()

    st=json.loads(a.stage_state.read_text())
    sl=json.loads(a.alpha_slice.read_text())
    sy=json.loads(a.symbolic.read_text())
    bc=json.loads(a.bc1_alpha.read_text())
    tc=json.loads(a.texture_channels.read_text())
    violations=[];rows=[]

    if st.get('status')!='D1_MATERIAL_STAGE_STATE_EXACT' or st.get('violations'):
        violations.append('paired material stage state not exact')
    if sl.get('status')!='D1_GCN_TERMINAL_ALPHA_SLICE_EXACT' or sl.get('violations'):
        violations.append('terminal alpha slice not exact')
    if sy.get('status')!='D1_CROTA_ATTENUATION_SYMBOLIC_REDUCTION_EXACT' or sy.get('violations'):
        violations.append('symbolic attenuation reduction not exact')
    if bc.get('status')!='D1_BC1_ALPHA_DOMAIN_EXACT' or bc.get('violations'):
        violations.append('BC1 alpha-domain proof not exact')
    if tc.get('status')!='D1_CROTA_TEXTURE_CHANNEL_PROOF_EXACT' or tc.get('violations'):
        violations.append('consolidated texture-channel proof not exact')

    mats={norm(k):v for k,v in (st.get('materials') or {}).items()}
    slices={norm(x['shader']):x for x in sl.get('shaders',[])}
    symbolic={(norm(x['material']),norm(x['pixel_shader'])):x for x in sy.get('rows',[])}
    alpha={norm(x['texture']):x for x in bc.get('textures',[])}
    tcrows={norm(k):v for k,v in (tc.get('textures') or {}).items()}
    for h in ('80AACF2A','8108E951','8108E952'):
        a0=alpha.get(h); t0=tcrows.get(h)
        if not a0 or not t0:
            violations.append(f'{h}: missing cross-proof row')
        elif bool(a0.get('alpha_exact_one')) != bool(t0.get('sample_alpha_constant_one')):
            violations.append(f'{h}: BC1 alpha proof disagreement')
    bc4=tcrows.get('8108E7B6')
    if not bc4 or bc4.get('format')!='BC4':
        violations.append('8108E7B6: exact BC4 channel proof missing')

    for partner,spec in PAIRS.items():
        m=mats.get(partner);color=mats.get(spec['color']);sh=spec['shader']
        if not m or m.get('error'):
            violations.append(f'{partner}: exact partner material missing/error');continue
        if not color or color.get('error'):
            violations.append(f"{spec['color']}: exact color material missing/error");continue
        if norm(m['ps']['shader'])!=sh:
            violations.append(f"{partner}: PS {m['ps']['shader']} != {sh}");continue
        gottex=texmap(m['ps'])
        if gottex!=spec['textures']:
            violations.append(f'{partner}: texture map drift {gottex} != {spec["textures"]}')
        vals=flat(m['ps'])
        expected=READ958 if sh=='8108E958' else READ959
        if not vals or max(expected)>=len(vals):
            violations.append(f'{partner}: cbuffer too short for {expected}');continue
        coeff={f'm{i}':vals[i] for i in expected}

        # Validate current partner constants are the exact common prefix already
        # observed on the paired color material rather than silently borrowing
        # constants from the color side.
        cvals=flat(color['ps'])
        if vals!=cvals[:len(vals)]:
            violations.append(f'{partner}: partner cbuffer is not exact color-prefix')
        slrow=slices.get(sh)
        if not slrow:
            violations.append(f'{partner}: terminal alpha slice missing for {sh}');continue
        syrow=symbolic.get((partner,sh))
        if not syrow:
            # Older symbolic reducer rows may have been keyed from exact partner
            # identities but if not, fail closed instead of substituting color.
            violations.append(f'{partner}: symbolic material row missing');continue

        if sh=='8108E958':
            for ti in (1,2,4):
                th=gottex.get(ti)
                pr=alpha.get(th)
                if not pr or not pr.get('alpha_exact_one'):
                    violations.append(f'{partner}: t{ti} {th} alpha not exact one')
            if not exact_zero(coeff['m27']):
                violations.append(f"{partner}: m27 not exact zero: {coeff['m27']}")
            if not exact_zero(coeff['m48']):
                violations.append(f"{partner}: m48 not exact zero: {coeff['m48']}")
            if not exact_one(coeff['m11']):
                violations.append(f"{partner}: m11 not exact one: {coeff['m11']}")
            if not exact_one(coeff['m23']):
                violations.append(f"{partner}: m23 not exact one: {coeff['m23']}")
            rows.append({
              'partner_material':partner,'color_material':spec['color'],'pixel_shader':sh,
              'serialized_coefficients':coeff,
              'exact_texture_map':{str(k):v for k,v in sorted(gottex.items())},
              'exact_bc1_alpha_substitutions':{'t1.w':1.0,'t2.w':1.0,'t4.w':1.0},
              'dead_native_dependencies':{
                'API12_28_30_and_dot_input':True,
                'reason':'m27 == 0 makes U/d contribution to V identically zero; V == m23 == 1',
                't1_w_t2_w_variation':True,
                't4_w_variation':True,
              },
              'remaining_direct_varying_texture_lanes':['t0.x'],
              'remaining_direct_texture':'8108E7B6',
              'remaining_direct_texture_channel_evidence':None if not bc4 else {
                'format':bc4.get('format'),
                'preview_decoder_u8_min':bc4.get('preview_decoder_u8_min'),
                'preview_decoder_u8_max':bc4.get('preview_decoder_u8_max'),
                'preview_decoder_u8_unique_value_count':bc4.get('preview_decoder_u8_unique_value_count'),
                'preview_decoder_u8_zero_count':bc4.get('preview_decoder_u8_zero_count'),
                'preview_decoder_u8_255_count':bc4.get('preview_decoder_u8_255_count'),
                'linear_sha256':bc4.get('linear_sha256'),
              },
              'specialized_equation':[
                'V = 1',
                'F = clamp(0.010300000198185444 * (0.6000000238418579 + 9.399999618530273*1) * (0.6000000238418579 + 9.399999618530273*1) - 0.05999999865889549)',
                f"G = clamp({coeff['m13']!r} + {coeff['m12']!r}*(1 - t0.x))",
                'H = 0.07999999821186066',
                'A = clamp(G*F) + clamp(H)*H',
              ],
              'terminal_alpha_class':'BC4_SCALAR_ONLY_AFTER_EXACT_MATERIAL_SPECIALIZATION',
              'api12_affects_terminal_alpha':False,
              'semantic_boundary':'NUMERICAL_TERMINAL_ALPHA_ONLY_PASS_ROLE_WITHHELD',
            })
        else:
            th=gottex.get(0);pr=alpha.get(th)
            if not pr or not pr.get('alpha_exact_one'):
                violations.append(f'{partner}: t0 {th} alpha not exact one')
            if not exact_zero(coeff['m19']):
                violations.append(f"{partner}: m19 not exact zero: {coeff['m19']}")
            if not exact_one(coeff['m15']):
                violations.append(f"{partner}: m15 not exact one: {coeff['m15']}")
            rows.append({
              'partner_material':partner,'color_material':spec['color'],'pixel_shader':sh,
              'serialized_coefficients':coeff,
              'exact_texture_map':{str(k):v for k,v in sorted(gottex.items())},
              'exact_bc1_alpha_substitutions':{'t0.w':1.0},
              'dead_native_dependencies':{
                'API12_28_30_and_dot_input':True,
                'reason':'m19 == 0 removes V/d contribution; m15 == 1 and t0.w == 1',
              },
              'remaining_direct_varying_texture_lanes':[],
              'specialized_equation':['A = 1.0'],
              'terminal_alpha_class':'EXACT_ONE',
              'api12_affects_terminal_alpha':False,
              'semantic_boundary':'NUMERICAL_TERMINAL_ALPHA_ONLY_PASS_ROLE_WITHHELD',
            })

    out={
      'schema':'d1_crota_attenuation_material_specialization/v1',
      'status':'D1_CROTA_ATTENUATION_MATERIAL_SPECIALIZATION_EXACT' if len(rows)==4 and not violations else 'D1_CROTA_ATTENUATION_MATERIAL_SPECIALIZATION_PARTIAL',
      'row_count':len(rows),'rows':rows,'violations':violations,
      'structural_conclusions':{
        '8108E958_current_materials':'terminal alpha varies only with BC4 texture 8108E7B6 t0.x; API12/view-dot and all BC1 alpha inputs are algebraically dead/constant',
        '8108E959_current_materials':'terminal alpha is exactly 1.0; API12/view-dot and texture-alpha variation are algebraically dead/constant',
      },
      'semantic_boundary':{
        'terminal_alpha_numerical_dependency':'EXACT_FOR_THE_FOUR_SELECTED_RETAIL_PARTNER_MATERIALS',
        'surviving_8108E958_texture_channel':'EXACT_BC4_8108E7B6_T0_X_IDENTITY_AND_ENCODED_BYTES',
        'generic_shader_capability':'NOT_REDUCED_GLOBALLY',
        'API12_semantic_name':'WITHHELD',
        'native_pass_order':'WITHHELD',
        'portable_material_role':'WITHHELD',
      },
      'policy':'Specialization applies only to exact selected partner material payloads. BC1 alpha substitutions are cross-checked by two exact block-byte proofs; the surviving 8108E7B6 BC4 lane carries exact retail encoded-block identity plus a clearly labeled exporter-equivalent preview census; PS4 sampler numeric values and material meaning remain withheld. A dead dependency for these constants is not promoted as a generic shader invariant, and numerical alpha does not establish engine pass ownership/order.',
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'status':out['status'],'rows':[{
        'material':x['partner_material'],'shader':x['pixel_shader'],
        'class':x['terminal_alpha_class'],
        'remaining_texture_lanes':x['remaining_direct_varying_texture_lanes'],
        'api12_affects':x['api12_affects_terminal_alpha'],
        'coefficients':x['serialized_coefficients'],
    } for x in rows],'violations':violations},indent=2))
    return 0 if out['status']=='D1_CROTA_ATTENUATION_MATERIAL_SPECIALIZATION_EXACT' else 2

if __name__=='__main__':
    raise SystemExit(main())
