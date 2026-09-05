#!/usr/bin/env python3
"""Probe D1 ROI SMapDataTable serialization without assuming the broken array view.

The current map-data census used the source-derived DynamicArray descriptor at +0x08
and a 0x90-byte SMapDataEntry stride. Several shipped Tower tables instead produced
impossible starts/counts. This diagnostic keeps those source values as candidates,
but independently searches descriptor offsets, record strides, and exact
payload-size factorizations against shipped-data invariants.

Nothing in this tool promotes a new layout automatically. It records raw bytes,
same-class patch occurrences, descriptor candidates, and record-run candidates so a
single framing rule can be proven across all target tables before the canonical
census is changed.
"""
from __future__ import annotations
import argparse,json,math,struct,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import d1_tower_map_schema_validate_v5 as v5

TABLE_CLASS='808009A2'; ENTITY_CLASS='80800734'
SOURCE_STRIDE=0x90
CANDIDATE_STRIDES=(0x90,0x98,0xA0,0xA8,0xB0)

def norm(x): return str(x).upper().removeprefix('0X').zfill(8)
def i32(b,o): return struct.unpack_from('<i',b,o)[0]
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def i64(b,o): return struct.unpack_from('<q',b,o)[0]
def f4(b,o): return struct.unpack_from('<4f',b,o)
def hx(b,n=0x80): return b[:min(n,len(b))].hex()

def record_score(c,b,start,count,stride):
    if count<=0 or start<0 or start+count*stride>len(b): return None
    # The known D1 fields under test all lie below +0x90, so every candidate
    # stride here can be scored without assuming anything about a possible tail.
    if stride<0x90: return None
    ent_exists=ent_class=finite=rot_reasonable=resource_bounds=0
    samples=[]
    for i in range(count):
        o=start+i*stride
        eh=f'{u32(b,o):08X}'; m=c.entry_meta(eh)
        ent_exists += int(m is not None)
        ent_class += int(bool(m and norm(m.get('reference',''))==ENTITY_CLASS))
        vals=f4(b,o+0x20)+f4(b,o+0x30)
        good=all(math.isfinite(x) for x in vals); finite+=int(good)
        r=vals[:4]
        rot_reasonable += int(good and max(abs(x) for x in r)<2.5)
        rel=i64(b,o+0x88)
        # ResourcePointer is allowed to be null. A non-null pointer is scored only
        # for landing inside the same serialized payload; no class semantics here.
        resource_bounds += int(rel==0 or 4 <= o+0x88+rel <= len(b))
        if i<3:
            samples.append({'index':i,'offset':o,'entity':eh,
                            'entity_reference':m.get('reference') if m else None,
                            'rotation':[float(x) for x in vals[:4]],
                            'translation':[float(x) for x in vals[4:]],
                            'resource_relative':rel})
    return {'start':start,'count':count,'stride':stride,'end':start+count*stride,
            'entity_exists':ent_exists,'entity_class_matches':ent_class,
            'finite_transforms':finite,'reasonable_rotations':rot_reasonable,
            'resource_pointer_in_bounds_or_null':resource_bounds,'samples':samples,
            'score':ent_class*100+ent_exists*10+finite+rot_reasonable+resource_bounds}

def descriptor_candidates(c,b):
    out=[]
    for off in range(0,min(0x50,max(0,len(b)-0x10))+1,4):
        count=i32(b,off); rel=i64(b,off+8)
        if count<=0 or count>20000: continue
        starts={
          'source_ptr_plus_rel_plus_0x10':off+8+rel+0x10,
          'ptr_plus_rel':off+8+rel,
          'struct_plus_rel_plus_0x10':off+rel+0x10,
          'file_rel_plus_0x10':rel+0x10,
          'file_rel':rel,
        }
        for stride in CANDIDATE_STRIDES:
            for formula,start in starts.items():
                rs=record_score(c,b,int(start),count,stride)
                if rs is not None:
                    out.append({'descriptor_offset':off,'count':count,
                                'unknown04':u32(b,off+4),'relative':rel,
                                'formula':formula,**rs})
    out.sort(key=lambda x:(-x['score'],x['descriptor_offset'],x['stride'],x['start']))
    return out[:80]

def exact_size_candidates(c,b):
    """Factor the whole payload as header + N * stride, then score every row."""
    out=[]
    for header in range(0,0x81,4):
        for stride in CANDIDATE_STRIDES:
            rem=len(b)-header
            if rem<=0 or rem%stride: continue
            count=rem//stride
            if count<=0 or count>20000: continue
            rs=record_score(c,b,header,count,stride)
            if rs:
                out.append({'header_bytes':header,'payload_exact':True,**rs})
    out.sort(key=lambda x:(-x['score'],-x['count'],x['header_bytes'],x['stride']))
    return out[:40]

def scan_runs(c,b):
    # Independent of any descriptor. Try each candidate stride and every byte
    # offset in the first 0x200 bytes.
    rows=[]
    for stride in CANDIDATE_STRIDES:
        maxstart=min(0x200,max(0,len(b)-stride))
        for start in range(maxstart+1):
            maxn=(len(b)-start)//stride
            if maxn<=0: continue
            n=min(maxn,256); rs=record_score(c,b,start,n,stride)
            if rs and (rs['entity_class_matches']>=2 or
                       (rs['finite_transforms']>=min(n,8) and
                        rs['reasonable_rotations']>=min(n,8))):
                rows.append(rs)
    rows.sort(key=lambda x:(-x['score'],-x['entity_class_matches'],-x['count'],x['stride'],x['start']))
    return rows[:50]

def occurrence_rows(c,h):
    rows=[]
    for gen,p,r,e in c.occ.get(h,[]):
        row={'snapshot':p.name,'generation':gen,'reference':e['reference'].upper(),
             'entry_index':int(e['index']),'file_size':int(e['file_size']),
             'available':bool(r.available(e['index']))}
        if row['available']:
            try:
                b=r.entry(e['index']); row['decoded_bytes']=len(b);row['prefix_hex']=hx(b,0x60)
                row['u32_prefix']=[f'{u32(b,o):08X}' for o in range(0,min(0x50,len(b)-3),4)]
            except Exception as ex: row['decode_error']=repr(ex)
        rows.append(row)
    return rows

def descriptor_view(b,off):
    if off+0x10>len(b): return None
    rel=i64(b,off+8)
    return {'offset':off,'count':i32(b,off),'unknown04':u32(b,off+4),
            'relative':rel,'source_formula_absolute':off+8+rel+0x10}

def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument('--snapshot',type=Path,action='append',required=True)
    ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('--map-data-table',action='append',required=True)
    ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    c=v5.v3.base.Corpus([p.resolve() for p in a.snapshot],a.runtime.resolve())
    tables=[]
    for x in a.map_data_table:
        h=norm(x); meta=c.entry_meta(h); b,src=c.payload(h)
        t={'hash':h,'meta':meta,'payload_source':src,'occurrences':occurrence_rows(c,h)}
        if not meta or norm(meta.get('reference',''))!=TABLE_CLASS:
            t['error']='class_mismatch';tables.append(t);continue
        if b is None:
            t['error']='payload_unavailable';tables.append(t);continue
        t['payload_bytes']=len(b);t['prefix_hex']=hx(b)
        t['u32_prefix']=[{'offset':o,'value':f'{u32(b,o):08X}'} for o in range(0,min(0x80,len(b)-3),4)]
        t['source_schema_descriptor']=descriptor_view(b,0x08)
        t['alternate_descriptor_0x10']=descriptor_view(b,0x10)
        t['descriptor_candidates']=descriptor_candidates(c,b)
        t['exact_size_candidates']=exact_size_candidates(c,b)
        t['record_run_candidates']=scan_runs(c,b)
        tables.append(t)
    out={'schema_version':2,'status':'D1_WORLD_MAP_DATA_TABLE_LAYOUT_PROBE',
      'table_class':TABLE_CLASS,'source_entry_class':'06048080',
      'source_entry_stride':SOURCE_STRIDE,'candidate_strides':list(CANDIDATE_STRIDES),
      'tables':tables,
      'policy':'Diagnostic only. No candidate becomes canonical until one serialization/framing rule explains all target tables and shipped class/transform/resource-pointer invariants.'}
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps([{'hash':t['hash'],'payload_bytes':t.get('payload_bytes'),
      'source':t.get('source_schema_descriptor'),'alternate_0x10':t.get('alternate_descriptor_0x10'),
      'best_descriptor':(t.get('descriptor_candidates') or [None])[0],
      'best_exact_size':(t.get('exact_size_candidates') or [None])[0],
      'best_run':(t.get('record_run_candidates') or [None])[0]} for t in tables],indent=2))
    return 0
if __name__=='__main__': raise SystemExit(main())
