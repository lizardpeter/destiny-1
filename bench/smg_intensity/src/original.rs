//! Nintendo GX / J3D TEX1 + BTI texture decoding.
//!
//! Decoding is source-private. The generic renderer receives RGBA8
//! NeutralTexture payloads and never knows about GX swizzles or palettes.

use neutral_scene::{
    program::{
        ProgramAddressMode, ProgramFilter, ProgramMipmapMode, ProgramSamplerState,
    },
    NeutralTexture, NeutralTextureMip,
};

#[derive(Clone, Debug)]
pub struct J3dTexture {
    pub source_index: usize,
    pub format: u8,
    pub palette_format: u8,
    pub wrap_s: u8,
    pub wrap_t: u8,
    pub max_anisotropy: u8,
    pub min_filter: u8,
    pub mag_filter: u8,
    pub min_lod: f32,
    pub max_lod: f32,
    pub mip_count: u8,
    pub lod_bias: f32,
    pub neutral: NeutralTexture,
}

impl J3dTexture {
    /// Translate the preserved GX BTI sampler to source-neutral state.
    ///
    /// Authored TEX1 mip levels are retained in the neutral texture so GX
    /// minification/LOD state can be translated without renderer-side guesses.
    pub fn neutral_sampler_state(&self) -> Result<ProgramSamplerState, String> {
        let address = |wrap: u8| -> Result<ProgramAddressMode, String> {
            match wrap {
                0 => Ok(ProgramAddressMode::ClampToEdge),
                1 => Ok(ProgramAddressMode::Repeat),
                2 => Ok(ProgramAddressMode::MirroredRepeat),
                other => Err(format!("unsupported GX wrap mode {other}")),
            }
        };
        let mag_filter = match self.mag_filter {
            0 => ProgramFilter::Nearest,
            1 => ProgramFilter::Linear,
            other => return Err(format!("unsupported GX mag filter {other}")),
        };
        let (min_filter, mipmap_mode, source_uses_mips) = match self.min_filter {
            0 => (ProgramFilter::Nearest, ProgramMipmapMode::Nearest, false),
            1 => (ProgramFilter::Linear, ProgramMipmapMode::Nearest, false),
            2 => (ProgramFilter::Nearest, ProgramMipmapMode::Nearest, true),
            3 => (ProgramFilter::Linear, ProgramMipmapMode::Nearest, true),
            4 => (ProgramFilter::Nearest, ProgramMipmapMode::Linear, true),
            5 => (ProgramFilter::Linear, ProgramMipmapMode::Linear, true),
            other => return Err(format!("unsupported GX min filter {other}")),
        };
        if source_uses_mips && self.neutral.mips.len() + 1 != self.mip_count as usize {
            return Err(format!(
                "GX texture declares {} mip(s) but neutral payload carries {}",
                self.mip_count,
                self.neutral.mips.len() + 1
            ));
        }
        let max_anisotropy = match self.max_anisotropy {
            0 => 1,
            1 => 2,
            2 => 4,
            other => return Err(format!("unsupported GX anisotropy mode {other}")),
        };
        Ok(ProgramSamplerState {
            mag_filter,
            min_filter,
            mipmap_mode,
            address_u: address(self.wrap_s)?,
            address_v: address(self.wrap_t)?,
            address_w: ProgramAddressMode::Repeat,
            mip_lod_bias_bits: self.lod_bias.to_bits(),
            max_anisotropy,
            compare: None,
            min_lod_bits: self.min_lod.to_bits(),
            max_lod_bits: if source_uses_mips { self.max_lod.to_bits() } else { 0.0f32.to_bits() },
            ..Default::default()
        })
    }
}

/// Decode one standalone Nintendo BTI texture. BTI uses the same 0x20-byte
/// image header embedded in J3D TEX1, with palette/image offsets relative to
/// the start of that header.
pub fn decode_bti(bytes: &[u8], name: &str) -> Result<J3dTexture, String> {
    if bytes.len() < 0x20 {
        return Err(format!("BTI {name} is only {} bytes", bytes.len()));
    }
    let format = byte(bytes, 0)?;
    let width = be16(bytes, 0x02)? as usize;
    let height = be16(bytes, 0x04)? as usize;
    let wrap_s = byte(bytes, 0x06)?;
    let wrap_t = byte(bytes, 0x07)?;
    let palette_format = byte(bytes, 0x09)?;
    let palette_count = be16(bytes, 0x0a)? as usize;
    let palette_rel = be32(bytes, 0x0c)? as usize;
    let max_anisotropy = byte(bytes, 0x13)?;
    let min_filter = byte(bytes, 0x14)?;
    let mag_filter = byte(bytes, 0x15)?;
    let min_lod = byte(bytes, 0x16)? as i8 as f32 / 8.0;
    let max_lod = byte(bytes, 0x17)? as i8 as f32 / 8.0;
    let mip_count = byte(bytes, 0x18)?.max(1);
    let lod_bias = be16(bytes, 0x1a)? as i16 as f32 / 100.0;
    let data_rel = be32(bytes, 0x1c)? as usize;

    if width == 0 || height == 0 {
        return Err(format!("BTI {name} has zero dimensions"));
    }
    if data_rel == 0 {
        return Err(format!("BTI {name} has no image payload"));
    }

    let palette = if matches!(format, 0x08 | 0x09 | 0x0a) {
        if palette_rel == 0 {
            return Err(format!("BTI {name} indexed texture has no palette"));
        }
        let len = palette_count.checked_mul(2).ok_or("BTI palette size overflow")?;
        Some(
            bytes
                .get(palette_rel..palette_rel + len)
                .ok_or_else(|| format!("BTI {name} palette out of range"))?,
        )
    } else {
        None
    };

    let mut level_offset = data_rel;
    let mut rgba = Vec::new();
    let mut mips = Vec::with_capacity(mip_count.saturating_sub(1) as usize);
    for level in 0..mip_count as usize {
        let level_width = (width >> level).max(1);
        let level_height = (height >> level).max(1);
        let level_len = gx_level_size(format, level_width, level_height)?;
        let level_data = bytes
            .get(level_offset..level_offset + level_len)
            .ok_or_else(|| {
                format!(
                    "BTI {name} mip {level} payload out of range at 0x{level_offset:x}"
                )
            })?;
        let decoded = decode_gx_texture_level(
            format,
            palette_format,
            palette,
            level_data,
            level_width,
            level_height,
        )?;
        if level == 0 {
            rgba = decoded;
        } else {
            mips.push(NeutralTextureMip {
                width: level_width as u32,
                height: level_height as u32,
                rgba: decoded,
            });
        }
        level_offset = level_offset
            .checked_add(level_len)
            .ok_or("BTI mip offset overflow")?;
    }

    Ok(J3dTexture {
        source_index: 0,
        format,
        palette_format,
        wrap_s,
        wrap_t,
        max_anisotropy,
        min_filter,
        mag_filter,
        min_lod,
        max_lod,
        mip_count,
        lod_bias,
        neutral: NeutralTexture {
            name: name.to_owned(),
            width: width as u32,
            height: height as u32,
            rgba,
            mips,
            compressed: None,
        },
    })
}

pub fn decode_tex1(bytes: &[u8], model_name: &str) -> Result<Vec<J3dTexture>, String> {
    let count = be16(bytes, 0x08)? as usize;
    let headers = be32(bytes, 0x0c)? as usize;
    let names_off = be32(bytes, 0x10)? as usize;
    let names = parse_string_table(bytes, names_off)?;

    let mut out = Vec::with_capacity(count);
    for i in 0..count {
        let h = headers.checked_add(i.checked_mul(0x20).ok_or("TEX1 header overflow")?)
            .ok_or("TEX1 header overflow")?;
        let format = byte(bytes, h)?;
        let width = be16(bytes, h + 0x02)? as usize;
        let height = be16(bytes, h + 0x04)? as usize;
        let wrap_s = byte(bytes, h + 0x06)?;
        let wrap_t = byte(bytes, h + 0x07)?;
        let palette_format = byte(bytes, h + 0x09)?;
        let palette_count = be16(bytes, h + 0x0a)? as usize;
        let palette_rel = be32(bytes, h + 0x0c)? as usize;
        let max_anisotropy = byte(bytes, h + 0x13)?;
        let min_filter = byte(bytes, h + 0x14)?;
        let mag_filter = byte(bytes, h + 0x15)?;
        let min_lod = byte(bytes, h + 0x16)? as i8 as f32 / 8.0;
        let max_lod = byte(bytes, h + 0x17)? as i8 as f32 / 8.0;
        let mip_count = byte(bytes, h + 0x18)?.max(1);
        let lod_bias = be16(bytes, h + 0x1a)? as i16 as f32 / 100.0;
        let data_rel = be32(bytes, h + 0x1c)? as usize;

        if width == 0 || height == 0 {
            return Err(format!("TEX1 texture {i} has zero dimensions"));
        }
        if data_rel == 0 {
            return Err(format!("TEX1 texture {i} has no image payload"));
        }

        let data_off = h.checked_add(data_rel).ok_or("TEX1 image offset overflow")?;

        let palette = if matches!(format, 0x08 | 0x09 | 0x0a) {
            if palette_rel == 0 {
                return Err(format!("TEX1 indexed texture {i} has no palette"));
            }
            let p = h.checked_add(palette_rel).ok_or("TEX1 palette offset overflow")?;
            let len = palette_count.checked_mul(2).ok_or("TEX1 palette size overflow")?;
            Some(bytes.get(p..p + len).ok_or_else(|| format!("TEX1 texture {i} palette out of range"))?)
        } else {
            None
        };

        let mut level_offset = data_off;
        let mut rgba = Vec::new();
        let mut mips = Vec::with_capacity(mip_count.saturating_sub(1) as usize);
        for level in 0..mip_count as usize {
            let level_width = (width >> level).max(1);
            let level_height = (height >> level).max(1);
            let level_len = gx_level_size(format, level_width, level_height)?;
            let level_data = bytes
                .get(level_offset..level_offset + level_len)
                .ok_or_else(|| format!(
                    "TEX1 texture {i} mip {level} payload out of range at 0x{level_offset:x}"
                ))?;
            let decoded = decode_gx_texture_level(
                format,
                palette_format,
                palette,
                level_data,
                level_width,
                level_height,
            )?;
            if level == 0 {
                rgba = decoded;
            } else {
                mips.push(NeutralTextureMip {
                    width: level_width as u32,
                    height: level_height as u32,
                    rgba: decoded,
                });
            }
            level_offset = level_offset
                .checked_add(level_len)
                .ok_or("TEX1 mip offset overflow")?;
        }
        let name = names.get(i).cloned().unwrap_or_else(|| format!("texture_{i}"));
        out.push(J3dTexture {
            source_index: i,
            format,
            palette_format,
            wrap_s,
            wrap_t,
            max_anisotropy,
            min_filter,
            mag_filter,
            min_lod,
            max_lod,
            mip_count,
            lod_bias,
            neutral: NeutralTexture {
                name: format!("{model_name}:{name}"),
                width: width as u32,
                height: height as u32,
                rgba,
                mips,
                compressed: None,
            },
        });
    }
    Ok(out)
}

pub fn decode_gx_texture_level(
    format: u8,
    palette_format: u8,
    palette: Option<&[u8]>,
    data: &[u8],
    width: usize,
    height: usize,
) -> Result<Vec<u8>, String> {
    let (bw, bh, block_bytes) = block_layout(format)?;
    let blocks_x = width.div_ceil(bw);
    let blocks_y = height.div_ceil(bh);
    let need = blocks_x.checked_mul(blocks_y)
        .and_then(|v| v.checked_mul(block_bytes))
        .ok_or("GX texture size overflow")?;
    if data.len() < need {
        return Err(format!("GX texture needs {need} bytes but has {}", data.len()));
    }

    let mut rgba = vec![0u8; width * height * 4];
    let mut src = 0usize;
    for by in 0..blocks_y {
        for bx in 0..blocks_x {
            let block = &data[src..src + block_bytes];
            match format {
                0x00 => decode_i4(block, bx, by, width, height, &mut rgba),
                0x01 => decode_i8(block, bx, by, width, height, &mut rgba),
                0x02 => decode_ia4(block, bx, by, width, height, &mut rgba),
                0x03 => decode_ia8(block, bx, by, width, height, &mut rgba),
                0x04 => decode_rgb565_block(block, bx, by, width, height, &mut rgba),
                0x05 => decode_rgb5a3_block(block, bx, by, width, height, &mut rgba),
                0x06 => decode_rgba8(block, bx, by, width, height, &mut rgba),
                0x08 => decode_c4(block, bx, by, width, height, palette_format, palette.ok_or("C4 missing palette")?, &mut rgba)?,
                0x09 => decode_c8(block, bx, by, width, height, palette_format, palette.ok_or("C8 missing palette")?, &mut rgba)?,
                0x0a => decode_c14x2(block, bx, by, width, height, palette_format, palette.ok_or("C14X2 missing palette")?, &mut rgba)?,
                0x0e => decode_cmpr(block, bx, by, width, height, &mut rgba),
                other => return Err(format!("unsupported GX texture format 0x{other:02x}")),
            }
            src += block_bytes;
        }
    }
    Ok(rgba)
}

fn block_layout(format: u8) -> Result<(usize, usize, usize), String> {
    match format {
        0x00 => Ok((8, 8, 32)), // I4
        0x01 | 0x02 | 0x09 => Ok((8, 4, 32)), // I8, IA4, C8
        0x03 | 0x04 | 0x05 | 0x0a => Ok((4, 4, 32)), // IA8, 565, 5A3, C14X2
        0x06 => Ok((4, 4, 64)), // RGBA8 split AR/GB planes
        0x08 => Ok((8, 8, 32)), // C4
        0x0e => Ok((8, 8, 32)), // CMPR
        other => Err(format!("unsupported GX texture format 0x{other:02x}")),
    }
}

fn gx_level_size(format: u8, width: usize, height: usize) -> Result<usize, String> {
    let (bw, bh, bytes) = block_layout(format)?;
    width.div_ceil(bw)
        .checked_mul(height.div_ceil(bh))
        .and_then(|v| v.checked_mul(bytes))
        .ok_or_else(|| "GX texture size overflow".to_owned())
}

fn write_pixel(out: &mut [u8], width: usize, height: usize, x: usize, y: usize, c: [u8; 4]) {
    if x >= width || y >= height { return; }
    let o = (y * width + x) * 4;
    out[o..o + 4].copy_from_slice(&c);
}

// GX_TF_I4 and GX_TF_I8 are intensity textures, not opaque luminance:
// Nintendo GX copies the intensity component to *all four* RGBA channels.
// Source particles depend on I4/I8's intensity also being their alpha mask.
fn intensity_rgba(v: u8) -> [u8; 4] { [v, v, v, v] }

fn decode_i4(block: &[u8], bx: usize, by: usize, w: usize, h: usize, out: &mut [u8]) {
    for y in 0..8 {
        for x in 0..8 {
            let b = block[(y * 8 + x) / 2];
            let n = if x & 1 == 0 { b >> 4 } else { b & 0x0f };
            write_pixel(out, w, h, bx * 8 + x, by * 8 + y, intensity_rgba(n * 17));
        }
    }
}

fn decode_i8(block: &[u8], bx: usize, by: usize, w: usize, h: usize, out: &mut [u8]) {
    for y in 0..4 { for x in 0..8 {
        write_pixel(out, w, h, bx*8+x, by*4+y, intensity_rgba(block[y*8+x]));
    }}
}

fn decode_ia4(block: &[u8], bx: usize, by: usize, w: usize, h: usize, out: &mut [u8]) {
    for y in 0..4 { for x in 0..8 {
        let v=block[y*8+x];
        let a=(v>>4)*17; let i=(v&15)*17;
        write_pixel(out,w,h,bx*8+x,by*4+y,[i,i,i,a]);
    }}
}

fn decode_ia8(block: &[u8], bx: usize, by: usize, w: usize, h: usize, out: &mut [u8]) {
    for y in 0..4 { for x in 0..4 {
        let o=(y*4+x)*2;
        let a=block[o]; let i=block[o+1];
        write_pixel(out,w,h,bx*4+x,by*4+y,[i,i,i,a]);
    }}
}

fn rgb565(v:u16)->[u8;4]{
    let r=((v>>11)&31) as u8; let g=((v>>5)&63) as u8; let b=(v&31) as u8;
    [expand5(r), expand6(g), expand5(b), 255]
}
fn rgb5a3(v:u16)->[u8;4]{
    if v&0x8000!=0 {
        [expand5(((v>>10)&31)as u8),expand5(((v>>5)&31)as u8),expand5((v&31)as u8),255]
    } else {
        let a=((v>>12)&7) as u8; let r=((v>>8)&15)as u8; let g=((v>>4)&15)as u8; let b=(v&15)as u8;
        [r*17,g*17,b*17,(a as u16*255/7)as u8]
    }
}
fn expand5(v:u8)->u8{(v<<3)|(v>>2)}
fn expand6(v:u8)->u8{(v<<2)|(v>>4)}

fn decode_rgb565_block(block:&[u8],bx:usize,by:usize,w:usize,h:usize,out:&mut[u8]){
    for y in 0..4{for x in 0..4{
        let o=(y*4+x)*2; let v=u16::from_be_bytes([block[o],block[o+1]]);
        write_pixel(out,w,h,bx*4+x,by*4+y,rgb565(v));
    }}
}
fn decode_rgb5a3_block(block:&[u8],bx:usize,by:usize,w:usize,h:usize,out:&mut[u8]){
    for y in 0..4{for x in 0..4{
        let o=(y*4+x)*2; let v=u16::from_be_bytes([block[o],block[o+1]]);
        write_pixel(out,w,h,bx*4+x,by*4+y,rgb5a3(v));
    }}
}
fn decode_rgba8(block:&[u8],bx:usize,by:usize,w:usize,h:usize,out:&mut[u8]){
    // GX RGBA8 stores a 4x4 AR plane followed by a 4x4 GB plane.
    for y in 0..4{for x in 0..4{
        let i=y*4+x;
        let a=block[i*2]; let r=block[i*2+1];
        let g=block[32+i*2]; let b=block[32+i*2+1];
        write_pixel(out,w,h,bx*4+x,by*4+y,[r,g,b,a]);
    }}
}

fn palette_color(palette_format:u8,palette:&[u8],index:usize)->Result<[u8;4],String>{
    let o=index.checked_mul(2).ok_or("GX palette index overflow")?;
    let s=palette.get(o..o+2).ok_or_else(||format!("GX palette index {index} out of range"))?;
    let v=u16::from_be_bytes([s[0],s[1]]);
    Ok(match palette_format {
        0x00 => { let a=(v>>8)as u8; let i=v as u8; [i,i,i,a] },
        0x01 => rgb565(v),
        0x02 => rgb5a3(v),
        other => return Err(format!("unsupported GX palette format 0x{other:02x}")),
    })
}
fn decode_c4(block:&[u8],bx:usize,by:usize,w:usize,h:usize,pf:u8,p:&[u8],out:&mut[u8])->Result<(),String>{
    for y in 0..8{for x in 0..8{
        let b=block[(y*8+x)/2]; let i=if x&1==0{b>>4}else{b&15};
        write_pixel(out,w,h,bx*8+x,by*8+y,palette_color(pf,p,i as usize)?);
    }} Ok(())
}
fn decode_c8(block:&[u8],bx:usize,by:usize,w:usize,h:usize,pf:u8,p:&[u8],out:&mut[u8])->Result<(),String>{
    for y in 0..4{for x in 0..8{
        write_pixel(out,w,h,bx*8+x,by*4+y,palette_color(pf,p,block[y*8+x] as usize)?);
    }} Ok(())
}
fn decode_c14x2(block:&[u8],bx:usize,by:usize,w:usize,h:usize,pf:u8,p:&[u8],out:&mut[u8])->Result<(),String>{
    for y in 0..4{for x in 0..4{
        let o=(y*4+x)*2;
        let i=(u16::from_be_bytes([block[o],block[o+1]])&0x3fff)as usize;
        write_pixel(out,w,h,bx*4+x,by*4+y,palette_color(pf,p,i)?);
    }} Ok(())
}

fn decode_cmpr(block:&[u8],bx:usize,by:usize,w:usize,h:usize,out:&mut[u8]){
    for sub in 0..4 {
        let sx=(sub&1)*4; let sy=(sub>>1)*4; let b=&block[sub*8..sub*8+8];
        let c0=u16::from_be_bytes([b[0],b[1]]); let c1=u16::from_be_bytes([b[2],b[3]]);
        let a=rgb565(c0); let z=rgb565(c1);
        let mut pal=[[0u8;4];4]; pal[0]=a; pal[1]=z;
        if c0>c1 {
            pal[2]=mix(a,z,2,1,3); pal[3]=mix(a,z,1,2,3);
        } else {
            pal[2]=mix(a,z,1,1,2); pal[3]=[0,0,0,0];
        }
        let bits=u32::from_be_bytes([b[4],b[5],b[6],b[7]]);
        for y in 0..4{for x in 0..4{
            let shift=30-2*(y*4+x);
            let idx=((bits>>shift)&3)as usize;
            write_pixel(out,w,h,bx*8+sx+x,by*8+sy+y,pal[idx]);
        }}
    }
}
fn mix(a:[u8;4],b:[u8;4],aw:u16,bw:u16,d:u16)->[u8;4]{
    [0,1,2,3].map(|i|((a[i]as u16*aw+b[i]as u16*bw)/d)as u8)
}

fn parse_string_table(bytes:&[u8],off:usize)->Result<Vec<String>,String>{
    let count=be16(bytes,off)? as usize; let mut out=Vec::with_capacity(count);
    for i in 0..count {
        let rel=be16(bytes,off+4+i*4+2)? as usize;
        out.push(c_string(bytes,off+rel)?);
    }
    Ok(out)
}
fn byte(b:&[u8],o:usize)->Result<u8,String>{b.get(o).copied().ok_or_else(||format!("TEX1 byte 0x{o:x} out of range"))}
fn be16(b:&[u8],o:usize)->Result<u16,String>{let s=b.get(o..o+2).ok_or_else(||format!("TEX1 u16 0x{o:x} out of range"))?;Ok(u16::from_be_bytes(s.try_into().unwrap()))}
fn be32(b:&[u8],o:usize)->Result<u32,String>{let s=b.get(o..o+4).ok_or_else(||format!("TEX1 u32 0x{o:x} out of range"))?;Ok(u32::from_be_bytes(s.try_into().unwrap()))}
fn c_string(b:&[u8],o:usize)->Result<String,String>{
    if o>=b.len(){return Err(format!("TEX1 string 0x{o:x} out of range"))}
    let n=b[o..].iter().position(|&v|v==0).unwrap_or(b.len()-o);
    Ok(String::from_utf8_lossy(&b[o..o+n]).into_owned())
}

#[cfg(test)]
mod tests{
    use super::*;

    #[test]
    fn standalone_bti_rejects_truncated_header() {
        assert!(decode_bti(&[0u8; 0x1f], "short.bti").is_err());
    }

    #[test]
    fn tex1_retains_authored_lower_mips() {
        let mut sec = vec![0u8; 0x140];
        sec[..4].copy_from_slice(b"TEX1");
        sec[0x08..0x0a].copy_from_slice(&1u16.to_be_bytes());
        sec[0x0c..0x10].copy_from_slice(&0x20u32.to_be_bytes());
        sec[0x10..0x14].copy_from_slice(&0x100u32.to_be_bytes());
        let h=0x20usize;
        sec[h]=0x01; // I8
        sec[h+2..h+4].copy_from_slice(&8u16.to_be_bytes());
        sec[h+4..h+6].copy_from_slice(&8u16.to_be_bytes());
        sec[h+6]=1; sec[h+7]=1;
        sec[h+0x14]=2; // nearest mip nearest
        sec[h+0x15]=1;
        sec[h+0x16]=0; sec[h+0x17]=8;
        sec[h+0x18]=2;
        sec[h+0x1c..h+0x20].copy_from_slice(&0x20u32.to_be_bytes());
        // I8 8x8 is one 8x4 block row pair = 64 bytes; 4x4 is one 8x4 block = 32.
        for b in &mut sec[h+0x20..h+0x20+64] { *b=0x40; }
        for b in &mut sec[h+0x20+64..h+0x20+64+32] { *b=0xc0; }
        sec[0x100..0x102].copy_from_slice(&1u16.to_be_bytes());
        sec[0x104..0x106].copy_from_slice(&8u16.to_be_bytes());
        sec[0x108..0x10a].copy_from_slice(&0u16.to_be_bytes());
        sec[0x10c]=b't'; sec[0x10d]=0;
        let textures=decode_tex1(&sec,"mips").unwrap();
        assert_eq!(textures[0].neutral.mips.len(),1);
        assert_eq!((textures[0].neutral.mips[0].width,textures[0].neutral.mips[0].height),(4,4));
        assert_eq!(textures[0].neutral.rgba[0],0x40);
        assert_eq!(textures[0].neutral.mips[0].rgba[0],0xc0);
    }

    #[test]
    fn bti_sampler_offsets_match_juttexture_contract(){
        let mut sec=vec![0u8;0x80];
        sec[..4].copy_from_slice(b"TEX1");
        sec[0x08..0x0a].copy_from_slice(&1u16.to_be_bytes());
        sec[0x0c..0x10].copy_from_slice(&0x20u32.to_be_bytes());
        sec[0x10..0x14].copy_from_slice(&0x60u32.to_be_bytes());
        let h=0x20usize;
        sec[h]=0x01;
        sec[h+2..h+4].copy_from_slice(&1u16.to_be_bytes());
        sec[h+4..h+6].copy_from_slice(&1u16.to_be_bytes());
        sec[h+6]=1;
        sec[h+7]=2;
        sec[h+0x13]=2;
        sec[h+0x14]=5;
        sec[h+0x15]=1;
        sec[h+0x16]=0;
        sec[h+0x17]=8;
        sec[h+0x18]=1;
        sec[h+0x1a..h+0x1c].copy_from_slice(&(-25i16).to_be_bytes());
        sec[h+0x1c..h+0x20].copy_from_slice(&0x20u32.to_be_bytes());
        sec[h+0x20]=0x7f;
        sec[0x60..0x62].copy_from_slice(&1u16.to_be_bytes());
        sec[0x64..0x66].copy_from_slice(&8u16.to_be_bytes());
        sec[0x68..0x6a].copy_from_slice(&0u16.to_be_bytes());
        sec[0x6c]=b't'; sec[0x6d]=0;
        let t=decode_tex1(&sec,"test").unwrap();
        assert_eq!(t[0].wrap_s,1);
        assert_eq!(t[0].wrap_t,2);
        assert_eq!(t[0].max_anisotropy,2);
        assert_eq!(t[0].min_filter,5);
        assert_eq!(t[0].mag_filter,1);
        assert_eq!(t[0].min_lod,0.0);
        assert_eq!(t[0].max_lod,1.0);
        assert_eq!(t[0].lod_bias,-0.25);
    }

    #[test]
    fn rgba8_split_planes_decode(){
        let mut b=[0u8;64];
        b[0]=0x80; b[1]=0x11; b[32]=0x22; b[33]=0x33;
        let p=decode_gx_texture_level(0x06,0,None,&b,1,1).unwrap();
        assert_eq!(&p[..4], &[0x11,0x22,0x33,0x80]);
    }

    #[test]
    fn i4_nibble_order_is_high_then_low(){
        let mut b=[0u8;32]; b[0]=0xaf;
        let p=decode_gx_texture_level(0x00,0,None,&b,2,1).unwrap();
        assert_eq!(&p[..4], &[0xaa,0xaa,0xaa,0xaa]);
        assert_eq!(&p[4..8], &[255,255,255,255]);
    }

    #[test]
    fn gx_intensity_i4_preserves_alpha_mask() {
        let mut texel = [0u8; 32];
        texel[0] = 0x08; // first pixel fully transparent, second pixel halfway
        let rgba = decode_gx_texture_level(0x00, 0, None, &texel, 2, 1).unwrap();
        assert_eq!(&rgba[0..4], &[0, 0, 0, 0]);
        assert_eq!(&rgba[4..8], &[136, 136, 136, 136]);
    }

    #[test]
    fn gx_intensity_i8_preserves_alpha_mask() {
        let mut texel = [0u8; 32];
        texel[0] = 0;
        texel[1] = 127;
        texel[2] = 255;
        let rgba = decode_gx_texture_level(0x01, 0, None, &texel, 3, 1).unwrap();
        assert_eq!(&rgba[0..4], &[0, 0, 0, 0]);
        assert_eq!(&rgba[4..8], &[127, 127, 127, 127]);
        assert_eq!(&rgba[8..12], &[255, 255, 255, 255]);
    }

    #[test]
    fn rgb565_primaries(){
        assert_eq!(rgb565(0xf800), [255,0,0,255]);
        assert_eq!(rgb565(0x07e0), [0,255,0,255]);
        assert_eq!(rgb565(0x001f), [0,0,255,255]);
    }
}
