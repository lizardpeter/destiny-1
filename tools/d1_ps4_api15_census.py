#!/usr/bin/env python3
"""Build a PS4-native census of ImmConstBuffer API15 usage.

Consumes reports from d1_gcn_constant_buffer_usage_analyze.py. The generic
analyzer maps direct descriptor SGPRs only; spilled user-data descriptors are
still visible as exact OrbShdr declarations but require a dedicated spill proof.
This census therefore keeps declaration coverage and directly mapped loads as
separate facts and assigns no engine-level semantic.
"""
from __future__ import annotations
import argparse, json
from collections import Counter
from pathlib import Path


def named_path(raw: str) -> tuple[str, Path]:
    if '=' not in raw: raise argparse.ArgumentTypeError('expected NAME=PATH')
    n,p=raw.split('=',1)
    if not n.strip(): raise argparse.ArgumentTypeError('empty name')
    return n.strip(),Path(p)


def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument('--input',action='append',required=True,type=named_path); ap.add_argument('--disasm',action='append',default=[],type=named_path); ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args(); ddirs=dict(a.disasm); violations=[]; rows=[]; shaders=set(); all_shaders=set(); offhist=Counter(); dyn=0; mapped=0; shader_rows=0
    for corpus,path in a.input:
        doc=json.loads(path.read_text())
        if doc.get('status')!='D1_GCN_CONSTANT_BUFFER_USAGE_ANALYZED': violations.append(f'{corpus}:bad_status:{doc.get("status")}')
        for sh in doc.get('shaders',[]):
            shader_rows+=1; h=str(sh.get('shader','')).upper()
            if not h: violations.append(f'{corpus}:missing_shader'); continue
            all_shaders.add(h); hits=[]
            for ld in sh.get('loads',[]):
                cb=ld.get('constant_buffer')
                if not cb or int(cb.get('api_slot',-1))!=15: continue
                mapped+=1
                r={'line_number':ld.get('line_number'),'line':ld.get('line'),'descriptor_start_register':ld.get('descriptor_start_register'),'width_dwords':int(ld.get('width_dwords') or 1),'offset_operand':ld.get('offset_operand'),'static_offset':ld.get('static_offset')}
                if r['static_offset'] is None: dyn+=1
                else:
                    for i in range(r['width_dwords']): offhist[str(int(r['static_offset'])+i)]+=1
                ddir=ddirs.get(corpus)
                if ddir and r['line_number']:
                    p=ddir/f'PS_{h}.s'
                    if p.exists():
                        lines=p.read_text(errors='replace').splitlines(); ln=int(r['line_number']); r['context']=lines[max(0,ln-6):min(len(lines),ln+5)]
                hits.append(r)
            declared=[x for x in sh.get('imm_constant_buffers',[]) if int(x.get('api_slot',-1))==15]
            if declared or hits:
                shaders.add(h); rows.append({'corpus':corpus,'shader':h,'api15_declarations':declared,'api15_direct_mapped_loads':hits,'api15_direct_mapped_load_count':len(hits),'requires_spill_specific_mapping':bool(declared and not hits)})
    out={'schema_version':1,'status':'D1_PS4_API15_CENSUS_COMPLETE' if not violations else 'D1_PS4_API15_CENSUS_PARTIAL','corpora':[n for n,_ in a.input],'scanned_shader_row_count':shader_rows,'unique_shader_count':len(all_shaders),'api15_shader_count':len(shaders),'api15_shaders':sorted(shaders),'api15_row_count':len(rows),'api15_direct_mapped_load_count':mapped,'api15_direct_static_dword_histogram':dict(sorted(offhist.items(),key=lambda x:int(x[0]))),'api15_direct_dynamic_load_count':dyn,'rows':rows,'violations':violations,'policy':'PS4 OrbShdr declarations are authoritative for API15 presence. Direct GCN load mapping covers non-spilled descriptors only; spilled descriptors require a separate exact spill proof. No producer name or runtime value is inferred.'}
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ['status','corpora','scanned_shader_row_count','unique_shader_count','api15_shader_count','api15_shaders','api15_direct_mapped_load_count','violations']},indent=2)); return 0 if not violations else 2

if __name__=='__main__': raise SystemExit(main())
