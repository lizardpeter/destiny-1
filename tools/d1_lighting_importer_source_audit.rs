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
    // The original combined-table census used a map root as a diagnostic
    // placeholder. Scenario activities have a different source layout, so
    // permit an explicit root and keep that distinction visible in the log.
    let mut activity = None;
    let mut scenario_tables = false;
    let mut map_tables = false;
    let mut tables = Vec::new();
    let mut remaining = args.iter().skip(2);
    let parse_hash = |s: &str| -> Result<u32> {
        u32::from_str_radix(s.trim_start_matches("0x").trim_start_matches("0X"), 16)
            .map_err(|_| Error::Invalid(format!("invalid source TagHash {s:?}")))
    };
    while let Some(arg) = remaining.next() {
        if arg == "--scenario-tables" {
            scenario_tables = true;
        } else if arg == "--map-tables" {
            map_tables = true;
        } else if arg == "--activity" {
            if activity.is_some() {
                return Err(Error::Invalid("--activity supplied more than once".into()));
            }
            let value = remaining.next()
                .ok_or_else(|| Error::Invalid("--activity requires a source TagHash".into()))?;
            activity = Some(parse_hash(value)?);
        } else {
            tables.push(parse_hash(arg)?);
        }
    }
    if (scenario_tables || map_tables) && (activity.is_none() || !tables.is_empty() || (scenario_tables && map_tables)) {
        return Err(Error::Invalid("choose one of --scenario-tables/--map-tables, with --activity and no explicit table hashes".into()));
    }
    if let Some(activity) = activity {
        if map_tables {
            tables = destiny1_importer::d1_map::activity_map_tables(&archive, activity)?;
            println!("DESTINATION_MAP_TABLES {:?}", tables.iter().map(|h| format!("{h:08X}")).collect::<Vec<_>>());
        } else {
        let placed = destiny1_importer::world_activity::decode_activity_entity_placements(&archive, activity)?;
        println!("ACTIVITY_PLACEMENTS {:?}", placed.census);
        println!("ACTIVITY_TABLES {:?}", placed.map_data_tables.iter().map(|h| format!("{h:08X}")).collect::<Vec<_>>());
        match destiny1_importer::global_channel_sequencer::decode_activity_global_channel_sequencers(
            &archive, activity, &globals.defaults,
        ) {
            Ok(plan) => {
                println!("ACTIVITY_SEQUENCERS RESOURCES {:?} PROGRAMS {}", plan.resource_hashes.iter().map(|h| format!("{h:08X}")).collect::<Vec<_>>(), plan.programs.len());
                for program in &plan.programs {
                    println!("ACTIVITY_PROGRAM RESOURCE {:08X} CHANNEL {:02X} REQUIREMENTS {:?}",
                        program.resource_hash, program.global_channel_index,
                        destiny1_importer::global_channel_sequencer::global_channel_sequencer_requirements(program)?);
                }
            }
            Err(error) => println!("ACTIVITY_SEQUENCERS UNAVAILABLE {error}"),
        }
        if scenario_tables { tables = placed.map_data_tables; }
        }
    }
    let tables = if tables.is_empty() && !scenario_tables && !map_tables { vec![0x80C984AA, 0x80CA0B18] } else { tables };
    println!("TABLE_SCOPE {}", if scenario_tables { "SCENARIO_ENTITY_LAYER" } else if map_tables { "DESTINATION_BUBBLE_GRAPH" } else { "EXPLICIT_OR_DIAGNOSTIC_TABLE_CENSUS" });
    println!("ACTIVITY_ROOT {:08X} DIAGNOSTIC_PLACEHOLDER {}", activity.unwrap_or(0x80C98019), activity.is_none());
    let lighting = destiny1_importer::d1_scene_lighting::build_d1_scene_lighting(&archive, activity.unwrap_or(0x80C98019), &tables)?;
    println!("LIGHTING PROGRAMS {} LIGHTS {} TEXTURES {}", lighting.programs.len(),
        lighting.model.lights.len(), lighting.model.textures.len());
    for line in lighting.report { println!("REPORT {line}"); }
    for p in &lighting.programs { p.validate().map_err(Error::Invalid)?; }
    println!("LIGHTING_IR_VALIDATED");
    Ok(())
}
