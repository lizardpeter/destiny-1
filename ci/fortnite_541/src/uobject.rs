//! Bounded source-authored UE4.21 cooked package name/TOC recovery.
//! Fortnite 5.41 packages are commonly unversioned (-7 legacy summary).
//! This module does not guess actors, meshes, transforms or physics.
use std::str;

const MAGIC: u32 = 0x9E2A_83C1;
const MAX_NAME_COUNT: usize = 250_000;
const MAX_TEXT_BYTES: usize = 128 * 1024;

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct PackageSummary {
    pub total_header_size: u32,
    pub folder_name: String,
    pub flags: u32,
    pub unversioned: bool,
    pub name_count: u32,
    pub name_offset: u32,
    pub export_count: u32,
    pub export_offset: u32,
    pub import_count: u32,
    pub import_offset: u32,
    pub depends_offset: u32,
}

#[derive(Debug, Clone)]
pub struct PackageCatalog {
    pub summary: PackageSummary,
    pub names: Vec<String>,
}

struct Reader<'a> { data: &'a [u8], pos: usize }
impl<'a> Reader<'a> {
    fn at(data: &'a [u8], pos: usize) -> Result<Self, String> {
        if pos > data.len() { return Err("package offset exceeds source file".into()); }
        Ok(Self { data, pos })
    }
    fn bytes(&mut self, len: usize) -> Result<&'a [u8], String> {
        let end = self.pos.checked_add(len).ok_or("package field offset overflow")?;
        let bytes = self.data.get(self.pos..end).ok_or("truncated cooked package field")?;
        self.pos = end;
        Ok(bytes)
    }
    fn i32(&mut self) -> Result<i32, String> {
        Ok(i32::from_le_bytes(self.bytes(4)?.try_into().unwrap()))
    }
    fn u32(&mut self) -> Result<u32, String> {
        Ok(u32::from_le_bytes(self.bytes(4)?.try_into().unwrap()))
    }
    fn string(&mut self) -> Result<String, String> {
        let count = self.i32()?;
        if count == 0 { return Ok(String::new()); }
        if count > 0 {
            let length = usize::try_from(count).map_err(|_| "invalid name string length")?;
            if length > MAX_TEXT_BYTES { return Err("source name exceeds byte limit".into()); }
            let raw = self.bytes(length)?;
            if raw.last() != Some(&0) { return Err("non-terminated source name".into()); }
            return str::from_utf8(&raw[..length - 1])
                .map(|s| s.to_owned()).map_err(|_| "non-UTF8 source name".into());
        }
        let length = usize::try_from(count.checked_neg().ok_or("invalid UTF16 name length")?)
            .map_err(|_| "invalid UTF16 name length")?;
        if length > MAX_TEXT_BYTES / 2 { return Err("source UTF16 name exceeds byte limit".into()); }
        let raw = self.bytes(length.checked_mul(2).ok_or("UTF16 length overflow")?)?;
        if !raw.ends_with(&[0, 0]) { return Err("non-terminated UTF16 source name".into()); }
        let utf16 = raw[..raw.len() - 2].chunks_exact(2)
            .map(|pair| u16::from_le_bytes([pair[0], pair[1]]))
            .collect::<Vec<_>>();
        String::from_utf16(&utf16).map_err(|_| "invalid UTF16 source name".into())
    }
}

/// Recover source-authored package summaries and FName map for Fortnite 5.41.
/// The imported game uses UE4.21 unversioned cooked packages; FName serialized
/// entries contain an FString plus a pair of source hashing u16 fields.
pub fn inspect(bytes: &[u8]) -> Result<PackageCatalog, String> {
    let mut r = Reader::at(bytes, 0)?;
    if r.u32()? != MAGIC { return Err("not a little-endian UE4 package".into()); }
    let legacy = r.i32()?;
    if legacy != -7 {
        return Err(format!("unsupported UE4 package legacy summary {legacy}, expected -7"));
    }
    let _legacy_ue3 = r.i32()?;
    let file_ue4 = r.i32()?;
    let file_licensee = r.i32()?;
    let versions = r.i32()?;
    if versions != 0 {
        return Err(format!("UE4 custom-version table (count={versions}) not yet supported"));
    }
    let total_header_size = r.u32()?;
    if total_header_size as usize > bytes.len() {
        return Err("UE4 total header size escapes source .umap".into());
    }
    let folder_name = r.string()?;
    let flags = r.u32()?;
    let name_count = r.u32()?;
    let name_offset = r.u32()?;
    let _gatherable_text_count = r.u32()?;
    let _gatherable_text_offset = r.u32()?;
    let export_count = r.u32()?;
    let export_offset = r.u32()?;
    let import_count = r.u32()?;
    let import_offset = r.u32()?;
    let depends_offset = r.u32()?;
    let summary = PackageSummary {
        total_header_size, folder_name, flags,
        unversioned: file_ue4 == 0 && file_licensee == 0,
        name_count, name_offset, export_count, export_offset,
        import_count, import_offset, depends_offset,
    };
    if name_count as usize > MAX_NAME_COUNT ||
        [name_offset, export_offset, import_offset].iter().any(|v| *v as usize > bytes.len()) {
        return Err("invalid cooked name/import/export table limits".into());
    }
    let mut names_reader = Reader::at(bytes, name_offset as usize)?;
    let mut names = Vec::with_capacity(name_count as usize);
    for _ in 0..name_count {
        names.push(names_reader.string()?);
        names_reader.bytes(4)?; // FNameEntrySerialized non-case/case hash pair.
    }
    if (import_count != 0 && names_reader.pos > import_offset as usize) ||
        (export_count != 0 && names_reader.pos > export_offset as usize) {
        return Err("name map crosses source import/export table".into());
    }
    Ok(PackageCatalog { summary, names })
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn rejects_truncated_and_wrong_magic_packages() {
        assert!(inspect(&[]).is_err());
        assert!(inspect(&[0u8; 200]).is_err());
    }
    #[test]
    fn rejects_oversized_name_map() {
        let mut package = vec![0u8; 193];
        package[0..4].copy_from_slice(&MAGIC.to_le_bytes());
        package[4..8].copy_from_slice(&(-7i32).to_le_bytes());
        package[24..28].copy_from_slice(&193u32.to_le_bytes());
        package[28..32].copy_from_slice(&5i32.to_le_bytes());
        package[32..37].copy_from_slice(b"None\0");
        package[41..45].copy_from_slice(&u32::MAX.to_le_bytes());
        package[45..49].copy_from_slice(&193u32.to_le_bytes());
        assert!(inspect(&package).unwrap_err().contains("invalid cooked name"));
    }
}
