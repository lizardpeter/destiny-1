# D1 `0767` articulated-asset census

Date: 2026-09-05

This note supersedes any earlier shorthand that treated `ps4_arch_vex_com01_0767_*` as proof of a Vex combatant body.

## Complete skeleton inventory

Using the final logical `_4` namespace with `_0/_1/_4` siblings present, the package family contains exactly five decoded skeleton resources:

```text
816CE092   12 nodes
816CE0DE    3 nodes
816CE06A    1 node
816CE0D9    1 node
816CE0DF    1 node
```

There is **no large humanoid/combatant-sized skeleton in this package family**.

The 12-node skeleton hashes are:

```text
0EB2FACF
5285FA07
2FF610A3
2FF610A0
2FF610A1
D22191F7
BB4A94B5
5E855C4E
EDD486FF
D3D81B52
D3D81B51
EDBA26FB
```

The 3-node skeleton is:

```text
0EB2FACF
D001474F
D001474C
```

The three 1-node skeletons each use `0EB2FACF`.

## Structural census

Latest logical namespace counts:

```text
model parents       6
s_entity_model      6
skeletons           5
runtime rigs        3
compositions        5
animation clips     5
animation wrappers  1
post/action controls 2
```

Only one component is automatically connected strongly enough to qualify as an animated articulated **asset** candidate:

```text
parent       816CE0DC
model        816CE1A4
skeleton     816CE0DE   3 nodes
runtime rig  816CE122   3 controls
composition  816CE109
control      816CE10A
clips        816CE113 / 816CE114 / 816CE115
```

All three clips independently decode and retarget on that 3-node rig.

The independently proven 12-node animation fixture remains:

```text
model        816CE09A
render owner 816CE12B
skeleton     816CE092   12 nodes
runtime rig  816CE095   12 controls
clips        816CE09D / 816CE09E
```

but the generic literal-reference graph still does not connect all of those roles into one gameplay owner component. Its animation compatibility and render ownership are separately proven; its gameplay identity is not.

## Identity conclusion

The evidence now makes the conservative interpretation stronger:

> `0767` is a useful Vex-associated articulated-object / animation-format corpus, but it is **not currently evidence that we have extracted a full Vex enemy character**.

The small skeleton sizes are consistent with environmental machinery, animated props, mechanisms, or sub-objects. They do not by themselves prove any one of those identities, so the exact object identity remains unresolved.

Package family names such as `arch_vex_*` are treated only as architecture/theme association. They are never sufficient to promote a model to `character` or `combatant`.

Canonical discovery interface is now:

```text
tools/d1_articulated_asset_census.py
```

The legacy `d1_character_family_census.py` filename remains only for compatibility. Its old `observed_0767_combatant_component` nickname is not considered semantic evidence; canonical output reframes it as `observed_0767_special_component`.
