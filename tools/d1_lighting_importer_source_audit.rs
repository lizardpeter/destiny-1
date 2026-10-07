//! Linux source-contract probe against the production D1 importer.
//! Requires the owner-provided Oodle 3 DLL and verified liblinoodle3 bridge.
//! Build with RUSTFLAGS='-L native=/absolute/runtime' cargo build --example lighting_source_audit.
//! Run from that runtime directory with LD_LIBRARY_PATH set to its path.
use std::{ffi::c_void, path::Path};
use destiny1_importer::{archive::Destiny1Archive, tiger::TigerBlockDecompressor, Error, Result};

#[link(name = "linoodle3")]
unsafe extern "C" {
    fn OodleLZ_Decompress(src: *const c_void, src_len: i64, dst: *mut c_void, dst_len: i64,
        fuzz_safe: u32, crc: u32, verbosity: u32, a: *mut c_void, b: *mut c_void,
        c: *mut c_void, d: *mut c_void, e: *mut c_void, f: *mut c_void, phase: u32) -> i64;
}

struct Bridge;
impl TigerBlockDecompressor for Bridge {
    fn decompress_exact(&self, stored: &[u8], raw_len: usize) -> Result<Vec<u8>> {
        let mut raw = vec![0; raw_len];
        let null = std::ptr::null_mut();
        let got = unsafe { OodleLZ_Decompress(stored.as_ptr().cast(), stored.len() as i64,
            raw.as_mut_ptr().cast(), raw_len as i64, 1, 0, 1, null, null, null, null, null, null, 3) };
        if got != raw_len as i64 {
            return Err(Error::Invalid(format!("Oodle returned {got}, expected {raw_len}")));
        }
        Ok(raw)
    }
}

fn main() -> Result<()> {
    let args: Vec<_> = std::env::args().collect();
    let root = args.get(1).expect("package directory argument");
    let mut archive = Destiny1Archive::scan(Path::new(root))?;
    archive.set_block_decompressor(Box::new(Bridge));
    println!("CURRENT_TAGS {}", archive.current_tags().len());
    let globals = destiny1_importer::global_channels::decode_current_render_global_channels(&archive)?;
    println!("GLOBALS {:08X} CHANNELS {:08X} COUNT {}", globals.render_globals_hash,
        globals.global_channel_defaults_hash, globals.defaults.channels.len());
    let tables: Vec<u32> = args.iter().skip(2).map(|s| u32::from_str_radix(s.trim_start_matches("0x"), 16).unwrap()).collect();
    let tables = if tables.is_empty() { vec![0x80C984AA, 0x80CA0B18] } else { tables };
    let lighting = destiny1_importer::d1_scene_lighting::build_d1_scene_lighting(&archive, 0x80C98019, &tables)?;
    println!("LIGHTING PROGRAMS {} LIGHTS {} TEXTURES {}", lighting.programs.len(),
        lighting.model.lights.len(), lighting.model.textures.len());
    for line in lighting.report { println!("REPORT {line}"); }
    for p in &lighting.programs { p.validate().map_err(Error::Invalid)?; }
    println!("LIGHTING_IR_VALIDATED");
    Ok(())
}
