from __future__ import annotations

from tools.d1_weapon_action_readiness import build_readiness


def manifest(inv: str, pattern: int | None, *, visual=True, internal=True, shared=True):
    return {
        "inventory_item_hash": inv,
        "inventory_definition": {"name": inv},
        "equipping": {
            "weapon_pattern_index": pattern,
            "art_arrangements": [{"art_arrangement_index": 1229}],
        },
        "status": {
            "visual_entity_selection_resolved": visual,
            "weapon_pattern_resolved": internal,
            "shared_viewmodel_context_resolved": shared,
        },
        "visual": {"entity": "DEADBEEF"},
        "internal_weapon_pattern": {"weapon_pattern_index": pattern},
        "shared_viewmodel": {"profile": "CA2"},
    }


def action(pattern: int, bundles: list[dict]):
    return {
        "weapon_pattern_index": pattern,
        "pattern_entity": "80AA2E00",
        "weapon_type_hash": "CAFEBABE",
        "action_bundles": bundles,
    }


def test_exact_pattern_join_promotes_animation_candidate_without_claiming_equivalence():
    manifests = {"manifests": [manifest("D471D331", 39)]}
    actions = {
        "patterns": [
            action(39, [{
                "carrier_resource": "80AAECD6",
                "action_controls": ["80AA2DCD"],
                "context_tables": ["80AADE4C"],
                "wrappers": ["80AA2DDB"],
            }])
        ]
    }

    out = build_readiness(manifests, actions)

    assert out["summary"]["pattern_action_bundle_ready"] == 1
    assert out["summary"]["shared_and_pattern_action_ready"] == 1
    assert out["summary"]["full_animated_weapon_candidate"] == 1
    row = out["queues"]["full_animated_weapon_candidate"][0]
    assert row["inventory_item_hash"] == "D471D331"
    assert row["weapon_pattern_index"] == 39
    assert row["action_bundles"][0]["carrier_resource"] == "80AAECD6"
    assert row["shared_pattern_equivalence_proven"] is False


def test_weapon_type_similarity_cannot_join_wrong_pattern():
    manifests = {"manifests": [manifest("11111111", 7)]}
    actions = {
        "patterns": [
            {
                **action(8, [{"carrier_resource": "80AA0001"}]),
                "weapon_type_hash": "SAME_TYPE",
            }
        ]
    }

    out = build_readiness(manifests, actions)

    assert out["summary"]["pattern_action_bundle_ready"] == 0
    assert out["summary"]["full_animated_weapon_candidate"] == 0
    assert out["blocked"][0]["blockers"] == ["weapon_pattern_absent_from_action_resolution"]


def test_pattern_without_bundle_remains_blocked_even_when_other_layers_are_ready():
    manifests = {"manifests": [manifest("22222222", 12)]}
    actions = {"patterns": [action(12, [])]}

    out = build_readiness(manifests, actions)

    assert out["summary"]["pattern_action_bundle_ready"] == 0
    assert "weapon_pattern_has_no_exact_action_bundle" in out["blocked"][0]["blockers"]


def test_missing_visual_does_not_block_pattern_action_queue_but_blocks_full_candidate():
    manifests = {"manifests": [manifest("33333333", 3, visual=False)]}
    actions = {"patterns": [action(3, [{"carrier_resource": "80AA0003"}])]}

    out = build_readiness(manifests, actions)

    assert out["summary"]["pattern_action_bundle_ready"] == 1
    assert out["summary"]["shared_and_pattern_action_ready"] == 1
    assert out["summary"]["full_animated_weapon_candidate"] == 0
    assert "visual_entity_selection_unresolved" in out["blocked"][0]["blockers"]
