#!/usr/bin/env python3
"""Join byte-proven Guardian model parents to decoded texture-plate roles.

The visual-context report establishes model -> exact TexturePlatesROI header.
The remote plate report establishes header -> albedo/normal/gstack plate tags.
This tool combines only those exact keys into the normalized schema consumed by
d1_arrangement_apply_texture_plates.py.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

ROLES=('albedo','normal','gstack')

def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument('--visual-context',type=Path,required=True);ap.add_argument('--plate-report',type=Path,required=True);ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args();v=json.loads(a.visual_context.read_text());p=json.loads(a.plate_report.read_text())
    by_header={x['tag_hash'].upper():x for x in p.get('headers',[]) if not x.get('error')}
    rows=[];seen=set()
    for m in v.get('models',[]):
        model=m['tag_hash'].upper();rp=m.get('render_parent') or {};ents=rp.get('texture_plates_roi_entries',[])
        if len(ents)!=1:raise RuntimeError(f'{model}: expected exactly one TexturePlatesROI header, got {ents}')
        header=ents[0]['texture_plate_header_tag_hash'].upper();h=by_header.get(header)
        if h is None:raise RuntimeError(f'{model}: header {header} absent from plate report')
        plates=h.get('plates',{})
        if set(plates)!=set(ROLES):raise RuntimeError(f'{model}/{header}: incomplete roles {list(plates)}')
        rec={'model_tag':model,'header_tag':header,'plate_tags':{r:plates[r]['tag_hash'].upper() for r in ROLES},
             'entity_resource_hash':m.get('entity_resource_hash'),'body_role':v.get('body_role'),'examples':m.get('examples',[])}
        if model in seen:raise RuntimeError(f'duplicate model {model}')
        seen.add(model);rows.append(rec)
    rep={'schema':'d1_guardian_plate_ownership_join/v1','body_role':v.get('body_role'),'model_count':len(rows),'models':rows,
         'policy':'Each model/header edge comes from the exact selected EntityResource model parent; each role/tag edge comes from the serialized texture-plate header.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(rep,indent=2)+'\n')
    print(json.dumps(rep,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
