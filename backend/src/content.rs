//! Content manifest ("CdnContentManifest", fetched from the URL in the sign-on client
//! config during `bootflow:content_check`, processed by eboot+0x2B0980).
//!
//! Retail manifests start with a 0x108-byte signature block checked against Bungie's
//! keys when the byte at 0x18DC974 is set; d1-native clears it when D1_BACKEND is used,
//! so ours is unsigned. Schema (0x1911470):
//! ```text
//!  1 repeated {1 int, 2 string[129], 3 int, 4 string[129]}            (x64)
//!  2 repeated {1 int, 2 int, 3 {...}, 4 int, 5 bool, 6 string[48]}     (x64, offers)
//!  3 repeated {1 int id, 2 string[257] package name, 3 int package id,
//!              4 int64}                                                (x1500)
//!  4 repeated {1 string[257], 2 int}                                    (x800)
//!  5 string[37]  GUID; must match client config id 101
//! ```
//! Field 3 is the patchable package list that `bootflow:package_registration`
//! (0x79E740) registers with the resource system (0x78AF50 -> 0xCDBD0 -> 0xD6300).
//! Entries whose id has top nibble 0xB are entitlement-gated; others are always
//! registered. Registration checks the package header against the entry: header u16 at
//! 0x04 must equal field 3 (else -91) and header u64 at 0x08 must equal field 4 (else
//! -90), so the backend reads both from the package files' headers.

use crate::{pb, Shared};
use axum::extract::State;
use std::collections::BTreeMap;
use tracing::info;

pub const MANIFEST_GUID: &str = "d1b00000-0000-4000-8000-000000000001";

/// One patchable package: the newest generation of each package id (English only for
/// localized packages).
pub struct Package {
    pub file: String,
    pub id: u16,
    /// Header u64 at 0x08 (checked against manifest field 4).
    pub key: u64,
}

/// Parses a `packages.txt` listing (one `.pkg` file name per line) and reads each chosen
/// package's header from `dir` (only the first 0x140 bytes are needed).
pub fn load_packages(list: &str, dir: &std::path::Path) -> Vec<Package> {
    let mut newest: BTreeMap<String, (u32, String, u16)> = BTreeMap::new();
    for line in list.lines().map(str::trim).filter(|l| l.ends_with(".pkg")) {
        let stem = &line[..line.len() - 4];
        let Some((base, generation)) = stem.rsplit_once('_') else { continue };
        let Ok(generation) = generation.parse::<u32>() else { continue };
        let mut parts: Vec<&str> = base.split('_').collect();
        // localized: ..._<id>_<locale>_<gen>
        let locale = parts.last().copied().filter(|p| p.len() <= 3 && p.chars().all(|c| c.is_ascii_lowercase()));
        if let Some(l) = locale {
            if l != "en" {
                continue;
            }
            parts.pop();
        }
        let Some(id) = parts.last().and_then(|p| u16::from_str_radix(p, 16).ok().filter(|_| p.len() == 4)) else {
            continue; // unpatchable bootstrap packages have no id and ship on disc
        };
        let e = newest.entry(base.to_string()).or_insert((generation, line.to_string(), id));
        if generation >= e.0 {
            *e = (generation, line.to_string(), id);
        }
    }
    newest
        .into_values()
        .filter_map(|(_, file, id)| {
            use std::io::Read;
            let mut h = [0u8; 0x10];
            let mut f = std::fs::File::open(dir.join(&file)).map_err(|e| tracing::warn!("{file}: {e}")).ok()?;
            f.read_exact(&mut h).ok()?;
            let hid = u16::from_le_bytes([h[4], h[5]]);
            if hid != id {
                tracing::warn!("{file}: header package id {hid:#x} != name id {id:#x}");
            }
            Some(Package { file, id: hid, key: u64::from_le_bytes(h[8..16].try_into().unwrap()) })
        })
        .collect()
}

pub async fn manifest(State(st): State<Shared>) -> Vec<u8> {
    let mut m = pb::Msg::new();
    for (i, p) in st.packages.iter().enumerate().take(1500) {
        let entry = pb::Msg::new()
            .uint(1, (i + 1) as u64)
            .str(2, &p.file)
            .uint(3, u64::from(p.id))
            .uint(4, p.key);
        m = m.msg(3, entry);
    }
    info!("content: manifest requested ({} packages)", st.packages.len());
    m.str(5, MANIFEST_GUID).into_bytes()
}
