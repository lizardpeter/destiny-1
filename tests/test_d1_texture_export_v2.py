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
