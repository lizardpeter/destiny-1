#!/usr/bin/env python3
"""Source-close D1 spawned-actor animation options through the native retarget path.

This supersedes the strict-dimension diagnostic in
``d1_remote_spawned_actor_animation_census.py`` for runtime compatibility.

Important distinction:
  * an 80802C0E control may serialize a larger animation-list bank;
  * only FileHashes actually selected by decoded state-table records are runtime
    animation options for this control;
  * D1 deliberately supports cross-rig retargeting, so source clip node/control
    dimensions do not need to equal the target skeleton/runtime-rig dimensions.

For every actor this tool source-proves the two calibrated animation-owner edges,
recovers every selector state without assigning a default action, then executes each
selector-selected 808005A1 clip through the pinned retail decode/retarget/localize
sequence against the actor's exact source skeleton/runtime rig.

No state name, idle/default action, or visual choice is inferred.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import struct
import sys
import tempfile
import traceback
import numpy as np
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_animation_control_state_map import decode_control
from d1_animation_retarget_probe import component_rows, common_component_prefix
from d1_entity_resource_probe import ENTITY_RESOURCE_CLASS, parse_resource
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_activity_placements import RemoteCorpus
from d1_remote_s_entity_resource_package_find import S_ENTITY_REF, parse_entity_resources
from d1_split_tar_extract import SplitHttpTar

NULLS = {'00000000', 'FFFFFFFF'}

MOTION_EPS = 1e-6

def _canonical_curve_hash(tracks: list) -> str:
    """Hash complete decoded local transform arrays in one deterministic format.

    The hash is over canonical little-endian float64 array bytes plus explicit
    track/lane/shape framing.  It establishes equality of decoded local arrays
    under this pinned parser/retarget/localize path; it is not a hash of the
    original compressed clip bytes.
    """
    h=hashlib.sha256()
    h.update(b'D1_DECODED_LOCAL_CURVE_V1\0')
    lanes=(('scales',1),('rotations',2),('translations',3))
    h.update(struct.pack('<I',len(tracks)))
    for ti,t in enumerate(tracks):
        h.update(struct.pack('<I',ti))
        for name,lane_id in lanes:
            h.update(struct.pack('<I',lane_id))
            arr=getattr(t,name,None)
            if arr is None:
                h.update(struct.pack('<I',0xFFFFFFFF))
                continue
            a=np.asarray(arr,dtype=np.float64)
            a=np.ascontiguousarray(a.astype('<f8',copy=False))
            h.update(struct.pack('<I',a.ndim))
            for dim in a.shape:
                h.update(struct.pack('<Q',int(dim)))
            h.update(struct.pack('<Q',int(a.size)))
            h.update(a.tobytes(order='C'))
    return h.hexdigest()


def _track_motion_summary(tracks: list) -> dict:
    """Summarize exact decoded local-space variation without naming behavior."""
    dyn_scale=[]; dyn_rot=[]; dyn_tr=[]; any_dyn=[]
    for i,t in enumerate(tracks):
        changed=False
        sc=getattr(t,'scales',None)
        if sc is not None and len(sc)>1:
            a=np.asarray(sc,dtype=np.float64)
            if float(np.max(np.abs(a-a[0])))>MOTION_EPS:
                dyn_scale.append(i); changed=True
        rot=getattr(t,'rotations',None)
        if rot is not None and len(rot)>1:
            q=np.asarray(rot,dtype=np.float64)
            q0=q[0]
            qn=np.linalg.norm(q,axis=1); n0=float(np.linalg.norm(q0))
            if n0>0 and np.all(qn>0):
                dots=np.abs((q @ q0)/(qn*n0))
                if float(1.0-np.min(np.clip(dots,0.0,1.0)))>MOTION_EPS:
                    dyn_rot.append(i); changed=True
            elif float(np.max(np.abs(q-q0)))>MOTION_EPS:
                dyn_rot.append(i); changed=True
        tr=getattr(t,'translations',None)
        if tr is not None and len(tr)>1:
            a=np.asarray(tr,dtype=np.float64)
            if float(np.max(np.abs(a-a[0])))>MOTION_EPS:
                dyn_tr.append(i); changed=True
        if changed:
            any_dyn.append(i)
    bone0={}
    if tracks:
        tr=getattr(tracks[0],'translations',None)
        if tr is not None and len(tr):
            a=np.asarray(tr,dtype=np.float64)
            start=a[0]; end=a[-1]
            bone0={
                'translation_start':start.tolist(),
                'translation_end':end.tolist(),
                'translation_end_minus_start':(end-start).tolist(),
                'translation_end_displacement':float(np.linalg.norm(end-start)),
                'translation_peak_displacement_from_start':float(np.max(np.linalg.norm(a-start,axis=1))),
            }
    return {
        'epsilon':MOTION_EPS,
        'track_count':len(tracks),
        'dynamic_scale_track_count':len(dyn_scale),
        'dynamic_rotation_track_count':len(dyn_rot),
        'dynamic_translation_track_count':len(dyn_tr),
        'dynamic_any_track_count':len(any_dyn),
        'dynamic_scale_track_indices':dyn_scale,
        'dynamic_rotation_track_indices':dyn_rot,
        'dynamic_translation_track_indices':dyn_tr,
        'dynamic_any_track_indices':any_dyn,
        'decoded_local_curve_sha256':_canonical_curve_hash(tracks),
        'decoded_local_curve_hash_basis':'D1_DECODED_LOCAL_CURVE_V1_CANONICAL_LE_FLOAT64_ARRAY_BYTES',
        'decoded_local_curve_hash_semantic':'EQUAL_HASH_MEANS_EQUAL_CANONICAL_DECODED_LOCAL_ARRAYS_UNDER_PINNED_PIPELINE',
        'bone0_translation_syntax':bone0,
        'semantic_boundary':'LOCAL_SPACE_VARIATION_ONLY_BONE0_NOT_NAMED_ROOT_MOTION',
    }

def _codec_header_summary(h) -> dict | None:
    if h is None:
        return None
    out={
        'codec_type':int(h.codec_type),
        'scale_stream_count':int(h.scale_stream_count),
        'rotation_stream_count':int(h.rotation_stream_count),
        'translation_stream_count':int(h.translation_stream_count),
        'prob_error_value':float(h.prob_error_value),
        'prob_compression_rate':float(h.prob_compression_rate),
    }
    if hasattr(h,'frame_count'):
        out['frame_count']=int(h.frame_count)
    return out

def _tag_array_len(a) -> int:
    if hasattr(a,'length'):
        return int(a.length)
    return int(len(a))

def _d1_roi_adjacent_header_vectors(hd, payload: bytes) -> dict:
    """Preserve the three exact D1 ROI Vec_Pointer words at header 0x130..0x15F.

    read_animation_header currently discards the first vector (unk_arr_1_pointer).
    The next two are frame_events_array_pointer and rig_components_array_pointer.
    We preserve raw words and bounded target prefixes without assigning an element
    type or stride to the unnamed vector.
    """
    if len(payload) < 0x160:
        raise ValueError(f'D1 ROI animation payload shorter than 0x160 header: {len(payload):#x}')

    def vec(name, length_off, relative_off, prefix_bytes=64):
        length=struct.unpack_from('<Q',payload,length_off)[0]
        rel=struct.unpack_from('<Q',payload,relative_off)[0]
        target=None if rel==0 else relative_off+rel
        if target is not None and not (0 <= target < len(payload)):
            raise ValueError(f'{name}: target OOB {target:#x}/{len(payload):#x}')
        prefix=b'' if target is None else payload[target:min(len(payload),target+prefix_bytes)]
        return {
            'name':name,
            'length_word_offset':length_off,
            'relative_word_offset':relative_off,
            'length_u64':length,
            'relative_u64':rel,
            'relative_hex':f'{rel:016X}',
            'target_offset':target,
            'target_prefix_byte_count':len(prefix),
            'target_prefix_hex':prefix.hex(),
        }

    unknown=vec('header_vec_0x130_UNNAMED',0x130,0x138)
    events=vec('frame_events_array_pointer',0x140,0x148)
    rig=vec('rig_components_array_pointer',0x150,0x158)

    hp=hd.frame_events_array_pointer
    rp=hd.rig_components_array_pointer
    checks={
        'frame_events_length_matches_parser':int(events['length_u64'])==int(hp.length),
        'frame_events_length_address_matches_parser':int(hp.length_address)==0x140,
        'frame_events_relative_address_matches_parser':int(hp.offset_address)==0x148,
        'frame_events_target_matches_parser':events['target_offset']==(None if int(hp.offset)==0 else int(hp.get_address())),
        'rig_components_length_matches_parser':int(rig['length_u64'])==int(rp.length),
        'rig_components_length_address_matches_parser':int(rp.length_address)==0x150,
        'rig_components_relative_address_matches_parser':int(rp.offset_address)==0x158,
        'rig_components_target_matches_parser':rig['target_offset']==(None if int(rp.offset)==0 else int(rp.get_address())),
    }
    if not all(checks.values()):
        raise ValueError(f'D1 ROI adjacent-header Vec_Pointer cross-check failed: {checks}')
    def rel_row(name,p):
        off_addr=int(p.offset_address); rel=int(p.offset)
        target=None if rel==0 else int(p.get_address())
        return {'name':name,'relative_word_offset':off_addr,'relative_u64':rel,
                'relative_hex':f'{rel:016X}','target_offset':target}

    def parser_vec_row(name,p):
        return {'name':name,'length_word_offset':int(p.length_address),
                'relative_word_offset':int(p.offset_address),'length_u64':int(p.length),
                'relative_u64':int(p.offset),'relative_hex':f'{int(p.offset):016X}',
                'target_offset':None if int(p.offset)==0 else int(p.get_address())}

    known_rel=[
        rel_row('static_bone_data_pointer',hd.static_bone_data_pointer),
        rel_row('animated_bone_data_pointer',hd.animated_bone_data_pointer),
        *[rel_row(f'extra_data_{i}_pointer',getattr(hd,f'extra_data_{i}_pointer')) for i in range(8)],
    ]
    known_vec=[
        parser_vec_row('static_scale_control_map_pointer',hd.static_scale_control_map_pointer),
        parser_vec_row('static_rotation_control_map_pointer',hd.static_rotation_control_map_pointer),
        parser_vec_row('static_translation_control_map_pointer',hd.static_translation_control_map_pointer),
        parser_vec_row('animated_scale_control_map_pointer',hd.animated_scale_control_map_pointer),
        parser_vec_row('animated_rotation_control_map_pointer',hd.animated_rotation_control_map_pointer),
        parser_vec_row('animated_translation_control_map_pointer',hd.animated_translation_control_map_pointer),
        events,rig,
    ]
    known_targets={}
    for q in [*known_rel,*known_vec]:
        t=q.get('target_offset')
        if t is not None:known_targets.setdefault(str(t),[]).append(q['name'])

    return {
        'd1_roi_header_bytes_minimum':0x160,
        'unnamed_vector':unknown,
        'frame_events_vector':events,
        'rig_components_vector':rig,
        'known_rel_pointers':known_rel,
        'known_vec_pointers':known_vec,
        'known_target_aliases':known_targets,
        'unnamed_target_aliases_to_known_fields':[] if unknown['target_offset'] is None else known_targets.get(str(unknown['target_offset']),[]),
        'parser_crosschecks':checks,
        'semantic_boundary':'RAW_D1_ROI_HEADER_VEC_POINTERS_UNNAMED_0X130_ELEMENT_SCHEMA_WITHHELD',
    }


def _frame_event_pointer_summary(hd, payload: bytes) -> dict:
    """Preserve the exact D1 ROI frame-event pointer array without decoding records."""
    p=hd.frame_events_array_pointer
    count=int(p.length);base=int(p.get_address())
    if count<0:
        raise ValueError(f'negative frame-event pointer count {count}')
    if count and (base<0 or base+count*8>len(payload)):
        raise ValueError(f'frame-event pointer array OOB: count={count} base={base:#x} len={len(payload):#x}')
    rows=[]
    for i in range(count):
        po=base+i*8
        rel=struct.unpack_from('<Q',payload,po)[0]
        target=None if rel==0 else po+rel
        if target is not None and not (0<=target<len(payload)):
            raise ValueError(f'frame-event pointer {i} target OOB: ptr={po:#x} rel={rel:#x} target={target:#x} len={len(payload):#x}')
        prefix=b'' if target is None else payload[target:min(len(payload),target+32)]
        rows.append({
            'index':i,'pointer_offset':po,'raw_relative_u64':rel,
            'raw_relative_hex':f'{rel:016X}','target_offset':target,
            'target_prefix_byte_count':len(prefix),'target_prefix_hex':prefix.hex(),
        })
    return {
        'count':count,'array_offset':base,
        'nonnull_count':sum(x['target_offset'] is not None for x in rows),
        'unique_nonnull_target_count':len({x['target_offset'] for x in rows if x['target_offset'] is not None}),
        'pointers':rows,
        'semantic_boundary':'POINTER_STRUCTURE_AND_BOUNDED_PREFIX_ONLY_EVENT_SCHEMA_WITHHELD',
    }
CONTROL_REF = '80802C0E'
CLIP_REF = '808005A1'
RUNTIME_RIG_PAIR = ('808008B2', '8080099B')
OWNER_EDGES = {
    ('808020BF', '808029D2'): 0x110,
    ('80802B92', '808020BB'): 0x448,
}


def norm(x) -> str:
    return str(x).upper().removeprefix('0X').zfill(8)


def u32(b: bytes, o: int) -> int:
    if o < 0 or o + 4 > len(b):
        raise ValueError(f'u32 OOB at 0x{o:X}/0x{len(b):X}')
    return struct.unpack_from('<I', b, o)[0]


def exact(c: RemoteCorpus, h: str, expected_ref: str | None = None):
    h = norm(h)
    m = c.entry_meta(h)
    b, src = c.payload(h)
    if m is None or b is None:
        raise KeyError(f'{h}: exact payload unavailable')
    got = norm(m.get('reference', 'FFFFFFFF'))
    if expected_ref is not None and got != norm(expected_ref):
        raise ValueError(f'{h}: reference {got} != {norm(expected_ref)}')
    return m, b, str(src)


def filebacked(read_animation, payload: bytes, version):
    with tempfile.NamedTemporaryFile() as f:
        f.write(payload)
        f.flush()
        f.seek(0)
        return read_animation(f, version)


def entity_resources(c: RemoteCorpus, entity: str) -> list[dict]:
    _, b, _ = exact(c, entity, S_ENTITY_REF)
    out = []
    for rr in parse_entity_resources(b):
        rh = norm(rr['resource_hash'])
        if rh in NULLS:
            continue
        rm, rb, rsrc = exact(c, rh)
        row = {
            'resource_index': int(rr['resource_index']),
            'resource_hash': rh,
            'reference': norm(rm.get('reference')),
            'source': rsrc,
        }
        if row['reference'] == ENTITY_RESOURCE_CLASS:
            pr = parse_resource(rb, 'PS4')
            row['semantic_role'] = pr.get('semantic_role')
            row['pair'] = [
                norm((pr.get('unk10') or {}).get('class_hash', 'FFFFFFFF')),
                norm((pr.get('unk18') or {}).get('class_hash', 'FFFFFFFF')),
            ]
            row['embedded_model'] = pr.get('embedded_model_tag_hash')
        out.append(row)
    return out


def selected_hashes(control: dict) -> list[str]:
    return sorted({
        norm(item['tag_hash'])
        for st in control['state_table']['records']
        for item in st.get('selected_animations', [])
    })


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--entity', action='append', default=[])
    ap.add_argument('--seed', type=Path)
    ap.add_argument('--member-catalog', type=Path, action='append', required=True)
    ap.add_argument('--base-url', required=True)
    ap.add_argument('--part-count', type=int, default=10)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--parser-root', type=Path, required=True)
    ap.add_argument('-o', '--output', type=Path, required=True)
    a = ap.parse_args()

    entities = [norm(x) for x in a.entity]
    if a.seed:
        seed = json.loads(a.seed.read_text())
        entities.extend(norm(x) for x in seed.get('entity_hashes', []))
    entities = list(dict.fromkeys(entities))
    if not entities:
        raise SystemExit('no entities supplied')

    cats = load_catalogs(a.member_catalog)
    arc = SplitHttpTar(
        [f"{a.base_url.rstrip('/')}/packages.tar.{i:03d}" for i in range(1, a.part_count + 1)],
        retries=6, timeout=90,
    )
    c = RemoteCorpus(arc, cats, a.runtime)

    sys.path.insert(0, str(a.parser_root.resolve()))
    from tag.game_version import Game_Version
    from tag_readers.read_skeleton import read_skeleton
    from tag_readers.read_rig import read_runtime_rig
    from tag_readers.read_animation import read_animation
    from animation_decoding.decode_animation import decode_animation
    from runtime_rig.rig_retarget import rig_retarget, calc_control_limit
    from animation_export.convert_animation_object_to_local import convert_obj_to_local
    ver = Game_Version.D1_ROI

    control_cache: dict[str, dict] = {}
    clip_cache: dict[str, dict] = {}
    skeleton_cache: dict[str, dict] = {}
    rig_cache: dict[str, dict] = {}
    target_cache: dict[tuple[str, str, str], dict] = {}

    def control_info(h: str) -> dict:
        h = norm(h)
        if h not in control_cache:
            m, b, src = exact(c, h, CONTROL_REF)
            dec = decode_control(b, None, [])
            animation_list = [norm(x['tag_hash']) for x in dec['animation_list']['items']]
            selected = selected_hashes(dec)
            control_cache[h] = {
                'tag_hash': h,
                'entry_index': int(m['index']),
                'size': int(m['file_size']),
                'source': src,
                'animation_list': dec['animation_list'],
                'state_table': dec['state_table'],
                'animation_list_hashes': animation_list,
                'selector_selected_clip_hashes': selected,
                'animation_list_count': len(animation_list),
                'selector_selected_unique_clip_count': len(selected),
                'unused_animation_list_hashes': sorted(set(animation_list) - set(selected)),
            }
        return control_cache[h]

    def clip_info(h: str) -> dict:
        h = norm(h)
        if h not in clip_cache:
            m, b, src = exact(c, h, CLIP_REF)
            anim = filebacked(read_animation, b, ver)
            hd = anim.animation_header
            cm=anim.control_maps
            clip_cache[h] = {
                'tag_hash': h,
                'entry_index': int(m['index']),
                'size': int(m['file_size']),
                'source': src,
                'payload_sha256': hashlib.sha256(b).hexdigest(),
                'animation_hash': f'{int(hd.animation_hash):08X}',
                'frame_count': int(hd.frame_count),
                'node_count': int(hd.node_count),
                'rig_control_count': int(hd.rig_control_count),
                'static_codec': _codec_header_summary(anim.static_bones_header),
                'animated_codec': _codec_header_summary(anim.animated_bones_header),
                'control_map_counts': {
                    'static_scale':_tag_array_len(cm.static_scale_control_map),
                    'static_rotation':_tag_array_len(cm.static_rotation_control_map),
                    'static_translation':_tag_array_len(cm.static_translation_control_map),
                    'animated_scale':_tag_array_len(cm.animated_scale_control_map),
                    'animated_rotation':_tag_array_len(cm.animated_rotation_control_map),
                    'animated_translation':_tag_array_len(cm.animated_translation_control_map),
                },
                'frame_event_pointers': _frame_event_pointer_summary(hd,b),
                'adjacent_header_vectors': _d1_roi_adjacent_header_vectors(hd,b),
                'runtime_components': component_rows(anim.runtime_rig_components),
                '_animation': anim,
            }
        return clip_cache[h]

    def skeleton_info(h: str) -> dict:
        h = norm(h)
        if h not in skeleton_cache:
            m, b, src = exact(c, h, ENTITY_RESOURCE_CLASS)
            sk = read_skeleton(io.BytesIO(b), ver)
            skeleton_cache[h] = {
                'tag_hash': h,
                'entry_index': int(m['index']),
                'source': src,
                'node_count': len(sk.node_defs),
                '_skeleton': sk,
            }
        return skeleton_cache[h]

    def rig_info(h: str) -> dict:
        h = norm(h)
        if h not in rig_cache:
            m, b, src = exact(c, h, ENTITY_RESOURCE_CLASS)
            rig = read_runtime_rig(io.BytesIO(b), ver)
            comps = component_rows(rig.rig_components)
            rig_cache[h] = {
                'tag_hash': h,
                'entry_index': int(m['index']),
                'source': src,
                'control_count': len(rig.controls_relations),
                'runtime_components': comps,
                '_rig': rig,
            }
        return rig_cache[h]

    def target_validation(skh: str, rgh: str, ch: str) -> dict:
        key = (norm(skh), norm(rgh), norm(ch))
        if key in target_cache:
            return target_cache[key]
        skh, rgh, ch = key
        skd = skeleton_info(skh)
        rgd = rig_info(rgh)
        ci = control_info(ch)
        sk = skd['_skeleton']
        rig = rgd['_rig']
        target_components = rgd['runtime_components']
        results = []
        for cliph in ci['selector_selected_clip_hashes']:
            cp = clip_info(cliph)
            anim = cp['_animation']
            clip_components = cp['runtime_components']
            rr = {
                'clip': cliph,
                'source_animation_hash': cp['animation_hash'],
                'source_clip_payload_sha256': cp['payload_sha256'],
                'frame_count': cp['frame_count'],
                'source_node_count': cp['node_count'],
                'source_rig_control_count': cp['rig_control_count'],
                'source_static_codec': cp['static_codec'],
                'source_animated_codec': cp['animated_codec'],
                'source_control_map_counts': cp['control_map_counts'],
                'source_frame_event_pointers': cp['frame_event_pointers'],
                'target_node_count': skd['node_count'],
                'target_rig_control_count': rgd['control_count'],
                'source_dimensions_exact': (
                    cp['node_count'] == skd['node_count'] and
                    cp['rig_control_count'] == rgd['control_count'] and
                    clip_components == target_components
                ),
                'component_prefix': common_component_prefix(target_components, clip_components),
            }
            try:
                limit = int(calc_control_limit(rig, anim.runtime_rig_components))
                rr['native_control_limit'] = limit
                if limit != int(rr['component_prefix']['control_limit']):
                    raise RuntimeError(
                        f'control-limit disagreement {limit} != '
                        f'{rr["component_prefix"]["control_limit"]}'
                    )
                decoded = decode_animation(anim)
                retargeted = rig_retarget(anim, decoded, sk, rig)
                local = convert_obj_to_local(anim, retargeted, sk)
                if len(retargeted) != skd['node_count'] or len(local) != skd['node_count']:
                    raise RuntimeError(
                        f'retarget/local track domains {len(retargeted)}/{len(local)} '
                        f'!= target nodes {skd["node_count"]}'
                    )
                rr.update({
                    'decoded_track_count': len(decoded),
                    'retargeted_track_count': len(retargeted),
                    'local_track_count': len(local),
                    'local_motion_summary': _track_motion_summary(local),
                    'retarget_success': True,
                })
            except Exception as ex:
                rr.update({
                    'retarget_success': False,
                    'error_type': type(ex).__name__,
                    'error': str(ex),
                    'trace_tail': traceback.format_exc().splitlines()[-8:],
                })
            results.append(rr)
        out = {
            'skeleton': skh,
            'runtime_rig': rgh,
            'control': ch,
            'skeleton_node_count': skd['node_count'],
            'runtime_rig_control_count': rgd['control_count'],
            'selector_state_count': int(ci['state_table']['count']),
            'animation_list_count': ci['animation_list_count'],
            'selector_selected_unique_clip_count': ci['selector_selected_unique_clip_count'],
            'unused_animation_list_clip_count': len(ci['unused_animation_list_hashes']),
            'clips': results,
            'retarget_success_count': sum(1 for x in results if x['retarget_success']),
            'retarget_failure_count': sum(1 for x in results if not x['retarget_success']),
            'exact_dimension_clip_count': sum(1 for x in results if x['source_dimensions_exact']),
            'native_retarget_required_clip_count': sum(1 for x in results if not x['source_dimensions_exact']),
        }
        out['all_selector_selected_clips_retarget_success'] = (
            bool(results) and out['retarget_failure_count'] == 0
        )
        target_cache[key] = out
        print(
            'TARGET', skh, rgh, ch,
            'clips', len(results),
            'success', out['retarget_success_count'],
            'fail', out['retarget_failure_count'],
            'exact_dims', out['exact_dimension_clip_count'],
            'retargeted', out['native_retarget_required_clip_count'],
            flush=True,
        )
        return out

    rows = []
    violations = []
    frontiers = []
    for entity in entities:
        row = {'entity': entity, 'violations': [], 'frontiers': []}
        try:
            resources = entity_resources(c, entity)
            row['resources'] = resources
            sks = [r['resource_hash'] for r in resources if r.get('semantic_role') == 'entity_skeleton']
            rigs = [r['resource_hash'] for r in resources if tuple(r.get('pair') or []) == RUNTIME_RIG_PAIR]
            owners = []
            for r in resources:
                pair = tuple(r.get('pair') or [])
                if pair not in OWNER_EDGES:
                    continue
                off = OWNER_EDGES[pair]
                _, ob, osrc = exact(c, r['resource_hash'], ENTITY_RESOURCE_CLASS)
                control = f'{u32(ob, off):08X}'
                cm = c.entry_meta(control)
                exact_control = cm is not None and norm(cm.get('reference')) == CONTROL_REF
                owners.append({
                    'resource_hash': r['resource_hash'],
                    'pair': list(pair),
                    'edge_offset': off,
                    'edge_offset_hex': f'0x{off:X}',
                    'observed_control': control,
                    'control_reference': None if cm is None else norm(cm.get('reference')),
                    'exact_control_class': exact_control,
                    'source': osrc,
                })
            row['skeleton_resources'] = sks
            row['runtime_rig_resources'] = rigs
            row['animation_owner_edges'] = owners
            if len(sks) != 1:
                row['frontiers'].append(f'expected one source skeleton, got {sks}')
            if len(rigs) != 1:
                row['frontiers'].append(f'expected one runtime rig pair {RUNTIME_RIG_PAIR}, got {rigs}')
            if len(owners) != 2:
                row['frontiers'].append(f'expected two calibrated animation owner resources, got {len(owners)}')
            bad_owner = [x for x in owners if not x['exact_control_class']]
            if bad_owner:
                row['violations'].append(f'owner edge(s) do not resolve to {CONTROL_REF}: {bad_owner}')
            controls = sorted({x['observed_control'] for x in owners if x['exact_control_class']})
            row['control_hashes'] = controls
            row['owner_pair_controls_agree'] = len(controls) == 1 and len(owners) == 2
            if len(controls) > 1:
                row['frontiers'].append(f'animation owner resources select multiple controls {controls}; preserving all')

            row['controls'] = [control_info(ch) for ch in controls]
            selected = sorted({
                h for ci in row['controls'] for h in ci['selector_selected_clip_hashes']
            })
            bank = sorted({h for ci in row['controls'] for h in ci['animation_list_hashes']})
            row['selector_selected_clip_hashes'] = selected
            row['animation_list_clip_hashes'] = bank
            row['unused_animation_list_clip_hashes'] = sorted(set(bank) - set(selected))
            row['state_option_count'] = sum(int(ci['state_table']['count']) for ci in row['controls'])
            row['nonempty_state_option_count'] = sum(
                1 for ci in row['controls'] for st in ci['state_table']['records']
                if st.get('selected_animations')
            )

            target_rows = []
            if len(sks) == 1 and len(rigs) == 1:
                for ch in controls:
                    tv = target_validation(sks[0], rigs[0], ch)
                    target_rows.append({k: v for k, v in tv.items() if k != 'clips'})
                    if not tv['all_selector_selected_clips_retarget_success']:
                        row['violations'].append(
                            f'{ch}: selector-selected native retarget failures '
                            f'{tv["retarget_failure_count"]}/{tv["selector_selected_unique_clip_count"]}'
                        )
            row['target_validations'] = target_rows
            row['all_selector_selected_clips_retarget_success'] = (
                bool(target_rows) and all(x['all_selector_selected_clips_retarget_success'] for x in target_rows)
            )
            row['status'] = (
                'source_closed'
                if not row['violations'] and not row['frontiers'] and controls
                and row['all_selector_selected_clips_retarget_success']
                else 'preserved_with_frontier' if not row['violations']
                else 'violation'
            )
        except Exception as ex:
            row['status'] = 'violation'
            row['violations'].append(repr(ex))
        for x in row['violations']:
            violations.append({'entity': entity, 'error': x})
        for x in row['frontiers']:
            frontiers.append({'entity': entity, 'frontier': x})
        rows.append(row)
        print(
            'ENTITY', entity, 'STATUS', row['status'],
            'SKEL', row.get('skeleton_resources'),
            'RIG', row.get('runtime_rig_resources'),
            'CONTROLS', row.get('control_hashes'),
            'SELECTED', len(row.get('selector_selected_clip_hashes', [])),
            'BANK', len(row.get('animation_list_clip_hashes', [])),
            'STATES', row.get('state_option_count'),
            'VIOL', len(row['violations']), 'FRONT', len(row['frontiers']),
            flush=True,
        )

    family_keys = defaultdict(list)
    for r in rows:
        sk = (r.get('skeleton_resources') or [None])[0] if len(r.get('skeleton_resources') or []) == 1 else None
        rig = (r.get('runtime_rig_resources') or [None])[0] if len(r.get('runtime_rig_resources') or []) == 1 else None
        controls = tuple(r.get('control_hashes') or [])
        family_keys[(sk, rig, controls)].append(r['entity'])
    families = []
    for i, ((sk, rig, controls), ents) in enumerate(sorted(family_keys.items(), key=lambda x: str(x[0])), 1):
        families.append({
            'family_id': f'ANIM_FAMILY_{i:02d}',
            'skeleton': sk,
            'runtime_rig': rig,
            'controls': list(controls),
            'entity_count': len(ents),
            'entities': sorted(ents),
        })

    statuses = Counter(r['status'] for r in rows)
    controls_public = {
        h: {k: v for k, v in ci.items()}
        for h, ci in control_cache.items()
    }
    for ci in controls_public.values():
        # Everything in the decoded control is JSON-safe already.
        pass
    clips_public = {
        h: {k: v for k, v in cp.items() if not k.startswith('_')}
        for h, cp in clip_cache.items()
    }
    targets_public = []
    for (sk, rig, ch), tv in sorted(target_cache.items()):
        targets_public.append({
            'target_id': f'{sk}:{rig}:{ch}',
            **tv,
        })

    unique_selected = sorted({h for ci in control_cache.values() for h in ci['selector_selected_clip_hashes']})
    unique_bank = sorted({h for ci in control_cache.values() for h in ci['animation_list_hashes']})
    out = {
        'schema': 'd1_remote_spawned_actor_animation_options/v2',
        'status': 'D1_TOWER_SPAWNED_ACTOR_ANIMATION_OPTIONS_COMPLETE' if not violations and not frontiers else 'D1_TOWER_SPAWNED_ACTOR_ANIMATION_OPTIONS_PARTIAL',
        'entity_count': len(rows),
        'source_closed_entity_count': statuses['source_closed'],
        'preserved_with_frontier_entity_count': statuses['preserved_with_frontier'],
        'violation_entity_count': statuses['violation'],
        'animation_family_count': len(families),
        'families': families,
        'unique_control_count': len(control_cache),
        'unique_selector_selected_clip_count': len(unique_selected),
        'unique_animation_list_clip_count': len(unique_bank),
        'unused_animation_list_clip_count': len(set(unique_bank) - set(unique_selected)),
        'unique_selector_selected_clip_hashes': unique_selected,
        'unique_animation_list_clip_hashes': unique_bank,
        'controls': controls_public,
        'clips': clips_public,
        'target_count': len(targets_public),
        'closed_target_count': sum(1 for x in targets_public if x['all_selector_selected_clips_retarget_success']),
        'retarget_pair_execution_count': sum(x['selector_selected_unique_clip_count'] for x in targets_public),
        'retarget_pair_success_count': sum(x['retarget_success_count'] for x in targets_public),
        'retarget_pair_failure_count': sum(x['retarget_failure_count'] for x in targets_public),
        'targets': targets_public,
        'entities': rows,
        'frontier_count': len(frontiers),
        'frontiers': frontiers,
        'violation_count': len(violations),
        'violations': violations,
        'policy': (
            'Animation ownership comes only from the two calibrated source owner edges. '
            'Runtime options are only FileHashes selected by decoded control state records; '
            'unselected animation-list bank entries are preserved but are not promoted to actor actions. '
            'Compatibility is established by executing the pinned D1 decode -> calc_control_limit -> '
            'rig_retarget -> convert-to-local path against each exact source skeleton/runtime rig. '
            'No state is designated idle/default/startup and no state-name preimage is invented.'
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + '\n')
    print(
        'STATUS', out['status'],
        'ENTITIES', out['entity_count'],
        'SOURCE_CLOSED', out['source_closed_entity_count'],
        'FAMILIES', out['animation_family_count'],
        'CONTROLS', out['unique_control_count'],
        'SELECTED_UNIQUE', out['unique_selector_selected_clip_count'],
        'BANK_UNIQUE', out['unique_animation_list_clip_count'],
        'TARGETS', out['target_count'],
        'CLOSED_TARGETS', out['closed_target_count'],
        'RETARGET_PAIRS', out['retarget_pair_execution_count'],
        'FAILURES', out['retarget_pair_failure_count'],
    )
    return 0 if not violations and not frontiers else 2


if __name__ == '__main__':
    raise SystemExit(main())
