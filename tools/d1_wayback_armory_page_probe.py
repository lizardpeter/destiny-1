#!/usr/bin/env python3
"""Discover and recover archived D1 Bungie Armory pages for one exact item id.

CDX prefix queries are used only to discover historical URL spellings/encodings.
Every returned capture is then filtered by parsed query parameters so `item` must
equal the requested unsigned D1 inventory hash exactly. No nearby item, name,
timestamp, or database version is substituted.
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
    out=[]; low=text.lower()
    for kw in KEYWORDS:
        start=0
        while True:
            i=low.find(kw.lower(),start)
            if i<0: break
            aa=max(0,i-radius); bb=min(len(text),i+len(kw)+radius)
            out.append({'keyword':kw,'offset':i,'text':text[aa:bb]}); start=i+len(kw)
            if len(out)>=20: return out
    return out

def cdx_query(prefix:str):
    params={'url':prefix,'matchType':'prefix','output':'json','fl':'timestamp,original,statuscode,digest,length,mimetype','filter':'statuscode:200','collapse':'digest'}
    url='https://web.archive.org/cdx/search/cdx?'+urllib.parse.urlencode(params)
    st,hh,bb=req(url)
    return url,st,bb

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--item',required=True,type=int); ap.add_argument('--name',default=''); ap.add_argument('-o','--out-dir',type=Path,required=True); ap.add_argument('--attempts',type=int,default=12); a=ap.parse_args()
    a.out_dir.mkdir(parents=True,exist_ok=True)
    # Historical public links exist in both forms below; HTTP/HTTPS and www/non-www
    # are queried separately. Discovery is broad, acceptance remains exact by parsed item id.
    prefixes=[]
    for scheme in ('https','http'):
        for host in ('www.bungie.net','bungie.net'):
            prefixes += [
                f'{scheme}://{host}/en/Armory/Detail?type=item&item={a.item}',
                f'{scheme}://{host}/en/Armory/Detail?item={a.item}',
            ]
    report={'schema':'d1_wayback_armory_page_probe/v2','item':a.item,'name':a.name,'prefixes':prefixes,'cdx_queries':[],'captures':[],'selected':None,'snippets':[]}
    candidates=[]; seen=set()
    for qi,prefix in enumerate(prefixes):
        url,st,body=cdx_query(prefix)
        (a.out_dir/f'cdx_response_{qi}.bin').write_bytes(body)
        qrec={'prefix':prefix,'cdx_url':url,'status':st,'bytes':len(body)}; report['cdx_queries'].append(qrec)
        if st!=200: continue
        try: rows=json.loads(body.decode('utf-8-sig'))
        except Exception as e: qrec['parse_error']=repr(e); continue
        if not rows: continue
        hdr=rows[0]
        for row in rows[1:]:
            d=dict(zip(hdr,row)); orig=d.get('original','')
            if not exact_item_url(orig,a.item): continue
            key=(d.get('timestamp'),orig,d.get('digest'))
            if key in seen: continue
            seen.add(key); candidates.append(d)
    candidates.sort(key=lambda x:x.get('timestamp',''),reverse=True)
    report['capture_count']=len(candidates); report['captures']=candidates[:200]
    for c in candidates[:max(1,a.attempts)]:
        replay=f"https://web.archive.org/web/{c['timestamp']}id_/{c['original']}"
        st,hh,bb=req(replay)
        attempt={'timestamp':c['timestamp'],'original':c['original'],'replay':replay,'http_status':st,'bytes':len(bb),'sha256':hashlib.sha256(bb).hexdigest(),'content_type':hh.get('Content-Type')}
        report.setdefault('attempts',[]).append(attempt)
        if st!=200: time.sleep(.3); continue
        p=a.out_dir/f"capture_{c['timestamp']}.html"; p.write_bytes(bb)
        text=bb.decode('utf-8',errors='replace'); ss=snippets(text)
        if report['selected'] is None or ss:
            report['selected']=attempt; report['snippets']=ss; report['selected_file']=p.name
        if ss: break
        time.sleep(.3)
    (a.out_dir/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'item':a.item,'name':a.name,'capture_count':report['capture_count'],'selected':report['selected'],'snippet_keywords':[x['keyword'] for x in report['snippets']],'cdx_statuses':[x['status'] for x in report['cdx_queries']]},indent=2))
    return 0
if __name__=='__main__': raise SystemExit(main())
