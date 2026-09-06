#!/usr/bin/env python3
"""Resolve Destiny 1 ROI global Tag identity without conflating tag class and schema.

Pinned Charm source gives two independent kinds of evidence for D1 global Tags:

1. A typed serialized edge, e.g. `Tag<SBubbleDefinition>`, tells the deserializer which
   SchemaStruct to use for the target payload.
2. `FileHash.GetReferenceFromManifest()` follows the target's ordinary file-entry
   Reference to an `S48018080` manifest parent. That parent stores a TagClassHash at
   +0x0C and the target FileHash backlink at +0x10.

Those values are NOT interchangeable. Tower proves this directly: five source-typed
`Tag<SBubbleDefinition>` children have structurally valid S48018080 parents/backlinks,
but every parent stores manifest TagClassHash 80800580 while the D1 SBubbleDefinition
SchemaStruct identifier is 808091E0 (Charm E0918080).

Therefore this module exposes two APIs:

- `resolve_manifest_identity`: prove the D1 global-tag parent/backlink and preserve its
  manifest TagClassHash exactly.
- `resolve_typed_tag`: validate a source-typed Tag<T>. A direct file-entry schema class
  is accepted directly; otherwise a valid S48018080 identity/backlink proves the target
  identity while the caller's typed schema supplies the expected payload interpretation.

`resolve_tag_class` remains the strict manifest-tag-class comparison helper for cases
where the caller genuinely wants TagClassHash equality. It must not be used to reject a
source-typed Tag<T> merely because TagClassHash differs from SchemaStruct class hash.
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


def resolve_manifest_identity(c, tag_hash: str) -> dict:
    """Prove a D1 global Tag's S48018080 parent and +0x10 backlink."""
    h = norm(tag_hash)
    meta = c.entry_meta(h)
    out = {
        'hash': h,
        'exists': meta is not None,
        'meta': meta,
        'ordinary_reference': None,
        'manifest_parent': None,
        'manifest_identity_valid': False,
        'manifest_tag_class': None,
        'violations': [],
    }
    if not meta:
        out['violations'].append('tag_missing')
        return out

    parent_hash = norm(meta.get('reference', ''))
    out['ordinary_reference'] = parent_hash
    parent_meta = c.entry_meta(parent_hash)
    parent = {
        'hash': parent_hash,
        'exists': parent_meta is not None,
        'meta': parent_meta,
        'payload_source': None,
        'payload_bytes': None,
        'declared_file_size': None,
        'parent_reference': None,
        'parent_reference_is_S48018080': False,
        'manifest_tag_class': None,
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

    parent_ref = norm(parent_meta.get('reference', ''))
    parent['parent_reference'] = parent_ref
    parent['parent_reference_is_S48018080'] = parent_ref == MANIFEST_PARENT
    if not parent['parent_reference_is_S48018080']:
        parent['violations'].append(
            f'manifest_parent_class_mismatch:{parent_ref}!={MANIFEST_PARENT}'
        )
        out['violations'].append('manifest_parent_class_mismatch')
        return out

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
    parent['manifest_tag_class'] = cls
    parent['tag_hash'] = child
    parent['tag_matches_original'] = child == h
    parent['structurally_valid'] = (
        parent['parent_reference_is_S48018080'] and parent['tag_matches_original']
    )
    out['manifest_tag_class'] = cls

    if not parent['tag_matches_original']:
        parent['violations'].append(f'manifest_parent_tag_mismatch:{child}!={h}')
        out['violations'].append('manifest_parent_tag_mismatch')
        return out

    out['manifest_identity_valid'] = True
    return out


def resolve_tag_class(c, tag_hash: str, expected: str | None = None) -> dict:
    """Strictly compare a D1 Tag's direct/manifest TagClassHash to `expected`."""
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
        'manifest_tag_class': None,
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

    identity = resolve_manifest_identity(c, h)
    out['manifest_parent'] = identity.get('manifest_parent')
    out['manifest_tag_class'] = identity.get('manifest_tag_class')
    if not identity.get('manifest_identity_valid'):
        out['violations'].extend(identity.get('violations', []))
        return out

    cls = norm(identity['manifest_tag_class'])
    out['resolution_mode'] = 'd1_manifest_parent_S48018080_tag_class'
    out['resolved_class'] = cls
    out['reference_matches'] = expected is None or cls == expected
    if expected is not None and cls != expected:
        out['violations'].append(f'manifest_tag_class_mismatch:{cls}!={expected}')
    return out


def resolve_typed_tag(c, tag_hash: str, expected_schema: str) -> dict:
    """Validate identity for a source-typed D1 `Tag<T>` edge.

    The caller supplies `expected_schema` from the pinned serialized field type. A direct
    ordinary Reference equal to that schema is complete class-direct evidence. If the
    ordinary Reference is a FileHash instead, a valid S48018080 parent/backlink proves
    the target identity; its manifest TagClassHash is preserved but is not required to
    equal the SchemaStruct identifier.
    """
    h = norm(tag_hash)
    expected = norm(expected_schema)
    meta = c.entry_meta(h)
    out = {
        'hash': h,
        'exists': meta is not None,
        'meta': meta,
        'expected_reference': expected,  # compatibility with existing reports
        'expected_schema': expected,
        'resolution_mode': None,
        'resolved_schema': None,
        'resolved_class': None,
        'reference_matches': False,      # compatibility: means typed target accepted
        'typed_target_valid': False,
        'manifest_parent': None,
        'manifest_tag_class': None,
        'manifest_tag_class_matches_schema': None,
        'schema_evidence': None,
        'violations': [],
    }
    if not meta:
        out['violations'].append('tag_missing')
        return out

    direct = norm(meta.get('reference', ''))
    out['ordinary_reference'] = direct
    if direct == expected:
        out['resolution_mode'] = 'direct_file_entry_schema_reference'
        out['resolved_schema'] = expected
        out['resolved_class'] = expected
        out['schema_evidence'] = 'DIRECT_FILE_ENTRY_REFERENCE'
        out['typed_target_valid'] = True
        out['reference_matches'] = True
        return out

    identity = resolve_manifest_identity(c, h)
    out['manifest_parent'] = identity.get('manifest_parent')
    out['manifest_tag_class'] = identity.get('manifest_tag_class')
    if not identity.get('manifest_identity_valid'):
        out['violations'].extend(identity.get('violations', []))
        return out

    manifest_cls = norm(identity['manifest_tag_class'])
    out['manifest_tag_class_matches_schema'] = manifest_cls == expected
    out['resolution_mode'] = 'd1_manifest_identity_plus_source_typed_schema'
    out['resolved_schema'] = expected
    # Keep compatibility while making the semantic distinction visible.
    out['resolved_class'] = expected
    out['schema_evidence'] = 'PINNED_SOURCE_TYPED_TAG_EDGE_PLUS_S48018080_BACKLINK'
    out['typed_target_valid'] = True
    out['reference_matches'] = True
    return out


def current_hashes_by_class(c, expected: str) -> list[str]:
    """Strictly enumerate hashes whose direct/manifest TagClassHash equals expected."""
    expected = norm(expected)
    out = []
    for h in c.occ:
        r = resolve_tag_class(c, h, expected)
        if r.get('reference_matches'):
            out.append(norm(h))
    return sorted(set(out))
