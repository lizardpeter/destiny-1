#!/usr/bin/env python3
"""Pure fail-closed resolver for proven D1 texture backing chain shapes.

This module does not assign official Tiger names to 65:1 or 5:1.  It only
encodes storage shapes already source/binary closed in D1_RESOURCE_CLASSES.md:
32:1 -> 1:1 direct data and 32:1 -> 65:1 -> 5:1 two-hop data.  TextureCube's
observed direct pair 32:2 -> 1:2 is accepted separately.  Any other adjacency
is rejected rather than followed merely because a reference exists.
"""


def _kind(entry):
    return (entry.get('type'),entry.get('subtype'))


def _lookup(global_by, tag_hash, label):
    if not isinstance(tag_hash,str) or not tag_hash:
        raise ValueError(f'{label} missing reference')
    rec=global_by.get(tag_hash.upper())
    if rec is None:
        raise KeyError(f'{label} unresolved reference {tag_hash.upper()}')
    if not isinstance(rec,tuple) or len(rec)!=2 or not isinstance(rec[1],dict):
        raise TypeError(f'{label} malformed global index record')
    return rec


def resolve_texture_backing(global_by, header_entry):
    """Return ``(first_hop, backing, mode)`` after exact type-shape checks."""
    hk=_kind(header_entry)
    if hk not in {(32,1),(32,2)}:
        raise ValueError(f'not a proven texture header class: {hk}')
    first=_lookup(global_by,header_entry.get('reference'),'texture header')
    fe=first[1]; fk=_kind(fe)

    direct=(1,hk[1])
    if fk==direct:
        return first,first,'direct'

    if hk==(32,1) and fk==(65,1):
        backing=_lookup(global_by,fe.get('reference'),'65:1 first hop')
        bk=_kind(backing[1])
        if bk!=(5,1):
            raise ValueError(f'32:1 -> 65:1 terminal must be 5:1, got {bk}')
        return first,backing,'two_hop_65_1_to_5_1'

    raise ValueError(f'unproven texture backing chain {hk} -> {fk}')
