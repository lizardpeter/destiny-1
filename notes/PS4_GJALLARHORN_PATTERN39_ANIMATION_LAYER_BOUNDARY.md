# Destiny 1 PS4 Gjallarhorn pattern-39 animation-layer boundary

Date: 2026-09-05

## Proven pattern-specific internal rig

Gjallarhorn Year 3 weapon pattern 39 (`80A6A017`) directly owns:

- skeleton EntityResource `80AA3C97`
- runtime rig EntityResource `80AA2D6D`
- animation control `80AA2DCD`
- directly serialized clips `80AA2E4A` and `80AA2E4B`

The skeleton has 7 bones. The completed arrangement-1229 GLB uses exact per-vertex rigid joint indices stored in primary vertex-stream int16 lane 3, with all 9,801 vertices in the range 0..6.

## Complete 0151 control census

Workflow run `33931817445` (`Census Gjallarhorn firing animation candidates`) scanned every resident class-`80802C0E` control in the complete logical `ps4_globals_0151` package and resolved aligned references to class-`808005A1` animation clips.

Results:

- 17 animation controls contained clip references.
- 342 unique control-referenced clips were found.
- Every referenced clip was parsed with the pinned D1 ROI animation parser.
- Every clip with `node_count == 7` and `rig_control_count == 7` was retarget-tested against exact Gjallarhorn skeleton `80AA3C97` and runtime rig `80AA2D6D`.
- Exactly two clips matched:
  - `80AA2E4A`: 115 frames, 3.8 s, control `80AA2DCD` offset `0xB0`.
  - `80AA2E4B`: 31 frames, 1.0 s, control `80AA2DCD` offset `0xB4`.
- No other one of the 342 control-referenced clips is a 7-node/7-control Gjallarhorn-rig clip.

This closes the question of whether a separate firing clip is merely missing from the weapon-specific 7-bone control set: it is not.

## Interpretation boundary

`CONFIRMED_BINARY`: Gjallarhorn's pattern-specific 7-bone animation layer contains only the two clips above within the complete 0151 control census.

`INFERRED_STRONG`: first-person firing/recoil belongs to a different animation layer, most likely the shared Guardian/viewmodel weapon/arms graph. This is consistent with Destiny attaching the weapon to a player/viewmodel socket while pattern-specific weapon bones animate internal moving parts.

Do not label any other 0151 clip as "Gjallarhorn fire" merely from duration or motion. The next task is to trace the player/viewmodel action graph and prove the rocket-launcher firing control/clip ownership path before merging those animations into the exported GLB.

## Next target

Trace the shared first-person heavy-weapon/rocket-launcher animation path that drives:

- fire/recoil
- ready/raise/lower
- sprint/idle transitions
- ADS transitions
- equip/stow
- any player-hand portion of reload

Then merge the proven player/viewmodel socket transform with the existing Gjallarhorn internal rig rather than synthesizing recoil on the 7-bone weapon skeleton.
