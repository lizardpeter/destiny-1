#!/usr/bin/env python3
"""Source-prove the GFX7 v_madmk_f32 operation used by D1 shader lifting.

This supplemental proof is intentionally small so an independently green renderer
checkpoint does not need its entire established VOP contract regenerated merely to
add one opcode family. It may later be folded into the consolidated VOP semantics
registry after downstream consumers are green.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--vop2-source', type=Path, required=True)
    ap.add_argument('--vop2-revision', required=True)
    ap.add_argument('-o', '--output', type=Path, required=True)
    a = ap.parse_args()
    violations = []
    proof = {}
    try:
        text = a.vop2_source.read_text(errors='replace')
        equation = '// D.f = S0.f * K + S1.f; K is a 32-bit inline constant.'
        no_mods = '// This opcode cannot use the VOP3 encoding and cannot use input/output'
        no_mods2 = '// modifiers.'
        assert 'Inst_VOP2__V_MADMK_F32' in text
        assert equation in text
        assert no_mods in text and no_mods2 in text
        proof = {
            'opcode': 'v_madmk_f32',
            'operation': 'MADMK',
            'equation': 'D = S0 * K + S1',
            'constant_kind': '32_BIT_INLINE_CONSTANT',
            'input_output_modifiers': 'NOT_SUPPORTED',
            'vop3_encoding': 'NOT_SUPPORTED',
            'source_revision': a.vop2_revision,
            'source_file_sha256': sha(a.vop2_source),
            'source_literals': [equation, no_mods, no_mods2],
        }
    except Exception as exc:
        violations.append(repr(exc))
    out = {
        'schema_version': 1,
        'status': 'D1_GCN_V_MADMK_F32_SEMANTICS_SOURCE_PROVEN' if proof and not violations else 'D1_GCN_V_MADMK_F32_SEMANTICS_PARTIAL',
        'semantics': proof,
        'violations': violations,
        'policy': 'Only literal immutable upstream AMDGPU semantics are promoted; shader/material intent is not inferred.',
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps(out, indent=2))
    return 0 if not violations else 2


if __name__ == '__main__':
    raise SystemExit(main())
