#!/usr/bin/env python3
"""Recover exact D1 PS4 GCN constant-buffer dword usage from Sony user-data provenance.

The analyzer follows the same logical->physical SGPR model used by the image-resource
analyzer, but terminates at SMEM scalar-buffer loads.  It proves which API constant
buffer descriptor feeds each s_buffer_load_* and expands the immediate offset/width
into exact dword indices.

No semantic names are assigned to constant-buffer values.
"""
from __future__ import annotations
import argparse, collections, json, re
from pathlib import Path

SHADER_RE=re.compile(r'PS_([0-9A-Fa-f]{8})(?:_GFX700)?\\.s
SMEM_RE=re.compile(
    r'\bs_load_dword(?:(x)(2|4|8|16))?\s+'
    r'(s\[\d+:\d+\]|s\d+),\s+(s\[\d+:\d+\]|s\d+),\s+'
    r'(0x[0-9A-Fa-f]+|\d+)'
)
SBUF_RE=re.compile(
    r'\bs_buffer_load_dword(?:(x)(2|4|8|16))?\s+'
    r'(s\[\d+:\d+\]|s\d+),\s+(s\[\d+:\d+\]|s\d+),\s+'
    r'(0x[0-9A-Fa-f]+|\d+)'
)
MOV64_RE=re.compile(r'\bs_mov_b64\s+(s\[\d+:\d+\]),\s+(s\[\d+:\d+\])')
MOV32_RE=re.compile(r'\bs_mov_b32\s+(s\d+),\s+(s\d+)\b')
RANGE_RE=re.compile(r'^s\[(\d+):(\d+)\]$')
SINGLE_RE=re.compile(r'^s(\d+)$')
ADDR_RE=re.compile(r'/\*([0-9A-Fa-f]{8,16}):')

WIDTHS={'ImmConstBuffer':4,'PtrExtendedUserData':2}

def norm(x): return str(x).upper().removeprefix('0X').zfill(8)

def regs(tok):
    m=RANGE_RE.match(tok)
    if m:return list(range(int(m.group(1)),int(m.group(2))+1))
    m=SINGLE_RE.match(tok)
    return [int(m.group(1))] if m else []

def logical_words(usage):
    out={}
    for slot in usage.get('slots',[]):
        typ=slot.get('usage_name'); start=int(slot.get('start_register',-1))
        width=WIDTHS.get(typ)
        if width is None: continue
        base={'kind':typ,'api_slot':int(slot.get('api_slot',-1)),'logical_start':start,'usage_slot_index':int(slot.get('index',-1))}
        for i in range(width): out[start+i]={**base,'word':i}
    return out

def copyprov(phys,dst,src):
    vals=[phys.get(x) for x in src]
    for d in dst: phys.pop(d,None)
    for d,v in zip(dst,vals):
        if v is not None: phys[d]=dict(v)

def descriptor(phys,src):
    if len(src)!=4:return None
    vals=[phys.get(x) for x in src]
    if any(v is None for v in vals):return None
    keys={(v.get('kind'),v.get('api_slot'),v.get('logical_start')) for v in vals}
    words=[v.get('word') for v in vals]
    if len(keys)==1 and keys.pop()[0]=='ImmConstBuffer' and words==[0,1,2,3]:
        v=vals[0]
        return {'kind':'ImmConstBuffer','api_slot':int(v['api_slot']),'logical_start':int(v['logical_start'])}
    return None

def width(m):
    return int(m.group(2)) if m.group(1) else 1

def analyze(shader,text,usage):
    logical=logical_words(usage)
    phys={r:dict(p) for r,p in logical.items() if r<16}
    events=[]; unresolved=[]; reads=collections.defaultdict(set)
    for lineno,line in enumerate(text.splitlines(),1):
        m=MOV64_RE.search(line)
        if m: copyprov(phys,regs(m.group(1)),regs(m.group(2)))
        m=MOV32_RE.search(line)
        if m: copyprov(phys,regs(m.group(1)),regs(m.group(2)))

        m=SMEM_RE.search(line)
        if m:
            dst=regs(m.group(3)); src=regs(m.group(4)); off=int(m.group(5),0)
            srcp=phys.get(src[0]) if src else None
            for d in dst: phys.pop(d,None)
            if srcp and srcp.get('kind')=='PtrExtendedUserData':
                lstart=16+off
                for i,d in enumerate(dst):
                    p=logical.get(lstart+i)
                    if p is not None: phys[d]=dict(p)

        m=SBUF_RE.search(line)
        if not m: continue
        dst=regs(m.group(3)); src=regs(m.group(4)); off=int(m.group(5),0); w=width(m)
        desc=descriptor(phys,src)
        am=ADDR_RE.search(line)
        row={'line_number':lineno,'address':am.group(1).upper() if am else None,'destination':dst,
             'descriptor_registers':src,'offset_dwords':off,'width_dwords':w,
             'dword_indices':list(range(off,off+w)),'descriptor_provenance':desc,'assembly':line.strip()}
        if desc is None:
            unresolved.append(row)
        else:
            row['api_slot']=desc['api_slot']
            reads[desc['api_slot']].update(row['dword_indices'])
            events.append(row)
        # Scalar-buffer result values are ordinary data, so destination descriptor provenance dies.
        for d in dst: phys.pop(d,None)
    slots={str(k):sorted(v) for k,v in sorted(reads.items())}
    return {'shader':shader,'resolved_load_count':len(events),'unresolved_load_count':len(unresolved),
            'api_slot_read_dwords':slots,'loads':events,'unresolved_loads':unresolved}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--extract-report',type=Path,required=True)
    ap.add_argument('--disasm-dir',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    ext=json.loads(a.extract_report.read_text())
    by={norm(x['shader']):x for x in ext.get('shaders',[])}
    rows=[]; missing=[]
    for p in sorted(a.disasm_dir.glob('PS_*.s')):
        m=SHADER_RE.match(p.name)
        if not m: continue
        h=norm(m.group(1)); src=by.get(h)
        if not src or not src.get('usage'):
            missing.append({'shader':h,'reason':'extract usage missing'}); continue
        rows.append(analyze(h,p.read_text(errors='replace'),src['usage']))
    unresolved=sum(x['unresolved_load_count'] for x in rows)
    # Unresolved scalar-buffer loads are retained, because some shaders can construct
    # non-material descriptors through tables. Exactness here means every discovered
    # ImmConstBuffer read is provenance-closed; the report does not claim every SBUF
    # instruction in every shader is a material cbuffer.
    out={'schema':'d1_gcn_cbuffer_usage/v1','status':'D1_GCN_CBUFFER_USAGE_EXACT' if not missing else 'D1_GCN_CBUFFER_USAGE_PARTIAL',
         'shader_count':len(rows),'unresolved_scalar_buffer_load_count':unresolved,'missing_usage':missing,'shaders':rows,
         'policy':'API constant-buffer slots are assigned only when all four descriptor SGPR words trace to one Sony ImmConstBuffer usage slot. Immediate offsets are recorded as GFX700 scalar-buffer dword indices. Unresolved SBUF loads are preserved without invented ownership.'}
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'status':out['status'],'shader_count':len(rows),'unresolved_scalar_buffer_load_count':unresolved,
                      'api0':{x['shader']:x['api_slot_read_dwords'].get('0',[]) for x in rows if x['api_slot_read_dwords'].get('0')}},indent=2))
    return 0 if out['status']=='D1_GCN_CBUFFER_USAGE_EXACT' else 2

if __name__=='__main__': raise SystemExit(main())
)
SMEM_RE=re.compile(
    r'\bs_load_dword(?:(x)(2|4|8|16))?\s+'
    r'(s\[\d+:\d+\]|s\d+),\s+(s\[\d+:\d+\]|s\d+),\s+'
    r'(0x[0-9A-Fa-f]+|\d+)'
)
SBUF_RE=re.compile(
    r'\bs_buffer_load_dword(?:(x)(2|4|8|16))?\s+'
    r'(s\[\d+:\d+\]|s\d+),\s+(s\[\d+:\d+\]|s\d+),\s+'
    r'(0x[0-9A-Fa-f]+|\d+)'
)
MOV64_RE=re.compile(r'\bs_mov_b64\s+(s\[\d+:\d+\]),\s+(s\[\d+:\d+\])')
MOV32_RE=re.compile(r'\bs_mov_b32\s+(s\d+),\s+(s\d+)\b')
RANGE_RE=re.compile(r'^s\[(\d+):(\d+)\]$')
SINGLE_RE=re.compile(r'^s(\d+)$')
ADDR_RE=re.compile(r'/\*([0-9A-Fa-f]{8,16}):')

WIDTHS={'ImmConstBuffer':4,'PtrExtendedUserData':2}

def norm(x): return str(x).upper().removeprefix('0X').zfill(8)

def regs(tok):
    m=RANGE_RE.match(tok)
    if m:return list(range(int(m.group(1)),int(m.group(2))+1))
    m=SINGLE_RE.match(tok)
    return [int(m.group(1))] if m else []

def logical_words(usage):
    out={}
    for slot in usage.get('slots',[]):
        typ=slot.get('usage_name'); start=int(slot.get('start_register',-1))
        width=WIDTHS.get(typ)
        if width is None: continue
        base={'kind':typ,'api_slot':int(slot.get('api_slot',-1)),'logical_start':start,'usage_slot_index':int(slot.get('index',-1))}
        for i in range(width): out[start+i]={**base,'word':i}
    return out

def copyprov(phys,dst,src):
    vals=[phys.get(x) for x in src]
    for d in dst: phys.pop(d,None)
    for d,v in zip(dst,vals):
        if v is not None: phys[d]=dict(v)

def descriptor(phys,src):
    if len(src)!=4:return None
    vals=[phys.get(x) for x in src]
    if any(v is None for v in vals):return None
    keys={(v.get('kind'),v.get('api_slot'),v.get('logical_start')) for v in vals}
    words=[v.get('word') for v in vals]
    if len(keys)==1 and keys.pop()[0]=='ImmConstBuffer' and words==[0,1,2,3]:
        v=vals[0]
        return {'kind':'ImmConstBuffer','api_slot':int(v['api_slot']),'logical_start':int(v['logical_start'])}
    return None

def width(m):
    return int(m.group(2)) if m.group(1) else 1

def analyze(shader,text,usage):
    logical=logical_words(usage)
    phys={r:dict(p) for r,p in logical.items() if r<16}
    events=[]; unresolved=[]; reads=collections.defaultdict(set)
    for lineno,line in enumerate(text.splitlines(),1):
        m=MOV64_RE.search(line)
        if m: copyprov(phys,regs(m.group(1)),regs(m.group(2)))
        m=MOV32_RE.search(line)
        if m: copyprov(phys,regs(m.group(1)),regs(m.group(2)))

        m=SMEM_RE.search(line)
        if m:
            dst=regs(m.group(3)); src=regs(m.group(4)); off=int(m.group(5),0)
            srcp=phys.get(src[0]) if src else None
            for d in dst: phys.pop(d,None)
            if srcp and srcp.get('kind')=='PtrExtendedUserData':
                lstart=16+off
                for i,d in enumerate(dst):
                    p=logical.get(lstart+i)
                    if p is not None: phys[d]=dict(p)

        m=SBUF_RE.search(line)
        if not m: continue
        dst=regs(m.group(3)); src=regs(m.group(4)); off=int(m.group(5),0); w=width(m)
        desc=descriptor(phys,src)
        am=ADDR_RE.search(line)
        row={'line_number':lineno,'address':am.group(1).upper() if am else None,'destination':dst,
             'descriptor_registers':src,'offset_dwords':off,'width_dwords':w,
             'dword_indices':list(range(off,off+w)),'descriptor_provenance':desc,'assembly':line.strip()}
        if desc is None:
            unresolved.append(row)
        else:
            row['api_slot']=desc['api_slot']
            reads[desc['api_slot']].update(row['dword_indices'])
            events.append(row)
        # Scalar-buffer result values are ordinary data, so destination descriptor provenance dies.
        for d in dst: phys.pop(d,None)
    slots={str(k):sorted(v) for k,v in sorted(reads.items())}
    return {'shader':shader,'resolved_load_count':len(events),'unresolved_load_count':len(unresolved),
            'api_slot_read_dwords':slots,'loads':events,'unresolved_loads':unresolved}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--extract-report',type=Path,required=True)
    ap.add_argument('--disasm-dir',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    ext=json.loads(a.extract_report.read_text())
    by={norm(x['shader']):x for x in ext.get('shaders',[])}
    rows=[]; missing=[]
    for p in sorted(a.disasm_dir.glob('PS_*.s')):
        m=SHADER_RE.match(p.name)
        if not m: continue
        h=norm(m.group(1)); src=by.get(h)
        if not src or not src.get('usage'):
            missing.append({'shader':h,'reason':'extract usage missing'}); continue
        rows.append(analyze(h,p.read_text(errors='replace'),src['usage']))
    unresolved=sum(x['unresolved_load_count'] for x in rows)
    # Unresolved scalar-buffer loads are retained, because some shaders can construct
    # non-material descriptors through tables. Exactness here means every discovered
    # ImmConstBuffer read is provenance-closed; the report does not claim every SBUF
    # instruction in every shader is a material cbuffer.
    out={'schema':'d1_gcn_cbuffer_usage/v1','status':'D1_GCN_CBUFFER_USAGE_EXACT' if not missing else 'D1_GCN_CBUFFER_USAGE_PARTIAL',
         'shader_count':len(rows),'unresolved_scalar_buffer_load_count':unresolved,'missing_usage':missing,'shaders':rows,
         'policy':'API constant-buffer slots are assigned only when all four descriptor SGPR words trace to one Sony ImmConstBuffer usage slot. Immediate offsets are recorded as GFX700 scalar-buffer dword indices. Unresolved SBUF loads are preserved without invented ownership.'}
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'status':out['status'],'shader_count':len(rows),'unresolved_scalar_buffer_load_count':unresolved,
                      'api0':{x['shader']:x['api_slot_read_dwords'].get('0',[]) for x in rows if x['api_slot_read_dwords'].get('0')}},indent=2))
    return 0 if out['status']=='D1_GCN_CBUFFER_USAGE_EXACT' else 2

if __name__=='__main__': raise SystemExit(main())
