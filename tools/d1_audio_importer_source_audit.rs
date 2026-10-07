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
    let root = args.get(1).expect("package directory");
    let hash = u32::from_str_radix(args.get(2).expect("root TagHash"), 16).unwrap();
    let mut archive = Destiny1Archive::scan(Path::new(root))?;
    archive.set_block_decompressor(Box::new(Bridge));
    println!("CURRENT_TAGS {}", archive.current_tags().len());
    if args.get(3).is_some_and(|s| s == "dump") {
        let tag = archive.read_tag(hash)?;
        println!("METADATA {:?} BYTES {}", tag.metadata, tag.bytes.len());
        for (index, chunk) in tag.bytes.chunks(16).enumerate() {
            println!("{:04X}: {:02X?}", index * 16, chunk);
        }
        std::fs::write(format!("{hash:08X}.bin"), tag.bytes)?;
        return Ok(());
    }
    let imported = if args.get(3).is_some_and(|s| s == "scenario") {
        let plan = destiny1_importer::decode_activity_entity_placements(&archive, hash)?;
        println!("SCENARIO TABLES {} PLACEMENTS {}", plan.map_data_tables.len(), plan.placements.len());
        destiny1_importer::build_activity_audio_package(&archive, &plan)?
    } else {
        let tables = destiny1_importer::d1_map::activity_map_tables(&archive, hash)?;
        println!("DESTINATION TABLES {}", tables.len());
        destiny1_importer::build_map_table_audio_package(&archive, &tables)?
    };
    println!("AUDIO_REPORT {:?}", imported.report);
    for owner in imported.ownership { println!("OWNER {:?}", owner); }
    for clip in imported.package.clips {
        println!("CLIP {} channels {} rate {} frames {} loop {:?}", clip.id, clip.channels, clip.sample_rate, clip.frame_count, clip.loop_region);
    }
    Ok(())
}
