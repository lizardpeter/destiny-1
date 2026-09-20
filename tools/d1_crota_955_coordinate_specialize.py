#!/usr/bin/env python3
"""Material-specialize PS8108E955 image-coordinate paths for Crota.

This proof combines:
* exact paired material stage state;
* exact GCN image resource/sampler + coordinate dataflow;
* exact pinned PS8108E955 native identity.

For the selected Crota materials, serialized API0 coordinate coefficients make the
t3/t4/t1/t2 sample coordinates collapse to zero.  t1/t2/t4 additionally bind the
same texture and the same sampler descriptor, so their native sampled RGBA values
are identical even though the shader carries them as separate resources/operations.

The surviving t0 coordinate source is left as attr1.x/attr1.y.  No UV semantic is
assigned to attr1 here.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

SHADER='8108E955'
GCN_SHA='2bb9b4e27b0aa204e5d0b47ce8d85746853da1187d8b0ce2700b94009810795f'
MATERIALS=('8108E7A9','8108E7B2')
EXPECTED_TEXTURES={0:'8108E7B6',1:'80AACF2A',2:'80AACF2A',3:'80AAD0E1',4:'80AACF2A'}
EXPECTED_SAMPLE_CHAIN=[
    ('00000000004C',3,4,['v4','v5','v6','v7']),
    ('0000000000D8',4,5,['v4','v5','v6','v7']),
    ('0000000000E0',1,2,['v8','v9','v10','v11']),
    ('0000000000E8',2,3,['v16','v17','v18','v19']),
    ('0000000000F4',0,1,['v2','v3','v4','v5']),
]
# API0 dwords 28..47 are the exact coordinate transform rows consumed before
# the first four samples in the pinned native program.
EXPECTED_28_47=[
    0.0,0.0,0.0,0.0,
    0.0,0.0,0.0,0.0,
    0.0,0.0,0.0,0.0,
    0.10000000149011612,0.10000000149011612,-0.05000000074505806,-0.05000000074505806,
    0.0,0.0,0.0,0.0,
]
ANCHORS=[
    'v_mov_b32       v4, s22',
    'v_mov_b32       v5, s23',
    'v_mac_f32       v4, s20, v2',
    'v_mac_f32       v5, s21, v3',
    'image_sample    v[4:5], v[4:7], s[24:31], s[32:35] dmask:3',
    'v_mad_f32       v4, v4, s20, v2',
    'v_mad_f32       v5, v5, s21, v3',
    'v_add_f32       v4, s22, v4',
    'v_add_f32       v5, s23, v5',
    'v_mad_f32       v4, s24, v4, v6',
    'v_mad_f32       v5, s25, v5, v7',
    'v_mac_f32       v8, s28, v2',
    'v_mac_f32       v9, s29, v3',
    'v_mad_f32       v16, v2, s32, v10',
    'v_mad_f32       v17, v3, s33, v11',
    'image_sample    v[4:7], v[4:7], s[36:43], s[44:47] dmask:15',
    'image_sample    v[12:15], v[8:11], s[48:55], s[8:11] dmask:15',
    'image_sample    v[8:11], v[16:19], s[56:63], s[64:67] dmask:15',
    'image_sample    v2, v[2:5], s[20:27], s[4:7]',
]

def norm(x): return str(x).upper().removeprefix('0X').zfill(8)

def flat(stage):
    out=[]
    for r in (stage.get('cbuffers') or {}).get('items',[]):
        out.extend(float(x) for x in r['value'])
    return out

def texmap(stage):
    return {int(x['texture_index']):norm(x['texture']) for x in (stage.get('textures') or {}).get('items',[])}

def sampler_rows(stage):
    rows=stage.get('sampler_references') or []
    return [{
        'inline_index':int(x['inline_index']),
        'sampler_taghash':norm(x['sampler_taghash']),
        'descriptor':((x.get('native_sampler') or {}).get('decoded') or {}),
    } for x in rows]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--stage-state',type=Path,required=True)
    ap.add_argument('--coordinate-slices',type=Path,required=True)
    ap.add_argument('--extract-report',type=Path,required=True)
    ap.add_argument('--disasm',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()

    st=json.loads(a.stage_state.read_text())
    cs=json.loads(a.coordinate_slices.read_text())
    ex=json.loads(a.extract_report.read_text())
    violations=[];rows=[]

    if st.get('status')!='D1_MATERIAL_STAGE_STATE_EXACT' or st.get('violations'):
        violations.append('stage state not exact')
    if cs.get('status')!='D1_GCN_IMAGE_COORDINATE_SLICE_EXACT' or cs.get('violations'):
        violations.append('coordinate slices not exact')
    if ex.get('status')!='D1_WORLD_PIXEL_SHADER_GCN_EXACT' or ex.get('error_count'):
        violations.append('shader extract not exact')

    er=[x for x in ex.get('shaders',[]) if norm(x.get('shader'))==SHADER]
    if len(er)!=1 or str(er[0].get('gcn_sha256','')).lower()!=GCN_SHA:
        violations.append(f'{SHADER}: exact GCN identity drift')

    text=a.disasm.read_text(errors='replace')
    missing=[x for x in ANCHORS if x not in text]
    if missing: violations.append(f'{SHADER}: missing native coordinate anchors {missing}')

    csr=[x for x in cs.get('shaders',[]) if norm(x.get('shader'))==SHADER]
    if len(csr)!=1:
        violations.append(f'{SHADER}: expected one coordinate-slice row, got {len(csr)}')
        samples=[]
    else:
        samples=csr[0].get('samples') or []
    got=[(x['address'],int(x['texture_index']),int(x['sampler_index']),x['encoded_coordinate_registers']) for x in samples]
    if got!=EXPECTED_SAMPLE_CHAIN: violations.append(f'{SHADER}: sample chain drift {got}')

    mats={norm(k):v for k,v in (st.get('materials') or {}).items()}
    for mh in MATERIALS:
        try:
            m=mats.get(mh)
            if not m or m.get('error'): raise ValueError('material missing/error')
            ps=m['ps']
            if norm(ps['shader'])!=SHADER: raise ValueError(f"PS {ps['shader']} != {SHADER}")
            if texmap(ps)!=EXPECTED_TEXTURES: raise ValueError(f'texture map drift {texmap(ps)}')
            vals=flat(ps)
            if len(vals)<=47: raise ValueError(f'cbuffer too short: {len(vals)}')
            if vals[28:48]!=EXPECTED_28_47:
                raise ValueError(f'API0 dwords28:47 drift {vals[28:48]}')

            sr=sampler_rows(ps)
            if len(sr)!=5: raise ValueError(f'sampler row count {len(sr)} != 5')
            tags=[x['sampler_taghash'] for x in sr]
            if len(set(tags))!=1: raise ValueError(f'sampler taghashes differ {tags}')
            desc0=sr[0]['descriptor']
            for x in sr[1:]:
                if x['descriptor']!=desc0: raise ValueError('native sampler descriptors differ')
            if (desc0.get('wrap_x') or {}).get('gnm_name')!='Wrap' or (desc0.get('wrap_y') or {}).get('gnm_name')!='Wrap':
                raise ValueError(f'sampler wrap drift {desc0}')
            if (desc0.get('mag_filter') or {}).get('gnm_name')!='Bilinear' or (desc0.get('min_filter') or {}).get('gnm_name')!='Bilinear':
                raise ValueError(f'sampler filter drift {desc0}')
            if int(desc0.get('force_unnormalized_raw',-1))!=0:
                raise ValueError(f'sampler normalized-coordinate flag drift {desc0}')

            # Algebra from exact native anchors + exact dword values:
            # first sample: coord3.xy = (m36*attr1.x+m38, m37*attr1.y+m39) = (0,0)
            # t4: intermediate is multiplied by m44/m45 and biased by m46/m47 => (0,0)
            # t1: (m28*attr1.x+m30, m29*attr1.y+m31) = (0,0)
            # t2: (m32*attr1.x+m34, m33*attr1.y+m35) = (0,0)
            # t0 is sampled before attr1 registers are overwritten: first two encoded lanes are attr1.x/y.
            rows.append({
                'material':mh,'pixel_shader':SHADER,
                'texture_map':{str(k):v for k,v in sorted(EXPECTED_TEXTURES.items())},
                'sampler_taghash':tags[0],
                'sampler_descriptor_exact':{
                    'wrap_x':desc0.get('wrap_x'),'wrap_y':desc0.get('wrap_y'),
                    'force_unnormalized_raw':desc0.get('force_unnormalized_raw'),
                    'mag_filter':desc0.get('mag_filter'),'min_filter':desc0.get('min_filter'),
                    'mip_filter':desc0.get('mip_filter'),
                },
                'coordinate_specialization':{
                    't3':'first two encoded coordinate lanes = (0,0)',
                    't4':'first two encoded coordinate lanes = (0,0); t3 sampled value contribution to this coordinate is multiplied by exact zeros',
                    't1':'first two encoded coordinate lanes = (0,0)',
                    't2':'first two encoded coordinate lanes = (0,0)',
                    't0':'first two encoded coordinate lanes = attr1.x, attr1.y',
                },
                'same_sample_equivalence':{
                    'texture_indices':[1,2,4],
                    'texture':'80AACF2A',
                    'same_sampler':True,
                    'same_first_two_encoded_coordinate_lanes':[0.0,0.0],
                    'conclusion':'t1.rgba == t2.rgba == t4.rgba for this selected material under the same native texture+sampler+coordinate state',
                },
                't3_terminal_value_effect':'DEAD_FOR_T4_COORDINATE_AFTER_EXACT_ZERO_MULTIPLIERS',
                'api0_coordinate_dwords_28_47':vals[28:48],
            })
        except Exception as ex0:
            violations.append(f'{mh}: {ex0}')

    out={
        'schema':'d1_crota_955_coordinate_specialization/v1',
        'status':'D1_CROTA_955_COORDINATE_SPECIALIZATION_EXACT' if len(rows)==2 and not violations else 'D1_CROTA_955_COORDINATE_SPECIALIZATION_PARTIAL',
        'rows':rows,'violations':violations,
        'semantic_boundary':{
            'native_coordinate_arithmetic':'EXACT_FOR_SELECTED_MATERIALS',
            'resource_sampler_identity':'EXACT',
            'attr1_semantic_name':'WITHHELD',
            'encoded_coordinate_range_dimensionality':'WITHHELD_BEYOND_FIRST_TWO_PROVEN_LANES',
            'filtered_sample_numeric_value_at_zero':'NOT_EVALUATED_HERE',
        },
        'policy':'The first two coordinate lanes are reduced from exact native arithmetic and exact serialized constants. Equality of t1/t2/t4 is promoted because texture, sampler descriptor and those coordinate lanes are identical. No UV label or hardware-filtered numeric sample value is invented.',
    }
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'status':out['status'],'rows':rows,'violations':violations},indent=2))
    return 0 if out['status']=='D1_CROTA_955_COORDINATE_SPECIALIZATION_EXACT' else 2

if __name__=='__main__':raise SystemExit(main())
