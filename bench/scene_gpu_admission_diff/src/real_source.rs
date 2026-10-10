#[derive(Clone,Debug,PartialEq,Eq)]
pub struct StreamChange {dirty:bool,upload:std::ops::Range<usize>}
pub fn changed_byte_range<T: bytemuck::Pod>(
    source: &[T],
    uploaded: &[T],
) -> StreamChange {
    let new_bytes = bytemuck::cast_slice::<T, u8>(source);
    let old_bytes = bytemuck::cast_slice::<T, u8>(uploaded);
    let shared_len = new_bytes.len().min(old_bytes.len());

    // Compare cache-friendly blocks with slice equality (the compiler can
    // lower this to a vectorized memcmp) instead of iterating one byte at a
    // time through multi-megabyte bone/instance streams every frame. Locate
    // mismatches *within* the first unequal block to retain the exact Vulkan
    // mapped-buffer byte range, including unaligned single-byte changes.
    const BLOCK: usize = 256;
    let mut first = 0usize;
    while shared_len - first >= BLOCK
        && new_bytes[first..first + BLOCK] == old_bytes[first..first + BLOCK]
    {
        first += BLOCK;
    }
    let scan_end = (first + BLOCK).min(shared_len);
    first += new_bytes[first..scan_end]
        .iter()
        .zip(&old_bytes[first..scan_end])
        .position(|(a, b)| a != b)
        .unwrap_or(scan_end - first);

    if first == shared_len && new_bytes.len() == old_bytes.len() {
        return StreamChange {
            dirty: false,
            upload: 0..0,
        };
    }

    // Preserve the common suffix exactly, including when only a small middle
    // region changes. Appended bytes must always be uploaded; a shrunk array
    // needs no GPU-tail clearing. Check complete blocks before the final
    // byte-precise scan so an unchanged tail does not cost O(bytes) scalar
    // comparisons.
    let mut end = new_bytes.len();
    while end > first && end <= old_bytes.len() && end - first >= BLOCK
        && new_bytes[end - BLOCK..end] == old_bytes[end - BLOCK..end]
    {
        end -= BLOCK;
    }
    while end > first
        && end <= old_bytes.len()
        && new_bytes[end - 1] == old_bytes[end - 1]
    {
        end -= 1;
    }
    StreamChange { dirty: true, upload: first..end }
}
pub fn commit_uploaded_bytes<T: bytemuck::Pod + bytemuck::Zeroable + Copy>(
    source: &[T],
    uploaded: &mut Vec<T>,
    change: &StreamChange,
) {
    if source.len() > uploaded.len() {
        uploaded.resize(source.len(), T::zeroed());
    }
    if !change.upload.is_empty() {
        let bytes = bytemuck::cast_slice::<T, u8>(source);
        let destination = bytemuck::cast_slice_mut::<T, u8>(uploaded.as_mut_slice());
        destination[change.upload.clone()].copy_from_slice(&bytes[change.upload.clone()]);
    }
    uploaded.truncate(source.len());
}
