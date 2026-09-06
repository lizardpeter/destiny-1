#!/usr/bin/env python3
"""Recover an exact retired D1 Bungie URL from the Internet Archive CDX index.

The tool never substitutes a nearby filename or content version. It queries CDX for
exact captures of the supplied original URL, records every returned timestamp/digest,
and optionally downloads one exact capture using the `id_` replay form so archived
bytes are not rewritten by the Wayback toolbar.
"""
from __future__ import annotations
import argparse,hashlib,json,urllib.error,urllib.parse,urllib.request
from pathlib import Path

UA='d1-reversal-evidence/1.0 (+https://github.com/lizardpeter/destiny-1)'

def request(url:str, timeout:int=90)->tuple[int,dict,bytes]:
    req=urllib.request.Request(url,headers={'User-Agent':UA,'Accept':'*/*'})
    try:
        with urllib.request.urlopen(req,timeout=timeout) as r:
            return int(getattr(r,'status',200)),dict(r.headers.items()),r.read()
    except urllib.error.HTTPError as e:
        return int(e.code),dict(e.headers.items()),e.read()


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--url',required=True)
    ap.add_argument('--output-report',type=Path,required=True)
    ap.add_argument('--output-payload',type=Path)
    ap.add_argument('--timestamp',help='optional exact capture timestamp; otherwise latest exact 200 capture')
    a=ap.parse_args()

    q=urllib.parse.urlencode({
        'url':a.url,'output':'json','filter':'statuscode:200',
        'fl':'timestamp,original,statuscode,digest,length,mimetype','collapse':'digest'
    })
    cdx=f'https://web.archive.org/cdx/search/cdx?{q}'
    status,headers,body=request(cdx)
    captures=[]; parse_error=None
    if status==200:
        try:
            j=json.loads(body.decode('utf-8-sig'))
            if j:
                hdr=j[0]
                for row in j[1:]: captures.append(dict(zip(hdr,row)))
        except Exception as ex: parse_error=repr(ex)
    chosen=None
    if captures:
        if a.timestamp:
            chosen=next((x for x in captures if x.get('timestamp')==a.timestamp),None)
        else:
            chosen=sorted(captures,key=lambda x:x.get('timestamp',''))[-1]
    replay_status=None; replay_headers={}; payload=b''; replay_url=None
    if chosen:
        replay_url=f"https://web.archive.org/web/{chosen['timestamp']}id_/{chosen['original']}"
        replay_status,replay_headers,payload=request(replay_url,timeout=180)
        if replay_status==200 and a.output_payload:
            a.output_payload.parent.mkdir(parents=True,exist_ok=True); a.output_payload.write_bytes(payload)

    rep={
      'schema':'d1_wayback_exact_recover/v1','requested_url':a.url,
      'cdx_url':cdx,'cdx_status':status,'cdx_response_sha256':hashlib.sha256(body).hexdigest(),
      'cdx_parse_error':parse_error,'capture_count':len(captures),'captures':captures,
      'chosen_capture':chosen,'replay_url':replay_url,'replay_status':replay_status,
      'replay_sha256':hashlib.sha256(payload).hexdigest() if payload else None,
      'replay_size':len(payload),'replay_content_type':replay_headers.get('Content-Type'),
      'policy':'Only an exact CDX capture of the requested URL is accepted. No filename/version fallback is inferred.'
    }
    a.output_report.parent.mkdir(parents=True,exist_ok=True); a.output_report.write_text(json.dumps(rep,indent=2)+'\n')
    print('CDX',status,'captures',len(captures),'chosen',chosen,'replay',replay_status,'bytes',len(payload))
    return 0 if replay_status==200 else 3

if __name__=='__main__': raise SystemExit(main())
