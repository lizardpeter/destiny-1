#!/usr/bin/env python3
"""Correlate exact D1 Tower light structures without guessing render semantics.

Inputs are already source-closed artifacts:
  * 737 LightData/transform/bounds instances,
  * exact LightData +0x80 SMaterial_ROI ownership,
  * 497 decoded source light materials,
  * 412 decoded light TFX BufferData programs,
  * mathematically proven AFFINE_VOLUME / PROJECTIVE_VOLUME structure.

This stage asks which opaque fields, shader families, and program families partition the
retail data.  It deliberately does NOT rename a family "point", "spot", "area", assign
RGB/intensity, or promote unknown flag bits.  The output is evidence for the next source-
dataflow pass, not a visual approximation.
"""
from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


def norm(x: object) -> str:
    return str(x).upper().removeprefix('0X').zfill(8)


def purity(rows, key):
    out=[]
    for value, kinds in sorted(rows.items(), key=lambda kv: str(kv[0])):
        c=Counter(kinds); n=sum(c.values())
        out.append({
            key:value,'count':n,'volume_kind_histogram':dict(c),
            'single_volume_kind':len(c)==1,
            'volume_kind':next(iter(c)) if len(c)==1 else None,
        })
    return out


def stats(values):
    vals=[float(x) for x in values if isinstance(x,(int,float)) and math.isfinite(float(x))]
    if not vals:return {'count':0}
    rounded={round(x,9) for x in vals}
    return {
        'count':len(vals),'unique_rounded_1e9_count':len(rounded),
        'min':min(vals),'max':max(vals),
        'constant_rounded_1e9':len(rounded)==1,
        'constant_value':next(iter(rounded)) if len(rounded)==1 else None,
    }


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--lighting-census',type=Path,required=True)
    ap.add_argument('--semantic-probe',type=Path,required=True)
    ap.add_argument('--material-manifest',type=Path,required=True)
    ap.add_argument('--volume-invariants',type=Path,required=True)
    ap.add_argument('--tfx-inventory',type=Path,required=True)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()

    lighting=json.loads(a.lighting_census.read_text())
    sem=json.loads(a.semantic_probe.read_text())
    mats=json.loads(a.material_manifest.read_text())
    vol=json.loads(a.volume_invariants.read_text())
    tfx=json.loads(a.tfx_inventory.read_text())

    required={
        'lighting':(lighting.get('status'),'D1_WORLD_MAP_LIGHTING_CENSUS_COMPLETE'),
        'semantic':(sem.get('status'),'D1_WORLD_MAP_LIGHT_SEMANTIC_PROBE_COMPLETE'),
        'materials':(mats.get('status'),'D1_WORLD_LIGHT_MATERIAL_MANIFEST_COMPLETE'),
        'tfx':(tfx.get('status'),'D1_TFX_PROGRAM_INVENTORY_COMPLETE'),
    }
    bad={k:v for k,v in required.items() if v[0]!=v[1]}
    if bad:raise SystemExit(f'upstream source closure incomplete: {bad}')
    if vol.get('violations'):
        raise SystemExit(f'volume invariant violations: {vol["violations"][:20]}')

    # Semantic probe is the canonical per-instance join domain.
    sem_rows={(norm(x['collection_hash']),int(x['index'])):x for x in sem.get('light_instances',[])}
    if len(sem_rows)!=737:raise SystemExit(f'expected 737 semantic instances, got {len(sem_rows)}')

    # Volume tool schemas have evolved. Accept the loss-preserving per-instance array
    # under either current spelling and fail if exact collection/index keys are absent.
    vol_list=(vol.get('instances') or vol.get('light_instances') or vol.get('records') or [])
    vol_rows={}
    for x in vol_list:
        c=x.get('collection_hash') or x.get('collection')
        i=x.get('index')
        if c is not None and i is not None:
            vol_rows[(norm(c),int(i))]=x
    if len(vol_rows)!=737:
        raise SystemExit(f'expected 737 volume instances, got {len(vol_rows)}; schema keys={sorted(vol.keys())}')

    buffers={norm(x['hash']):x for x in lighting.get('light_buffers',[])}
    tfxbuf={norm(x['buffer_hash']):x for x in tfx.get('buffers',[])}
    material_rows=mats.get('materials',{})

    # Material usage is already source-proven by LightData+0x80.
    rows=[];viol=[]
    by_flag88=defaultdict(list);by_flag8c=defaultdict(list);by_ps=defaultdict(list)
    by_vs=defaultdict(list);by_prog=defaultdict(list);by_material=defaultdict(list)
    by_combo=defaultdict(list);by_kind=defaultdict(list)
    bit_counts={b:{'set':Counter(),'clear':Counter()} for b in range(32)}
    b2_components={k:{(i,j):[] for i in range(8) for j in range(4)} for k in ('AFFINE_VOLUME','PROJECTIVE_VOLUME')}

    for key,s in sorted(sem_rows.items()):
        v=vol_rows.get(key)
        if v is None:
            viol.append(f'{key}: missing volume row');continue
        kind=v.get('volume_kind') or v.get('kind') or v.get('classification')
        if kind not in ('AFFINE_VOLUME','PROJECTIVE_VOLUME'):
            viol.append(f'{key}: bad volume kind {kind!r}');continue
        bh=norm(s['buffer_data'])
        b=buffers.get(bh);tp=tfxbuf.get(bh)
        if b is None or tp is None:
            viol.append(f'{key}: missing buffer/tfx {bh}');continue
        mr=s.get('candidate_ref80') or {};mh=norm(mr.get('hash','FFFFFFFF'))
        m=material_rows.get(mh)
        if not m or m.get('error'):
            viol.append(f'{key}: missing material {mh}');continue
        ps=norm(m['pixel_shader']);vs=norm(m['vertex_shader']);prog=tp['program_sha256']
        f88=norm(s['flags88_hex']);f8c=norm(s['flags8c_hex'])
        f88i=int(f88,16);f8ci=int(f8c,16)
        b2=b.get('buffer2',[])
        if len(b2)!=8 or any(len(x)!=4 for x in b2):
            viol.append(f'{key}: Buffer2 shape not 8x4');continue
        r={'collection_hash':key[0],'index':key[1],'volume_kind':kind,
           'buffer_data':bh,'program_sha256':prog,'material':mh,
           'pixel_shader':ps,'vertex_shader':vs,'flags88':f88,'flags8c':f8c}
        rows.append(r);by_kind[kind].append(r)
        for table,val in ((by_flag88,f88),(by_flag8c,f8c),(by_ps,ps),(by_vs,vs),(by_prog,prog),(by_material,mh),(by_combo,(ps,f88,f8c))):table[val].append(kind)
        for bit in range(32):
            bit_counts[bit]['set' if (f88i>>bit)&1 else 'clear'][kind]+=1
        for i in range(8):
            for j in range(4):b2_components[kind][(i,j)].append(b2[i][j])

    if len(rows)!=737:viol.append(f'joined instance count {len(rows)} != 737')

    # Program signatures preserve only source-decoded operations/externs/output slots.
    program_signatures={}
    for p in tfx.get('program_groups',[]):
        sha=p['program_sha256']; members=[tfxbuf[norm(h)] for h in p['buffer_hashes']]
        exemplar=members[0]
        extern=Counter();outputs=Counter();ops=Counter()
        for op in exemplar.get('ops',[]):
            ops[op.get('name')]+=1
            if op.get('extern_name'):extern[op['extern_name']]+=1
            if op.get('name') in ('PopOutput','PopOutputMat4') and op.get('operand_bytes'):
                outputs[str(op['operand_bytes'][0])]+=1
        program_signatures[sha]={'buffer_count':len(members),'op_histogram':dict(ops),'extern_histogram':dict(extern),'output_slots':dict(outputs)}

    flag88_purity=purity(by_flag88,'flags88')
    flag8c_purity=purity(by_flag8c,'flags8c')
    ps_purity=purity(by_ps,'pixel_shader')
    vs_purity=purity(by_vs,'vertex_shader')
    prog_purity=purity(by_prog,'program_sha256')
    mat_purity=purity(by_material,'material')

    bits=[]
    for bit,d in bit_counts.items():
        setc=dict(d['set']);clearc=dict(d['clear'])
        bits.append({'bit':bit,'mask_hex':f'{1<<bit:08X}','set_volume_kind_histogram':setc,'clear_volume_kind_histogram':clearc,
                     'set_count':sum(setc.values()),'clear_count':sum(clearc.values())})

    b2_summary={}
    for kind,comp in b2_components.items():
        b2_summary[kind]={f'v{i}.{"xyzw"[j]}':stats(vals) for (i,j),vals in comp.items()}

    out={
        'schema_version':1,
        'status':'D1_TOWER_LIGHT_SEMANTIC_CORRELATION_COMPLETE' if not viol else 'D1_TOWER_LIGHT_SEMANTIC_CORRELATION_PARTIAL',
        'instance_count':len(rows),
        'volume_kind_histogram':dict(Counter(r['volume_kind'] for r in rows)),
        'unique_material_count':len(by_material),'unique_pixel_shader_count':len(by_ps),'unique_vertex_shader_count':len(by_vs),'unique_tfx_program_count':len(by_prog),
        'flags88_value_count':len(by_flag88),'flags8c_value_count':len(by_flag8c),
        'pixel_shader_volume_partition':ps_purity,
        'vertex_shader_volume_partition':vs_purity,
        'tfx_program_volume_partition':prog_purity,
        'material_volume_partition':mat_purity,
        'flags88_volume_partition':flag88_purity,
        'flags8c_volume_partition':flag8c_purity,
        'flags88_bit_partition':bits,
        'buffer2_component_statistics_by_volume_kind':b2_summary,
        'program_signatures':program_signatures,
        'fully_pure_partition_counts':{
            'pixel_shaders':sum(x['single_volume_kind'] for x in ps_purity),
            'vertex_shaders':sum(x['single_volume_kind'] for x in vs_purity),
            'tfx_programs':sum(x['single_volume_kind'] for x in prog_purity),
            'materials':sum(x['single_volume_kind'] for x in mat_purity),
            'flags88_values':sum(x['single_volume_kind'] for x in flag88_purity),
            'flags8c_values':sum(x['single_volume_kind'] for x in flag8c_purity),
        },
        'instances':rows,
        'violations':viol,
        'policy':('This report promotes only exact structural correlations. AFFINE_VOLUME and PROJECTIVE_VOLUME are mathematical volume-geometry classifications, not gameplay light-type names. '
                  'No point/spot/area label, RGB colour, intensity, inner cone, shadow mode, or unknown flag-bit semantic is inferred from correlation or frequency.'),
    }
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ('status','instance_count','volume_kind_histogram','unique_material_count','unique_pixel_shader_count','unique_vertex_shader_count','unique_tfx_program_count','flags88_value_count','flags8c_value_count','fully_pure_partition_counts','violations')},indent=2))
    return 0 if not viol else 2

if __name__=='__main__':raise SystemExit(main())
