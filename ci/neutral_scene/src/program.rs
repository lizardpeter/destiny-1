//! Surface programs: the engine's own per-pixel material format.
//!
//! An importer translates a game's material shader into a `SurfaceProgram`:
//! a straight-line SSA list of scalar operations over textures, material
//! constants and standard interpolated inputs, ending in the surface values
//! the generic lighting consumes. The engine compiles programs to its own
//! shading language; it never sees the source game's shaders.
//!
//! Every value is a 32-bit word. Float operations read and write the word as
//! an IEEE f32; integer and bit operations treat it as u32 / i32. Booleans
//! are 0 or 1.

/// Index of an earlier op's result.
pub type Value = u32;

use std::collections::HashMap;

/// Source-neutral SSA builder shared by every game importer.
///
/// This is deliberately part of the universal material IR rather than any
/// source-game decoder. Importers lower their native shader representation
/// into `Op` values through this builder, gaining identical constant folding
/// and common-subexpression reuse regardless of whether the source was GCN,
/// DXBC, a symbolic DAG, or a future importer.
#[derive(Default)]
pub struct ProgramBuilder {
    pub ops: Vec<Op>,
    memo: HashMap<Op, Value>,
}

impl ProgramBuilder {
    /// The literal word of `v`, when it is a constant.
    pub fn constant_of(&self, v: Value) -> Option<u32> {
        match self.ops[v as usize] {
            Op::Const(c) => Some(c),
            _ => None,
        }
    }

    pub fn push(&mut self, op: Op) -> Value {
        let folded = match op {
            Op::Unary(o, a) => self.constant_of(a).map(|a| eval_unary(o, a)),
            Op::Binary(o, a, b) => match (self.constant_of(a), self.constant_of(b)) {
                (Some(a), Some(b)) => Some(eval_binary(o, a, b)),
                _ => None,
            },
            Op::Ternary(o, a, b, c) => match (
                self.constant_of(a),
                self.constant_of(b),
                self.constant_of(c),
            ) {
                (Some(a), Some(b), Some(c)) => Some(eval_ternary(o, a, b, c)),
                _ => None,
            },
            Op::Select(c, a, b) => {
                if a == b {
                    return a;
                }
                match self.constant_of(c) {
                    Some(0) => return b,
                    Some(_) => return a,
                    None => None,
                }
            }
            _ => None,
        };
        let op = folded.map_or(op, Op::Const);
        if let Some(&v) = self.memo.get(&op) {
            return v;
        }
        let v = self.ops.len() as Value;
        self.ops.push(op);
        self.memo.insert(op, v);
        v
    }

    pub fn c(&mut self, bits: u32) -> Value {
        self.push(Op::Const(bits))
    }

    pub fn f(&mut self, value: f32) -> Value {
        self.c(value.to_bits())
    }

    pub fn un(&mut self, op: Unary, a: Value) -> Value {
        self.push(Op::Unary(op, a))
    }

    pub fn bin(&mut self, op: Binary, a: Value, b: Value) -> Value {
        self.push(Op::Binary(op, a, b))
    }

    pub fn tri(&mut self, op: Ternary, a: Value, b: Value, c: Value) -> Value {
        self.push(Op::Ternary(op, a, b, c))
    }

    pub fn select(&mut self, cond: Value, a: Value, b: Value) -> Value {
        self.push(Op::Select(cond, a, b))
    }

    /// Boolean and of values already normalized to 0/1.
    pub fn and(&mut self, a: Value, b: Value) -> Value {
        match (self.constant_of(a), self.constant_of(b)) {
            (Some(0), _) | (_, Some(0)) => self.c(0),
            (Some(_), _) => b,
            (_, Some(_)) => a,
            _ if a == b => a,
            _ => self.bin(Binary::And, a, b),
        }
    }

    /// Boolean or of values already normalized to 0/1.
    pub fn or(&mut self, a: Value, b: Value) -> Value {
        match (self.constant_of(a), self.constant_of(b)) {
            (Some(x), _) if x != 0 => self.c(1),
            (_, Some(x)) if x != 0 => self.c(1),
            (Some(_), _) => b,
            (_, Some(_)) => a,
            _ if a == b => a,
            _ => self.bin(Binary::Or, a, b),
        }
    }

    pub fn not(&mut self, value: Value) -> Value {
        self.un(Unary::LogicalNot, value)
    }

    pub fn is_true(&self, value: Value) -> bool {
        self.constant_of(value).is_some_and(|word| word != 0)
    }

    pub fn is_zero_word(&self, value: Value) -> bool {
        matches!(self.ops[value as usize], Op::Const(0))
    }

    pub fn is_zero_f(&self, value: Value) -> bool {
        self.constant_of(value)
            .is_some_and(|word| f32::from_bits(word) == 0.0)
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub enum ProgramTextureKind {
    D2,
    Cube,
    /// 3D texture sampled at (s, t, r). Used by scene-lighting programs, whose
    /// textures come from `SceneLightingModel::textures`.
    D3,
}

/// A texture slot a program samples. The material supplies which texture
/// fills each slot.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub struct ProgramTextureSlot {
    pub kind: ProgramTextureKind,
    /// Stored sRGB: sampling returns linear values.
    pub srgb: bool,
}


#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub enum ProgramFilter {
    Nearest,
    Linear,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub enum ProgramMipmapMode {
    Nearest,
    Linear,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub enum ProgramAddressMode {
    Repeat,
    MirroredRepeat,
    ClampToEdge,
    ClampToBorder,
    MirrorClampToEdge,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash, PartialOrd, Ord)]
pub enum ProgramCompareOp {
    Never,
    Less,
    Equal,
    LessOrEqual,
    Greater,
    NotEqual,
    GreaterOrEqual,
    Always,
}

/// Source-neutral fixed-function depth state for a surface-program binding.
///
/// A missing ProgramBinding depth preserves the renderer's legacy/default
/// policy. Importers should set this only when the source depth contract is
/// known exactly.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash, PartialOrd, Ord)]
pub struct ProgramDepthState {
    pub test_enable: bool,
    pub write_enable: bool,
    pub compare: ProgramCompareOp,
}

/// Source-neutral sampler state supplied by a material binding.
///
/// Float fields are stored as exact IEEE words so this contract remains
/// Eq/Hash and can preserve source state byte-for-byte through import/dedup.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub struct ProgramSamplerState {
    pub mag_filter: ProgramFilter,
    pub min_filter: ProgramFilter,
    pub mipmap_mode: ProgramMipmapMode,
    pub address_u: ProgramAddressMode,
    pub address_v: ProgramAddressMode,
    pub address_w: ProgramAddressMode,
    pub mip_lod_bias_bits: u32,
    /// 0 = renderer-adaptive legacy/default policy, 1 = disabled,
    /// values >1 request that exact maximum level.
    pub max_anisotropy: u8,
    pub compare: Option<ProgramCompareOp>,
    pub min_lod_bits: u32,
    /// +infinity means no source-side maximum LOD clamp.
    pub max_lod_bits: u32,
    /// Colour read outside the texture by clamp-to-border addressing.
    pub border: ProgramBorderColor,
}

#[derive(Clone, Copy, Debug, Default, PartialEq, Eq, Hash)]
pub enum ProgramBorderColor {
    #[default]
    TransparentBlack,
    OpaqueBlack,
    OpaqueWhite,
}

impl Default for ProgramSamplerState {
    fn default() -> Self {
        Self {
            mag_filter: ProgramFilter::Linear,
            min_filter: ProgramFilter::Linear,
            mipmap_mode: ProgramMipmapMode::Linear,
            address_u: ProgramAddressMode::Repeat,
            address_v: ProgramAddressMode::Repeat,
            address_w: ProgramAddressMode::Repeat,
            mip_lod_bias_bits: 0.0f32.to_bits(),
            max_anisotropy: 0,
            compare: None,
            min_lod_bits: 0.0f32.to_bits(),
            max_lod_bits: f32::INFINITY.to_bits(),
            border: ProgramBorderColor::TransparentBlack,
        }
    }
}

/// Standard interpolated inputs, all in engine space (Y-up metres).
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub enum Input {
    /// xyz.
    WorldPosition,
    /// xyz, unit length.
    WorldNormal,
    /// xyz unit tangent, w = bitangent sign.
    WorldTangent,
    /// xy.
    Uv,
    /// rgba.
    VertexColor,
    /// Source-defined per-vertex values (`NeutralVertex::data`).
    VertexData,
    /// xyz.
    CameraPosition,
    /// x = seconds since the map started.
    Time,
    /// x = the renderer's late-latched linear scene exposure multiplier for
    /// the active camera/view. Importers may derive source-engine exposure
    /// constants from this without baking a camera-dependent value at load time.
    ExposureMultiplier,
    /// Strongest authored directional light selected by the source-neutral
    /// runtime. xyz = unit direction from the shaded scene toward the light;
    /// w = 1 when such a light exists, otherwise 0.
    PrimaryDirectionalLightDirectionToLight,
    /// Same selected directional light. rgb = linear light colour, w = scalar
    /// intensity. This is raw authored scene-light state, not attenuated PBR
    /// output, so importers may use it only for proven source-engine semantics.
    PrimaryDirectionalLightColorIntensity,
    /// Visibility in [0, 1] of the same selected directional light at the
    /// shaded pixel, from the renderer's own shadowing of that light
    /// (1 = unshadowed). Pixel stage only, component 0. This is the
    /// source-neutral stand-in for an engine's screen-space sun shadow mask.
    PrimaryDirectionalShadow,
    /// Current render-target extent. x/y = width/height in pixels,
    /// z/w = reciprocal width/height. This is renderer-owned neutral state;
    /// source importers may bind it only when their source semantic is proven.
    ViewportSize,
    /// xy = pixel position in the render target, zw = unused.
    FragCoord,
    /// x = 1 for the front face, 0 for the back face.
    FrontFacing,
    /// Vertex stage only: raw source vertex attribute. Component
    /// `attribute * 4 + lane` reads lane 0-3 of `ProgramVertexStage::attributes[attribute]`,
    /// converted exactly as the GPU input assembler converts its format.
    SourceAttribute,
    /// Skinned-vertex-stage only: bind-relative skeletal deformation result
    /// before the instance/object transform is applied. xyz are in the generic
    /// asset's local engine-space coordinate system (Y-up metres); w is 1.
    ///
    /// Importers derive source-engine post-skin domains from this neutral value;
    /// source-specific packed vertex formats never enter the renderer contract.
    SkinnedLocalPosition,
    /// Skinned-vertex-stage only: post-skin local normal before any generic
    /// normalization or instance transform. xyz; w = 0.
    SkinnedLocalNormal,
    /// Skinned-vertex-stage only: post-skin local tangent before any generic
    /// normalization or instance transform. xyz; w carries
    /// the generic tangent handedness/sign from the source asset.
    SkinnedLocalTangent,
    /// Vertex-stage only: current skin matrix of the program-selected
    /// skeleton joint. The selected joint is `ProgramVertexStage::skinned_joint`.
    /// Component `row * 4 + column`, rows 0-2 of the 3x4 affine matrix.
    /// This is the bind-relative skin matrix (animated_world * inverse_bind),
    /// not a source-engine joint representation.
    SelectedJointSkinMatrix,
    /// The instance's object-to-world transform (engine space). Component
    /// `row * 4 + column`, rows 0-2 of the 3x4 affine matrix.
    ObjectToWorld,
    /// Camera-relative view-projection in the renderer's engine coordinate
    /// domain: `VP_abs * Translation(camera_position)`. Component
    /// `column * 4 + row` addresses the 4x4 column-major matrix.
    CameraRelativeViewProjection,
    /// Rotation-only world-to-view transform in engine coordinates.
    /// Component `row * 4 + column`, rows 0-2, columns 0-2. The fourth
    /// component of each row is zero. This deliberately excludes camera
    /// translation so importers can reproduce source environment/reflection
    /// coordinate generation without depending on renderer camera internals.
    WorldToViewRotation,
    /// Opaque source-defined per-instance scalar payload. Component
    /// `row * 4 + lane` addresses `NeutralInstance::program_data[row][lane]`.
    /// It is available to both program stages and has no renderer-defined meaning.
    InstanceData,
    /// Pixel stage only: interpolated vertex-stage result. Component `i` is
    /// `ProgramVertexStage::varyings[i]`, interpolated as an f32.
    Varying,
    /// Scene-lighting programs only (light and composition programs of a
    /// `SceneLightingModel`): word `component` of the exact source surface
    /// payload the shaded pixel's material wrote (`SurfaceOutputs::payload`).
    /// A deferred renderer reads it back from its payload targets; a forward
    /// renderer passes the material's values directly. Either way the light
    /// program sees the same words.
    SurfacePayload,
    /// Composition program only: light accumulated over every light program
    /// that reached this pixel. Components 0-2 = summed `light_diffuse`,
    /// 3-5 = summed `light_specular`.
    LightAccumulation,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub enum Unary {
    // f32
    Neg,
    Abs,
    Floor,
    Ceil,
    Trunc,
    RoundEven,
    Fract,
    Sqrt,
    InverseSqrt,
    Reciprocal,
    Exp2,
    Log2,
    /// sin(x * 2pi) (argument in turns).
    SinTurns,
    /// cos(x * 2pi).
    CosTurns,
    Saturate,
    /// f32 -> i32 (truncating, saturating).
    FloatToInt,
    FloatToUint,
    IntToFloat,
    UintToFloat,
    /// f32 -> f16 bits in the low half (round toward zero).
    FloatToHalf,
    /// f16 bits (low half) -> f32.
    HalfToFloat,
    // u32
    Not,
    /// Boolean negation of a 0/1 value.
    LogicalNot,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub enum Binary {
    // f32
    Add,
    Sub,
    Mul,
    /// Multiply where 0 * anything = 0 (legacy DX9 rule).
    MulLegacy,
    Div,
    Min,
    Max,
    /// x * 2^n (n as i32).
    Ldexp,
    // f32 comparisons -> 0/1 (ordered unless noted)
    Lt,
    Le,
    Gt,
    Ge,
    Eq,
    /// Unordered not-equal.
    Ne,
    // i32 / u32
    IAdd,
    ISub,
    IMul,
    IMin,
    IMax,
    UMin,
    UMax,
    And,
    Or,
    Xor,
    Shl,
    ShrU,
    ShrI,
    ILt,
    ILe,
    IGt,
    IGe,
    IEq,
    INe,
    ULt,
    ULe,
    UGt,
    UGe,
    /// Pack two f32 as f16 (a low, b high), round toward zero.
    PackHalf2,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub enum Ternary {
    /// a * b + c (fused).
    Fma,
    /// a * b + c with the legacy zero rule for the product.
    MadLegacy,
    Min3,
    Max3,
    Med3,
    /// (a >> b) & ((1 << c) - 1), unsigned.
    BitExtractU,
    /// (a & b) | (!a & c).
    BitSelect,
    /// Cube-map helpers of direction (a, b, c): face id, s, t, 2 * major axis.
    CubeId,
    CubeS,
    CubeT,
    CubeMajor2,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub enum Lod {
    /// Hardware derivatives.
    Implicit,
    Level(Value),
    Bias(Value),
    /// d(s,t)/dx then d(s,t)/dy.
    Grad([Value; 4]),
}

/// Source-neutral per-instance scene textures owned by the renderer rather
/// than by a material. Importers may use these only when the source resource
/// identity is proven and the corresponding scene payload is retained.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub enum ProgramSceneTexture {
    /// Exact source-native RGBA baked-lighting texture associated with the
    /// instance's lightmap. The renderer supplies one array layer per
    /// lightmap; coordinates remain in the source texture's normalized space.
    SourceBakedLightmap,
    /// Exact source-owned 3D scene texture. Coordinates are normalized source
    /// texture coordinates. The renderer assigns no semantic meaning to the
    /// payload beyond ordinary sampled UNORM RGBA.
    SourceVolume,
    /// Exact source-owned reflection cubemap selected by the instance.
    /// Direction coordinates remain in source cube space and authored
    /// compressed mips/sRGB interpretation are preserved by the renderer.
    SourceReflectionCube,
    /// Snapshot of the scene colour taken after ordinary/source-opaque world
    /// rendering and before late refractive/composite surfaces. Coordinates
    /// are normalized screen UV. For SourceFramebuffer programs the snapshot
    /// preserves framebuffer/code values rather than reinterpreting them as
    /// linear radiance.
    SceneColorSnapshot,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub enum Op {
    /// A literal 32-bit word.
    Const(u32),
    Input(Input, u8),
    /// Material constant vec4 `index`, component `component`.
    Constant(u16, u8),
    /// Frame constant vec4 `index`, component `component`: the outputs of the
    /// scene's `FrameProgram`, evaluated once per frame/view by the renderer.
    FrameConstant(u16, u8),
    Unary(Unary, Value),
    Binary(Binary, Value, Value),
    Ternary(Ternary, Value, Value, Value),
    /// cond != 0 ? a : b.
    Select(Value, Value, Value),
    /// Sample slot `texture` at (s, t) for 2D or direction (s, t, r) for
    /// cubes. The result is a vec4 addressed with `Component`.
    Sample { texture: u8, sampler: u8, coords: [Value; 3], lod: Lod },
    /// Sample a renderer-owned per-instance scene texture. Unlike `Sample`,
    /// this does not consume a material texture or sampler slot.
    SceneSample { texture: ProgramSceneTexture, coords: [Value; 3], lod: Lod },
    /// Texel fetch (integer coordinates, mip level).
    Load { texture: u8, coords: [Value; 2], level: Value },
    /// Level of detail the hardware would pick: component 0 clamped, 1 raw.
    QueryLod { texture: u8, sampler: u8, coords: [Value; 3] },
    /// Channel of a `Sample`/`Load`/`QueryLod` result.
    Component(Value, u8),
    /// Read `value` from another pixel of the 2x2 quad: `lanes[i]` is the
    /// lane (0 = top-left, 1 = top-right, 2 = bottom-left, 3 = bottom-right)
    /// pixel i reads.
    QuadRead(Value, [u8; 4]),
}

/// How the program's result combines with the frame.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub enum ProgramBlend {
    /// A lit opaque (or alpha-tested) surface.
    Surface,
    /// Radiance added to what is behind (glows, sky layers).
    Additive,
    /// Premultiplied radiance over what is behind, weighted by alpha.
    PremultipliedAlpha,
}

/// Numeric domain in which a source fixed-function blend is defined.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash, PartialOrd, Ord)]
pub enum ProgramBlendDomain {
    /// Blend factors operate on linear scene/attachment values.
    Linear,
    /// Blend factors operate on source framebuffer/code values before the
    /// engine crosses into its linear presentation space.
    SourceFramebuffer,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash, PartialOrd, Ord)]
pub enum ProgramBlendFactor {
    Zero,
    One,
    SrcColor,
    OneMinusSrcColor,
    DstColor,
    OneMinusDstColor,
    SrcAlpha,
    OneMinusSrcAlpha,
    DstAlpha,
    OneMinusDstAlpha,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash, PartialOrd, Ord)]
pub enum ProgramFixedBlendMode {
    Blend,
    Subtract,
    Logic,
}

/// Numeric precision/rounding contract of a fixed-function blender.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash, PartialOrd, Ord)]
pub enum ProgramBlendMath {
    /// Conventional normalized fixed-function blend math.
    Normalized,
    /// GameCube/Wii GX EFB integer blend: 8-bit factors are promoted with
    /// f += f >> 7 (0..256), channels combine in integer arithmetic, then
    /// shift right by eight and saturate.
    GxU8Factor256,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash, PartialOrd, Ord)]
pub enum ProgramLogicOp {
    Clear,
    And,
    ReverseAnd,
    Copy,
    InvertedAnd,
    NoOp,
    Xor,
    Or,
    Nor,
    Equivalent,
    Invert,
    ReverseOr,
    InvertedCopy,
    InvertedOr,
    Nand,
    Set,
}

/// Exact source fixed-function composition state retained alongside the
/// universal shader. The coarse ProgramBlend remains the currently available
/// renderer path; this contract prevents source factors/domain from being lost
/// while exact source-domain compositing is brought online.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash, PartialOrd, Ord)]
pub struct ProgramFixedBlendState {
    pub domain: ProgramBlendDomain,
    pub mode: ProgramFixedBlendMode,
    pub math: ProgramBlendMath,
    pub src_factor: ProgramBlendFactor,
    pub dst_factor: ProgramBlendFactor,
    pub logic_op: ProgramLogicOp,
}

/// Semantic domain of a SurfaceProgram's RGB result.
///
/// This is deliberately independent of storage format. A source-framebuffer
/// code value may later be converted into a linear representation for a modern
/// attachment, but that conversion must not retroactively reinterpret the
/// source arithmetic as linear-light shading.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub enum ProgramOutputDomain {
    /// Generic material inputs that still require engine lighting/fog.
    LitSurface,
    /// Source shader has produced linear scene radiance; engine presentation
    /// (exposure/display transform) still follows.
    LinearScene,
    /// Source pipeline has produced framebuffer/code values after its own
    /// fixed-function material math. These values bypass engine lighting,
    /// exposure, tonemapping and grading. Their numeric blend domain remains a
    /// source-pipeline concern, not a linear-radiance one.
    SourceFramebuffer,
}

/// Where the lit surface values come from. `None` fields use defaults.
#[derive(Clone, Debug, Default, PartialEq, Eq, Hash)]
pub struct SurfaceOutputs {
    /// Linear albedo.
    pub base_color: Option<[Value; 3]>,
    /// Coverage / opacity.
    pub alpha: Option<Value>,
    /// Engine-space world normal (not necessarily unit length).
    pub world_normal: Option<[Value; 3]>,
    /// 0 = rough, 1 = smooth.
    pub gloss: Option<Value>,
    pub metallic: Option<Value>,
    /// Ambient occlusion.
    pub occlusion: Option<Value>,
    /// Linear radiance (for `Surface`, added to the lit result).
    pub emissive: Option<[Value; 3]>,
    /// Discard the pixel when this is non-zero.
    pub discard: Option<Value>,
    /// Fully shaded scene radiance (already lit and fogged by the source
    /// shader), in engine radiance units before exposure. When present the
    /// engine applies only exposure and the display transform: none of the
    /// lit-surface fields above are used and no engine lighting or fog is
    /// added.
    pub final_color: Option<[Value; 3]>,
    /// Source-authored framebuffer/code-value colour. Fixed-function pipelines
    /// such as GX TEV operate on these numeric colour codes directly; they are
    /// not automatically linear-light radiance. The renderer bypasses engine
    /// lighting, exposure, tonemapping, grading and generic fog. A later target
    /// conversion may place the same source code value into a modern linear
    /// attachment, but it must preserve the source pipeline's numeric meaning.
    pub source_framebuffer_color: Option<[Value; 3]>,
    /// Exact source surface payload words (for example the source game's
    /// G-buffer render-target values) consumed by the scene lighting model.
    /// A material writing a payload is shaded only by the scene's
    /// `SceneLightingModel`: none of the generic lit-surface fields are used.
    pub payload: Option<Vec<Value>>,
    /// Light program result added into the diffuse accumulation.
    pub light_diffuse: Option<[Value; 3]>,
    /// Light program result added into the specular accumulation.
    pub light_specular: Option<[Value; 3]>,
}

/// How the input assembler converts one source vertex attribute into the
/// four lanes a vertex program reads (missing lanes read as 0, 0, 0, 1).
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub enum SourceFormat {
    F32,
    F32x2,
    F32x3,
    F32x4,
    F16x2,
    F16x4,
    Unorm8x4,
    Snorm8x4,
    Uint8x4,
    Unorm16x2,
    Snorm16x2,
    Unorm16x4,
    Snorm16x4,
    Uint32,
    Unorm10_10_10_2,
}

impl SourceFormat {
    /// Size in bytes.
    pub fn size(self) -> u32 {
        match self {
            Self::F32 | Self::F16x2 | Self::Unorm8x4 | Self::Snorm8x4 | Self::Uint8x4 | Self::Unorm16x2
            | Self::Snorm16x2 | Self::Uint32 | Self::Unorm10_10_10_2 => 4,
            Self::F32x2 | Self::F16x4 | Self::Unorm16x4 | Self::Snorm16x4 => 8,
            Self::F32x3 => 12,
            Self::F32x4 => 16,
        }
    }

    /// Integer formats deliver raw integers; the rest deliver f32 lanes.
    pub fn is_integer(self) -> bool {
        matches!(self, Self::Uint8x4 | Self::Uint32)
    }
}

/// One raw attribute of a mesh's source vertex stream.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub struct SourceAttribute {
    /// Byte offset inside each vertex.
    pub offset: u32,
    pub format: SourceFormat,
}

/// A mesh's vertices in the source game's own layout, `stride` bytes each,
/// read by programs with a vertex stage.
#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct SourceVertexStream {
    pub stride: u32,
    pub bytes: Vec<u8>,
    /// Attributes whose source values are exact for this mesh. Canonical
    /// streams may reserve/fill other offsets, but those filler lanes must not
    /// qualify a program that requires the corresponding retail source.
    pub attributes: Vec<SourceAttribute>,
}

/// Structural ceiling for source attributes referenced by one universal
/// vertex program. These are vertex-pulled from a storage buffer, so this is
/// not a Vulkan fixed-function vertex-location limit.
pub const PROGRAM_MAX_SOURCE_ATTRIBUTES: usize = 16;
/// Most scalar varyings a fully source-shaded (`final_color` or
/// `source_framebuffer_color`) vertex stage may pass to the pixel stage on the renderer's
/// portable Vulkan baseline.
/// They are packed four per location. Final-color programs use a compact
/// vertex-output ABI, leaving enough of the minimum 64 vertex-output
/// components for every standard pixel input they can legally request.
pub const PROGRAM_MAX_VARYINGS: usize = 40;
/// Lit surface programs additionally feed the full generic environment
/// shading interface (32 scalar components), so only eight vec4 varying
/// locations remain on the same minimum Vulkan baseline.
pub const PROGRAM_MAX_LIT_VARYINGS: usize = 32;

/// Per-vertex part of a program: source-game vertex maths evaluated once per
/// vertex and interpolated into the pixel stage, exactly like the source
/// game's own vertex shader outputs.
#[derive(Clone, Debug, PartialEq, Eq, Hash)]
pub struct ProgramVertexStage {
    /// Bytes per vertex of the source stream this stage reads. Meshes drawn
    /// with the program must carry a `SourceVertexStream` of this stride.
    pub stride: u32,
    pub attributes: Vec<SourceAttribute>,
    /// Optional skeleton joint whose current bind-relative skin matrix is
    /// exposed through `Input::SelectedJointSkinMatrix`. This stays neutral:
    /// importers assign the joint index; the renderer assigns no semantic name.
    pub skinned_joint: Option<u16>,
    /// SSA ops, same rules as the pixel ops. No texture sampling, no
    /// pixel-only inputs.
    pub ops: Vec<Op>,
    /// Values handed to the pixel stage (`Input::Varying`, component = index).
    pub varyings: Vec<Value>,
}

#[derive(Clone, Debug, PartialEq, Eq, Hash)]
pub struct SurfaceProgram {
    /// Diagnostic name (source shader).
    pub name: String,
    pub textures: Vec<ProgramTextureSlot>,
    /// Number of independently bound sampler slots the shader reads.
    pub sampler_count: u8,
    /// Number of material constant vec4s the program reads.
    pub constant_count: u16,
    pub ops: Vec<Op>,
    pub outputs: SurfaceOutputs,
    pub blend: ProgramBlend,
    /// Exact source fixed-function blend state when known. This is retained
    /// even when the current renderer uses the coarser blend path.
    pub fixed_blend: Option<ProgramFixedBlendState>,
    /// Optional per-vertex stage. Programs with one may feed either a fully
    /// source-shaded linear result or source-framebuffer result.
    pub vertex: Option<ProgramVertexStage>,
}

/// A material's use of a program: which scene textures fill its slots and
/// the constant values it provides.
#[derive(Clone, Debug)]
pub struct ProgramBinding {
    /// Index into `NeutralScene::programs`.
    pub program: usize,
    /// Scene texture per program slot (None = black).
    pub textures: Vec<Option<usize>>,
    /// Source-neutral sampler state per program sampler slot.
    pub samplers: Vec<ProgramSamplerState>,
    pub constants: Vec<[f32; 4]>,
    /// Exact source fixed-function depth state when known.
    pub depth: Option<ProgramDepthState>,
}

/// Frame-uniform source constants, computed once per frame and view.
///
/// The ops follow the pixel-op rules but may read only frame-uniform inputs
/// (camera, viewport, time, exposure and the renderer view matrices) and no
/// textures. Output `i` is frame constant vec4 `i` (`Op::FrameConstant`). The
/// renderer evaluates it on the CPU, so importers can place source view/frame
/// constant-buffer construction here instead of repeating it per pixel.
#[derive(Clone, Debug, Default, PartialEq, Eq, Hash)]
pub struct FrameProgram {
    pub ops: Vec<Op>,
    pub outputs: Vec<[Value; 4]>,
}

impl FrameProgram {
    /// Validate as the scene frame program (no constants).
    pub fn validate(&self) -> Result<(), String> {
        self.validate_as(false)
    }

    /// Validate as a frame program (`constants == false`) or as a light
    /// constant program, which may also read `Op::Constant` (the light's
    /// binding constants) and `Op::FrameConstant` (the evaluated frame).
    pub fn validate_as(&self, constants: bool) -> Result<(), String> {
        for (i, op) in self.ops.iter().enumerate() {
            // Program validation can run over thousands of recovered shader
            // operations at import time. Never allocate a Vec per unary,
            // binary or ternary instruction just to validate three indices.
            // Keep the exact original operand order and rejection messages.
            let undefined = |v: Value| (v as usize >= i).then_some(v);
            let bad = match *op {
                Op::Const(_) | Op::Constant(..) | Op::FrameConstant(..) => None,
                Op::Input(input, _) => {
                    if !frame_uniform_input(input) {
                        return Err(format!("frame op {i} reads per-pixel input {input:?}"));
                    }
                    None
                }
                Op::Unary(_, a) => undefined(a),
                Op::Binary(_, a, b) => undefined(a).or_else(|| undefined(b)),
                Op::Ternary(_, a, b, c) | Op::Select(a, b, c) => {
                    undefined(a).or_else(|| undefined(b)).or_else(|| undefined(c))
                }
                _ => return Err(format!("frame op {i} is {op:?}; frame programs cannot sample or read pixels")),
            };
            if let Some(v) = bad {
                return Err(format!("frame op {i} reads value {v} that is not defined before it"));
            }
            if !constants && matches!(op, Op::Constant(..) | Op::FrameConstant(..)) {
                return Err(format!("frame op {i} reads {op:?}; frame programs have no constants"));
            }
        }
        for out in &self.outputs {
            if let Some(&v) = out.iter().find(|&&v| v as usize >= self.ops.len()) {
                return Err(format!("frame output reads value {v} that is not defined"));
            }
        }
        Ok(())
    }

    /// Evaluate on the CPU with frame-uniform renderer `input`s.
    pub fn evaluate(&self, input: &dyn Fn(Input, u8) -> f32) -> Vec<[f32; 4]> {
        self.evaluate_with(input, &[], &[])
    }

    /// Evaluate with binding `constants` and evaluated `frame` constants (for
    /// light constant programs).
    pub fn evaluate_with(&self, input: &dyn Fn(Input, u8) -> f32, constants: &[[f32; 4]], frame: &[[f32; 4]]) -> Vec<[f32; 4]> {
        let mut values = Vec::new();
        let mut outputs = Vec::new();
        self.evaluate_with_into(input, constants, frame, &mut values, &mut outputs);
        outputs
    }

    /// Exactly the same scalar operation order/bit patterns as evaluate_with,
    /// but reuse caller-owned working buffers. Source-light scenes often run
    /// many constant programs every frame; allocating one op vector and one
    /// output vector per light is unnecessary frame-time overhead.
    pub fn evaluate_with_into(
        &self,
        input: &dyn Fn(Input, u8) -> f32,
        constants: &[[f32; 4]],
        frame: &[[f32; 4]],
        values: &mut Vec<u32>,
        outputs: &mut Vec<[f32; 4]>,
    ) {
        values.resize(self.ops.len(), 0);
        for (i, op) in self.ops.iter().enumerate() {
            values[i] = match *op {
                Op::Const(c) => c,
                Op::Input(inp, c) => w(input(inp, c)),
                Op::Constant(index, c) => w(constants.get(index as usize).map_or(0.0, |v| v[c as usize & 3])),
                Op::FrameConstant(index, c) => w(frame.get(index as usize).map_or(0.0, |v| v[c as usize & 3])),
                Op::Unary(o, a) => eval_unary(o, values[a as usize]),
                Op::Binary(o, a, b) => eval_binary(o, values[a as usize], values[b as usize]),
                Op::Ternary(o, a, b, c) => eval_ternary(o, values[a as usize], values[b as usize], values[c as usize]),
                Op::Select(c, a, b) => if values[c as usize] != 0 { values[a as usize] } else { values[b as usize] },
                _ => 0,
            };
        }
        outputs.clear();
        outputs.extend(self.outputs.iter().map(|o| o.map(|v| f(values[v as usize]))));
    }
}

/// Renderer inputs that are uniform over a frame/view.
pub fn frame_uniform_input(input: Input) -> bool {
    matches!(
        input,
        Input::CameraPosition
            | Input::Time
            | Input::ExposureMultiplier
            | Input::ViewportSize
            | Input::CameraRelativeViewProjection
            | Input::WorldToViewRotation
            | Input::PrimaryDirectionalLightDirectionToLight
            | Input::PrimaryDirectionalLightColorIntensity
    )
}

/// Where a scene light can contribute.
#[derive(Clone, Debug, PartialEq)]
pub enum SceneLightVolume {
    /// Every pixel (sun, ambient, full-screen source passes).
    Global,
    /// Points `p` (engine space) with `world_to_unit * (p, 1)` inside the unit
    /// cube [-1, 1]^3. Row-major affine transform (rows 0-2 used).
    Box { world_to_unit: [[f32; 4]; 4] },
    /// Points whose `world_to_clip * (p, 1)` projects inside x, y in [-w, w]
    /// and z in [0, w] (row-major). Used for source frustum-shaped volumes.
    Frustum { world_to_clip: [[f32; 4]; 4] },
}

/// One light: a light program, its bound resources and constants, and the
/// volume it can reach.
#[derive(Clone, Debug)]
pub struct SceneLight {
    /// `binding.program` writes `light_diffuse` / `light_specular`.
    pub binding: ProgramBinding,
    pub volume: SceneLightVolume,
    /// Per-frame constants: when set, `SceneLightingModel::constant_programs`
    /// entry `i` is evaluated once per frame/view with `Op::Constant` reading
    /// `binding.constants` and `Op::FrameConstant` reading the frame program's
    /// outputs; its outputs are the constants the light program sees. This is
    /// where source per-light constant programs (animation, view-dependent
    /// transforms) run, so light pixel programs stay shared between lights.
    pub constants_program: Option<usize>,
}

/// Texel storage of a scene-lighting texture. Values are what the source GPU
/// sampled (no sRGB decode unless the format says so).
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub enum SceneTextureFormat {
    Rgba8Unorm,
    Rgba8Srgb,
    /// Two IEEE half floats per texel (r, g); b = 0, a = 1 when sampled.
    Rg16Float,
    Rgba16Float,
    Rgba32Float,
}

impl SceneTextureFormat {
    pub fn texel_bytes(self) -> usize {
        match self {
            Self::Rgba8Unorm | Self::Rgba8Srgb | Self::Rg16Float => 4,
            Self::Rgba16Float => 8,
            Self::Rgba32Float => 16,
        }
    }
}

/// A texture owned by the scene lighting model (lookup tables, light cookies,
/// screen-independent source resources). 2D when `depth == 1` and the
/// program slot is `ProgramTextureKind::D2`, 3D for `ProgramTextureKind::D3`.
#[derive(Clone, Debug)]
pub struct SceneLightingTexture {
    pub name: String,
    pub width: u32,
    pub height: u32,
    pub depth: u32,
    pub format: SceneTextureFormat,
    /// Level 0 texels, x fastest, then y, then z.
    pub data: Vec<u8>,
}

/// Source-exact lighting, independent of forward or deferred rendering.
///
/// A material that writes `SurfaceOutputs::payload` is shaded as follows,
/// whatever the renderer's architecture:
///
/// 1. every light whose volume contains the shaded point evaluates its light
///    program on the payload; diffuse and specular results are summed;
/// 2. the composition program turns payload plus accumulation into
///    `final_color` (linear scene radiance before exposure).
///
/// A forward/clustered renderer runs both steps inside the material's pixel
/// shader; a deferred renderer stores the payload, accumulates light passes
/// and runs the composition full-screen. Light and composition programs read
/// `Input::SurfacePayload`, `Input::LightAccumulation` (composition only),
/// `Op::FrameConstant`, standard per-pixel inputs (world position, fragment
/// coordinate, viewport) and their own constants/textures.
#[derive(Clone, Debug)]
pub struct SceneLightingModel {
    /// Payload words every lit material writes.
    pub payload_words: u8,
    pub frame: FrameProgram,
    pub lights: Vec<SceneLight>,
    /// `composition.program` writes `final_color`.
    pub composition: ProgramBinding,
    /// Textures of the light and composition programs: their
    /// `ProgramBinding::textures` index this list (not `NeutralScene::textures`).
    pub textures: Vec<SceneLightingTexture>,
    /// Light constant programs (see `SceneLight::constants_program`).
    pub constant_programs: Vec<FrameProgram>,
}

impl SurfaceProgram {
    /// Semantic domain of this program's RGB output.
    #[inline]
    pub fn output_domain(&self) -> ProgramOutputDomain {
        if self.outputs.source_framebuffer_color.is_some() {
            ProgramOutputDomain::SourceFramebuffer
        } else if self.outputs.final_color.is_some() || self.outputs.payload.is_some() {
            ProgramOutputDomain::LinearScene
        } else {
            ProgramOutputDomain::LitSurface
        }
    }

    /// Structural check: every operand refers to an earlier op and every
    /// texture/constant index is in range.
    pub fn validate(&self) -> Result<(), String> {
        self.validate_ops(&self.ops, false)?;
        if let Some(stage) = &self.vertex {
            self.validate_ops(&stage.ops, true)?;
            if stage.attributes.len() > PROGRAM_MAX_SOURCE_ATTRIBUTES {
                return Err(format!("vertex stage reads {} source attributes (max {PROGRAM_MAX_SOURCE_ATTRIBUTES})", stage.attributes.len()));
            }
            let max_varyings = if self.outputs.final_color.is_some()
                || self.outputs.source_framebuffer_color.is_some()
            {
                PROGRAM_MAX_VARYINGS
            } else {
                PROGRAM_MAX_LIT_VARYINGS
            };
            if stage.varyings.len() > max_varyings {
                return Err(format!(
                    "vertex stage writes {} varyings (max {max_varyings} for this output mode)",
                    stage.varyings.len()
                ));
            }
            for attribute in &stage.attributes {
                if attribute.offset % 4 != 0 || attribute.offset + attribute.format.size() > stage.stride {
                    return Err(format!("source attribute {attribute:?} does not fit stride {}", stage.stride));
                }
            }
            for &v in &stage.varyings {
                if v as usize >= stage.ops.len() {
                    return Err(format!("varying reads vertex value {v} of {}", stage.ops.len()));
                }
            }
        }
        let n = self.ops.len();
        let out = &self.outputs;
        if out.final_color.is_some() && out.source_framebuffer_color.is_some() {
            return Err("surface program cannot write both final_color and source_framebuffer_color".to_owned());
        }
        if let Some(blend) = self.fixed_blend {
            if blend.domain == ProgramBlendDomain::SourceFramebuffer
                && self.output_domain() != ProgramOutputDomain::SourceFramebuffer
            {
                return Err(
                    "source-framebuffer fixed blend requires source-framebuffer RGB output"
                        .to_owned(),
                );
            }
        }
        if out.source_framebuffer_color.is_some()
            && (out.base_color.is_some()
                || out.world_normal.is_some()
                || out.gloss.is_some()
                || out.metallic.is_some()
                || out.occlusion.is_some()
                || out.emissive.is_some())
        {
            return Err(
                "source-framebuffer output cannot also request generic linear lighting outputs"
                    .to_owned(),
            );
        }
        let all = out
            .base_color
            .iter()
            .flatten()
            .chain(out.world_normal.iter().flatten())
            .chain(out.emissive.iter().flatten())
            .chain(out.alpha.iter())
            .chain(out.gloss.iter())
            .chain(out.metallic.iter())
            .chain(out.occlusion.iter())
            .chain(out.discard.iter())
            .chain(out.final_color.iter().flatten())
            .chain(out.source_framebuffer_color.iter().flatten())
            .chain(out.payload.iter().flatten())
            .chain(out.light_diffuse.iter().flatten())
            .chain(out.light_specular.iter().flatten());
        for &v in all {
            if v as usize >= n {
                return Err(format!("output reads value {v} that is not defined"));
            }
        }
        Ok(())
    }

    /// Operand order, resource ranges and stage rules of one op list.
    fn validate_ops(&self, ops: &[Op], vertex: bool) -> Result<(), String> {
        let check = |at: usize, v: Value| -> Result<(), String> {
            if (v as usize) < at {
                Ok(())
            } else {
                Err(format!("op {at} reads value {v} that is not defined before it"))
            }
        };
        let stage = if vertex { "vertex" } else { "pixel" };
        let varyings = self.vertex.as_ref().map_or(0, |v| v.varyings.len());
        let attributes = self.vertex.as_ref().map_or(0, |v| v.attributes.len());
        for (i, op) in ops.iter().enumerate() {
            match *op {
                Op::Const(_) => {}
                Op::Input(input, c) => {
                    let ok = match input {
                        Input::SourceAttribute => vertex && (c as usize) < attributes * 4,
                        Input::SkinnedLocalPosition
                        | Input::SkinnedLocalNormal
                        | Input::SkinnedLocalTangent => vertex && c < 4,
                        Input::Varying => !vertex && (c as usize) < varyings,
                        Input::SelectedJointSkinMatrix => {
                            vertex
                                && c < 12
                                && self
                                    .vertex
                                    .as_ref()
                                    .is_some_and(|stage| stage.skinned_joint.is_some())
                        }
                        Input::ObjectToWorld => c < 12,
                        Input::CameraRelativeViewProjection => c < 16,
                        Input::WorldToViewRotation => c < 12,
                        Input::InstanceData => c < 32,
                        // Vertex programs may consume four opaque vec4 sidecars
                        // (16 scalar lanes). Pixel programs retain the historical
                        // single interpolated vec4 contract.
                        Input::VertexData => if vertex { c < 16 } else { c < 4 },
                        Input::ViewportSize
                        | Input::PrimaryDirectionalLightDirectionToLight
                        | Input::PrimaryDirectionalLightColorIntensity => c < 4,
                        Input::FragCoord | Input::FrontFacing => !vertex,
                        Input::PrimaryDirectionalShadow => !vertex && c < 1,
                        Input::SurfacePayload => !vertex,
                        Input::LightAccumulation => !vertex && c < 6,
                        _ => true,
                    };
                    if !ok {
                        return Err(format!("{stage} op {i} reads {input:?}.{c}, which that stage does not have"));
                    }
                }
                Op::Sample { .. } | Op::SceneSample { .. } | Op::Load { .. } | Op::QueryLod { .. } | Op::QuadRead(..) if vertex => {
                    return Err(format!("vertex op {i} is {op:?}; the vertex stage cannot sample or read quads"));
                }
                _ => {}
            }
            match *op {
                Op::Const(_) | Op::Input(..) => {}
                Op::FrameConstant(_, c) => {
                    if c > 3 {
                        return Err(format!("op {i} reads frame constant lane {c}"));
                    }
                }
                Op::Constant(index, c) => {
                    if index >= self.constant_count || c > 3 {
                        return Err(format!("op {i} reads constant {index}.{c} of {}", self.constant_count));
                    }
                }
                Op::Unary(_, a) | Op::Component(a, _) | Op::QuadRead(a, _) => check(i, a)?,
                Op::Binary(_, a, b) => {
                    check(i, a)?;
                    check(i, b)?;
                }
                Op::Ternary(_, a, b, c) | Op::Select(a, b, c) => {
                    check(i, a)?;
                    check(i, b)?;
                    check(i, c)?;
                }
                Op::Sample { texture, sampler, coords, lod } => {
                    self.check_texture(i, texture)?;
                    self.check_sampler(i, sampler)?;
                    for c in coords {
                        check(i, c)?;
                    }
                    match lod {
                        Lod::Implicit => {}
                        Lod::Level(v) | Lod::Bias(v) => check(i, v)?,
                        Lod::Grad(g) => {
                            for v in g {
                                check(i, v)?;
                            }
                        }
                    }
                }
                Op::SceneSample { coords, lod, .. } => {
                    for c in coords {
                        check(i, c)?;
                    }
                    match lod {
                        Lod::Implicit => {}
                        Lod::Level(v) | Lod::Bias(v) => check(i, v)?,
                        Lod::Grad(g) => {
                            for v in g {
                                check(i, v)?;
                            }
                        }
                    }
                }
                Op::Load { texture, coords, level } => {
                    self.check_texture(i, texture)?;
                    check(i, coords[0])?;
                    check(i, coords[1])?;
                    check(i, level)?;
                }
                Op::QueryLod { texture, sampler, coords } => {
                    self.check_texture(i, texture)?;
                    self.check_sampler(i, sampler)?;
                    for c in coords {
                        check(i, c)?;
                    }
                }
            }
        }
        Ok(())
    }

    fn check_texture(&self, at: usize, texture: u8) -> Result<(), String> {
        if (texture as usize) < self.textures.len() {
            Ok(())
        } else {
            Err(format!("op {at} samples texture slot {texture} of {}", self.textures.len()))
        }
    }

    fn check_sampler(&self, at: usize, sampler: u8) -> Result<(), String> {
        if sampler < self.sampler_count {
            Ok(())
        } else {
            Err(format!(
                "op {at} samples sampler slot {sampler} of {}",
                self.sampler_count
            ))
        }
    }
}

// ---------------------------------------------------------------------------
// Reference semantics (constant folding, CPU evaluation).

#[inline]
fn f(v: u32) -> f32 {
    f32::from_bits(v)
}

#[inline]
fn w(v: f32) -> u32 {
    v.to_bits()
}

fn legacy_mul(a: f32, b: f32) -> f32 {
    if a == 0.0 || b == 0.0 {
        0.0
    } else {
        a * b
    }
}

pub fn f32_to_f16_rtz(v: f32) -> u16 {
    let bits = v.to_bits();
    let sign = ((bits >> 16) & 0x8000) as u16;
    let exp = ((bits >> 23) & 0xff) as i32;
    let mant = bits & 0x7f_ffff;
    if exp == 255 {
        return sign | 0x7c00 | if mant != 0 { 0x200 } else { 0 };
    }
    let e = exp - 127 + 15;
    if e >= 31 {
        return sign | 0x7bff;
    }
    if e <= 0 {
        if e < -10 {
            return sign;
        }
        let m = (mant | 0x80_0000) >> (14 - e);
        return sign | m as u16;
    }
    sign | ((e as u16) << 10) | (mant >> 13) as u16
}

pub fn f16_to_f32(h: u16) -> f32 {
    let sign = ((h & 0x8000) as u32) << 16;
    let exp = ((h >> 10) & 0x1f) as u32;
    let mant = (h & 0x3ff) as u32;
    let bits = if exp == 0 {
        if mant == 0 {
            sign
        } else {
            let mut e = 0i32;
            let mut m = mant;
            while m & 0x400 == 0 {
                m <<= 1;
                e -= 1;
            }
            m &= 0x3ff;
            sign | (((e + 1 + 127 - 15) as u32) << 23) | (m << 13)
        }
    } else if exp == 31 {
        sign | 0x7f80_0000 | (mant << 13)
    } else {
        sign | ((exp + 127 - 15) << 23) | (mant << 13)
    };
    f32::from_bits(bits)
}

/// (face id, s, t, 2 * major axis) of a direction, GCN cube conventions.
pub fn cube_ops(x: f32, y: f32, z: f32) -> (f32, f32, f32, f32) {
    let (ax, ay, az) = (x.abs(), y.abs(), z.abs());
    if az >= ax && az >= ay {
        let id = if z < 0.0 { 5.0 } else { 4.0 };
        let sc = if z < 0.0 { -x } else { x };
        (id, sc, -y, 2.0 * z)
    } else if ay >= ax {
        let id = if y < 0.0 { 3.0 } else { 2.0 };
        let tc = if y < 0.0 { -z } else { z };
        (id, x, tc, 2.0 * y)
    } else {
        let id = if x < 0.0 { 1.0 } else { 0.0 };
        let sc = if x < 0.0 { z } else { -z };
        (id, sc, -y, 2.0 * x)
    }
}

pub fn eval_unary(op: Unary, a: u32) -> u32 {
    let x = f(a);
    match op {
        Unary::Neg => w(-x),
        Unary::Abs => w(x.abs()),
        Unary::Floor => w(x.floor()),
        Unary::Ceil => w(x.ceil()),
        Unary::Trunc => w(x.trunc()),
        Unary::RoundEven => w(x.round_ties_even()),
        Unary::Fract => w(x - x.floor()),
        Unary::Sqrt => w(x.sqrt()),
        Unary::InverseSqrt => w(1.0 / x.sqrt()),
        Unary::Reciprocal => w(1.0 / x),
        Unary::Exp2 => w(x.exp2()),
        Unary::Log2 => w(x.log2()),
        Unary::SinTurns => w((x * std::f32::consts::TAU).sin()),
        Unary::CosTurns => w((x * std::f32::consts::TAU).cos()),
        Unary::Saturate => w(if x.is_nan() { 0.0 } else { x.clamp(0.0, 1.0) }),
        Unary::FloatToInt => (if x.is_nan() { 0 } else { x.clamp(i32::MIN as f32, i32::MAX as f32) as i32 }) as u32,
        Unary::FloatToUint => x.max(0.0).min(u32::MAX as f32) as u32,
        Unary::IntToFloat => w(a as i32 as f32),
        Unary::UintToFloat => w(a as f32),
        Unary::FloatToHalf => f32_to_f16_rtz(x) as u32,
        Unary::HalfToFloat => w(f16_to_f32(a as u16)),
        Unary::Not => !a,
        Unary::LogicalNot => (a == 0) as u32,
    }
}

pub fn eval_binary(op: Binary, a: u32, b: u32) -> u32 {
    let (x, y) = (f(a), f(b));
    let (i, j) = (a as i32, b as i32);
    match op {
        Binary::Add => w(x + y),
        Binary::Sub => w(x - y),
        Binary::Mul => w(x * y),
        Binary::MulLegacy => w(legacy_mul(x, y)),
        Binary::Div => w(x / y),
        Binary::Min => w(x.min(y)),
        Binary::Max => w(x.max(y)),
        Binary::Ldexp => w(x * 2f32.powi(j)),
        Binary::Lt => (x < y) as u32,
        Binary::Le => (x <= y) as u32,
        Binary::Gt => (x > y) as u32,
        Binary::Ge => (x >= y) as u32,
        Binary::Eq => (x == y) as u32,
        Binary::Ne => (x != y) as u32,
        Binary::IAdd => a.wrapping_add(b),
        Binary::ISub => a.wrapping_sub(b),
        Binary::IMul => a.wrapping_mul(b),
        Binary::IMin => i.min(j) as u32,
        Binary::IMax => i.max(j) as u32,
        Binary::UMin => a.min(b),
        Binary::UMax => a.max(b),
        Binary::And => a & b,
        Binary::Or => a | b,
        Binary::Xor => a ^ b,
        Binary::Shl => a.wrapping_shl(b & 31),
        Binary::ShrU => a.wrapping_shr(b & 31),
        Binary::ShrI => (i >> (b & 31)) as u32,
        Binary::ILt => (i < j) as u32,
        Binary::ILe => (i <= j) as u32,
        Binary::IGt => (i > j) as u32,
        Binary::IGe => (i >= j) as u32,
        Binary::IEq => (a == b) as u32,
        Binary::INe => (a != b) as u32,
        Binary::ULt => (a < b) as u32,
        Binary::ULe => (a <= b) as u32,
        Binary::UGt => (a > b) as u32,
        Binary::UGe => (a >= b) as u32,
        Binary::PackHalf2 => f32_to_f16_rtz(x) as u32 | (f32_to_f16_rtz(y) as u32) << 16,
    }
}

pub fn eval_ternary(op: Ternary, a: u32, b: u32, c: u32) -> u32 {
    let (x, y, z) = (f(a), f(b), f(c));
    match op {
        Ternary::Fma => w(x.mul_add(y, z)),
        Ternary::MadLegacy => w(legacy_mul(x, y) + z),
        Ternary::Min3 => w(x.min(y).min(z)),
        Ternary::Max3 => w(x.max(y).max(z)),
        Ternary::Med3 => w(x.max(y).min(x.min(y).max(z))),
        Ternary::BitExtractU => {
            let (off, width) = (b & 31, c & 31);
            if width == 0 {
                0
            } else {
                (a >> off) & ((1u32 << width).wrapping_sub(1))
            }
        }
        Ternary::BitSelect => (a & b) | (!a & c),
        Ternary::CubeId | Ternary::CubeS | Ternary::CubeT | Ternary::CubeMajor2 => {
            let (id, s, t, ma) = cube_ops(x, y, z);
            w(match op {
                Ternary::CubeId => id,
                Ternary::CubeS => s,
                Ternary::CubeT => t,
                _ => ma,
            })
        }
    }
}

/// Values a CPU evaluation of one pixel produced.
#[derive(Clone, Debug, Default)]
pub struct EvaluatedSurface {
    pub base_color: Option<[f32; 3]>,
    pub alpha: Option<f32>,
    pub world_normal: Option<[f32; 3]>,
    pub gloss: Option<f32>,
    pub metallic: Option<f32>,
    pub occlusion: Option<f32>,
    pub emissive: Option<[f32; 3]>,
    pub final_color: Option<[f32; 3]>,
    pub source_framebuffer_color: Option<[f32; 3]>,
    pub payload: Option<Vec<f32>>,
    pub light_diffuse: Option<[f32; 3]>,
    pub light_specular: Option<[f32; 3]>,
    pub discard: bool,
}

/// Evaluate a program for one pixel on the CPU. Quad reads return the
/// pixel's own value and implicit LOD is `implicit_lod`.
pub fn evaluate(
    program: &SurfaceProgram,
    input: &dyn Fn(Input, u8) -> f32,
    constants: &[[f32; 4]],
    sample: &dyn Fn(u8, u8, [f32; 3], Option<f32>) -> [f32; 4],
    load: &dyn Fn(u8, [i32; 2], u32) -> [f32; 4],
) -> EvaluatedSurface {
    evaluate_with_values(program, input, constants, sample, load).0
}

/// `evaluate`, also returning every op's result word.
pub fn evaluate_with_values(
    program: &SurfaceProgram,
    input: &dyn Fn(Input, u8) -> f32,
    constants: &[[f32; 4]],
    sample: &dyn Fn(u8, u8, [f32; 3], Option<f32>) -> [f32; 4],
    load: &dyn Fn(u8, [i32; 2], u32) -> [f32; 4],
) -> (EvaluatedSurface, Vec<u32>) {
    evaluate_with_frame(program, input, constants, &[], sample, load)
}

/// `evaluate_with_values` with the scene frame constants (`Op::FrameConstant`).
pub fn evaluate_with_frame(
    program: &SurfaceProgram,
    input: &dyn Fn(Input, u8) -> f32,
    constants: &[[f32; 4]],
    frame: &[[f32; 4]],
    sample: &dyn Fn(u8, u8, [f32; 3], Option<f32>) -> [f32; 4],
    load: &dyn Fn(u8, [i32; 2], u32) -> [f32; 4],
) -> (EvaluatedSurface, Vec<u32>) {
    let mut vals = vec![0u32; program.ops.len()];
    let mut vec_results: std::collections::HashMap<usize, [f32; 4]> = std::collections::HashMap::new();
    for (i, op) in program.ops.iter().enumerate() {
        vals[i] = match *op {
            Op::Const(c) => c,
            Op::Input(inp, c) => w(input(inp, c)),
            Op::Constant(index, c) => w(constants.get(index as usize).map_or(0.0, |v| v[c as usize])),
            Op::FrameConstant(index, c) => w(frame.get(index as usize).map_or(0.0, |v| v[c as usize])),
            Op::Unary(o, a) => eval_unary(o, vals[a as usize]),
            Op::Binary(o, a, b) => eval_binary(o, vals[a as usize], vals[b as usize]),
            Op::Ternary(o, a, b, c) => eval_ternary(o, vals[a as usize], vals[b as usize], vals[c as usize]),
            Op::Select(c, a, b) => {
                if vals[c as usize] != 0 {
                    vals[a as usize]
                } else {
                    vals[b as usize]
                }
            }
            Op::Sample { texture, sampler, coords, lod } => {
                let coords = coords.map(|c| f(vals[c as usize]));
                let level = match lod {
                    Lod::Level(v) => Some(f(vals[v as usize])),
                    _ => None,
                };
                vec_results.insert(i, sample(texture, sampler, coords, level));
                0
            }
            Op::SceneSample { .. } => {
                // The generic CPU evaluator has no scene resource table.
                // Renderer-backed tests exercise this op through generated
                // WGSL; callers that need CPU scene sampling can add a
                // dedicated evaluator without weakening runtime semantics.
                vec_results.insert(i, [0.0; 4]);
                0
            }
            Op::Load { texture, coords, level } => {
                vec_results.insert(i, load(texture, coords.map(|c| vals[c as usize] as i32), vals[level as usize]));
                0
            }
            Op::QueryLod { .. } => {
                vec_results.insert(i, [0.0; 4]);
                0
            }
            Op::Component(v, c) => w(vec_results.get(&(v as usize)).map_or(0.0, |r| r[c as usize])),
            Op::QuadRead(v, _) => vals[v as usize],
        };
    }
    let get = |v: Value| f(vals[v as usize]);
    let out = &program.outputs;
    let result = EvaluatedSurface {
        base_color: out.base_color.map(|c| c.map(get)),
        alpha: out.alpha.map(get),
        world_normal: out.world_normal.map(|c| c.map(get)),
        gloss: out.gloss.map(get),
        metallic: out.metallic.map(get),
        occlusion: out.occlusion.map(get),
        emissive: out.emissive.map(|c| c.map(get)),
        discard: out.discard.is_some_and(|v| vals[v as usize] != 0),
        final_color: out.final_color.map(|c| c.map(get)),
        source_framebuffer_color: out.source_framebuffer_color.map(|c| c.map(get)),
        payload: out.payload.as_ref().map(|p| p.iter().map(|&v| get(v)).collect()),
        light_diffuse: out.light_diffuse.map(|c| c.map(get)),
        light_specular: out.light_specular.map(|c| c.map(get)),
    };
    (result, vals)
}

#[cfg(test)]
mod reusable_frame_program_scratch_tests {
    use super::*;

    #[test]
    fn allocation_free_frame_validation_keeps_original_dependency_checks() {
        let invalid = FrameProgram {
            ops: vec![
                Op::Const(0.0_f32.to_bits()),
                Op::Binary(Binary::Add, 0, 2),
            ],
            outputs: Vec::new(),
        };
        assert_eq!(
            invalid.validate().unwrap_err(),
            "frame op 1 reads value 2 that is not defined before it"
        );

        let wrong_stage = FrameProgram {
            ops: vec![Op::Input(Input::FragCoord, 0)],
            outputs: vec![[0; 4]],
        };
        assert!(wrong_stage.validate().unwrap_err().contains("per-pixel input"));

        let constant = FrameProgram {
            ops: vec![Op::Constant(0, 1)],
            outputs: vec![[0; 4]],
        };
        assert!(constant.validate().is_err());
        assert!(constant.validate_as(true).is_ok());
    }

    #[test]
    fn reused_scratch_keeps_frame_constants_and_time_bit_exact() {
        let program = FrameProgram {
            ops: vec![
                Op::Const(1.5_f32.to_bits()),
                Op::Input(Input::Time, 0),
                Op::Constant(0, 0),
                Op::FrameConstant(0, 1),
                Op::Binary(Binary::Add, 0, 1),
            ],
            outputs: vec![[4, 2, 3, 1]],
        };
        program.validate_as(true).unwrap();
        let constants = [[7.0, 0.0, 0.0, 0.0]];
        let frame = [[0.0, 11.0, 0.0, 0.0]];
        let mut values = Vec::new();
        let mut outputs = Vec::new();
        for time in [2.0_f32, 3.0, -1.0, 12.25, 2.0] {
            let input = |kind, _| match kind {
                Input::Time => time,
                _ => 0.0,
            };
            let ordinary = program.evaluate_with(&input, &constants, &frame);
            program.evaluate_with_into(
                &input, &constants, &frame, &mut values, &mut outputs,
            );
            assert_eq!(outputs.len(), 1);
            assert_eq!(outputs[0].map(f32::to_bits), ordinary[0].map(f32::to_bits));
            assert_eq!(outputs[0][0].to_bits(), (1.5 + time).to_bits());
            assert_eq!(outputs[0][1], 7.0);
            assert_eq!(outputs[0][2], 11.0);
        }
    }

    #[test]
    fn scratch_handles_shrinking_and_growing_programs_without_stale_ops() {
        let long = FrameProgram {
            ops: vec![Op::Const(3.0_f32.to_bits()), Op::Const(8.0_f32.to_bits())],
            outputs: vec![[0, 1, 0, 1]],
        };
        let short = FrameProgram {
            ops: vec![Op::Const(5.0_f32.to_bits())],
            outputs: vec![[0, 0, 0, 0]],
        };
        let mut values = Vec::new();
        let mut outputs = Vec::new();
        long.evaluate_with_into(&|_, _| 0.0, &[], &[], &mut values, &mut outputs);
        assert_eq!(outputs, vec![[3.0, 8.0, 3.0, 8.0]]);
        short.evaluate_with_into(&|_, _| 0.0, &[], &[], &mut values, &mut outputs);
        assert_eq!(outputs, vec![[5.0; 4]]);
        long.evaluate_with_into(&|_, _| 0.0, &[], &[], &mut values, &mut outputs);
        assert_eq!(outputs, vec![[3.0, 8.0, 3.0, 8.0]]);
    }
}
