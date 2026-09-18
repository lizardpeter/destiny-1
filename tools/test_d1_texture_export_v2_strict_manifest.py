#!/usr/bin/env python3
"""Regression for the production texture exporter strict-chain adapter.

Synthetic records are regression fixtures only. They prove fail-closed control
flow; they are not retail evidence and do not establish Tiger semantic names.
"""
from __future__ import annotations
import sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import d1_texture_export_v2 as v2

R=object()
def rec(kind, ref=''):
    return (R, {'type':kind[0],'subtype':kind[1],'reference':ref,'tag_hash':'F00DBAAD'})

def must_fail(fn, needle):
    try: fn()
    except Exception as ex:
        assert needle in str(ex), (needle,repr(ex))
    else: raise AssertionError('expected fail-closed rejection')

# Proven direct 2D shape.
h={'type':32,'subtype':1,'reference':'A'}
g={'A':rec((1,1))}
first,back=v2.strict_follow_backing(g,h)
assert first is back and back[1]['type']==1

# Proven streamed 2D shape.
h={'type':32,'subtype':1,'reference':'A'}
g={'A':rec((65,1),'B'),'B':rec((5,1))}
first,back=v2.strict_follow_backing(g,h)
assert first[1]['type']==65 and back[1]['type']==5

# Observed direct cube pair.
h={'type':32,'subtype':2,'reference':'A'}
g={'A':rec((1,2))}
first,back=v2.strict_follow_backing(g,h)
assert first is back and back[1]['subtype']==2

# Legacy exporter would have followed this merely because B resolves. v2 must not.
h={'type':32,'subtype':1,'reference':'A'}
g={'A':rec((1,1),'B'),'B':rec((5,1))}
first,back=v2.strict_follow_backing(g,h)
assert first is back, 'direct 1:1 must terminate even when its reference resolves'

# A 65:1 hop cannot terminate in an arbitrary resolvable class.
h={'type':32,'subtype':1,'reference':'A'}
g={'A':rec((65,1),'B'),'B':rec((1,1))}
must_fail(lambda:v2.strict_follow_backing(g,h),'terminal must be 5:1')

# No source-closed cube two-hop shape has been admitted.
h={'type':32,'subtype':2,'reference':'A'}
g={'A':rec((65,1),'B'),'B':rec((5,1))}
must_fail(lambda:v2.strict_follow_backing(g,h),'unproven texture backing chain')
print('PASS: production v2 adapter is fail-closed over proven texture chain shapes')
