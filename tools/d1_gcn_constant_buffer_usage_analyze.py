#!/usr/bin/env python3
"""Map CLRX GCN scalar-buffer loads to PS4 OrbShdr constant-buffer slots.

Consumes the exact shader extraction report (which includes Sony InputUsageSlot metadata)
and CLRX raw GFX700 disassemblies. The analysis is intentionally mechanical:

* ImmConstBuffer usage records provide API slot and starting SGPR.
* s_buffer_load_* instructions are parsed for their scalar resource descriptor SGPR range
  and immediate byte/dword offset where statically encoded.
* A load is assigned to an API constant-buffer slot only when its descriptor start SGPR
  exactly matches an OrbShdr ImmConstBuffer usage slot.

No semantic name (colour/intensity/range/etc.) is assigned to a constant offset here.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

LOAD_RE = re.compile(r'\bs_buffer_load_dword(?P<width>x2|x4|x8|x16)?\s+[^,]+,\s*(?P<desc>s\[[0-9]+:[0-9]+\]|s[0-9]+)\s*,\s*(?P<off>[^\s;/]+)', re.I)
RANGE_RE = re.compile(r's\[(\d+):(\d+)\]', re.I)
SINGLE_RE = re.compile(r's(\d+)', re.I)


def desc_start(x: str) -> int | None:
    m = RANGE_RE.fullmatch(x)
    if m:
        return int(m.group(1))
    m = SINGLE_RE.fullmatch(x)
    return int(m.group(1)) if m else None


def parse_imm(x: str) -> int | None:
    x = x.rstrip(',')
    try:
        return int(x, 0)
    except Exception:
        return None


def width_dwords(suffix: str | None) -> int:
    return {None: 1, 'x2': 2, 'x4': 4, 'x8': 8, 'x16': 16}[suffix.lower() if suffix else None]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--extract-report', type=Path, required=True)
    ap.add_argument('--disasm-dir', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()

    rep = json.loads(a.extract_report.read_text())
    rows = []
    total_loads = 0
    mapped_loads = 0
    unmatched = 0
    slot_hist = Counter()
    slot_offset_hist: dict[str, Counter] = defaultdict(Counter)
    violations = []

    for sh in rep.get('shaders', []):
        h = str(sh['shader']).upper()
        usage = (sh.get('usage') or {}).get('slots', [])
        cb_by_reg = {}
        for u in usage:
            if u.get('usage_name') == 'ImmConstBuffer':
                cb_by_reg[int(u['start_register'])] = {
                    'api_slot': int(u['api_slot']),
                    'start_register': int(u['start_register']),
                    'raw_usage': u,
                }
        path = a.disasm_dir / f'PS_{h}.s'
        if not path.exists():
            violations.append(f'{h}:missing_disassembly')
            continue
        loads = []
        lines = path.read_text(errors='replace').splitlines()
        for lineno, line in enumerate(lines, 1):
            m = LOAD_RE.search(line)
            if not m:
                continue
            total_loads += 1
            ds = desc_start(m.group('desc'))
            imm = parse_imm(m.group('off'))
            width = width_dwords(m.group('width'))
            cb = cb_by_reg.get(ds) if ds is not None else None
            mapped = cb is not None
            mapped_loads += int(mapped)
            unmatched += int(not mapped)
            row = {
                'line_number': lineno,
                'line': line.strip(),
                'descriptor_operand': m.group('desc'),
                'descriptor_start_register': ds,
                'width_dwords': width,
                'offset_operand': m.group('off'),
                'static_offset': imm,
                'constant_buffer': cb,
            }
            if cb:
                slot = str(cb['api_slot'])
                slot_hist[slot] += 1
                if imm is not None:
                    slot_offset_hist[slot][str(imm)] += 1
            loads.append(row)
        rows.append({
            'shader': h,
            'imm_constant_buffers': list(cb_by_reg.values()),
            'scalar_buffer_load_count': len(loads),
            'mapped_load_count': sum(x['constant_buffer'] is not None for x in loads),
            'loads': loads,
        })

    out = {
        'schema_version': 1,
        'status': 'D1_GCN_CONSTANT_BUFFER_USAGE_ANALYZED' if not violations else 'D1_GCN_CONSTANT_BUFFER_USAGE_PARTIAL',
        'shader_count': len(rows),
        'total_scalar_buffer_load_count': total_loads,
        'mapped_constant_buffer_load_count': mapped_loads,
        'unmatched_scalar_buffer_load_count': unmatched,
        'constant_buffer_api_slot_histogram': dict(slot_hist),
        'constant_buffer_static_offset_histograms': {k: dict(v) for k, v in sorted(slot_offset_hist.items())},
        'shaders': rows,
        'violations': violations,
        'policy': 'Mechanical OrbShdr InputUsageSlot to GCN descriptor-register mapping only; no light-parameter semantics inferred.',
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({k: out[k] for k in (
        'status','shader_count','total_scalar_buffer_load_count','mapped_constant_buffer_load_count',
        'unmatched_scalar_buffer_load_count','constant_buffer_api_slot_histogram','constant_buffer_static_offset_histograms','violations')}, indent=2))
    return 0 if not violations else 2


if __name__ == '__main__':
    raise SystemExit(main())
