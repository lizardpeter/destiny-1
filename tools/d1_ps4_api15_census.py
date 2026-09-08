#!/usr/bin/env python3
"""Build a PS4-native census of ImmConstBuffer API15 usage.

Consumes reports from d1_gcn_constant_buffer_usage_analyze.py. The census is
mechanical and fail-closed: it records every shader row declaring/using API15,
including dynamic scalar-buffer offsets. It assigns no engine-level semantic.
"""
from __future__ import annotations
import argparse, json
from collections import Counter
from pathlib import Path


def named_path(raw: str) -> tuple[str, Path]:
    if '=' not in raw:
        raise argparse.ArgumentTypeError('expected NAME=PATH')
    n,p=raw.split('=',1)
    if not n.strip(): raise argparse.ArgumentTypeError('empty name')
    return n.strip(),Path(p)


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--input',action='append',required=True,type=named_path)
    ap.add_argument('--disasm',action='append',default=[],type=named_path)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args(); ddirs=dict(a.disasm); violations=[]; rows=[]; shaders=set(); offhist=Counter(); dyn=0
    for corpus,path in a.input:
        doc=json.loads(path.read_text())
        if doc.get('status')!='D1_GCN_CONSTANT_BUFFER_USAGE_ANALYZED':
            violations.append(f'{corpus}:bad_status:{doc.get("status")}')
        for sh in doc.get('shaders',[]):
            h=str(sh.get('shader','')).upper()
            if not h: violations.append(f'{corpus}:missing_shader'); continue
            hits=[]
            for ld in sh.get('loads',[]):
                cb=ld.get('constant_buffer')
                if not cb or int(cb.get('api_slot',-1))!=15: continue
                r={
                    'line_number':ld.get('line_number'),'line':ld.get('line'),
                    'descriptor_start_register':ld.get('descriptor_start_register'),
                    'width_dwords':int(ld.get('width_dwords') or 1),
                    'offset_operand':ld.get('offset_operand'),'static_offset':ld.get('static_offset'),
                }
                if r['static_offset'] is None: dyn+=1
                else:
                    for i in range(r['width_dwords']): offhist[str(int(r['static_offset'])+i)]+=1
                ddir=ddirs.get(corpus)
                if ddir and r['line_number']:
                    p=ddir/f'PS_{h}.s'
                    if p.exists():
                        lines=p.read_text(errors='replace').splitlines(); ln=int(r['line_number'])
                        r['context']=lines[max(0,ln-6):min(len(lines),ln+5)]
                hits.append(r)
            declared=[x for x in sh.get('imm_constant_buffers',[]) if int(x.get('api_slot',-1))==15]
            if declared or hits:
                shaders.add(h); rows.append({'corpus':corpus,'shader':h,'api15_declarations':declared,'api15_loads':hits,'api15_load_count':len(hits)})
    out={
        'schema_version':1,
        'status':'D1_PS4_API15_CENSUS_COMPLETE' if not violations else 'D1_PS4_API15_CENSUS_PARTIAL',
        'corpora':[n for n,_ in a.input],
        'api15_shader_count':len(shaders),'api15_shaders':sorted(shaders),
        'api15_row_count':len(rows),'api15_static_dword_histogram':dict(sorted(offhist.items(),key=lambda x:int(x[0]))),
        'api15_dynamic_load_count':dyn,'rows':rows,'violations':violations,
        'policy':'PS4 OrbShdr declaration plus native GCN scalar-buffer usage only; no producer name or runtime value inferred.'
    }
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ['status','corpora','api15_shader_count','api15_shaders','api15_static_dword_histogram','api15_dynamic_load_count','violations']},indent=2))
    return 0 if not violations else 2

if __name__=='__main__': raise SystemExit(main())
