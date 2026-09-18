#!/usr/bin/env python3
"""Fix Blender 5.2 slotted Action assignment for the lightweight Tower NPC test.

Blender 4.4+ Actions are slotted. Assigning AnimationData.action alone does not
necessarily select a compatible ActionSlot, leaving the object non-animated even
though the Action appears assigned in the UI. This adapter pairs each already-
assigned D1_TEST Action with the first compatible slot exposed through
AnimationData.action_suitable_slots, then saves a new .blend.
"""
from __future__ import annotations
import argparse,hashlib,json,sys
from pathlib import Path
import bpy

def cli():
    raw=sys.argv;args=raw[raw.index('--')+1:] if '--' in raw else []
    ap=argparse.ArgumentParser();ap.add_argument('--out-blend',type=Path,required=True);ap.add_argument('--report',type=Path,required=True);return ap.parse_args(args)

def sha256(p:Path):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8<<20),b''):h.update(b)
    return h.hexdigest()

def main():
    a=cli();rows=[];viol=[]
    arms=[o for o in bpy.data.objects if o.type=='ARMATURE' and o.get('d1LaptopTestAsset')]
    if len(arms)!=3:viol.append(f'armature_count:{len(arms)}')
    for arm in arms:
        ad=arm.animation_data
        act=ad.action if ad else None
        if ad is None or act is None:
            viol.append(f'{arm.name}:missing_assigned_action');continue
        slots=list(ad.action_suitable_slots)
        if not slots:
            # Fall back to Action slots only if Blender reports no suitability;
            # still require a single unambiguous slot for this exact test.
            slots=list(act.slots)
        if len(slots)!=1:
            viol.append(f'{arm.name}:compatible_slot_count:{len(slots)}:{[s.identifier for s in slots]}');continue
        slot=slots[0]
        ad.action_slot=slot
        arm['d1TestPreviewActionSlot']=slot.identifier
        arm['d1TestPreviewActionSlotTargetIDType']=str(slot.target_id_type)
        rows.append({'armature':arm.name,'action':act.name,'slot_identifier':slot.identifier,'slot_target_id_type':str(slot.target_id_type),'slot_count':len(slots),'frame_range':[float(act.frame_range[0]),float(act.frame_range[1])]})
    if viol:raise SystemExit('slot assignment failed: '+','.join(viol))
    bpy.context.scene['d1TestPreviewActionSlotsAssigned']=True
    a.out_blend.parent.mkdir(parents=True,exist_ok=True);bpy.ops.wm.save_as_mainfile(filepath=str(a.out_blend.resolve()))
    rep={'schema_version':1,'status':'D1_TOWER_THREE_NPC_ACTION_SLOTS_ASSIGNED','violations':viol,'armature_count':len(arms),'assigned_slot_count':len(rows),'rows':rows,'blend':str(a.out_blend),'blend_bytes':a.out_blend.stat().st_size,'blend_sha256':sha256(a.out_blend),'policy':'Blender inspection handoff only. Existing diagnostic Actions are paired with compatible Blender ActionSlots; retail active animation state remains unclaimed.'}
    a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(rep,indent=2)+'\n');print(json.dumps(rep,indent=2))
if __name__=='__main__':main()
