#!/usr/bin/env python3
"""Decode one exact D1 ROI runtime-rig EntityResource through verified remote catalogs.

Runtime-rig identity is accepted only when the outer EntityResource resolves the
validated class pair 808008B2 -> 8080099B.  Detailed decoding is delegated to the
pinned tiger-animation-parser supplied by --parser-root.  All mapping arrays are
preserved so skeleton compatibility can be tested by bone hash rather than guessed
from node counts or adjacency.
"""
from __future__ import annotations
import argparse, dataclasses, io, json, sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))

from d1_character_family_census import RUNTIME_RIG_DISCRIMINATOR,RUNTIME_RIG_INFO
from d1_entity_resource_probe import parse_resource
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_model_tgxm_signature_match import LazyExactHashResolver
from d1_split_tar_extract import SplitHttpTar


def norm(s:str)->str:return s.upper().removeprefix('0X').zfill(8)

def simple(v):
    if v is None or isinstance(v,(bool,int,float,str)): return v
    if isinstance(v,bytes): return {'bytes_hex':v.hex(),'byte_count':len(v)}
    if dataclasses.is_dataclass(v): return {k:simple(x) for k,x in dataclasses.asdict(v).items()}
    if isinstance(v,dict): return {str(k):simple(x) for k,x in v.items()}
    if isinstance(v,(list,tuple)): return [simple(x) for x in v]
    try:
        return [simple(x) for x in v]
    except Exception:
        pass
    d=getattr(v,'__dict__',None)
    if isinstance(d,dict): return {str(k):simple(x) for k,x in d.items() if not str(k).startswith('_')}
    try:return int(v)
    except Exception:return str(v)

def seq(v):
    if v is None:return []
    try:return list(v)
    except Exception:return []

def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument('--rig-resource',required=True)
    ap.add_argument('--member-catalog',type=Path,action='append',required=True)
    ap.add_argument('--base-url',required=True);ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('--parser-root',type=Path,required=True)
    ap.add_argument('-o','--output',type=Path,required=True);a=ap.parse_args()
    h=norm(a.rig_resource);cats=load_catalogs(a.member_catalog)
    arc=SplitHttpTar([f"{a.base_url.rstrip('/')}/packages.tar.{i:03d}" for i in range(1,a.part_count+1)],retries=6,timeout=90)
    resolver=LazyExactHashResolver(arc,cats,a.runtime);_v,e,b=resolver.bytes(h)
    outer=parse_resource(b,'PS4');u10=(outer.get('unk10') or {}).get('class_hash');u18=(outer.get('unk18') or {}).get('class_hash')
    if (u10,u18)!=(RUNTIME_RIG_DISCRIMINATOR,RUNTIME_RIG_INFO):
        raise ValueError(f'{h}: not validated runtime-rig pair: {u10}->{u18}')
    sys.path.insert(0,str(a.parser_root.resolve()))
    from tag.game_version import Game_Version
    from tag_readers.read_rig import read_runtime_rig
    rig=read_runtime_rig(io.BytesIO(b),Game_Version.D1_ROI)
    fields={}
    for name in ('bone_to_control','control_to_bone','rig_components','control_name_to_bone_index','controls_relations','controls_transforms'):
        if hasattr(rig,name):fields[name]=simple(seq(getattr(rig,name)))
    comps=[]
    for x in seq(getattr(rig,'rig_components',[])):
        hv=getattr(x,'hash',None);ct=getattr(x,'count',None)
        comps.append({'hash':f'{int(hv)&0xffffffff:08X}' if hv is not None else None,'count':int(ct) if ct is not None else None})
    rep={'schema':'d1_remote_runtime_rig_probe/v1','rig_resource_tag_hash':h,'entry_index':int(e['index']),'entry_size':int(e['file_size']),
         'discriminator_class':u10,'info_class':u18,'control_count':len(seq(getattr(rig,'controls_relations',[]))),
         'runtime_rig_components':comps,'decoded_fields':fields,'entity_resource':outer,
         'policy':'The requested exact FileHash is promoted as a runtime rig only from class pair 808008B2->8080099B. Mapping arrays come directly from the pinned D1 ROI parser; no skeleton identity or control semantic is inferred.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(rep,indent=2)+'\n')
    print('RUNTIME_RIG',h,'CONTROLS',rep['control_count'],'COMPONENTS',comps)
    print('BONE_TO_CONTROL',fields.get('bone_to_control'))
    print('CONTROL_TO_BONE',fields.get('control_to_bone'))
    return 0
if __name__=='__main__':raise SystemExit(main())
