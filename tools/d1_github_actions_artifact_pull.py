#!/usr/bin/env python3
"""Fail-closed GitHub Actions artifact resolver/downloader.

Given a repository, workflow run id and exact artifact name:
* lists that run's artifacts through the GitHub REST API;
* selects exactly one non-expired artifact of that name;
* downloads its ZIP through the API;
* verifies the GitHub-reported sha256 digest when present;
* rejects ZIP path traversal and extracts into the requested directory;
* emits optional provenance JSON.

Designed for source-closure workflows that must not silently fall back to an expired
historical artifact or a same-named artifact from another run.
"""
from __future__ import annotations
import argparse,hashlib,json,os,shutil,sys,tempfile,urllib.error,urllib.parse,urllib.request,zipfile
from pathlib import Path

API='https://api.github.com'
UA='d1-source-closure-artifact-pull/1'

class StripCrossOriginAuthorization(urllib.request.HTTPRedirectHandler):
    """Follow GitHub's signed blob redirect without leaking GitHub auth to Azure."""
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        nxt=super().redirect_request(req,fp,code,msg,headers,newurl)
        if nxt is None:return None
        old=urllib.parse.urlsplit(req.full_url)
        new=urllib.parse.urlsplit(newurl)
        if (old.scheme.lower(),old.netloc.lower()) != (new.scheme.lower(),new.netloc.lower()):
            # urllib copies request headers onto redirects. The Actions artifact API
            # returns a signed Azure URL; forwarding "Authorization: Bearer ..." to
            # that host causes InvalidAuthenticationInfo and is also unnecessary.
            nxt.remove_header('Authorization')
            nxt.headers.pop('Authorization',None)
            nxt.unredirected_hdrs.pop('Authorization',None)
        return nxt

OPENER=urllib.request.build_opener(StripCrossOriginAuthorization())

def request(url,token):
    headers={'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28','User-Agent':UA}
    if token:headers['Authorization']=f'Bearer {token}'
    return urllib.request.Request(url,headers=headers)

def get_json(url,token):
    with OPENER.open(request(url,token),timeout=60) as r:
        return json.load(r)

def safe_extract(zf:zipfile.ZipFile,dst:Path):
    root=dst.resolve()
    names=[]
    for info in zf.infolist():
        p=(root/info.filename).resolve()
        try:p.relative_to(root)
        except ValueError:raise RuntimeError(f'unsafe artifact zip path: {info.filename}')
        names.append(info.filename)
    zf.extractall(root)
    return names

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--repo',required=True,help='owner/repo')
    ap.add_argument('--run-id',required=True,type=int)
    ap.add_argument('--artifact-name',required=True)
    ap.add_argument('--out-dir',type=Path,required=True)
    ap.add_argument('--report',type=Path)
    ap.add_argument('--token-env',default='GH_TOKEN')
    ap.add_argument('--clean',action='store_true')
    a=ap.parse_args()
    token=os.environ.get(a.token_env,'')
    if not token:raise SystemExit(f'missing token environment variable {a.token_env}')

    all_rows=[];page=1
    while True:
        url=f'{API}/repos/{a.repo}/actions/runs/{a.run_id}/artifacts?per_page=100&page={page}'
        d=get_json(url,token)
        rows=d.get('artifacts') or [];all_rows.extend(rows)
        if len(rows)<100:break
        page+=1
        if page>100:raise SystemExit('artifact pagination runaway')

    named=[x for x in all_rows if x.get('name')==a.artifact_name]
    live=[x for x in named if not bool(x.get('expired'))]
    if len(live)!=1:
        raise SystemExit(json.dumps({
            'error':'expected exactly one live exact-name artifact',
            'repo':a.repo,'run_id':a.run_id,'artifact_name':a.artifact_name,
            'matching_artifact_count':len(named),'live_matching_artifact_count':len(live),
            'matches':[{'id':x.get('id'),'expired':x.get('expired'),'created_at':x.get('created_at'),'digest':x.get('digest')} for x in named],
        },indent=2))
    art=live[0];aid=int(art['id'])
    archive_url=f'{API}/repos/{a.repo}/actions/artifacts/{aid}/zip'

    a.out_dir.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='d1_artifact_pull_') as td:
        zp=Path(td)/'artifact.zip'
        h=hashlib.sha256();size=0
        try:
            with OPENER.open(request(archive_url,token),timeout=180) as r,zp.open('wb') as f:
                while True:
                    b=r.read(1024*1024)
                    if not b:break
                    f.write(b);h.update(b);size+=len(b)
        except urllib.error.HTTPError as ex:
            body=ex.read().decode('utf-8','replace')
            raise SystemExit(f'artifact download HTTP {ex.code}: {body[:2000]}')
        got=h.hexdigest()
        declared=str(art.get('digest') or '')
        if declared:
            if not declared.startswith('sha256:'):raise SystemExit(f'unsupported artifact digest {declared!r}')
            expected=declared.split(':',1)[1].lower()
            if got!=expected:raise SystemExit(f'artifact digest mismatch: {got} != {expected}')

        if a.clean and a.out_dir.exists():shutil.rmtree(a.out_dir)
        a.out_dir.mkdir(parents=True,exist_ok=True)
        try:
            with zipfile.ZipFile(zp) as zf:names=safe_extract(zf,a.out_dir)
        except zipfile.BadZipFile as ex:raise SystemExit(f'bad artifact zip: {ex}')

    out={
        'schema':'d1_github_actions_artifact_pull/v1',
        'status':'D1_GITHUB_ACTIONS_ARTIFACT_PULL_EXACT',
        'repository':a.repo,'run_id':a.run_id,'artifact_name':a.artifact_name,
        'artifact_id':aid,'artifact_created_at':art.get('created_at'),'artifact_expires_at':art.get('expires_at'),
        'artifact_size_in_bytes_api':art.get('size_in_bytes'),'artifact_digest_api':declared or None,
        'downloaded_zip_bytes':size,'downloaded_zip_sha256':got,
        'extracted_file_count':len(names),'extracted_files':sorted(names),
    }
    if a.report:
        a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ('status','repository','run_id','artifact_name','artifact_id','downloaded_zip_bytes','downloaded_zip_sha256','extracted_file_count')},indent=2))
    return 0

if __name__=='__main__':raise SystemExit(main())
