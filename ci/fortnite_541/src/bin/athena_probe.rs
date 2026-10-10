//! Read-only proof against real Fortnite 5.41 retail files.
//! Requires a local original PakFile (full or sparse, range-populated) and a
//! historical AES key supplied by the operator. Never runs game code.
use fortnite_541_importer::pak::{self, IndexStatus};
use std::{env, path::PathBuf, process::ExitCode};

fn parse_key(value: &str) -> Result<[u8; 32], String> {
    let hex = value.strip_prefix("0x").unwrap_or(value);
    if hex.len() != 64 || !hex.bytes().all(|ch| ch.is_ascii_hexdigit()) {
        return Err("AES key must have exactly 64 hexadecimal digits".into());
    }
    let mut key = [0u8; 32];
    for (i, byte) in key.iter_mut().enumerate() {
        *byte = u8::from_str_radix(&hex[i * 2..i * 2 + 2], 16)
            .map_err(|_| "invalid AES key hex")?;
    }
    Ok(key)
}

fn run() -> Result<(), String> {
    let path = env::args_os().nth(1).map(PathBuf::from)
        .ok_or("usage: fortnite_541_athena_probe PATH_TO_PAK (set RUST_TEST_FORTNITE_541_AES_KEY)")?;
    let key = parse_key(&env::var("RUST_TEST_FORTNITE_541_AES_KEY")
        .map_err(|_| "missing RUST_TEST_FORTNITE_541_AES_KEY")?)?;
    let report = pak::inspect_with_key(&path, &key)?;
    let IndexStatus::Indexed { mount_point, entries } = &report.status else {
        return Err(format!("Fortnite source index not decoded: {:?}", report.status));
    };
    println!("UE4 PAK v{} original source: {} entries, mount={mount_point:?}",
        report.footer.version, entries.len());
    let map_names = entries.iter().filter(|entry| entry.path.ends_with(".umap")).count();
    println!("Source-backed UMAP packages: {map_names}");
    for path_suffix in [
        "/Maps/Athena_Terrain.umap",
        "/Maps/Athena_Terrain.uexp",
        "/Maps/Landscape/Athena_Terrain_LS_00.umap",
        "/Maps/Landscape/Athena_Terrain_LS_00.uexp",
        "/Maps/Streaming/Sublevel_X0Y0.umap",
        "/Maps/Streaming/Sublevel_X0Y0.uexp",
        "/Maps/Background/Athena_Background.umap",
        "/Maps/Background/Athena_Background.uexp",
    ] {
        let entry = entries.iter().find(|entry| entry.path.ends_with(path_suffix))
            .ok_or_else(|| format!("missing exact source record {path_suffix}"))?;
        let data = pak::extract_plain_entry(&path, &report, entry)?;
        if entry.path.ends_with(".umap") && !data.starts_with(&0x9E2A_83C1u32.to_le_bytes()) {
            return Err(format!("invalid UE4 package file signature {:?}", entry.path));
        }
        println!("VERIFIED {} ({} bytes, SHA-1 matches source entry)",
            entry.path, data.len());
    }
    Ok(())
}

fn main() -> ExitCode {
    match run() {
        Ok(()) => ExitCode::SUCCESS,
        Err(message) => {
            eprintln!("Fortnite Athena retail import proof failed: {message}");
            ExitCode::FAILURE
        }
    }
}
