from __future__ import annotations

import struct
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from d1_guardian_inline_skin_probe import decode_stream


def test_stride_0c_rigid_w_is_one_bone():
    # xyz + position-W joint 18 + two UV int16 values.
    b=struct.pack('<hhhhhh',1,2,3,18,100,-100)
    d=decode_stream(b,0x0C,67)
    assert d['weight_sum_failure_count']==0
    assert d['out_of_range_influence_count']==0
    assert d['unresolved_vertex_count']==0
    assert d['mode_counts']=={'rigid_w':1}
    assert d['vertices'][0]['influences']==[{'bone':18,'weight_u8':255,'weight':1.0}]


def test_stride_0c_7fff_is_inline_two_weight_skin():
    # xyz + sentinel + indices 5,8 + normalized U8 weights 100,155.
    b=struct.pack('<hhhhBBBB',1,2,3,32767,5,8,100,155)
    d=decode_stream(b,0x0C,67)
    assert d['weight_sum_failure_count']==0
    assert d['out_of_range_influence_count']==0
    assert d['mode_counts']=={'inline2':1}
    assert [(x['bone'],x['weight_u8']) for x in d['vertices'][0]['influences']]==[(5,100),(8,155)]


def test_stride_10_is_inline_four_weight_skin():
    # xyz + sentinel + four weight bytes + four bone bytes.
    b=struct.pack('<hhhhBBBBBBBB',1,2,3,32767,64,64,64,63,1,5,8,11)
    d=decode_stream(b,0x10,67)
    assert d['weight_sum_failure_count']==0
    assert d['out_of_range_influence_count']==0
    assert d['mode_counts']=={'inline4':1}
    assert [(x['bone'],x['weight_u8']) for x in d['vertices'][0]['influences']]==[(1,64),(5,64),(8,64),(11,63)]


def test_zero_weight_unused_index_is_not_a_nonzero_influence():
    b=struct.pack('<hhhhBBBBBBBB',1,2,3,32767,255,0,0,0,18,255,255,255)
    d=decode_stream(b,0x10,67)
    assert d['out_of_range_influence_count']==0
    assert d['bone_domain']==[18]
    assert d['vertices'][0]['influences']==[{'bone':18,'weight_u8':255,'weight':1.0}]


def test_malformed_weight_sum_is_reported_fail_closed():
    b=struct.pack('<hhhhBBBB',1,2,3,32767,5,8,100,100)
    d=decode_stream(b,0x0C,67)
    assert d['weight_sum_failure_count']==1
    assert d['weight_sum_failures'][0]['sum']==200


def test_nonzero_out_of_range_bone_is_reported():
    b=struct.pack('<hhhhBBBB',1,2,3,32767,5,99,100,155)
    d=decode_stream(b,0x0C,67)
    assert d['out_of_range_influence_count']==1
    assert d['out_of_range_influences'][0]['bone']==99
