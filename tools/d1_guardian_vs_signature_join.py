#!/usr/bin/env python3
"""Join exact Spektar mesh stream families to D1 PS4 native VS input signatures.

Input is a d1_guardian_material_vs_census report.  Vertex-shader hashes are not
rediscovered or inferred: they come from exact stage-part material +0x28 links in
that report.  This tool resolves each 32:9 shader through verified package member
catalogs, decodes the embedded Gnmx input semantic table, and compares component
widths against meshes using that shader.

The main purpose is a positive/negative control for the D1 dye-detail half2 lane:
detail-lane and no-detail shader families are both decoded from retail bytes.
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))

from d1_entity_model_export import byhash
from d1_investment_arrangement_probe import filehash_pkg_index
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_ps4_vertex_shader_header import parse_header, VERTEX_SHADER_TYPE, VERTEX_SHADER_SUBTYPE
from d1_remote_investment_parent_probe import RemoteLogicalPackage
from d1_remote_model_export import MultiPackageReader
from d1_split_tar_extract import SplitHttpTar


def pkg_id(tag:str)->int:
    return filehash_pkg_index(int(tag,16))[0]


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--report',type=Path,required=True)
    ap.add_argument('--member-catalog',type=Path,action='append',required=True)
    ap.add_argument('--base-url',required=True)
    ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()

    src=json.loads(a.report.read_text())
    if src.get('schema')!='d1_guardian_material_vs_census/v1':
        raise ValueError('unexpected report schema')
    vs_rows=src['vertex_shaders']
    wanted=[v['vertex_shader_hash'].upper() for v in vs_rows]

    catalogs=load_catalogs(a.member_catalog)
    missing=sorted({pkg_id(x) for x in wanted}-set(catalogs))
    if missing:
        raise SystemExit('missing vertex-shader package catalogs: '+', '.join(f'{x:04X}' for x in missing))

    base=a.base_url.rstrip('/')
    arc=SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1,a.part_count+1)],retries=6,timeout=90)
    views={pkg:RemoteLogicalPackage(arc,fam,a.runtime) for pkg,fam in sorted(catalogs.items())}
    multi=MultiPackageReader(views); hmap=byhash(multi)

    # Material -> exact mesh users from the source census.
    mat_users={m['material_hash']:m['users'] for m in src['materials']}
    out=[]
    for old in vs_rows:
        tag=old['vertex_shader_hash'].upper(); e=hmap.get(tag)
        row={
            'vertex_shader_hash':tag,
            'texcoord2_candidate_usage_values':old['texcoord2_candidate_usage_values'],
            'material_hashes':old['material_hashes'],
            'required_package_id':f'{pkg_id(tag):04X}',
        }
        users=[]
        for mh in old['material_hashes']:
            users.extend(mat_users.get(mh,[]))
        # dedupe exact user tuples
        unique=[]; seen=set()
        for u in users:
            k=(u['model_tag'],u['mesh_index'],u['stride0'],u['stride1'],bool(u['texcoord2_half2_candidate']))
            if k not in seen:
                seen.add(k); unique.append(u)
        row['mesh_users']=unique
        row['stride_pairs']=sorted({f"{u['stride0']:#x}/{u['stride1']:#x}" for u in unique})

        if e is None:
            row['resolved']=False; row['error']='32:9 FileHash absent'; out.append(row); continue
        row['entry']={k:e[k] for k in ('index','type','subtype','reference','file_size')}
        if (e['type'],e['subtype'])!=(VERTEX_SHADER_TYPE,VERTEX_SHADER_SUBTYPE):
            row['resolved']=False; row['error']=f"unexpected resource class {e['type']}:{e['subtype']}";out.append(row);continue
        hb=multi.entry(e['index']); ne=hmap.get(e['reference'].upper())
        nb=multi.entry(ne['index']) if ne is not None else None
        dec=parse_header(hb,nb)
        row['resolved']=True
        row['input_semantic_count']=dec['gnmx']['num_input_semantics']
        row['input_component_widths']=[x['size_in_elements'] for x in dec['gnmx']['input_semantics']]
        row['input_semantic_ids']=[x['semantic'] for x in dec['gnmx']['input_semantics']]
        row['input_vgprs']=[x['vgpr'] for x in dec['gnmx']['input_semantics']]
        row['output_semantic_count']=dec['gnmx']['num_export_semantics']
        row['header_size']=dec['header_size']
        row['shader_size']=dec['gnmx']['shader_size']
        row['checks']=dec['checks']
        row['native_checks']=dec.get('native_checks')
        out.append(row)

    detail=[r for r in out if r['texcoord2_candidate_usage_values']==[True]]
    nodetail=[r for r in out if r['texcoord2_candidate_usage_values']==[False]]
    mixed=[r for r in out if len(r['texcoord2_candidate_usage_values'])!=1]
    by_stride=collections.defaultdict(lambda:{'detail':[],'no_detail':[]})
    for r in out:
        bucket='detail' if r['texcoord2_candidate_usage_values']==[True] else 'no_detail' if r['texcoord2_candidate_usage_values']==[False] else None
        if bucket:
            for s in r['stride_pairs']:
                by_stride[s][bucket].append({
                    'vertex_shader_hash':r['vertex_shader_hash'],
                    'widths':r.get('input_component_widths'),
                    'semantic_ids':r.get('input_semantic_ids'),
                })

    # A strict negative-control comparison: for any stride family represented by
    # both states, a detail signature must equal a no-detail signature plus one
    # final 2-component input.  Multiple shader variants may exist, so compare all
    # unique width sequences as sets.
    controls={}
    all_controls_pass=True
    for stride,buckets in sorted(by_stride.items()):
        dw={tuple(x['widths']) for x in buckets['detail'] if x['widths'] is not None}
        nw={tuple(x['widths']) for x in buckets['no_detail'] if x['widths'] is not None}
        comparable=bool(dw and nw)
        passes=None
        if comparable:
            passes=all(any(d==n+(2,) for n in nw) for d in dw) and all(any(d==n+(2,) for d in dw) for n in nw)
            all_controls_pass &= passes
        controls[stride]={
            'detail_width_sequences':[list(x) for x in sorted(dw)],
            'no_detail_width_sequences':[list(x) for x in sorted(nw)],
            'comparable':comparable,
            'detail_equals_no_detail_plus_final_vec2':passes,
        }

    rep={
        'schema':'d1_guardian_vs_signature_join/v1',
        'vertex_shader_count':len(out),
        'resolved_vertex_shader_count':sum(bool(x.get('resolved')) for x in out),
        'detail_shader_count':len(detail),
        'no_detail_shader_count':len(nodetail),
        'mixed_usage_shader_count':len(mixed),
        'stride_controls':controls,
        'all_comparable_stride_controls_pass':all_controls_pass,
        'vertex_shaders':out,
        'interpretation_policy':(
            'The Gnm semantic byte is kept as a native link ID. A final vec2 is identified structurally; naming it D1 dye-detail texcoord multiplier additionally relies on the independent Bungie renderer contract and the retail half2 lane census.'
        ),
    }
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(rep,indent=2)+'\n')
    print('VS',rep['resolved_vertex_shader_count'],'/',rep['vertex_shader_count'],'detail',len(detail),'no_detail',len(nodetail),'mixed',len(mixed))
    for r in out:
        print(r['vertex_shader_hash'],r['texcoord2_candidate_usage_values'],r['stride_pairs'],r.get('input_component_widths'),r.get('input_semantic_ids'))
    print('CONTROLS',json.dumps(controls,sort_keys=True))
    print('ALL_COMPARABLE_CONTROLS_PASS',all_controls_pass)
    return 0


if __name__=='__main__':
    raise SystemExit(main())
