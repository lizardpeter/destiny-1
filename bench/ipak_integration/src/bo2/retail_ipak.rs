use std::{
    fs,
    path::{Path, PathBuf},
};

const IPAK_VERSION: u32 = 0x0005_0000;
const IPAK_INDEX_SECTION: u32 = 1;
const IPAK_DATA_SECTION: u32 = 2;
const HEADER_BYTES: usize = 16;
const SECTION_BYTES: usize = 16;
const INDEX_ENTRY_BYTES: usize = 16;
const DATA_BLOCK_BYTES: usize = 128;
const DATA_BLOCK_ALIGNMENT: usize = 128;
const DATA_BLOCK_COMMANDS: usize = 31;
const DATA_BLOCK_DECODE_CAPACITY: usize = 0x8000;
const COMMAND_UNCOMPRESSED: u8 = 0;
const COMMAND_LZO: u8 = 1;
const COMMAND_SKIP: u8 = 0xcf;
const DATA_HASH_MASK: u32 = 0x1fff_ffff;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum T6IpakEndian {
    Little,
    Big,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct T6IpakSection {
    pub section_type: u32,
    pub offset: u32,
    pub size: u32,
    pub item_count: u32,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct T6IpakIndexEntry {
    pub data_hash: u32,
    pub name_hash: u32,
    /// Byte offset relative to the IPAK data section.
    pub offset: u32,
    /// Serialized IPAK entry span. The entry contains block headers and
    /// compressed/uncompressed commands; this is not the decoded image size.
    pub size: u32,
}

impl T6IpakIndexEntry {
    #[inline]
    pub const fn combined_key(self) -> u64 {
        ((self.name_hash as u64) << 32) | self.data_hash as u64
    }
}

#[derive(Clone, Debug)]
pub struct T6IpakIndex {
    pub path: PathBuf,
    pub endian: T6IpakEndian,
    pub declared_size: u32,
    pub index_section: T6IpakSection,
    pub data_section: T6IpakSection,
    pub entries: Vec<T6IpakIndexEntry>,
}

impl T6IpakIndex {
    /// Parse a retail T6 IPAK without mutating it. This mirrors the pinned OAT
    /// IPak header/section/index loader.
    pub fn load(path: &Path) -> Result<Self, String> {
        let bytes = fs::read(path)
            .map_err(|error| format!("failed to read T6 IPAK {}: {error}", path.display()))?;
        Self::parse(path.to_path_buf(), &bytes)
    }

    pub fn parse(path: PathBuf, bytes: &[u8]) -> Result<Self, String> {
        if bytes.len() < HEADER_BYTES {
            return Err("T6 IPAK header is truncated".to_owned());
        }
        let endian = match &bytes[0..4] {
            b"KAPI" => T6IpakEndian::Little,
            b"IPAK" => T6IpakEndian::Big,
            other => {
                return Err(format!(
                    "invalid T6 IPAK magic {:02x?}; expected KAPI/IPAK",
                    other
                ))
            }
        };
        let version = read_u32(bytes, 4, endian)?;
        if version != IPAK_VERSION {
            return Err(format!(
                "unsupported T6 IPAK version 0x{version:08x}; expected 0x{IPAK_VERSION:08x}"
            ));
        }
        let declared_size = read_u32(bytes, 8, endian)?;
        let section_count = read_u32(bytes, 12, endian)? as usize;
        if section_count == 0 || section_count > 64 {
            return Err(format!("invalid T6 IPAK section count {section_count}"));
        }
        if declared_size as usize != bytes.len() {
            return Err(format!(
                "T6 IPAK declared size {} != file size {}",
                declared_size,
                bytes.len()
            ));
        }

        let section_table_end = HEADER_BYTES
            .checked_add(
                section_count
                    .checked_mul(SECTION_BYTES)
                    .ok_or_else(|| "T6 IPAK section table size overflow".to_owned())?,
            )
            .ok_or_else(|| "T6 IPAK section table range overflow".to_owned())?;
        if section_table_end > bytes.len() {
            return Err("T6 IPAK section table is truncated".to_owned());
        }

        let mut index_section = None;
        let mut data_section = None;
        for section_index in 0..section_count {
            let base = HEADER_BYTES + section_index * SECTION_BYTES;
            let section = T6IpakSection {
                section_type: read_u32(bytes, base, endian)?,
                offset: read_u32(bytes, base + 4, endian)?,
                size: read_u32(bytes, base + 8, endian)?,
                item_count: read_u32(bytes, base + 12, endian)?,
            };
            validate_section(bytes.len(), section, section_index)?;
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

        let mut entries = Vec::with_capacity(index_section.item_count as usize);
        for entry_index in 0..index_section.item_count as usize {
            let base = index_section.offset as usize + entry_index * INDEX_ENTRY_BYTES;
            let entry = T6IpakIndexEntry {
                data_hash: read_u32(bytes, base, endian)?,
                name_hash: read_u32(bytes, base + 4, endian)?,
                offset: read_u32(bytes, base + 8, endian)?,
                size: read_u32(bytes, base + 12, endian)?,
            };
            let end = (entry.offset as u64)
                .checked_add(entry.size as u64)
                .ok_or_else(|| format!("T6 IPAK index entry {entry_index} range overflow"))?;
            if end > data_section.size as u64 {
                return Err(format!(
                    "T6 IPAK index entry {entry_index} data range {}..{} escapes data section size {}",
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

        Ok(Self {
            path,
            endian,
            declared_size,
            index_section,
            data_section,
            entries,
        })
    }

    #[inline]
    pub fn find(&self, name_hash: u32, data_hash: u32) -> Option<&T6IpakIndexEntry> {
        let wanted = ((name_hash as u64) << 32) | (data_hash & DATA_HASH_MASK) as u64;
        self.entries
            .binary_search_by_key(&wanted, |entry| {
                ((entry.name_hash as u64) << 32) | (entry.data_hash & DATA_HASH_MASK) as u64
            })
            .ok()
            .map(|index| &self.entries[index])
    }

    /// Admit the dataHash-only fallback used by the source-closed R2 extractor
    /// only when this IPAK contains exactly one matching 29-bit payload identity.
    pub fn find_unique_data_hash(&self, data_hash: u32) -> Option<&T6IpakIndexEntry> {
        let wanted = data_hash & DATA_HASH_MASK;
        let mut found = None;
        for entry in &self.entries {
            if entry.data_hash & DATA_HASH_MASK == wanted {
                if found.is_some() {
                    return None;
                }
                found = Some(entry);
            }
        }
        found
    }

    #[inline]
    pub fn absolute_entry_range(&self, entry: &T6IpakIndexEntry) -> (u64, u64) {
        let start = self.data_section.offset as u64 + entry.offset as u64;
        (start, start + entry.size as u64)
    }

    /// Decode one indexed entry from the immutable retail IPAK and verify its
    /// exact 29-bit payload CRC identity. Only the raw and LZO command kinds
    /// proven by the canonical T6 range extractor are admitted. Known skip
    /// commands contribute no output; every other command kind fails closed.
    pub fn extract_entry(&self, entry: &T6IpakIndexEntry) -> Result<Vec<u8>, String> {
        let bytes = fs::read(&self.path)
            .map_err(|error| format!("failed to read T6 IPAK {}: {error}", self.path.display()))?;
        self.extract_entry_from_bytes(&bytes, entry)
    }

    pub fn extract_entry_from_bytes(
        &self,
        bytes: &[u8],
        entry: &T6IpakIndexEntry,
    ) -> Result<Vec<u8>, String> {
        if bytes.len() != self.declared_size as usize {
            return Err(format!(
                "T6 IPAK extraction source size {} != indexed size {}",
                bytes.len(), self.declared_size
            ));
        }
        let (absolute_start, absolute_end) = self.absolute_entry_range(entry);
        if absolute_end > bytes.len() as u64 {
            return Err("T6 IPAK entry range escapes extraction source".to_owned());
        }

        let mut pos = absolute_start as usize;
        let end = absolute_end as usize;
        let mut output = Vec::new();
        // One fixed-capacity scratch buffer per extraction, reused by every LZO command.
        let mut lzo_scratch = [0u8; DATA_BLOCK_DECODE_CAPACITY];
        let mut block_count = 0usize;

        while pos < end {
            pos = align_up(pos, DATA_BLOCK_ALIGNMENT)?;
            if pos >= end {
                break;
            }
            let header_end = pos
                .checked_add(DATA_BLOCK_BYTES)
                .ok_or_else(|| "T6 IPAK block header range overflow".to_owned())?;
            let header = bytes
                .get(pos..header_end)
                .ok_or_else(|| format!("T6 IPAK block at 0x{pos:X} is truncated"))?;
            let count_and_offset = read_u32(header, 0, self.endian)?;
            let file_offset = (count_and_offset & 0x00ff_ffff) as usize;
            let command_count = (count_and_offset >> 24) as usize;
            if command_count > DATA_BLOCK_COMMANDS {
                return Err(format!(
                    "T6 IPAK block at 0x{pos:X} has {command_count} commands; maximum is {DATA_BLOCK_COMMANDS}"
                ));
            }

            let mut commands = Vec::with_capacity(command_count);
            let mut payload_size = 0usize;
            let mut contains_output_command = false;
            for command_index in 0..command_count {
                let word = read_u32(header, 4 + command_index * 4, self.endian)?;
                let command_size = (word & 0x00ff_ffff) as usize;
                let command_kind = (word >> 24) as u8;
                payload_size = payload_size
                    .checked_add(command_size)
                    .ok_or_else(|| "T6 IPAK command payload size overflow".to_owned())?;
                contains_output_command |= matches!(command_kind, COMMAND_UNCOMPRESSED | COMMAND_LZO);
                commands.push((command_size, command_kind));
            }
            if contains_output_command && file_offset != output.len() {
                return Err(format!(
                    "T6 IPAK block output offset {file_offset} != decoded head {}",
                    output.len()
                ));
            }

            let payload_start = header_end;
            let payload_end = payload_start
                .checked_add(payload_size)
                .ok_or_else(|| "T6 IPAK block payload range overflow".to_owned())?;
            if payload_end > end || payload_end > bytes.len() {
                return Err(format!(
                    "T6 IPAK block payload {}..{} escapes indexed entry end {}",
                    payload_start, payload_end, end
                ));
            }
            let payload = &bytes[payload_start..payload_end];
            let mut payload_cursor = 0usize;
            for (command_index, (command_size, command_kind)) in commands.into_iter().enumerate() {
                let command_end = payload_cursor
                    .checked_add(command_size)
                    .ok_or_else(|| "T6 IPAK command range overflow".to_owned())?;
                let command = payload
                    .get(payload_cursor..command_end)
                    .ok_or_else(|| "T6 IPAK command payload is truncated".to_owned())?;
                match command_kind {
                    COMMAND_UNCOMPRESSED => output.extend_from_slice(command),
                    COMMAND_LZO => {
                        let decoded = lzo::decompress_into(command, &mut lzo_scratch).map_err(
                            |error| {
                                format!(
                                    "T6 IPAK LZO command {command_index} at block 0x{pos:X} failed: {error:?}"
                                )
                            },
                        )?;
                        output.extend_from_slice(&lzo_scratch[..decoded]);
                    }
                    COMMAND_SKIP => {}
                    other => {
                        return Err(format!(
                            "unsupported T6 IPAK compression command 0x{other:02x} at block 0x{pos:X}; refusing guess"
                        ))
                    }
                }
                payload_cursor = command_end;
            }

            pos = payload_end;
            block_count += 1;
            if block_count > 10_000 {
                return Err("T6 IPAK block walk exceeded 10,000 blocks".to_owned());
            }
        }

        let actual_crc29 = super::retail_ipak_crc::crc32(&output) & DATA_HASH_MASK;
        let expected_crc29 = entry.data_hash & DATA_HASH_MASK;
        if actual_crc29 != expected_crc29 {
            return Err(format!(
                "T6 IPAK decoded CRC29 0x{actual_crc29:08x} != index dataHash 0x{expected_crc29:08x}"
            ));
        }
        Ok(output)
    }
}

/// T6/OAT R_HashString used for IPAK name identity. The seed is intentionally
/// explicit because different callers can use different starting hashes.
pub fn t6_hash_string(value: &str, mut hash: u32) -> u32 {
    for byte in value.bytes() {
        hash = hash.wrapping_mul(33) ^ u32::from(byte.to_ascii_lowercase());
    }
    hash
}

fn validate_section(file_len: usize, section: T6IpakSection, index: usize) -> Result<(), String> {
    let end = (section.offset as u64)
        .checked_add(section.size as u64)
        .ok_or_else(|| format!("T6 IPAK section {index} range overflow"))?;
    if end > file_len as u64 {
        return Err(format!(
            "T6 IPAK section {index} range {}..{} escapes file size {file_len}",
            section.offset, end
        ));
    }
    Ok(())
}

fn align_up(value: usize, alignment: usize) -> Result<usize, String> {
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

/// Small dependency-free IEEE CRC-32 used only to verify the IPAK's retained
/// 29-bit payload identity after decoding. This is not on the render/frame path.

#[cfg(test)]
mod tests {
    use super::*;

    fn put_u32(bytes: &mut [u8], offset: usize, value: u32) {
        bytes[offset..offset + 4].copy_from_slice(&value.to_le_bytes());
    }

    #[test]
    fn parses_minimal_little_endian_index_and_finds_exact_pair() {
        let mut bytes = vec![0u8; 0x90];
        let file_len = bytes.len() as u32;
        bytes[0..4].copy_from_slice(b"KAPI");
        put_u32(&mut bytes, 4, IPAK_VERSION);
        put_u32(&mut bytes, 8, file_len);
        put_u32(&mut bytes, 12, 2);
        // index section
        put_u32(&mut bytes, 16, IPAK_INDEX_SECTION);
        put_u32(&mut bytes, 20, 0x40);
        put_u32(&mut bytes, 24, 0x10);
        put_u32(&mut bytes, 28, 1);
        // data section
        put_u32(&mut bytes, 32, IPAK_DATA_SECTION);
        put_u32(&mut bytes, 36, 0x50);
        put_u32(&mut bytes, 40, 0x40);
        put_u32(&mut bytes, 44, 0);
        // index entry
        put_u32(&mut bytes, 0x40, 0x1122_3344);
        put_u32(&mut bytes, 0x44, 0xaabb_ccdd);
        put_u32(&mut bytes, 0x48, 0x08);
        put_u32(&mut bytes, 0x4c, 0x10);

        let index = T6IpakIndex::parse(PathBuf::from("synthetic.ipak"), &bytes).unwrap();
        let entry = index.find(0xaabb_ccdd, 0x1122_3344).unwrap();
        assert_eq!(entry.offset, 8);
        assert_eq!(index.absolute_entry_range(entry), (0x58, 0x68));
    }

    #[test]
    fn decodes_uncompressed_entry_and_verifies_crc29() {
        let payload = b"retail-t6-ipak-canary";
        let data_hash = super::retail_ipak_crc::crc32(payload) & DATA_HASH_MASK;
        let mut bytes = vec![0u8; 0x200];
        let file_len = bytes.len() as u32;
        bytes[0..4].copy_from_slice(b"KAPI");
        put_u32(&mut bytes, 4, IPAK_VERSION);
        put_u32(&mut bytes, 8, file_len);
        put_u32(&mut bytes, 12, 2);
        put_u32(&mut bytes, 16, IPAK_INDEX_SECTION);
        put_u32(&mut bytes, 20, 0x40);
        put_u32(&mut bytes, 24, 0x10);
        put_u32(&mut bytes, 28, 1);
        put_u32(&mut bytes, 32, IPAK_DATA_SECTION);
        put_u32(&mut bytes, 36, 0x80);
        put_u32(&mut bytes, 40, 0x180);
        put_u32(&mut bytes, 44, 0);
        // Entry begins at data section offset 0, and its serialized span includes
        // one 128-byte header plus the raw command payload.
        put_u32(&mut bytes, 0x40, data_hash);
        put_u32(&mut bytes, 0x44, 0x1234_5678);
        put_u32(&mut bytes, 0x48, 0);
        put_u32(&mut bytes, 0x4c, (DATA_BLOCK_BYTES + payload.len()) as u32);
        // countAndOffset: count=1, decoded file offset=0.
        put_u32(&mut bytes, 0x80, 1u32 << 24);
        // command 0: raw, size=payload.len().
        put_u32(&mut bytes, 0x84, payload.len() as u32);
        bytes[0x100..0x100 + payload.len()].copy_from_slice(payload);

        let index = T6IpakIndex::parse(PathBuf::from("synthetic.ipak"), &bytes).unwrap();
        let entry = index.find(0x1234_5678, data_hash).unwrap();
        let decoded = index.extract_entry_from_bytes(&bytes, entry).unwrap();
        assert_eq!(decoded, payload);
    }

    #[test]
    fn decodes_lzo_entry_with_shared_workspace_and_verifies_crc29() {
        // Standard liblzo2 LZO1X1 compressed representation of this string.
        let compressed: [u8; 21] = [
            34, 104, 101, 108, 108, 111, 44, 32, 108, 122, 111, 32,
            119, 111, 114, 108, 100, 33, 17, 0, 0,
        ];
        let expected = b"hello, lzo world!";
        let data_hash = super::retail_ipak_crc::crc32(expected) & DATA_HASH_MASK;
        let mut bytes = vec![0u8; 0x200];
        let length = bytes.len() as u32;
        bytes[0..4].copy_from_slice(b"KAPI");
        put_u32(&mut bytes, 4, IPAK_VERSION);
        put_u32(&mut bytes, 8, length);
        put_u32(&mut bytes, 12, 2);
        put_u32(&mut bytes, 16, IPAK_INDEX_SECTION);
        put_u32(&mut bytes, 20, 0x40);
        put_u32(&mut bytes, 24, 0x10);
        put_u32(&mut bytes, 28, 1);
        put_u32(&mut bytes, 32, IPAK_DATA_SECTION);
        put_u32(&mut bytes, 36, 0x80);
        put_u32(&mut bytes, 40, 0x180);
        put_u32(&mut bytes, 0x40, data_hash);
        put_u32(&mut bytes, 0x44, 0x1234_5678);
        put_u32(&mut bytes, 0x48, 0);
        put_u32(&mut bytes, 0x4c, (DATA_BLOCK_BYTES + compressed.len()) as u32);
        put_u32(&mut bytes, 0x80, 1 << 24);
        put_u32(&mut bytes, 0x84, (1 << 24) | compressed.len() as u32);
        bytes[0x100..0x100 + compressed.len()].copy_from_slice(&compressed);
        let index = T6IpakIndex::parse(PathBuf::from("synthetic-lzo.ipak"), &bytes).unwrap();
        let entry = index.find(0x1234_5678, data_hash).unwrap();
        assert_eq!(index.extract_entry_from_bytes(&bytes, entry).unwrap(), expected);
    }

    #[test]
    fn hash_is_case_insensitive_like_t6() {
        assert_eq!(t6_hash_string("Test", 0), t6_hash_string("test", 0));
    }
}
