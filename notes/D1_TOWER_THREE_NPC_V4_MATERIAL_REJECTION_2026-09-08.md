# D1 Tower three-NPC V4 material-correctness rejection

Date: 2026-09-08

Status: **V4 REJECTED AS A VISUAL-CORRECTNESS EXPORT**

The V4 animation/geometry handoff is not being promoted to a correct Destiny 1 character render. Its target-native action append and evaluated-mesh deformation gates remain useful evidence, but its material presentation is invalid.

## User-visible failure

Both the CI canary and Blender inspection show saturated neon green/red/blue regions on the selected Tower actors. This is not a Blender viewport-mode issue and is not caused by the V4 target-native animation append.

## Exact pipeline defect

The pinned production textured-variant job (`34172347436`, artifact `10036629355`) generated an evidence-scoped texture-role inventory over 320 active materials with this portable base-role coverage:

- `PROVEN`: 15
- `STRONG_FORMAT_CANDIDATE`: 252
- `MEDIUM_PREVIEW_CANDIDATE`: 46
- `NONE`: 7

The production binder was invoked with `--include-medium-base --bind-normal-candidates`. Consequently, `STRONG_FORMAT_CANDIDATE` and `MEDIUM_PREVIEW_CANDIDATE` textures were written into standard glTF `baseColorTexture` slots even though those labels explicitly represent preview heuristics rather than native shader color-dataflow proof.

V4 then preserved those existing portable preview bindings. Its `COLOR_0` demotion fixed one independent portability bug, but did not make the pre-existing heuristic `baseColorTexture` choices correct.

## Xur psychedelic material family was already source-closed

The Xur Wave 5 proof had already identified the exact failure mode for PS `80876579` / bounded GCN SHA-256 `f60720572d9bd42f06c3fffc3ef5e178f8a9d7917fa8c83d96511830e45b0c00`.

For materials `808761EC`, `80876227`, `8087623F`, and `80876411`, native GCN proves:

- t0 `80876551` is RGB palette/control data, **not visible base color**;
- t1 `80876552` supplies the visible surface RGB;
- t0 selects/reconstructs a palette using t2/t3/t4;
- visible surface RGB begins as `t1.rgb * palette` before the native reflection path.

Putting t0 directly in glTF `baseColorTexture` therefore exposes the saturated control mask and produces the exact psychedelic appearance seen in Blender.

The actor export pipeline failed to consume this already-closed shader-semantic evidence.

## Independent Xur material-selection gate

The shared-human Xur model `80C88CEF` also has an independent external-material permutation gate. The static D1 permutation graph is exact, but live Xur selector/configuration evaluation is not yet source-closed. In particular the E6/E7/E8 material-selection gates remain false.

Therefore a correctness export must not claim that a convenience/default/signature material member is the retail-selected Xur material unless the live selector state is proven.

## New mandatory correctness policy

From this checkpoint forward:

1. `STRONG_FORMAT_CANDIDATE` and `MEDIUM_PREVIEW_CANDIDATE` are forbidden from standard glTF `baseColorTexture` in any export labeled correct/final/retail-equivalent.
2. Exact native texture bindings may remain embedded as evidence even when their high-level role is unresolved.
3. A visible material may be presented as retail-correct only when its color path is backed by an instruction/source-closed shader semantic handler using that asset's exact textures/constants/samplers/required runtime inputs.
4. Exact bounded native GCN SHA-256, not serialized shader TagHash or appearance, is the reusable shader-semantic identity.
5. Material permutation selection remains an independent required gate for shared models such as Xur.
6. CI image generation is necessary but not sufficient. A green render must be preceded by a material-semantic proof gate; merely producing PNG pixels is not visual correctness.

The next generated Blender handoff must fail closed rather than replace unresolved material semantics with gray placeholders or heuristic color guesses.
