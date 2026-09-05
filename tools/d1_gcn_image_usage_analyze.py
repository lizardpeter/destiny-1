#!/usr/bin/env python3
"""Map CLRX GCN image instructions back to exact D1 shader t# resources.

Inputs:
- the exact `d1_world_shader_extract.py` report, whose Sony InputUsageSlot table
  identifies ImmResource api_slot (D1 shader t#) -> SGPR descriptor range;
- one or more CLRX raw GFX700 disassemblies named `PS_<hash>.s`.

This stage is deliberately semantic-neutral.  It proves which serialized texture
register is actually consumed by each native image instruction, which sampler
slot accompanies it, the image opcode, and the requested dmask.  It does NOT
rename a resource to albedo/normal/etc.  Higher-level dataflow analysis may use
this exact census as evidence.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

SHADER_RE=re.compile(r'PS_([0-9A-Fa-f]{8})\.s$')
IMAGE_RE=re.compile(r'\b(image_[A-Za-z0-9_]+)\b')
SGPR_RANGE_RE=re.compile(r'\bs\[(\d+)\s*:\s*(\d+)\]')
SGPR_SINGLE_RE=re.compile(r'\bs(\d+)\b')
DMASK_RE=re.compile(r'\bdmask:0x([0-9A-Fa-f]+)\b')
HEXADDR_RE=re.compile(r'//\s*([0-9A-Fa-f]{8,16})\s*:')


def norm(h:str)->str:
    return h.upper().removeprefix('0X').zfill(8)


def mask_channels(mask:int)->str:
    return ''.join(c for i,c in enumerate('xyzw') if mask & (1<<i))


def descriptor_maps(usage:dict):
    resources={};samplers={};const_buffers={}
    for slot in usage.get('slots',[]):
        typ=slot.get('usage_name')
        start=int(slot.get('start_register',-1))
        api=int(slot.get('api_slot',-1))
        if typ=='ImmResource':
            # GCN image resource descriptors are 8 SGPRs for these validated D1
            # PS4 shaders. The InputUsageSlot register_count bit is preserved in
            # the source report, but the native image instruction itself gives
            # us the exact range consumed.
            resources[start]={'api_slot':api,'usage_slot':slot}
        elif typ=='ImmSampler':
            samplers[start]={'api_slot':api,'usage_slot':slot}
        elif typ=='ImmConstBuffer':
            const_buffers[start]={'api_slot':api,'usage_slot':slot}
    return resources,samplers,const_buffers


def parse_s_operands(line:str):
    out=[];covered=[]
    for m in SGPR_RANGE_RE.finditer(line):
        a=int(m.group(1));b=int(m.group(2));out.append({'start':a,'end':b,'text':m.group(0)})
        covered.append((m.start(),m.end()))
    # Single scalar operands are rare for image descriptors but retain them so
    # unusual instructions cannot silently disappear from the report.
    for m in SGPR_SINGLE_RE.finditer(line):
        if any(a<=m.start()<b for a,b in covered): continue
        a=int(m.group(1));out.append({'start':a,'end':a,'text':m.group(0)})
    return out


def analyze_shader(shader:str,text:str,usage:dict):
    resources,samplers,_=descriptor_maps(usage)
    instructions=[];resource_counts=Counter();sampler_counts=Counter();op_counts=Counter();unmatched=[]
    for lineno,line in enumerate(text.splitlines(),1):
        im=IMAGE_RE.search(line)
        if not im: continue
        op=im.group(1)
        sops=parse_s_operands(line)
        rmatch=[];smatch=[]
        for s in sops:
            if s['start'] in resources:
                x=resources[s['start']]
                rmatch.append({'sgpr':s['text'],'start_register':s['start'],'end_register':s['end'],'texture_index':x['api_slot']})
            if s['start'] in samplers:
                x=samplers[s['start']]
                smatch.append({'sgpr':s['text'],'start_register':s['start'],'end_register':s['end'],'sampler_index':x['api_slot']})
        dm=DMASK_RE.search(line);dmask=int(dm.group(1),16) if dm else None
        am=HEXADDR_RE.search(line)
        rec={
            'line_number':lineno,'address':am.group(1).upper() if am else None,'opcode':op,
            'dmask':dmask,'dmask_channels':mask_channels(dmask) if dmask is not None else None,
            'resources':rmatch,'samplers':smatch,'scalar_operands':sops,'assembly':line.strip(),
        }
        instructions.append(rec);op_counts[op]+=1
        if not rmatch:
            unmatched.append({'line_number':lineno,'opcode':op,'reason':'no ImmResource SGPR start matched','assembly':line.strip()})
        for r in rmatch: resource_counts[r['texture_index']]+=1
        for s in smatch: sampler_counts[s['sampler_index']]+=1

    declared=sorted(int(v['api_slot']) for v in resources.values())
    used=sorted(resource_counts)
    return {
        'shader':shader,
        'image_instruction_count':len(instructions),
        'image_opcodes':dict(op_counts.most_common()),
        'declared_texture_indices':declared,
        'used_texture_indices':used,
        'unused_declared_texture_indices':sorted(set(declared)-set(used)),
        'texture_instruction_counts':{str(k):v for k,v in sorted(resource_counts.items())},
        'sampler_instruction_counts':{str(k):v for k,v in sorted(sampler_counts.items())},
        'unmatched_image_instruction_count':len(unmatched),
        'unmatched_image_instructions':unmatched,
        'instructions':instructions,
    }


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--extract-report',type=Path,required=True)
    ap.add_argument('--disasm-dir',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    ext=json.loads(a.extract_report.read_text())
    by={norm(r['shader']):r for r in ext.get('shaders',[])}
    rows=[];missing=[]
    for p in sorted(a.disasm_dir.glob('PS_*.s')):
        m=SHADER_RE.search(p.name)
        if not m: continue
        sh=norm(m.group(1));src=by.get(sh)
        if not src or not src.get('usage'):
            missing.append({'shader':sh,'disassembly':str(p),'reason':'usage table missing from extraction report'})
            continue
        rows.append(analyze_shader(sh,p.read_text(errors='replace'),src['usage']))
    seen={r['shader'] for r in rows}
    expected={norm(r['shader']) for r in ext.get('shaders',[]) if r.get('gcn_file')}
    missing_disasm=sorted(expected-seen)
    total_images=sum(r['image_instruction_count'] for r in rows)
    total_unmatched=sum(r['unmatched_image_instruction_count'] for r in rows)
    out={
        'schema_version':1,
        'status':'D1_GCN_IMAGE_RESOURCE_USAGE_EXACT',
        'shader_count':len(rows),
        'image_instruction_count':total_images,
        'unmatched_image_instruction_count':total_unmatched,
        'missing_disassembly_shaders':missing_disasm,
        'missing_usage':missing,
        'shaders':rows,
        'policy':'Texture indices are mapped only from Sony ImmResource api_slot to the SGPR descriptor range consumed by native image instructions. No albedo/normal/PBR role is inferred here.',
    }
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({
        'shaders':len(rows),'image_instructions':total_images,
        'unmatched_image_instructions':total_unmatched,'missing_disassembly':len(missing_disasm),
        'unused_declared_total':sum(len(r['unused_declared_texture_indices']) for r in rows),
    },indent=2))
    # Fail closed if a decoded image instruction could not be associated with a
    # declared native resource. Missing disassembly is also an extraction error.
    return 0 if total_unmatched==0 and not missing_disasm and not missing else 2

if __name__=='__main__':raise SystemExit(main())
