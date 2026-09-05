#!/usr/bin/env python3
"""Fail-closed validation for instruction-proven D1 shader texture roles.

A semantic role is only legal if the exact native GCN image-usage report proves
that the corresponding shader consumed that t# register. The validator also
checks every visible material using a covered shader actually serializes the
expected register and that all materials in one role family agree on register
presence.

This does not prove the human-readable *meaning* of the role string by itself;
that meaning is established by documented instruction dataflow. It prevents the
role table from silently drifting away from the exact native resource bindings.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from d1_shader_texture_roles import PROVEN_PIXEL_SHADER_ROLES


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--image-usage',type=Path,required=True)
    ap.add_argument('--manifest',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()

    usage=json.loads(a.image_usage.read_text())
    manifest=json.loads(a.manifest.read_text())
    by_usage={r['shader'].upper():r for r in usage.get('shaders',[])}
    by_shader={}
    for mh,m in manifest.get('materials',{}).items():
        ps=m.get('pixel_shader')
        if ps:by_shader.setdefault(ps.upper(),[]).append((mh,m))

    rows=[];errors=[];covered_materials=0;covered_roles=0
    for shader,rolemap in sorted(PROVEN_PIXEL_SHADER_ROLES.items()):
        shader=shader.upper();u=by_usage.get(shader);mats=by_shader.get(shader,[])
        rec={
            'shader':shader,'role_count':len(rolemap),'material_count':len(mats),
            'roles':{str(k):v for k,v in sorted(rolemap.items())},
            'native_usage_available':u is not None,
        }
        if u is not None:
            used=set(int(x) for x in u.get('used_texture_indices',[]))
            rec['native_used_texture_indices']=sorted(used)
            illegal=sorted(set(rolemap)-used)
            rec['role_indices_not_used_by_native_shader']=illegal
            if illegal:
                errors.append({'shader':shader,'error':'role indices absent from native image usage','indices':illegal})
            else:
                covered_roles+=len(rolemap)
        else:
            # Some canonical roles (e.g. the separately solved Vex fixtures) are
            # outside a Tower-only top-40 image-usage report. Preserve that scope
            # distinction rather than treating absence from this report as false.
            rec['native_scope_status']='OUTSIDE_THIS_USAGE_REPORT'

        missing_by_material=[]
        for mh,m in mats:
            psidx={int(b['texture_index']) for b in m.get('bindings',[]) if b.get('stage')=='ps'}
            missing=sorted(set(rolemap)-psidx)
            if missing:missing_by_material.append({'material':mh,'missing_indices':missing,'serialized_indices':sorted(psidx)})
        rec['materials_missing_role_registers']=missing_by_material
        if missing_by_material:
            errors.append({'shader':shader,'error':'visible material missing role register','materials':missing_by_material})
        elif mats:
            covered_materials+=len(mats)
        rows.append(rec)

    out={
        'schema_version':1,
        'status':'D1_SHADER_TEXTURE_ROLE_TABLE_VALID' if not errors else 'D1_SHADER_TEXTURE_ROLE_TABLE_INVALID',
        'usage_status':usage.get('status'),'manifest_status':manifest.get('status'),
        'table_shader_count':len(PROVEN_PIXEL_SHADER_ROLES),
        'validated_native_role_count':covered_roles,
        'visible_materials_covered_by_role_table':covered_materials,
        'error_count':len(errors),'errors':errors,'shaders':rows,
        'policy':'A role-table t# must be consumed by exact native image instructions when that shader is in the supplied usage report, and every covered visible material must serialize that t#.',
    }
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ('status','table_shader_count','validated_native_role_count','visible_materials_covered_by_role_table','error_count')},indent=2))
    return 0 if not errors else 2

if __name__=='__main__':raise SystemExit(main())
