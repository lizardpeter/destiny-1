//! Source-neutral scene that game importers produce for the engine's generic
//! renderer: plain meshes, instances, RGBA8 textures, PBR-style material
//! hints and baked lighting in generic forms. Everything game-specific is
//! resolved before data lands in these types; the engine never sees it.

pub mod preview;
pub mod progress;
pub mod program;
pub mod trajectory;


#[derive(Clone, Copy, Debug, Default)]
pub struct NeutralVertex {
    pub position: [f32; 3],
    pub normal: [f32; 3],
    pub tangent: [f32; 4],
    pub uv: [f32; 2],
    pub color: [f32; 4],
    /// Source-defined per-vertex values surface programs read
    /// (`program::Input::VertexData`); zero when unused.
    pub data: [f32; 4],
    /// Second UV set addressing the mesh's lightmap (0..1 over the lightmap).
    pub lightmap_uv: [f32; 2],
    /// Blend weights of the material's extra layers (see `NeutralMaterial::layers`).
    pub layer_weights: [f32; 2],
    /// UV sets of layers 1 and 2 (the primary UV when the source has none).
    pub layer_uvs: [[f32; 2]; 2],
}

/// Source-neutral solid convex collision brush in engine coordinates (Y-up,
/// metres). A point is inside exactly when dot(normal, point) <= distance for
/// every source-authored plane. Unlike a triangle soup, these halfspaces
/// preserve the volume and distinguish a solid brush from its surface.
#[derive(Clone, Debug, PartialEq)]
pub struct NeutralConvexBrush {
    /// Optional ordinal of this convex volume in the source collision store.
    /// Used only for debugging provenance; it cannot change collision.
    pub source_record: Option<u32>,
    pub planes: Vec<([f32; 3], f32)>,
    pub min: [f32; 3],
    pub max: [f32; 3],
}

/// Geometry in its own local space (world meshes use world space directly).
#[derive(Clone, Debug)]
pub struct NeutralMesh {
    pub name: String,
    pub material: usize,
    pub vertices: Vec<NeutralVertex>,
    pub indices: Vec<u32>,
    /// Baked lighting for this mesh, an index into `NeutralScene::lightmaps`.
    pub lightmap: Option<usize>,
    /// For model surfaces: index of this surface's first vertex in the
    /// model's LOD0 vertex list (per-placement vertex lighting follows it).
    pub model_vertex_base: u32,
    /// Per-vertex baked light (RGB, lightmap scale) and sun visibility (A),
    /// for meshes baked for one placement.
    pub vertex_light: Option<Vec<[f32; 4]>>,
    /// The source game's own vertices for this mesh, read by programs with a
    /// vertex stage (`program::ProgramVertexStage`). Same vertex order as
    /// `vertices`.
    pub source_vertices: Option<program::SourceVertexStream>,
}

/// Source-neutral procedural motion for a rigid scene instance.
///
/// This is intentionally expressed in canonical engine/local coordinates, not
/// in any source game's animation or map-parts vocabulary.
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum NeutralInstanceMotion {
    /// Rotate around a local-space unit axis by one fixed angular increment at
    /// a fixed source simulation rate. Sampling is stepped (not interpolated),
    /// preserving runtimes whose map-part motion advances once per game tick.
    SteppedLocalRotation {
        axis: [f32; 3],
        degrees_per_step: f32,
        steps_per_second: f32,
    },
    /// Rotate continuously around one local-space unit axis at an authored
    /// angular velocity. Unlike SteppedLocalRotation, this is sampled directly
    /// from elapsed scene time and must not be quantized to host/render ticks.
    ///
    /// Importers should use this only when their source runtime proves a
    /// constant axis/angular-velocity contract. Script lifecycle still decides
    /// whether/when the motion is active.
    ContinuousLocalRotation {
        axis: [f32; 3],
        degrees_per_second: f32,
    },
    /// Rotate around a local-space unit axis by a finite authored angle using
    /// the shared trapezoidal source-time trajectory profile. The authored
    /// instance transform is the start pose; the sampled rotation is layered
    /// onto its local geometry.
    TimedLocalRotation {
        axis: [f32; 3],
        degrees: f32,
        timing: trajectory::NeutralTrajectoryTiming,
        /// Delay from the scene/runtime epoch before trajectory time begins.
        /// Event-driven sources should normally retain their plan instead of
        /// converting an unknown event timestamp into this field.
        start_delay_millis: u32,
    },
    /// Translate by a world-space delta using the shared trapezoidal source-time
    /// trajectory profile. The authored instance transform is the start pose;
    /// this delta is layered onto its translation only.
    TimedWorldTranslation {
        delta: [f32; 3],
        timing: trajectory::NeutralTrajectoryTiming,
        /// Delay from the scene/runtime epoch before trajectory time begins.
        /// Event-driven sources should normally retain their plan instead of
        /// converting an unknown event timestamp into this field.
        start_delay_millis: u32,
    },
    /// Camera-facing local geometry. Translation and authored scale come from
    /// the instance rows; local rotation is replaced by a camera-facing basis.
    /// This covers source billboards and particle sprites without exposing
    /// source-engine draw vocabulary to the renderer.
    CameraFacingBillboard {
        /// Preserve world +Y as the billboard up axis when true.
        y_axis_only: bool,
    },
    /// Player-following regular grid displaced by two source-authored sine
    /// waves along world +Y. The renderer snaps the grid origin to the local
    /// player along the instance's local X/Z axes, preserving fixed-grid
    /// surface runtimes without exposing source-game actor/material vocabulary.
    ///
    /// wave*_vector is radians per engine metre in world X/Z. Both waves
    /// advance by the same source phase increment once per source simulation
    /// step, matching runtimes that update their phase counters in a fixed
    /// movement tick rather than continuously at render rate.
    PlayerFollowingDualSineHeightField {
        wave0_vector: [f32; 2],
        wave1_vector: [f32; 2],
        wave0_amplitude: f32,
        wave1_amplitude: f32,
        phase_per_step: f32,
        steps_per_second: f32,
        /// Grid recenter quantum in engine metres. A non-positive value
        /// disables player-follow recentering while retaining wave motion.
        recenter_step: f32,
        /// Recentered-grid texture anchoring: UV offset per metre of local
        /// grid shift. U follows local Z, V follows local X. These are
        /// authored coordinates, not an inferred renderer-wide water scale.
        recenter_uv_per_meter_zx: [f32; 2],
    },
}

/// Source-neutral target for one opaque per-instance SurfaceProgram payload.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct NeutralProgramDataTarget {
    pub data: [[f32; 4]; 8],
    pub valid_rows: u8,
    /// Number of source simulation updates used to reach this target.
    pub transition_steps: u16,
}

/// Spatial selector used by runtime per-instance program-data controllers.
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum NeutralProgramDataSpatialShape {
    OrientedBox {
        origin: [f32; 3],
        axes: [[f32; 3]; 3],
        min_local: [f32; 3],
        max_local: [f32; 3],
    },
    OrientedCylinder {
        origin: [f32; 3],
        up: [f32; 3],
        radius: f32,
        height: f32,
    },
}

/// One source-neutral spatial region. Later regions win on overlap.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct NeutralProgramDataRegion {
    pub shape: NeutralProgramDataSpatialShape,
    pub target: NeutralProgramDataTarget,
}

/// Opaque coordinate-space interpolation rule. A scalar flag below 0.5 means
/// world space and at/above 0.5 means view space.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct NeutralProgramDataPointSpaceBlend {
    pub vector_row: u8,
    pub space_flag_component: u8,
}

/// Generic runtime selector for per-instance SurfaceProgram data.
#[derive(Clone, Debug, PartialEq)]
pub struct NeutralProgramDataController {
    pub steps_per_second: f32,
    pub default_target: NeutralProgramDataTarget,
    pub regions: Vec<NeutralProgramDataRegion>,
    pub point_space_blends: Vec<NeutralProgramDataPointSpaceBlend>,
}

/// Attach one controller state to all listed NeutralScene instance indices.
/// Multiple mesh instances belonging to one source actor intentionally share a
/// single state machine and therefore switch/blend in lockstep.
#[derive(Clone, Debug, PartialEq)]
pub struct NeutralProgramDataControllerBinding {
    pub instances: Vec<usize>,
    pub controller: NeutralProgramDataController,
}

/// One placed copy of a mesh. `rows` is a 3x4 row-major affine transform in
/// engine space (Y-up meters).
#[derive(Clone, Copy, Debug)]
pub struct NeutralInstance {
    pub mesh: usize,
    pub rows: [[f32; 4]; 3],
    /// Optional source-neutral procedural transform layered on top of rows.
    pub motion: Option<NeutralInstanceMotion>,
    /// Camera-relative authored background placement; renderer adds the
    /// current camera translation while preserving authored orientation/scale.
    pub camera_relative: bool,
    /// Baked irradiance for meshes without a lightmap: 9 real spherical
    /// harmonic coefficients (RGB, linear, engine-space directions) so that
    /// irradiance(n) = sum(c[i] * Y_i(n)).
    pub irradiance_sh: Option<[[f32; 3]; 9]>,
    /// Reflection probe for generic PBR specular (index into
    /// `NeutralScene::reflection_probes`). Importers may assign an
    /// approximate nearest probe here for presentation fallback.
    pub reflection_probe: Option<usize>,
    /// Exact source-selected reflection probe for universal shader replay.
    /// Unlike `reflection_probe`, this must never be filled by a nearest-probe
    /// heuristic or other renderer-facing approximation.
    pub source_reflection_probe: Option<usize>,
    /// Baked visibility of the sun for the whole placement (static models).
    pub sun_visibility: Option<f32>,
    /// Opaque source-defined per-instance values read only by universal
    /// SurfacePrograms. The renderer assigns no meaning to these lanes.
    pub program_data: [[f32; 4]; 8],
    /// Bit i is set only when program_data row i is exact/source-closed for
    /// this placement. The bridge falls back to generic PBR for a program
    /// instance whose required rows are not valid.
    pub program_data_valid_rows: u8,
    /// Index into `NeutralScene::instance_vertex_data`: per-placement,
    /// per-vertex values that replace `program::Input::VertexData` lanes of
    /// this instance's mesh vertices (for example baked per-instance vertex
    /// ambient occlusion). None leaves the mesh's own lanes.
    pub vertex_data_override: Option<u32>,
}

/// Per-placement, per-vertex unorm8 values replacing `Input::VertexData`
/// lanes `first_lane .. first_lane + lanes` (value / 255) of one instance.
/// `values` holds `lanes` bytes per mesh vertex, in mesh vertex order.
#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct NeutralInstanceVertexData {
    pub first_lane: u8,
    pub lanes: u8,
    pub values: Vec<u8>,
}

/// Block-compressed format of an exact source-owned reflection cube.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum NeutralSourceCubeFormat {
    Bc1Unorm,
    Bc1Srgb,
    Bc2Unorm,
    Bc2Srgb,
    Bc3Unorm,
    Bc3Srgb,
}

/// Exact compressed cubemap payload retained for universal shader replay.
/// Face indices remain in source order 0..5 and every authored mip is kept
/// byte-for-byte. Generic environment lighting never interprets this payload.
#[derive(Clone, Debug)]
pub struct NeutralSourceCube {
    pub format: NeutralSourceCubeFormat,
    pub size: u32,
    /// Mip-major, then source face index 0..5. Each face contains the original
    /// BC block bytes without decode, axis conversion or RGBM conversion.
    pub mips: Vec<[Vec<u8>; 6]>,
}

/// A reflection cubemap captured in the map: faces +X, -X, +Y, -Y, +Z, -Z in
/// engine space, RGBM (see `LIGHTMAP_RGBM_RANGE`), full mip chain.
#[derive(Clone, Debug)]
pub struct NeutralReflectionProbe {
    pub origin: [f32; 3],
    pub size: u32,
    pub mips: Vec<[Vec<u8>; 6]>,
    /// Optional untouched source cube used only by universal SurfacePrograms.
    pub source_cube: Option<NeutralSourceCube>,
}

pub const IDENTITY_ROWS: [[f32; 4]; 3] = [
    [1.0, 0.0, 0.0, 0.0],
    [0.0, 1.0, 0.0, 0.0],
    [0.0, 0.0, 1.0, 0.0],
];

/// One authored lower mip level of a source-neutral RGBA8 texture.
#[derive(Clone, Debug)]
pub struct NeutralTextureMip {
    pub width: u32,
    pub height: u32,
    pub rgba: Vec<u8>,
}

#[derive(Clone, Debug)]
pub struct NeutralTexture {
    pub name: String,
    pub width: u32,
    pub height: u32,
    pub rgba: Vec<u8>,
    /// Authored lower mip levels, level 1 onward. Empty means the source did
    /// not provide a source-closed chain and the renderer may generate one.
    pub mips: Vec<NeutralTextureMip>,
    /// The source's own block-compressed encoding of exactly these texels
    /// (`rgba` and `mips` are its decode), when the source stores one. GPUs
    /// that sample the format can use it directly: same texels, a quarter to
    /// an eighth of the memory, and no decode/re-upload of RGBA.
    pub compressed: Option<NeutralCompressedTexture>,
}

/// Standard 4x4 block-compressed texel formats (BCn / DXTn).
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub enum NeutralBlockFormat {
    /// RGB + 1-bit alpha (punch-through), 8 bytes per block.
    Bc1,
    /// RGB + explicit 4-bit alpha, 16 bytes per block.
    Bc2,
    /// RGB + interpolated alpha, 16 bytes per block.
    Bc3,
    /// One unsigned channel (red), 8 bytes per block.
    Bc4,
    /// Two unsigned channels (red, green), 16 bytes per block.
    Bc5,
}

impl NeutralBlockFormat {
    pub fn block_bytes(self) -> usize {
        match self {
            Self::Bc1 | Self::Bc4 => 8,
            Self::Bc2 | Self::Bc3 | Self::Bc5 => 16,
        }
    }

    /// Exact byte size of one level.
    pub fn level_bytes(self, width: u32, height: u32) -> usize {
        width.div_ceil(4) as usize * height.div_ceil(4) as usize * self.block_bytes()
    }
}

/// One block-compressed level: blocks row-major, top-left origin.
#[derive(Clone, Debug)]
pub struct NeutralCompressedLevel {
    pub width: u32,
    pub height: u32,
    pub blocks: Vec<u8>,
}

/// Source block data for a texture: `levels[0]` is the top level, followed
/// by the same authored lower levels the RGBA form carries.
#[derive(Clone, Debug)]
pub struct NeutralCompressedTexture {
    pub format: NeutralBlockFormat,
    pub levels: Vec<NeutralCompressedLevel>,
}

/// One exact source-owned 3D RGBA8 scene texture retained for universal shader
/// replay. The shared renderer treats the payload only as a sampled UNORM
/// volume; importers own all source-specific layout and texel semantics.
#[derive(Clone, Debug)]
pub struct NeutralVolumeTexture {
    pub name: String,
    pub width: u32,
    pub height: u32,
    pub depth: u32,
    /// x changes fastest, then y, then z; four bytes per texel in logical
    /// sampled RGBA order.
    pub rgba: Vec<u8>,
}

/// Directional lightmap in a generic form: irradiance(n) =
/// ambient + directional * max(dot(n, direction), 0). Colours are linear and
/// may exceed 1, so they are stored as RGBM (rgb * a * LIGHTMAP_RGBM_RANGE);
/// `direction` holds an engine-space unit vector as rgb * 2 - 1.
#[derive(Clone, Debug)]
pub struct NeutralLightmap {
    pub width: u32,
    pub height: u32,
    pub ambient_rgbm: Vec<u8>,
    pub directional_rgbm: Vec<u8>,
    /// RGB: dominant incoming direction encoded as xyz * 0.5 + 0.5.
    /// A: baked visibility of the primary directional light (the sun).
    pub direction: Vec<u8>,
    /// Optional source-native RGBA8 baked-lighting texture retained exactly
    /// for universal shader replay. Generic environment lighting never
    /// interprets this payload; importers provide it only when source bytes and
    /// dimensions are known exactly.
    pub source_texture: Option<NeutralTexture>,
}

/// Range of the RGBM encoding used for lightmaps.
pub const LIGHTMAP_RGBM_RANGE: f32 = 8.0;

/// Encode a linear HDR colour as RGBM bytes.
pub fn encode_rgbm(rgb: [f32; 3]) -> [u8; 4] {
    let peak = rgb.iter().fold(0.0f32, |m, &v| m.max(v)).clamp(1e-6, LIGHTMAP_RGBM_RANGE);
    let m = (peak / LIGHTMAP_RGBM_RANGE * 255.0).ceil().clamp(1.0, 255.0);
    let scale = m / 255.0 * LIGHTMAP_RGBM_RANGE;
    let c = |v: f32| (v.max(0.0) / scale * 255.0).round().clamp(0.0, 255.0) as u8;
    [c(rgb[0]), c(rgb[1]), c(rgb[2]), m as u8]
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub enum NeutralAlpha {
    Opaque,
    Mask(f32),
    /// Standard or premultiplied transparency.
    Blend,
    /// Added on top of what is behind it (glows, light shafts).
    Additive,
    /// Multiplies what is behind it (grime and shadow decals).
    Multiply,
}

#[derive(Clone, Debug)]
pub struct NeutralMaterial {
    pub name: String,
    pub base_color_texture: Option<usize>,
    pub normal_texture: Option<usize>,
    /// Specular colour (RGB, sRGB) and gloss (A).
    pub specular_texture: Option<usize>,
    /// Standard glTF-channel metallic-roughness texture: G = roughness,
    /// B = metalness. Independent of the specular-glossiness source workflow.
    pub metallic_roughness_texture: Option<usize>,
    /// Standard emissive RGB texture in sRGB colour encoding.
    pub emissive_texture: Option<usize>,
    /// Source-neutral scalar PBR metalness (0..1).
    pub metallic: f32,
    /// Source-neutral linear RGB emissive radiance factor.
    pub emissive: [f32; 3],
    pub roughness: f32,
    /// Use point/nearest texel sampling for deliberately pixelated source art.
    /// This is a generic presentation property, independent of any importer.
    pub point_sampled: bool,
    /// Opaque surfaces without a specular map keep gloss in colour alpha.
    pub gloss_from_color_alpha: bool,
    pub alpha: NeutralAlpha,
    pub double_sided: bool,
    /// Cull front-facing triangles instead of back-facing ones. Ignored when
    /// double_sided is true.
    pub front_culled: bool,
    /// Shown without scene lighting (sky, emissive signs); the colour is final.
    pub unlit: bool,
    /// Radiance of an unlit surface at full-white texture (lightmap scale).
    pub emissive_scale: f32,
    /// Extra layers painted over the base (road markings, grime, damage):
    /// layer i shows where its colour alpha x the vertex's `layer_weights[i]`.
    pub layers: [NeutralLayer; 2],
    /// False for surfaces the source never draws in the colour pass
    /// (shadow-only casters, tool surfaces).
    pub visible: bool,
    /// Whether this surface should become player collision.
    pub collides: bool,
    /// Per-pixel surface program; when present it replaces the texture
    /// fields above for shading.
    pub program: Option<program::ProgramBinding>,
}

#[derive(Clone, Copy, Debug, Default)]
pub struct NeutralLayer {
    pub color_texture: Option<usize>,
    pub normal_texture: Option<usize>,
    pub mode: NeutralLayerMode,
}

/// How a detail layer combines with the surface beneath it (`w` = the
/// layer's vertex weight):
/// Blend: mix(base, layer, layer.a * w); Multiply: base * mix(1, layer, w);
/// Add: base + layer * layer.a * w.
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub enum NeutralLayerMode {
    #[default]
    Blend,
    Multiply,
    Add,
}

#[derive(Clone, Debug, Default)]
pub struct NeutralReport {
    pub lines: Vec<String>,
}

/// Sun and ambient in engine space, from the source map's lighting settings.
#[derive(Clone, Copy, Debug)]
pub struct NeutralSun {
    /// Unit vector pointing from the scene toward the sun.
    pub direction_to_light: [f32; 3],
    pub color: [f32; 3],
    pub intensity: f32,
}

/// Source-neutral local-light class consumed by the shared renderer.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum NeutralLocalLightKind {
    Point,
    Spot,
}

/// A local scene light in engine space. Importers may use these for exact
/// source semantics or an explicitly reported visual-parity lighting floor.
#[derive(Clone, Copy, Debug)]
pub struct NeutralLocalLight {
    pub kind: NeutralLocalLightKind,
    pub position: [f32; 3],
    /// Direction light travels. Ignored for point lights.
    pub direction: [f32; 3],
    pub color: [f32; 3],
    pub intensity: f32,
    pub radius: f32,
    pub inner_angle_degrees: f32,
    pub outer_angle_degrees: f32,
    pub specular_strength: f32,
}

/// Exponential height fog in engine units: transmittance over a distance d at
/// height h is exp(-density * exp(-(h - base_height) * height_falloff) * d).
#[derive(Clone, Copy, Debug)]
pub struct NeutralFog {
    /// Linear colour the fog fades to.
    pub color: [f32; 3],
    pub density: f32,
    pub base_height: f32,
    pub height_falloff: f32,
    /// Fog amount is (1 - transmittance) * max_opacity.
    pub max_opacity: f32,
    /// Toward the sun the fog shifts to another colour and opacity.
    pub sun: Option<NeutralSunFog>,
}

#[derive(Clone, Copy, Debug)]
pub struct NeutralSunFog {
    pub direction: [f32; 3],
    pub color: [f32; 3],
    pub max_opacity: f32,
    pub inner_angle: f32,
    pub outer_angle: f32,
}

/// Background sky as six cube faces (+X, -X, +Y, -Y, +Z, -Z in engine space).
#[derive(Clone, Debug)]
pub struct NeutralSky {
    /// sRGB faces holding radiance / `intensity`.
    pub faces: [NeutralTexture; 6],
    /// Radiance of a face texel at full white.
    pub intensity: f32,
}

/// How the lit scene becomes display colour. The scene radiance is scaled by
/// `exposure`, encoded with a power curve of `encode_gamma` (0.5 = square
/// root), compressed above `shoulder_knee` so the curve approaches 1 with unit
/// slope at the knee, then mapped through `lut` (32x32x32 RGBA, red fastest,
/// display-encoded output). Without a LUT the encoded value is shown directly.
#[derive(Clone, Debug)]
pub struct NeutralDisplayGrade {
    pub exposure: f32,
    pub encode_gamma: f32,
    pub shoulder_knee: f32,
    pub lut: Option<Vec<u8>>,
    /// Convex regions (inside when dot(plane.xyz, p) + plane.w <= 0 for all
    /// planes, engine space) with their own `exposure`; first match wins.
    pub exposure_volumes: Vec<(Vec<[f32; 4]>, f32)>,
}

/// CPU-readable, source-neutral voxel irradiance for camera-attached
/// geometry (hands, held items). Terrain may already bake the same irradiance
/// per vertex; this field is NOT an extra light source in the world shader.
/// Each cell is a linear, monochrome radiance sample encoded as byte * scale.
/// Bricks are 16x16x16 with x-major, z-middle, y-fastest byte order.
#[derive(Clone, Debug)]
pub struct NeutralIrradianceBrick {
    /// World-space integer cell origin; coordinates may be negative.
    pub origin: [i32; 3],
    pub values: Vec<u8>,
}

/// Optional direct-sky exposure above loaded geometry columns. Missing
/// sections below a column top are NOT assumed to receive daylight.
#[derive(Clone, Debug)]
pub struct NeutralIrradianceColumn {
    /// World-space x,z coordinate of the 16x16 column origin.
    pub origin: [i32; 2],
    pub top_opaque_y: Vec<i32>,
}

#[derive(Clone, Debug)]
pub struct NeutralIrradianceField {
    pub linear_scale: f32,
    pub bricks: Vec<NeutralIrradianceBrick>,
    pub columns: Vec<NeutralIrradianceColumn>,
    pub above_surface_level: u8,
}

#[derive(Clone, Debug)]
pub struct NeutralScene {
    /// Surface programs referenced by materials.
    pub programs: Vec<program::SurfaceProgram>,
    pub meshes: Vec<NeutralMesh>,
    pub instances: Vec<NeutralInstance>,
    /// Optional source-neutral per-instance runtime data state machines.
    pub program_data_controllers: Vec<NeutralProgramDataControllerBinding>,
    pub materials: Vec<NeutralMaterial>,
    pub textures: Vec<NeutralTexture>,
    pub lightmaps: Vec<NeutralLightmap>,
    /// Static irradiance at the camera for first-person models. No game-
    /// specific metadata is exposed beyond this source-neutral radiance.
    pub irradiance_field: Option<NeutralIrradianceField>,
    /// Optional exact source-owned 3D scene texture used only by universal
    /// SurfacePrograms. Generic PBR/environment lighting never interprets it.
    pub source_volume: Option<NeutralVolumeTexture>,
    pub local_lights: Vec<NeutralLocalLight>,
    pub sun: Option<NeutralSun>,
    pub sky: Option<NeutralSky>,
    pub fog: Option<NeutralFog>,
    pub grade: Option<NeutralDisplayGrade>,
    pub reflection_probes: Vec<NeutralReflectionProbe>,
    /// Source-exact lighting for materials that write a surface payload.
    pub lighting: Option<program::SceneLightingModel>,
    /// Per-instance vertex data streams (`NeutralInstance::vertex_data_override`).
    pub instance_vertex_data: Vec<NeutralInstanceVertexData>,
    /// Player collision triangles in engine space.
    pub collision: Vec<[[f32; 3]; 3]>,
    pub report: NeutralReport,
}

/// Rebuild a standard tangent-space RGB normal map from a two-channel
/// (X, Y) normal map; `x_channel`/`y_channel` pick the source channels.
pub fn normal_xy_to_rgb(rgba: &mut [u8], x_channel: usize, y_channel: usize) {
    for texel in rgba.chunks_exact_mut(4) {
        let (x, y) = (texel[x_channel], texel[y_channel]);
        let nx = x as f32 / 127.5 - 1.0;
        let ny = y as f32 / 127.5 - 1.0;
        let nz = (1.0 - nx * nx - ny * ny).max(0.0).sqrt();
        texel[0] = x;
        texel[1] = y;
        texel[2] = ((nz * 0.5 + 0.5) * 255.0).round() as u8;
        texel[3] = 255;
    }
}

/// Specular-glossiness packing: RGB stays the specular colour (sRGB), alpha
/// is gloss. Source maps without a gloss channel get a moderate gloss.
pub fn specular_to_specular_gloss(rgba: &mut [u8]) {
    const DEFAULT_GLOSS: u8 = 90;
    if rgba.chunks_exact(4).all(|t| t[3] == 255) {
        for texel in rgba.chunks_exact_mut(4) {
            texel[3] = DEFAULT_GLOSS;
        }
    }
}

#[derive(Clone, Copy)]
pub enum BcKind {
    Bc1,
    Bc2,
    Bc3,
    Bc5,
}

pub fn decode_bc(bytes: &[u8], width: u32, height: u32, kind: BcKind) -> Option<Vec<u8>> {
    let block_bytes = if matches!(kind, BcKind::Bc1) { 8 } else { 16 };
    let bw = width.div_ceil(4) as usize;
    let bh = height.div_ceil(4) as usize;
    if bytes.len() < bw * bh * block_bytes {
        return None;
    }
    let (w, h) = (width as usize, height as usize);
    let mut out = vec![0u8; w * h * 4];
    for by in 0..bh {
        for bx in 0..bw {
            let block = &bytes[(by * bw + bx) * block_bytes..][..block_bytes];
            let mut texels = [[0u8; 4]; 16];
            match kind {
                BcKind::Bc1 => decode_color_block(block, &mut texels, true),
                BcKind::Bc2 => {
                    decode_color_block(&block[8..], &mut texels, false);
                    for i in 0..16 {
                        let nibble = (block[i / 2] >> ((i % 2) * 4)) & 0xf;
                        texels[i][3] = nibble * 17;
                    }
                }
                BcKind::Bc3 => {
                    decode_color_block(&block[8..], &mut texels, false);
                    let mut alpha = [0u8; 16];
                    decode_alpha_block(&block[..8], &mut alpha);
                    for i in 0..16 {
                        texels[i][3] = alpha[i];
                    }
                }
                BcKind::Bc5 => {
                    let mut red = [0u8; 16];
                    let mut green = [0u8; 16];
                    decode_alpha_block(&block[..8], &mut red);
                    decode_alpha_block(&block[8..], &mut green);
                    for i in 0..16 {
                        texels[i] = [red[i], green[i], 0, 255];
                    }
                }
            }
            for ty in 0..4 {
                for tx in 0..4 {
                    let (x, y) = (bx * 4 + tx, by * 4 + ty);
                    if x < w && y < h {
                        out[(y * w + x) * 4..][..4].copy_from_slice(&texels[ty * 4 + tx]);
                    }
                }
            }
        }
    }
    Some(out)
}

fn rgb565(value: u16) -> [u8; 3] {
    let r = ((value >> 11) & 0x1f) as u32;
    let g = ((value >> 5) & 0x3f) as u32;
    let b = (value & 0x1f) as u32;
    [((r * 527 + 23) >> 6) as u8, ((g * 259 + 33) >> 6) as u8, ((b * 527 + 23) >> 6) as u8]
}

fn decode_color_block(block: &[u8], texels: &mut [[u8; 4]; 16], bc1_alpha: bool) {
    let c0 = u16::from_le_bytes([block[0], block[1]]);
    let c1 = u16::from_le_bytes([block[2], block[3]]);
    let (a, b) = (rgb565(c0), rgb565(c1));
    let mut palette = [[a[0], a[1], a[2], 255], [b[0], b[1], b[2], 255], [0; 4], [0; 4]];
    let mix = |wa: u32, wb: u32, d: u32| -> [u8; 4] {
        let mut c = [0u8; 4];
        for i in 0..3 {
            c[i] = ((a[i] as u32 * wa + b[i] as u32 * wb) / d) as u8;
        }
        c[3] = 255;
        c
    };
    if c0 > c1 || !bc1_alpha {
        palette[2] = mix(2, 1, 3);
        palette[3] = mix(1, 2, 3);
    } else {
        palette[2] = mix(1, 1, 2);
        palette[3] = [0, 0, 0, 0];
    }
    let lookup = u32::from_le_bytes([block[4], block[5], block[6], block[7]]);
    for (i, texel) in texels.iter_mut().enumerate() {
        *texel = palette[((lookup >> (i * 2)) & 3) as usize];
    }
}

fn decode_alpha_block(block: &[u8], out: &mut [u8; 16]) {
    let (a0, a1) = (block[0] as u32, block[1] as u32);
    let mut palette = [0u32; 8];
    palette[0] = a0;
    palette[1] = a1;
    if a0 > a1 {
        for i in 1..7 {
            palette[i + 1] = ((7 - i as u32) * a0 + i as u32 * a1) / 7;
        }
    } else {
        for i in 1..5 {
            palette[i + 1] = ((5 - i as u32) * a0 + i as u32 * a1) / 5;
        }
        palette[6] = 0;
        palette[7] = 255;
    }
    let mut lookup = 0u64;
    for i in 0..6 {
        lookup |= (block[2 + i] as u64) << (8 * i);
    }
    for (i, value) in out.iter_mut().enumerate() {
        *value = palette[((lookup >> (3 * i)) & 7) as usize] as u8;
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn bc1_solid_block_decodes() {
        // c0 = pure red (0xF800), c1 = black, all indices 0.
        let block = [0x00, 0xF8, 0x00, 0x00, 0, 0, 0, 0];
        let rgba = decode_bc(&block, 4, 4, BcKind::Bc1).unwrap();
        assert_eq!(&rgba[..4], &[255, 0, 0, 255]);
    }

    #[test]
    fn bc5_reconstructs_flat_normal() {
        let mut block = [0u8; 16];
        block[0] = 128;
        block[1] = 128;
        block[8] = 128;
        block[9] = 128;
        let mut rgba = decode_bc(&block, 4, 4, BcKind::Bc5).unwrap();
        normal_xy_to_rgb(&mut rgba, 0, 1);
        assert!(rgba[2] > 250);
    }
}
