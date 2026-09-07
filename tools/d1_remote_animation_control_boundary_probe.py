#!/usr/bin/env python3
"""Forensically inspect D1 80802C0E selectors that cross the declared animation list.

This is intentionally a diagnostic tool, not a parser relaxation. It preserves the
serialized array counts/pointers, dumps words around the declared animation-list end,
and classifies any aligned FileHash-looking words through the verified retail catalog.
It also reports neighboring selector records so an exceptional boundary encoding can
be distinguished from a globally incorrect packed count/start interpretation.
"""
from __future__ import annotations
import argparse,json,struct,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_activity_placements import RemoteCorpus
from d1_split_tar_extract import SplitHttpTar

CONTROL_REF='80802C0E'
CLIP_REF='808005A1'

def norm(v): return str(v).upper().removeprefix('0X').zfill(8)
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def f32(b,o): return struct.unpack_from('<f',b,o)[0]

def rel_array(b,count_off,ptr_off,stride):
    count=u32(b,count_off); rel=u32(b,ptr_off); hdr=ptr_off+rel
    if hdr<0 or hdr+0x10>len(b): raise ValueError(f'header_oob:{hdr}')
    repeated=u32(b,hdr); elem=u32(b,hdr+8); data=hdr+0x10; end=data+count*stride
    return {'count':count,'relative':rel,'header':hdr,'repeated_count':repeated,
            'element_class':f'{elem:08X}','data':data,'end':end,'stride':stride,
            'payload_size':len(b),'bounds_ok':end<=len(b),'count_matches':count==repeated}

def classify_word(c,v):
    h=f'{v:08X}'; m=c.entry_meta(h)
    return {'value':h,'entry':m,'reference':None if m is None else norm(m.get('reference','FFFFFFFF'))}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--control',action='append',required=True)
    ap.add_argument('--member-catalog',type=Path,action='append',required=True)
    ap.add_argument('--base-url',required=True); ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--runtime',type=Path,required=True); ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()
    cats=load_catalogs(a.member_catalog); base=a.base_url.rstrip('/')
    arc=SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1,a.part_count+1)],retries=6,timeout=90)
    c=RemoteCorpus(arc,cats,a.runtime)
    rows=[]; violations=[]
    for ch0 in a.control:
        ch=norm(ch0); m=c.entry_meta(ch); b,src=c.payload(ch)
        r={'control':ch,'meta':m,'source':str(src),'violations':[]}
        if m is None or norm(m.get('reference','FFFFFFFF'))!=CONTROL_REF or b is None:
            r['violations'].append('control_missing_class_or_payload');rows.append(r);continue
        try:
            aa=rel_array(b,0x08,0x10,4); ss=rel_array(b,0x68,0x70,0x20)
            r['animation_array']=aa;r['selector_array']=ss
            anim=[]
            for i in range(aa['count']):
                x=classify_word(c,u32(b,aa['data']+i*4));x['index']=i;anim.append(x)
            r['animation_list']=anim
            # Inspect 16 words on either side of the declared bank boundary where in-bounds.
            words=[]
            for o in range(max(0,aa['end']-16*4),min(len(b),aa['end']+16*4),4):
                x=classify_word(c,u32(b,o));x['offset']=o;x['relative_to_declared_end']=o-aa['end'];words.append(x)
            r['animation_boundary_words']=words
            selectors=[];cross=[]
            for i in range(ss['count']):
                o=ss['data']+i*0x20; sh=u32(b,o+0x10); packed=u32(b,o+0x18)
                cnt=(packed>>16)&0xffff; start=packed&0xffff
                row={'record_index':i,'record_offset':o,'state_hash':f'{sh:08X}','scalar_f32':f32(b,o+0x14),
                     'packed_selection':f'{packed:08X}','selection_start':start,'selection_count':cnt,
                     'declared_range_end_exclusive':start+cnt,
                     'declared_bank_count':aa['count'],
                     'range_within_declared_bank':packed==0x0000FFFF or start+cnt<=aa['count']}
                if not row['range_within_declared_bank']:
                    cross.append(row)
                selectors.append(row)
            r['crossing_selectors']=cross
            neigh=[]
            for x in cross:
                lo=max(0,x['record_index']-4);hi=min(len(selectors),x['record_index']+5)
                neigh.append({'crossing_record_index':x['record_index'],'records':selectors[lo:hi]})
            r['selector_neighborhoods']=neigh
            # If exactly one missing list word would complete a crossing selection, inspect it explicitly.
            missing=[]
            for x in cross:
                for idx in range(max(x['selection_start'],aa['count']),x['selection_start']+x['selection_count']):
                    off=aa['data']+idx*4
                    item={'logical_index':idx,'serialized_offset_if_contiguous':off,'within_payload':off+4<=len(b)}
                    if item['within_payload']:
                        item.update(classify_word(c,u32(b,off)))
                    missing.append(item)
            r['crossing_missing_logical_items_if_contiguous']=missing
        except Exception as ex:r['violations'].append(repr(ex))
        violations.extend(f'{ch}:{x}' for x in r['violations']);rows.append(r)
    out={'schema':'d1_remote_animation_control_boundary_probe/v1','status':'COMPLETE' if not violations else 'WITH_VIOLATIONS',
         'controls':rows,'violation_count':len(violations),'violations':violations,
         'policy':'Diagnostic only. Words beyond the declared animation-list count are never promoted as list members by this tool, even when they resolve to s_animation_clip. Parser semantics require independent proof.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n')
    for r in rows:
        print('CONTROL',r['control'],'ANIMS',(r.get('animation_array') or {}).get('count'),'STATES',(r.get('selector_array') or {}).get('count'),
              'CROSS',len(r.get('crossing_selectors',[])),'MISSING',r.get('crossing_missing_logical_items_if_contiguous',[]))
    return 0 if not violations else 2
if __name__=='__main__': raise SystemExit(main())
