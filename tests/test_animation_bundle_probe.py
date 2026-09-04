from __future__ import annotations

import struct

from tools.d1_animation_bundle_probe import aligned_u32_matches, classify_pattern


def test_aligned_u32_matches_only_accepts_aligned_dwords():
    payload = bytearray(32)
    struct.pack_into("<I", payload, 4, 0xD3FD602F)
    # Same bytes at an unaligned location must not become evidence.
    payload[13:17] = bytes.fromhex("FF60B76F")

    hits = aligned_u32_matches(bytes(payload), ["D3FD602F", "6FB760FF"])

    assert hits == {"D3FD602F": [4]}


def assert_render_ownership_not_assessed(result):
    assert result["render_ownership_assessed"] is False
    assert result["render_ownership_conclusion"] == "not_assessed"
    # Deprecated compatibility key must never encode false negative evidence.
    assert result["final_render_model_proven"] is None


def test_hash_correlated_bundle_pattern_requires_model_clip_and_havok():
    result = classify_pattern(
        model_count=1,
        clip_count=2,
        havok_count=1,
        known_animation_hash_match_count=1,
    )

    assert result["classification"] == "hash_correlated_animation_bundle_pattern"
    assert result["animation_bundle_candidate"] is True
    assert result["proxy_candidate"] is True
    assert_render_ownership_not_assessed(result)


def test_wrapper_plus_model_alone_is_not_promoted_to_bundle():
    result = classify_pattern(
        model_count=1,
        clip_count=0,
        havok_count=0,
        known_animation_hash_match_count=0,
    )

    assert result["classification"] == "wrapper_plus_model_unresolved"
    assert result["animation_bundle_candidate"] is False
    assert result["proxy_candidate"] is False
    assert_render_ownership_not_assessed(result)


def test_animation_side_without_model_is_not_promoted():
    result = classify_pattern(
        model_count=0,
        clip_count=1,
        havok_count=1,
        known_animation_hash_match_count=1,
    )

    assert result["classification"] == "wrapper_only_unresolved"
    assert result["animation_bundle_candidate"] is False
    assert result["proxy_candidate"] is False
    assert_render_ownership_not_assessed(result)
