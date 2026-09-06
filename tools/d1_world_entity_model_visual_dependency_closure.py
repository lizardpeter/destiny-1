#!/usr/bin/env python3
"""Close cross-package visual dependencies for a source-derived D1 EntityModel set.

Used by table-scoped/common map geometry after ``d1_world_common_model_plan`` has
identified the exact model TagHashes.  For each EntityModel this closure derives:

  EntityModel TagHash
    -> mesh vertex1 / vertex2 / index reference-file FileHashes
    -> inline (variant_shader_index == -1) material FileHashes
    -> each reference-file entry's exact backing FileHash

Every resulting package family is recovered through the archive-wide package index.
No package names or visual heuristics participate in dependency discovery.  External
variant materials are deliberately not invented without an owning EntityResource;
the map-decal exporter already rejects those parts fail-closed.
"""
from __future__ import annotations

import argparse,json,re,subprocess,sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import d1_tower_map_schema_validate_v5 as v5
from d1_entity_model_probe import parse_model
from d1_world_activity_manifest_dependency_plan import filehash_package_id

NULLS={'00000000','FFFFFFFF'}
PKG_RX=re.compile(r'_([0-9A-Fa-f]{4})_[0-9]+\.pkg$',re.I)
ENTITY_MODEL='80801AB5';MATERIAL='80801AD7'


def norm(x):return str(x).upper().removeprefix('0X').zfill(8)
def pid_hash(h):return f'{filehash_package_id(norm(h)):04x}'
def pid_name(name):
    m=PKG_RX.search(Path(name).name);return m.group(1).lower() if m else None

def snaps(root:Path):return sorted(p.resolve() for p in root.glob('*.pkg') if p.is_file())

def recover(index,plist,pkgdir,ids,have,work,n):
    new=sorted({str(x).lower().zfill(4) for x in ids}-have)
    if not new:return []
    rep=work/f'recovery_{n:02d}.json';out=work/f'recovery_{n:02d}.stdout.txt'
    cmd=[sys.executable,str(HERE/'d1_recover_indexed_package_families.py'),'--index',str(index),'--package-list',str(plist),'--out-dir',str(pkgdir),'--report',str(rep)]
    for p in new:cmd+=['--package-id',p]
    cp=subprocess.run(cmd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);out.write_text(cp.stdout)
    if cp.returncode:raise RuntimeError(f'indexed recovery failed rc={cp.returncode}; see {out}')
    have.update(new);return new

def model_hashes(plan:dict)->list[str]:
    xs=[]
    for x in plan.get('models',[]):
        if isinstance(x,str):h=norm(x)
        else:h=norm(x.get('model') or x.get('hash'))
        if h not in NULLS:xs.append(h)
    return sorted(set(xs))

def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument('--index',type=Path,required=True);ap.add_argument('--package-list',type=Path,required=True)
    ap.add_argument('--model-plan',type=Path,required=True);ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--package-dir',type=Path,required=True);ap.add_argument('--work-dir',type=Path,required=True);ap.add_argument('--report',type=Path,required=True);ap.add_argument('--max-passes',type=int,default=8);a=ap.parse_args()
    plan=json.loads(a.model_plan.read_text())
    if plan.get('status')!='D1_WORLD_COMMON_MODEL_PLAN_COMPLETE':raise SystemExit('model plan incomplete')
    models=model_hashes(plan)
    if not models:raise SystemExit('model plan contains no models')
    a.package_dir.mkdir(parents=True,exist_ok=True);a.work_dir.mkdir(parents=True,exist_ok=True)
    have={p for p in (pid_name(x.name) for x in snaps(a.package_dir)) if p};required=set(have)
    for h in models:required.add(pid_hash(h))
    recovery_no=0;first=recover(a.index,a.package_list,a.package_dir,required,have,a.work_dir,recovery_no);recovery_no+=int(bool(first));passes=[];final_rows=[];stop=None
    for n in range(a.max_passes):
        c=v5.v3.base.Corpus(snaps(a.package_dir),a.runtime.resolve());headers=set();materials=set();rows=[];viol=[];before=set(required)
        for h in models:
            meta=c.entry_meta(h);b,src=c.payload(h);row={'model':h,'meta':meta,'source':src,'mesh_count':None,'buffer_headers':[],'inline_materials':[],'violations':[]}
            if meta is None or norm(meta.get('reference',''))!=ENTITY_MODEL or b is None:
                row['violations'].append('entity_model_unavailable_or_class_mismatch');viol.append({'model':h,'reason':row['violations'][-1]});rows.append(row);continue
            try:m=parse_model(b,'PS4')
            except Exception as ex:
                row['violations'].append('parse_model:'+repr(ex));viol.append({'model':h,'reason':row['violations'][-1]});rows.append(row);continue
            row['mesh_count']=len(m['meshes'])
            for mi,mesh in enumerate(m['meshes']):
                for field in ('vertices1','vertices2','indices'):
                    bh=norm(mesh.get(field))
                    if bh in NULLS:continue
                    headers.add(bh);required.add(pid_hash(bh));row['buffer_headers'].append({'mesh':mi,'field':field,'hash':bh,'package_id':pid_hash(bh)})
                for pi,p in enumerate(mesh.get('parts',[])):
                    if int(p.get('variant_shader_index',-1))!=-1:continue
                    mh=norm(p.get('material'))
                    if mh in NULLS:continue
                    materials.add(mh);required.add(pid_hash(mh));row['inline_materials'].append({'mesh':mi,'part':pi,'hash':mh,'package_id':pid_hash(mh),'lod':p.get('lod')})
            rows.append(row)
        new1=recover(a.index,a.package_list,a.package_dir,required,have,a.work_dir,recovery_no);recovery_no+=int(bool(new1))
        if new1:c=v5.v3.base.Corpus(snaps(a.package_dir),a.runtime.resolve())
        backing=[];unresolved=[]
        for hh in sorted(headers):
            meta=c.entry_meta(hh);edge={'header':hh,'header_package_id':pid_hash(hh),'meta':meta,'backing':None,'backing_package_id':None}
            if meta is None:unresolved.append(hh)
            else:
                ref=norm(meta.get('reference',''))
                if ref in NULLS:unresolved.append(hh);edge['error']='null_backing_reference'
                else:edge['backing']=ref;edge['backing_package_id']=pid_hash(ref);required.add(edge['backing_package_id'])
            backing.append(edge)
        new2=recover(a.index,a.package_list,a.package_dir,required,have,a.work_dir,recovery_no);recovery_no+=int(bool(new2))
        if new2:c=v5.v3.base.Corpus(snaps(a.package_dir),a.runtime.resolve())
        missing_backing=[]
        for e in backing:
            h=e.get('backing')
            if not h:continue
            b,src=c.payload(h);e['backing_source']=src;e['backing_bytes']=None if b is None else len(b)
            if b is None:missing_backing.append(h)
        missing_material=[]
        for mh in sorted(materials):
            meta=c.entry_meta(mh);b,src=c.payload(mh)
            if meta is None or norm(meta.get('reference',''))!=MATERIAL or b is None:missing_material.append(mh)
        final_rows=rows
        row={'pass':n,'new_required_package_ids':sorted(required-before),'new_package_ids_headers_materials':new1,'new_package_ids_backings':new2,'model_parse_violations':viol,'buffer_header_count':len(headers),'inline_material_count':len(materials),'unresolved_headers':unresolved,'missing_backing_payloads':sorted(set(missing_backing)),'missing_inline_materials':missing_material,'backing_edges':backing};passes.append(row)
        if not viol and not unresolved and not missing_backing and not missing_material:
            stop='closed_all_entity_model_visual_dependencies';break
        if not (new1 or new2 or required-before):stop='partial_no_dependency_progress';break
    else:stop='max_passes_reached'
    closed=stop=='closed_all_entity_model_visual_dependencies'
    rep={'schema_version':1,'status':'D1_WORLD_ENTITY_MODEL_VISUAL_DEPENDENCY_CLOSURE_COMPLETE' if closed else 'D1_WORLD_ENTITY_MODEL_VISUAL_DEPENDENCY_CLOSURE_PARTIAL','source_model_plan':str(a.model_plan),'model_count':len(models),'models':models,'final_package_ids':sorted(have),'required_package_ids':sorted(required),'stop_reason':stop,'passes':passes,'policy':'Only model/mesh/material/reference-file FileHashes serialized by the source-derived EntityModel set produce package dependencies. External material variants remain unresolved without an owning EntityResource and are not fabricated.'}
    a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(rep,indent=2)+'\n');print(json.dumps({k:rep[k] for k in ('status','model_count','final_package_ids','stop_reason')},indent=2));return 0 if closed else 2
if __name__=='__main__':raise SystemExit(main())
