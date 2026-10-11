//! Fortnite 5.41 / UE4.21 cooked UTexture2D external first-mip decoding.
//!
//! Retail landscape textures are 128x128 PF_B8G8R8A8. Their highest-resolution
//! mip is stored in the package's original .ubulk, not the smaller inline mips
//! at the end of .uexp. A signed serialized FPak bulk offset is relative to
//! the end of the logically concatenated .umap + .uexp minus four bytes.
//! Bounds, pixel format, byte count, mip dimensions and source object class
//! must be authenticated before any samples become terrain geometry.
use crate::{properties, uobject::{PackageCatalog, PackageExport}};
const MAX_MIP_BYTES: usize = 64*1024*1024;

#[derive(Debug, Clone)]
pub struct SourceTextureMip<'a> {
    pub width: u32,
    pub height: u32,
    pub format: &'static str,
    pub source_bulk_offset: usize,
    pub source_bulk_flags: u32,
    /// Exactly original source B,G,R,A bytes, without transcoding or scaling.
    pub bgra8: &'a [u8],
}
fn u32_at(bytes: &[u8], start: usize) -> Result<u32,String> {
    Ok(u32::from_le_bytes(bytes.get(start..start+4)
        .ok_or("truncated Fortnite UTexture2D mip")?.try_into().unwrap()))
}
fn i64_at(bytes: &[u8], start: usize) -> Result<i64,String> {
    Ok(i64::from_le_bytes(bytes.get(start..start+8)
        .ok_or("truncated Fortnite FByteBulkData signed offset")?.try_into().unwrap()))
}

/// Recover the source top mip. No guessed low-res replacements and no channel
/// reinterpretation: the actual raw pixels remain BGRA8.
pub fn first_mip_bgra8<'a>(
    catalog: &PackageCatalog,
    package_file: &[u8],
    companion_uexp: &[u8],
    companion_ubulk: &'a [u8],
    export: &PackageExport,
) -> Result<SourceTextureMip<'a>, String> {
    if catalog.export_class_name(export) != Some("Texture2D") {
        return Err("the source heightmap FPackageIndex does not point to Texture2D".into());
    }
    let serialized = catalog.export_data(package_file, companion_uexp, export)?;
    let props = properties::scan(catalog, serialized)?;
    let cooked = serialized.get(props.bytes_consumed..)
        .ok_or("source UTexture2D has no cooked platform data")?;

    // Source-confirmed Fortnite 5.41 UE4 cooked FTexturePlatformData layout.
    // A different source build must fail instead of silently reusing offsets.
    let width=u32_at(cooked,28)?;
    let height=u32_at(cooked,32)?;
    let depth=u32_at(cooked,36)?;
    let name_len=u32_at(cooked,40)? as usize;
    if name_len != 12 ||
        cooked.get(44..56) != Some(b"PF_B8G8R8A8\0".as_slice()) {
        return Err("source top mip is not PF_B8G8R8A8".into());
    }
    let flags=u32_at(cooked,68)?;
    let count=u32_at(cooked,72)? as usize;
    let stored=u32_at(cooked,76)? as usize;
    let signed_offset=i64_at(cooked,80)?;
    let mip_width=u32_at(cooked,88)?;
    let mip_height=u32_at(cooked,92)?;
    let mip_depth=u32_at(cooked,96)?;
    if width == 0 || height == 0 || width > 8192 || height > 8192 ||
        width != mip_width || height != mip_height ||
        depth != 1 || mip_depth != 1 {
        return Err("source texture first-mip dimensions differ from platform header".into());
    }
    let expected=(width as usize).checked_mul(height as usize)
        .and_then(|v|v.checked_mul(4)).ok_or("source mip dimensions overflow")?;
    if expected>MAX_MIP_BYTES || count!=expected || stored!=expected {
        return Err("source PF_B8G8R8A8 top mip byte count inconsistent".into());
    }
    // Fortnite 5.41 uses (bPayloadAtEndOfFile | bPayloadInSeperateFile
    // | bNoOffsetFixUp etc), observed as 0x0501. This parser is intentionally
    // version-pinned, not a general-purpose Unreal bulk-data decoder.
    if flags != 0x0501 {
        return Err(format!("unsupported source texture bulk flag pattern 0x{flags:x}"));
    }
    let package_total=package_file.len().checked_add(companion_uexp.len())
        .ok_or("UE4 source package size overflow")?;
    let bulk_offset=i64::try_from(package_total).map_err(|_| "source package too large")?
        .checked_sub(4).and_then(|x|x.checked_add(signed_offset))
        .ok_or("source relative .ubulk offset overflow")?;
    let start=usize::try_from(bulk_offset).map_err(|_| "source .ubulk offset is negative")?;
    let end=start.checked_add(expected).ok_or("source .ubulk range overflow")?;
    let bgra8=companion_ubulk.get(start..end)
        .ok_or("source first-mip bytes escape original .ubulk file")?;
    Ok(SourceTextureMip {
        width,height,format:"PF_B8G8R8A8",source_bulk_offset:start,
        source_bulk_flags:flags,bgra8,
    })
}

impl SourceTextureMip<'_> {
    /// UE4 landscape height is encoded in R(high) and G(low); B/A are the
    /// encoded tangent/normal channels, NOT extra height bits.
    pub fn height_u16(&self,x:u32,y:u32)->Result<u16,String>{
        if x>=self.width || y>=self.height {return Err("height sample outside texture".into());}
        let i=(y as usize*self.width as usize + x as usize)*4;
        let g=self.bgra8[i+1] as u16;
        let r=self.bgra8[i+2] as u16;
        Ok((r<<8)|g)
    }
    /// Original Unreal local landscape Z before Landscape actor scale:
    /// (stored 16-bit height minus 32768) / 128.
    pub fn height_local(&self,x:u32,y:u32)->Result<f32,String>{
        Ok((self.height_u16(x,y)? as f32-32768.0)/128.0)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn height_channels_use_bgra_red_and_green_not_blue_or_alpha() {
        let px=[0xFF,0x30,0x80,0x77];
        let mip=SourceTextureMip {
            width:1,height:1,format:"PF_B8G8R8A8",
            source_bulk_offset:0,source_bulk_flags:0x0501,bgra8:&px,
        };
        assert_eq!(mip.height_u16(0,0).unwrap(),0x8030);
        assert_eq!(mip.height_local(0,0).unwrap(),48.0/128.0);
        assert!(mip.height_u16(1,0).is_err());
    }
}


/// Source-authenticated UE4 BC1/2/3/4/5 first (highest-resolution) mip.
/// Original block data is left unchanged, and may be consumed by the generic
/// NeutralScene BC texture path once source material sampler semantics close.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum OriginalBcFormat {
    Bc1,
    Bc2,
    Bc3,
    Bc4,
    Bc5,
}
impl OriginalBcFormat {
    fn from_source_pixel_format(bytes:&[u8])->Result<Self,String>{
        match bytes {
            b"PF_DXT1\0"=>Ok(Self::Bc1),
            b"PF_DXT3\0"=>Ok(Self::Bc2),
            b"PF_DXT5\0"=>Ok(Self::Bc3),
            b"PF_BC4\0"=>Ok(Self::Bc4),
            b"PF_BC5\0"=>Ok(Self::Bc5),
            _=>Err("original texture is not one of the supported UE4 BC formats".into()),
        }
    }
    fn bytes_per_block(self)->usize{
        match self {
            Self::Bc1|Self::Bc4=>8,
            Self::Bc2|Self::Bc3|Self::Bc5=>16,
        }
    }
}
#[derive(Debug, Clone)]
pub struct OriginalBcTopMip<'a> {
    pub width: u32,
    pub height: u32,
    pub format: OriginalBcFormat,
    pub flags: u32,
    pub source_bulk_offset: usize,
    pub blocks: &'a [u8],
}
pub fn first_mip_bc<'a>(
    catalog:&PackageCatalog,
    package_file:&[u8],
    companion_uexp:&[u8],
    companion_ubulk:&'a [u8],
    export:&PackageExport,
)->Result<OriginalBcTopMip<'a>,String>{
    if catalog.export_class_name(export)!=Some("Texture2D"){
        return Err("original BC texture export is not a Texture2D".into());
    }
    let source=catalog.export_data(package_file,companion_uexp,export)?;
    let props=properties::scan(catalog,source)?;
    let cooked=source.get(props.bytes_consumed..)
        .ok_or("original BC texture cooked platform data missing")?;
    let width=u32_at(cooked,28)?;
    let height=u32_at(cooked,32)?;
    let depth=u32_at(cooked,36)?;
    let format_name_size=u32_at(cooked,40)? as usize;
    // The original FString pixel-format token includes its terminating NUL.
    // PF_BC4/PF_BC5 use seven bytes, whereas PF_DXT1/3/5 use eight.
    // Accept only exact names; never infer a format from dimensions or bulk size.
    if !matches!(format_name_size,7|8){return Err(format!(
        "original BC texture unexpected platform pixel format name size {format_name_size}"
    ));}
    let fmt=OriginalBcFormat::from_source_pixel_format(
        cooked.get(44..44+format_name_size)
            .ok_or("original BC texture format name truncated")?
    )?;
    let flags_offset=44+format_name_size+12;
    let flags=u32_at(cooked,flags_offset)?;
    let size=u32_at(cooked,flags_offset+4)? as usize;
    let count=u32_at(cooked,flags_offset+8)? as usize;
    let signed_offset=i64_at(cooked,flags_offset+12)?;
    let mip_width=u32_at(cooked,flags_offset+20)?;
    let mip_height=u32_at(cooked,flags_offset+24)?;
    let mip_depth=u32_at(cooked,flags_offset+28)?;
    if width==0||height==0||width>8192||height>8192
        ||width!=mip_width||height!=mip_height||depth!=1||mip_depth!=1{
        return Err("original BC texture top mip extent is invalid".into());
    }
    let bsize=fmt.bytes_per_block();
    let expected=(width.div_ceil(4) as usize)
        .checked_mul(height.div_ceil(4) as usize)
        .and_then(|n|n.checked_mul(bsize))
        .ok_or("original BC texture mip bytes overflow")?;
    if expected>MAX_MIP_BYTES||size!=expected||count!=expected{
        return Err(format!("original BC texture byte count mismatch: dimensions {width}x{height}, stored={size}, count={count}, expected={expected}"));
    }
    if flags!=0x0501 {return Err(format!("original BC external mip flags not source-verified: 0x{flags:x}"));}
    let relative_base=package_file.len().checked_add(companion_uexp.len())
        .and_then(|len|len.checked_sub(4))
        .ok_or("original source package length invalid")? as i64;
    let start=usize::try_from(relative_base.checked_add(signed_offset)
        .ok_or("original BC texture bulk offset overflow")?)
        .map_err(|_|"original BC texture bulk offset negative")?;
    let end=start.checked_add(expected).ok_or("original BC bulk range overflow")?;
    let blocks=companion_ubulk.get(start..end)
        .ok_or("original BC top mip does not fit authenticated external .ubulk")?;
    Ok(OriginalBcTopMip{
        width,height,format:fmt,flags,source_bulk_offset:start,blocks,
    })
}

#[cfg(test)]
mod bc_mip_tests{
    use super::*;
    #[test]fn exact_ue4_pixel_format_names_map_to_universal_bc_formats(){
        for (source,format,size) in [
            (b"PF_DXT1\0".as_slice(),OriginalBcFormat::Bc1,8),
            (b"PF_DXT3\0".as_slice(),OriginalBcFormat::Bc2,16),
            (b"PF_DXT5\0".as_slice(),OriginalBcFormat::Bc3,16),
            (b"PF_BC4\0".as_slice(),OriginalBcFormat::Bc4,8),
            (b"PF_BC5\0".as_slice(),OriginalBcFormat::Bc5,16),
        ]{
            assert_eq!(OriginalBcFormat::from_source_pixel_format(source).unwrap(),format);
            assert_eq!(format.bytes_per_block(),size);
        }
        assert!(OriginalBcFormat::from_source_pixel_format(b"PF_BC5").is_err());
        assert!(OriginalBcFormat::from_source_pixel_format(b"PF_ASTC_4x4\0").is_err());
    }
    #[test]fn original_bc_block_sizes_are_distinct(){
        assert_eq!((2048u32.div_ceil(4)*2048u32.div_ceil(4)*8) as usize,2097152);
        assert_eq!((2048u32.div_ceil(4)*2048u32.div_ceil(4)*16) as usize,4194304);
    }
}

/// First retail Fortnite 5.41 six-face sky cube from the original cooked
/// UTextureCube export (PF_DXT5, inline bulk payload). Unlike landscape
/// UTexture2D mips, the six BC3 cube faces are stored INLINE in .uexp.
///
/// The physical source face order is UE/D3D +X,-X,+Y,-Y,+Z,-Z.
/// This is source byte decoding, not a claim that the full original sky-dome
/// material, exposure/tonemapping or angular orientation is reconstructed.
#[derive(Debug,Clone)]
pub struct OriginalBcCubeTopMip<'a>{
    pub face_size:u32,
    pub source_format:OriginalBcFormat,
    pub source_srgb:bool,
    pub faces:[&'a [u8];6],
}
fn original_bc3_cube_inline<'a>(
    cooked:&'a[u8],source_srgb:bool,
)->Result<OriginalBcCubeTopMip<'a>,String>{
    // Established against SHA-1-verified T_AthenaSkylight.uasset/.uexp
    // from the 4,353,633,176-byte original 5.41 split-s4 archive:
    // 256x256, 6 faces, PF_DXT5, 9 source mips, first inline mip 0x60000.
    if u32_at(cooked,28)?!=256 ||u32_at(cooked,32)?!=256 ||
        u32_at(cooked,36)?!=6 ||u32_at(cooked,40)?!=8 ||
        cooked.get(44..52)!=Some(b"PF_DXT5\0".as_slice()) ||
        u32_at(cooked,56)?!=9 {
        return Err("original Athena sky TextureCube platform dimensions/format/mip count unrecognized".into());
    }
    // The original cooked inline FByteBulkData record contains a 72-byte
    // source descriptor, two matching 0x60000 payload extents, and the
    // 920-byte archive-local placement marker before the six faces.
    // Any changed layout is rejected rather than treated as image pixels.
    if u32_at(cooked,60)?!=1 ||u32_at(cooked,64)?!=72 ||
        u32_at(cooked,68)?!=393_216 ||u32_at(cooked,72)?!=393_216 ||
        u32_at(cooked,76)?!=920 ||
        cooked.get(80..92)!=Some([0u8;12].as_slice()) {
        return Err("original Athena sky inline BC3 mip header does not match verified UE4.21 source".into());
    }
    let blocks_per_face=(256usize/4)*(256usize/4)*16;
    let top=cooked.get(92..92+blocks_per_face*6)
        .ok_or("original Athena sky inline six-face BC3 source bytes truncated")?;
    let faces=std::array::from_fn(|face|{
        let start=face*blocks_per_face;
        &top[start..start+blocks_per_face]
    });
    Ok(OriginalBcCubeTopMip{
        face_size:256,source_format:OriginalBcFormat::Bc3,
        source_srgb,faces,
    })
}

/// Decode the authenticated UTextureCube's top mip. Preserves the original
/// block bytes/face order, rejects unsupported SRGB property metadata.
pub fn first_mip_original_skylight_cube<'a>(
    catalog:&PackageCatalog,
    source_uasset:&[u8],
    source_uexp:&'a[u8],
    export:&PackageExport,
)->Result<OriginalBcCubeTopMip<'a>,String>{
    if catalog.export_class_name(export)!=Some("TextureCube"){
        return Err("original Fortnite sky source is not TextureCube".into());
    }
    let serialized=catalog.export_data(source_uasset,source_uexp,export)?;
    let props=properties::scan(catalog,serialized)?;
    let mut srgb=props.fields.iter().filter(|f|f.name=="SRGB");
    let property=srgb.next().ok_or("original sky TextureCube SRGB serialization missing")?;
    if srgb.next().is_some() ||property.kind!="BoolProperty"{
        return Err("original sky has multiple/non-boolean SRGB source properties".into());
    }
    let linear=property.metadata.iter().any(|f|f=="bool_value=0");
    let gamma=property.metadata.iter().any(|f|f=="bool_value=1");
    if !linear && !gamma{
        return Err("original sky TextureCube SRGB source flag unknown".into());
    }
    original_bc3_cube_inline(
        serialized.get(props.bytes_consumed..)
            .ok_or("original sky cube platform bytes missing")?,
        gamma,
    )
}

#[cfg(test)]
mod original_bc_cube_tests{
    use super::*;
    #[test]fn six_original_bc3_faces_have_exact_nonoverlapping_spans(){
        let mut cooked=vec![0u8;92+393_216];
        cooked[28..32].copy_from_slice(&256u32.to_le_bytes());
        cooked[32..36].copy_from_slice(&256u32.to_le_bytes());
        cooked[36..40].copy_from_slice(&6u32.to_le_bytes());
        cooked[40..44].copy_from_slice(&8u32.to_le_bytes());
        cooked[44..52].copy_from_slice(b"PF_DXT5\0");
        for (offset,value) in [(56,9u32),(60,1),(64,72),(68,393_216),(72,393_216),(76,920)]{
            cooked[offset..offset+4].copy_from_slice(&value.to_le_bytes());
        }
        for face in 0..6{
            cooked[92+face*65_536..92+(face+1)*65_536].fill(face as u8+1);
        }
        let decoded=original_bc3_cube_inline(&cooked,false).unwrap();
        assert_eq!(decoded.face_size,256);
        assert!(!decoded.source_srgb);
        for i in 0..6{
            assert_eq!(decoded.faces[i].len(),65_536);
            assert!(decoded.faces[i].iter().all(|b|*b==i as u8+1));
        }
        cooked[32..36].copy_from_slice(&128u32.to_le_bytes());
        assert!(original_bc3_cube_inline(&cooked,false).is_err());
    }
    #[test]fn broken_original_cube_mip_record_is_rejected(){
        let mut cooked=vec![0u8;92];
        cooked[28..32].copy_from_slice(&256u32.to_le_bytes());
        cooked[32..36].copy_from_slice(&256u32.to_le_bytes());
        cooked[36..40].copy_from_slice(&6u32.to_le_bytes());
        cooked[40..44].copy_from_slice(&8u32.to_le_bytes());
        cooked[44..52].copy_from_slice(b"PF_DXT5\0");
        cooked[56..60].copy_from_slice(&9u32.to_le_bytes());
        assert!(original_bc3_cube_inline(&cooked,false).is_err());
    }
}
