#!/usr/bin/env python3
"""Resolve Destiny 1 ROI Tag classes through the shared-manifest parent layer.

D1 global/named Tags are different from ordinary class-direct package entries. Charm's
pinned D1 implementation expresses this explicitly in FileHash.GetReferenceFromManifest:

    original TagHash
      -> ordinary file-entry Reference interpreted as a FileHash
      -> S48018080 manifest parent
           +0x0C TagClassHash
           +0x10 FileHash Tag

Pinned source:
  MontagueM/Charm@50d36ee1f9ecadad7522504c20b1f3f9c97e30af
  Tiger/TigerHash.cs::GetReferenceFromManifest
  Tiger/Schema/Activity/ActivityStructsROI.cs::S48018080

Project canonical/raw uint class for Charm display 48018080 is 80800148.

This helper never guesses a class from payload shape. A Tag matches an expected class
only if either:

1. its current ordinary file-entry Reference is already that class (class-direct Tag), or
2. that Reference resolves to a manifest-parent payload whose +0x10 Tag equals the
   original TagHash and whose +0x0C TagClassHash equals the expected class.

Missing shared-manifest packages remain explicit unresolved evidence.
"""
from __future__ import annotations

import struct

MANIFEST_PARENT = '80800148'  # Charm schema display 48018080


def norm(x: object) -> str:
    return str(x).upper().removeprefix('0X').zfill(8)


def hx(v: int) -> str:
    return f'{v:08X}'


def u32(b: bytes, o: int) -> int:
    return struct.unpack_from('<I', b, o)[0]


def i64(b: bytes, o: int) -> int:
    return struct.unpack_from('<q', b, o)[0]


def resolve_tag_class(c, tag_hash: str, expected: str | None = None) -> dict:
    """Resolve current D1 Tag class via direct Reference or S48018080 manifest parent."""
    h = norm(tag_hash)
    expected = norm(expected) if expected is not None else None
    meta = c.entry_meta(h)
    out = {
        'hash': h,
        'exists': meta is not None,
        'meta': meta,
        'expected_reference': expected,
        'resolution_mode': None,
        'resolved_class': None,
        'reference_matches': False,
        'manifest_parent': None,
        'violations': [],
    }
    if not meta:
        out['violations'].append('tag_missing')
        return out

    direct = norm(meta.get('reference', ''))
    out['ordinary_reference'] = direct
    if expected is not None and direct == expected:
        out['resolution_mode'] = 'direct_file_entry_reference'
        out['resolved_class'] = direct
        out['reference_matches'] = True
        return out

    # D1 global Tag path: ordinary Reference is a FileHash naming S48018080.
    parent_hash = direct
    parent_meta = c.entry_meta(parent_hash)
    parent = {
        'hash': parent_hash,
        'exists': parent_meta is not None,
        'meta': parent_meta,
        'payload_source': None,
        'payload_bytes': None,
        'declared_file_size': None,
        'parent_reference_is_S48018080': False,
        'class_hash': None,
        'tag_hash': None,
        'tag_matches_original': False,
        'structurally_valid': False,
        'violations': [],
    }
    out['manifest_parent'] = parent
    if not parent_meta:
        parent['violations'].append('manifest_parent_missing')
        out['violations'].append('manifest_parent_missing')
        return out

    parent['parent_reference_is_S48018080'] = norm(parent_meta.get('reference', '')) == MANIFEST_PARENT
    pb, psrc = c.payload(parent_hash)
    parent['payload_source'] = psrc
    if pb is None:
        parent['violations'].append('manifest_parent_payload_unavailable')
        out['violations'].append('manifest_parent_payload_unavailable')
        return out
    parent['payload_bytes'] = len(pb)
    if len(pb) < 0x14:
        parent['violations'].append('manifest_parent_payload_shorter_than_0x14')
        out['violations'].append('manifest_parent_payload_shorter_than_0x14')
        return out

    parent['declared_file_size'] = i64(pb, 0x00)
    cls = hx(u32(pb, 0x0C))
    child = hx(u32(pb, 0x10))
    parent['class_hash'] = cls
    parent['tag_hash'] = child
    parent['tag_matches_original'] = child == h
    parent['structurally_valid'] = parent['tag_matches_original']

    if not parent['tag_matches_original']:
        parent['violations'].append(f'manifest_parent_tag_mismatch:{child}!={h}')
        out['violations'].append('manifest_parent_tag_mismatch')
        return out

    out['resolution_mode'] = 'd1_manifest_parent_S48018080'
    out['resolved_class'] = cls
    out['reference_matches'] = expected is None or cls == expected
    if expected is not None and cls != expected:
        out['violations'].append(f'manifest_class_mismatch:{cls}!={expected}')
    return out


def current_hashes_by_class(c, expected: str) -> list[str]:
    """Enumerate current TagHashes whose class resolves by either supported D1 path."""
    expected = norm(expected)
    out = []
    for h in c.occ:
        r = resolve_tag_class(c, h, expected)
        if r.get('reference_matches'):
            out.append(norm(h))
    return sorted(set(out))
