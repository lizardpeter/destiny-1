import importlib.util
import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('demote', ROOT/'tools'/'d1_gltf_demote_control_color.py')
mod = importlib.util.module_from_spec(SPEC)
sys.modules['demote'] = mod
SPEC.loader.exec_module(mod)


def make_glb(path: Path):
    doc = {
        'asset': {'version':'2.0'},
        'buffers':[{'byteLength':4}],
        'bufferViews':[{'buffer':0,'byteOffset':0,'byteLength':4}],
        'accessors':[{'bufferView':0,'componentType':5121,'count':1,'type':'VEC4','normalized':True}],
        'materials':[{'name':'TigerMaterial_80C9993C_PREVIEW'}],
        'meshes':[{'primitives':[{'attributes':{'COLOR_0':0},'material':0}]}],
    }
    jb=json.dumps(doc,separators=(',',':')).encode();jb+=b' '*((-len(jb))&3)
    bb=b'\x01\x02\x03\x04'
    total=12+8+len(jb)+8+len(bb)
    path.write_bytes(struct.pack('<III',mod.MAGIC,2,total)+struct.pack('<II',len(jb),mod.JSON_CHUNK)+jb+struct.pack('<II',len(bb),mod.BIN_CHUNK)+bb)


def test_demote_preserves_accessor_and_bin(tmp_path, monkeypatch):
    src=tmp_path/'in.glb';out=tmp_path/'out.glb';rep=tmp_path/'r.json';make_glb(src)
    monkeypatch.setattr(sys,'argv',['x','--input-glb',str(src),'--material','80C9993C','--out',str(out),'--report',str(rep)])
    assert mod.main()==0
    d,b,_=mod.read_glb(out)
    attrs=d['meshes'][0]['primitives'][0]['attributes']
    assert 'COLOR_0' not in attrs
    assert attrs['_D1_COLOR']==0
    assert b==b'\x01\x02\x03\x04'
    r=json.loads(rep.read_text())
    assert r['bin_byte_identical'] is True
    assert r['renamed_primitive_count']==1
