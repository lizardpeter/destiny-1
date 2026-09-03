import struct, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from d1_skeleton_probe import parse_skeleton_resource
from d1_entity_resource_probe import D1_SKELETON_DISCRIMINATOR,D1_SKELETON_INFO

def array_header(b, o, data_off, count):
    struct.pack_into('<I',b,o,count)
    struct.pack_into('<q',b,o+8,data_off-(o+8)-0x10)

def resource_ptr(b,o,target,cls):
    struct.pack_into('<q',b,o,target-o)
    struct.pack_into('<I',b,target-4,cls)

def test_source_derived_d1_skeleton_layout_parser():
    b=bytearray(0x500)
    struct.pack_into('<Q',b,0,len(b))
    resource_ptr(b,0x10,0x80,D1_SKELETON_DISCRIMINATOR)
    base=0x100
    resource_ptr(b,0x18,base,D1_SKELETON_INFO)
    nodes=0x300; defs=0x320; invs=0x360; ranges=0x3A0; inner=0x3A4
    array_header(b,base+0x88,nodes,2); array_header(b,base+0x98,defs,2); array_header(b,base+0xA8,invs,2)
    array_header(b,base+0xB8,ranges,2); array_header(b,base+0xC8,inner,2)
    struct.pack_into('<Iiii',b,nodes,0x11111111,-1,1,-1); struct.pack_into('<Iiii',b,nodes+0x10,0x22222222,0,-1,-1)
    struct.pack_into('<8f',b,defs,0,0,0,1,1,2,3,1); struct.pack_into('<8f',b,defs+0x20,0,0,0,1,4,5,6,1)
    struct.pack_into('<8f',b,invs,0,0,0,1,-1,-2,-3,1); struct.pack_into('<8f',b,invs+0x20,0,0,0,1,-4,-5,-6,1)
    struct.pack_into('<2h',b,ranges,3,4); struct.pack_into('<2h',b,inner,5,6)
    s=parse_skeleton_resource(bytes(b))['skeleton_info']
    assert s['node_hierarchy']['count']==2
    assert s['bones'][0]['node_hash']=='11111111' and s['bones'][0]['parent_node_index']==-1
    assert s['bones'][1]['parent_node_index']==0
    assert s['bones'][1]['default_object_space_transform']['translation']==[4.0,5.0,6.0]
    assert s['range_index_map']['items']==[3,4]
    assert all(s['count_invariants'].values())
