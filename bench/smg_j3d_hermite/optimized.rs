//! J3D BCK / ANK1 skeletal animation decoder.
//!
//! SMG uses BCK joint animation for authored map-object states such as the
//! Comet Observatory's "Revival" pose. The source-specific format terminates
//! here: callers receive only per-joint S/R/T values in radians/source units.

/// J3D full mesh-visibility animation (BVA/VAF1).
///
/// Tracks are indexed by SHP1 logical shape index. Values are the authored
/// GX/J3D visibility bytes normalized to booleans; sampling retains J3D's
/// nearest-frame frame+0.5 and per-track terminal clamping semantics.
#[derive(Clone, Debug)]
pub struct J3dBva {
    pub loop_mode: u8,
    pub duration: f32,
    tracks: Vec<Vec<bool>>,
}

impl J3dBva {
    #[inline]
    pub fn track_count(&self) -> usize {
        self.tracks.len()
    }

    #[inline]
    pub fn tracks(&self) -> &[Vec<bool>] {
        &self.tracks
    }

    pub fn sample(&self, frame: f32) -> Vec<bool> {
        self.tracks
            .iter()
            .map(|track| {
                if track.is_empty() {
                    return true;
                }
                // J3DAnmVisibilityFull::getVisibility rounds the current
                // frame, then clamps independently to each track's last key.
                let rounded = (frame + 0.5).floor();
                let index = if !rounded.is_finite() || rounded <= 0.0 {
                    0
                } else {
                    (rounded as usize).min(track.len() - 1)
                };
                track[index]
            })
            .collect()
    }

    #[inline]
    pub fn sample_start(&self) -> Vec<bool> {
        self.sample(0.0)
    }
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct J3dJointPose {
    pub scale: [f32; 3],
    pub rotation_radians: [f32; 3],
    pub translation: [f32; 3],
}

#[derive(Clone, Copy, Debug)]
struct Keyframe {
    time: f32,
    value: f32,
    tangent_in: f32,
    tangent_out: f32,
}

#[derive(Clone, Debug)]
struct Track {
    frames: Vec<Keyframe>,
    // Parsed ANK1 keyframes are ordered, but NaN times were previously
    // accepted. Preserve the original linear sampler for those inputs.
    binary_searchable: bool,
}

/// One Hermite key retained from a J3D animation for exact runtime replay.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct J3dAnimationKeyframe {
    pub time: f32,
    pub value: f32,
    pub tangent_in: f32,
    pub tangent_out: f32,
}

/// A source animation curve in frame units.
#[derive(Clone, Debug, PartialEq)]
pub struct J3dAnimationTrack {
    pub frames: Vec<J3dAnimationKeyframe>,
}

/// Four-channel TEV-register animation retained from a BRK/TRK1 resource.
/// The importer lowers this to generic SurfaceProgram Time math; GX/J3D
/// register names do not escape into the renderer.
#[derive(Clone, Debug, PartialEq)]
pub struct J3dColorAnimation {
    pub duration: f32,
    pub loop_mode: u8,
    pub channels: [J3dAnimationTrack; 4],
}

#[derive(Clone, Debug, PartialEq)]
pub struct J3dBpkColorUpdate {
    pub material_name: String,
    /// PAK1 in SMG animates the primary material color register (MAT0).
    pub values: [f32; 4],
}

#[derive(Clone, Debug)]
struct BpkEntry {
    material_name: String,
    channels: [Track; 4],
}

#[derive(Clone, Debug)]
pub struct J3dBpk {
    pub duration: f32,
    pub loop_mode: u8,
    entries: Vec<BpkEntry>,
}

impl J3dBpk {
    pub fn runtime_entries(&self) -> Vec<(String, J3dColorAnimation)> {
        self.entries
            .iter()
            .map(|entry| {
                (
                    entry.material_name.clone(),
                    J3dColorAnimation {
                        duration: self.duration,
                        loop_mode: self.loop_mode,
                        channels: std::array::from_fn(|channel| (&entry.channels[channel]).into()),
                    },
                )
            })
            .collect()
    }

    pub fn sample(&self, frame: f32) -> Vec<J3dBpkColorUpdate> {
        self.entries
            .iter()
            .map(|entry| J3dBpkColorUpdate {
                material_name: entry.material_name.clone(),
                values: std::array::from_fn(|channel| {
                    sample_track(&entry.channels[channel], frame)
                }),
            })
            .collect()
    }

    pub fn sample_start(&self) -> Vec<J3dBpkColorUpdate> {
        self.sample(0.0)
    }

    pub fn sample_end(&self) -> Vec<J3dBpkColorUpdate> {
        self.sample(self.duration)
    }
}

/// One live BTK texture-SRT target after its J3D container has been decoded.
/// The renderer never sees this type; the SMG importer lowers it into the
/// universal SurfaceProgram Time input.
#[derive(Clone, Debug, PartialEq)]
pub struct J3dTextureSrtAnimation {
    pub duration: f32,
    pub loop_mode: u8,
    pub is_maya: bool,
    pub center: [f32; 3],
    pub scale_s: J3dAnimationTrack,
    pub scale_t: J3dAnimationTrack,
    /// Effective J3D signed-short rotation units before conversion to radians.
    pub rotation: J3dAnimationTrack,
    pub translation_s: J3dAnimationTrack,
    pub translation_t: J3dAnimationTrack,
}

impl From<&Track> for J3dAnimationTrack {
    fn from(track: &Track) -> Self {
        Self {
            frames: track
                .frames
                .iter()
                .map(|key| J3dAnimationKeyframe {
                    time: key.time,
                    value: key.value,
                    tangent_in: key.tangent_in,
                    tangent_out: key.tangent_out,
                })
                .collect(),
        }
    }
}

#[derive(Clone, Debug)]
struct JointAnimation {
    scale: [Track; 3],
    rotation: [Track; 3],
    translation: [Track; 3],
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum J3dJointSamplingMode {
    HermiteKey,
    FullNearest,
}

#[derive(Clone, Debug)]
pub struct J3dBck {
    pub duration: f32,
    /// J3DFrameCtrl source loop mode, retained for both BCK/ANK1 and BCA/ANF1.
    pub loop_mode: u8,
    sampling: J3dJointSamplingMode,
    joints: Vec<JointAnimation>,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum J3dBrkTarget {
    Register(u8),
    Konst(u8),
}

#[derive(Clone, Debug, PartialEq)]
pub struct J3dBrkColorUpdate {
    pub material_name: String,
    pub target: J3dBrkTarget,
    pub values: [f32; 4],
}

#[derive(Clone, Debug)]
struct BrkEntry {
    material_name: String,
    target: J3dBrkTarget,
    channels: [Track; 4],
}

#[derive(Clone, Debug)]
pub struct J3dBrk {
    pub duration: f32,
    /// J3DFrameCtrl loop mode encoded by TRK1.
    pub loop_mode: u8,
    entries: Vec<BrkEntry>,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct J3dBtpUpdate {
    pub material_name: String,
    pub tex_map_index: u8,
    pub texture_index: u16,
}

#[derive(Clone, Debug)]
struct BtpEntry {
    material_name: String,
    tex_map_index: u8,
    texture_indices: Vec<u16>,
}

#[derive(Clone, Debug)]
pub struct J3dBtp {
    pub duration: f32,
    entries: Vec<BtpEntry>,
}

#[derive(Clone, Debug, PartialEq)]
pub struct J3dBtkUpdate {
    pub material_name: String,
    pub tex_mtx_index: u8,
    pub center: [f32; 3],
    pub scale: [f32; 2],
    /// Same signed-short rotation domain J3D MAT3 stores in TexMtx SRT.
    pub rotation_s16: i16,
    pub translation: [f32; 2],
    pub is_maya: bool,
}

#[derive(Clone, Debug)]
struct BtkEntry {
    material_name: String,
    tex_mtx_index: u8,
    center: [f32; 3],
    scale_s: Track,
    scale_t: Track,
    rotation: Track,
    translation_s: Track,
    translation_t: Track,
}

#[derive(Clone, Debug)]
pub struct J3dBtk {
    pub duration: f32,
    /// J3DFrameCtrl loop mode: 0 Once, 1 OnceAndReset, 2 Repeat,
    /// 3 MirroredOnce, 4 MirroredRepeat.
    pub loop_mode: u8,
    pub is_maya: bool,
    entries: Vec<BtkEntry>,
}

impl J3dBtk {
    /// Exact live texture-SRT targets for universal runtime lowering.
    pub fn runtime_entries(&self) -> Vec<(String, u8, J3dTextureSrtAnimation)> {
        self.entries
            .iter()
            .map(|entry| {
                (
                    entry.material_name.clone(),
                    entry.tex_mtx_index,
                    J3dTextureSrtAnimation {
                        duration: self.duration,
                        loop_mode: self.loop_mode,
                        is_maya: self.is_maya,
                        center: entry.center,
                        scale_s: (&entry.scale_s).into(),
                        scale_t: (&entry.scale_t).into(),
                        rotation: (&entry.rotation).into(),
                        translation_s: (&entry.translation_s).into(),
                        translation_t: (&entry.translation_t).into(),
                    },
                )
            })
            .collect()
    }

    pub fn sample(&self, frame: f32) -> Vec<J3dBtkUpdate> {
        self.entries
            .iter()
            .map(|entry| J3dBtkUpdate {
                material_name: entry.material_name.clone(),
                tex_mtx_index: entry.tex_mtx_index,
                center: entry.center,
                scale: [
                    sample_track(&entry.scale_s, frame),
                    sample_track(&entry.scale_t, frame),
                ],
                rotation_s16: sample_track(&entry.rotation, frame)
                    .round()
                    .clamp(i16::MIN as f32, i16::MAX as f32) as i16,
                translation: [
                    sample_track(&entry.translation_s, frame),
                    sample_track(&entry.translation_t, frame),
                ],
                is_maya: self.is_maya,
            })
            .collect()
    }

    pub fn sample_start(&self) -> Vec<J3dBtkUpdate> {
        self.sample(0.0)
    }

    pub fn sample_end(&self) -> Vec<J3dBtkUpdate> {
        self.sample(self.duration)
    }
}

impl J3dBtp {
    pub fn sample(&self, frame: f32) -> Vec<J3dBtpUpdate> {
        self.entries
            .iter()
            .filter_map(|entry| {
                if entry.texture_indices.is_empty() {
                    return None;
                }
                // J3DAnmTexPattern::getTexNo():
                //   frame < 0         -> first pattern entry
                //   frame >= maxFrame -> last pattern entry
                //   otherwise         -> truncating frame index
                let index = if frame < 0.0 {
                    0
                } else if frame >= entry.texture_indices.len() as f32 {
                    entry.texture_indices.len() - 1
                } else {
                    frame as usize
                };
                Some(J3dBtpUpdate {
                    material_name: entry.material_name.clone(),
                    tex_map_index: entry.tex_map_index,
                    texture_index: entry.texture_indices[index],
                })
            })
            .collect()
    }

    pub fn sample_end(&self) -> Vec<J3dBtpUpdate> {
        // MR::setAllAnimFrameAtEnd() sets the BTP player to J3DFrameCtrl::getEnd().
        // Individual TPT1 entries clamp that frame to their final pattern entry.
        self.sample(self.duration)
    }
}

impl J3dBrk {
    /// Exact live TEV color-register targets for universal runtime lowering.
    pub fn runtime_entries(&self) -> Vec<(String, J3dBrkTarget, J3dColorAnimation)> {
        self.entries
            .iter()
            .map(|entry| {
                (
                    entry.material_name.clone(),
                    entry.target,
                    J3dColorAnimation {
                        duration: self.duration,
                        loop_mode: self.loop_mode,
                        channels: std::array::from_fn(|channel| (&entry.channels[channel]).into()),
                    },
                )
            })
            .collect()
    }

    pub fn sample(&self, frame: f32) -> Vec<J3dBrkColorUpdate> {
        self.entries
            .iter()
            .map(|entry| J3dBrkColorUpdate {
                material_name: entry.material_name.clone(),
                target: entry.target,
                values: std::array::from_fn(|channel| {
                    sample_track(&entry.channels[channel], frame)
                }),
            })
            .collect()
    }

    /// MR::setAllAnimFrameAtEnd() assigns J3DFrameCtrl::getEnd() to BRK too.
    pub fn sample_end(&self) -> Vec<J3dBrkColorUpdate> {
        self.sample(self.duration)
    }
}

impl J3dBck {
    pub fn sample(&self, frame: f32) -> Vec<J3dJointPose> {
        let sample = |track: &Track| match self.sampling {
            J3dJointSamplingMode::HermiteKey => sample_track(track, frame),
            J3dJointSamplingMode::FullNearest => sample_full_track(track, frame),
        };
        self.joints
            .iter()
            .map(|joint| J3dJointPose {
                scale: std::array::from_fn(|axis| sample(&joint.scale[axis])),
                rotation_radians: std::array::from_fn(|axis| sample(&joint.rotation[axis])),
                translation: std::array::from_fn(|axis| sample(&joint.translation[axis])),
            })
            .collect()
    }

    #[inline]
    pub fn uses_nearest_frame_sampling(&self) -> bool {
        self.sampling == J3dJointSamplingMode::FullNearest
    }

    /// Retail MR::setAllAnimFrameAtEnd() assigns J3DFrameCtrl::getEnd()
    /// directly, so the source-authored terminal pose is sampled at duration.
    pub fn sample_end(&self) -> Vec<J3dJointPose> {
        self.sample(self.duration)
    }
}

pub fn decode_bva(bytes: &[u8]) -> Result<J3dBva, String> {
    if bytes.get(0..8) != Some(&b"J3D1bva1"[..]) {
        return Err("BVA magic is not J3D1bva1".to_owned());
    }
    let chunk_count = be32(bytes, 0x0c)? as usize;
    let mut off = 0x20usize;
    for _ in 0..chunk_count {
        let tag = bytes.get(off..off + 4).ok_or("BVA chunk tag out of range")?;
        let size = be32(bytes, off + 4)? as usize;
        let end = off.checked_add(size).ok_or("BVA chunk size overflow")?;
        if size < 8 || end > bytes.len() {
            return Err(format!("BVA chunk at 0x{off:x} has invalid size 0x{size:x}"));
        }
        if tag == &b"VAF1"[..] {
            return decode_vaf1(&bytes[off..end]);
        }
        off = end;
    }
    Err("BVA contains no VAF1 chunk".to_owned())
}

pub fn decode_bva_start_state(bytes: &[u8]) -> Result<Vec<bool>, String> {
    Ok(decode_bva(bytes)?.sample_start())
}

fn decode_vaf1(bytes: &[u8]) -> Result<J3dBva, String> {
    if bytes.get(0..4) != Some(&b"VAF1"[..]) {
        return Err("animation chunk is not VAF1".to_owned());
    }
    let loop_mode = byte(bytes, 0x08)?;
    if loop_mode > 4 {
        return Err(format!("VAF1 loop mode {loop_mode} is outside J3DFrameCtrl 0..=4"));
    }
    let duration = be16(bytes, 0x0a)? as f32;
    let track_count = be16(bytes, 0x0c)? as usize;
    let value_count = be16(bytes, 0x0e)? as usize;
    let track_off = be32(bytes, 0x10)? as usize;
    let value_off = be32(bytes, 0x14)? as usize;

    let values_end = value_off
        .checked_add(value_count)
        .ok_or("VAF1 visibility table size overflow")?;
    let values = bytes
        .get(value_off..values_end)
        .ok_or_else(|| {
            format!(
                "VAF1 visibility table 0x{value_off:x}..0x{values_end:x} is out of range"
            )
        })?;

    let mut tracks = Vec::with_capacity(track_count);
    for index in 0..track_count {
        let at = track_off
            .checked_add(index.checked_mul(4).ok_or("VAF1 track offset overflow")?)
            .ok_or("VAF1 track offset overflow")?;
        let count = be16(bytes, at)? as usize;
        let first = be16(bytes, at + 2)? as usize;
        if count == 0 {
            return Err(format!("VAF1 visibility track {index} has zero frames"));
        }
        let end = first
            .checked_add(count)
            .ok_or("VAF1 visibility track range overflow")?;
        if end > values.len() {
            return Err(format!(
                "VAF1 visibility track {index} range {first}..{end} exceeds {value_count} values"
            ));
        }
        tracks.push(values[first..end].iter().map(|value| *value != 0).collect());
    }

    Ok(J3dBva {
        loop_mode,
        duration,
        tracks,
    })
}

pub fn decode_bpk(bytes: &[u8]) -> Result<J3dBpk, String> {
    if bytes.get(0..8) != Some(&b"J3D1bpk1"[..]) {
        return Err("BPK magic is not J3D1bpk1".to_owned());
    }
    let chunk_count = be32(bytes, 0x0c)? as usize;
    let mut off = 0x20usize;
    for _ in 0..chunk_count {
        let tag = bytes.get(off..off + 4).ok_or("BPK chunk tag out of range")?;
        let size = be32(bytes, off + 4)? as usize;
        let end = off.checked_add(size).ok_or("BPK chunk size overflow")?;
        if size < 8 || end > bytes.len() {
            return Err(format!("BPK chunk at 0x{off:x} has invalid size 0x{size:x}"));
        }
        if tag == &b"PAK1"[..] {
            return decode_pak1(&bytes[off..end]);
        }
        off = end;
    }
    Err("BPK contains no PAK1 chunk".to_owned())
}

pub fn decode_bpk_start_state(bytes: &[u8]) -> Result<Vec<J3dBpkColorUpdate>, String> {
    Ok(decode_bpk(bytes)?.sample_start())
}

pub fn decode_bpk_end_state(bytes: &[u8]) -> Result<Vec<J3dBpkColorUpdate>, String> {
    Ok(decode_bpk(bytes)?.sample_end())
}

pub fn decode_bck(bytes: &[u8]) -> Result<J3dBck, String> {
    if bytes.get(0..8) != Some(&b"J3D1bck1"[..]) {
        return Err("BCK magic is not J3D1bck1".to_owned());
    }
    let chunk_count = be32(bytes, 0x0c)? as usize;
    let mut off = 0x20usize;
    for _ in 0..chunk_count {
        let tag = bytes.get(off..off + 4).ok_or("BCK chunk tag out of range")?;
        let size = be32(bytes, off + 4)? as usize;
        let Some(end) = off.checked_add(size) else {
            return Err("BCK chunk size overflow".to_owned());
        };
        if size < 8 || end > bytes.len() {
            return Err(format!("BCK chunk at 0x{off:x} has invalid size 0x{size:x}"));
        }
        if tag == &b"ANK1"[..] {
            return decode_ank1(&bytes[off..end]);
        }
        off = end;
    }
    Err("BCK contains no ANK1 chunk".to_owned())
}

pub fn decode_bck_start_pose(bytes: &[u8]) -> Result<Vec<J3dJointPose>, String> {
    Ok(decode_bck(bytes)?.sample(0.0))
}

pub fn decode_bck_end_pose(bytes: &[u8]) -> Result<Vec<J3dJointPose>, String> {
    Ok(decode_bck(bytes)?.sample_end())
}

pub fn decode_bca(bytes: &[u8]) -> Result<J3dBck, String> {
    if bytes.get(0..8) != Some(&b"J3D1bca1"[..]) {
        return Err("BCA magic is not J3D1bca1".to_owned());
    }
    let chunk_count = be32(bytes, 0x0c)? as usize;
    let mut off = 0x20usize;
    for _ in 0..chunk_count {
        let tag = bytes.get(off..off + 4).ok_or("BCA chunk tag out of range")?;
        let size = be32(bytes, off + 4)? as usize;
        let end = off.checked_add(size).ok_or("BCA chunk size overflow")?;
        if size < 8 || end > bytes.len() {
            return Err(format!("BCA chunk at 0x{off:x} has invalid size 0x{size:x}"));
        }
        if tag == &b"ANF1"[..] {
            return decode_anf1(&bytes[off..end]);
        }
        off = end;
    }
    Err("BCA contains no ANF1 chunk".to_owned())
}

fn decode_anf1(bytes: &[u8]) -> Result<J3dBck, String> {
    if bytes.get(0..4) != Some(&b"ANF1"[..]) {
        return Err("animation chunk is not ANF1".to_owned());
    }
    let loop_mode = byte(bytes, 0x08)?;
    if loop_mode > 4 {
        return Err(format!("ANF1 loop mode {loop_mode} is outside J3DFrameCtrl 0..=4"));
    }
    // ANF1 byte 0x09 is serialized but J3DAnmTransformFull does not apply the
    // ANK1 decShift. Full rotations use the native s16 angle domain directly.
    let _rotation_decimal = byte(bytes, 0x09)?;
    let duration = be16(bytes, 0x0a)? as f32;
    let joint_count = be16(bytes, 0x0c)? as usize;
    let scale_count = be16(bytes, 0x0e)? as usize;
    let rotation_count = be16(bytes, 0x10)? as usize;
    let translation_count = be16(bytes, 0x12)? as usize;
    let animation_off = be32(bytes, 0x14)? as usize;
    let scale_off = be32(bytes, 0x18)? as usize;
    let rotation_off = be32(bytes, 0x1c)? as usize;
    let translation_off = be32(bytes, 0x20)? as usize;

    let scale_data = read_f32_table(bytes, scale_off, scale_count)?;
    let rotation_data = read_i16_table(bytes, rotation_off, rotation_count)?;
    let translation_data = read_f32_table(bytes, translation_off, translation_count)?;
    let rotation_scale = core::f32::consts::PI / 32767.0;

    let descriptor_bytes = joint_count
        .checked_mul(3)
        .and_then(|value| value.checked_mul(12))
        .ok_or("ANF1 descriptor size overflow")?;
    let descriptor_end = animation_off
        .checked_add(descriptor_bytes)
        .ok_or("ANF1 descriptor overflow")?;
    if descriptor_end > bytes.len() {
        return Err("ANF1 joint animation table is truncated".to_owned());
    }

    let mut cursor = animation_off;
    let mut joints = Vec::with_capacity(joint_count);
    for _ in 0..joint_count {
        let mut scale = Vec::with_capacity(3);
        let mut rotation = Vec::with_capacity(3);
        let mut translation = Vec::with_capacity(3);
        for _axis in 0..3 {
            scale.push(read_full_track(bytes, &mut cursor, &scale_data, 1.0)?);
            rotation.push(read_full_track(
                bytes,
                &mut cursor,
                &rotation_data,
                rotation_scale,
            )?);
            translation.push(read_full_track(
                bytes,
                &mut cursor,
                &translation_data,
                1.0,
            )?);
        }
        joints.push(JointAnimation {
            scale: scale
                .try_into()
                .map_err(|_| "ANF1 scale track count mismatch".to_owned())?,
            rotation: rotation
                .try_into()
                .map_err(|_| "ANF1 rotation track count mismatch".to_owned())?,
            translation: translation
                .try_into()
                .map_err(|_| "ANF1 translation track count mismatch".to_owned())?,
        });
    }

    Ok(J3dBck {
        duration: if duration == 0.0 { 1.0 } else { duration },
        loop_mode,
        sampling: J3dJointSamplingMode::FullNearest,
        joints,
    })
}

pub fn decode_brk(bytes: &[u8]) -> Result<J3dBrk, String> {
    if bytes.get(0..8) != Some(&b"J3D1brk1"[..]) {
        return Err("BRK magic is not J3D1brk1".to_owned());
    }
    let chunk_count = be32(bytes, 0x0c)? as usize;
    let mut off = 0x20usize;
    for _ in 0..chunk_count {
        let tag = bytes.get(off..off + 4).ok_or("BRK chunk tag out of range")?;
        let size = be32(bytes, off + 4)? as usize;
        let Some(end) = off.checked_add(size) else {
            return Err("BRK chunk size overflow".to_owned());
        };
        if size < 8 || end > bytes.len() {
            return Err(format!("BRK chunk at 0x{off:x} has invalid size 0x{size:x}"));
        }
        if tag == &b"TRK1"[..] {
            return decode_trk1(&bytes[off..end]);
        }
        off = end;
    }
    Err("BRK contains no TRK1 chunk".to_owned())
}

pub fn decode_brk_start_state(bytes: &[u8]) -> Result<Vec<J3dBrkColorUpdate>, String> {
    Ok(decode_brk(bytes)?.sample(0.0))
}

pub fn decode_brk_end_state(bytes: &[u8]) -> Result<Vec<J3dBrkColorUpdate>, String> {
    Ok(decode_brk(bytes)?.sample_end())
}

pub fn decode_btp(bytes: &[u8]) -> Result<J3dBtp, String> {
    if bytes.get(0..8) != Some(&b"J3D1btp1"[..]) {
        return Err("BTP magic is not J3D1btp1".to_owned());
    }
    let chunk_count = be32(bytes, 0x0c)? as usize;
    let mut off = 0x20usize;
    for _ in 0..chunk_count {
        let tag = bytes.get(off..off + 4).ok_or("BTP chunk tag out of range")?;
        let size = be32(bytes, off + 4)? as usize;
        let Some(end) = off.checked_add(size) else {
            return Err("BTP chunk size overflow".to_owned());
        };
        if size < 8 || end > bytes.len() {
            return Err(format!("BTP chunk at 0x{off:x} has invalid size 0x{size:x}"));
        }
        if tag == &b"TPT1"[..] {
            return decode_tpt1(&bytes[off..end]);
        }
        off = end;
    }
    Err("BTP contains no TPT1 chunk".to_owned())
}

pub fn decode_btp_start_state(bytes: &[u8]) -> Result<Vec<J3dBtpUpdate>, String> {
    Ok(decode_btp(bytes)?.sample(0.0))
}

pub fn decode_btp_end_state(bytes: &[u8]) -> Result<Vec<J3dBtpUpdate>, String> {
    Ok(decode_btp(bytes)?.sample_end())
}

pub fn decode_btk(bytes: &[u8]) -> Result<J3dBtk, String> {
    if bytes.get(0..8) != Some(&b"J3D1btk1"[..]) {
        return Err("BTK magic is not J3D1btk1".to_owned());
    }
    let chunk_count = be32(bytes, 0x0c)? as usize;
    let mut off = 0x20usize;
    for _ in 0..chunk_count {
        let tag = bytes.get(off..off + 4).ok_or("BTK chunk tag out of range")?;
        let size = be32(bytes, off + 4)? as usize;
        let Some(declared_end) = off.checked_add(size) else {
            return Err("BTK chunk size overflow".to_owned());
        };
        // Retail TTK1 commonly declares four bytes beyond the physical chunk.
        // J3D's loader accepts that quirk; mirror it rather than rejecting an
        // otherwise valid authored texture animation.
        let end = if declared_end <= bytes.len() {
            declared_end
        } else if declared_end == bytes.len().saturating_add(4) {
            bytes.len()
        } else {
            return Err(format!("BTK chunk at 0x{off:x} has invalid size 0x{size:x}"));
        };
        if size < 8 {
            return Err(format!("BTK chunk at 0x{off:x} has invalid size 0x{size:x}"));
        }
        if tag == &b"TTK1"[..] {
            return decode_ttk1(&bytes[off..end]);
        }
        off = end;
    }
    Err("BTK contains no TTK1 chunk".to_owned())
}

pub fn decode_btk_start_state(bytes: &[u8]) -> Result<Vec<J3dBtkUpdate>, String> {
    Ok(decode_btk(bytes)?.sample_start())
}

pub fn decode_btk_end_state(bytes: &[u8]) -> Result<Vec<J3dBtkUpdate>, String> {
    Ok(decode_btk(bytes)?.sample_end())
}

fn decode_ttk1(bytes: &[u8]) -> Result<J3dBtk, String> {
    if bytes.get(0..4) != Some(&b"TTK1"[..]) {
        return Err("animation chunk is not TTK1".to_owned());
    }
    let loop_mode = byte(bytes, 0x08)?;
    if loop_mode > 4 {
        return Err(format!("TTK1 loop mode {loop_mode} is outside J3DFrameCtrl 0..=4"));
    }
    let rotation_decimal = byte(bytes, 0x09)?;
    let duration = be16(bytes, 0x0a)? as f32;
    let raw_animation_count = be16(bytes, 0x0c)? as usize;
    if raw_animation_count % 3 != 0 {
        return Err(format!(
            "TTK1 animation table count {raw_animation_count} is not divisible by three"
        ));
    }
    let animation_count = raw_animation_count / 3;
    let scale_count = be16(bytes, 0x0e)? as usize;
    let rotation_count = be16(bytes, 0x10)? as usize;
    let translation_count = be16(bytes, 0x12)? as usize;
    let animation_off = be32(bytes, 0x14)? as usize;
    let _remap_off = be32(bytes, 0x18)? as usize;
    let name_off = be32(bytes, 0x1c)? as usize;
    let tex_mtx_index_off = be32(bytes, 0x20)? as usize;
    let center_off = be32(bytes, 0x24)? as usize;
    let scale_off = be32(bytes, 0x28)? as usize;
    let rotation_off = be32(bytes, 0x2c)? as usize;
    let translation_off = be32(bytes, 0x30)? as usize;
    let is_maya = be32(bytes, 0x5c)? == 1;

    let names = read_string_table(bytes, name_off)?;
    if names.len() < animation_count {
        return Err(format!(
            "TTK1 has {animation_count} animation entries but only {} material name(s)",
            names.len()
        ));
    }
    let scale_data = read_f32_table(bytes, scale_off, scale_count)?;
    let rotation_data = read_i16_table(bytes, rotation_off, rotation_count)?;
    let translation_data = read_f32_table(bytes, translation_off, translation_count)?;
    // J3DAnmTextureSRTKey returns an s16 angle after applying mDecShift.
    let rotation_scale = 2.0f32.powi(rotation_decimal as i32);

    let mut cursor = animation_off;
    let mut entries = Vec::with_capacity(animation_count);
    for index in 0..animation_count {
        let scale_s = read_track(bytes, &mut cursor, &scale_data, 1.0)?;
        let rotation_s = read_track(bytes, &mut cursor, &rotation_data, rotation_scale)?;
        let translation_s = read_track(bytes, &mut cursor, &translation_data, 1.0)?;
        let scale_t = read_track(bytes, &mut cursor, &scale_data, 1.0)?;
        let _rotation_t = read_track(bytes, &mut cursor, &rotation_data, rotation_scale)?;
        let translation_t = read_track(bytes, &mut cursor, &translation_data, 1.0)?;
        let _scale_q = read_track(bytes, &mut cursor, &scale_data, 1.0)?;
        let rotation_q = read_track(bytes, &mut cursor, &rotation_data, rotation_scale)?;
        let _translation_q = read_track(bytes, &mut cursor, &translation_data, 1.0)?;

        // J3DAnmTextureSRTKey::calcTransform uses X scale/translation, Y
        // scale/translation and the third transform table's rotation.
        let tex_mtx_index = byte(bytes, tex_mtx_index_off + index)?;
        if tex_mtx_index >= 8 {
            return Err(format!("TTK1 texture-matrix index {tex_mtx_index} exceeds TEXMTX7"));
        }
        let center_base = center_off
            .checked_add(index.checked_mul(12).ok_or("TTK1 center table overflow")?)
            .ok_or("TTK1 center table overflow")?;
        entries.push(BtkEntry {
            material_name: names[index].clone(),
            tex_mtx_index,
            center: [
                be_f32(bytes, center_base)?,
                be_f32(bytes, center_base + 4)?,
                be_f32(bytes, center_base + 8)?,
            ],
            scale_s,
            scale_t,
            rotation: rotation_q,
            translation_s,
            translation_t,
        });
        // rotation_s is intentionally consumed to preserve the serialized
        // track cursor even though J3D uses the third table's rotation.
        let _ = rotation_s;
    }

    Ok(J3dBtk {
        duration,
        loop_mode,
        is_maya,
        entries,
    })
}

fn decode_tpt1(bytes: &[u8]) -> Result<J3dBtp, String> {
    if bytes.get(0..4) != Some(&b"TPT1"[..]) {
        return Err("animation chunk is not TPT1".to_owned());
    }
    let duration = be16(bytes, 0x0a)? as f32;
    let entry_count = be16(bytes, 0x0c)? as usize;
    let texture_index_count = be16(bytes, 0x0e)? as usize;
    let entry_off = be32(bytes, 0x10)? as usize;
    let texture_index_off = be32(bytes, 0x14)? as usize;
    let _remap_off = be32(bytes, 0x18)? as usize;
    let name_off = be32(bytes, 0x1c)? as usize;

    let names = read_string_table(bytes, name_off)?;
    if names.len() < entry_count {
        return Err(format!(
            "TPT1 has {entry_count} animation entries but only {} material name(s)",
            names.len()
        ));
    }

    let mut texture_indices = Vec::with_capacity(texture_index_count);
    for index in 0..texture_index_count {
        texture_indices.push(be16(bytes, texture_index_off + index * 2)?);
    }

    let mut entries = Vec::with_capacity(entry_count);
    for index in 0..entry_count {
        let at = entry_off
            .checked_add(index.checked_mul(8).ok_or("TPT1 entry overflow")?)
            .ok_or("TPT1 entry overflow")?;
        let count = be16(bytes, at)? as usize;
        let first = be16(bytes, at + 2)? as usize;
        let tex_map_index = byte(bytes, at + 4)?;
        if tex_map_index >= 8 {
            return Err(format!("TPT1 tex-map index {tex_map_index} exceeds TEXMAP7"));
        }
        let end = first.checked_add(count).ok_or("TPT1 pattern range overflow")?;
        if end > texture_indices.len() {
            return Err(format!(
                "TPT1 entry {index} pattern range {first}..{end} exceeds {} texture indices",
                texture_indices.len()
            ));
        }
        entries.push(BtpEntry {
            material_name: names[index].clone(),
            tex_map_index,
            texture_indices: texture_indices[first..end].to_vec(),
        });
    }

    Ok(J3dBtp { duration, entries })
}

fn decode_pak1(bytes: &[u8]) -> Result<J3dBpk, String> {
    if bytes.get(0..4) != Some(&b"PAK1"[..]) {
        return Err("animation chunk is not PAK1".to_owned());
    }
    let loop_mode = byte(bytes, 0x08)?;
    if loop_mode > 4 {
        return Err(format!("PAK1 loop mode {loop_mode} is outside J3DFrameCtrl 0..=4"));
    }

    // J3DAnmColorKey / PAK1 differs from BRK/TRK1: duration starts at 0x0c.
    let duration = be16(bytes, 0x0c)? as f32;
    let entry_count = be16(bytes, 0x0e)? as usize;
    let channel_counts = [
        be16(bytes, 0x10)? as usize,
        be16(bytes, 0x12)? as usize,
        be16(bytes, 0x14)? as usize,
        be16(bytes, 0x16)? as usize,
    ];
    let animation_off = be32(bytes, 0x18)? as usize;
    let _remap_off = be32(bytes, 0x1c)? as usize;
    let name_off = be32(bytes, 0x20)? as usize;
    let channel_offs = [
        be32(bytes, 0x24)? as usize,
        be32(bytes, 0x28)? as usize,
        be32(bytes, 0x2c)? as usize,
        be32(bytes, 0x30)? as usize,
    ];

    let names = read_string_table(bytes, name_off)?;
    if names.len() < entry_count {
        return Err(format!(
            "PAK1 has {entry_count} animation entries but only {} material name(s)",
            names.len()
        ));
    }

    let channel_data = [
        read_i16_table(bytes, channel_offs[0], channel_counts[0])?,
        read_i16_table(bytes, channel_offs[1], channel_counts[1])?,
        read_i16_table(bytes, channel_offs[2], channel_counts[2])?,
        read_i16_table(bytes, channel_offs[3], channel_counts[3])?,
    ];

    let mut cursor = animation_off;
    let mut entries = Vec::with_capacity(entry_count);
    for index in 0..entry_count {
        // Noclip's loader scales PAK1 by 1/255 because its material colors are
        // normalized floats. Our J3D contract deliberately keeps GX colors in
        // the native 0..255 register domain, so retain the serialized values.
        let channels = [
            read_track(bytes, &mut cursor, &channel_data[0], 1.0)?,
            read_track(bytes, &mut cursor, &channel_data[1], 1.0)?,
            read_track(bytes, &mut cursor, &channel_data[2], 1.0)?,
            read_track(bytes, &mut cursor, &channel_data[3], 1.0)?,
        ];
        entries.push(BpkEntry {
            material_name: names[index].clone(),
            channels,
        });
    }

    Ok(J3dBpk {
        duration,
        loop_mode,
        entries,
    })
}

fn decode_trk1(bytes: &[u8]) -> Result<J3dBrk, String> {
    if bytes.get(0..4) != Some(&b"TRK1"[..]) {
        return Err("animation chunk is not TRK1".to_owned());
    }

    let loop_mode = byte(bytes, 0x08)?;
    if loop_mode > 4 {
        return Err(format!("TRK1 loop mode {loop_mode} is outside J3DFrameCtrl 0..=4"));
    }
    let duration = be16(bytes, 0x0a)? as f32;
    let register_count = be16(bytes, 0x0c)? as usize;
    let konst_count = be16(bytes, 0x0e)? as usize;
    let register_counts = [
        be16(bytes, 0x10)? as usize,
        be16(bytes, 0x12)? as usize,
        be16(bytes, 0x14)? as usize,
        be16(bytes, 0x16)? as usize,
    ];
    let konst_counts = [
        be16(bytes, 0x18)? as usize,
        be16(bytes, 0x1a)? as usize,
        be16(bytes, 0x1c)? as usize,
        be16(bytes, 0x1e)? as usize,
    ];

    let register_animation_off = be32(bytes, 0x20)? as usize;
    let konst_animation_off = be32(bytes, 0x24)? as usize;
    let register_name_off = be32(bytes, 0x30)? as usize;
    let konst_name_off = be32(bytes, 0x34)? as usize;
    let register_data_offs = [
        be32(bytes, 0x38)? as usize,
        be32(bytes, 0x3c)? as usize,
        be32(bytes, 0x40)? as usize,
        be32(bytes, 0x44)? as usize,
    ];
    let konst_data_offs = [
        be32(bytes, 0x48)? as usize,
        be32(bytes, 0x4c)? as usize,
        be32(bytes, 0x50)? as usize,
        be32(bytes, 0x54)? as usize,
    ];

    let register_names = read_string_table(bytes, register_name_off)?;
    let konst_names = read_string_table(bytes, konst_name_off)?;
    if register_names.len() < register_count {
        return Err(format!(
            "TRK1 has {register_count} register animation(s) but only {} material name(s)",
            register_names.len()
        ));
    }
    if konst_names.len() < konst_count {
        return Err(format!(
            "TRK1 has {konst_count} konst animation(s) but only {} material name(s)",
            konst_names.len()
        ));
    }

    let register_data = [
        read_i16_table(bytes, register_data_offs[0], register_counts[0])?,
        read_i16_table(bytes, register_data_offs[1], register_counts[1])?,
        read_i16_table(bytes, register_data_offs[2], register_counts[2])?,
        read_i16_table(bytes, register_data_offs[3], register_counts[3])?,
    ];
    let konst_data = [
        read_i16_table(bytes, konst_data_offs[0], konst_counts[0])?,
        read_i16_table(bytes, konst_data_offs[1], konst_counts[1])?,
        read_i16_table(bytes, konst_data_offs[2], konst_counts[2])?,
        read_i16_table(bytes, konst_data_offs[3], konst_counts[3])?,
    ];

    let mut entries = Vec::with_capacity(register_count + konst_count);

    let mut cursor = register_animation_off;
    for index in 0..register_count {
        let channels = [
            read_track(bytes, &mut cursor, &register_data[0], 1.0)?,
            read_track(bytes, &mut cursor, &register_data[1], 1.0)?,
            read_track(bytes, &mut cursor, &register_data[2], 1.0)?,
            read_track(bytes, &mut cursor, &register_data[3], 1.0)?,
        ];
        let color_id = byte(bytes, cursor)?;
        cursor = cursor.checked_add(4).ok_or("TRK1 register entry overflow")?;
        if color_id >= 4 {
            return Err(format!("TRK1 register color ID {color_id} exceeds C0..C3"));
        }
        entries.push(BrkEntry {
            material_name: register_names[index].clone(),
            target: J3dBrkTarget::Register(color_id),
            channels,
        });
    }

    cursor = konst_animation_off;
    for index in 0..konst_count {
        let channels = [
            read_track(bytes, &mut cursor, &konst_data[0], 1.0)?,
            read_track(bytes, &mut cursor, &konst_data[1], 1.0)?,
            read_track(bytes, &mut cursor, &konst_data[2], 1.0)?,
            read_track(bytes, &mut cursor, &konst_data[3], 1.0)?,
        ];
        let color_id = byte(bytes, cursor)?;
        cursor = cursor.checked_add(4).ok_or("TRK1 konst entry overflow")?;
        if color_id >= 4 {
            return Err(format!("TRK1 konst color ID {color_id} exceeds K0..K3"));
        }
        entries.push(BrkEntry {
            material_name: konst_names[index].clone(),
            target: J3dBrkTarget::Konst(color_id),
            channels,
        });
    }

    Ok(J3dBrk {
        duration,
        loop_mode,
        entries,
    })
}

fn decode_ank1(bytes: &[u8]) -> Result<J3dBck, String> {
    if bytes.get(0..4) != Some(&b"ANK1"[..]) {
        return Err("animation chunk is not ANK1".to_owned());
    }

    let loop_mode = byte(bytes, 0x08)?;
    if loop_mode > 4 {
        return Err(format!("ANK1 loop mode {loop_mode} is outside J3DFrameCtrl 0..=4"));
    }
    let rotation_decimal = byte(bytes, 0x09)?;
    let duration = be16(bytes, 0x0a)? as f32;
    let joint_count = be16(bytes, 0x0c)? as usize;
    let scale_count = be16(bytes, 0x0e)? as usize;
    let rotation_count = be16(bytes, 0x10)? as usize;
    let translation_count = be16(bytes, 0x12)? as usize;
    let animation_off = be32(bytes, 0x14)? as usize;
    let scale_off = be32(bytes, 0x18)? as usize;
    let rotation_off = be32(bytes, 0x1c)? as usize;
    let translation_off = be32(bytes, 0x20)? as usize;

    let scale_data = read_f32_table(bytes, scale_off, scale_count)?;
    let rotation_data = read_i16_table(bytes, rotation_off, rotation_count)?;
    let translation_data = read_f32_table(bytes, translation_off, translation_count)?;
    let rotation_scale = 2.0f32.powi(rotation_decimal as i32) / 32767.0 * core::f32::consts::PI;

    let descriptor_bytes = joint_count
        .checked_mul(9)
        .and_then(|v| v.checked_mul(6))
        .ok_or("ANK1 descriptor size overflow")?;
    let descriptor_end = animation_off.checked_add(descriptor_bytes).ok_or("ANK1 descriptor overflow")?;
    if descriptor_end > bytes.len() {
        return Err("ANK1 joint animation table is truncated".to_owned());
    }

    let mut cursor = animation_off;
    let mut joints = Vec::with_capacity(joint_count);
    for _ in 0..joint_count {
        let mut scale = Vec::with_capacity(3);
        let mut rotation = Vec::with_capacity(3);
        let mut translation = Vec::with_capacity(3);
        for _axis in 0..3 {
            scale.push(read_track(bytes, &mut cursor, &scale_data, 1.0)?);
            rotation.push(read_track(bytes, &mut cursor, &rotation_data, rotation_scale)?);
            translation.push(read_track(bytes, &mut cursor, &translation_data, 1.0)?);
        }
        joints.push(JointAnimation {
            scale: scale.try_into().map_err(|_| "ANK1 scale track count mismatch".to_owned())?,
            rotation: rotation.try_into().map_err(|_| "ANK1 rotation track count mismatch".to_owned())?,
            translation: translation.try_into().map_err(|_| "ANK1 translation track count mismatch".to_owned())?,
        });
    }

    Ok(J3dBck {
        duration: if duration == 0.0 { 1.0 } else { duration },
        loop_mode,
        sampling: J3dJointSamplingMode::HermiteKey,
        joints,
    })
}

trait TrackValue: Copy {
    fn as_f32(self) -> f32;
}

impl TrackValue for f32 {
    fn as_f32(self) -> f32 { self }
}

impl TrackValue for i16 {
    fn as_f32(self) -> f32 { self as f32 }
}

fn read_track<T: TrackValue>(
    bytes: &[u8],
    cursor: &mut usize,
    data: &[T],
    value_scale: f32,
) -> Result<Track, String> {
    let count = be16(bytes, *cursor)? as usize;
    let index = be16(bytes, *cursor + 2)? as usize;
    let tangent = be16(bytes, *cursor + 4)?;
    *cursor += 6;

    if count == 0 {
        return Err("ANK1 track has zero keys".to_owned());
    }
    if count == 1 {
        let value = (*data.get(index).ok_or("ANK1 constant track index out of range")?).as_f32() * value_scale;
        return Ok(Track { binary_searchable: true,
            frames: vec![Keyframe { time: 0.0, value, tangent_in: 0.0, tangent_out: 0.0 }],
        });
    }

    let stride = match tangent {
        0 => 3usize,
        1 => 4usize,
        other => return Err(format!("ANK1 track has unknown tangent type {other}")),
    };
    let needed = index
        .checked_add(count.checked_mul(stride).ok_or("ANK1 track size overflow")?)
        .ok_or("ANK1 track range overflow")?;
    if needed > data.len() {
        return Err(format!(
            "ANK1 track range {index}..{needed} exceeds data table length {}",
            data.len()
        ));
    }

    let mut frames = Vec::with_capacity(count);
    for key in 0..count {
        let base = index + key * stride;
        let time = data[base].as_f32();
        let value = data[base + 1].as_f32() * value_scale;
        let tangent_in = data[base + 2].as_f32() * value_scale;
        let tangent_out = if stride == 4 {
            data[base + 3].as_f32() * value_scale
        } else {
            tangent_in
        };
        frames.push(Keyframe { time, value, tangent_in, tangent_out });
    }
    if frames.windows(2).any(|pair| pair[0].time > pair[1].time) {
        return Err("ANK1 keyframe times are not monotonic".to_owned());
    }
    Ok(Track { binary_searchable: frames.iter().all(|key| key.time.is_finite()), frames })
}

fn read_full_track<T: TrackValue>(
    bytes: &[u8],
    cursor: &mut usize,
    data: &[T],
    value_scale: f32,
) -> Result<Track, String> {
    let count = be16(bytes, *cursor)? as usize;
    let index = be16(bytes, *cursor + 2)? as usize;
    *cursor += 4;
    if count == 0 {
        return Err("ANF1 full track has zero frames".to_owned());
    }
    let end = index
        .checked_add(count)
        .ok_or("ANF1 full track range overflow")?;
    if end > data.len() {
        return Err(format!(
            "ANF1 full track range {index}..{end} exceeds data table length {}",
            data.len()
        ));
    }
    Ok(Track { binary_searchable: true,
        frames: (0..count)
            .map(|frame| Keyframe {
                time: frame as f32,
                value: data[index + frame].as_f32() * value_scale,
                tangent_in: 0.0,
                tangent_out: 0.0,
            })
            .collect(),
    })
}

fn sample_full_track(track: &Track, frame: f32) -> f32 {
    let frames = &track.frames;
    if frames.is_empty() {
        return 0.0;
    }
    if !frame.is_finite() || frame < 0.0 {
        return frames[0].value;
    }
    let index = ((frame + 0.5).floor() as usize).min(frames.len() - 1);
    frames[index].value
}

fn sample_track(track: &Track, frame: f32) -> f32 {
    let frames = &track.frames;
    if frames.len() == 1 || frame <= frames[0].time {
        return frames[0].value;
    }
    // Keep the hot early-frame path identical to the source linear sampler.
    // Only larger finite curves *past* the 64th timestamp use a logarithmic
    // seek; unconditional binary search regressed early-frame workloads.
    if frames.len() >= 96 && track.binary_searchable && frame > frames[63].time {
        let next = frames.partition_point(|key| !(frame < key.time));
        if next == frames.len() {
            return frames.last().unwrap().value;
        }
        return hermite(frames[next - 1], frames[next], frame);
    }
    let Some(next) = frames.iter().position(|key| frame < key.time) else {
        return frames.last().unwrap().value;
    };
    hermite(frames[next - 1], frames[next], frame)
}

fn hermite(a: Keyframe, b: Keyframe, frame: f32) -> f32 {
    let length = b.time - a.time;
    if length <= 0.0 {
        return b.value;
    }
    let t = ((frame - a.time) / length).clamp(0.0, 1.0);
    let t2 = t * t;
    let t3 = t2 * t;
    let h00 = 2.0 * t3 - 3.0 * t2 + 1.0;
    let h10 = t3 - 2.0 * t2 + t;
    let h01 = -2.0 * t3 + 3.0 * t2;
    let h11 = t3 - t2;
    h00 * a.value
        + h10 * (a.tangent_out * length)
        + h01 * b.value
        + h11 * (b.tangent_in * length)
}

fn read_string_table(bytes: &[u8], off: usize) -> Result<Vec<String>, String> {
    let count = be16(bytes, off)? as usize;
    let mut out = Vec::with_capacity(count);
    for index in 0..count {
        let rel = be16(bytes, off + 4 + index * 4 + 2)? as usize;
        out.push(read_c_string(bytes, off.checked_add(rel).ok_or("J3D string offset overflow")?)?);
    }
    Ok(out)
}

fn read_c_string(bytes: &[u8], off: usize) -> Result<String, String> {
    let tail = bytes.get(off..).ok_or_else(|| format!("J3D string 0x{off:x} out of range"))?;
    let len = tail.iter().position(|&byte| byte == 0).ok_or("J3D string is not NUL terminated")?;
    Ok(String::from_utf8_lossy(&tail[..len]).into_owned())
}

fn read_f32_table(bytes: &[u8], off: usize, count: usize) -> Result<Vec<f32>, String> {
    (0..count).map(|i| be_f32(bytes, off + i * 4)).collect()
}

fn read_i16_table(bytes: &[u8], off: usize, count: usize) -> Result<Vec<i16>, String> {
    (0..count).map(|i| be_i16(bytes, off + i * 2)).collect()
}

fn byte(bytes: &[u8], off: usize) -> Result<u8, String> {
    bytes.get(off).copied().ok_or_else(|| format!("read u8 at 0x{off:x} out of range"))
}

fn be16(bytes: &[u8], off: usize) -> Result<u16, String> {
    let data = bytes.get(off..off + 2).ok_or_else(|| format!("read u16 at 0x{off:x} out of range"))?;
    Ok(u16::from_be_bytes([data[0], data[1]]))
}

fn be_i16(bytes: &[u8], off: usize) -> Result<i16, String> {
    let data = bytes.get(off..off + 2).ok_or_else(|| format!("read i16 at 0x{off:x} out of range"))?;
    Ok(i16::from_be_bytes([data[0], data[1]]))
}

fn be32(bytes: &[u8], off: usize) -> Result<u32, String> {
    let data = bytes.get(off..off + 4).ok_or_else(|| format!("read u32 at 0x{off:x} out of range"))?;
    Ok(u32::from_be_bytes([data[0], data[1], data[2], data[3]]))
}

fn be_f32(bytes: &[u8], off: usize) -> Result<f32, String> {
    Ok(f32::from_bits(be32(bytes, off)?))
}

#[cfg(test)]
mod tests {
    use super::*;

    // Source fixture writers shared by the pre-existing animation tests.
    fn put_u16(data: &mut [u8], offset: usize, value: u16) {
        data[offset..offset + 2].copy_from_slice(&value.to_be_bytes());
    }
    fn put_i16(data: &mut [u8], offset: usize, value: i16) {
        data[offset..offset + 2].copy_from_slice(&value.to_be_bytes());
    }
    fn put_u32(data: &mut [u8], offset: usize, value: u32) {
        data[offset..offset + 4].copy_from_slice(&value.to_be_bytes());
    }
    fn put_f32(data: &mut [u8], offset: usize, value: f32) {
        put_u32(data, offset, value.to_bits());
    }

    #[test]
    fn pak1_decodes_primary_material_color_track() {
        // Minimal one-entry PAK1 chunk wrapped in a BPK container.
        // Four constant channels live in four independent s16 tables.
        let chunk_size = 0x60u32;
        let mut bytes = vec![0u8; 0x20 + chunk_size as usize];
        bytes[0..8].copy_from_slice(b"J3D1bpk1");
        bytes[0x0c..0x10].copy_from_slice(&1u32.to_be_bytes());
        let off = 0x20usize;
        bytes[off..off + 4].copy_from_slice(b"PAK1");
        bytes[off + 4..off + 8].copy_from_slice(&chunk_size.to_be_bytes());
        bytes[off + 0x08] = 2; // repeat
        bytes[off + 0x0c..off + 0x0e].copy_from_slice(&60u16.to_be_bytes());
        bytes[off + 0x0e..off + 0x10].copy_from_slice(&1u16.to_be_bytes());
        for p in [0x10usize, 0x12, 0x14, 0x16] {
            bytes[off + p..off + p + 2].copy_from_slice(&1u16.to_be_bytes());
        }
        bytes[off + 0x18..off + 0x1c].copy_from_slice(&0x34u32.to_be_bytes());
        bytes[off + 0x1c..off + 0x20].copy_from_slice(&0x4cu32.to_be_bytes());
        bytes[off + 0x20..off + 0x24].copy_from_slice(&0x4cu32.to_be_bytes());
        for (p, v) in [
            (0x24usize, 0x58u32),
            (0x28, 0x5a),
            (0x2c, 0x5c),
            (0x30, 0x5e),
        ] {
            bytes[off + p..off + p + 4].copy_from_slice(&v.to_be_bytes());
        }
        // Four descriptors: count=1,index=0,tangent=0.
        for d in 0..4usize {
            let p = off + 0x34 + d * 6;
            bytes[p..p + 2].copy_from_slice(&1u16.to_be_bytes());
        }
        // J3D string table: count=1, hash=0, string offset=8, then "Mat\0".
        bytes[off + 0x4c..off + 0x4e].copy_from_slice(&1u16.to_be_bytes());
        bytes[off + 0x52..off + 0x54].copy_from_slice(&8u16.to_be_bytes());
        bytes[off + 0x54..off + 0x58].copy_from_slice(b"Mat\0");
        bytes[off + 0x58..off + 0x5a].copy_from_slice(&255i16.to_be_bytes());
        bytes[off + 0x5a..off + 0x5c].copy_from_slice(&128i16.to_be_bytes());
        bytes[off + 0x5c..off + 0x5e].copy_from_slice(&64i16.to_be_bytes());
        bytes[off + 0x5e..off + 0x60].copy_from_slice(&32i16.to_be_bytes());

        let bpk = decode_bpk(&bytes).unwrap();
        assert_eq!(bpk.duration, 60.0);
        assert_eq!(bpk.loop_mode, 2);
        let sample = bpk.sample_start();
        assert_eq!(sample.len(), 1);
        assert_eq!(sample[0].material_name, "Mat");
        assert_eq!(sample[0].values, [255.0, 128.0, 64.0, 32.0]);
        let runtime = bpk.runtime_entries();
        assert_eq!(runtime[0].1.loop_mode, 2);
        assert_eq!(runtime[0].1.channels[0].frames[0].value, 255.0);
    }

    #[test]
    fn bva_vaf1_decodes_shape_visibility_tracks() {
        let mut bytes = vec![0xffu8; 0x50];
        let file_len = bytes.len() as u32;
        bytes[0..8].copy_from_slice(b"J3D1bva1");
        bytes[0x08..0x0c].copy_from_slice(&file_len.to_be_bytes());
        bytes[0x0c..0x10].copy_from_slice(&1u32.to_be_bytes());
        bytes[0x20..0x24].copy_from_slice(b"VAF1");
        bytes[0x24..0x28].copy_from_slice(&0x30u32.to_be_bytes());
        bytes[0x28] = 2;
        bytes[0x29] = 0xff;
        put_u16(&mut bytes, 0x2a, 3);
        put_u16(&mut bytes, 0x2c, 2);
        put_u16(&mut bytes, 0x2e, 5);
        bytes[0x30..0x34].copy_from_slice(&0x18u32.to_be_bytes());
        bytes[0x34..0x38].copy_from_slice(&0x20u32.to_be_bytes());
        put_u16(&mut bytes, 0x38, 3);
        put_u16(&mut bytes, 0x3a, 0);
        put_u16(&mut bytes, 0x3c, 2);
        put_u16(&mut bytes, 0x3e, 3);
        bytes[0x40..0x45].copy_from_slice(&[1, 0, 1, 0, 1]);

        let bva = decode_bva(&bytes).unwrap();
        assert_eq!(bva.loop_mode, 2);
        assert_eq!(bva.duration, 3.0);
        assert_eq!(bva.track_count(), 2);
        assert_eq!(bva.sample(0.0), vec![true, false]);
        assert_eq!(bva.sample(1.0), vec![false, true]);
        assert_eq!(bva.sample(2.0), vec![true, true]);
        assert_eq!(bva.sample(99.0), vec![true, true]);
    }

    #[test]
    fn decodes_minimal_one_joint_bck_terminal_pose() {
        const CHUNK: usize = 0x20;
        const ANIM: usize = 0x24;
        const SCALE: usize = 0x5c;
        const ROT: usize = 0x68;
        const TRANS: usize = 0x70;
        const CHUNK_SIZE: usize = 0x7c;
        let mut bytes = vec![0u8; CHUNK + CHUNK_SIZE];

        bytes[0..8].copy_from_slice(b"J3D1bck1");
        let file_size = bytes.len() as u32;
        put_u32(&mut bytes, 0x08, file_size);
        put_u32(&mut bytes, 0x0c, 1);

        bytes[CHUNK..CHUNK + 4].copy_from_slice(b"ANK1");
        put_u32(&mut bytes, CHUNK + 0x04, CHUNK_SIZE as u32);
        bytes[CHUNK + 0x08] = 0;
        bytes[CHUNK + 0x09] = 0;
        put_u16(&mut bytes, CHUNK + 0x0a, 10);
        put_u16(&mut bytes, CHUNK + 0x0c, 1);
        put_u16(&mut bytes, CHUNK + 0x0e, 3);
        put_u16(&mut bytes, CHUNK + 0x10, 3);
        put_u16(&mut bytes, CHUNK + 0x12, 3);
        put_u32(&mut bytes, CHUNK + 0x14, ANIM as u32);
        put_u32(&mut bytes, CHUNK + 0x18, SCALE as u32);
        put_u32(&mut bytes, CHUNK + 0x1c, ROT as u32);
        put_u32(&mut bytes, CHUNK + 0x20, TRANS as u32);

        let mut descriptor = CHUNK + ANIM;
        for axis in 0..3u16 {
            for _kind in 0..3 {
                put_u16(&mut bytes, descriptor, 1);
                put_u16(&mut bytes, descriptor + 2, axis);
                put_u16(&mut bytes, descriptor + 4, 0);
                descriptor += 6;
            }
        }

        for (axis, value) in [1.0f32, 2.0, 3.0].into_iter().enumerate() {
            put_f32(&mut bytes, CHUNK + SCALE + axis * 4, value);
        }
        for axis in 0..3 {
            put_i16(&mut bytes, CHUNK + ROT + axis * 2, 0);
        }
        for (axis, value) in [4.0f32, 5.0, 6.0].into_iter().enumerate() {
            put_f32(&mut bytes, CHUNK + TRANS + axis * 4, value);
        }

        let bck = decode_bck(&bytes).unwrap();
        assert_eq!(bck.duration, 10.0);
        let pose = bck.sample_end();
        assert_eq!(pose.len(), 1);
        assert_eq!(pose[0].scale, [1.0, 2.0, 3.0]);
        assert_eq!(pose[0].rotation_radians, [0.0; 3]);
        assert_eq!(pose[0].translation, [4.0, 5.0, 6.0]);
    }

    #[test]
    fn btk_start_state_preserves_texture_srt_target() {
        let btk = J3dBtk {
            duration: 90.0,
            loop_mode: 2,
            is_maya: true,
            entries: vec![BtkEntry {
                material_name: "Sky".to_owned(),
                tex_mtx_index: 2,
                center: [0.5, 0.5, 1.0],
                scale_s: Track { binary_searchable: true, frames: vec![Keyframe { time: 0.0, value: 2.0, tangent_in: 0.0, tangent_out: 0.0 }] },
                scale_t: Track { binary_searchable: true, frames: vec![Keyframe { time: 0.0, value: 3.0, tangent_in: 0.0, tangent_out: 0.0 }] },
                rotation: Track { binary_searchable: true, frames: vec![Keyframe { time: 0.0, value: 16384.0, tangent_in: 0.0, tangent_out: 0.0 }] },
                translation_s: Track { binary_searchable: true, frames: vec![Keyframe { time: 0.0, value: 0.25, tangent_in: 0.0, tangent_out: 0.0 }] },
                translation_t: Track { binary_searchable: true, frames: vec![Keyframe { time: 0.0, value: -0.5, tangent_in: 0.0, tangent_out: 0.0 }] },
            }],
        };
        let runtime = btk.runtime_entries();
        assert_eq!(runtime.len(), 1);
        assert_eq!(runtime[0].0, "Sky");
        assert_eq!(runtime[0].1, 2);
        assert_eq!(runtime[0].2.loop_mode, 2);
        assert_eq!(runtime[0].2.duration, 90.0);
        assert_eq!(runtime[0].2.scale_s.frames[0].value, 2.0);

        assert_eq!(
            btk.sample_start(),
            vec![J3dBtkUpdate {
                material_name: "Sky".to_owned(),
                tex_mtx_index: 2,
                center: [0.5, 0.5, 1.0],
                scale: [2.0, 3.0],
                rotation_s16: 16384,
                translation: [0.25, -0.5],
                is_maya: true,
            }]
        );
    }

    #[test]
    fn btp_terminal_state_uses_last_pattern_texture() {
        let btp = J3dBtp {
            duration: 30.0,
            entries: vec![BtpEntry {
                material_name: "Ground".to_owned(),
                tex_map_index: 2,
                texture_indices: vec![4, 7, 9],
            }],
        };
        assert_eq!(
            btp.sample_end(),
            vec![J3dBtpUpdate {
                material_name: "Ground".to_owned(),
                tex_map_index: 2,
                texture_index: 9,
            }]
        );
        assert_eq!(btp.sample(1.9)[0].texture_index, 7);
        assert_eq!(btp.sample(-1.0)[0].texture_index, 4);
    }

    #[test]
    fn brk_terminal_state_preserves_register_and_konst_targets() {
        let register = BrkEntry {
            material_name: "MatA".to_owned(),
            target: J3dBrkTarget::Register(2),
            channels: std::array::from_fn(|channel| Track { binary_searchable: true,
                frames: vec![Keyframe {
                    time: 0.0,
                    value: 10.0 + channel as f32,
                    tangent_in: 0.0,
                    tangent_out: 0.0,
                }],
            }),
        };
        let konst = BrkEntry {
            material_name: "MatB".to_owned(),
            target: J3dBrkTarget::Konst(1),
            channels: std::array::from_fn(|channel| Track { binary_searchable: true,
                frames: vec![Keyframe {
                    time: 0.0,
                    value: 20.0 + channel as f32,
                    tangent_in: 0.0,
                    tangent_out: 0.0,
                }],
            }),
        };
        let brk = J3dBrk {
            duration: 30.0,
            loop_mode: 0,
            entries: vec![register, konst],
        };
        let updates = brk.sample_end();
        assert_eq!(updates[0].material_name, "MatA");
        assert_eq!(updates[0].target, J3dBrkTarget::Register(2));
        assert_eq!(updates[0].values, [10.0, 11.0, 12.0, 13.0]);
        assert_eq!(updates[1].target, J3dBrkTarget::Konst(1));
        assert_eq!(updates[1].values, [20.0, 21.0, 22.0, 23.0]);
    }

    #[test]
    fn hermite_clamps_to_last_key_at_animation_end() {
        let track = Track { binary_searchable: true,
            frames: vec![
                Keyframe { time: 0.0, value: 2.0, tangent_in: 0.0, tangent_out: 1.0 },
                Keyframe { time: 10.0, value: 7.0, tangent_in: 0.0, tangent_out: 0.0 },
            ],
        };
        assert_eq!(sample_track(&track, 10.0), 7.0);
        assert_eq!(sample_track(&track, 15.0), 7.0);
    }


    #[test]
    fn long_hermite_curve_binary_search_is_bitwise_identical_to_original() {
        fn original(track: &Track, frame: f32) -> f32 {
            let frames = &track.frames;
            if frames.len() == 1 || frame <= frames[0].time {
                return frames[0].value;
            }
            let Some(next) = frames.iter().position(|key| frame < key.time) else {
                return frames.last().unwrap().value;
            };
            hermite(frames[next - 1], frames[next], frame)
        }
        for count in [1usize, 2, 15, 16, 17, 32, 128, 256] {
            for duplicates in [false, true] {
                let frames = (0..count).map(|i| Keyframe {
                    time: if duplicates { (i / 3) as f32 } else { i as f32 },
                    value: i as f32 * 0.7 - 20.0,
                    tangent_in: i as f32 * 0.1,
                    tangent_out: -(i as f32) * 0.2,
                }).collect::<Vec<_>>();
                let track = Track { binary_searchable: true, frames };
                for step in -100..(count as i32 * 10 + 100) {
                    let frame = step as f32 / 10.0;
                    assert_eq!(sample_track(&track, frame).to_bits(), original(&track, frame).to_bits(),
                        "count={count} duplicates={duplicates} frame={frame}");
                }
                for frame in [f32::NEG_INFINITY, f32::INFINITY, f32::NAN] {
                    assert_eq!(sample_track(&track, frame).to_bits(), original(&track, frame).to_bits(),
                        "special frame count={count} duplicates={duplicates} {frame:?}");
                }
            }
        }
        let frames = (0..64).map(|i| Keyframe {
            time: if i == 15 { f32::NAN } else { i as f32 },
            value: i as f32,
            tangent_in: 0.0,
            tangent_out: 0.0,
        }).collect::<Vec<_>>();
        let malformed = Track { binary_searchable: false, frames };
        for frame in [-1.0, 0.0, 15.0, 32.0, 63.0, f32::NAN] {
            assert_eq!(sample_track(&malformed, frame).to_bits(), original(&malformed, frame).to_bits());
        }
    }

    #[test]
    fn hermite_midpoint_respects_tangents() {
        let a = Keyframe { time: 0.0, value: 0.0, tangent_in: 0.0, tangent_out: 1.0 };
        let b = Keyframe { time: 2.0, value: 2.0, tangent_in: 1.0, tangent_out: 0.0 };
        assert!((hermite(a, b, 1.0) - 1.0).abs() < 1.0e-6);
    }
}


#[cfg(test)]
mod animation_source_tests {
    use super::*;

    #[test]
    fn ank1_retains_source_loop_mode() {
        // Minimal zero-joint ANK1 chunk. The table offsets all point at the end
        // because their element counts are zero.
        let mut bytes = vec![0u8; 0x24];
        bytes[0..4].copy_from_slice(b"ANK1");
        bytes[0x08] = 2;
        bytes[0x09] = 0;
        bytes[0x0a..0x0c].copy_from_slice(&10u16.to_be_bytes());
        for off in [0x14usize, 0x18, 0x1c, 0x20] {
            bytes[off..off + 4].copy_from_slice(&(0x24u32).to_be_bytes());
        }

        let decoded = decode_ank1(&bytes).expect("minimal ANK1 should decode");
        assert_eq!(decoded.loop_mode, 2);
        assert_eq!(decoded.duration, 10.0);
        assert!(decoded.joints.is_empty());
    }

    #[test]
    fn ank1_rejects_invalid_loop_mode_before_payload_decode() {
        let mut bytes = vec![0u8; 0x24];
        bytes[0..4].copy_from_slice(b"ANK1");
        bytes[0x08] = 5;
        let error = decode_ank1(&bytes).expect_err("loop mode 5 is outside J3DFrameCtrl");
        assert!(error.contains("ANK1 loop mode 5"));
    }
}

pub struct BenchmarkTrack(Track);
impl BenchmarkTrack {
    pub fn new(n: usize, duplicates: bool) -> Self {
        let frames = (0..n).map(|i| Keyframe {
            time: if duplicates {(i / 3) as f32} else {i as f32},
            value: i as f32 * 0.173 + 0.77,
            tangent_in: i as f32 * 0.031,
            tangent_out: i as f32 * -0.061,
        }).collect::<Vec<_>>();
        Self(Track {binary_searchable: true, frames})
    }
    #[inline(never)]
    pub fn sample(&self,frame:f32)->f32 {sample_track(&self.0,frame)}
}
