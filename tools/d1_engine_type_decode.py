"""Python port of the backend engine-type bitstream decoder (backend/src/invest.rs) with every
field kind, plus guess(): which types decode a payload exactly. Research aid."""
import json
SCH = json.load(open(__import__('os').path.join(__import__('os').path.dirname(__file__), '..', 'backend', 'data', 'investment_schema.json')))['types']
class Bad(Exception): pass
class R:
    def __init__(s, data): s.d = data; s.p = 0
    def bits(s, n):
        v = 0
        for _ in range(n):
            i = s.p >> 3
            if i >= len(s.d): raise Bad('overrun')
            v = (v << 1) | ((s.d[i] >> (7 - (s.p & 7))) & 1); s.p += 1
        return v
POINT3D = None  # (bits_x, bits_y, bits_z) when world positions are quantized (runtime config)
def point3d(r):
    if POINT3D and r.bits(1):
        return tuple(r.bits(b) for b in POINT3D)
    return tuple(r.bits(32) for _ in range(3))
def scalar(r, m, k=None):
    k = m['kind'] if k is None else k
    if k in (0, 17): return None
    if k == 2: return bool(r.bits(1))
    if k == 11:
        n = m.get('p2', 0)
        if 0 < n < 32: return ('q', r.bits(n))
        import struct; return struct.unpack('<f', r.bits(32).to_bytes(4, 'little'))[0]
    if k == 12: return r.bits(64)
    if 3 <= k <= 10:
        b = m.get('bits', 0)
        if b == 0 or b > 64: raise Bad('bits')
        v = r.bits(b) - m.get('bias', 0)
        w = {3: 8, 7: 8, 4: 16, 8: 16, 5: 32, 9: 32}.get(k, 64)
        v &= (1 << w) - 1
        if v >> (w - 1) and k in (3, 4, 5, 6): v -= 1 << w
        return v
    if k == 13: return point3d(r)
    if k == 14: return None if r.bits(1) else ('vec', r.bits(19), r.bits(16))
    if k in (18, 20, 21, 22, 23): return r.bits(32) if r.bits(1) else -1
    if k == 19: return (r.bits(32), r.bits(6)) if r.bits(1) else -1
    if k in (24, 25): return scalar(r, m, r.bits(6))
    if k == 26: return r.bits(128)
    if k in (27, 28):
        if not r.bits(1): return None
        return r.bits(192) if not r.bits(1) else (r.bits(32), r.bits(32), r.bits(12))
    if k == 29:
        h = (r.bits(32), r.bits(6)) if r.bits(1) else None
        return (h, r.bits(128))
    if k == 35: return int.from_bytes(bytes(r.bits(8) for _ in range(8)), 'little')
    if k in (34, 41):
        t = r.bits(32) if r.bits(1) else -1
        if t == -1: return None
        tid = '0x%08x' % t
        if tid not in SCH or SCH[tid].get('opaque'): raise Bad('dyn type')
        return {tid: members(r, SCH[tid], 1)}
    raise Bad(f'kind {k}')
def members(r, t, depth):
    out = []
    for m in t.get('members', []):
        out.append(member(r, m, t, out, depth))
    return out
def member(r, m, parent, sib, depth):
    if depth > 12: raise Bad('depth')
    if m.get('pres') and not r.bits(1): return None
    if m['kind'] == 1:
        sub = SCH.get(m.get('type'))
        if sub is None or sub.get('opaque'): raise Bad('type')
        if sub.get('array', 0) > 0:
            n = sub['array']
            if 'count_at' in m:
                idx = [i for i, s in enumerate(parent['members']) if s['off'] == m['count_at']]
                n = min(max(sib[idx[0]] or 0, 0), sub['array']) if idx and idx[0] < len(sib) and isinstance(sib[idx[0]], int) else 0
            em = sub['members'][0]
            return [member(r, em, sub, [], depth + 1) for _ in range(n)]
        return members(r, sub, depth + 1)
    return scalar(r, m)
def decode(data, tid):
    r = R(data); v = members(r, SCH[tid], 0); return v, r.p
def guess(data, slack=8):
    hits = []
    for tid, t in SCH.items():
        if t.get('opaque') or not t.get('members'): continue
        try:
            v, used = decode(data, tid)
        except (Bad, RecursionError, KeyError, IndexError, TypeError):
            continue
        if 0 <= len(data) * 8 - used < slack: hits.append((tid, used))
    return hits
