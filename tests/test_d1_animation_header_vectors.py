#!/usr/bin/env python3
from __future__ import annotations
import struct,sys,unittest
from pathlib import Path
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))

import d1_remote_spawned_actor_animation_options_v2 as anim


class FakeRel:
    def __init__(self,offset_address,offset=0):
        self.offset_address=offset_address
        self.offset=offset
    def get_address(self):
        return self.offset_address+self.offset


class FakeVec:
    def __init__(self,length_address,offset_address,length,offset):
        self.length_address=length_address
        self.offset_address=offset_address
        self.length=length
        self.offset=offset
    def get_address(self):
        return self.offset_address+self.offset


def fake_header(frame_length_address=0x140):
    q={
        'frame_events_array_pointer':FakeVec(frame_length_address,0x148,2,0x190-0x148),
        'rig_components_array_pointer':FakeVec(0x150,0x158,4,0x1A0-0x158),
    }
    rel_names=['static_bone_data_pointer','animated_bone_data_pointer']+[f'extra_data_{i}_pointer' for i in range(8)]
    for i,name in enumerate(rel_names):
        q[name]=FakeRel(0x10+i*8,0)
    vec_names=[
        'static_scale_control_map_pointer','static_rotation_control_map_pointer',
        'static_translation_control_map_pointer','animated_scale_control_map_pointer',
        'animated_rotation_control_map_pointer','animated_translation_control_map_pointer',
    ]
    for i,name in enumerate(vec_names):
        q[name]=FakeVec(0x98+i*16,0xA0+i*16,0,0)
    return SimpleNamespace(**q)


class TestD1AnimationHeaderVectors(unittest.TestCase):
    def test_d1_roi_adjacent_vec_pointer_offsets_and_relative_targets(self):
        b=bytearray(0x300)
        # unnamed vector: len=3, relative word 0x138 -> target 0x180
        struct.pack_into('<Q',b,0x130,3)
        struct.pack_into('<Q',b,0x138,0x180-0x138)
        # frame-event vector: len=2, relative word 0x148 -> target 0x190
        struct.pack_into('<Q',b,0x140,2)
        struct.pack_into('<Q',b,0x148,0x190-0x148)
        # rig-component vector: len=4, relative word 0x158 -> target 0x1A0
        struct.pack_into('<Q',b,0x150,4)
        struct.pack_into('<Q',b,0x158,0x1A0-0x158)
        for i in range(64):
            b[0x180+i]=(0xA0+i)&0xff
        hd=fake_header()
        d=anim._d1_roi_adjacent_header_vectors(hd,bytes(b))
        self.assertEqual(d['unnamed_vector']['length_u64'],3)
        self.assertEqual(d['unnamed_vector']['target_offset'],0x180)
        self.assertEqual(d['frame_events_vector']['target_offset'],0x190)
        self.assertEqual(d['rig_components_vector']['target_offset'],0x1A0)
        self.assertEqual(d['unnamed_vector']['target_prefix_byte_count'],64)
        self.assertEqual(
            bytes.fromhex(d['unnamed_vector']['target_prefix_hex']),
            bytes(b[0x180:0x1C0]),
        )
        self.assertTrue(all(d['parser_crosschecks'].values()))
        self.assertEqual(
            d['semantic_boundary'],
            'RAW_D1_ROI_HEADER_VEC_POINTERS_UNNAMED_0X130_ELEMENT_SCHEMA_WITHHELD',
        )

    def test_adjacent_vec_crosscheck_fails_on_parser_offset_drift(self):
        b=bytearray(0x300)
        struct.pack_into('<Q',b,0x140,2)
        struct.pack_into('<Q',b,0x148,0x190-0x148)
        struct.pack_into('<Q',b,0x150,4)
        struct.pack_into('<Q',b,0x158,0x1A0-0x158)
        hd=fake_header(frame_length_address=0x141)
        with self.assertRaisesRegex(ValueError,'cross-check failed'):
            anim._d1_roi_adjacent_header_vectors(hd,bytes(b))


if __name__=='__main__':
    unittest.main()
