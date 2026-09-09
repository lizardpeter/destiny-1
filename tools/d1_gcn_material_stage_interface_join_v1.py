#!/usr/bin/env python3
"""Join exact material-owned VS/PS pairs to frozen anonymous GFX7 interfaces.

This is deliberately diagnostic. A retail material proves that its serialized VS and PS
headers belong together, but does not by itself prove that the raster pipeline connects
VS PARAM[n] directly to PS ATTR[n]; tessellation/domain-stage ownership remains a separate
source gate. Therefore this tool classifies exact owner-pair interface shapes while keeping
PARAM->ATTR provenance promotions at zero.
"""
from __future__ import annotations
import argparse, collections, json
from pathlib import Path

OWNER_SCHEMA='d1_gcn_material_shader_owner_frontier/v1'
OWNER_STATUS='D1_GCN_MATERIAL_SHADER_OWNER_FRONTIER_EXACT'
IF_SCHEMA='d1_gcn_stage_interface_frontier/v1'
IF_STATUS='D1_GCN_STAGE_INTERFACE_FRONTIER_EXACT'
SCHEMA='d1_gcn_material_stage_interface_join/v1'
STATUS='D1_GCN_MATERIAL_STAGE_INTERFACE_JOIN_EXACT_DIAGNOSTIC'


def shape(rows,key):
    return {int(x[key]):int(x['channel_mask']) for x in rows}

def compatible(imports,exports):
    return all((exports.get(slot,0)&mask)==mask for slot,mask in imports.items())

def build(owner_path:Path, interface_path:Path)->dict:
    owner=json.loads(owner_path.read_text()); iface=json.loads(interface_path.read_text())
    violations=[]
    if owner.get('schema')!=OWNER_SCHEMA or owner.get('status')!=OWNER_STATUS or owner.get('violations'):
        violations.append(f"owner_not_exact:{owner.get('schema')}:{owner.get('status')}:{len(owner.get('violations') or [])}")
    if iface.get('schema')!=IF_SCHEMA or iface.get('status')!=IF_STATUS or iface.get('violations'):
        violations.append(f"interface_not_exact:{iface.get('schema')}:{iface.get('status')}:{len(iface.get('violations') or [])}")
    pe=(iface.get('program_interfaces') or {}).get('parameter_exports') or {}
    pi=(iface.get('program_interfaces') or {}).get('pixel_imports') or {}
    classes=collections.Counter(); pair_counts=collections.Counter(); material_counts=collections.Counter()
    rows=[]; seen_materials=set()
    for p in owner.get('owner_pairs') or []:
        vs=p['vertex_gcn_sha256']; ps=p['pixel_gcn_sha256']; mats=list(p.get('materials') or [])
        vr=pe.get(vs); pr=pi.get(ps)
        if vr is None:
            violations.append(f'missing_vs_interface:{vs}')
            continue
        if pr is None:
            violations.append(f'missing_ps_interface:{ps}')
            continue
        ex=shape(vr.get('parameter_exports') or [],'parameter')
        im=shape(pr.get('imports') or [],'attribute')
        if not im: cls='PS_NO_INTERPOLANTS'
        elif compatible(im,ex): cls='ANONYMOUS_SHAPE_COMPATIBLE'
        else: cls='SHAPE_MISMATCH_PIPELINE_OWNER_REQUIRED'
        classes[cls]+=1; pair_counts[cls]+=1; material_counts[cls]+=len(mats)
        overlap=[]
        for slot in sorted(set(ex)|set(im)):
            overlap.append({'slot':slot,'vs_export_mask':ex.get(slot,0),'ps_import_mask':im.get(slot,0),
                            'import_covered':(ex.get(slot,0)&im.get(slot,0))==im.get(slot,0)})
        duplicate=seen_materials.intersection(mats)
        if duplicate: violations.append(f'material_in_multiple_owner_pairs:{sorted(duplicate)[:10]}')
        seen_materials.update(mats)
        rows.append({'vertex_shader_header':p['vertex_shader_header'],'pixel_shader_header':p['pixel_shader_header'],
                     'vertex_gcn_sha256':vs,'pixel_gcn_sha256':ps,'material_count':len(mats),
                     'classification':cls,'vs_parameter_exports':vr.get('parameter_exports') or [],
                     'ps_attribute_imports':pr.get('imports') or [],'slot_diagnostic':overlap})
    expected=int((owner.get('coverage') or {}).get('materials_with_resolved_vs_ps_owner_pair',-1))
    if len(seen_materials)!=expected:
        violations.append(f'owner_material_accounting:{len(seen_materials)}!={expected}')
    if sum(material_counts.values())!=expected:
        violations.append(f'class_material_accounting:{sum(material_counts.values())}!={expected}')
    cov={'owner_pair_count':len(rows),'owner_pair_material_count':len(seen_materials),
         'classification_pair_counts':dict(sorted(pair_counts.items())),
         'classification_material_counts':dict(sorted(material_counts.items())),
         'param_index_to_attr_index_promotions':0,'direct_stage_link_promotions':0,
         'varying_semantic_name_promotions':0,'shader_expression_semantic_promotions':0}
    return {'schema':SCHEMA,'status':STATUS if not violations else 'D1_GCN_MATERIAL_STAGE_INTERFACE_JOIN_WITH_VIOLATIONS',
            'coverage':cov,'pairs':rows,'violations':violations,
            'semantic_boundary':{'material_backed_vs_ps_owner_relation':'GLOBAL_EXACT_PREREQUISITE',
              'anonymous_interface_shape_compatibility':'MATERIAL_SCOPED_EXACT_DIAGNOSTIC',
              'param_index_to_attr_index_provenance':'WITHHELD_UNTIL_DIRECT_PIPELINE_STAGE_OWNERSHIP',
              'domain_shader_pipeline_ownership':'REQUIRED_FOR_DIRECTNESS_CLASSIFICATION',
              'varying_semantic_names':'WITHHELD','shader_expression_semantics':'WITHHELD'},
            'policy':('Same-material VS/PS ownership plus compatible anonymous slot masks is diagnostic only. '
                      'No PARAM->ATTR edge is promoted until retail pipeline ownership proves no intervening domain stage.')}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--owner',type=Path,required=True); ap.add_argument('--interface',type=Path,required=True); ap.add_argument('-o','--output',type=Path,required=True); a=ap.parse_args()
    out=build(a.owner,a.interface); a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':out['status'],'coverage':out['coverage'],'violations':out['violations'][:50]},indent=2,sort_keys=True)); return 0 if not out['violations'] else 2
if __name__=='__main__': raise SystemExit(main())
