use std::{
    collections::{BTreeMap, HashMap},
    fs::File,
    io::{Read, Seek, SeekFrom},
    path::{Component, Path, PathBuf},
    sync::{Arc, Mutex},
};

#[cfg(windows)]
use std::sync::atomic::{AtomicUsize, Ordering};

use crate::{sha1, Error, Result};

pub const TIGER_VERSION: u16 = 24;
pub const LOGICAL_BLOCK_SIZE: usize = 0x40000;
pub const OODLE_RAW_QUANTUM: usize = 0x4000;
pub const FILE_ENTRY_STRIDE: usize = 16;
pub const BLOCK_ENTRY_STRIDE: usize = 32;
pub const NAMED_TAG_STRIDE: usize = 68;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Platform {
    Ps4,
    XboxOne,
}

impl Platform {
    pub fn code(self) -> u16 {
        match self {
            Self::Ps4 => 7,
            Self::XboxOne => 8,
        }
    }
}

#[derive(Clone, Debug)]
pub struct TigerHeader {
    pub version: u16,
    pub platform: Platform,
    pub package_id: u16,
    pub unknown_06: u16,
    pub unknown_08: u64,
    pub build_time_raw: u64,
    pub build_id_raw: u32,
    pub version_major: u16,
    pub version_minor: u16,
    pub patch_id: u16,
    pub language_code: u16,
    pub tool_string: String,
    pub unknown_a4: u32,
    pub unknown_a8: u32,
    pub unknown_ac: u32,
    pub header_signature_offset: u32,
    pub file_entry_count: u32,
    pub file_entry_table_offset: u32,
    pub file_entry_table_sha1: [u8; 20],
    pub block_entry_count: u32,
    pub block_entry_table_offset: u32,
    pub block_entry_table_sha1: [u8; 20],
    pub named_tag_count: u32,
    pub named_tag_table_offset: u32,
    pub named_tag_table_sha1: [u8; 20],
    pub package_file_size: u32,
}

#[derive(Clone, Debug)]
pub struct TigerFileEntry {
    pub index: usize,
    pub tag_hash: u32,
    pub reference: u32,
    pub entry_b: u32,
    pub file_type: u8,
    pub file_subtype: u8,
    pub metadata_16_23: u8,
    pub starting_block: usize,
    pub starting_block_offset: usize,
    pub file_size: usize,
}

#[derive(Clone, Debug)]
pub struct TigerBlockEntry {
    pub index: usize,
    pub offset: u32,
    pub size: u32,
    pub patch_id: u16,
    pub flags: u16,
    pub sha1: [u8; 20],
}

impl TigerBlockEntry {
    #[inline]
    pub fn compressed(&self) -> bool {
        self.flags & 0x1 != 0
    }

    #[inline]
    pub fn encrypted(&self) -> bool {
        self.flags & 0x2 != 0
    }

    #[inline]
    pub fn alternate_key(&self) -> bool {
        self.flags & 0x4 != 0
    }

    #[inline]
    pub fn unknown_0x8(&self) -> bool {
        self.flags & 0x8 != 0
    }
}

#[derive(Clone, Debug)]
pub struct TigerNamedTag {
    pub index: usize,
    pub tag_hash: u32,
    pub class_hash: u32,
    pub name: String,
}

pub trait TigerBlockDecompressor {
    fn decompress_exact(&self, stored: &[u8], raw_len: usize) -> Result<Vec<u8>>;
}

/// Source-neutral Tiger block adapter backed by the clean-room legacy Oodle
/// 2.3 LZH implementation. Each call owns its decoding state, so independent
/// blocks may safely be decoded on different threads by higher-level callers.
/// Unsupported Oodle codec families fail closed rather than trying to decode
/// a different stream as LZH.
#[derive(Clone, Copy, Debug, Default)]
pub struct NativeLzhDecompressor;

impl TigerBlockDecompressor for NativeLzhDecompressor {
    fn decompress_exact(&self, stored: &[u8], raw_len: usize) -> Result<Vec<u8>> {
        if stored.is_empty() || raw_len == 0 || raw_len > LOGICAL_BLOCK_SIZE {
            return Err(Error::Invalid(format!(
                "invalid native Oodle LZH block sizes: stored {}, raw {} (capacity {})",
                stored.len(), raw_len, LOGICAL_BLOCK_SIZE,
            )));
        }
        d1_oodle3::lzh::decode_stream(stored, raw_len).map_err(|error| {
            Error::Unsupported(format!(
                "native Rust Oodle 2.3 LZH decode refused this block ({} input bytes, {} output bytes): {error}",
                stored.len(), raw_len
            ))
        })
    }
}

/// Default active-map Tiger working set. This is RAM-only and is owned by one
/// Destiny1Archive; dropping the map drops the cache. It is deliberately small
/// enough to be a working set rather than a second copy of the game archive.
pub(crate) const DEFAULT_BLOCK_CACHE_BYTES: usize = 64 * 1024 * 1024;

#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
struct TigerBlockCacheKey {
    package_id: u16,
    snapshot_patch_id: u16,
    block_index: usize,
}

#[derive(Debug)]
struct TigerCachedBlock {
    bytes: Arc<[u8]>,
    last_used: u64,
}

#[derive(Debug)]
pub(crate) struct TigerBlockCache {
    max_bytes: usize,
    current_bytes: usize,
    clock: u64,
    entries: HashMap<TigerBlockCacheKey, TigerCachedBlock>,
}

impl TigerBlockCache {
    pub(crate) fn new(max_bytes: usize) -> Self {
        Self {
            max_bytes,
            current_bytes: 0,
            clock: 0,
            entries: HashMap::new(),
        }
    }

    fn get(&mut self, key: TigerBlockCacheKey) -> Option<Arc<[u8]>> {
        self.clock = self.clock.wrapping_add(1);
        let entry = self.entries.get_mut(&key)?;
        entry.last_used = self.clock;
        Some(Arc::clone(&entry.bytes))
    }

    fn insert(&mut self, key: TigerBlockCacheKey, bytes: Arc<[u8]>) {
        let len = bytes.len();
        if self.max_bytes == 0 || len > self.max_bytes {
            return;
        }
        self.clock = self.clock.wrapping_add(1);
        if let Some(previous) = self.entries.remove(&key) {
            self.current_bytes = self.current_bytes.saturating_sub(previous.bytes.len());
        }
        self.current_bytes = self.current_bytes.saturating_add(len);
        self.entries.insert(
            key,
            TigerCachedBlock {
                bytes,
                last_used: self.clock,
            },
        );
        while self.current_bytes > self.max_bytes {
            let Some((&oldest_key, _)) = self.entries.iter().min_by_key(|(_, value)| value.last_used)
            else {
                break;
            };
            if let Some(oldest) = self.entries.remove(&oldest_key) {
                self.current_bytes = self.current_bytes.saturating_sub(oldest.bytes.len());
            }
        }
    }
}

#[derive(Clone, Debug)]
struct TigerTarMemberLocation {
    path: PathBuf,
    data_offset: u64,
    size: u64,
}

/// Read-only index of package members inside one uncompressed TAR container.
///
/// The index retains TAR byte offsets and sizes and read-only file handles.
/// Package data is never unpacked, rewritten, or cached. Range requests use
/// positioned reads on Unix, and independent short-locked handles on Windows.
#[derive(Debug)]
pub(crate) struct TigerTarIndex {
    tar_path: PathBuf,
    members: BTreeMap<PathBuf, TigerTarMemberLocation>,
    #[cfg(unix)]
    source_file: File,
    #[cfg(windows)]
    source_files: Vec<Mutex<File>>,
    #[cfg(windows)]
    next_source_file: AtomicUsize,
}

impl TigerTarIndex {
    pub(crate) fn open(path: impl AsRef<Path>) -> Result<Self> {
        let tar_path = path.as_ref().to_path_buf();
        if !tar_path.is_file() {
            return Err(Error::Invalid(format!(
                "D1 TAR container does not exist or is not a file: {}",
                tar_path.display()
            )));
        }

        let source_file = File::open(&tar_path)?;
        let tar_size = source_file.metadata()?.len();
        // Scan through an independent handle; retain the original read-only
        // handle for all later exact member reads.
        let mut archive = tar::Archive::new(File::open(&tar_path)?);
        let mut members = BTreeMap::<PathBuf, TigerTarMemberLocation>::new();
        let entries = archive.entries_with_seek().map_err(|error| {
            Error::IoContext(
                format!("reading D1 TAR directory {}", tar_path.display()),
                error,
            )
        })?;

        for entry in entries {
            let entry = entry.map_err(|error| {
                Error::IoContext(
                    format!("walking D1 TAR directory {}", tar_path.display()),
                    error,
                )
            })?;
            if !entry.header().entry_type().is_file() {
                continue;
            }
            let path = normalize_tar_member_path(entry.path()?.as_ref())?;
            if !is_tiger_package_filename(&path) {
                continue;
            }
            let size = entry.size();
            let data_offset = entry.raw_file_position();
            let end = data_offset.checked_add(size).ok_or_else(|| {
                Error::Invalid(format!(
                    "D1 TAR member {} has an overflowing byte range",
                    path.display()
                ))
            })?;
            if end > tar_size {
                return Err(Error::Invalid(format!(
                    "D1 TAR member {} byte range {data_offset:#x}..{end:#x} exceeds container size {tar_size:#x}",
                    path.display()
                )));
            }
            if members
                .insert(
                    path.clone(),
                    TigerTarMemberLocation {
                        path: path.clone(),
                        data_offset,
                        size,
                    },
                )
                .is_some()
            {
                return Err(Error::Invalid(format!(
                    "D1 TAR {} contains duplicate package member {}; package ownership would be ambiguous",
                    tar_path.display(),
                    path.display()
                )));
            }
        }

        if members.is_empty() {
            return Err(Error::Invalid(format!(
                "D1 TAR {} contains no .pkg or .pkg.bin members",
                tar_path.display()
            )));
        }

        #[cfg(windows)]
        let source_files = {
            let mut handles = vec![Mutex::new(source_file)];
            // Bound resource use even with thousands of logical block readers.
            // Each Windows handle has an independent seek cursor. If opening
            // additional handles fails, the first remains sufficient.
            for _ in 1..4 {
                match File::open(&tar_path) {
                    Ok(file) => handles.push(Mutex::new(file)),
                    Err(_) => break,
                }
            }
            handles
        };
        Ok(Self {
            tar_path,
            members,
            #[cfg(unix)]
            source_file,
            #[cfg(windows)]
            source_files,
            #[cfg(windows)]
            next_source_file: AtomicUsize::new(0),
        })
    }

    #[inline]
    pub(crate) fn tar_path(&self) -> &Path {
        &self.tar_path
    }

    pub(crate) fn package_members(&self) -> Vec<PathBuf> {
        self.members.keys().cloned().collect()
    }

    #[inline]
    fn contains_member(&self, path: &Path) -> bool {
        self.members.contains_key(path)
    }

    fn member_size(&self, path: &Path) -> Result<u64> {
        self.members
            .get(path)
            .map(|member| member.size)
            .ok_or_else(|| {
                Error::Invalid(format!(
                    "D1 TAR {} has no package member {}",
                    self.tar_path.display(),
                    path.display()
                ))
            })
    }

    fn read_member_range(&self, path: &Path, offset: u64, len: usize) -> Result<Vec<u8>> {
        let member = self.members.get(path).ok_or_else(|| {
            Error::Invalid(format!(
                "D1 TAR {} has no package member {}",
                self.tar_path.display(),
                path.display()
            ))
        })?;
        let end = offset.checked_add(len as u64).ok_or_else(|| {
            Error::Invalid(format!(
                "D1 TAR member {} read range overflow",
                member.path.display()
            ))
        })?;
        if end > member.size {
            return Err(Error::Invalid(format!(
                "D1 TAR member {} read {offset:#x}..{end:#x} exceeds member size {:#x}",
                member.path.display(),
                member.size
            )));
        }
        let absolute = member.data_offset.checked_add(offset).ok_or_else(|| {
            Error::Invalid(format!(
                "D1 TAR member {} absolute read offset overflow",
                member.path.display()
            ))
        })?;
        let mut bytes = Vec::new();
        bytes.try_reserve_exact(len).map_err(|error| {
            Error::Invalid(format!(
                "D1 TAR member {} refused {len} byte allocation: {error}",
                member.path.display()
            ))
        })?;
        bytes.resize(len, 0);

        #[cfg(unix)]
        {
            use std::os::unix::fs::FileExt;
            let mut consumed = 0usize;
            while consumed < bytes.len() {
                match self.source_file.read_at(&mut bytes[consumed..], absolute + consumed as u64) {
                    Ok(0) => return Err(Error::IoContext(
                        format!("reading D1 TAR {} at {absolute:#x}", self.tar_path.display()),
                        std::io::Error::from(std::io::ErrorKind::UnexpectedEof),
                    )),
                    Ok(n) => consumed += n,
                    Err(error) if error.kind() == std::io::ErrorKind::Interrupted => continue,
                    Err(error) => return Err(Error::IoContext(
                        format!("reading D1 TAR {} at {absolute:#x}", self.tar_path.display()),
                        error,
                    )),
                }
            }
        }
        #[cfg(windows)]
        {
            let slot = self.next_source_file.fetch_add(1, Ordering::Relaxed)
                % self.source_files.len();
            let mut file = self.source_files[slot].lock().map_err(|_| {
                Error::Invalid(format!(
                    "read-only D1 TAR {} handle lock was poisoned",
                    self.tar_path.display()
                ))
            })?;
            file.seek(SeekFrom::Start(absolute))?;
            file.read_exact(&mut bytes)?;
        }
        #[cfg(not(any(unix, windows)))]
        {
            let mut file = File::open(&self.tar_path)?;
            file.seek(SeekFrom::Start(absolute))?;
            file.read_exact(&mut bytes)?;
        }
        Ok(bytes)
    }
}

/// Package block reads are source-exact and immutable for an import session.
/// Retain at most eight distinct physical patch files per TigerPackage rather
/// than opening and closing one file for every 0x40000-byte logical block.
const MAX_RETAINED_PACKAGE_FILES: usize = 8;

#[derive(Debug, Default)]
struct TigerFileRangeCache {
    handles: Mutex<HashMap<PathBuf, Arc<TigerFileReader>>>,
}

#[derive(Debug)]
struct TigerFileReader {
    #[cfg(unix)]
    file: File,
    #[cfg(windows)]
    files: Vec<Mutex<File>>,
    #[cfg(windows)]
    next_file: AtomicUsize,
    #[cfg(not(any(unix, windows)))]
    file: Mutex<File>,
}

impl TigerFileReader {
    fn new(path: &Path) -> Result<Self> {
        let file = File::open(path).map_err(|error| {
            Error::IoContext(format!("opening D1 package {}", path.display()), error)
        })?;
        #[cfg(windows)]
        let files = {
            let mut pool = vec![Mutex::new(file)];
            // This small pool is local to this patch file, and opening extra
            // handles is opportunistic: one is enough for correct operation.
            for _ in 1..4 {
                match File::open(path) {
                    Ok(extra) => pool.push(Mutex::new(extra)),
                    Err(_) => break,
                }
            }
            pool
        };
        Ok(Self {
            #[cfg(unix)]
            file,
            #[cfg(windows)]
            files,
            #[cfg(windows)]
            next_file: AtomicUsize::new(0),
            #[cfg(not(any(unix, windows)))]
            file: Mutex::new(file),
        })
    }

    fn read_range(&self, path: &Path, offset: u64, len: usize) -> Result<Vec<u8>> {
        #[cfg(unix)]
        let size = self.file.metadata()?.len();
        #[cfg(windows)]
        let size = {
            let guard = self.files[0].lock().map_err(|_| {
                Error::Invalid(format!("D1 package {} file lock poisoned", path.display()))
            })?;
            guard.metadata()?.len()
        };
        #[cfg(not(any(unix, windows)))]
        let size = {
            let guard = self.file.lock().map_err(|_| {
                Error::Invalid(format!("D1 package {} file lock poisoned", path.display()))
            })?;
            guard.metadata()?.len()
        };
        let end = offset.checked_add(len as u64).ok_or_else(|| {
            Error::Invalid(format!("D1 package {} read range overflow", path.display()))
        })?;
        if end > size {
            return Err(Error::Invalid(format!(
                "D1 package {} read {offset:#x}..{end:#x} exceeds file size {size:#x}",
                path.display()
            )));
        }
        let mut bytes = Vec::new();
        bytes.try_reserve_exact(len).map_err(|error| {
            Error::Invalid(format!(
                "D1 package {} refused {len} byte allocation for read at {offset:#x}: {error}",
                path.display()
            ))
        })?;
        bytes.resize(len, 0);
        #[cfg(unix)]
        {
            use std::os::unix::fs::FileExt;
            let mut consumed = 0usize;
            while consumed < bytes.len() {
                match self.file.read_at(&mut bytes[consumed..], offset + consumed as u64) {
                    Ok(0) => return Err(Error::IoContext(
                        format!("reading D1 package {} at {offset:#x}", path.display()),
                        std::io::Error::from(std::io::ErrorKind::UnexpectedEof),
                    )),
                    Ok(n) => consumed += n,
                    Err(error) if error.kind() == std::io::ErrorKind::Interrupted => continue,
                    Err(error) => return Err(Error::IoContext(
                        format!("reading D1 package {} at {offset:#x}", path.display()), error
                    )),
                }
            }
        }
        #[cfg(windows)]
        {
            let slot = self.next_file.fetch_add(1, Ordering::Relaxed) % self.files.len();
            let mut file = self.files[slot].lock().map_err(|_| {
                Error::Invalid(format!("D1 package {} file lock poisoned", path.display()))
            })?;
            file.seek(SeekFrom::Start(offset))?;
            file.read_exact(&mut bytes)?;
        }
        #[cfg(not(any(unix, windows)))]
        {
            let mut file = self.file.lock().map_err(|_| {
                Error::Invalid(format!("D1 package {} file lock poisoned", path.display()))
            })?;
            file.seek(SeekFrom::Start(offset))?;
            file.read_exact(&mut bytes)?;
        }
        Ok(bytes)
    }
}

impl TigerFileRangeCache {
    fn read_range(&self, path: &Path, offset: u64, len: usize) -> Result<Vec<u8>> {
        let reader = {
            let mut cached = self.handles.lock().map_err(|_| {
                Error::Invalid("D1 package file-handle cache lock poisoned".to_owned())
            })?;
            if let Some(reader) = cached.get(path) {
                Some(Arc::clone(reader))
            } else if cached.len() >= MAX_RETAINED_PACKAGE_FILES {
                // Bound persistent Windows handle use. Even when there are
                // more than eight patch owners, the original path remains.
                None
            } else {
                let reader = Arc::new(TigerFileReader::new(path)?);
                cached.insert(path.to_path_buf(), Arc::clone(&reader));
                Some(reader)
            }
        };
        match reader {
            Some(reader) => reader.read_range(path, offset, len),
            None => read_file_range(path, offset, len),
        }
    }
}

#[derive(Clone, Debug)]
enum TigerPackageStorage {
    File { path: PathBuf, ranges: Arc<TigerFileRangeCache> },
    TarMember {
        index: Arc<TigerTarIndex>,
        member_path: PathBuf,
    },
}

impl TigerPackageStorage {
    fn logical_path(&self) -> &Path {
        match self {
            Self::File { path, .. } => path,
            Self::TarMember { member_path, .. } => member_path,
        }
    }

    fn actual_size(&self) -> Result<u64> {
        match self {
            Self::File { path, .. } => Ok(File::open(path)?.metadata()?.len()),
            Self::TarMember { index, member_path } => index.member_size(member_path),
        }
    }

    fn read_self_range(&self, offset: u64, len: usize) -> Result<Vec<u8>> {
        match self {
            Self::File { path, ranges } => ranges.read_range(path, offset, len),
            Self::TarMember { index, member_path } => {
                index.read_member_range(member_path, offset, len)
            }
        }
    }

    fn sibling_exists(&self, path: &Path) -> bool {
        match self {
            Self::File { .. } => path.is_file(),
            Self::TarMember { index, .. } => index.contains_member(path),
        }
    }

    fn read_sibling_range(&self, path: &Path, offset: u64, len: usize) -> Result<Vec<u8>> {
        match self {
            Self::File { ranges, .. } => ranges.read_range(path, offset, len),
            Self::TarMember { index, .. } => index.read_member_range(path, offset, len),
        }
    }

    fn describe_member(&self, path: &Path) -> String {
        match self {
            Self::File { .. } => path.display().to_string(),
            Self::TarMember { index, .. } => {
                format!("{}!{}", index.tar_path().display(), path.display())
            }
        }
    }
}

#[derive(Debug)]
pub struct TigerPackage {
    path: PathBuf,
    storage: TigerPackageStorage,
    header: TigerHeader,
    entries: Vec<TigerFileEntry>,
    blocks: Vec<TigerBlockEntry>,
    named_tags: Vec<TigerNamedTag>,
    block_used_end: Vec<usize>,
    // Optional because standalone package readers remain uncached. Archives
    // attach one shared, bounded cache across all package snapshots for the
    // active map only.
    block_cache: Option<Arc<Mutex<TigerBlockCache>>>,
}

impl TigerPackage {
    pub fn open(path: impl AsRef<Path>) -> Result<Self> {
        let path = path.as_ref().to_path_buf();
        Self::open_storage(TigerPackageStorage::File {
            path,
            ranges: Arc::new(TigerFileRangeCache::default()),
        })
    }

    pub(crate) fn open_tar_member(
        index: Arc<TigerTarIndex>,
        member_path: impl AsRef<Path>,
    ) -> Result<Self> {
        let member_path = normalize_tar_member_path(member_path.as_ref())?;
        if !index.contains_member(&member_path) {
            return Err(Error::Invalid(format!(
                "D1 TAR {} has no indexed package member {}",
                index.tar_path().display(),
                member_path.display()
            )));
        }
        Self::open_storage(TigerPackageStorage::TarMember { index, member_path })
    }

    fn open_storage(storage: TigerPackageStorage) -> Result<Self> {
        let path = storage.logical_path().to_path_buf();
        let actual_size = storage.actual_size()?;
        let header_bytes = storage.read_self_range(0, 0x140)?;
        let header = parse_header(&header_bytes)?;

        if header.version != TIGER_VERSION {
            return Err(Error::Invalid(format!(
                "{} is Tiger version {}, expected proven D1 v{}",
                storage.describe_member(&path),
                header.version,
                TIGER_VERSION
            )));
        }
        if header.package_file_size as u64 != actual_size {
            return Err(Error::Invalid(format!(
                "{} header file size {} does not match actual size {}",
                storage.describe_member(&path),
                header.package_file_size,
                actual_size
            )));
        }

        let entry_bytes = read_table(
            &storage,
            actual_size,
            header.file_entry_table_offset,
            header.file_entry_count,
            FILE_ENTRY_STRIDE,
            "file-entry",
        )?;
        validate_table_sha1(
            &entry_bytes,
            &header.file_entry_table_sha1,
            false,
            "file-entry",
        )?;

        let block_bytes = read_table(
            &storage,
            actual_size,
            header.block_entry_table_offset,
            header.block_entry_count,
            BLOCK_ENTRY_STRIDE,
            "block-entry",
        )?;
        validate_table_sha1(
            &block_bytes,
            &header.block_entry_table_sha1,
            false,
            "block-entry",
        )?;

        let named_bytes = read_table(
            &storage,
            actual_size,
            header.named_tag_table_offset,
            header.named_tag_count,
            NAMED_TAG_STRIDE,
            "named-tag",
        )?;
        validate_table_sha1(
            &named_bytes,
            &header.named_tag_table_sha1,
            header.named_tag_count == 0,
            "named-tag",
        )?;

        let entries = parse_entries(&entry_bytes, header.package_id);
        let blocks = parse_blocks(&block_bytes);
        let named_tags = parse_named_tags(&named_bytes);
        validate_entry_spans(&entries, blocks.len())?;
        let block_used_end = compute_block_usage(&entries, blocks.len());

        Ok(Self {
            path,
            storage,
            header,
            entries,
            blocks,
            named_tags,
            block_used_end,
            block_cache: None,
        })
    }

    #[inline]
    pub fn path(&self) -> &Path {
        &self.path
    }

    #[inline]
    pub fn header(&self) -> &TigerHeader {
        &self.header
    }

    #[inline]
    pub fn entries(&self) -> &[TigerFileEntry] {
        &self.entries
    }

    #[inline]
    pub fn blocks(&self) -> &[TigerBlockEntry] {
        &self.blocks
    }

    #[inline]
    pub fn named_tags(&self) -> &[TigerNamedTag] {
        &self.named_tags
    }

    pub(crate) fn attach_block_cache(&mut self, cache: Arc<Mutex<TigerBlockCache>>) {
        self.block_cache = Some(cache);
    }

    pub fn entry_by_tag_hash(&self, tag_hash: u32) -> Option<&TigerFileEntry> {
        let (package_id, entry_index) = split_tag_hash(tag_hash)?;
        if package_id != self.header.package_id || entry_index >= self.entries.len() {
            return None;
        }
        let entry = &self.entries[entry_index];
        (entry.tag_hash == tag_hash).then_some(entry)
    }

    pub fn expected_raw_block_len(&self, block_index: usize) -> Result<usize> {
        let used = *self.block_used_end.get(block_index).ok_or_else(|| {
            Error::Invalid(format!("D1 block index {block_index} is out of range"))
        })?;
        if used == 0 {
            return Ok(LOGICAL_BLOCK_SIZE);
        }
        let aligned = align_up(used, OODLE_RAW_QUANTUM)?;
        Ok(aligned.min(LOGICAL_BLOCK_SIZE))
    }

    pub fn entry_available(&self, entry_index: usize) -> Result<bool> {
        let entry = self.entries.get(entry_index).ok_or_else(|| {
            Error::Invalid(format!("D1 entry index {entry_index} is out of range"))
        })?;
        for block_index in entry_block_range(entry) {
            let block = &self.blocks[block_index];
            let owner = patch_path(&self.path, block.patch_id);
            if !self.storage.sibling_exists(&owner) {
                return Ok(false);
            }
        }
        Ok(true)
    }

    pub fn read_entry(
        &self,
        entry_index: usize,
        decompressor: Option<&dyn TigerBlockDecompressor>,
    ) -> Result<Vec<u8>> {
        self.read_entry_impl(entry_index, decompressor, false)
    }

    /// Decode separate Tiger blocks concurrently using only the native LZH
    /// backend. Every worker owns its decoder state and reads an independently
    /// addressable, SHA-1-verified physical block; the original block order is
    /// restored before reconstructing the FileEntry. Small entries remain
    /// sequential. RUST_TEST_D1_BLOCK_THREADS=1 disables parallelism.
    pub fn read_entry_native_parallel(&self, entry_index: usize) -> Result<Vec<u8>> {
        let native = NativeLzhDecompressor;
        self.read_entry_impl(entry_index, Some(&native), true)
    }

    fn read_entry_impl(
        &self,
        entry_index: usize,
        decompressor: Option<&dyn TigerBlockDecompressor>,
        native_parallel: bool,
    ) -> Result<Vec<u8>> {
        let entry = self.entries.get(entry_index).ok_or_else(|| {
            Error::Invalid(format!("D1 entry index {entry_index} is out of range"))
        })?;
        if entry.file_size == 0 {
            return Ok(Vec::new());
        }

        let indices = entry_block_range(entry);
        let max_threads = if native_parallel && indices.len() >= 8 {
            std::thread::available_parallelism().map(|n| n.get()).unwrap_or(1).min(8)
        } else {
            1
        };
        let workers = std::env::var("RUST_TEST_D1_BLOCK_THREADS")
            .ok()
            .and_then(|raw| raw.parse::<usize>().ok())
            .unwrap_or(max_threads)
            .clamp(1, max_threads);

        let blocks: Vec<Arc<[u8]>> = if workers > 1 {
            // Scoped workers borrow this read-only package and share only its
            // bounded, synchronized block cache. The decompressor is a fresh
            // native decoder per block, not a shared mutable FFI runtime.
            std::thread::scope(|scope| {
                let chunk_size = (indices.len() + workers - 1) / workers;
                let mut tasks = Vec::new();
                for first in (indices.start..indices.end).step_by(chunk_size) {
                    let last = first.saturating_add(chunk_size).min(indices.end);
                    tasks.push(scope.spawn(move || {
                        let native = NativeLzhDecompressor;
                        (first..last)
                            .map(|block_index| self.read_logical_block(block_index, Some(&native)))
                            .collect::<Result<Vec<Arc<[u8]>>>>()
                    }));
                }
                let mut ordered = Vec::with_capacity(indices.len());
                for task in tasks {
                    let part = task.join().map_err(|_| {
                        Error::Invalid("native D1 Tiger decode worker panicked".to_owned())
                    })??;
                    ordered.extend(part);
                }
                Ok::<Vec<Arc<[u8]>>, Error>(ordered)
            })?
        } else {
            indices
                .map(|block_index| self.read_logical_block(block_index, decompressor))
                .collect::<Result<Vec<_>>>()?
        };

        let mut remaining = entry.file_size;
        let mut block_offset = entry.starting_block_offset;
        let mut output = Vec::new();
        output.try_reserve_exact(entry.file_size).map_err(|error| {
            Error::Invalid(format!(
                "D1 entry {} ({:08X}) in package {:04X} refused {} byte allocation: {error}",
                entry.index, entry.tag_hash, self.header.package_id, entry.file_size,
            ))
        })?;
        for block in blocks {
            let take = remaining.min(LOGICAL_BLOCK_SIZE - block_offset);
            output.extend_from_slice(&block[block_offset..block_offset + take]);
            remaining -= take;
            block_offset = 0;
        }
        if output.len() != entry.file_size {
            return Err(Error::Invalid(format!(
                "D1 entry {} reconstructed {} bytes, expected {}",
                entry.index, output.len(), entry.file_size
            )));
        }
        Ok(output)
    }

    fn read_logical_block(
        &self,
        block_index: usize,
        decompressor: Option<&dyn TigerBlockDecompressor>,
    ) -> Result<Arc<[u8]>> {
        let cache_key = TigerBlockCacheKey {
            package_id: self.header.package_id,
            snapshot_patch_id: self.header.patch_id,
            block_index,
        };
        if let Some(cache) = self.block_cache.as_ref() {
            if let Ok(mut cache) = cache.lock() {
                if let Some(bytes) = cache.get(cache_key) {
                    return Ok(bytes);
                }
            }
        }

        let block = self.blocks.get(block_index).ok_or_else(|| {
            Error::Invalid(format!("D1 block index {block_index} is out of range"))
        })?;
        if block.encrypted() {
            return Err(Error::Unsupported(format!(
                "D1 block {block_index} is encrypted (flags {:#x}); D1 encryption is not source-closed in the Rust runtime yet",
                block.flags
            )));
        }
        if block.unknown_0x8() || block.flags & !0x000f != 0 {
            return Err(Error::Unsupported(format!(
                "D1 block {block_index} uses unsupported flags {:#x}",
                block.flags
            )));
        }

        let owner = patch_path(&self.path, block.patch_id);
        let stored = self
            .storage
            .read_sibling_range(&owner, block.offset as u64, block.size as usize)
            .map_err(|error| {
                Error::Invalid(format!(
                    "D1 logical block {block_index} belongs to patch {} at {} but could not be read: {error}",
                    block.patch_id,
                    self.storage.describe_member(&owner)
                ))
            })?;
        let actual_sha1 = sha1::digest(&stored);
        if actual_sha1 != block.sha1 {
            return Err(Error::Invalid(format!(
                "D1 stored block {block_index} SHA-1 mismatch in {}: expected {}, got {}",
                self.storage.describe_member(&owner),
                hex20(&block.sha1),
                hex20(&actual_sha1)
            )));
        }

        let mut decoded = if block.compressed() {
            let decompressor = decompressor.ok_or_else(|| {
                Error::Unsupported(format!(
                    "D1 block {block_index} is Oodle-3 compressed but no Oodle runtime is configured"
                ))
            })?;
            let expected = self.expected_raw_block_len(block_index)?;
            let decoded = decompressor.decompress_exact(&stored, expected)?;
            if decoded.len() != expected {
                return Err(Error::Invalid(format!(
                    "D1 Oodle block {block_index} decoded {} bytes, expected exact source-derived length {}",
                    decoded.len(),
                    expected
                )));
            }
            decoded
        } else {
            stored
        };

        if decoded.len() > LOGICAL_BLOCK_SIZE {
            return Err(Error::Invalid(format!(
                "D1 block {block_index} decoded to {} bytes, beyond logical capacity {}",
                decoded.len(),
                LOGICAL_BLOCK_SIZE
            )));
        }
        decoded.resize(LOGICAL_BLOCK_SIZE, 0);
        let decoded: Arc<[u8]> = decoded.into();
        if let Some(cache) = self.block_cache.as_ref() {
            if let Ok(mut cache) = cache.lock() {
                cache.insert(cache_key, Arc::clone(&decoded));
            }
        }
        Ok(decoded)
    }
}

#[inline]
pub fn tag_hash(package_id: u16, entry_index: usize) -> u32 {
    (0x8080_0000u64
        .wrapping_add((package_id as u64) << 13)
        .wrapping_add((entry_index % 8192) as u64)) as u32
}

pub fn split_tag_hash(hash: u32) -> Option<(u16, usize)> {
    if hash < 0x8080_0000 {
        return None;
    }
    let delta = hash.wrapping_sub(0x8080_0000);
    Some(((delta >> 13) as u16, (delta & 0x1fff) as usize))
}

pub fn patch_path(current: &Path, patch_id: u16) -> PathBuf {
    let Some(name) = current.file_name().and_then(|value| value.to_str()) else {
        return current.to_path_buf();
    };
    let suffix = if name.to_ascii_lowercase().ends_with(".pkg.bin") {
        ".pkg.bin"
    } else if name.to_ascii_lowercase().ends_with(".pkg") {
        ".pkg"
    } else {
        return current.to_path_buf();
    };
    let stem = &name[..name.len() - suffix.len()];
    let Some(underscore) = stem.rfind('_') else {
        return current.to_path_buf();
    };
    if stem[underscore + 1..].is_empty()
        || !stem[underscore + 1..].bytes().all(|byte| byte.is_ascii_digit())
    {
        return current.to_path_buf();
    }
    current.with_file_name(format!("{}_{}{}", &stem[..underscore], patch_id, suffix))
}

fn normalize_tar_member_path(path: &Path) -> Result<PathBuf> {
    let mut normalized = PathBuf::new();
    for component in path.components() {
        match component {
            Component::CurDir => {}
            Component::Normal(value) => normalized.push(value),
            Component::ParentDir | Component::RootDir | Component::Prefix(_) => {
                return Err(Error::Invalid(format!(
                    "D1 TAR member path {} is not a safe relative path",
                    path.display()
                )))
            }
        }
    }
    if normalized.as_os_str().is_empty() {
        return Err(Error::Invalid("D1 TAR member has an empty path".to_owned()));
    }
    Ok(normalized)
}

fn read_file_range(path: &Path, offset: u64, len: usize) -> Result<Vec<u8>> {
    let mut file = File::open(path).map_err(|error| {
        Error::IoContext(format!("opening D1 package {}", path.display()), error)
    })?;
    let size = file.metadata()?.len();
    let end = offset.checked_add(len as u64).ok_or_else(|| {
        Error::Invalid(format!("D1 package {} read range overflow", path.display()))
    })?;
    if end > size {
        return Err(Error::Invalid(format!(
            "D1 package {} read {offset:#x}..{end:#x} exceeds file size {size:#x}",
            path.display()
        )));
    }
    file.seek(SeekFrom::Start(offset))?;
    let mut bytes = Vec::new();
    bytes.try_reserve_exact(len).map_err(|error| {
        Error::Invalid(format!(
            "D1 package {} refused {len} byte allocation for read at {offset:#x}: {error}",
            path.display()
        ))
    })?;
    bytes.resize(len, 0);
    file.read_exact(&mut bytes)?;
    Ok(bytes)
}

fn parse_header(bytes: &[u8]) -> Result<TigerHeader> {
    if bytes.len() < 0x140 {
        return Err(Error::Invalid(format!(
            "D1 Tiger header is {} bytes, expected at least 0x140",
            bytes.len()
        )));
    }

    let platform_code = u16_at(bytes, 0x02);
    let platform = match platform_code {
        7 => Platform::Ps4,
        8 => Platform::XboxOne,
        other => {
            return Err(Error::Unsupported(format!(
                "D1 Tiger platform code {other} is not PS4 (7) or Xbox One (8)"
            )))
        }
    };

    Ok(TigerHeader {
        version: u16_at(bytes, 0x00),
        platform,
        package_id: u16_at(bytes, 0x04),
        unknown_06: u16_at(bytes, 0x06),
        unknown_08: u64_at(bytes, 0x08),
        build_time_raw: u64_at(bytes, 0x10),
        build_id_raw: u32_at(bytes, 0x18),
        version_major: u16_at(bytes, 0x1c),
        version_minor: u16_at(bytes, 0x1e),
        patch_id: u16_at(bytes, 0x20),
        language_code: u16_at(bytes, 0x22),
        tool_string: decode_cstr(&bytes[0x24..0xa4]),
        unknown_a4: u32_at(bytes, 0xa4),
        unknown_a8: u32_at(bytes, 0xa8),
        unknown_ac: u32_at(bytes, 0xac),
        header_signature_offset: u32_at(bytes, 0xb0),
        file_entry_count: u32_at(bytes, 0xb4),
        file_entry_table_offset: u32_at(bytes, 0xb8),
        file_entry_table_sha1: bytes[0xbc..0xd0].try_into().unwrap(),
        block_entry_count: u32_at(bytes, 0xd0),
        block_entry_table_offset: u32_at(bytes, 0xd4),
        block_entry_table_sha1: bytes[0xd8..0xec].try_into().unwrap(),
        named_tag_count: u32_at(bytes, 0xec),
        named_tag_table_offset: u32_at(bytes, 0xf0),
        named_tag_table_sha1: bytes[0xf4..0x108].try_into().unwrap(),
        package_file_size: u32_at(bytes, 0x13c),
    })
}

fn read_table(
    storage: &TigerPackageStorage,
    actual_size: u64,
    offset: u32,
    count: u32,
    stride: usize,
    label: &str,
) -> Result<Vec<u8>> {
    let size = (count as usize)
        .checked_mul(stride)
        .ok_or_else(|| Error::Invalid(format!("D1 {label} table size overflow")))?;
    let end = (offset as u64)
        .checked_add(size as u64)
        .ok_or_else(|| Error::Invalid(format!("D1 {label} table range overflow")))?;
    if end > actual_size {
        return Err(Error::Invalid(format!(
            "D1 {label} table {offset:#x}..{end:#x} exceeds package size {actual_size:#x}"
        )));
    }
    storage.read_self_range(offset as u64, size)
}

fn validate_table_sha1(
    bytes: &[u8],
    expected: &[u8; 20],
    zero_count_uses_zero_hash: bool,
    label: &str,
) -> Result<()> {
    if zero_count_uses_zero_hash && bytes.is_empty() && *expected == [0u8; 20] {
        return Ok(());
    }
    let actual = sha1::digest(bytes);
    if actual != *expected {
        return Err(Error::Invalid(format!(
            "D1 {label} table SHA-1 mismatch: expected {}, got {}",
            hex20(expected),
            hex20(&actual)
        )));
    }
    Ok(())
}

fn parse_entries(bytes: &[u8], package_id: u16) -> Vec<TigerFileEntry> {
    bytes
        .chunks_exact(FILE_ENTRY_STRIDE)
        .enumerate()
        .map(|(index, row)| {
            let reference = u32_at(row, 0);
            let entry_b = u32_at(row, 4);
            let block_info = u64_at(row, 8);
            TigerFileEntry {
                index,
                tag_hash: tag_hash(package_id, index),
                reference,
                entry_b,
                file_type: (entry_b & 0xff) as u8,
                metadata_16_23: ((entry_b >> 16) & 0xff) as u8,
                file_subtype: ((entry_b >> 24) & 0xff) as u8,
                starting_block: (block_info & 0x3fff) as usize,
                starting_block_offset: (((block_info >> 14) & 0x3fff) << 4) as usize,
                file_size: ((block_info >> 28) & 0x3fff_ffff) as usize,
            }
        })
        .collect()
}

fn parse_blocks(bytes: &[u8]) -> Vec<TigerBlockEntry> {
    bytes
        .chunks_exact(BLOCK_ENTRY_STRIDE)
        .enumerate()
        .map(|(index, row)| TigerBlockEntry {
            index,
            offset: u32_at(row, 0),
            size: u32_at(row, 4),
            patch_id: u16_at(row, 8),
            flags: u16_at(row, 10),
            sha1: row[12..32].try_into().unwrap(),
        })
        .collect()
}

fn parse_named_tags(bytes: &[u8]) -> Vec<TigerNamedTag> {
    bytes
        .chunks_exact(NAMED_TAG_STRIDE)
        .enumerate()
        .map(|(index, row)| TigerNamedTag {
            index,
            tag_hash: u32_at(row, 0),
            class_hash: u32_at(row, 4),
            name: decode_cstr(&row[8..68]),
        })
        .collect()
}

fn validate_entry_spans(entries: &[TigerFileEntry], block_count: usize) -> Result<()> {
    for entry in entries {
        if entry.starting_block >= block_count {
            return Err(Error::Invalid(format!(
                "D1 entry {} starts at block {}, beyond block table size {}",
                entry.index, entry.starting_block, block_count
            )));
        }
        let span = entry
            .starting_block_offset
            .checked_add(entry.file_size)
            .ok_or_else(|| Error::Invalid(format!("D1 entry {} span overflow", entry.index)))?;
        let needed = 1usize.max((span + LOGICAL_BLOCK_SIZE - 1) / LOGICAL_BLOCK_SIZE);
        if entry.starting_block + needed > block_count {
            return Err(Error::Invalid(format!(
                "D1 entry {} spans blocks {}..{}, beyond block table size {}",
                entry.index,
                entry.starting_block,
                entry.starting_block + needed,
                block_count
            )));
        }
    }
    Ok(())
}

fn compute_block_usage(entries: &[TigerFileEntry], block_count: usize) -> Vec<usize> {
    let mut used_end = vec![0usize; block_count];
    for entry in entries {
        let mut remaining = entry.file_size;
        let mut block_index = entry.starting_block;
        let mut offset = entry.starting_block_offset;
        while remaining != 0 && block_index < block_count {
            let take = remaining.min(LOGICAL_BLOCK_SIZE - offset);
            used_end[block_index] = used_end[block_index].max(offset + take);
            remaining -= take;
            block_index += 1;
            offset = 0;
        }
    }
    used_end
}

fn entry_block_range(entry: &TigerFileEntry) -> std::ops::Range<usize> {
    let span = entry.starting_block_offset + entry.file_size;
    let count = 1usize.max((span + LOGICAL_BLOCK_SIZE - 1) / LOGICAL_BLOCK_SIZE);
    entry.starting_block..entry.starting_block + count
}

fn align_up(value: usize, alignment: usize) -> Result<usize> {
    value
        .checked_add(alignment - 1)
        .map(|value| value / alignment * alignment)
        .ok_or_else(|| Error::Invalid("D1 block raw-length alignment overflow".to_owned()))
}

fn decode_cstr(bytes: &[u8]) -> String {
    let end = bytes.iter().position(|byte| *byte == 0).unwrap_or(bytes.len());
    String::from_utf8_lossy(&bytes[..end]).into_owned()
}

#[inline]
fn u16_at(bytes: &[u8], offset: usize) -> u16 {
    u16::from_le_bytes(bytes[offset..offset + 2].try_into().unwrap())
}

#[inline]
fn u32_at(bytes: &[u8], offset: usize) -> u32 {
    u32::from_le_bytes(bytes[offset..offset + 4].try_into().unwrap())
}

#[inline]
fn u64_at(bytes: &[u8], offset: usize) -> u64 {
    u64::from_le_bytes(bytes[offset..offset + 8].try_into().unwrap())
}

fn hex20(bytes: &[u8; 20]) -> String {
    let mut out = String::with_capacity(40);
    for byte in bytes {
        use std::fmt::Write;
        let _ = write!(out, "{byte:02x}");
    }
    out
}

fn is_tiger_package_filename(path: &Path) -> bool {
    let Some(name) = path.file_name().and_then(|value| value.to_str()) else {
        return false;
    };
    let lower = name.to_ascii_lowercase();
    lower.ends_with(".pkg") || lower.ends_with(".pkg.bin")
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn tag_hash_round_trip() {
        let hash = tag_hash(0x005b, 0);
        assert_eq!(hash, 0x808b_6000);
        assert_eq!(split_tag_hash(hash), Some((0x005b, 0)));
    }

    #[test]
    fn patch_member_resolution_preserves_suffix() {
        assert_eq!(
            patch_path(Path::new("ps4_arch_cabal_005b_1.pkg"), 3),
            PathBuf::from("ps4_arch_cabal_005b_3.pkg")
        );
        assert_eq!(
            patch_path(Path::new("ps4_arch_cabal_005b_1.pkg.bin"), 0),
            PathBuf::from("ps4_arch_cabal_005b_0.pkg.bin")
        );
    }


    #[test]
    fn tar_range_reader_reuses_handle_and_reads_member_byte_ranges_concurrently() {
        use std::io::Cursor;
        use std::time::{SystemTime, UNIX_EPOCH};
        let stamp = SystemTime::now()
            .duration_since(UNIX_EPOCH).unwrap().as_nanos();
        let path = std::env::temp_dir().join(format!(
            "d1-retained-tar-{}-{stamp}.tar", std::process::id()
        ));
        let payload: Vec<u8> = (0..4096)
            .map(|i| (i as u8).wrapping_mul(19).wrapping_add(7))
            .collect();
        {
            let f = File::create(&path).unwrap();
            let mut builder = tar::Builder::new(f);
            let mut header = tar::Header::new_gnu();
            header.set_size(payload.len() as u64);
            header.set_mode(0o644);
            header.set_cksum();
            builder.append_data(
                &mut header, "packages/ps4_arch_cabal_005b_0.pkg.bin", Cursor::new(&payload)
            ).unwrap();
            builder.finish().unwrap();
        }
        {
            let index = Arc::new(TigerTarIndex::open(&path).unwrap());
            let member = Path::new("packages/ps4_arch_cabal_005b_0.pkg.bin");
            assert_eq!(index.read_member_range(member, 0, payload.len()).unwrap(), payload);
            assert_eq!(index.read_member_range(member, 150, 170).unwrap(), payload[150..320]);
            assert!(index.read_member_range(member, 4096, 0).unwrap().is_empty());
            assert!(index.read_member_range(member, 4090, 7).is_err());
            assert!(index.read_member_range(member, u64::MAX, 1).is_err());
            std::thread::scope(|scope| {
                for worker in 0..12 {
                    let index = Arc::clone(&index);
                    let payload = &payload;
                    scope.spawn(move || {
                        for i in 0..50 {
                            let offset = (worker * 31 + i * 47) % 4000;
                            let bytes = index.read_member_range(member, offset as u64, 64).unwrap();
                            assert_eq!(bytes, payload[offset..offset + 64]);
                        }
                    });
                }
            });
        }
        // Ensure Windows handles are disposed when the archive index drops.
        std::fs::remove_file(path).unwrap();
    }


    #[test]
    fn standalone_pkg_range_cache_reads_concurrently_across_patch_owners() {
        use std::time::{SystemTime, UNIX_EPOCH};
        let stamp = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_nanos();
        let dir = std::env::temp_dir().join(format!(
            "d1-range-cache-{}-{stamp}", std::process::id()
        ));
        std::fs::create_dir(&dir).unwrap();
        let cache = Arc::new(TigerFileRangeCache::default());
        let mut paths = Vec::new();
        let mut expected = Vec::new();
        for patch in 0..12u8 {
            let path = dir.join(format!("ps4_arch_cabal_005b_{patch}.pkg.bin"));
            let payload = (0..8192)
                .map(|n| (n as u8).wrapping_mul(31).wrapping_add(patch))
                .collect::<Vec<u8>>();
            std::fs::write(&path, &payload).unwrap();
            paths.push(path);
            expected.push(payload);
        }
        for (path, data) in paths.iter().zip(&expected) {
            assert_eq!(cache.read_range(path, 0, data.len()).unwrap(), *data);
            assert_eq!(cache.read_range(path, 99, 255).unwrap(), data[99..354]);
            assert!(cache.read_range(path, 8190, 3).is_err());
            assert!(cache.read_range(path, u64::MAX, 1).is_err());
        }
        assert_eq!(cache.handles.lock().unwrap().len(), MAX_RETAINED_PACKAGE_FILES);
        std::thread::scope(|scope| {
            for worker in 0..12 {
                let cache = Arc::clone(&cache);
                let paths = &paths;
                let expected = &expected;
                scope.spawn(move || {
                    for i in 0..40 {
                        let owner = (worker + i) % paths.len();
                        let offset = (worker * 43 + i * 179) % 8000;
                        let bytes = cache.read_range(&paths[owner], offset as u64, 128).unwrap();
                        assert_eq!(bytes, expected[owner][offset..offset + 128]);
                    }
                });
            }
        });
        drop(cache);
        for path in paths { std::fs::remove_file(path).unwrap(); }
        std::fs::remove_dir(dir).unwrap();
    }

    #[test]
    fn tar_member_normalization_preserves_package_namespace() {
        assert_eq!(
            normalize_tar_member_path(Path::new("./packages/ps4_arch_cabal_005b_1.pkg")).unwrap(),
            PathBuf::from("packages/ps4_arch_cabal_005b_1.pkg")
        );
        assert!(normalize_tar_member_path(Path::new("../outside.pkg")).is_err());
    }
}

#[cfg(test)]
mod native_lzh_integration_tests {
    use super::{NativeLzhDecompressor, TigerBlockDecompressor, LOGICAL_BLOCK_SIZE};

    #[test]
    fn native_oodle_fails_closed_on_truncated_and_invalid_raw_lengths() {
        let decoder = NativeLzhDecompressor;
        assert!(decoder.decompress_exact(&[0xb7], 0x4000).is_err());
        assert!(decoder.decompress_exact(&[0xb7], 0).is_err());
        assert!(decoder.decompress_exact(&[0xb7], LOGICAL_BLOCK_SIZE + 1).is_err());
        assert!(decoder.decompress_exact(&[], 0x4000).is_err());
    }
}

pub fn synthetic_raw_package(path: std::path::PathBuf, hashes: &[[u8; 20]],
    start_offset: usize, file_size: usize, cache: bool) -> TigerPackage {
    let mut package = TigerPackage {
        storage: TigerPackageStorage::File {
            path: path.clone(),
            ranges: Arc::new(TigerFileRangeCache::default()),
        },
        path,
        header: TigerHeader {
            version: TIGER_VERSION, platform: Platform::Ps4, package_id: 0x5b,
            unknown_06: 0, unknown_08: 0, build_time_raw: 0, build_id_raw: 0,
            version_major: 1, version_minor: 0, patch_id: 0,
            language_code: 0, tool_string: String::new(), unknown_a4: 0,
            unknown_a8: 0, unknown_ac: 0, header_signature_offset: 0,
            file_entry_count: 1, file_entry_table_offset: 0,
            file_entry_table_sha1: [0; 20],
            block_entry_count: hashes.len() as u32, block_entry_table_offset: 0,
            block_entry_table_sha1: [0; 20],
            named_tag_count: 0, named_tag_table_offset: 0,
            named_tag_table_sha1: [0; 20],
            package_file_size: (hashes.len() * LOGICAL_BLOCK_SIZE) as u32,
        },
        entries: vec![TigerFileEntry {
            index: 0, tag_hash: tag_hash(0x5b, 0), reference: 0, entry_b: 0,
            file_type: 0, file_subtype: 0, metadata_16_23: 0,
            starting_block: 0, starting_block_offset: start_offset,
            file_size,
        }],
        blocks: hashes.iter().enumerate().map(|(i, sha1)| TigerBlockEntry {
            index: i, offset: (i * LOGICAL_BLOCK_SIZE) as u32,
            size: LOGICAL_BLOCK_SIZE as u32, patch_id: 0,
            flags: 0, sha1: *sha1,
        }).collect(),
        named_tags: Vec::new(),
        block_used_end: vec![LOGICAL_BLOCK_SIZE; hashes.len()],
        block_cache: None,
    };
    if cache {
        package.attach_block_cache(Arc::new(Mutex::new(TigerBlockCache::new(
            hashes.len() * LOGICAL_BLOCK_SIZE
        ))));
    }
    package
}
