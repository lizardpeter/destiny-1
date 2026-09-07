#!/usr/bin/env python3
"""Inspect D1 ROI animation codec-1 array_7 routing for exact retail clips.

Diagnostic only. This tool does not decode or patch a clip. It reopens exact 808005A1
payloads with the pinned tiger-animation-parser and records the codec headers, buffer
lengths, array_7 routing values partitioned by scale/rotation/translation streams, and
control maps. It is designed to compare clips that fail the current third-party
codec-1 decoder with successful clips from the same skeleton/runtime-rig family.
"""
from __future__ import annotations
import argparse, json, sys, tempfile
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_activity_placements import RemoteCorpus
from d1_split_tar_extract import SplitHttpTar

CLIP_REF='808005A1'

def norm(v): return str(v).upper().removeprefix('0X').zfill(8)

def filebacked(fn,payload,version):
    with tempfile.NamedTemporaryFile() as f:
        f.write(payload); f.flush(); f.seek(0); return fn(f,version)

def array_data(x):
    if x is None: return []
    d=getattr(x,'data',None)
    if d is not None:
        try: return [int(v) for v in d.tolist()]
        except Exception: return [int(v) for v in d]
    try: return [int(v) for v in x]
    except Exception: return []

def arr_len(x):
    if x is None: return 0
    d=getattr(x,'data',None)
    if d is not None:
        try: return int(len(d))
        except Exception: pass
    try: return int(len(x))
    except Exception: return int(getattr(x,'length',0) or 0)

def header_row(h):
    if h is None: return None
    out={
        'codec_type':int(h.codec_type),
        'scale_stream_count':int(h.scale_stream_count),
        'rotation_stream_count':int(h.rotation_stream_count),
        'translation_stream_count':int(h.translation_stream_count),
    }
    return out

def codec1_row(h,b):
    out={'header':header_row(h)}
    if h is None or int(h.codec_type)!=1 or b is None: return out
    names=['uncompressed_data','compressed_data','keyframe_deltas','interpolation_data','quantization_minimums','quantization_extents','array_7']
    out['buffer_lengths']={n:arr_len(getattr(b,n,None)) for n in names}
    vals=array_data(b.array_7)
    sc=int(h.scale_stream_count); ro=int(h.rotation_stream_count); tr=int(h.translation_stream_count)
    expected=sc+ro+tr
    out['array_7_length']=len(vals); out['array_7_expected_stream_count']=expected
    out['array_7_length_matches_stream_count']=len(vals)==expected
    out['array_7']={
        'scale':vals[:sc],
        'rotation':vals[sc:sc+ro],
        'translation':vals[sc+ro:sc+ro+tr],
    }
    out['zero_entries']={
        kind:[i for i,v in enumerate(seq) if v==0]
        for kind,seq in out['array_7'].items()
    }
    out['negative_entries']={
        kind:[{'index':i,'value':v} for i,v in enumerate(seq) if v<0]
        for kind,seq in out['array_7'].items()
    }
    out['positive_entry_counts']={kind:sum(v>0 for v in seq) for kind,seq in out['array_7'].items()}
    return out

def control_maps_row(cm):
    if cm is None: return None
    names=[
        'static_scale_control_map','static_rotation_control_map','static_translation_control_map',
        'animated_scale_control_map','animated_rotation_control_map','animated_translation_control_map'
    ]
    out={}
    for n in names:
        vals=array_data(getattr(cm,n,None)); out[n]={'count':len(vals),'values':vals}
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--clip',action='append',required=True)
    ap.add_argument('--member-catalog',type=Path,action='append',required=True)
    ap.add_argument('--base-url',required=True);ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('--parser-root',type=Path,required=True)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()
    cats=load_catalogs(a.member_catalog);base=a.base_url.rstrip('/')
    arc=SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1,a.part_count+1)],retries=6,timeout=90)
    c=RemoteCorpus(arc,cats,a.runtime)
    sys.path.insert(0,str(a.parser_root.resolve()))
    from tag.game_version import Game_Version
    from tag_readers.read_animation import read_animation
    ver=Game_Version.D1_ROI
    rows=[]; violations=[]
    for h0 in a.clip:
        h=norm(h0); row={'clip':h,'violations':[]}
        try:
            m=c.entry_meta(h);payload,src=c.payload(h)
            if m is None or payload is None or norm(m.get('reference','FFFFFFFF'))!=CLIP_REF:
                raise ValueError('clip_missing_or_wrong_class')
            anim=filebacked(read_animation,payload,ver); hd=anim.animation_header
            row.update({'source':str(src),'size':len(payload),'frame_count':int(hd.frame_count),'node_count':int(hd.node_count),'rig_control_count':int(hd.rig_control_count)})
            row['static']=codec1_row(anim.static_bones_header,anim.static_bones_buffers)
            row['animated']=codec1_row(anim.animated_bones_header,anim.animated_bones_buffers)
            row['control_maps']=control_maps_row(anim.control_maps)
            row['runtime_rig_component_count']=len(anim.runtime_rig_components)
            # Correlate codec-1 zero routes to their matching animated control-map entries.
            if row['animated'] and (row['animated'].get('header') or {}).get('codec_type')==1:
                z=row['animated'].get('zero_entries',{})
                cm=row['control_maps'] or {}
                corr={}
                for kind,map_name in [('scale','animated_scale_control_map'),('rotation','animated_rotation_control_map'),('translation','animated_translation_control_map')]:
                    vals=(cm.get(map_name) or {}).get('values',[])
                    corr[kind]=[{'stream_index':i,'control_map_value':vals[i] if i<len(vals) else None} for i in z.get(kind,[])]
                row['animated_zero_route_control_map_correlation']=corr
        except Exception as ex: row['violations'].append(repr(ex))
        violations.extend(f'{h}:{x}' for x in row['violations']);rows.append(row)
        print('CLIP',h,'FRAMES',row.get('frame_count'),'ANIM_CODEC',((row.get('animated') or {}).get('header') or {}).get('codec_type'),'ZERO',((row.get('animated') or {}).get('zero_entries')),'VIOL',row['violations'],flush=True)
    out={'schema':'d1_remote_codec1_array7_probe/v1','status':'COMPLETE' if not violations else 'WITH_VIOLATIONS','clips':rows,'violations':violations,
         'policy':'Diagnostic only. array_7 value 0 is reported but assigned no semantics. No animation tracks are fabricated or decoded by this tool.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n')
    return 0 if not violations else 2
if __name__=='__main__': raise SystemExit(main())
