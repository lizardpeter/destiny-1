from __future__ import annotations

from tools.d1_action_control_signature_compare import compare_controls


def report(tag: str, rows: list[dict], animations: int = 4):
    return {
        "control": {"tag_hash": tag},
        "animation_list": {"count": animations},
        "state_table": {"count": len(rows), "records": rows},
    }


def row(h: str, idx: int, clips: list[str], name: str | None = None):
    return {
        "state_hash": h,
        "state_name": name,
        "record_index": idx,
        "selection_start": 0,
        "selection_count": len(clips),
        "selected_animations": [{"tag_hash": x} for x in clips],
    }


def test_exact_clip_similarity_never_promotes_ownership():
    a = report("AAAA0001", [row("6FB760FF", 0, ["CCCC0001"], "idle")])
    b = report("BBBB0001", [row("6FB760FF", 0, ["CCCC0001"], "idle")])

    out = compare_controls(a, b)

    assert out["same_action_hash_set"] is True
    assert out["exact_clip_match_count"] == 1
    assert out["exact_record_index_match_count"] == 1
    assert out["ownership_equivalence_proven"] is False


def test_different_selector_indexes_and_clips_are_reported_literally():
    a = report("AAAA0001", [
        row("6FB760FF", 0, ["CCCC0001"], "idle"),
        row("9FAC79C9", 5, ["CCCC0002"], "fire"),
    ])
    b = report("BBBB0001", [
        row("6FB760FF", 13, ["CCCC0001"], "idle"),
        row("9FAC79C9", 12, ["DDDD0001"], "fire"),
        row("E480E089", 39, ["DDDD0002", "DDDD0003"], "jump"),
    ])

    out = compare_controls(a, b)

    assert out["common_action_count"] == 2
    assert out["left_only_action_count"] == 0
    assert out["right_only_action_count"] == 1
    assert out["same_action_hash_set"] is False
    idle = next(x for x in out["common_actions"] if x["state_name"] == "idle")
    fire = next(x for x in out["common_actions"] if x["state_name"] == "fire")
    assert idle["same_exact_clips"] is True
    assert idle["same_record_index"] is False
    assert fire["same_exact_clips"] is False
