#!/usr/bin/env python3
"""Fresh-source exhaustive Tower baked-static production driver.

Input package metadata must be generated in the caller's current run from current
retail packages.txt/split-TAR. No old Tower GLB, table list, package recovery report,
texture export, or Actions/release artifact is accepted.

Two outputs are built from the same source closure:
  * retail-visible: exact D1 GetStatics() selection for normal inspection;
  * all-serialized: every serialized placement/detail/material variant for forensics.
Both material populations receive independent exact texture dependency closure.
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent


def load(p:Path)->dict:return json.loads(p.read_text(encoding='utf-8'))
def sha256(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()

def run(args:list[str],log:Path|None=None)->None:
    cmd=[sys.executable,*args];print('RUN',' '.join(cmd),flush=True)
    if log is None:cp=subprocess.run(cmd,check=False)
    else:
        log.parent.mkdir(parents=True,exist_ok=True)
        with log.open('w',encoding='utf-8') as f:cp=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,text=True,check=False)
    if cp.returncode:
        tail=''
        if log and log.exists():tail='\n'.join(log.read_text(errors='replace').splitlines()[-50:])
        raise RuntimeError(f'command failed rc={cp.returncode}: {" ".join(cmd)}'+(f'\n{tail}' if tail else ''))

def tool(n:str)->str:return str(HERE/n)

def snapshot_args(package_dir:Path,extra:Path|None=None)->list[str]:
    ps={p.name:p for p in package_dir.glob('*.pkg') if p.is_file()}
    if extra and extra.exists():
        for p in extra.glob('*.pkg'):
            if p.is_file():ps[p.name]=p
    out=[]
    for p in sorted(ps.values()):out += ['--snapshot',str(p)]
    if not out:raise ValueError('no recovered package snapshots')
    return out

def merge(glbs:list[Path],out:Path,report:Path)->None:
    if not glbs:raise ValueError('no GLBs to merge')
    args=[tool('d1_gltf_layer_merge.py'),'--base',str(glbs[0])]
    for i,p in enumerate(glbs[1:],1):args += ['--layer',f'cell_{i:03d}={p}']
    args += ['--out',str(out),'--report',str(report)]
    run(args,report.with_suffix('.stdout.txt'))
    d=load(report)
    if d.get('status')!='D1_GLTF_LAYER_MERGE_EXACT_BASE_PRESERVATION':raise ValueError(d)

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--activity-index',type=Path,required=True)
    ap.add_argument('--package-list',type=Path,required=True)
    ap.add_argument('--fresh-source-manifest',type=Path,required=True)
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--out-dir',type=Path,required=True)
    a=ap.parse_args();out=a.out_dir;out.mkdir(parents=True,exist_ok=True)
    for d in ('logs','reports','packages','work','retail_cells','all_cells','merged','visible_textures','all_textures','visible_texture_expansion','all_texture_expansion','visible_texture_work','all_texture_work'): (out/d).mkdir(exist_ok=True)

    source=load(a.fresh_source_manifest)
    if source.get('status')!='D1_FRESH_SOURCE_INDEX_COMPLETE':raise ValueError('fresh source manifest incomplete')
    if source.get('github_sha')!=os.environ.get('GITHUB_SHA'):raise ValueError('checkout/source manifest mismatch')
    if sha256(a.activity_index)!=source.get('activity_index_sha256'):raise ValueError('activity index SHA mismatch')
    if sha256(a.package_list)!=source.get('packages_txt_sha256'):raise ValueError('package list SHA mismatch')

    packages=out/'packages';work=out/'work';reports=out/'reports'
    run([tool('d1_world_activity_root_dependency_closure.py'),'--index',str(a.activity_index),'--package-list',str(a.package_list),'--activity','80C98019','--runtime',str(a.runtime),'--package-dir',str(packages),'--work-dir',str(work/'root'),'--root-out',str(reports/'activity_map_roots.json'),'--report',str(reports/'activity_root_dependency_closure.json')],out/'logs'/'root_closure.txt')
    snaps=snapshot_args(packages)
    run([tool('d1_world_map_data_layer_census.py'),*snaps,'--runtime',str(a.runtime),'--map-root-json',str(reports/'activity_map_roots.json'),'--out',str(reports/'map_data_layer_census.json')],out/'logs'/'map_data_layer.txt')
    run([tool('d1_world_map_resource_subset_plan.py'),'--census',str(reports/'map_data_layer_census.json'),'--resource-class','80801AEA','--out',str(reports/'static_map_roots.json')],out/'logs'/'static_subset.txt')
    snaps=snapshot_args(packages)
    run([tool('d1_world_static_map_resource_chain_census.py'),*snaps,'--runtime',str(a.runtime),'--map-root-json',str(reports/'static_map_roots.json'),'--out',str(reports/'static_map_resource_chain_census.json')],out/'logs'/'static_chain.txt')
    run([tool('d1_world_static_visual_dependency_closure.py'),'--index',str(a.activity_index),'--package-list',str(a.package_list),'--chain-json',str(reports/'static_map_resource_chain_census.json'),'--runtime',str(a.runtime),'--package-dir',str(packages),'--work-dir',str(work/'baked'),'--validation-out',str(reports/'baked_validation.json'),'--report',str(reports/'baked_dependency_closure.json')],out/'logs'/'baked_dependency.txt')
    for p,status in ((reports/'activity_root_dependency_closure.json','D1_WORLD_ACTIVITY_ROOT_DEPENDENCY_CLOSURE_COMPLETE'),(reports/'static_map_resource_chain_census.json','D1_WORLD_STATIC_MAP_RESOURCE_CHAIN_CLOSED'),(reports/'baked_dependency_closure.json','D1_WORLD_STATIC_VISUAL_DEPENDENCY_CLOSURE_COMPLETE')):
        d=load(p)
        if d.get('status')!=status:raise ValueError(f'{p.name}: {d.get("status")}')
    bc=load(reports/'baked_dependency_closure.json')
    if bc.get('validation_failures'):raise ValueError(bc['validation_failures'])
    cells=sorted({x['static_map_data'] for x in bc.get('baked_cells',[])})
    if not cells:raise ValueError('no fresh Tower baked cells')
    (reports/'baked_cells.json').write_text(json.dumps({'cells':cells},indent=2)+'\n')

    snaps=snapshot_args(packages)
    retail_reports=[];all_reports=[];all_selectors=[]
    for h in cells:
        rg=out/'retail_cells'/f'{h}.glb';rj=out/'retail_cells'/f'{h}.json'
        run([tool('d1_world_static_visual_export.py'),*snaps,'--runtime',str(a.runtime),'--validation-json',str(reports/'baked_validation.json'),'--static-map-data',h,'--out',str(rg),'--json',str(rj),'--basis','gltf-y-up'],out/'logs'/f'retail_{h}.txt');retail_reports.append(rj)
        ag=out/'all_cells'/f'{h}_ALL_SERIALIZED.glb';aj=out/'all_cells'/f'{h}_ALL_SERIALIZED.json';sel=out/'all_cells'/f'{h}_ALL_MATERIAL_SELECTOR.json'
        run([tool('d1_world_static_all_serialized_export.py'),*snaps,'--runtime',str(a.runtime),'--validation-json',str(reports/'baked_validation.json'),'--static-map-data',h,'--out',str(ag),'--json',str(aj),'--material-selector',str(sel),'--basis','gltf-y-up'],out/'logs'/f'all_{h}.txt');all_reports.append(aj);all_selectors.append(sel)

    rr=[load(p) for p in retail_reports];ar=[load(p) for p in all_reports]
    if any(x.get('decode_error_count') for x in rr+ar):raise ValueError('static decode error in fresh cell set')
    if any(int(x['serialized_placements'])!=int(x['exported_placements']) for x in ar):raise ValueError('all-serialized placement coverage mismatch')
    retail_mats={}
    for x in rr:
        for h,m in x.get('materials',{}).items():
            if m.get('visual'):retail_mats[h.upper()]={'visual':True}
    visible_selector=reports/'visible_material_selector.json';visible_selector.write_text(json.dumps({'status':'D1_FRESH_TOWER_VISIBLE_MATERIAL_SELECTOR','activity':'80C98019','materials':dict(sorted(retail_mats.items()))},indent=2)+'\n')

    merge([out/'retail_cells'/f'{h}.glb' for h in cells],out/'merged'/'TOWER_RETAIL_VISIBLE_UNTEXTURED.glb',reports/'retail_merge.json')
    merge([out/'all_cells'/f'{h}_ALL_SERIALIZED.glb' for h in cells],out/'merged'/'TOWER_ALL_SERIALIZED_UNTEXTURED.glb',reports/'all_merge.json')

    # Close exact texture dependencies for the normal visible selection.
    run([tool('d1_close_world_texture_dependencies_indexed.py'),'--snapshot-dir',str(packages),'--runtime',str(a.runtime),'--visual-json',str(visible_selector),'--index',str(a.activity_index),'--package-list',str(a.package_list),'--expansion-dir',str(out/'visible_texture_expansion'),'--work-dir',str(out/'visible_texture_work'),'--out',str(out/'visible_textures'),'--report',str(reports/'visible_texture_closure.json')],out/'logs'/'visible_texture_closure.txt')
    # And independently for every serialized static material. Each selector records
    # retail_visual separately; the compatibility visual bit is only transport.
    args=[tool('d1_close_world_texture_dependencies_indexed.py'),'--snapshot-dir',str(packages),'--runtime',str(a.runtime)]
    for p in all_selectors:args += ['--visual-json',str(p)]
    args += ['--index',str(a.activity_index),'--package-list',str(a.package_list),'--expansion-dir',str(out/'all_texture_expansion'),'--work-dir',str(out/'all_texture_work'),'--out',str(out/'all_textures'),'--report',str(reports/'all_texture_closure.json')]
    run(args,out/'logs'/'all_texture_closure.txt')
    for p in (reports/'visible_texture_closure.json',reports/'all_texture_closure.json'):
        d=load(p)
        if d.get('status')!='D1_INDEXED_WORLD_TEXTURE_DEPENDENCY_CLOSURE_COMPLETE':raise ValueError(d)

    run([tool('d1_world_texture_role_inventory.py'),str(out/'visible_textures'/'material_texture_manifest.json'),'-o',str(reports/'visible_texture_roles.json')],out/'logs'/'visible_roles.txt')
    run([tool('d1_gltf_bind_exact_shader_textures.py'),'--input-glb',str(out/'merged'/'TOWER_RETAIL_VISIBLE_UNTEXTURED.glb'),'--manifest',str(out/'visible_textures'/'material_texture_manifest.json'),'--roles',str(reports/'visible_texture_roles.json'),'--texture-dir',str(out/'visible_textures'/'textures'),'--include-medium-base','--bind-normal-candidates','--out',str(out/'merged'/'TOWER_RETAIL_VISIBLE_EXACT_TEXTURES.glb'),'--report',str(reports/'visible_texture_binding.json')],out/'logs'/'visible_bind.txt')
    run([tool('d1_world_texture_role_inventory.py'),str(out/'all_textures'/'material_texture_manifest.json'),'-o',str(reports/'all_texture_roles.json')],out/'logs'/'all_roles.txt')
    run([tool('d1_gltf_bind_exact_shader_textures.py'),'--input-glb',str(out/'merged'/'TOWER_ALL_SERIALIZED_UNTEXTURED.glb'),'--manifest',str(out/'all_textures'/'material_texture_manifest.json'),'--roles',str(reports/'all_texture_roles.json'),'--texture-dir',str(out/'all_textures'/'textures'),'--include-medium-base','--bind-normal-candidates','--out',str(out/'merged'/'TOWER_ALL_SERIALIZED_EXACT_TEXTURES.glb'),'--report',str(reports/'all_texture_binding.json')],out/'logs'/'all_bind.txt')

    rv=load(out/'visible_textures'/'material_texture_manifest.json');av=load(out/'all_textures'/'material_texture_manifest.json')
    if rv.get('texture_errors') or rv.get('material_decode_errors') or av.get('texture_errors') or av.get('material_decode_errors'):raise ValueError('texture decode/material errors remain')
    rglb=out/'merged'/'TOWER_RETAIL_VISIBLE_EXACT_TEXTURES.glb';aglb=out/'merged'/'TOWER_ALL_SERIALIZED_EXACT_TEXTURES.glb'
    manifest={
      'schema':'d1_fresh_tower_static_target/v1','status':'D1_FRESH_TOWER_STATIC_TARGET_COMPLETE','source':source,
      'baked_cell_count':len(cells),
      'serialized_placement_count':sum(int(x['serialized_placements']) for x in ar),
      'retail_visible_placement_count':sum(int(x['retail_visible_placements']) for x in rr),
      'all_serialized_exported_placement_count':sum(int(x['exported_placements']) for x in ar),
      'retail_geometry_variant_count':sum(int(x['geometry_variants']) for x in rr),
      'all_serialized_geometry_variant_count':sum(int(x['geometry_variants']) for x in ar),
      'retail_visible_material_count':rv.get('visible_material_count'),
      'all_serialized_material_count':av.get('visible_material_count'),
      'retail_exact_texture_count':rv.get('unique_texture_tags'),
      'all_serialized_exact_texture_count':av.get('unique_texture_tags'),
      'retail_glb':str(rglb),'retail_glb_bytes':rglb.stat().st_size,'retail_glb_sha256':sha256(rglb),
      'all_serialized_glb':str(aglb),'all_serialized_glb_bytes':aglb.stat().st_size,'all_serialized_glb_sha256':sha256(aglb),
      'policy':'Both visual and forensic Tower static outputs are regenerated from current retail source in this run. Retail-visible applies D1 GetStatics selection. All-serialized retains every serialized placement/detail/material variant and independently closes every serialized material texture dependency. No prior Tower extract is an input.'
    }
    (out/'PRODUCTION_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest,indent=2));return 0

if __name__=='__main__':raise SystemExit(main())
