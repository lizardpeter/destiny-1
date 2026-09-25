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
    HuffmanUsedSymbolsOutOfRange(usize),
    HuffmanSymbolOutOfRange(usize),
    HuffmanCodeLengthWidthOutOfRange(u8),
    HuffmanCodeLengthOutOfRange(u8),
    HuffmanDuplicateSymbol(usize),
    HuffmanRunOutOfRange(usize),
    HuffmanPackedRunOutOfRange(usize),
    HuffmanComplexCodeLengthOutOfRange(i32),
    HuffmanFinalCodeLengthOutOfRange(u8),
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


#[derive(Debug, Clone, PartialEq, Eq)]
pub struct HuffmanCodebook {
    pub code_lengths: Vec<u8>,
    pub used_symbols: usize,
    pub one_symbol: Option<usize>,
}

impl HuffmanCodebook {
    /// Read the sparse/simple rrHuffman serialization used when its leading
    /// mode bit is zero.
    ///
    /// For an alphabet of N symbols the verified Oodle 3 reader uses
    /// ceil(log2(N)) bits for both the used-symbol count and symbol indices.
    /// If more than one symbol is present, a 3-bit field gives the number of
    /// bits used to serialize (code_length - 1), followed by that many
    /// (symbol, code_length) pairs.
    pub fn read(bits: &mut BitReader<'_>, alphabet_size: usize) -> Result<Self, Error> {
        if bits.read_bit()? == 0 {
            Self::read_sparse_after_mode(bits, alphabet_size)
        } else {
            Self::read_complex_after_mode(bits, alphabet_size)
        }
    }

    pub fn read_sparse_after_mode(
        bits: &mut BitReader<'_>,
        alphabet_size: usize,
    ) -> Result<Self, Error> {
        let index_bits = ceil_log2(alphabet_size) as u8;
        let used = bits.read_bits(index_bits)? as usize;
        if used > alphabet_size {
            return Err(Error::HuffmanUsedSymbolsOutOfRange(used));
        }

        let mut code_lengths = vec![0u8; alphabet_size];
        if used == 0 {
            return Ok(Self {
                code_lengths,
                used_symbols: 0,
                one_symbol: None,
            });
        }

        if used == 1 {
            let symbol = bits.read_bits(index_bits)? as usize;
            if symbol >= alphabet_size {
                return Err(Error::HuffmanSymbolOutOfRange(symbol));
            }
            // The original reader represents the single-symbol case
            // specially rather than assigning a normal positive code length.
            return Ok(Self {
                code_lengths,
                used_symbols: 1,
                one_symbol: Some(symbol),
            });
        }

        let code_len_bits = bits.read_bits(3)? as u8;
        if code_len_bits > 5 {
            return Err(Error::HuffmanCodeLengthWidthOutOfRange(code_len_bits));
        }

        for _ in 0..used {
            let symbol = bits.read_bits(index_bits)? as usize;
            if symbol >= alphabet_size {
                return Err(Error::HuffmanSymbolOutOfRange(symbol));
            }
            if code_lengths[symbol] != 0 {
                return Err(Error::HuffmanDuplicateSymbol(symbol));
            }

            let code_len = bits.read_bits(code_len_bits)? as u8 + 1;
            if code_len > 16 {
                return Err(Error::HuffmanCodeLengthOutOfRange(code_len));
            }
            code_lengths[symbol] = code_len;
        }

        Ok(Self {
            code_lengths,
            used_symbols: used,
            one_symbol: None,
        })
    }


    /// Read the packed/run-coded rrHuffman serialization used when the
    /// leading mode bit is one.
    ///
    /// The stream alternates zero runs and nonzero runs. Run lengths use the
    /// same order-1 exponential-Golomb-like code seen in the DLL. Each
    /// nonzero code length is an adaptive prediction plus a ZigZag signed
    /// delta whose unsigned magnitude is Rice-coded with the 2-bit parameter
    /// stored immediately after the mode bit.
    pub fn read_complex_after_mode(
        bits: &mut BitReader<'_>,
        alphabet_size: usize,
    ) -> Result<Self, Error> {
        let rice_k = bits.read_bits(2)? as u8;
        let mut predictor = (4 * ceil_log2(alphabet_size)) as i32;
        let mut code_lengths = vec![0u8; alphabet_size];
        let mut pos = 0usize;
        let mut used = 0usize;

        while pos < alphabet_size {
            let zero_run = read_packed_run_len(bits)?;
            if zero_run > alphabet_size - pos {
                return Err(Error::HuffmanRunOutOfRange(zero_run));
            }
            pos += zero_run;
            if pos == alphabet_size {
                break;
            }

            let packed = read_packed_run_len(bits)?;
            if packed > alphabet_size - pos {
                return Err(Error::HuffmanPackedRunOutOfRange(packed));
            }

            for _ in 0..packed {
                let unsigned_delta = read_rice_unsigned(bits, rice_k)?;
                let delta = zigzag_decode(unsigned_delta);
                let predicted = (predictor + 2) >> 2;
                let cur = predicted + delta;
                if !(1..=30).contains(&cur) {
                    return Err(Error::HuffmanComplexCodeLengthOutOfRange(cur));
                }

                code_lengths[pos] = cur as u8;
                used += 1;
                predictor = ((3 * predictor + 2) >> 2) + cur;
                pos += 1;
            }
        }

        if let Some(max_len) = code_lengths.iter().copied().max().filter(|&x| x != 0) {
            if max_len > 16 {
                return Err(Error::HuffmanFinalCodeLengthOutOfRange(max_len));
            }
        }

        Ok(Self {
            code_lengths,
            used_symbols: used,
            one_symbol: None,
        })
    }

    pub fn min_code_len(&self) -> Option<u8> {
        self.code_lengths.iter().copied().filter(|&x| x != 0).min()
    }

    pub fn max_code_len(&self) -> Option<u8> {
        self.code_lengths.iter().copied().max().filter(|&x| x != 0)
    }
}


fn read_packed_run_len(bits: &mut BitReader<'_>) -> Result<usize, Error> {
    // The DLL consumes 0^z, a one bit, and then (z+1) payload bits.
    // If the resulting (z+2)-bit value is V, RunLen = V - 1.
    let mut zeros = 0u8;
    while bits.read_bit()? == 0 {
        zeros = zeros.checked_add(1).ok_or(Error::UnexpectedEof)?;
    }
    let suffix_bits = zeros.checked_add(1).ok_or(Error::UnexpectedEof)?;
    let suffix = bits.read_bits(suffix_bits)? as usize;
    Ok((1usize << suffix_bits) + suffix - 1)
}

fn read_rice_unsigned(bits: &mut BitReader<'_>, k: u8) -> Result<u32, Error> {
    let mut quotient = 0u32;
    while bits.read_bit()? == 0 {
        quotient = quotient.checked_add(1).ok_or(Error::UnexpectedEof)?;
    }
    let remainder = bits.read_bits(k)?;
    quotient
        .checked_shl(k as u32)
        .and_then(|x| x.checked_add(remainder))
        .ok_or(Error::UnexpectedEof)
}

fn zigzag_decode(value: u32) -> i32 {
    ((value >> 1) as i32) ^ -((value & 1) as i32)
}

fn ceil_log2(n: usize) -> u32 {
    if n <= 1 {
        0
    } else {
        usize::BITS - (n - 1).leading_zeros()
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
    fn packed_run_length_ranges_match_dll_encoding() {
        // 10 -> 1, 11 -> 2, 0100 -> 3, 0110 -> 5.
        for (byte, expected) in [
            (0b1000_0000u8, 1usize),
            (0b1100_0000u8, 2usize),
            (0b0100_0000u8, 3usize),
            (0b0110_0000u8, 5usize),
        ] {
            let mut br = BitReader::new(&[byte], 0);
            assert_eq!(read_packed_run_len(&mut br).unwrap(), expected);
        }
    }

    #[test]
    fn rice_zigzag_delta_matches_reversed_inner_loop() {
        // k=1: 1|0 => u=0 => 0; 1|1 => u=1 => -1;
        // 01|0 => q=1,r=0 => u=2 => +1.
        let mut a = BitReader::new(&[0b1000_0000], 0);
        assert_eq!(zigzag_decode(read_rice_unsigned(&mut a, 1).unwrap()), 0);
        let mut b = BitReader::new(&[0b1100_0000], 0);
        assert_eq!(zigzag_decode(read_rice_unsigned(&mut b, 1).unwrap()), -1);
        let mut c = BitReader::new(&[0b0100_0000], 0);
        assert_eq!(zigzag_decode(read_rice_unsigned(&mut c, 1).unwrap()), 1);
    }

    #[test]
    fn complex_huffman_run_and_predictor_path() {
        // alphabet=8 => initial predictor=12, predicted length=3.
        // mode=1, rice k=0; zero run=1; packed run=2;
        // two zero deltas => lengths 3,3; final zero run=5.
        let bits = [
            1, 0,0, // complex mode, rice k=0
            1,0, // zero run 1
            1,1, // packed run 2
            1, // Rice u=0
            1, // Rice u=0
            0,1,1,0, // zero run 5
        ];
        let mut packed = vec![0u8; (bits.len()+7)/8];
        for (i,&b) in bits.iter().enumerate() {
            packed[i/8] |= b << (7-(i&7));
        }
        let mut br = BitReader::new(&packed,0);
        let h = HuffmanCodebook::read(&mut br,8).unwrap();
        assert_eq!(h.used_symbols,2);
        assert_eq!(h.code_lengths, vec![0,3,3,0,0,0,0,0]);
    }

    #[test]
    fn sparse_huffman_multi_symbol_layout_matches_reversed_reader() {
        // alphabet=8 => index width=3.
        // mode=0, used=3, code_len_bits=2,
        // then (symbol=1,len=1), (symbol=5,len=2), (symbol=7,len=3).
        let bits = [
            0, // mode
            0,1,1, // used=3
            0,1,0, // code_len_bits=2
            0,0,1, 0,0, // sym1,len-1=0
            1,0,1, 0,1, // sym5,len-1=1
            1,1,1, 1,0, // sym7,len-1=2
        ];
        let mut packed = vec![0u8; (bits.len()+7)/8];
        for (i,&b) in bits.iter().enumerate() {
            packed[i/8] |= b << (7-(i&7));
        }
        let mut br = BitReader::new(&packed,0);
        let h = HuffmanCodebook::read(&mut br,8).unwrap();
        assert_eq!(h.used_symbols,3);
        assert_eq!(h.code_lengths[1],1);
        assert_eq!(h.code_lengths[5],2);
        assert_eq!(h.code_lengths[7],3);
        assert_eq!(h.min_code_len(),Some(1));
        assert_eq!(h.max_code_len(),Some(3));
    }

    #[test]
    fn sparse_huffman_single_symbol_is_special() {
        // alphabet=8: mode 0, used=1, symbol=6.
        let mut br = BitReader::new(&[0b0001_1100],0);
        let h = HuffmanCodebook::read(&mut br,8).unwrap();
        assert_eq!(h.used_symbols,1);
        assert_eq!(h.one_symbol,Some(6));
        assert!(h.code_lengths.iter().all(|&x| x==0));
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
