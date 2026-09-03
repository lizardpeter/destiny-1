#!/usr/bin/env python3
from __future__ import annotations
import argparse, collections, json, struct, sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_entry_extract import EntryReader

PS4_MATERIAL_CLASS='80801AD7'
XBOX_MATERIAL_CLASS='80801C32'
XBOX_DXBC_CONTAINER_CLASS='80801B7C'
XBOX_VECTOR_CONTAINER_CLASS='80801AA5'


def u32(b,o): return struct.unpack_from('<I',b,o)[0]

def local_refs(r,b,by):
    out=[]
    for o in range(0,len(b)-3,4):
        v=u32(b,o)
        t=by.get(v)
        if t:
            out.append({'offset':o,'tag_hash':t['tag_hash'],'entry_index':t['index'],'type':t['type'],'subtype':t['subtype'],'class_hash':t['reference'],'size':t['file_size'],'available':r.available(t['index'])})
    return out

def summarize(r,class_hash):
    cls=class_hash.upper().removeprefix('0X')
    by={int(e['tag_hash'],16):e for e in r.entries}
    allm=[e for e in r.entries if e['type']==16 and e['subtype']==0 and e['reference'].upper()==cls]
    resident=[e for e in allm if r.available(e['index'])]
    size_counts=collections.Counter(e['file_size'] for e in resident)
    offsets=collections.defaultdict(collections.Counter)
    examples={}
    for e in resident:
        b=r.entry(e['index'])
        refs=local_refs(r,b,by)
        for x in refs:
            key=(x['type'],x['subtype'],x['class_hash'],x['size'])
            offsets[x['offset']][key]+=1
        examples[e['tag_hash']]={'entry_index':e['index'],'size':len(b),'references':refs}
    common=[]
    for off,c in sorted(offsets.items(),key=lambda kv:(-sum(kv[1].values()),kv[0])):
        total=sum(c.values())
        common.append({'offset':off,'count':total,'targets':[{'type':k[0],'subtype':k[1],'class_hash':k[2],'size':k[3],'count':n} for k,n in c.most_common()]})
    return {'class_hash':cls,'total_entries':len(allm),'resident_entries':len(resident),'resident_size_counts':dict(sorted(size_counts.items())),'common_reference_offsets':common,'materials':examples}

def main():
    ap=argparse.ArgumentParser(description='Probe D1 material/tag reference structure')
    ap.add_argument('pkg',type=Path); ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--class-hash',default=None,help='defaults to platform material class')
    ap.add_argument('--tag-hash',help='restrict verbose material list to one TagHash')
    ap.add_argument('-o','--output',type=Path)
    a=ap.parse_args(); r=EntryReader(a.pkg,a.runtime)
    cls=a.class_hash or (PS4_MATERIAL_CLASS if r.h['platform']=='PS4' else XBOX_MATERIAL_CLASS)
    rep={'package':str(r.pkg),'platform':r.h['platform'],'material_probe':summarize(r,cls)}
    if a.tag_hash:
        th=a.tag_hash.upper().removeprefix('0X')
        mats=rep['material_probe']['materials']; rep['material_probe']['materials']={th:mats[th]} if th in mats else {}
    text=json.dumps(rep,indent=2)
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(text+'\n'); print('wrote',a.output)
    else: print(text)
if __name__=='__main__': main()
