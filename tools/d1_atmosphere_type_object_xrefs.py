#!/usr/bin/env python3
"""Find instruction-decoded RIP-reference candidates to the atmosphere type object.

Includes displacement followed by an immediate (memory stores). File-backed
PT_LOAD bytes only; type-object BSS contents are not read as ELF file data.
Candidates are decoded independently and are not a whole-program CFG proof.
"""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from capstone import Cs, CS_ARCH_X86, CS_MODE_64
from capstone.x86 import X86_OP_MEM, X86_REG_RIP
from d1_global_lighting_settings_defaults import EXPECTED_SHA256

def probe(path, target):
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == EXPECTED_SHA256
    cs = Cs(CS_ARCH_X86, CS_MODE_64)
    cs.detail = True
    rows = {}
    for align in range(4):
        offset = 0x4000 + align
        count = (26035092 - align) // 4
        words = np.frombuffer(raw, dtype='<i4', count=count, offset=offset)
        positions = np.arange(count, dtype=np.int64) * 4 + align
        for trailing in (0, 1, 4):
            candidates = np.flatnonzero(words.astype(np.int64) + positions + 4 + trailing == target)
            for index in candidates:
                p = offset + int(index) * 4
                for back in range(1, 10):
                    start = p - back
                    va = start - 0x4000
                    decoded = list(cs.disasm(raw[start:p + 4 + trailing], va))
                    if len(decoded) != 1:
                        continue
                    i = decoded[0]
                    if i.size != back + 4 + trailing:
                        continue
                    if not any(o.type == X86_OP_MEM and o.mem.base == X86_REG_RIP
                               and i.address + i.size + o.mem.disp == target for o in i.operands):
                        continue
                    context = list(cs.disasm(raw[start:start + 112], va))
                    rows[va] = {'va': hex(va), 'bytes': i.bytes.hex(),
                                'instruction': i.mnemonic + ' ' + i.op_str,
                                'context': [{'va': hex(c.address), 'bytes': c.bytes.hex(),
                                             'instruction': c.mnemonic + ' ' + c.op_str} for c in context]}
    # Prefer the full prefixed instruction over suffix decodings ending at
    # the same byte. This still does not establish CFG reachability.
    by_end = {}
    for va, row in rows.items():
        end = va + len(bytes.fromhex(row['bytes']))
        if end not in by_end or va < int(by_end[end]['va'], 16):
            by_end[end] = row
    rows = {int(row['va'], 16): row for row in by_end.values()}
    return {'schema': 'd1-atmosphere-type-object-xrefs-v1', 'sha256': EXPECTED_SHA256,
            'target_va': hex(target), 'references': [rows[k] for k in sorted(rows)],
            'boundary': 'RIP references only. Candidate decoding is not reachability proof. Serialized class ID and source payload relationship remain unclosed.'}

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('eboot', type=Path)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--target', type=lambda s: int(s, 0), default=0x28d75b0)
    args = ap.parse_args()
    result = probe(args.eboot, args.target)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result['references']))
