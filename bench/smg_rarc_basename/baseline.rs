//! Nintendo RARC archive reader. SMG-specific archive handling stays here.

use std::{collections::BTreeMap, fs, path::Path};

use crate::decompress_yaz0;

#[derive(Clone, Debug)]
pub struct RarcEntry {
    pub path: String,
    pub name: String,
    pub data: Vec<u8>,
}

#[derive(Clone, Debug, Default)]
pub struct RarcArchive {
    entries: BTreeMap<String, RarcEntry>,
}

impl RarcArchive {
    pub fn parse(source: &[u8]) -> Result<Self, String> {
        let owned;
        let bytes = if source.starts_with(b"Yaz0") {
            owned = decompress_yaz0(source)?;
            owned.as_slice()
        } else {
            source
        };
        if bytes.len() < 0x40 || &bytes[..4] != b"RARC" {
            return Err("not a big-endian RARC archive".to_owned());
        }

        let data_header_off = be32(bytes, 0x08)? as usize;
        if data_header_off != 0x20 {
            return Err(format!("unexpected RARC data-header offset 0x{data_header_off:x}"));
        }
        let data_header_size = be32(bytes, 0x0c)? as usize;
        let data_off = checked_add(data_header_off, data_header_size, "RARC data offset")?;

        let node_count = be32(bytes, 0x20)? as usize;
        let node_table = checked_add(data_header_off, be32(bytes, 0x24)? as usize, "node table")?;
        let entry_count = be32(bytes, 0x28)? as usize;
        let entry_table = checked_add(data_header_off, be32(bytes, 0x2c)? as usize, "entry table")?;
        let string_table = checked_add(data_header_off, be32(bytes, 0x34)? as usize, "string table")?;

        bounds(bytes, node_table, node_count.checked_mul(0x10).ok_or("node table overflow")?)?;
        bounds(bytes, entry_table, entry_count.checked_mul(0x14).ok_or("entry table overflow")?)?;

        let mut nodes = Vec::with_capacity(node_count);
        for i in 0..node_count {
            let off = node_table + i * 0x10;
            let name_off = be32(bytes, off + 0x04)? as usize;
            let name = c_string(bytes, checked_add(string_table, name_off, "node name")?)?;
            let _ = name;
            nodes.push(NodeRecord {
                count: be16(bytes, off + 0x0a)? as usize,
                first: be32(bytes, off + 0x0c)? as usize,
            });
        }
        if nodes.is_empty() {
            return Err("RARC has no root node".to_owned());
        }

        let mut archive = Self::default();
        let mut visiting = vec![false; nodes.len()];
        walk_node(
            bytes,
            &nodes,
            0,
            "",
            data_off,
            entry_table,
            string_table,
            entry_count,
            &mut visiting,
            &mut archive.entries,
        )?;
        Ok(archive)
    }

    pub fn get(&self, path: &str) -> Option<&[u8]> {
        let key = normalize(path);
        self.entries.get(&key).map(|e| e.data.as_slice()).or_else(|| {
            let name = key.rsplit('/').next()?;
            let mut matches = self.entries.values().filter(|e| e.name.eq_ignore_ascii_case(name));
            let first = matches.next()?;
            matches.next().is_none().then_some(first.data.as_slice())
        })
    }

    pub fn entry(&self, path: &str) -> Option<&RarcEntry> {
        self.entries.get(&normalize(path))
    }

    pub fn entries(&self) -> impl Iterator<Item = &RarcEntry> {
        self.entries.values()
    }

    pub fn entries_under<'a>(&'a self, prefix: &'a str) -> impl Iterator<Item = &'a RarcEntry> + 'a {
        let prefix = normalize(prefix);
        self.entries.values().filter(move |e| e.path.starts_with(&prefix))
    }
}

pub fn load_rarc_file(path: &Path) -> Result<RarcArchive, String> {
    let bytes = fs::read(path).map_err(|e| format!("read {}: {e}", path.display()))?;
    RarcArchive::parse(&bytes).map_err(|e| format!("{}: {e}", path.display()))
}

fn walk_node(
    bytes: &[u8],
    nodes: &[NodeRecord],
    node_index: usize,
    parent: &str,
    data_off: usize,
    entry_table: usize,
    string_table: usize,
    total_entries: usize,
    visiting: &mut [bool],
    out: &mut BTreeMap<String, RarcEntry>,
) -> Result<(), String> {
    if node_index >= nodes.len() {
        return Err(format!("RARC directory references node {node_index} of {}", nodes.len()));
    }
    if visiting[node_index] {
        return Ok(());
    }
    visiting[node_index] = true;

    let node = &nodes[node_index];
    if node.first().checked_add(node.count()).is_none_or(|v| v > total_entries) {
        return Err("RARC node entry range is invalid".to_owned());
    }

    for j in 0..node.count() {
        let off = entry_table + (node.first() + j) * 0x14;
        let flags_name = be32(bytes, off + 0x04)?;
        let flags = (flags_name >> 24) as u8;
        let name_off = (flags_name & 0x00ff_ffff) as usize;
        let name = c_string(bytes, checked_add(string_table, name_off, "entry name")?)?;
        if name == "." || name == ".." {
            continue;
        }
        let entry_data_off = be32(bytes, off + 0x08)? as usize;
        let entry_size = be32(bytes, off + 0x0c)? as usize;
        let path = if parent.is_empty() { name.clone() } else { format!("{parent}/{name}") };

        if flags & 0x02 != 0 {
            walk_node(
                bytes, nodes, entry_data_off, &path, data_off, entry_table, string_table,
                total_entries, visiting, out,
            )?;
            continue;
        }

        let start = checked_add(data_off, entry_data_off, "file data")?;
        bounds(bytes, start, entry_size)?;
        let raw = &bytes[start..start + entry_size];
        let data = if flags & 0x04 != 0 {
            if flags & 0x80 != 0 || raw.starts_with(b"Yaz0") {
                decompress_yaz0(raw)?
            } else {
                return Err(format!("{path}: Yay0-compressed RARC member is not supported yet"));
            }
        } else {
            raw.to_vec()
        };
        let key = normalize(&path);
        out.insert(key.clone(), RarcEntry { path: key, name, data });
    }

    visiting[node_index] = false;
    Ok(())
}

// Small trait keeps the recursive walker independent of the local parse struct.
trait NodeLike {
    fn first(&self) -> usize;
    fn count(&self) -> usize;
}
impl NodeLike for NodeRecord {
    fn first(&self) -> usize { self.first }
    fn count(&self) -> usize { self.count }
}
#[derive(Clone)]
struct NodeRecord { first: usize, count: usize }

fn normalize(path: &str) -> String {
    path.replace('\\', "/").trim_matches('/').to_ascii_lowercase()
}

fn checked_add(a: usize, b: usize, what: &str) -> Result<usize, String> {
    a.checked_add(b).ok_or_else(|| format!("{what} overflow"))
}
fn bounds(bytes: &[u8], off: usize, size: usize) -> Result<(), String> {
    if off.checked_add(size).is_some_and(|end| end <= bytes.len()) { Ok(()) }
    else { Err(format!("RARC range 0x{off:x}+0x{size:x} exceeds 0x{:x}", bytes.len())) }
}
fn be16(bytes: &[u8], off: usize) -> Result<u16, String> {
    bounds(bytes, off, 2)?;
    Ok(u16::from_be_bytes([bytes[off], bytes[off + 1]]))
}
fn be32(bytes: &[u8], off: usize) -> Result<u32, String> {
    bounds(bytes, off, 4)?;
    Ok(u32::from_be_bytes(bytes[off..off + 4].try_into().unwrap()))
}
fn c_string(bytes: &[u8], off: usize) -> Result<String, String> {
    if off >= bytes.len() { return Err("RARC string offset out of range".to_owned()); }
    let end = bytes[off..].iter().position(|&b| b == 0).map(|n| off + n).unwrap_or(bytes.len());
    Ok(String::from_utf8_lossy(&bytes[off..end]).into_owned())
}

