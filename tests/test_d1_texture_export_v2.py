#!/usr/bin/env python3
"""Regression for strict-chain installation in d1_texture_export_v2."""
import importlib.util
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import d1_texture_export as legacy
import d1_texture_export_v2 as v2

R=object()
def rec(t,st,ref='',tag='X'):
    return (R,{'type':t,'subtype':st,'reference':ref,'tag_hash':tag})

# The adapter preserves the legacy (first, backing) contract for proven paths.
g={'M':rec(65,1,'D','M'),'D':rec(5,1,'','D')}
f,b=v2.strict_follow_backing(g,{'type':32,'subtype':1,'reference':'M'})
assert f==g['M'] and b==g['D']

g={'D':rec(1,1,'','D')}
f,b=v2.strict_follow_backing(g,{'type':32,'subtype':1,'reference':'D'})
assert f is b and b==g['D']

# A resolvable second hop is no longer sufficient evidence.
g={'X':rec(99,1,'D','X'),'D':rec(5,1,'','D')}
try:
    v2.strict_follow_backing(g,{'type':32,'subtype':1,'reference':'X'})
except ValueError as e:
    assert 'unproven texture backing chain' in str(e)
else:
    raise AssertionError('v2 accepted adjacency-only texture chain')

# Verify export_reader actually installs the strict resolver into the legacy
# function's global namespace; this is the integration boundary used at run time.
old=legacy.follow_backing
v2.install_strict_chain_gate()
assert legacy.follow_backing is v2.strict_follow_backing
legacy.follow_backing=old

print('D1_TEXTURE_EXPORT_V2_STRICT_GATE_GREEN')


# Exact BC block sizing must work for dimensions smaller than/non-multiple of 4.
assert legacy.expected_base_size(1,1,legacy.GCN_BC1)==8
assert legacy.expected_base_size(3,5,legacy.GCN_BC3)==32
assert legacy.expected_base_size(5,5,legacy.GCN_BC5)==64
assert legacy.expected_base_size(7,9,legacy.GCN_RGBA8)==7*9*4

# Strict payload normalization must reject truncation rather than allowing the
# deswizzler to synthesize zero-filled blocks from missing source bytes.
try:
    legacy.normalize_top_level_payload(b'\0'*7,8,strict=True,label='fixture')
except ValueError as e:
    assert 'truncated' in str(e) and 'need at least 8 bytes, got 7' in str(e)
else:
    raise AssertionError('strict texture size gate accepted truncated backing')
assert legacy.normalize_top_level_payload(b'\0'*9,8,strict=True)==b'\0'*8

# A completed v2 manifest is itself fail-closed.
assert v2.strict_manifest_violations({
    'missing_requested':[],
    'textures':[{'header':'A','available':True,'array_size':1,'dds':'A.dds'}],
})==[]
v=v2.strict_manifest_violations({
    'missing_requested':['B'],
    'textures':[
        {'header':'A','available':False},
        {'header':'C','available':True,'array_size':1,'dds':None},
        {'header':'D','available':True,'array_size':6,'face_dds':['x']*5},
        {'header':'E','available':True,'array_size':2},
    ],
})
assert 'missing_requested:B' in v
assert 'A:header_unavailable' in v
assert 'C:missing_dds' in v
assert 'D:incomplete_cube_dds' in v
assert 'E:unsupported_array_size:2' in v
print('D1_TEXTURE_EXPORT_V2_SIZE_AND_MANIFEST_GATES_GREEN')
