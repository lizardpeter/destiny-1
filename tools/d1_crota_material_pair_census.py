#!/usr/bin/env python3
"""Exact Crota color/attenuation material-pair census.

Consumes source-closed D1 material stage state plus the exact paired GCN
differential.  It compares serialized material state across the five known
high-detail Crota color/attenuation material pairs.

No texture role, pass order, or behavioral semantic is invented here.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

PAIRS={
    '8108E7A9':('8108E955','8108E7AB','8108E958'),
    '8108E7AA':('8108E956','8108E7AC','8108E959'),
    '8108E7B1':('8108E953','809DD1DC','80AAE1CD'),
    '8108E7B2':('8108E955','8108E7B4','8108E958'),
    '8108E7B3':('8108E956','8108E7B5','8108E959'),
}

def norm(x): return str(x).upper().removeprefix('0X').zfill(8)

def texmap(stage):
    return [(int(x['texture_index']),norm(x['texture'])) for x in (stage.get('textures') or {}).get('items',[])]

def samplers(stage):
    return [
        {
            'inline_index':int(x['inline_index']),
            'inline_raw_hex':str(x['inline_raw_hex']).lower(),
            'sampler_taghash':norm(x['sampler_taghash']),
        }
        for x in stage.get('sampler_references',[])
    ]

def vecrows(stage,key):
    return [str(x['raw_hex']).lower() for x in (stage.get(key) or {}).get('items',[])]

def sha_obj(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--stage-state',type=Path,required=True)
    ap.add_argument('--paired-gcn',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    st=json.loads(a.stage_state.read_text())
    gd=json.loads(a.paired_gcn.read_text())
    violations=[]
    if st.get('status')!='D1_MATERIAL_STAGE_STATE_EXACT' or st.get('violations'):
        violations.append('material stage state not exact')
    if gd.get('status')!='D1_GCN_PAIRED_SHADER_DIFFERENTIAL_EXACT' or gd.get('violations'):
        violations.append('paired GCN differential not exact')
    mats={norm(k):v for k,v in (st.get('materials') or {}).items()}
    gpair={(norm(x['a']),norm(x['b'])):x for x in gd.get('pairs',[])}
    rows=[]
    for color,(cps,atten,aps) in PAIRS.items():
        c=mats.get(color); q=mats.get(atten)
        if not c or c.get('error'):
            violations.append(f'{color}: color material unresolved'); continue
        if not q or q.get('error'):
            violations.append(f'{atten}: attenuation material unresolved'); continue
        cps=norm(cps); aps=norm(aps)
        if norm((c.get('ps') or {}).get('shader'))!=cps:
            violations.append(f'{color}: expected PS {cps}, got {(c.get("ps") or {}).get("shader")}')
        if norm((q.get('ps') or {}).get('shader'))!=aps:
            violations.append(f'{atten}: expected PS {aps}, got {(q.get("ps") or {}).get("shader")}')
        gp=gpair.get((cps,aps))
        if gp is None:
            violations.append(f'{cps}:{aps}: paired GCN differential missing')
        cs=list(c.get('material_state4_u8') or []); qs=list(q.get('material_state4_u8') or [])
        if not cs or cs[0]!=0x88:
            violations.append(f'{color}: active blend selector byte0 not 0x88: {cs}')
        if not qs or qs[0]!=0x88:
            violations.append(f'{atten}: active blend selector byte0 not 0x88: {qs}')
        ctex=texmap(c['ps']); qtex=texmap(q['ps'])
        csamp=samplers(c['ps']); qsamp=samplers(q['ps'])
        cpriv=vecrows(c['ps'],'tfx_private_constants'); qpriv=vecrows(q['ps'],'tfx_private_constants')
        cbuf=vecrows(c['ps'],'cbuffers'); qbuf=vecrows(q['ps'],'cbuffers')
        row={
            'color_material':color,'color_pixel_shader':cps,
            'attenuation_material':atten,'attenuation_pixel_shader':aps,
            'material_state4':{'color':c.get('material_state4_hex'),'attenuation':q.get('material_state4_hex'),'identical':c.get('material_state4_hex')==q.get('material_state4_hex')},
            'vertex_shader':{'color':norm(c['vs']['shader']),'attenuation':norm(q['vs']['shader']),'identical':norm(c['vs']['shader'])==norm(q['vs']['shader'])},
            'ps_texture_map':{'color':ctex,'attenuation':qtex,'identical':ctex==qtex,'shared_edges':sorted(set(ctex)&set(qtex)),'color_only_edges':sorted(set(ctex)-set(qtex)),'attenuation_only_edges':sorted(set(qtex)-set(ctex))},
            'ps_sampler_records':{'color':csamp,'attenuation':qsamp,'identical':csamp==qsamp},
            'ps_tfx':{
                'color_sha256':c['ps'].get('tfx_program_sha256'),
                'attenuation_sha256':q['ps'].get('tfx_program_sha256'),
                'identical':c['ps'].get('tfx_program_sha256')==q['ps'].get('tfx_program_sha256'),
            },
            'ps_private_constants':{'color_sha256':sha_obj(cpriv),'attenuation_sha256':sha_obj(qpriv),'identical':cpriv==qpriv,'color_count':len(cpriv),'attenuation_count':len(qpriv)},
            'ps_cbuffers':{'color_sha256':sha_obj(cbuf),'attenuation_sha256':sha_obj(qbuf),'identical':cbuf==qbuf,'color_count':len(cbuf),'attenuation_count':len(qbuf)},
            'gcn_resource_differential':None if gp is None else {
                'shared_texture_indices':gp['resource_usage']['shared_texture_indices'],
                'color_only_texture_indices':gp['resource_usage']['a_only_texture_indices'],
                'attenuation_only_texture_indices':gp['resource_usage']['b_only_texture_indices'],
                'color_image_instruction_signatures':gp['resource_usage']['a'].get('image_instruction_signatures',[]),
                'attenuation_image_instruction_signatures':gp['resource_usage']['b'].get('image_instruction_signatures',[]),
                'color_exports':gp['native_structure']['a']['exports'],
                'attenuation_exports':gp['native_structure']['b']['exports'],
            },
            'semantic_boundary':'EXACT_PAIR_STRUCTURE_ONLY',
        }
        rows.append(row)
    out={
        'schema':'d1_crota_material_pair_census/v1',
        'status':'D1_CROTA_MATERIAL_PAIR_CENSUS_EXACT' if len(rows)==len(PAIRS) and not violations else 'D1_CROTA_MATERIAL_PAIR_CENSUS_PARTIAL',
        'expected_pair_count':len(PAIRS),'resolved_pair_count':len(rows),
        'rows':rows,'violations':violations,
        'promotion':{
            'known_blend_selector':'0x88 -> blend state 8 (promoted independently)',
            'pair_structure':'exact material identities + exact PS identities + exact serialized-state comparison + exact GCN resource differential',
            'pass_order':'WITHHELD',
            'runtime_attenuation_scalar_semantics':'WITHHELD',
        },
        'policy':'Pair membership is frozen from the exact Crota actor material graph. This census compares source bytes and native shader resource structure only. It does not derive pass order or replace unresolved attenuation proxies with guessed values.',
    }
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'status':out['status'],'pairs':[{
        'materials':(x['color_material'],x['attenuation_material']),
        'ps':(x['color_pixel_shader'],x['attenuation_pixel_shader']),
        'same_vs':x['vertex_shader']['identical'],
        'same_textures':x['ps_texture_map']['identical'],
        'same_samplers':x['ps_sampler_records']['identical'],
        'same_tfx':x['ps_tfx']['identical'],
        'same_cbuffers':x['ps_cbuffers']['identical'],
        'shared_gcn_t':x['gcn_resource_differential']['shared_texture_indices'] if x['gcn_resource_differential'] else None,
    } for x in rows],'violations':violations},indent=2))
    return 0 if out['status']=='D1_CROTA_MATERIAL_PAIR_CENSUS_EXACT' else 2

if __name__=='__main__': raise SystemExit(main())
