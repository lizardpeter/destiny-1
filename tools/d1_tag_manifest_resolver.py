#!/usr/bin/env python3
"""Resolve Destiny 1 ROI Tag identity without conflating entry class and schema type.

Pinned Charm source gives three distinct pieces of evidence for a D1 typed Tag edge:

1. The serialized field type, e.g. `Tag<SBubbleDefinition>` or `Tag<SMapContainer>`,
   tells `GetSchemaTag<T>` which SchemaStruct to use for the target FileHash.
2. Some global Tags have an ordinary file-entry Reference that is itself a FileHash to
   an `S48018080` manifest parent. That parent stores a TagClassHash at +0x0C and the
   target FileHash backlink at +0x10.
3. Other typed Tags have an ordinary file-entry Reference that is a non-schema class
   value. Charm does not require that value to equal the SchemaStruct id before opening
   `Tag<T>`; the source-typed field chooses T and the target payload is then deserialized.

Those values are NOT interchangeable. Tower proves both non-equalities directly:

- five source-typed `Tag<SBubbleDefinition>` children have valid S48018080 parents with
  manifest TagClassHash 80800580 while SBubbleDefinition SchemaStruct is 808091E0;
- their source-typed `Tag<SMapContainer>` children exist with ordinary Reference
  80800343 while SMapContainer SchemaStruct is 80808A54.

Therefore:

- `resolve_manifest_identity` proves only the optional D1 global manifest parent/backlink;
- `resolve_tag_class` is a strict helper for callers that genuinely need class equality;
- `resolve_typed_tag` mirrors Charm's typed `GetSchemaTag<T>` semantics. Existence plus
  the pinned source-typed edge is enough to attempt the target schema. Direct schema or
  valid manifest identity are stronger identity evidence, but not prerequisites. The
  caller must still validate the target payload structurally before promoting the edge.
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
    """Prove a D1 global Tag's S48018080 parent and +0x10 backlink when present."""
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
    """Resolve a source-typed D1 `Tag<T>` target for structural validation.

    This mirrors Charm's `GetSchemaTag<T>(FileHash)`: once a serialized source field is
    known to be `Tag<T>`, the FileHash is opened as T without first requiring the package
    entry Reference or manifest TagClassHash to equal T's SchemaStruct identifier.

    The returned `typed_target_valid` therefore means "the typed target exists and may be
    deserialized as the source-declared schema". It is not final schema proof by itself;
    callers must validate schema-specific payload bounds/fields before promotion.
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
        'reference_matches': False,      # compatibility: typed target accepted
        'typed_target_valid': False,
        'requires_payload_validation': True,
        'manifest_parent': None,
        'manifest_identity_valid': False,
        'manifest_tag_class': None,
        'manifest_tag_class_matches_schema': None,
        'schema_evidence': None,
        'ordinary_reference_matches_schema': None,
        'violations': [],
    }
    if not meta:
        out['violations'].append('tag_missing')
        return out

    direct = norm(meta.get('reference', ''))
    out['ordinary_reference'] = direct
    out['ordinary_reference_matches_schema'] = direct == expected
    out['resolved_schema'] = expected
    out['resolved_class'] = expected

    if direct == expected:
        out['resolution_mode'] = 'direct_file_entry_schema_reference'
        out['schema_evidence'] = 'PINNED_SOURCE_TYPED_TAG_EDGE_PLUS_DIRECT_SCHEMA_REFERENCE'
        out['typed_target_valid'] = True
        out['reference_matches'] = True
        return out

    # Try to strengthen identity through the optional global-tag manifest path. Failure
    # here is not a typed-edge failure: the ordinary Reference may simply be a direct
    # non-schema tag-class value, as Tower SMapContainer children demonstrate (80800343).
    identity = resolve_manifest_identity(c, h)
    out['manifest_parent'] = identity.get('manifest_parent')
    out['manifest_identity_valid'] = bool(identity.get('manifest_identity_valid'))
    out['manifest_tag_class'] = identity.get('manifest_tag_class')
    if identity.get('manifest_identity_valid'):
        manifest_cls = norm(identity['manifest_tag_class'])
        out['manifest_tag_class_matches_schema'] = manifest_cls == expected
        out['resolution_mode'] = 'd1_manifest_identity_plus_source_typed_schema'
        out['schema_evidence'] = 'PINNED_SOURCE_TYPED_TAG_EDGE_PLUS_S48018080_BACKLINK'
    else:
        # Do not copy the manifest-probe violations into typed-edge violations: a failed
        # S48018080 probe is expected for class-direct typed Tags. Preserve the probe in
        # manifest_parent for diagnostics and require the caller's payload validation.
        out['resolution_mode'] = 'source_typed_schema_plus_existing_target'
        out['schema_evidence'] = 'PINNED_SOURCE_TYPED_TAG_EDGE_TARGET_EXISTS_PAYLOAD_MUST_VALIDATE'

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
