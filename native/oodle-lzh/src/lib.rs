//! Clean-room Destiny 1 Oodle 3 LZH decoder work.
//!
//! This crate intentionally models observed stream semantics rather than
//! embedding or linking the proprietary Oodle runtime.
//!
//! Current status:
//! - D1 0xB7 stream header -> Oodle decode type 7 -> LZH is modeled.
//! - The complete 457-entry LZH match descriptor table is generated.
//! - MSB-first bit reading, long-length extension, and recent-distance
//!   bookkeeping are modeled.
//! - Serialized Huffman-codebook parsing and the final token loop are the
//!   remaining implementation frontier.

pub const LITERAL_SYMBOLS: usize = 256;
pub const MATCH_SYMBOLS: usize = 457;
pub const LZH_ALPHABET_SIZE: usize = LITERAL_SYMBOLS + MATCH_SYMBOLS;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Compressor {
    Lzh,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct StreamHeader {
    pub header_mode: u8,
    pub decode_type: u8,
    pub decode_subtype: u8,
    pub field_0c: u8,
    pub field_10: u8,
    pub field_14: u8,
    pub bytes_consumed: usize,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Error {
    EmptyInput,
    UnsupportedHeader(u8),
    InvalidMatchSymbol(usize),
    UnexpectedEof,
    HuffmanCodebookNotImplemented,
}

/// Parse the one-byte header used by the currently validated D1 ROI corpus.
///
/// The verified Oodle 3 DLL parses 0xB7 as the six dword fields
/// [3, 7, 0, 0, 1, 0]. Its decode-type mapper maps type 7 to compressor
/// enum 0, whose public name is "LZH".
pub fn parse_d1_header(input: &[u8]) -> Result<(StreamHeader, Compressor), Error> {
    let first = *input.first().ok_or(Error::EmptyInput)?;
    if first != 0xB7 {
        return Err(Error::UnsupportedHeader(first));
    }
    Ok((
        StreamHeader {
            header_mode: 3,
            decode_type: 7,
            decode_subtype: 0,
            field_0c: 0,
            field_10: 1,
            field_14: 0,
            bytes_consumed: 1,
        },
        Compressor::Lzh,
    ))
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct MatchDescriptor {
    /// Zero for repeat-distance symbols; otherwise the base before adding
    /// the encoded distance bits and the mandatory +1.
    pub base_distance: u32,
    pub base_length: u16,
    pub distance_extra_bits: u8,
    pub length_extra_bits: u8,
    pub repeat_distance: bool,
}

const LENGTH_BASES: [u16; 20] = [
    2, 3, 4, 5, 6, 7, 8, 9, 11, 13, 15, 17, 21, 25, 29, 37, 45, 61, 93, 157,
];

const REPEAT_LENGTH_EXTRA: [u8; 20] = [
    0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 3, 3, 4, 5, 6, 6,
];

const NEW_LENGTH_BASES: [u16; 19] = [
    3, 4, 5, 6, 7, 8, 9, 11, 13, 15, 17, 21, 25, 29, 37, 45, 61, 93, 157,
];

const NEW_LENGTH_EXTRA: [u8; 19] = [
    0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 3, 3, 4, 5, 6, 7,
];

const DISTANCE_BASES: [u32; 23] = [
    0, 16, 32, 64, 128, 256, 512, 768, 1024, 1536, 2048, 3072, 4096, 5120,
    6144, 8192, 12288, 16384, 24576, 32768, 49152, 65536, 98304,
];

const DISTANCE_EXTRA: [u8; 23] = [
    4, 4, 5, 6, 7, 8, 8, 8, 9, 9, 10, 10, 10, 10, 11, 12, 12, 13, 13, 14, 14,
    15, 15,
];

/// Generate the descriptor indexed by (decoded Huffman symbol - 256).
///
/// The DLL stores 457 descriptors at VA 0x1800BD120. The first 20 are
/// repeat-distance length classes. The remaining 437 entries are exactly
/// 19 length classes x 23 new-distance buckets.
pub fn match_descriptor(index: usize) -> Result<MatchDescriptor, Error> {
    if index < 20 {
        return Ok(MatchDescriptor {
            base_distance: 0,
            base_length: LENGTH_BASES[index],
            distance_extra_bits: 2,
            length_extra_bits: REPEAT_LENGTH_EXTRA[index],
            repeat_distance: true,
        });
    }

    let rem = index - 20;
    let length_class = rem / DISTANCE_BASES.len();
    let distance_class = rem % DISTANCE_BASES.len();
    if length_class >= NEW_LENGTH_BASES.len() {
        return Err(Error::InvalidMatchSymbol(index));
    }

    Ok(MatchDescriptor {
        base_distance: DISTANCE_BASES[distance_class],
        base_length: NEW_LENGTH_BASES[length_class],
        distance_extra_bits: DISTANCE_EXTRA[distance_class],
        length_extra_bits: NEW_LENGTH_EXTRA[length_class],
        repeat_distance: false,
    })
}

#[derive(Debug, Clone)]
pub struct BitReader<'a> {
    data: &'a [u8],
    bit_pos: usize,
}

impl<'a> BitReader<'a> {
    pub fn new(data: &'a [u8], bit_pos: usize) -> Self {
        Self { data, bit_pos }
    }

    pub fn bit_pos(&self) -> usize {
        self.bit_pos
    }

    pub fn read_bits(&mut self, count: u8) -> Result<u32, Error> {
        if count == 0 {
            return Ok(0);
        }
        let end = self
            .bit_pos
            .checked_add(count as usize)
            .ok_or(Error::UnexpectedEof)?;
        if end > self.data.len() * 8 {
            return Err(Error::UnexpectedEof);
        }

        let mut value = 0u32;
        for _ in 0..count {
            let byte = self.data[self.bit_pos / 8];
            let shift = 7 - (self.bit_pos & 7);
            value = (value << 1) | (((byte >> shift) & 1) as u32);
            self.bit_pos += 1;
        }
        Ok(value)
    }

    pub fn read_bit(&mut self) -> Result<u32, Error> {
        self.read_bits(1)
    }
}

/// Decode the LZH match-length extension.
///
/// Base length 157 is the escape class observed in the D1 subtype-0 decoder.
/// It uses a prefix-selected wide extension rather than simply consuming the
/// descriptor's nominal extra-bit count.
pub fn decode_match_length(
    bits: &mut BitReader<'_>,
    base_length: u16,
    extra_bits: u8,
) -> Result<usize, Error> {
    if base_length != 157 {
        return Ok(base_length as usize + bits.read_bits(extra_bits)? as usize);
    }

    if bits.read_bit()? == 0 {
        return Ok(157 + bits.read_bits(6)? as usize);
    }
    if bits.read_bit()? == 0 {
        return Ok(221 + bits.read_bits(7)? as usize);
    }
    if bits.read_bit()? == 0 {
        return Ok(349 + bits.read_bits(8)? as usize);
    }
    if bits.read_bit()? == 0 {
        return Ok(605 + bits.read_bits(10)? as usize);
    }
    Ok(1629 + bits.read_bits(14)? as usize)
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct RecentDistances {
    slots: [usize; 4],
}

impl Default for RecentDistances {
    fn default() -> Self {
        Self {
            slots: [20, 24, 28, 32],
        }
    }
}

impl RecentDistances {
    pub fn slots(&self) -> [usize; 4] {
        self.slots
    }

    /// Select one of four recent distances and move it to the front.
    pub fn select_repeat(&mut self, selector: u8) -> usize {
        let idx = (selector & 3) as usize;
        let selected = self.slots[idx];
        for i in (1..=idx).rev() {
            self.slots[i] = self.slots[i - 1];
        }
        self.slots[0] = selected;
        selected
    }

    /// Update the three historical explicit-distance slots after decoding a
    /// new distance. This mirrors the subtype-0 conservative path:
    /// slot3 <- slot2, slot2 <- slot1, slot1 <- new, slot0 unchanged.
    pub fn insert_new(&mut self, distance: usize) {
        self.slots[3] = self.slots[2];
        self.slots[2] = self.slots[1];
        self.slots[1] = distance;
    }
}

/// Decode a new (non-repeat) distance from one generated descriptor.
pub fn decode_new_distance(
    bits: &mut BitReader<'_>,
    desc: MatchDescriptor,
) -> Result<usize, Error> {
    debug_assert!(!desc.repeat_distance);
    Ok(desc.base_distance as usize + bits.read_bits(desc.distance_extra_bits)? as usize + 1)
}

/// Full block decoding is deliberately not exposed as working until the
/// serialized 713-symbol Huffman codebook reader is behavior-matched.
pub fn decompress_destiny_lzh(_compressed: &[u8], _raw_len: usize) -> Result<Vec<u8>, Error> {
    Err(Error::HuffmanCodebookNotImplemented)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn b7_is_d1_lzh_subtype_zero() {
        let (h, c) = parse_d1_header(&[0xB7, 0x43]).unwrap();
        assert_eq!(c, Compressor::Lzh);
        assert_eq!(h.decode_type, 7);
        assert_eq!(h.decode_subtype, 0);
        assert_eq!(h.bytes_consumed, 1);
    }

    #[test]
    fn descriptor_table_has_exact_observed_shape() {
        assert_eq!(LZH_ALPHABET_SIZE, 713);
        assert_eq!(MATCH_SYMBOLS, 457);

        assert_eq!(
            match_descriptor(0).unwrap(),
            MatchDescriptor {
                base_distance: 0,
                base_length: 2,
                distance_extra_bits: 2,
                length_extra_bits: 0,
                repeat_distance: true,
            }
        );
        assert_eq!(match_descriptor(19).unwrap().base_length, 157);

        assert_eq!(
            match_descriptor(20).unwrap(),
            MatchDescriptor {
                base_distance: 0,
                base_length: 3,
                distance_extra_bits: 4,
                length_extra_bits: 0,
                repeat_distance: false,
            }
        );
        assert_eq!(match_descriptor(42).unwrap().base_distance, 98_304);
        assert_eq!(match_descriptor(43).unwrap().base_length, 4);

        let last = match_descriptor(456).unwrap();
        assert_eq!(last.base_distance, 98_304);
        assert_eq!(last.base_length, 157);
        assert_eq!(last.distance_extra_bits, 15);
        assert_eq!(last.length_extra_bits, 7);
        assert!(match_descriptor(457).is_err());
    }

    #[test]
    fn recent_distance_move_to_front_matches_observed_cache() {
        let mut recent = RecentDistances::default();
        assert_eq!(recent.select_repeat(3), 32);
        assert_eq!(recent.slots(), [32, 20, 24, 28]);
        recent.insert_new(1234);
        assert_eq!(recent.slots(), [32, 1234, 20, 24]);
        assert_eq!(recent.select_repeat(2), 20);
        assert_eq!(recent.slots(), [20, 32, 1234, 24]);
    }

    #[test]
    fn msb_reader_matches_dll_bit_order() {
        let mut br = BitReader::new(&[0b1011_0010, 0b0110_0000], 0);
        assert_eq!(br.read_bits(4).unwrap(), 0b1011);
        assert_eq!(br.read_bits(5).unwrap(), 0b00100);
        assert_eq!(br.bit_pos(), 9);
    }

    #[test]
    fn normal_match_length_adds_extra_bits() {
        let mut br = BitReader::new(&[0b1100_0000], 0);
        assert_eq!(decode_match_length(&mut br, 9, 1).unwrap(), 10);
    }

    #[test]
    fn escaped_match_length_first_range() {
        // Prefix 0, then six bits 000101 -> 157 + 5.
        let mut br = BitReader::new(&[0b0000_1010], 0);
        assert_eq!(decode_match_length(&mut br, 157, 6).unwrap(), 162);
    }
}
