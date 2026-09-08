#!/usr/bin/env python3
"""Resolve D1 GCN scalar constant-buffer loads to exact OrbShdr API slots.

This pass joins three already-exact layers:
  * structural GCN instructions;
  * SGPR provenance events from native resource analysis;
  * OrbShdr InputUsageSlot declarations from the exact shader extractor.

A buffer load is promoted only when its descriptor SGPR range has an earlier exact
provenance event whose logical extended-user-data register matches exactly one
ImmConstBuffer InputUsageSlot. API slot 0 may additionally be resolved to the
material-local PS vec4 payload supplied by the exact material-stage decoder.

No register adjacency or guessed cbuffer role is used.
"""
from __future__ import annotations
import argparse,json,re
from pathlib import Path

PAIR=re.compile(r'^s\[(\d+):(\d+)\]$')
SINGLE=re.compile(r'^s(\d+)$')
ADDR=re.compile(r'/\*([0-9A-Fa-f]+):')
LOAD_PREFIX='s_buffer_load_dword'


def norm(x):return str(x).upper().removeprefix('0X').zfill(8)

def pair_tuple(s):
    m=PAIR.match(s)
    return None if not m else (int(m.group(1)),int(m.group(2)))

def flatten_material(stage):
    vals=[];raw=[]
    for row in stage['ps_cbuffers']['items']:
        for ci,v in enumerate(row['value']):
            vals.append(float(v));raw.append({'vec4_index':int(row['index']),'component':'xyzw'[ci],'value':float(v),'raw_hex':row['raw_hex'][ci*8:(ci+1)*8]})
    return vals,raw

def shader_row(extract,shader):
    rows=[x for x in extract.get('shaders',[]) if norm(x.get('shader'))==shader]
    if len(rows)!=1:raise ValueError(f'{shader}: expected one shader-extract row, got {len(rows)}')
    return rows[0]

def usage_row(prov,shader):
    rows=[x for x in prov.get('shaders',[]) if norm(x.get('shader'))==shader]
    if len(rows)!=1:raise ValueError(f'{shader}: expected one provenance row, got {len(rows)}')
    return rows[0]

def event_address(e):
    m=ADDR.search(str(e.get('assembly') or ''))
    return None if not m else int(m.group(1),16)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--ir',type=Path,required=True);ap.add_argument('--image-usage',type=Path,required=True);ap.add_argument('--shader-extract',type=Path,required=True);ap.add_argument('--stage',type=Path,required=True);ap.add_argument('-o','--output',type=Path,required=True);a=ap.parse_args()
    ir=json.load(open(a.ir));prov=json.load(open(a.image_usage));ex=json.load(open(a.shader_extract));sd=json.load(open(a.stage));viol=[];rows=[]
    try:
        assert ir['status']=='D1_GCN_STRUCTURAL_IR_COMPLETE'
        shader=norm(ir['shader']);pr=usage_row(prov,shader);sr=shader_row(ex,shader)
        assert int(pr.get('unmatched_image_instruction_count',0))==0
        slots=[x for x in sr['usage']['slots'] if x.get('usage_name')=='ImmConstBuffer']
        by_start={int(x['start_register']):x for x in slots}
        assert len(by_start)==len(slots)
        assert sd['status']=='D1_CORPUS_MATERIAL_STAGE_EXACT' and len(sd['materials'])==1
        mat=sd['materials'][0];st=mat['stage'];assert norm(st['pixel_shader'])==shader
        mvals,mraw=flatten_material(st)
        events=[]
        for e in pr.get('provenance_events',[]):
            if e.get('resolved_kind')!='extended_user_data':continue
            addr=event_address(e)
            dst=e.get('destination') or []
            if addr is None or not dst:continue
            events.append({'address':addr,'start':int(dst[0]),'end':int(dst[-1]),'logical_start':int(e['logical_start']),'event':e})
        for x in ir['instructions']:
            if not x['opcode'].startswith(LOAD_PREFIX) or len(x['operands'])<3:continue
            desc=pair_tuple(x['operands'][1])
            if desc is None:continue
            candidates=[e for e in events if (e['start'],e['end'])==desc and e['address']<int(x['address'],16)]
            if not candidates:continue
            pe=max(candidates,key=lambda e:e['address']);slot=by_start.get(pe['logical_start'])
            if slot is None:continue
            off=int(x['operands'][2],0);count=1
            suf=x['opcode'][len(LOAD_PREFIX):]
            if suf.startswith('x'):count=int(suf[1:])
            dest=x['operands'][0];dm=SINGLE.match(dest);dp=pair_tuple(dest)
            if dm:dregs=[int(dm.group(1))+i for i in range(count)]
            elif dp:dregs=list(range(dp[0],dp[1]+1))
            else:dregs=[]
            if len(dregs)!=count:raise ValueError(f'{x["index"]}: destination width {dregs} != {count}')
            rr={'instruction':x['index'],'address':x['address_hex'],'opcode':x['opcode'],'destination_sgprs':[f's{i}' for i in dregs],
                'descriptor_sgpr_range':x['operands'][1],'descriptor_provenance_instruction_address':f'{pe["address"]:012X}',
                'extended_user_data_logical_start':pe['logical_start'],'orbshdr_usage_slot_index':int(slot['index']),'api_slot':int(slot['api_slot']),
                'orbshdr_start_register':int(slot['start_register']),'offset_dwords':off,'scalar_count':count,'material_values':None}
            if int(slot['api_slot'])==0:
                if off+count>len(mvals):raise ValueError(f'{x["index"]}: material b0 scalar load out of range {off}+{count}>{len(mvals)}')
                rr['material_values']=[mraw[i] for i in range(off,off+count)]
                rr['resolution']='EXACT_MATERIAL_PS_B0'
            else:rr['resolution']='EXACT_NONLOCAL_API_CBUFFER_SLOT'
            rows.append(rr)
        assert rows,'no exact cbuffer load provenance rows'
    except Exception as e:viol.append(repr(e))
    matloads=[r for r in rows if r.get('resolution')=='EXACT_MATERIAL_PS_B0']
    out={'schema_version':1,'status':'D1_GCN_CBUFFER_PROVENANCE_EXACT' if rows and not viol else 'D1_GCN_CBUFFER_PROVENANCE_PARTIAL','shader':ir.get('shader'),'material':sd.get('materials',[{}])[0].get('material') if sd.get('materials') else None,'load_count':len(rows),'material_b0_load_count':len(matloads),'loads':rows,'violations':viol,
         'policy':'A cbuffer load is resolved only through exact SGPR descriptor provenance joined to an exact OrbShdr ImmConstBuffer start register. API slot 0 values are then indexed into the exact material PS vec4 payload. No SGPR adjacency or visual role inference is permitted.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));return 0 if not viol else 2
if __name__=='__main__':raise SystemExit(main())
