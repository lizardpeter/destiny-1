#!/usr/bin/env python3
"""Prove the source-closed D1 terrain API12 camera window from exact GFX700 disassembly.

The proof requires, for every terrain PS that declares ImmConstBuffer API12:
  1. its descriptor is recovered through PtrExtendedUserData at
     (logical_start_sgpr - 16) dwords;
  2. the descriptor feeds exactly one s_buffer_load_dwordx4 at offset 0x1C;
  3. the first three loaded scalar words are read first by v_sub_f32;
  4. the fourth loaded word is overwritten before any read.

The semantic promotion to camera XYZ relies on the independently source-closed
RoI terrain API12 proof for the same D1 buffer window/dataflow contract. This
tool does not assign meanings to any other API12 word.
"""
from __future__ import annotations
import argparse,json,re
from collections import Counter
from pathlib import Path

LINE_RE=re.compile(r'/\*([0-9a-fA-F]+):.*?\*/\s*([A-Za-z0-9_]+)\s*(.*)$')
SINGLE_RE=re.compile(r'(?<![A-Za-z0-9_])s(\d+)(?![A-Za-z0-9_])')
RANGE_RE=re.compile(r's\[(\d+):(\d+)\]')

def sregs(text:str)->set[int]:
    out={int(x) for x in SINGLE_RE.findall(text)}
    for a,b in RANGE_RE.findall(text):
        out.update(range(int(a),int(b)+1))
    return out

def dest_sregs(op:str,rest:str)->set[int]:
    if not op.startswith('s_'):
        return set()
    return sregs(rest.split(',',1)[0].strip())

def instructions(path:Path):
    out=[]
    for raw in path.read_text(encoding='utf-8').splitlines():
        m=LINE_RE.search(raw)
        if m:
            out.append({
                'pc':int(m.group(1),16),
                'pc_hex':'0x'+m.group(1).upper(),
                'op':m.group(2),
                'rest':m.group(3),
                'text':m.group(2)+' '+m.group(3),
            })
    return out

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--resources',type=Path,required=True)
    ap.add_argument('--dataflow',type=Path,required=True)
    ap.add_argument('--disasm-dir',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()

    resources=json.loads(a.resources.read_text(encoding='utf-8'))
    flow=json.loads(a.dataflow.read_text(encoding='utf-8'))
    rows_by={x['pixel_shader']:x for x in resources['pixel_shaders']}
    api12=sorted(flow['api12_shaders'])
    proofs=[]
    violations=[]
    start_hist=Counter()

    for h in api12:
        row=rows_by[h]
        slots=[
            x for x in row['usage']['slots']
            if x['usage_name']=='ImmConstBuffer' and int(x['api_slot'])==12
        ]
        if len(slots)!=1:
            violations.append({'shader':h,'error':f'API12 usage count {len(slots)}'})
            continue
        start=int(slots[0]['start_register'])
        spill=start-16
        start_hist[start]+=1
        ins=instructions(a.disasm_dir/f'PS_{h}.s')

        descriptors=[]
        for i,x in enumerate(ins):
            if x['op']!='s_load_dwordx4' or 's[2:3]' not in x['rest']:
                continue
            if not re.search(rf'0x{spill:x}\b',x['rest'],re.I):
                continue
            regs=sorted(sregs(x['rest'].split(',',1)[0]))
            if len(regs)==4:
                descriptors.append((i,regs,x))
        matches=[]
        for i,regs,desc in descriptors:
            for j in range(i+1,min(len(ins),i+96)):
                x=ins[j]
                if x['op']!='s_buffer_load_dwordx4' or not re.search(r'0x1c\b',x['rest'],re.I):
                    continue
                parts=[p.strip() for p in x['rest'].split(',')]
                if len(parts)<3:
                    continue
                if sregs(parts[1])!=set(regs):
                    continue
                dst=sorted(sregs(parts[0]))
                if len(dst)==4:
                    matches.append((j,regs,dst,desc,x))
                    break
        if len(matches)!=1:
            violations.append({
                'shader':h,'error':f'API12 dword28..31 load match count {len(matches)}',
                'logical_start_register':start,'spill_dword':spill,
            })
            continue

        j,descriptor,dst,desc,load=matches[0]
        words=[]
        for lane,reg in enumerate(dst):
            first_use=None
            overwrite=None
            for x in ins[j+1:]:
                defs=dest_sregs(x['op'],x['rest'])
                allregs=sregs(x['rest'])
                if reg in defs:
                    overwrite=x
                    break
                if reg in allregs:
                    first_use=x
                    break
            word={
                'api12_dword':28+lane,
                'loaded_sgpr':reg,
                'first_use':None if first_use is None else {
                    'pc':first_use['pc_hex'],'instruction':first_use['text']
                },
                'overwrite':None if overwrite is None else {
                    'pc':overwrite['pc_hex'],'instruction':overwrite['text']
                },
            }
            if lane<3:
                if first_use is None or first_use['op']!='v_sub_f32':
                    violations.append({
                        'shader':h,'error':f'API12 dword {28+lane} first use is not v_sub_f32',
                        'word':word,
                    })
                word['classification']='camera_component_live'
            else:
                if first_use is not None:
                    violations.append({
                        'shader':h,'error':'API12 dword31 read before overwrite',
                        'word':word,
                    })
                word['classification']='dead_before_read'
            words.append(word)

        proofs.append({
            'pixel_shader':h,
            'logical_start_register':start,
            'extended_user_data_descriptor_dword':spill,
            'descriptor_load':{'pc':desc['pc_hex'],'instruction':desc['text']},
            'camera_window_load':{'pc':load['pc_hex'],'instruction':load['text']},
            'api12_window_dwords':[28,29,30,31],
            'words':words,
        })

    complete=(len(proofs)==len(api12) and not violations)
    out={
        'schema_version':1,
        'status':'D1_TERRAIN_API12_CAMERA_WINDOW_EXACT' if complete else 'D1_TERRAIN_API12_CAMERA_WINDOW_PARTIAL',
        'source_dataflow_status':flow.get('status'),
        'api12_shader_count':len(api12),
        'proved_shader_count':len(proofs),
        'logical_start_register_histogram':{str(k):v for k,v in sorted(start_hist.items())},
        'camera_live_dwords':[28,29,30],
        'dead_fourth_dword':31,
        'shaders':proofs,
        'violations':violations,
        'semantic_reference':'evidence/d1_roi_terrain_api12_camera_window_2026-10-02.json',
        'proof_boundary':(
            'For each scoped terrain PS, exact native user-data dataflow resolves API12 to '
            'one dwordx4 load at dword offset 0x1C; dwords 28..30 are first consumed by '
            'v_sub_f32 and dword31 dies before read. Camera XYZ semantics are promoted only '
            'for this already source-closed D1 terrain API12 window; no other API12 words '
            'or non-terrain shaders are generalized.'
        ),
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps({k:out[k] for k in (
        'status','api12_shader_count','proved_shader_count',
        'logical_start_register_histogram','camera_live_dwords',
        'dead_fourth_dword','violations'
    )},indent=2))
    return 0 if complete else 2

if __name__=='__main__':
    raise SystemExit(main())
