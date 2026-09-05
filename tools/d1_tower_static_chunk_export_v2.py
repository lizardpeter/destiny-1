#!/usr/bin/env python3
"""D1 Tower baked-static exporter v2: support the retail null Vertices1 sentinel.

This is a narrow compatibility layer over d1_tower_static_chunk_export.py. The base
exporter currently resolves V1 for provenance/stride reporting even though geometry is
decoded only from V0 + index. Validator v2 proves that retail D1 uses exactly
FFFFFFFF for an absent secondary V1/UV stream.

Safety boundary:
- V0 and index behavior are unchanged and remain mandatory.
- Only header hash FFFFFFFF is treated as absent V1.
- No buffer bytes are fabricated.
- The sentinel is recorded explicitly with null provenance and stride 0.
- All placement/index/material semantics still come from the validator-passing report.
"""
from __future__ import annotations
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import d1_tower_static_chunk_export as base

NULL='FFFFFFFF'
_original_read_reference_file=base.read_reference_file
_original_hdr_stride=base.hdr_stride


def read_reference_file_v2(c, header_hash: str):
    hh=base.norm_hash(header_hash)
    if hh != NULL:
        return _original_read_reference_file(c,hh)
    return {
        'header_hash':NULL,
        'header':None,
        'header_source':None,
        'header_meta':{'null_secondary_stream':True,'serialized_hash':NULL},
        'backing_hash':NULL,
        'backing':b'',
        'backing_source':None,
        'backing_meta':{'null_secondary_stream':True,'serialized_hash':NULL},
    }


def hdr_stride_v2(header):
    if header is None:
        return 0
    return _original_hdr_stride(header)


base.read_reference_file=read_reference_file_v2
base.hdr_stride=hdr_stride_v2

if __name__=='__main__':
    raise SystemExit(base.main())
