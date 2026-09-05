# PS4 D1 shared viewmodel owner and runtime-component retargeting

## Status

Resolved 2026-09-05. This closes the earlier Gjallarhorn ambiguity around the shared 76-node / 74-control idle, ready, and jump clips.

The earlier test harness incorrectly treated clip `node_count` / `rig_control_count` as a hard compatibility gate and therefore refused to try a 76/74 clip on the serialized CA2 75/73 owner rig. Destiny's runtime-retarget model does not work that way.

## Exact serialized owner families

The three shared viewmodel `s_entity` owners and their exact Resource[]-owned skeleton/rig/control/wrapper families are:

```text
80AA3CA0
  skeleton 80AA3CB3  (76 nodes)
  rig      80AA3CB2  (74 controls)
  control  80AA3CC2  (80802C0E)
  wrapper  80AA3CC4  (8080222A)

80AA3CA1
  skeleton 80AA3CB9  (76 nodes)
  rig      80AA3CB8  (74 controls)
  control  80AA3CC5  (80802C0E)
  wrapper  80AA3CC7  (8080222A)

80AA3CA2
  skeleton 80AA3CBF  (75 nodes)
  rig      80AA3CBE  (73 controls)
  control  80AA3CC9  (80802C0E)
  wrapper  80AA3CCB  (8080222A)
```

The owner-specific 0157 context resources serialize those pairs directly:

```text
80AAF413 -> 80AA3CC2 / 80AA3CC4
80AAF416 -> 80AA3CC5 / 80AA3CC7
80AAF419 -> 80AA3CC9 / 80AA3CCB
```

Therefore CA2 -> CBE/CBF -> CC9/CCB is a byte-backed ownership relationship, not adjacency or a dimensional guess.

## Sibling action selectors

All three controls select the same generic clips for several shared actions:

```text
idle   -> 80AA3CD6
ready  -> 80AA3CDA
jump   -> 80AA3CE2 + 80AA3CE3
```

They diverge for family-specific reload/fire:

```text
CA0: reload -> 80AA3CDB ; fire -> 80AA3CEC
CA1: reload -> 80AA3D2A ; fire -> 80AA3D2B
CA2: reload -> 80AA3D40 ; fire -> 80AA3D42
```

Thus clip identity alone cannot choose CA0 vs CA1 for the generic actions and must not be used as an owner discriminator.

## Why 76/74 generic clips are valid on CA2 75/73

`tiger-animation-parser`'s D1 runtime retargeter uses the clip's `runtime_rig_components` and the target runtime rig's component list. `calc_control_limit()` consumes matching component hashes in order. If a component hash differs, retargeting stops at the compatible prefix; raw total control counts are not a hard equality requirement.

CA2 runtime rig `80AA3CBE` is:

```text
D59A5FE6 : 8 controls
7CB60FEC : 62 controls
A5D99EA7 : 3 controls
----------------------
             73 total
```

The shared generic clips `80AA3CD6`, `80AA3CDA`, `80AA3CE2`, and `80AA3CE3` are:

```text
D59A5FE6 : 8 controls
7CB60FEC : 62 controls
4FE5F61B : 4 controls
----------------------
             74 total
```

The first two runtime-rig components match exactly, so the native compatible control limit is:

```text
8 + 62 = 70 controls
```

The third component hash differs, so retargeting intentionally stops there. The generic clips decode and retarget onto CA2's 75-node skeleton successfully, producing 75 local bone tracks.

By contrast, CA2's family-specific reload and fire clips exactly match all three CA2 components:

```text
80AA3D40 reload:
  D59A5FE6:8, 7CB60FEC:62, A5D99EA7:3 -> control limit 73

80AA3D42 fire:
  D59A5FE6:8, 7CB60FEC:62, A5D99EA7:3 -> control limit 73
```

## Cross-rig no-prefilter regression

Workflow:

```text
.github/workflows/tmp-d1-cross-rig-retarget-no-prefilter.yml
```

The regression actually runs:

```text
decode_animation
-> rig_retarget
-> convert_obj_to_local
```

for every selected generic/family clip against all three owner rigs with no count prefilter.

For the Gjallarhorn-relevant CA2 owner:

```text
80AA3CD6  76/74 -> CA2 75/73 : success, 75 retargeted/local tracks, limit 70
80AA3CDA  76/74 -> CA2 75/73 : success, 75 retargeted/local tracks, limit 70
80AA3CE2  76/74 -> CA2 75/73 : success, 75 retargeted/local tracks, limit 70
80AA3CE3  76/74 -> CA2 75/73 : success, 75 retargeted/local tracks, limit 70
80AA3D40  75/73 -> CA2 75/73 : success, 75 retargeted/local tracks, limit 73
80AA3D42  75/73 -> CA2 75/73 : success, 75 retargeted/local tracks, limit 73
```

Successful component-proof run: `33938962989` at commit `4e3f720527972890b28c1750518e55ce226ee071`.

## Wrapper state wiring

The `8080222A` wrappers also contain an action-hash -> local state index map and nested `8080200E` state resources. In CA2 wrapper `80AA3CCB`, the first `80802831` small index for each known action is exactly the corresponding selector-record index in `80AA3CC9`:

```text
reload_empty -> 0
reload_full  -> 1
fire         -> 5
idle         -> 13
ready        -> 14
jump         -> 39
```

This proves the wrapper is wiring nested state behavior back to exact records in its own owner control. It does not point generic idle/ready/jump to a different owner family.

## Correct conclusion for Gjallarhorn

Do not switch Gjallarhorn idle/ready/jump to CA0 or CA1 because the clip header says 76/74.

The exact path is:

```text
CA2 s_entity 80AA3CA2
  -> runtime rig / skeleton 80AA3CBE / 80AA3CBF
  -> action control / wrapper 80AA3CC9 / 80AA3CCB
  -> generic actions retarget through the 70-control common runtime-component prefix
  -> CA2-specific reload/fire consume all 73 controls
```

This removes the final count-based rig-selection guess from the Gjallarhorn shared-action path.
