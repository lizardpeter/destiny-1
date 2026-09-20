#!/usr/bin/env python3
"""Exact structural clustering for D1 Tower original-light pixel shader families.

Joins source-proven light material frequency with exact native GCN image/cbuffer usage
and terminal MRT0 slices. TFX bytecode is disassembled only with the pinned D1 framing
table. The output is deliberately semantic-neutral: clusters describe exact renderer
resource and program structure, not point/spot light types or human-readable buffer
meanings.
"""
from __future__ import annotations
import argparse,collections,hashlib,json,sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
if str(HERE) not in sys.path:sys.path.insert(0,str(HERE))
from d1_tfx_program_inventory import disassemble as disassemble_tfx

TOP_N=8

def norm(x): return str(x).upper().removeprefix('0X').zfill(8)

def freeze(v):
    if isinstance(v,dict): return tuple((k,freeze(v[k])) for k in sorted(v))
    if isinstance(v,list): return tuple(freeze(x) for x in v)
    return v

def main():
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
    i=json.loads(a.image_usage.read_text())
    c=json.loads(a.cbuffer_usage.read_text())
    t=json.loads(a.terminal_mrt0.read_text())
    violations=[]
    if m.get('status')!='D1_WORLD_LIGHT_MATERIAL_MANIFEST_COMPLETE':violations.append('material manifest not exact')
    if s.get('status')!='D1_WORLD_PIXEL_SHADER_GCN_EXACT' or s.get('error_count'):violations.append('shader report not exact')
    if i.get('status')!='D1_GCN_IMAGE_RESOURCE_USAGE_EXACT':violations.append('image usage not exact')
    if c.get('status')!='D1_GCN_CBUFFER_USAGE_EXACT':violations.append('cbuffer usage not exact')
    if t.get('status')!='D1_GCN_TERMINAL_MRT0_DEPENDENCY_CENSUS_EXACT':violations.append('terminal MRT0 report not exact')

    shader_rows={norm(x['shader']):x for x in s.get('shaders',[])}
    image_rows={norm(x['shader']):x for x in i.get('shaders',[])}
    cbuffer_rows={norm(x['shader']):x for x in c.get('shaders',[])}
    terminal_rows={norm(x['shader']):x for x in t.get('shaders',[])}
    freq={norm(k):int(v) for k,v in (m.get('pixel_shader_frequency') or {}).items()}
    materials=m.get('materials') or {}
    shader_materials={norm(k):[norm(x) for x in v] for k,v in (m.get('pixel_shader_materials') or {}).items()}

    top=sorted(freq,key=lambda sh:(-freq[sh],sh))[:TOP_N]
    top_instances=sum(freq[x] for x in top)
    if int(m.get('light_instance_count',-1))!=737:violations.append('light instance count drift')
    if int(m.get('unique_light_material_count',-1))!=497:violations.append('unique material count drift')
    if int(m.get('pixel_shader_count',-1))!=32:violations.append('pixel shader count drift')
    if top_instances!=575:violations.append(f'top8 instance coverage drift {top_instances} != 575')
    terminal_scope=sorted(terminal_rows)\n    missing_top=sorted(set(top)-set(terminal_rows))\n    extra_unknown=sorted(set(terminal_rows)-set(freq))\n    if missing_top:violations.append(f'terminal scope missing top8 shaders {missing_top}')\n    if extra_unknown:violations.append(f'terminal scope contains unknown shaders {extra_unknown}')

    rows=[]
    for sh in sorted(freq,key=lambda x:(-freq[x],x)):
        sr=shader_rows.get(sh);ir=image_rows.get(sh);cr=cbuffer_rows.get(sh);tr=terminal_rows.get(sh)
        if sr is None or ir is None or cr is None:
            violations.append(f'{sh}: exact shader/image/cbuffer row missing');continue
        mats=shader_materials.get(sh,[])
        if len(mats)==0:violations.append(f'{sh}: no material rows')
        instance_check=sum(int(materials[x].get('light_instance_count',0)) for x in mats if x in materials)
        if instance_check!=freq[sh]:violations.append(f'{sh}: material instance sum {instance_check} != {freq[sh]}')

        tfx_programs=collections.defaultdict(lambda:{'materials':[],'instances':0,'disassembly':None})
        sampler_tags=set();vs_hist=collections.Counter();serialized_ps_texture_edges=0
        for mh in mats:
            mr=materials.get(mh)
            if mr is None:
                violations.append(f'{sh}:{mh}: material row missing');continue
            if norm(mr.get('pixel_shader'))!=sh:violations.append(f'{sh}:{mh}: pixel shader mismatch')
            serialized_ps_texture_edges += int(mr.get('ps_texture_count',0))
            vs_hist[norm(mr.get('vertex_shader'))]+=int(mr.get('light_instance_count',0))
            for q in ((mr.get('samplers') or {}).get('ps') or {}).get('items',[]):
                tag=norm(q.get('first_dword_hex','FFFFFFFF'))
                if tag not in {'00000000','FFFFFFFF'}:sampler_tags.add(tag)
            raw=bytes.fromhex((((mr.get('tfx') or {}).get('ps') or {}).get('bytes_hex') or ''))
            sha=hashlib.sha256(raw).hexdigest()
            g=tfx_programs[sha];g['materials'].append(mh);g['instances']+=int(mr.get('light_instance_count',0))
            if g['disassembly'] is None:g['disassembly']=disassemble_tfx(raw,[],[])

        tfx_rows=[]
        for sha,g in sorted(tfx_programs.items(),key=lambda kv:(-kv[1]['instances'],kv[0])):
            d=g['disassembly'];externs=collections.Counter();outs=collections.Counter();ops=[]
            for op in d.get('ops',[]):
                ops.append(op.get('name'))
                if op.get('extern_name') is not None:externs[f"{op['extern_name']}[{op.get('extern_element')}]"]+=1
                if op.get('name') in ('PopOutput','PopOutputMat4') and op.get('operand_bytes'):
                    outs[str(op['operand_bytes'][0])]+=1
            if not d.get('complete'):violations.append(f'{sh}: TFX {sha} incomplete')
            tfx_rows.append({
                'sha256':sha,'material_count':len(g['materials']),'instance_count':g['instances'],
                'materials':sorted(g['materials']),'opcode_sequence':ops,
                'extern_histogram':dict(externs),'output_slot_histogram':dict(outs),
            })

        image_sig=[]
        for ins in ir.get('instructions',[]):
            rr=ins.get('resources') or [];ss=ins.get('samplers') or []
            image_sig.append({
                'address':ins.get('address'),'opcode':ins.get('opcode'),
                'texture_indices':[int(x['texture_index']) for x in rr],
                'sampler_indices':[int(x['sampler_index']) for x in ss],
                'dmask':int(ins.get('dmask',0)),'dmask_channels':ins.get('dmask_channels'),
            })
        api_reads={str(k):list(v) for k,v in sorted((cr.get('api_slot_read_dwords') or {}).items(),key=lambda kv:int(kv[0]))}

        terminal=None
        if tr is not None:
            terminal={
                'compressed':bool(tr.get('terminal_mrt0_compressed')),
                'operands':tr.get('terminal_mrt0_operands'),
                'value_union':tr.get('mrt0_value_union'),
                'address':tr.get('terminal_mrt0_export_address'),
            }

        renderer_resource_key=freeze([
            [(x['opcode'],tuple(x['texture_indices']),tuple(x['sampler_indices']),x['dmask']) for x in image_sig],
            api_reads,
            None if terminal is None else {
                'compressed':terminal['compressed'],
                'texture_sample_channels':terminal['value_union'].get('texture_sample_channels',[]),
                'cbuffer_dwords':terminal['value_union'].get('cbuffer_dwords',{}),
            },
        ])
        rows.append({
            'shader':sh,'instance_count':freq[sh],'material_count':len(mats),
            'native_shader':norm(sr.get('native_shader')),'gcn_sha256':sr.get('gcn_sha256'),'gcn_bytes':int(sr.get('gcn_bytes',0)),
            'serialized_ps_texture_binding_edge_count':serialized_ps_texture_edges,
            'renderer_resource_status':'NO_SERIALIZED_PS_TEXTURE_BINDINGS' if serialized_ps_texture_edges==0 else 'HAS_SERIALIZED_PS_TEXTURE_BINDINGS',
            'image_signature':image_sig,'api_slot_read_dwords':api_reads,
            'sampler_tags':sorted(sampler_tags),'vertex_shader_instance_histogram':dict(sorted(vs_hist.items())),
            'tfx_programs':tfx_rows,'tfx_program_count':len(tfx_rows),
            'terminal_mrt0':terminal,'renderer_resource_cluster_key':repr(renderer_resource_key),
        })

    # Exact equality clusters for structural renderer-resource signatures.
    groups=collections.defaultdict(list)
    for r in rows:groups[r['renderer_resource_cluster_key']].append(r)
    clusters=[]
    for n,(key,members) in enumerate(sorted(groups.items(),key=lambda kv:(-sum(x['instance_count'] for x in kv[1]),kv[1][0]['shader'])),1):
        clusters.append({
            'cluster_id':f'R{n:02d}',
            'shader_count':len(members),
            'instance_count':sum(x['instance_count'] for x in members),
            'shaders':[x['shader'] for x in members],
            'all_no_serialized_ps_texture_bindings':all(x['serialized_ps_texture_binding_edge_count']==0 for x in members),
            'exact_equality_basis':'image opcode/resource/sampler/dmask sequence + exact API cbuffer dword sets + terminal dependency signature when available',
        })
    for r in rows:
        r['renderer_resource_cluster_id']=next(x['cluster_id'] for x in clusters if r['shader'] in x['shaders'])
        r.pop('renderer_resource_cluster_key',None)

    out={
        'schema':'d1_tower_light_shader_family_cluster/v1',
        'status':'D1_TOWER_LIGHT_SHADER_FAMILY_CLUSTER_EXACT' if len(rows)==32 and not violations else 'D1_TOWER_LIGHT_SHADER_FAMILY_CLUSTER_PARTIAL',
        'light_instance_count':int(m.get('light_instance_count',0)),
        'unique_light_material_count':int(m.get('unique_light_material_count',0)),
        'pixel_shader_family_count':len(rows),
        'top8_shaders':top,'top8_instance_count':top_instances,\n        'terminal_dependency_shader_count':len(terminal_scope),\n        'terminal_dependency_shaders':terminal_scope,
        'top8_instance_fraction':top_instances/int(m.get('light_instance_count',1)),
        'renderer_resource_clusters':clusters,'shaders':rows,'violations':violations,
        'semantic_boundary':{
            'material_and_instance_frequency':'EXACT_SOURCE_LIGHT_RECORD_JOIN',
            'native_shader_identity':'EXACT',
            'image_and_cbuffer_usage':'EXACT_NATIVE_GCN_PROVENANCE',
            'tfx_opcode_framing':'PINNED_D1_SCHEMA',
            'terminal_mrt0_dataflow':'EXACT_FOR_DECLARED_TERMINAL_SCOPE',
            'renderer_resource_human_semantics':'WITHHELD',
            'light_type_identity':'WITHHELD',
            'live_runtime_values':'WITHHELD',
        },
        'policy':'Clusters are exact structural equality classes only. Renderer supplied t# inputs are not renamed as albedo/depth/cookie/etc, and no point/spot/area light type is inferred from shader shape.',
    }
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({
        'status':out['status'],'top8':[(x,freq[x]) for x in top],
        'top8_instance_fraction':out['top8_instance_fraction'],
        'clusters':clusters[:20],'violations':violations,
    },indent=2))
    return 0 if out['status']=='D1_TOWER_LIGHT_SHADER_FAMILY_CLUSTER_EXACT' else 2

if __name__=='__main__':raise SystemExit(main())
