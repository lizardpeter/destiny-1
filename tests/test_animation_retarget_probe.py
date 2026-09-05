from __future__ import annotations

from tools.d1_animation_retarget_probe import common_component_prefix


def c(h: str, n: int):
    return {"hash": h, "count": n}


def test_full_runtime_component_match_consumes_all_controls():
    out = common_component_prefix(
        [c("AAAA0001", 8), c("BBBB0002", 62), c("CCCC0003", 3)],
        [c("AAAA0001", 8), c("BBBB0002", 62), c("CCCC0003", 3)],
    )
    assert out["control_limit"] == 73
    assert out["stop_reason"] == "both_exhausted"


def test_shared_prefix_stops_at_first_component_hash_mismatch():
    out = common_component_prefix(
        [c("D59A5FE6", 8), c("7CB60FEC", 62), c("A5D99EA7", 3)],
        [c("D59A5FE6", 8), c("7CB60FEC", 62), c("4FE5F61B", 4)],
    )
    assert out["control_limit"] == 70
    assert out["stop_reason"] == "component_hash_mismatch"
    assert len(out["matched_components"]) == 2


def test_matching_hash_with_different_count_consumes_common_count_then_stops():
    out = common_component_prefix(
        [c("AAAA0001", 12)],
        [c("AAAA0001", 8)],
    )
    assert out["control_limit"] == 8
    assert out["stop_reason"] == "component_count_mismatch"
