#!/usr/bin/env python3
"""Discover and recover archived D1 Bungie Armory pages for one exact item id.

This uses a CDX prefix only to discover the historical spelling/encoding of the
Armory URL. Every returned capture is then filtered by parsed query parameters so
`item` must equal the requested unsigned D1 inventory hash exactly. No nearby item,
name, timestamp, or database version is substituted.
"""
from __future__ import annotations
import argparse,hashlib,json,time,urllib.error,urllib.parse,urllib.request
from pathlib import Path

UA='d1-reversal-evidence/1.0 (+https://github.com/lizardpeter/destiny-1)'
KEYWORDS=('ArmoryDetailPage.model','defaultArmor','gearAndDefaultArmor')

def req(url:str,timeout:int=90):
    r=urllib.request.Request(url,headers={'User-Agent':UA,'Accept':'*/*'})
    try:
        with urllib.request.urlopen(r,timeout=timeout) as x:
            return int(getattr(x,'status',200)),dict(x.headers.items()),x.read()
    except urllib.error.HTTPError as e:
        return int(e.code),dict(e.headers.items()),e.read()

def exact_item_url(url:str,item:int)->bool:
    u=urllib.parse.urlsplit(url)
    if u.netloc.lower() not in ('www.bungie.net','bungie.net'): return False
    if u.path.lower()!='/en/armory/detail': return False
    q=urllib.parse.parse_qs(u.query,keep_blank_values=True)
    return q.get('item')==[str(item)]

def snippets(text:str,radius:int=700):
    out=[]
    low=text.lower()
    for kw in KEYWORDS:
        start=0
        while True:
            i=low.find(kw.lower(),start)
            if i<0: break
            a=max(0,i-radius); b=min(len(text),i+len(kw)+radius)
            out.append({'keyword':kw,'offset':i,'text':text[a:b]})
            start=i+len(kw)
            if len(out)>=20: return out
    return out

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--item',required=True,type=int); ap.add_argument('--name',default=''); ap.add_argument('-o','--out-dir',type=Path,required=True); ap.add_argument('--attempts',type=int,default=8); a=ap.parse_args()
    a.out_dir.mkdir(parents=True,exist_ok=True)
    prefix=f'https://www.bungie.net/en/Armory/Detail?type=item&item={a.item}'
    params={'url':prefix,'matchType':'prefix','output':'json','fl':'timestamp,original,statuscode,digest,length,mimetype','filter':'statuscode:200','collapse':'digest'}
    cdx='https://web.archive.org/cdx/search/cdx?'+urllib.parse.urlencode(params)
    status,headers,body=req(cdx)
    report={'schema':'d1_wayback_armory_page_probe/v1','item':a.item,'name':a.name,'prefix':prefix,'cdx_url':cdx,'cdx_status':status,'captures':[],'selected':None,'snippets':[]}
    (a.out_dir/'cdx_response.bin').write_bytes(body)
    if status!=200:
        (a.out_dir/'report.json').write_text(json.dumps(report,indent=2)+'\n'); print(json.dumps(report,indent=2)); return 0
    try: rows=json.loads(body.decode('utf-8-sig'))
    except Exception as e:
        report['cdx_parse_error']=repr(e); (a.out_dir/'report.json').write_text(json.dumps(report,indent=2)+'\n'); print(json.dumps(report,indent=2)); return 0
    if not rows:
        (a.out_dir/'report.json').write_text(json.dumps(report,indent=2)+'\n'); print(json.dumps(report,indent=2)); return 0
    hdr=rows[0]; candidates=[]
    for row in rows[1:]:
        d=dict(zip(hdr,row))
        if exact_item_url(d.get('original',''),a.item): candidates.append(d)
    candidates.sort(key=lambda x:x.get('timestamp',''),reverse=True)
    report['capture_count']=len(candidates); report['captures']=candidates[:100]
    for n,c in enumerate(candidates[:max(1,a.attempts)]):
        replay=f"https://web.archive.org/web/{c['timestamp']}id_/{c['original']}"
        st,hh,bb=req(replay)
        attempt={'timestamp':c['timestamp'],'original':c['original'],'replay':replay,'http_status':st,'bytes':len(bb),'sha256':hashlib.sha256(bb).hexdigest(),'content_type':hh.get('Content-Type')}
        report.setdefault('attempts',[]).append(attempt)
        if st!=200: time.sleep(.5); continue
        p=a.out_dir/f"capture_{c['timestamp']}.html"; p.write_bytes(bb)
        text=bb.decode('utf-8',errors='replace'); ss=snippets(text)
        if report['selected'] is None or ss:
            report['selected']=attempt; report['snippets']=ss; report['selected_file']=p.name
        if ss: break
        time.sleep(.5)
    (a.out_dir/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    return 0
if __name__=='__main__': raise SystemExit(main())
