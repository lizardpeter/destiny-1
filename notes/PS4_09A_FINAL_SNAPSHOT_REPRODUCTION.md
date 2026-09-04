# PS4 816CE09A final-snapshot reproduction checkpoint

Date: 2026-09-04

This checkpoint validates the generalized logical-package handling against the
main Vex target after the weapon-family sibling collision was understood.

## Production workflow result

Workflow:

- `.github/workflows/build-09a-test-glb.yml`
- run: `33903936285`
- head commit: `531db233a12e643b56d9d4be8c14939fdd1793d8`
- conclusion: success
- artifact: `816CE09A-proven-material-test-glb`
- artifact id: `9948795693`

The build now opens the highest recovered `0767` entry-table snapshot:

- `ps4_arch_vex_com01_0767_4.pkg`

while keeping `_0`, `_1`, and `_4` siblings beside it so block `patch_id`
resolution can reach physical payload owners. Physical siblings are not passed
as `--dependency-pkg` aliases.

The texture build likewise opens `ps4_globals_0156_5.pkg` and uses only
genuinely different logical package namespaces (`0157`, `0767`) as cross-
package dependencies. A workflow regression intentionally attempts
`0156_5 + --dependency-pkg 0156_4` and requires `d1_texture_export.py` to reject
that misuse.

## Independently downloaded output

The Actions artifact was downloaded after the successful run and the GLB was
validated again outside the workflow.

`816CE09A_PROVEN_MATERIAL_TEST.glb`:

- size: `7,245,808` bytes
- SHA-256: `df63fbafd77f745a056220978d6c5579bc968ba6bd141f7571e8660ccbd396d7`
- glTF version: 2
- meshes: 1
- visible primitives: 2
- nodes: 14
- skins: 1
- animations: 2 (`816CE09D`, `816CE09E`)
- materials: 2
- embedded images: 11
- textures: 4
- samplers: 2
- vertices: 4,172
- triangles: 5,336

The report also retains:

- source vertex buffers `816CE09F`, `816CE0A0`
- source index buffer `816CE0A1`
- visible triangle split 564 + 4,772
- 12-joint animation/skin fixture
- auxiliary non-visible material passes `80AAE10B` and `80AAE10C`

## Strong reproducibility result

The final-snapshot `_4` build is byte-for-byte identical to the earlier proven
`0767_0` GLB:

- earlier SHA-256: `df63fbafd77f745a056220978d6c5579bc968ba6bd141f7571e8660ccbd396d7`
- final-snapshot SHA-256: `df63fbafd77f745a056220978d6c5579bc968ba6bd141f7571e8660ccbd396d7`

This is stronger than merely matching geometry counts. It demonstrates that,
for `816CE09A`, moving to the later authoritative entry-table snapshot while
resolving payload blocks through physical siblings leaves the complete portable
artifact unchanged byte-for-byte.

The generalized sibling-namespace guard therefore fixes the cross-package
collision class without changing the already-proven Vex model result.
