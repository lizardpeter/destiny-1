from __future__ import annotations

from tools.d1_character_family_census import classify_component, connected_components


def facts(**overrides):
    base = {
        "model_parents": [],
        "models": [],
        "skeletons": [],
        "runtime_rigs": [],
        "compositions": [],
        "observed_0767_combatant_components": [],
        "animation_clips": [],
        "animation_wrappers": [],
        "post_animation_controls": [],
        "context_tables": [],
    }
    base.update(overrides)
    return base


def test_model_skeleton_rig_and_clip_promotes_only_to_candidate():
    out = classify_component(facts(
        model_parents=["816CE12B"],
        models=["816CE09A"],
        skeletons=["816CE092"],
        runtime_rigs=["816CE095"],
        animation_clips=["816CE09D", "816CE09E"],
        compositions=["816CE097"],
        observed_0767_combatant_components=["816CE096"],
    ))

    assert out["classification"] == "animated_articulated_entity_candidate"
    assert out["candidate"] is True
    assert out["character_or_combatant_semantic_proven"] is False
    assert out["score"] == 110


def test_model_and_skeleton_without_runtime_rig_is_not_promoted():
    out = classify_component(facts(
        model_parents=["AAAA0001"],
        skeletons=["AAAA0002"],
        animation_clips=["AAAA0003"],
    ))

    assert out["classification"] == "model_skeleton_cluster"
    assert out["candidate"] is False


def test_model_and_animation_without_skeleton_is_unresolved():
    out = classify_component(facts(
        model_parents=["BBBB0001"],
        animation_wrappers=["BBBB0002"],
    ))

    assert out["classification"] == "model_animation_cluster_unresolved"
    assert out["candidate"] is False


def test_connected_components_do_not_bridge_disconnected_graphs():
    graph = {
        "A": {"B"},
        "B": {"A", "C"},
        "C": {"B"},
        "X": {"Y"},
        "Y": {"X"},
    }
    comps = connected_components(set(graph), graph)
    assert comps == [["A", "B", "C"], ["X", "Y"]]
