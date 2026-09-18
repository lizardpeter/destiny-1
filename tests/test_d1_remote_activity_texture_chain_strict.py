#!/usr/bin/env python3
"""Regression for strict texture shapes inside arbitrary-activity dependency closure."""
from __future__ import annotations
import struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import d1_remote_activity_material_dependency_closure as m

def hdr(kind=(32,1),ref='80802002',w=4,h=4,gfmt=0x23):
 b=bytearray(0x3c)
 struct.pack_into('<H',b,6,gfmt<<4)
 struct.pack_into('<I',b,0x24,0xBEEFCAFE)
 struct.pack_into('<H',b,0x28,w);struct.pack_into('<H',b,0x2a,h)
 struct.pack_into('<H',b,0x2c,1);struct.pack_into('<H',b,0x2e,1)
 return bytes(b)

class C:
 def __init__(self,meta,data):
  self.meta={k.upper():dict(v,index=i,file_size=len(data.get(k,b''))) for i,(k,v) in enumerate(meta.items())}
  self.data={k.upper():v for k,v in data.items()}
 def entry_meta(self,h):return self.meta.get(str(h).upper())
 def payload(self,h):h=str(h).upper();return self.data.get(h),f'fixture:{h}'

def E(t,st,ref='FFFFFFFF'):return {'type':t,'subtype':st,'reference':ref}

H='80802001';A='80802002';B='80802003'

# Exact two-hop Texture2D.
c=C({H:E(32,1,A),A:E(65,1,B),B:E(5,1)}, {H:hdr(),A:b'mid',B:b'12345678'})
out,v,e=m.texture_chain(c,H)
assert not v,v
assert out['storage_mode']=='two_hop_65_1_to_5_1'
assert out['strict_backing_hash']==B
assert out['final_payload_hash']==B
assert out['base_size_validation']=={'expected':8,'actual':8,'sufficient':True}

# Exact direct Texture2D.
c=C({H:E(32,1,A),A:E(1,1)}, {H:hdr(),A:b'12345678'})
out,v,e=m.texture_chain(c,H)
assert not v,v
assert out['storage_mode']=='direct' and out['strict_backing_hash']==A

# Arbitrary direct class remains serialized evidence but is rejected semantically.
c=C({H:E(32,1,A),A:E(99,1)}, {H:hdr(),A:b'12345678'})
out,v,e=m.texture_chain(c,H)
assert any('texture_storage_shape_rejected' in x for x in v),v
assert out['storage_mode'] is None

# The Texture2D streamed path is not silently promoted to TextureCube.
c=C({H:E(32,2,A),A:E(65,1,B),B:E(5,1)}, {H:hdr((32,2)),A:b'mid',B:b'12345678'})
out,v,e=m.texture_chain(c,H)
assert any('texture_storage_shape_rejected' in x for x in v),v

# Short terminal bytes fail even when the class chain is exact.
c=C({H:E(32,1,A),A:E(65,1,B),B:E(5,1)}, {H:hdr(),A:b'mid',B:b'1234567'})
out,v,e=m.texture_chain(c,H)
assert any('full_resolution_payload_short:7<8' in x for x in v),v

print('D1_REMOTE_ACTIVITY_TEXTURE_CHAIN_STRICT_GREEN')
