#!/usr/bin/env python3
"""Exact structural clustering for D1 Tower sky pixel-shader families.

Joins the source-closed Tower sky material manifest with exact native GCN image
resource provenance, ImmConstBuffer provenance, and terminal MRT0 dependency
slices.  The result groups shader families by exact renderer/resource structure
while retaining material frequency and serialized t#/sampler/TFX variation.

Clusters are structural equality classes only.  They do not assign semantic
labels such as atmosphere, cloud, sun, stars, fog, exposure, or cubemap.
"""
from __future__ import annotations
import argparse,collections,hashlib,json,sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
if str(HERE) not in sys.path:sys.path.insert(0,str(HERE))
from d1_tfx_program_inventory import disassemble as disassemble_tfx

EXPECTED_MATERIALS=74
EXPECTED_TEXTURES=44
EXPECTED_FAMILIES=43

def norm(x): return str(x).upper().removeprefix('0X').zfill(8)

def freeze(v):
    if isinstance(v,dict): return tuple((k,freeze(v[k])) for k in sorted(v))
    if isinstance(v,list): return tuple(freeze(x) for x in v)
    return v

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--material-manifest',type=Path,required=True)
    ap.add_argument('--shader-report',type=Path,required=True)
    ap.add_argument('--image-usage',type=Path,required=True)
    ap.add_argument('--cbuffer-usage',type=Path,required=True)
    ap.add_argument('--terminal-mrt0',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()

    m=json.loads(a.material_manifest.read_text())
    s=json.loads(a.shader_report.read_text())
    iu=json.loads(a.image_usage.read_text())
    cb=json.loads(a.cbuffer_usage.read_text())
    tm=json.loads(a.terminal_mrt0.read_text())
    violations=[]

    if m.get('status')!='D1_WORLD_VISIBLE_MATERIAL_TEXTURE_EXPORT':
        violations.append(f"material manifest status drift {m.get('status')!r}")
    if int(m.get('material_decode_errors',-1))!=0 or int(m.get('texture_errors',-1))!=0:
        violations.append('material/texture decode errors present')
    if int(m.get('visible_material_count',-1))!=EXPECTED_MATERIALS:
        violations.append(f"visible material count {m.get('visible_material_count')} != {EXPECTED_MATERIALS}")
    if int(m.get('unique_texture_tags',-1))!=EXPECTED_TEXTURES:
        violations.append(f"unique texture count {m.get('unique_texture_tags')} != {EXPECTED_TEXTURES}")
    if int(m.get('decoded_texture_tags',-1))!=EXPECTED_TEXTURES:
        violations.append('decoded texture count drift')
    freq={norm(k):int(v) for k,v in (m.get('pixel_shader_frequency') or {}).items()}
    if len(freq)!=EXPECTED_FAMILIES:
        violations.append(f'pixel shader family count {len(freq)} != {EXPECTED_FAMILIES}')
    if sum(freq.values())!=EXPECTED_MATERIALS:
        violations.append(f'pixel shader material frequency sum {sum(freq.values())} != {EXPECTED_MATERIALS}')
    if s.get('status')!='D1_WORLD_PIXEL_SHADER_GCN_EXACT' or s.get('error_count'):
        violations.append('shader report not exact')
    if int(s.get('selected_count',-1))!=EXPECTED_FAMILIES:
        violations.append('shader report selected count drift')
    if iu.get('status')!='D1_GCN_IMAGE_RESOURCE_USAGE_EXACT':
        violations.append('image usage not exact')
    if cb.get('status')!='D1_GCN_CBUFFER_USAGE_EXACT' or cb.get('missing_usage'):
        violations.append('cbuffer usage not exact')
    if tm.get('status')!='D1_GCN_TERMINAL_MRT0_DEPENDENCY_CENSUS_EXACT':
        violations.append('terminal MRT0 census not exact')

    shader_rows={norm(x['shader']):x for x in s.get('shaders',[])}
    image_rows={norm(x['shader']):x for x in iu.get('shaders',[])}
    cbuffer_rows={norm(x['shader']):x for x in cb.get('shaders',[])}
    terminal_rows={norm(x['shader']):x for x in tm.get('shaders',[])}

    mats_by_shader=collections.defaultdict(list)
    for mh,mr in (m.get('materials') or {}).items():
        sh=norm(mr.get('pixel_shader'))
        mats_by_shader[sh].append((norm(mh),mr))
    if set(mats_by_shader)!=set(freq):
        violations.append(f'manifest shader set mismatch materials={sorted(mats_by_shader)} freq={sorted(freq)}')

    rows=[]
    for sh in sorted(freq,key=lambda x:(-freq[x],x)):
        sr=shader_rows.get(sh);ir=image_rows.get(sh);cr=cbuffer_rows.get(sh);tr=terminal_rows.get(sh)
        if None in (sr,ir,cr,tr):
            violations.append(f'{sh}: exact shader/image/cbuffer/terminal row missing')
            continue
        mats=mats_by_shader.get(sh,[])
        if len(mats)!=freq[sh]:
            violations.append(f'{sh}: material rows {len(mats)} != frequency {freq[sh]}')

        binding_patterns=collections.Counter()
        sampler_patterns=collections.Counter()
        tfx_programs=collections.Counter()
        vs_hist=collections.Counter()
        serialized_edges=0
        material_rows=[]
        for mh,mr in mats:
            binds=sorted(
                (int(x['texture_index']),norm(x['texture']))
                for x in (mr.get('bindings') or [])
                if x.get('stage')=='ps'
            )
            serialized_edges+=len(binds)
            binding_patterns[tuple(binds)]+=1
            samplers=tuple(
                norm(x.get('first_dword_hex','FFFFFFFF'))
                for x in (((mr.get('samplers') or {}).get('ps') or {}).get('items') or [])
            )
            sampler_patterns[samplers]+=1
            raw=bytes.fromhex((((mr.get('tfx') or {}).get('ps') or {}).get('bytes_hex') or ''))
            tsha=hashlib.sha256(raw).hexdigest()
            tfx_programs[(tsha,raw.hex())]+=1
            vs_hist[norm(mr.get('vertex_shader'))]+=1
            material_rows.append({
                'material':mh,'vertex_shader':norm(mr.get('vertex_shader')),
                'ps_texture_bindings':[{'texture_index':i,'texture':t} for i,t in binds],
                'ps_sampler_tags':list(samplers),'ps_tfx_sha256':tsha,
            })

        tfx_rows=[]
        for (sha,hexbytes),count in sorted(tfx_programs.items(),key=lambda kv:(-kv[1],kv[0][0])):
            raw=bytes.fromhex(hexbytes);d=disassemble_tfx(raw,[],[])
            if not d.get('complete'):violations.append(f'{sh}: incomplete TFX disassembly {sha}')
            extern=collections.Counter();outs=collections.Counter();ops=[]
            for op in d.get('ops',[]):
                ops.append(op.get('name'))
                if op.get('extern_name') is not None:
                    extern[f"{op['extern_name']}[{op.get('extern_element')}]"]+=1
                if op.get('name') in ('PopOutput','PopOutputMat4') and op.get('operand_bytes'):
                    outs[str(op['operand_bytes'][0])]+=1
            tfx_rows.append({
                'sha256':sha,'material_count':count,'opcode_sequence':ops,
                'extern_histogram':dict(extern),'output_slot_histogram':dict(outs),
            })

        image_sig=[]
        for ins in ir.get('instructions',[]):
            image_sig.append({
                'address':ins.get('address'),'opcode':ins.get('opcode'),
                'texture_indices':[int(x['texture_index']) for x in (ins.get('resources') or [])],
                'sampler_indices':[int(x['sampler_index']) for x in (ins.get('samplers') or [])],
                'dmask':int(ins.get('dmask',0)),'dmask_channels':ins.get('dmask_channels'),
            })
        api_reads={str(k):list(v) for k,v in sorted((cr.get('api_slot_read_dwords') or {}).items(),key=lambda kv:int(kv[0]))}
        terminal={
            'address':tr.get('terminal_mrt0_export_address'),
            'compressed':bool(tr.get('terminal_mrt0_compressed')),
            'operands':tr.get('terminal_mrt0_operands'),
            'value_union':tr.get('mrt0_value_union'),
        }
        serialized_indices=sorted({i for pat in binding_patterns for i,_ in pat})
        used_indices=sorted({int(x) for x in ir.get('used_texture_indices',[])})
        sampled_serialized=sorted(set(serialized_indices)&set(used_indices))
        renderer_or_nonserialized=sorted(set(used_indices)-set(serialized_indices))

        key=freeze({
            'image':[(x['opcode'],x['texture_indices'],x['sampler_indices'],x['dmask']) for x in image_sig],
            'cbuffer':api_reads,
            'terminal':{
                'compressed':terminal['compressed'],
                'operands':terminal['operands'],
                'textures':terminal['value_union'].get('texture_sample_channels',[]),
                'cbuffers':terminal['value_union'].get('cbuffer_dwords',{}),
            },
            'serialized_indices':serialized_indices,
        })
        rows.append({
            'shader':sh,'material_count':freq[sh],
            'native_shader':norm(sr.get('native_shader')),'gcn_sha256':sr.get('gcn_sha256'),
            'gcn_bytes':int(sr.get('gcn_bytes',0)),
            'serialized_ps_texture_binding_edge_count':serialized_edges,
            'serialized_ps_texture_indices':serialized_indices,
            'native_used_texture_indices':used_indices,
            'sampled_serialized_texture_indices':sampled_serialized,
            'renderer_or_nonserialized_texture_indices':renderer_or_nonserialized,
            'binding_patterns':[{
                'bindings':[{'texture_index':i,'texture':t} for i,t in pat],
                'material_count':count,
            } for pat,count in sorted(binding_patterns.items(),key=lambda kv:(-kv[1],kv[0]))],
            'sampler_patterns':[{'sampler_tags':list(pat),'material_count':count} for pat,count in sorted(sampler_patterns.items(),key=lambda kv:(-kv[1],kv[0]))],
            'vertex_shader_material_histogram':dict(sorted(vs_hist.items())),
            'tfx_programs':tfx_rows,
            'image_signature':image_sig,'api_slot_read_dwords':api_reads,
            'terminal_mrt0':terminal,'materials':material_rows,
            '_cluster_key':repr(key),
        })

    groups=collections.defaultdict(list)
    for r in rows:groups[r['_cluster_key']].append(r)
    clusters=[]
    for n,(key,members) in enumerate(sorted(groups.items(),key=lambda kv:(-sum(x['material_count'] for x in kv[1]),kv[1][0]['shader'])),1):
        clusters.append({
            'cluster_id':f'S{n:02d}','shader_family_count':len(members),
            'material_count':sum(x['material_count'] for x in members),
            'shaders':[x['shader'] for x in members],
            'exact_equality_basis':'native image opcode/resource/sampler/dmask sequence + API cbuffer dword sets + MRT0 dependency signature + serialized t# index set',
        })
    bycluster={sh:c['cluster_id'] for c in clusters for sh in c['shaders']}
    for r in rows:
        r['structural_cluster_id']=bycluster[r['shader']]
        r.pop('_cluster_key',None)

    top=sorted(rows,key=lambda x:(-x['material_count'],x['shader']))
    top10=sum(x['material_count'] for x in top[:10])
    out={
        'schema':'d1_tower_sky_shader_family_cluster/v1',
        'status':'D1_TOWER_SKY_SHADER_FAMILY_CLUSTER_EXACT' if len(rows)==EXPECTED_FAMILIES and not violations else 'D1_TOWER_SKY_SHADER_FAMILY_CLUSTER_PARTIAL',
        'visible_material_count':EXPECTED_MATERIALS,'exact_texture_count':EXPECTED_TEXTURES,
        'pixel_shader_family_count':len(rows),'structural_cluster_count':len(clusters),
        'top10_material_count':top10,'top10_material_fraction':top10/EXPECTED_MATERIALS,
        'top10_shaders':[{'shader':x['shader'],'material_count':x['material_count'],'cluster_id':x['structural_cluster_id']} for x in top[:10]],
        'structural_clusters':clusters,'shaders':rows,'violations':violations,
        'semantic_boundary':{
            'material_texture_sampler_tfx_records':'EXACT_SOURCE_MATERIALS',
            'native_shader_identity':'EXACT',
            'image_and_cbuffer_usage':'EXACT_NATIVE_GCN_PROVENANCE',
            'terminal_mrt0_dataflow':'EXACT_NATIVE_GCN',
            'cluster_identity':'EXACT_STRUCTURAL_EQUALITY_ONLY',
            'sky_element_human_semantics':'WITHHELD',
            'active_sky_runtime_selection':'WITHHELD',
            'live_runtime_values':'WITHHELD',
        },
        'policy':'Sky clusters are exact structural equality classes only. No cloud/sun/stars/fog/exposure/cubemap meaning is inferred from resource position, frequency, or shader shape.',
    }
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({
        'status':out['status'],'families':len(rows),'clusters':len(clusters),
        'top10_material_fraction':out['top10_material_fraction'],
        'top10_shaders':out['top10_shaders'],'clusters_preview':clusters[:20],
        'violations':violations,
    },indent=2))
    return 0 if out['status']=='D1_TOWER_SKY_SHADER_FAMILY_CLUSTER_EXACT' else 2

if __name__=='__main__':raise SystemExit(main())
