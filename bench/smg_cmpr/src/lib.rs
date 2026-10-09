extern crate self as neutral_scene;
pub mod program {
    #[derive(Clone, Copy, Debug, Default)]
    pub enum ProgramAddressMode {
        #[default] ClampToEdge, Repeat, MirroredRepeat
    }
    #[derive(Clone, Copy, Debug, Default)]
    pub enum ProgramFilter {#[default] Nearest, Linear}
    #[derive(Clone, Copy, Debug, Default)]
    pub enum ProgramMipmapMode {#[default] Nearest, Linear}
    #[derive(Clone, Debug, Default)]
    pub struct ProgramSamplerState {
        pub mag_filter: ProgramFilter,
        pub min_filter: ProgramFilter,
        pub mipmap_mode: ProgramMipmapMode,
        pub address_u: ProgramAddressMode,
        pub address_v: ProgramAddressMode,
        pub address_w: ProgramAddressMode,
        pub mip_lod_bias_bits: u32,
        pub max_anisotropy: u32,
        pub compare: Option<()>,
        pub min_lod_bits: u32,
        pub max_lod_bits: u32
    }
}
#[derive(Clone, Debug, Default)]
pub struct NeutralTextureMip {pub width:u32, pub height:u32, pub rgba: Vec<u8>}
#[derive(Clone, Debug, Default)]
pub struct NeutralTexture {
    pub name:String, pub width:u32, pub height:u32, pub rgba:Vec<u8>,
    pub mips:Vec<NeutralTextureMip>, pub compressed: Option<()>
}
pub mod original;
pub mod optimized;

#[test]
fn whole_cmpr_api_agrees_for_generated_blocks_and_odd_dimensions() {
    let mut seed=0x1234_5678u32;
    for height in 1usize..=65 {
        for width in 1usize..=65 {
            let bytes=width.div_ceil(8)*height.div_ceil(8)*32;
            let mut compressed=vec![0u8;bytes];
            for b in &mut compressed {
                seed ^= seed << 13;
                seed ^= seed >> 17;
                seed ^= seed << 5;
                *b=seed as u8;
            }
            let slow=original::decode_gx_texture_level(0x0e,0,None,&compressed,width,height).unwrap();
            let fast=optimized::decode_gx_texture_level(0x0e,0,None,&compressed,width,height).unwrap();
            assert_eq!(slow,fast,"mismatch for {width}x{height}");
        }
    }
}
