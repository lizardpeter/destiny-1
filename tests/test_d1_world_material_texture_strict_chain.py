#!/usr/bin/env python3
"""Regression: generic world/Tower texture export shares the strict chain gate."""
from __future__ import annotations
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import d1_world_material_texture_export as w

class Corpus:
    def __init__(self,meta,payload=None):
        self.meta={k.upper():dict(v) for k,v in meta.items()}
        self.data={k.upper():v for k,v in (payload or {}).items()}
    def entry_meta(self,h):
        return self.meta.get(str(h).upper())
    def payload(self,h):
        h=str(h).upper()
        return self.data.get(h), f'fixture:{h}'

def E(t,st,ref='FFFFFFFF'):
    return {'type':t,'subtype':st,'reference':ref}

# Direct Texture2D.
c=Corpus({'H':E(32,1,'D'),'D':E(1,1)}, {'H':b'h','D':b'd'})
rows,mode,bh,err=w.resolve_chain(c,'H')
assert err is None and mode=='direct' and bh=='D'
assert [x['hash'] for x in rows]==['H','D']

# Proven streamed Texture2D.
c=Corpus({'H':E(32,1,'M'),'M':E(65,1,'D'),'D':E(5,1)},
         {'H':b'h','M':b'm','D':b'd'})
rows,mode,bh,err=w.resolve_chain(c,'H')
assert err is None and mode=='two_hop_65_1_to_5_1' and bh=='D'
assert [x['hash'] for x in rows]==['H','M','D']

# Proven direct cube.
c=Corpus({'H':E(32,2,'D'),'D':E(1,2)}, {'H':b'h','D':b'd'})
rows,mode,bh,err=w.resolve_chain(c,'H')
assert err is None and mode=='direct' and bh=='D'

# Adjacency/reference depth alone is never sufficient.
c=Corpus({'H':E(32,1,'X'),'X':E(99,1,'D'),'D':E(5,1)},
         {'H':b'h','X':b'x','D':b'd'})
rows,mode,bh,err=w.resolve_chain(c,'H')
assert mode is None and bh is None and 'unproven texture backing chain' in err
assert [x['hash'] for x in rows]==['H','X'], rows

# Cube may not silently inherit the 2D two-hop shape.
c=Corpus({'H':E(32,2,'M'),'M':E(65,1,'D'),'D':E(5,1)},
         {'H':b'h','M':b'm','D':b'd'})
rows,mode,bh,err=w.resolve_chain(c,'H')
assert mode is None and bh is None and 'unproven texture backing chain' in err

# Missing terminal remains an exact dependency frontier, not an arbitrary walk.
c=Corpus({'H':E(32,1,'M'),'M':E(65,1,'80AB0D9B')},
         {'H':b'h','M':b'm'})
rows,mode,bh,err=w.resolve_chain(c,'H')
assert mode is None and bh is None and 'terminal backing reference unavailable' in err
assert rows[-1]['unresolved_reference']=='80AB0D9B'

print('D1_WORLD_TEXTURE_STRICT_CHAIN_GREEN')
