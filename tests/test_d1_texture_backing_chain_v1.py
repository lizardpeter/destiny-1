#!/usr/bin/env python3
import importlib.util
from pathlib import Path

P=Path(__file__).resolve().parents[1]/'tools'/'d1_texture_backing_chain_v1.py'
s=importlib.util.spec_from_file_location('chain',P); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
R=object()
def rec(t,st,ref=''):
    return (R,{'type':t,'subtype':st,'reference':ref,'tag_hash':f'{t:02X}{st:02X}'})

# Proven direct Texture2D and TextureCube shapes.
g={'A':rec(1,1)}
f,b,mode=m.resolve_texture_backing(g,{'type':32,'subtype':1,'reference':'a'})
assert f is b and mode=='direct'
g={'B':rec(1,2)}
f,b,mode=m.resolve_texture_backing(g,{'type':32,'subtype':2,'reference':'b'})
assert f is b and mode=='direct'

# Proven large Texture2D shape.
g={'M':rec(65,1,'D'),'D':rec(5,1)}
f,b,mode=m.resolve_texture_backing(g,{'type':32,'subtype':1,'reference':'m'})
assert f==g['M'] and b==g['D'] and mode=='two_hop_65_1_to_5_1'

# Adjacency is not semantics: reject an arbitrary first hop even if it has a
# resolvable second reference.
g={'X':rec(99,1,'D'),'D':rec(5,1)}
try: m.resolve_texture_backing(g,{'type':32,'subtype':1,'reference':'X'})
except ValueError as e: assert 'unproven texture backing chain' in str(e)
else: raise AssertionError('arbitrary first hop accepted')

# Likewise reject a 65:1 hop whose terminal class is not the proven 5:1.
g={'M':rec(65,1,'D'),'D':rec(1,1)}
try: m.resolve_texture_backing(g,{'type':32,'subtype':1,'reference':'M'})
except ValueError as e: assert 'terminal must be 5:1' in str(e)
else: raise AssertionError('wrong terminal class accepted')

# Do not silently extend the 65:1 path to TextureCube.
g={'M':rec(65,1,'D'),'D':rec(5,1)}
try: m.resolve_texture_backing(g,{'type':32,'subtype':2,'reference':'M'})
except ValueError as e: assert 'unproven texture backing chain' in str(e)
else: raise AssertionError('unproven cube two-hop chain accepted')

print('D1_TEXTURE_BACKING_CHAIN_V1_GREEN')
