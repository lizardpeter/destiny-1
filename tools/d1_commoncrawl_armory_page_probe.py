#!/usr/bin/env python3
"""Recover exact historical Bungie D1 Armory pages from Common Crawl.

This is a second archive path for the server-rendered Armory model that supplied
`defaultArmor` / `gearAndDefaultArmor` to Bungie's D1 ItemPreview client.

The probe is fail closed:
* index collections are discovered from Common Crawl's own collinfo endpoint;
* only collections whose id year falls inside --start-year/--end-year are queried;
* every candidate record must parse back to the exact requested unsigned item id;
* WARC records are fetched by the exact index filename/offset/length tuple;
* no nearby item, page, timestamp, or asset database is substituted.

Index lookups are independent and therefore executed concurrently. This avoids a
single slow historical Common Crawl shard serially consuming the entire CI budget.
"""
from __future__ import annotations
import argparse,concurrent.futures,gzip,hashlib,json,re,socket,time,urllib.error,urllib.parse,urllib.request
from pathlib import Path

UA='d1-reversal-evidence/1.0 (+https://github.com/lizardpeter/destiny-1)'
KEYWORDS=('ArmoryDetailPage.model','defaultArmor','gearAndDefaultArmor')

def req(url:str, *, timeout:int=12, headers:dict|None=None):
    h={'User-Agent':UA,'Accept':'*/*'}
    if headers: h.update(headers)
    r=urllib.request.Request(url,headers=h)
    try:
        with urllib.request.urlopen(r,timeout=timeout) as x:
            return int(getattr(x,'status',200)),dict(x.headers.items()),x.read(),None
    except urllib.error.HTTPError as e:
        return int(e.code),dict(e.headers.items()),e.read(),f'HTTPError:{e.code}'
    except (urllib.error.URLError,TimeoutError,socket.timeout,OSError) as e:
        return 0,{},b'',f'{type(e).__name__}:{e}'

def parse_item(url:str):
    try:
        u=urllib.parse.urlsplit(url); q=urllib.parse.parse_qs(u.query,keep_blank_values=True); vals=q.get('item')
        return int(vals[0]) if vals and len(vals)==1 and vals[0].isdigit() else None
    except Exception: return None

def armory_path(url:str)->bool:
    try: return urllib.parse.urlsplit(url).path.lower()=='/en/armory/detail'
    except Exception: return False

def snippets(text:str,radius:int=1200):
    out=[]; low=text.lower()
    for kw in KEYWORDS:
        start=0
        while True:
            i=low.find(kw.lower(),start)
            if i<0: break
            aa=max(0,i-radius); bb=min(len(text),i+len(kw)+radius); out.append({'keyword':kw,'offset':i,'text':text[aa:bb]}); start=i+len(kw)
            if len(out)>=30: return out
    return out

def collection_year(cid:str):
    m=re.search(r'CC-MAIN-(20\d\d)-',cid); return int(m.group(1)) if m else None

def index_query(api:str,url_prefix:str):
    sep='&' if '?' in api else '?'; q=urllib.parse.urlencode({'url':url_prefix,'output':'json','matchType':'prefix','filter':'status:200'})
    st,hh,bb,err=req(api+sep+q); rows=[]
    if st==200:
        for line in bb.decode('utf-8',errors='replace').splitlines():
            line=line.strip()
            if not line: continue
            try: rows.append(json.loads(line))
            except Exception: pass
    return st,err,rows,len(bb)

def decode_warc_block(raw:bytes):
    try: data=gzip.decompress(raw)
    except Exception: data=raw
    p=data.find(b'\r\n\r\n')
    if p<0: p=data.find(b'\n\n')
    if p<0: return data
    payload=data[p+4:] if data[p:p+4]==b'\r\n\r\n' else data[p+2:]
    if payload.startswith(b'HTTP/'):
        q=payload.find(b'\r\n\r\n')
        if q<0: q=payload.find(b'\n\n')
        if q>=0: payload=payload[q+(4 if payload[q:q+4]==b'\r\n\r\n' else 2):]
    return payload

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--item',type=int,required=True); ap.add_argument('--name',default=''); ap.add_argument('--start-year',type=int,default=2015); ap.add_argument('--end-year',type=int,default=2017)
    ap.add_argument('--max-collections',type=int,default=60); ap.add_argument('--max-records',type=int,default=20); ap.add_argument('--workers',type=int,default=16); ap.add_argument('-o','--out-dir',type=Path,required=True); a=ap.parse_args()
    a.out_dir.mkdir(parents=True,exist_ok=True)
    st,hh,bb,err=req('https://index.commoncrawl.org/collinfo.json')
    report={'schema':'d1_commoncrawl_armory_page_probe/v2','item':a.item,'name':a.name,'years':[a.start_year,a.end_year],'collinfo_status':st,'collinfo_error':err,
            'index_queries':[],'candidates':[],'records':[],'selected':None,'snippets':[],'workers':a.workers,'policy':'Only exact requested item-id Armory captures are accepted.'}
    (a.out_dir/'collinfo.json').write_bytes(bb)
    if st!=200:
        (a.out_dir/'report.json').write_text(json.dumps(report,indent=2)+'\n'); print(json.dumps(report,indent=2)); return 0
    cols=json.loads(bb.decode('utf-8-sig')); cols=[c for c in cols if (collection_year(c.get('id','')) is not None and a.start_year<=collection_year(c['id'])<=a.end_year)][:a.max_collections]
    prefixes=[f'www.bungie.net/en/Armory/Detail?type=item&item={a.item}',f'bungie.net/en/Armory/Detail?type=item&item={a.item}',f'www.bungie.net/en/Armory/Detail?item={a.item}',f'bungie.net/en/Armory/Detail?item={a.item}']
    tasks=[]
    for c in cols:
        api=c.get('cdx-api') or c.get('index')
        if api:
            for prefix in prefixes: tasks.append((c['id'],api,prefix))
    def work(t):
        cid,api,prefix=t; qs,qe,rows,nbytes=index_query(api,prefix)
        return {'collection':cid,'api':api,'prefix':prefix,'status':qs,'error':qe,'response_bytes':nbytes,'row_count':len(rows)},rows
    results=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1,a.workers)) as ex:
        futs=[ex.submit(work,t) for t in tasks]
        for fut in concurrent.futures.as_completed(futs): results.append(fut.result())
    results.sort(key=lambda x:(x[0]['collection'],x[0]['prefix']))
    seen=set(); candidates=[]
    for qrec,rows in results:
        report['index_queries'].append(qrec)
        for row in rows:
            u=row.get('url','')
            if not armory_path(u) or parse_item(u)!=a.item: continue
            key=(row.get('filename'),str(row.get('offset')),str(row.get('length')))
            if key in seen: continue
            seen.add(key); row=dict(row); row['collection']=qrec['collection']; candidates.append(row)
    candidates.sort(key=lambda x:x.get('timestamp',''),reverse=True); report['candidates']=candidates[:200]; report['candidate_count']=len(candidates)
    for ri,row in enumerate(candidates[:a.max_records]):
        try: off=int(row['offset']); ln=int(row['length']); fn=row['filename']
        except Exception as e: report['records'].append({'candidate':row,'error':f'bad index tuple:{e}'}); continue
        url='https://data.commoncrawl.org/'+fn; rs,rh,rb,re_=req(url,headers={'Range':f'bytes={off}-{off+ln-1}'})
        rec={'collection':row['collection'],'timestamp':row.get('timestamp'),'url':row.get('url'),'filename':fn,'offset':off,'length':ln,'http_status':rs,'transport_error':re_,'fetched_bytes':len(rb),'sha256':hashlib.sha256(rb).hexdigest()}; report['records'].append(rec)
        if rs not in (200,206): continue
        body=decode_warc_block(rb); text=body.decode('utf-8',errors='replace'); ss=snippets(text); p=a.out_dir/f"capture_{ri:02d}_{row.get('timestamp','unknown')}.html"; p.write_bytes(body)
        rec['decoded_body_bytes']=len(body); rec['decoded_body_sha256']=hashlib.sha256(body).hexdigest(); rec['snippet_keywords']=[x['keyword'] for x in ss]
        if report['selected'] is None or ss: report['selected']=rec; report['selected_file']=p.name; report['snippets']=ss
        if ss: break
    (a.out_dir/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'item':a.item,'name':a.name,'collections':len(cols),'index_queries':len(report['index_queries']),'candidate_count':report.get('candidate_count',0),'selected':report['selected'],
                      'snippet_keywords':[x['keyword'] for x in report['snippets']],'index_transport_failures':sum(1 for q in report['index_queries'] if q['status']!=200)},indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
