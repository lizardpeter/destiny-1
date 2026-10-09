use std::{
    fs::{self, File},
    io::{Read, Seek, SeekFrom},
    path::{Path, PathBuf},
};

use super::retail_ipak::{T6IpakEndian, T6IpakIndex, T6IpakIndexEntry, T6IpakSection};

const IPAK_VERSION: u32 = 0x0005_0000;
const IPAK_INDEX_SECTION: u32 = 1;
const IPAK_DATA_SECTION: u32 = 2;
const HEADER_BYTES: usize = 16;
const SECTION_BYTES: usize = 16;
const INDEX_ENTRY_BYTES: usize = 16;
const DATA_BLOCK_BYTES: usize = 128;
const DATA_BLOCK_ALIGNMENT: u64 = 128;
const DATA_BLOCK_COMMANDS: usize = 31;
const DATA_BLOCK_DECODE_CAPACITY: usize = 0x8000;
const COMMAND_UNCOMPRESSED: u8 = 0;
const COMMAND_LZO: u8 = 1;
const COMMAND_SKIP: u8 = 0xcf;
const DATA_HASH_MASK: u32 = 0x1fff_ffff;

/// Immutable local retail IPAK opened through seek/range reads.
///
/// Unlike `T6IpakIndex::load`, this path never reads the complete IPAK into RAM.
/// A 2.61 GiB `base.ipak` therefore needs only its tiny header/section/index
/// ranges plus the exact compressed entry spans requested by the caller.
#[derive(Clone, Debug)]
pub struct T6RetailIpakFile {
    pub index: T6IpakIndex,
    pub file_bytes: u64,
}

impl T6RetailIpakFile {
    pub fn open(path: &Path) -> Result<Self, String> {
        let metadata = fs::metadata(path)
            .map_err(|error| format!("failed to stat T6 IPAK {}: {error}", path.display()))?;
        if !metadata.is_file() {
            return Err(format!("T6 IPAK source is not a file: {}", path.display()));
        }
        let file_bytes = metadata.len();
        if file_bytes < HEADER_BYTES as u64 {
            return Err(format!("T6 IPAK {} is smaller than its header", path.display()));
        }
        if file_bytes > u32::MAX as u64 {
            return Err(format!(
                "T6 IPAK {} has {} bytes; T6 header size field is u32",
                path.display(), file_bytes
            ));
        }

        let mut file = File::open(path)
            .map_err(|error| format!("failed to open T6 IPAK {} read-only: {error}", path.display()))?;
        let header = read_exact_at(&mut file, 0, HEADER_BYTES, "IPAK header")?;
        let endian = match &header[0..4] {
            b"KAPI" => T6IpakEndian::Little,
            b"IPAK" => T6IpakEndian::Big,
            other => {
                return Err(format!(
                    "invalid T6 IPAK magic {:02x?} in {}; expected KAPI/IPAK",
                    other,
                    path.display()
                ))
            }
        };
        let version = read_u32(&header, 4, endian)?;
        if version != IPAK_VERSION {
            return Err(format!(
                "unsupported T6 IPAK version 0x{version:08x} in {}; expected 0x{IPAK_VERSION:08x}",
                path.display()
            ));
        }
        let declared_size = read_u32(&header, 8, endian)?;
        if u64::from(declared_size) != file_bytes {
            return Err(format!(
                "T6 IPAK {} declares {} bytes but file has {file_bytes}",
                path.display(), declared_size
            ));
        }
        let section_count = read_u32(&header, 12, endian)? as usize;
        if section_count == 0 || section_count > 64 {
            return Err(format!(
                "T6 IPAK {} has invalid section count {section_count}",
                path.display()
            ));
        }

        let section_bytes = section_count
            .checked_mul(SECTION_BYTES)
            .ok_or_else(|| "T6 IPAK section-table byte count overflow".to_owned())?;
        let section_table = read_exact_at(
            &mut file,
            HEADER_BYTES as u64,
            section_bytes,
            "IPAK section table",
        )?;
        let mut index_section = None;
        let mut data_section = None;
        for section_index in 0..section_count {
            let base = section_index * SECTION_BYTES;
            let section = T6IpakSection {
                section_type: read_u32(&section_table, base, endian)?,
                offset: read_u32(&section_table, base + 4, endian)?,
                size: read_u32(&section_table, base + 8, endian)?,
                item_count: read_u32(&section_table, base + 12, endian)?,
            };
            let end = u64::from(section.offset)
                .checked_add(u64::from(section.size))
                .ok_or_else(|| format!("T6 IPAK section {section_index} range overflow"))?;
            if end > file_bytes {
                return Err(format!(
                    "T6 IPAK section {section_index} range {}..{} escapes {} bytes",
                    section.offset, end, file_bytes
                ));
            }
            match section.section_type {
                IPAK_INDEX_SECTION => {
                    if index_section.replace(section).is_some() {
                        return Err("T6 IPAK contains more than one index section".to_owned());
                    }
                }
                IPAK_DATA_SECTION => {
                    if data_section.replace(section).is_some() {
                        return Err("T6 IPAK contains more than one data section".to_owned());
                    }
                }
                _ => {}
            }
        }
        let index_section = index_section
            .ok_or_else(|| "T6 IPAK does not contain an index section".to_owned())?;
        let data_section = data_section
            .ok_or_else(|| "T6 IPAK does not contain a data section".to_owned())?;
        let required_index_bytes = (index_section.item_count as usize)
            .checked_mul(INDEX_ENTRY_BYTES)
            .ok_or_else(|| "T6 IPAK index byte count overflow".to_owned())?;
        if required_index_bytes > index_section.size as usize {
            return Err(format!(
                "T6 IPAK index needs {required_index_bytes} bytes for {} entries but section has {}",
                index_section.item_count, index_section.size
            ));
        }
        let index_bytes = read_exact_at(
            &mut file,
            u64::from(index_section.offset),
            required_index_bytes,
            "IPAK index",
        )?;
        let mut entries = Vec::with_capacity(index_section.item_count as usize);
        for entry_index in 0..index_section.item_count as usize {
            let base = entry_index * INDEX_ENTRY_BYTES;
            let entry = T6IpakIndexEntry {
                data_hash: read_u32(&index_bytes, base, endian)?,
                name_hash: read_u32(&index_bytes, base + 4, endian)?,
                offset: read_u32(&index_bytes, base + 8, endian)?,
                size: read_u32(&index_bytes, base + 12, endian)?,
            };
            let end = u64::from(entry.offset)
                .checked_add(u64::from(entry.size))
                .ok_or_else(|| format!("T6 IPAK index entry {entry_index} range overflow"))?;
            if end > u64::from(data_section.size) {
                return Err(format!(
                    "T6 IPAK entry {entry_index} range {}..{} escapes data section {}",
                    entry.offset, end, data_section.size
                ));
            }
            entries.push(entry);
        }
        entries.sort_by_key(|entry| entry.combined_key());
        if entries
            .windows(2)
            .any(|pair| pair[0].combined_key() == pair[1].combined_key())
        {
            return Err("T6 IPAK index contains duplicate (nameHash,dataHash) identity".to_owned());
        }

        let index = T6IpakIndex {
            path: path.to_path_buf(),
            endian,
            declared_size,
            index_section,
            data_section,
            entries,
        };
        println!(
            "T6 read-only range IPAK index: {} entries / {} metadata+index bytes read from {}-byte {}",
            index.entries.len(),
            HEADER_BYTES + section_bytes + required_index_bytes,
            file_bytes,
            path.display()
        );
        Ok(Self { index, file_bytes })
    }

    #[inline]
    pub fn find(&self, name_hash: u32, data_hash: u32) -> Option<&T6IpakIndexEntry> {
        self.index.find(name_hash, data_hash)
    }

    /// Decode one exact indexed payload by reading only its serialized entry
    /// range from disk. The retail file is opened read-only and never modified.
    pub fn extract_entry(&self, entry: &T6IpakIndexEntry) -> Result<Vec<u8>, String> {
        let (absolute_start, absolute_end) = self.index.absolute_entry_range(entry);
        if absolute_end > self.file_bytes || absolute_end < absolute_start {
            return Err(format!(
                "T6 IPAK entry range {absolute_start}..{absolute_end} escapes {} bytes",
                self.file_bytes
            ));
        }
        let entry_len = usize::try_from(absolute_end - absolute_start)
            .map_err(|_| "T6 IPAK entry span exceeds usize".to_owned())?;
        let mut file = File::open(&self.index.path).map_err(|error| {
            format!(
                "failed to open T6 IPAK {} read-only for entry extraction: {error}",
                self.index.path.display()
            )
        })?;
        let bytes = read_exact_at(&mut file, absolute_start, entry_len, "IPAK entry")?;
        decode_entry_range(&bytes, self.index.endian, entry.data_hash)
    }
}

/// Return the complete local retail IPAK candidate set used by the retained
/// Nuketown packed-image closure. Missing containers are simply absent so
/// prepared/minimal source trees remain usable. Paths are never created or
/// modified. The retail closure proved all 81 packed aliases only when DLC0's
/// two containers were included alongside the original shared six.
pub fn discover_standard_ipaks(root: &Path) -> Vec<PathBuf> {
    let candidates = [
        root.join("zone/all/mp_nuketown_2020.ipak"),
        root.join("zone/all/dlc0.ipak"),
        root.join("zone/all/dlc0_load_mp.ipak"),
        root.join("zone/all/mp.ipak"),
        root.join("zone/all/base.ipak"),
        root.join("zone/all/patch_mp.ipak"),
        root.join("zone/all/so.ipak"),
        root.join("zone/english/en_base.ipak"),
        // Prepared-source-tree equivalents used by the reversal workspace.
        root.join("map_specific/mp_nuketown_2020.ipak"),
        root.join("shared/dlc0.ipak"),
        root.join("shared/dlc0_load_mp.ipak"),
        root.join("shared/mp.ipak"),
        root.join("shared/base.ipak"),
        root.join("shared/patch_mp.ipak"),
        root.join("shared/so.ipak"),
        root.join("shared/en_base.ipak"),
    ];
    let mut out = Vec::new();
    for path in candidates {
        if path.is_file() && !out.iter().any(|existing| existing == &path) {
            out.push(path);
        }
    }
    out
}

fn decode_entry_range(bytes: &[u8], endian: T6IpakEndian, expected_data_hash: u32) -> Result<Vec<u8>, String> {
    let mut pos = 0usize;
    let end = bytes.len();
    let mut output = Vec::new();
        // One fixed-capacity scratch buffer per extraction, reused by every LZO command.
        let mut lzo_scratch = [0u8; DATA_BLOCK_DECODE_CAPACITY];
    let mut block_count = 0usize;

    while pos < end {
        pos = align_up_relative(pos, DATA_BLOCK_ALIGNMENT as usize)?;
        if pos >= end {
            break;
        }
        let header_end = pos
            .checked_add(DATA_BLOCK_BYTES)
            .ok_or_else(|| "T6 IPAK block header range overflow".to_owned())?;
        let header = bytes
            .get(pos..header_end)
            .ok_or_else(|| format!("T6 IPAK range block at +0x{pos:X} is truncated"))?;
        let count_and_offset = read_u32(header, 0, endian)?;
        let file_offset = (count_and_offset & 0x00ff_ffff) as usize;
        let command_count = (count_and_offset >> 24) as usize;
        if command_count > DATA_BLOCK_COMMANDS {
            return Err(format!(
                "T6 IPAK block at +0x{pos:X} has {command_count} commands; maximum is {DATA_BLOCK_COMMANDS}"
            ));
        }
        let mut commands = Vec::with_capacity(command_count);
        let mut payload_size = 0usize;
        let mut contains_output = false;
        for command_index in 0..command_count {
            let word = read_u32(header, 4 + command_index * 4, endian)?;
            let command_size = (word & 0x00ff_ffff) as usize;
            let command_kind = (word >> 24) as u8;
            payload_size = payload_size
                .checked_add(command_size)
                .ok_or_else(|| "T6 IPAK command payload size overflow".to_owned())?;
            contains_output |= matches!(command_kind, COMMAND_UNCOMPRESSED | COMMAND_LZO);
            commands.push((command_size, command_kind));
        }
        if contains_output && file_offset != output.len() {
            return Err(format!(
                "T6 IPAK block output offset {file_offset} != decoded head {}",
                output.len()
            ));
        }
        let payload_start = header_end;
        let payload_end = payload_start
            .checked_add(payload_size)
            .ok_or_else(|| "T6 IPAK block payload range overflow".to_owned())?;
        if payload_end > end {
            return Err(format!(
                "T6 IPAK block payload {payload_start}..{payload_end} escapes entry span {end}"
            ));
        }
        let payload = &bytes[payload_start..payload_end];
        let mut cursor = 0usize;
        for (command_index, (command_size, command_kind)) in commands.into_iter().enumerate() {
            let command_end = cursor
                .checked_add(command_size)
                .ok_or_else(|| "T6 IPAK command range overflow".to_owned())?;
            let command = payload
                .get(cursor..command_end)
                .ok_or_else(|| "T6 IPAK command payload is truncated".to_owned())?;
            match command_kind {
                COMMAND_UNCOMPRESSED => output.extend_from_slice(command),
                COMMAND_LZO => {
                    let decoded = lzo::decompress_into(command, &mut lzo_scratch).map_err(|error| {
                        format!(
                            "T6 IPAK LZO command {command_index} at block +0x{pos:X} failed: {error:?}"
                        )
                    })?;
                    output.extend_from_slice(&lzo_scratch[..decoded]);
                }
                COMMAND_SKIP => {}
                other => {
                    return Err(format!(
                        "unsupported T6 IPAK compression command 0x{other:02x} at block +0x{pos:X}; refusing guess"
                    ))
                }
            }
            cursor = command_end;
        }
        pos = payload_end;
        block_count += 1;
        if block_count > 10_000 {
            return Err("T6 IPAK entry block walk exceeded 10,000 blocks".to_owned());
        }
    }

    let actual_crc29 = super::retail_ipak_crc::crc32(&output) & DATA_HASH_MASK;
    let expected_crc29 = expected_data_hash & DATA_HASH_MASK;
    if actual_crc29 != expected_crc29 {
        return Err(format!(
            "T6 IPAK decoded CRC29 0x{actual_crc29:08x} != index dataHash 0x{expected_crc29:08x}"
        ));
    }
    Ok(output)
}

fn read_exact_at(file: &mut File, offset: u64, bytes: usize, label: &str) -> Result<Vec<u8>, String> {
    file.seek(SeekFrom::Start(offset))
        .map_err(|error| format!("failed to seek {label} to {offset}: {error}"))?;
    let mut out = vec![0u8; bytes];
    file.read_exact(&mut out)
        .map_err(|error| format!("failed to read {label} at {offset} ({bytes} bytes): {error}"))?;
    Ok(out)
}

fn align_up_relative(value: usize, alignment: usize) -> Result<usize, String> {
    let add = alignment
        .checked_sub(1)
        .ok_or_else(|| "T6 IPAK zero alignment".to_owned())?;
    value
        .checked_add(add)
        .map(|value| value / alignment * alignment)
        .ok_or_else(|| "T6 IPAK alignment overflow".to_owned())
}

fn read_u32(bytes: &[u8], offset: usize, endian: T6IpakEndian) -> Result<u32, String> {
    let raw: [u8; 4] = bytes
        .get(offset..offset + 4)
        .ok_or_else(|| format!("truncated T6 IPAK u32 at 0x{offset:X}"))?
        .try_into()
        .map_err(|_| "invalid T6 IPAK u32 slice".to_owned())?;
    Ok(match endian {
        T6IpakEndian::Little => u32::from_le_bytes(raw),
        T6IpakEndian::Big => u32::from_be_bytes(raw),
    })
}


#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn range_reader_decodes_lzo_command_and_enforces_crc29() {
        let compressed: [u8; 21] = [
            34, 104, 101, 108, 108, 111, 44, 32, 108, 122, 111, 32,
            119, 111, 114, 108, 100, 33, 17, 0, 0,
        ];
        let expected = b"hello, lzo world!";
        let mut entry = vec![0u8; DATA_BLOCK_BYTES + compressed.len()];
        // count=1, decoded output offset=0.
        entry[..4].copy_from_slice(&(1u32 << 24).to_le_bytes());
        // LZO command, 21 encoded bytes.
        entry[4..8].copy_from_slice(&((1u32 << 24) | compressed.len() as u32).to_le_bytes());
        entry[DATA_BLOCK_BYTES..].copy_from_slice(&compressed);
        let hash = super::retail_ipak_crc::crc32(expected) & DATA_HASH_MASK;
        assert_eq!(decode_entry_range(&entry, T6IpakEndian::Little, hash).unwrap(), expected);
        assert!(decode_entry_range(&entry, T6IpakEndian::Little, hash ^ 1).is_err());
    }

    #[test]
    fn standard_ipak_discovery_never_creates_paths() {
        let root = std::env::temp_dir().join("rust_test_t6_ipak_discovery_nonexistent");
        let before = root.exists();
        let found = discover_standard_ipaks(&root);
        assert!(found.is_empty());
        assert_eq!(root.exists(), before);
    }
}