//! Shared table-driven IEEE CRC-32 for T6 IPAK decoded payload identity.
//!
//! T6 indexes retain the low 29 bits of the *standard* IEEE CRC-32.
//! This deliberately does not use the SSE4.2 CRC32 instruction, which
//! computes the different CRC-32C polynomial.
const POLYNOMIAL: u32 = 0xedb8_8320;

const fn table() -> [u32; 256] {
    let mut values = [0u32; 256];
    let mut i = 0usize;
    while i < 256 {
        let mut crc = i as u32;
        let mut bit = 0;
        while bit < 8 {
            let mask = (crc & 1).wrapping_neg();
            crc = (crc >> 1) ^ (POLYNOMIAL & mask);
            bit += 1;
        }
        values[i] = crc;
        i += 1;
    }
    values
}

static CRC32_TABLE: [u32; 256] = table();

#[inline]
pub(super) fn crc32(bytes: &[u8]) -> u32 {
    let mut crc = !0u32;
    for &byte in bytes {
        let index = ((crc as u8) ^ byte) as usize;
        crc = (crc >> 8) ^ CRC32_TABLE[index];
    }
    !crc
}

#[cfg(test)]
mod tests {
    use super::*;

    fn bitwise_reference(bytes: &[u8]) -> u32 {
        let mut crc = !0u32;
        for &byte in bytes {
            crc ^= u32::from(byte);
            for _ in 0..8 {
                crc = (crc >> 1) ^ (POLYNOMIAL & (crc & 1).wrapping_neg());
            }
        }
        !crc
    }

    #[test]
    fn crc32_matches_standard_known_vectors() {
        assert_eq!(crc32(&[]), 0);
        assert_eq!(crc32(b"123456789"), 0xcbf4_3926);
        assert_eq!(crc32(b"The quick brown fox jumps over the lazy dog"), 0x414f_a339);
    }

    #[test]
    fn matches_previous_bitwise_implementation_at_boundaries() {
        for length in [0, 1, 2, 3, 4, 7, 8, 15, 16, 31, 32, 63, 64, 127, 128, 255, 256, 257, 4096, 32768] {
            let mut bytes = vec![0u8; length];
            let mut value = 0x1234_5678u32;
            for byte in &mut bytes {
                value ^= value << 13;
                value ^= value >> 17;
                value ^= value << 5;
                *byte = value as u8;
            }
            assert_eq!(crc32(&bytes), bitwise_reference(&bytes), "length {length}");
        }
    }

    #[test]
    fn t6_retained_crc29_is_identical() {
        for sample in [b"".as_slice(), b"ipak".as_slice(), b"123456789".as_slice()] {
            assert_eq!(crc32(sample) & 0x1fff_ffff, bitwise_reference(sample) & 0x1fff_ffff);
        }
    }
}
