#!/usr/bin/env python3
"""Map CLRX GCN image instructions back to exact D1 shader t# resources.

The Sony InputUsageSlot table describes *logical user-data registers*.  On D1
PS4, only the first user-data SGPRs are necessarily resident.  Later slots are
spilled behind PtrExtendedUserData and loaded into arbitrary temporary SGPRs;
some large shaders also use PtrResourceTable and fetch T# descriptors by table
offset.  This analyzer follows those native loads so image instructions can be
mapped back to exact D1 texture indices instead of comparing raw SGPR numbers.

It remains semantic-neutral: this proves native resource/sampler consumption,
opcode and dmask, but does not rename a texture as albedo/normal/etc.
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
DMASK_RE=re.compile(r'\bdmask:(0x[0-9A-Fa-f]+|\d+)\b')
ADDR_RE=re.compile(r'/\*([0-9A-Fa-f]{8,16}):')
LOAD_RE=re.compile(
    r'\bs_load_dword(?:(x)(2|4|8|16))?\s+'
    r'(s\[\d+:\d+\]|s\d+),\s+(s\[\d+:\d+\]|s\d+),\s+'
    r'(0x[0-9A-Fa-f]+|\d+)'
)
MOV64_RE=re.compile(r'\bs_mov_b64\s+(s\[\d+:\d+\]),\s+(s\[\d+:\d+\])')
MOV32_RE=re.compile(r'\bs_mov_b32\s+(s\d+),\s+(s\d+)\b')
WRITELANE_RE=re.compile(r'\bv_writelane_b32\s+v(\d+),\s+s(\d+),\s+(\d+)\b')
READLANE_RE=re.compile(r'\bv_readlane_b32\s+s(\d+),\s+v(\d+),\s+(\d+)\b')
RANGE_TOKEN_RE=re.compile(r'^s\[(\d+):(\d+)\]$')
SINGLE_TOKEN_RE=re.compile(r'^s(\d+)$')

WIDTHS={
    'ImmResource':8,
    'ImmSampler':4,
    'ImmConstBuffer':4,
    'PtrExtendedUserData':2,
    'PtrResourceTable':2,
}
RESOURCE_KINDS={'ImmResource','ResourceTableResource'}


def norm(h:str)->str:
    return h.upper().removeprefix('0X').zfill(8)


def mask_channels(mask:int)->str:
    return ''.join(c for i,c in enumerate('xyzw') if mask & (1<<i))


def reg_range(tok:str)->list[int]:
    m=RANGE_TOKEN_RE.match(tok)
    if m:return list(range(int(m.group(1)),int(m.group(2))+1))
    m=SINGLE_TOKEN_RE.match(tok)
    return [int(m.group(1))] if m else []


def logical_words(usage:dict):
    """Logical Sony user-data dword -> provenance."""
    out={}
    for slot in usage.get('slots',[]):
        typ=slot.get('usage_name');start=int(slot.get('start_register',-1))
        width=WIDTHS.get(typ,1)
        base={
            'kind':typ,'api_slot':int(slot.get('api_slot',-1)),
            'logical_start':start,'chunk_mask':int(slot.get('chunk_mask',0)),
            'usage_slot_index':int(slot.get('index',-1)),
        }
        for i in range(width):out[start+i]={**base,'word':i}
    return out


def copy_provenance(phys:dict[int,dict],dst:list[int],src:list[int]):
    vals=[phys.get(x) for x in src]
    for x in dst:phys.pop(x,None)
    for d,v in zip(dst,vals):
        if v is not None:phys[d]=dict(v)


def range_provenance(phys:dict[int,dict],regs:list[int]):
    by=defaultdict(list)
    for r in regs:
        p=phys.get(r)
        if p is not None:by[(p['kind'],p['api_slot'])].append(r)
    return by


def analyze_shader(shader:str,text:str,usage:dict):
    logical=logical_words(usage)
    # Physical SGPR provenance evolves as native loads overwrite registers.
    phys={r:dict(p) for r,p in logical.items() if r<16}
    # Small scratch model for the descriptor-preserving writelane/readlane idiom
    # emitted by several large D1 shaders.
    vlane={}

    instructions=[];resource_counts=Counter();sampler_counts=Counter();op_counts=Counter();unmatched=[]
    provenance_events=[]

    for lineno,line in enumerate(text.splitlines(),1):
        # Scalar descriptor/pointer copies.
        m=MOV64_RE.search(line)
        if m:
            dst,src=reg_range(m.group(1)),reg_range(m.group(2))
            copy_provenance(phys,dst,src)
        m=MOV32_RE.search(line)
        if m:
            dst,src=reg_range(m.group(1)),reg_range(m.group(2))
            copy_provenance(phys,dst,src)

        # Preserve descriptor words temporarily moved through one VGPR lane bank.
        m=WRITELANE_RE.search(line)
        if m:
            v,lane,s=int(m.group(1)),int(m.group(3)),int(m.group(2))
            p=phys.get(s)
            if p is None:vlane.pop((v,lane),None)
            else:vlane[(v,lane)]=dict(p)
        m=READLANE_RE.search(line)
        if m:
            s,v,lane=int(m.group(1)),int(m.group(2)),int(m.group(3))
            phys.pop(s,None);p=vlane.get((v,lane))
            if p is not None:phys[s]=dict(p)

        # SMEM loads from the extended user-data pointer recover logical slots.
        # Offsets in these GFX700 instructions are dword indices.  The spilled
        # area begins at logical user-data dword 16.
        m=LOAD_RE.search(line)
        if m:
            dst=reg_range(m.group(3));src=reg_range(m.group(4));off=int(m.group(5),0)
            width=int(m.group(2)) if m.group(1) else 1
            srcp=phys.get(src[0]) if src else None
            for d in dst:phys.pop(d,None)
            event={'line_number':lineno,'assembly':line.strip(),'destination':dst,'offset_dwords':off,'source_provenance':srcp}
            if srcp and srcp['kind']=='PtrExtendedUserData':
                lstart=16+off
                for i,d in enumerate(dst):
                    p=logical.get(lstart+i)
                    if p is not None:phys[d]=dict(p)
                event.update({'resolved_kind':'extended_user_data','logical_start':lstart})
            elif srcp and srcp['kind']=='PtrResourceTable' and width==8 and off%8==0:
                # Resource-table entries are eight-dword T# descriptors.  The
                # table api_slot is the base texture index (0 in current Tower
                # families); sequential 8-dword offsets therefore identify t#.
                ti=int(srcp['api_slot'])+off//8
                p={'kind':'ResourceTableResource','api_slot':ti,'logical_start':None,
                   'table_offset_dwords':off,'usage_slot_index':srcp.get('usage_slot_index')}
                for i,d in enumerate(dst):phys[d]={**p,'word':i}
                event.update({'resolved_kind':'resource_table','texture_index':ti})
            provenance_events.append(event)

        im=IMAGE_RE.search(line)
        if not im:continue
        op=im.group(1);op_counts[op]+=1
        ranges=[list(range(int(a),int(b)+1)) for a,b in SGPR_RANGE_RE.findall(line)]
        rmatch=[];smatch=[]
        for rg in ranges:
            by=range_provenance(phys,rg)
            for (kind,api),regs in by.items():
                if kind in RESOURCE_KINDS and len(regs)==8:
                    rmatch.append({'sgpr':f's[{rg[0]}:{rg[-1]}]','start_register':rg[0],'end_register':rg[-1],
                                   'texture_index':api,'provenance_kind':kind})
                elif kind=='ImmSampler' and len(regs)==4:
                    smatch.append({'sgpr':f's[{rg[0]}:{rg[-1]}]','start_register':rg[0],'end_register':rg[-1],
                                   'sampler_index':api,'provenance_kind':kind})
        dm=DMASK_RE.search(line)
        # CLRX omits dmask when the encoded mask is its x-only default.  In all
        # observed omitted-mask D1 instructions the raw first word is F...0100
        # and destination width is one; record that native/default value while
        # retaining whether the disassembler printed it explicitly.
        dmask=int(dm.group(1),0) if dm else 1
        am=ADDR_RE.search(line)
        rec={
            'line_number':lineno,'address':am.group(1).upper() if am else None,'opcode':op,
            'dmask':dmask,'dmask_channels':mask_channels(dmask),'dmask_explicit':bool(dm),
            'resources':rmatch,'samplers':smatch,'assembly':line.strip(),
        }
        instructions.append(rec)
        if not rmatch:
            miss={'line_number':lineno,'opcode':op,'reason':'resource descriptor provenance unresolved','assembly':line.strip()}
            unmatched.append(miss)
        for r in rmatch:resource_counts[r['texture_index']]+=1
        for s in smatch:sampler_counts[s['sampler_index']]+=1

    declared=sorted({int(s['api_slot']) for s in usage.get('slots',[]) if s.get('usage_name')=='ImmResource'})
    # PtrResourceTable does not enumerate texture indices in InputUsageSlot;
    # table indices proven by actual descriptor loads are still exact uses.
    used=sorted(resource_counts)
    return {
        'shader':shader,'image_instruction_count':len(instructions),'image_opcodes':dict(op_counts.most_common()),
        'declared_immediate_texture_indices':declared,'used_texture_indices':used,
        'unused_declared_immediate_texture_indices':sorted(set(declared)-set(used)),
        'texture_instruction_counts':{str(k):v for k,v in sorted(resource_counts.items())},
        'sampler_instruction_counts':{str(k):v for k,v in sorted(sampler_counts.items())},
        'unmatched_image_instruction_count':len(unmatched),'unmatched_image_instructions':unmatched,
        'instructions':instructions,'provenance_events':provenance_events,
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
        if not m:continue
        sh=norm(m.group(1));src=by.get(sh)
        if not src or not src.get('usage'):
            missing.append({'shader':sh,'disassembly':str(p),'reason':'usage table missing from extraction report'});continue
        rows.append(analyze_shader(sh,p.read_text(errors='replace'),src['usage']))
    seen={r['shader'] for r in rows}
    expected={norm(r['shader']) for r in ext.get('shaders',[]) if r.get('gcn_file')}
    missing_disasm=sorted(expected-seen)
    total_images=sum(r['image_instruction_count'] for r in rows)
    total_unmatched=sum(r['unmatched_image_instruction_count'] for r in rows)
    out={
        'schema_version':2,'status':'D1_GCN_IMAGE_RESOURCE_USAGE_EXACT' if not total_unmatched and not missing_disasm and not missing else 'D1_GCN_IMAGE_RESOURCE_USAGE_PARTIAL',
        'shader_count':len(rows),'image_instruction_count':total_images,'unmatched_image_instruction_count':total_unmatched,
        'missing_disassembly_shaders':missing_disasm,'missing_usage':missing,'shaders':rows,
        'policy':'Texture indices are recovered from Sony user-data provenance, including PtrExtendedUserData spills and PtrResourceTable descriptor loads. No albedo/normal/PBR role is inferred here.',
    }
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'shaders':len(rows),'image_instructions':total_images,'unmatched_image_instructions':total_unmatched,
                      'missing_disassembly':len(missing_disasm)},indent=2))
    return 0 if total_unmatched==0 and not missing_disasm and not missing else 2

if __name__=='__main__':raise SystemExit(main())
