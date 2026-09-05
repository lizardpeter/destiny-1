#!/usr/bin/env python3
"""Probe D1 ROI SMapDataTable serialization without assuming the broken array view.

The current map-data census used the source-derived DynamicArray descriptor at +0x08,
but several shipped Tower tables produced impossible starts/counts.  This diagnostic
keeps the source schema as one candidate while independently scanning the payload for
0x90-byte SMapDataEntry runs and scoring them by shipped-data invariants.

Nothing in this tool promotes a new layout automatically.  It records enough raw
bytes, same-class patch occurrences, descriptor candidates and record-run candidates
to prove the framing/offset before changing the canonical census.
"""
from __future__ import annotations
import argparse,json,math,struct,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import d1_tower_map_schema_validate_v5 as v5

TABLE_CLASS='808009A2'; ENTITY_CLASS='80800734'; STRIDE=0x90

def norm(x): return str(x).upper().removeprefix('0X').zfill(8)
def i32(b,o): return struct.unpack_from('<i',b,o)[0]
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def i64(b,o): return struct.unpack_from('<q',b,o)[0]
def f4(b,o): return struct.unpack_from('<4f',b,o)
def hx(b,n=0x80): return b[:min(n,len(b))].hex()

def record_score(c,b,start,count):
    if count<=0 or start<0 or start+count*STRIDE>len(b): return None
    ent_exists=ent_class=finite=rot_reasonable=0
    samples=[]
    for i in range(count):
        o=start+i*STRIDE
        eh=f'{u32(b,o):08X}'; m=c.entry_meta(eh)
        ent_exists += int(m is not None)
        ent_class += int(bool(m and norm(m.get('reference',''))==ENTITY_CLASS))
        vals=f4(b,o+0x20)+f4(b,o+0x30)
        good=all(math.isfinite(x) for x in vals); finite+=int(good)
        r=vals[:4]
        rot_reasonable += int(good and max(abs(x) for x in r)<2.5)
        if i<3: samples.append({'index':i,'offset':o,'entity':eh,'entity_reference':m.get('reference') if m else None,
                                'rotation':[float(x) for x in vals[:4]],'translation':[float(x) for x in vals[4:]]})
    return {'start':start,'count':count,'end':start+count*STRIDE,
            'entity_exists':ent_exists,'entity_class_matches':ent_class,'finite_transforms':finite,
            'reasonable_rotations':rot_reasonable,'samples':samples,
            'score':ent_class*100+ent_exists*10+finite+rot_reasonable}

def descriptor_candidates(c,b):
    out=[]
    for off in range(0,min(0x40,max(0,len(b)-0x10))+1,4):
        count=i32(b,off); rel=i64(b,off+8)
        if count<0 or count>20000: continue
        starts={
          'source_ptr_plus_rel_plus_0x10':off+8+rel+0x10,
          'ptr_plus_rel':off+8+rel,
          'struct_plus_rel_plus_0x10':off+rel+0x10,
          'file_rel_plus_0x10':rel+0x10,
          'file_rel':rel,
        }
        for formula,start in starts.items():
            rs=record_score(c,b,int(start),count)
            if rs is not None:
                out.append({'descriptor_offset':off,'count':count,'unknown04':u32(b,off+4),'relative':rel,
                            'formula':formula,**rs})
    out.sort(key=lambda x:(-x['score'],x['descriptor_offset'],x['start']))
    return out[:40]

def scan_runs(c,b):
    # A run candidate is independent of the descriptor.  Try every byte offset in
    # the first 0x200 bytes, because a relative-pointer target need not be aligned.
    maxstart=min(0x200,max(0,len(b)-STRIDE)); rows=[]
    for start in range(maxstart+1):
        maxn=(len(b)-start)//STRIDE
        if maxn<=0: continue
        # Score the longest plausible prefix; entity resolution is the strongest
        # signal, but keep finite-only candidates because some rows can be resource-only.
        n=min(maxn,256); rs=record_score(c,b,start,n)
        if rs and (rs['entity_class_matches']>=2 or (rs['finite_transforms']>=min(n,8) and rs['reasonable_rotations']>=min(n,8))):
            rows.append(rs)
    rows.sort(key=lambda x:(-x['score'],-x['entity_class_matches'],-x['count'],x['start']))
    return rows[:30]

def occurrence_rows(c,h):
    rows=[]
    for gen,p,r,e in c.occ.get(h,[]):
        row={'snapshot':p.name,'generation':gen,'reference':e['reference'].upper(),'entry_index':int(e['index']),
             'file_size':int(e['file_size']),'available':bool(r.available(e['index']))}
        if row['available']:
            try:
                b=r.entry(e['index']); row['decoded_bytes']=len(b);row['prefix_hex']=hx(b,0x50)
                row['u32_prefix']=[f'{u32(b,o):08X}' for o in range(0,min(0x40,len(b)-3),4)]
            except Exception as ex: row['decode_error']=repr(ex)
        rows.append(row)
    return rows

def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument('--snapshot',type=Path,action='append',required=True)
    ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('--map-data-table',action='append',required=True)
    ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    c=v5.v3.base.Corpus([p.resolve() for p in a.snapshot],a.runtime.resolve())
    tables=[]
    for x in a.map_data_table:
        h=norm(x); meta=c.entry_meta(h); b,src=c.payload(h)
        t={'hash':h,'meta':meta,'payload_source':src,'occurrences':occurrence_rows(c,h)}
        if not meta or norm(meta.get('reference',''))!=TABLE_CLASS: t['error']='class_mismatch';tables.append(t);continue
        if b is None: t['error']='payload_unavailable';tables.append(t);continue
        t['payload_bytes']=len(b);t['prefix_hex']=hx(b);t['u32_prefix']=[{'offset':o,'value':f'{u32(b,o):08X}'} for o in range(0,min(0x80,len(b)-3),4)]
        t['source_schema_descriptor']={'offset':8,'count':i32(b,8) if len(b)>=12 else None,
          'unknown04':u32(b,12) if len(b)>=16 else None,'relative':i64(b,16) if len(b)>=24 else None,
          'computed_absolute':(8+8+i64(b,16)+0x10) if len(b)>=24 else None}
        t['descriptor_candidates']=descriptor_candidates(c,b);t['record_run_candidates']=scan_runs(c,b)
        tables.append(t)
    out={'schema_version':1,'status':'D1_WORLD_MAP_DATA_TABLE_LAYOUT_PROBE','table_class':TABLE_CLASS,
      'entry_class':'06048080','entry_stride':STRIDE,'tables':tables,
      'policy':'Diagnostic only. No candidate becomes canonical until one serialization/framing rule explains all target tables and shipped class/transform invariants.'}
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps([{'hash':t['hash'],'payload_bytes':t.get('payload_bytes'),'source':t.get('source_schema_descriptor'),
      'best_descriptor':(t.get('descriptor_candidates') or [None])[0],'best_run':(t.get('record_run_candidates') or [None])[0]} for t in tables],indent=2))
    return 0
if __name__=='__main__': raise SystemExit(main())
