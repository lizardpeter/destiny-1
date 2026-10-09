//! IPAK CRC-32 validation fast path (same IEEE polynomial and byte order).
pub(crate) const fn table() -> [u32; 256] {
    let mut out = [0u32; 256];
    let mut i = 0;
    while i < 256 {
        let mut crc = i as u32;
        let mut j = 0;
        while j < 8 {
            let mask = 0u32.wrapping_sub(crc & 1);
            crc = (crc >> 1) ^ (0xedb8_8320 & mask);
            j += 1;
        }
        out[i] = crc;
        i += 1;
    }
    out
}
pub(crate) const CRC32_TABLE: [u32; 256] = table();

#[inline]
pub(crate) fn crc32(bytes: &[u8]) -> u32 {
    let mut crc = 0xffff_ffffu32;
    for &byte in bytes {
        crc = (crc >> 8) ^ CRC32_TABLE[((crc as u8) ^ byte) as usize];
    }
    !crc
}
