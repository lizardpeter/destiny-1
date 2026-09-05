# PS4 Gjallarhorn native fire recoil attachment correction

## Status

Closed on 2026-09-05 by workflow run `33938311919` at commit `92742a7401d257109638d2decaeef210b823397c`.

The prior standalone fire export was structurally valid but visually incomplete. It selected the correct native state and clip (`fire` -> `80AA3D42`, 19 frames / 0.6 s) and exported a third glTF animation, but it baked motion from `C410084A`. That node is not where the visible native recoil impulse lives.

## Exact hierarchy and measured motion

On the proven 75-node / 73-control rocket-launcher viewmodel family (`80AA3CBF` skeleton, `80AA3CBE` runtime rig), the relevant chain is:

```text
EF4BAB19  (known public dictionary identity: right grip)
  -> C410084A
      -> E6477C3B
```

`C410084A` is effectively static in local space during the fire clip. Baking only its evaluated world motion therefore captured mostly the small inherited hand/viewmodel motion and produced only about 8 mm of translation, which can appear to be no firing animation at all.

`E6477C3B`, a direct child of `C410084A`, contains the native fire impulse. Its local translation is static except for the second sample:

```text
frame 0 / 0.0000 s : [ 0.017505, 0.104200, -0.004286 ]
frame 1 / 0.0333 s : [ 0.017505, 0.104997, -0.044856 ]
frame 2 / 0.0667 s : [ 0.017505, 0.104200, -0.004286 ]
```

The local Z excursion is therefore about `-0.04057 m` for one native sample. When the complete animated ancestor chain is evaluated and the resulting `E6477C3B` world transform is rebased to frame 0, the standalone weapon receives:

- 19 samples
- 0.600000 s duration
- maximum translation delta: `0.0333957002 m`
- maximum rotation delta: `0.469804883 deg`
- maximum scale delta: `7.42e-7`

No recoil curve is synthesized. The standalone root animation is still exactly:

```text
source_world(t) * inverse(source_world(t0))
```

but the source node is now the native child that actually carries the recoil impulse.

## Export regression

`.github/workflows/build-gjallarhorn-rocket-launcher-fire.yml` now:

1. proves `E6477C3B` exists exactly once,
2. proves it is a direct child of `C410084A`,
3. exports the exact `80AA3D42` viewmodel proof GLB,
4. bakes `E6477C3B` world motion instead of `C410084A`, and
5. rejects the final output unless maximum translation is between 3 cm and 5 cm.

That last assertion prevents the original near-static-parent mistake from silently returning.

## Corrected artifact

Successful workflow run: `33938311919`

Artifact: `9960920492`, `D1-Gjallarhorn-Year3-TEXTURED-ANIMATED-WITH-FIRE`

Final GLB SHA-256:

```text
9db62a85e01276f7eaf6ea1a2bb5c9248b23168eb2e28912237ff3dc14c9b459
```

Final animation list remains:

```text
80AA2E4A
80AA2E4B
rocket_launcher_fire_STATE_9FAC79C9_80AA3D42_VIEWMODEL_MOTION
```

## Semantic caution

The public hash dictionary does not currently provide a trusted semantic name for `E6477C3B`. It is therefore documented as the native weapon-motion/recoil child by measured behavior and exact hierarchy, not assigned a guessed bone name.
