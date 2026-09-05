#!/usr/bin/env python3
"""Bulk-census D1 PS4 textures without letting one bad generation abort a family.

For every texture-header TagHash seen in any supplied same-family snapshot, try
snapshots newest-to-oldest. Each attempt uses the normal strict
`d1_texture_export.export_reader` for exactly one TagHash. A successful attempt
copies its portable outputs to the final directory; failures remain explicit in
the aggregate manifest.

This is for discovery/census work. It does not weaken the production exporter:
all ownership/backing rules remain those of d1_texture_export, and every chosen
snapshot plus every failed attempt is recorded.
"""
from __future__ import annotations
import argparse,json,shutil
from pathlib import Path

from d1_entry_extract import EntryReader
from d1_texture_export import export_reader


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--snapshot',type=Path,action='append',required=True,
                    help='same-family logical snapshots, newest-to-oldest')
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    a.out.mkdir(parents=True,exist_ok=True)
    attempts=a.out/'.attempts';attempts.mkdir(exist_ok=True)
    readers=[(p,EntryReader(p,a.runtime)) for p in a.snapshot]
    tags=set()
    source_presence={}
    for p,r in readers:
        for e in r.entries:
            if (e['type'],e['subtype']) in {(32,1),(32,2)}:
                h=e['tag_hash'].upper();tags.add(h);source_presence.setdefault(h,[]).append(str(p))
    resolved=[];failures=[]
    for n,tag in enumerate(sorted(tags),1):
        tag_attempts=[];accepted=None
        for p,r in readers:
            adir=attempts/tag/p.stem
            if adir.exists():shutil.rmtree(adir)
            adir.mkdir(parents=True,exist_ok=True)
            rec={'snapshot':str(p)}
            try:
                rep=export_reader(r,adir,tag_hashes=[tag],dependencies=[])
                rec['missing_requested']=rep.get('missing_requested')
                rows=rep.get('textures') or []
                if rep.get('missing_requested') or len(rows)!=1:
                    rec['reject']='tag absent or non-unique in snapshot';tag_attempts.append(rec);continue
                row=rows[0];rec['texture']=row
                portable=[]
                for key in ('dds','png'):
                    fn=row.get(key)
                    if fn and (adir/fn).is_file():shutil.copy2(adir/fn,a.out/fn);portable.append(fn)
                for key in ('face_dds','face_pngs'):
                    for fn in row.get(key) or []:
                        if (adir/fn).is_file():shutil.copy2(adir/fn,a.out/fn);portable.append(fn)
                # A resolved census row needs at least one portable image/data output and no backing error.
                if not portable or row.get('error'):
                    rec['reject']=row.get('error') or 'no portable output';tag_attempts.append(rec);continue
                rec['accepted']=True;rec['portable_files']=portable;tag_attempts.append(rec)
                accepted={'tag_hash':tag,'chosen_snapshot':str(p),'texture':row,'portable_files':portable,'attempts':tag_attempts}
                break
            except Exception as ex:
                rec['error']=repr(ex);tag_attempts.append(rec)
        if accepted:resolved.append(accepted)
        else:failures.append({'tag_hash':tag,'present_in':source_presence.get(tag,[]),'attempts':tag_attempts})
        if n%50==0:print(f'textures {n}/{len(tags)} resolved={len(resolved)} failed={len(failures)}',flush=True)
    # Remove bulky attempt trees after provenance has been serialized.
    shutil.rmtree(attempts,ignore_errors=True)
    out={'mode':'tolerant generation-safe family texture census','snapshots_newest_to_oldest':[str(p) for p in a.snapshot],
         'unique_texture_header_count':len(tags),'resolved_count':len(resolved),'failed_count':len(failures),
         'textures':resolved,'failures':failures}
    (a.out/'texture_manifest.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ('textures','failures')},indent=2))
    return 0
if __name__=='__main__':raise SystemExit(main())
