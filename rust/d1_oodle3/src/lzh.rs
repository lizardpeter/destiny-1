//! Clean-room decoder primitives for the legacy Oodle LZH stream used by Destiny 1.
//!
//! This module starts with the transmitted canonical-Huffman model.  The retail
//! Oodle 2.3 runtime uses a 713-symbol alphabet, a 10-bit fast-decode prefix,
//! and permits code lengths through 16 bits.

pub const SYMBOL_COUNT: usize = 713;
pub const FAST_DECODE_BITS: u8 = 10;
pub const MAX_CODE_LEN: u8 = 16;

pub const LITERAL_SYMBOLS: usize = 256;
pub const RECENT_TOKEN_COUNT: usize = 20;
pub const EXPLICIT_LENGTH_CLASS_COUNT: usize = 19;
pub const EXPLICIT_DISTANCE_CLASS_COUNT: usize = 23;
pub const TOKEN_SYMBOLS: usize =
    RECENT_TOKEN_COUNT + EXPLICIT_LENGTH_CLASS_COUNT * EXPLICIT_DISTANCE_CLASS_COUNT;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct LengthCode {
    pub base: u16,
    pub extra_bits: u8,
    pub extended: bool,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct DistanceCode {
    pub base: u32,
    pub extra_bits: u8,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum SymbolCode {
    Literal(u8),
    Recent {
        selector_bits: u8,
        length: LengthCode,
    },
    Explicit {
        distance: DistanceCode,
        length: LengthCode,
    },
}

#[rustfmt::skip]
const RECENT_LENGTHS: [LengthCode; RECENT_TOKEN_COUNT] = [
    LengthCode { base: 2, extra_bits: 0, extended: false },
    LengthCode { base: 3, extra_bits: 0, extended: false },
    LengthCode { base: 4, extra_bits: 0, extended: false },
    LengthCode { base: 5, extra_bits: 0, extended: false },
    LengthCode { base: 6, extra_bits: 0, extended: false },
    LengthCode { base: 7, extra_bits: 0, extended: false },
    LengthCode { base: 8, extra_bits: 0, extended: false },
    LengthCode { base: 9, extra_bits: 1, extended: false },
    LengthCode { base: 11, extra_bits: 1, extended: false },
    LengthCode { base: 13, extra_bits: 1, extended: false },
    LengthCode { base: 15, extra_bits: 1, extended: false },
    LengthCode { base: 17, extra_bits: 2, extended: false },
    LengthCode { base: 21, extra_bits: 2, extended: false },
    LengthCode { base: 25, extra_bits: 2, extended: false },
    LengthCode { base: 29, extra_bits: 3, extended: false },
    LengthCode { base: 37, extra_bits: 3, extended: false },
    LengthCode { base: 45, extra_bits: 4, extended: false },
    LengthCode { base: 61, extra_bits: 5, extended: false },
    LengthCode { base: 93, extra_bits: 6, extended: false },
    LengthCode { base: 157, extra_bits: 6, extended: true },
];

#[rustfmt::skip]
const EXPLICIT_LENGTHS: [LengthCode; EXPLICIT_LENGTH_CLASS_COUNT] = [
    LengthCode { base: 3, extra_bits: 0, extended: false },
    LengthCode { base: 4, extra_bits: 0, extended: false },
    LengthCode { base: 5, extra_bits: 0, extended: false },
    LengthCode { base: 6, extra_bits: 0, extended: false },
    LengthCode { base: 7, extra_bits: 0, extended: false },
    LengthCode { base: 8, extra_bits: 0, extended: false },
    LengthCode { base: 9, extra_bits: 1, extended: false },
    LengthCode { base: 11, extra_bits: 1, extended: false },
    LengthCode { base: 13, extra_bits: 1, extended: false },
    LengthCode { base: 15, extra_bits: 1, extended: false },
    LengthCode { base: 17, extra_bits: 2, extended: false },
    LengthCode { base: 21, extra_bits: 2, extended: false },
    LengthCode { base: 25, extra_bits: 2, extended: false },
    LengthCode { base: 29, extra_bits: 3, extended: false },
    LengthCode { base: 37, extra_bits: 3, extended: false },
    LengthCode { base: 45, extra_bits: 4, extended: false },
    LengthCode { base: 61, extra_bits: 5, extended: false },
    LengthCode { base: 93, extra_bits: 6, extended: false },
    LengthCode { base: 157, extra_bits: 7, extended: true },
];

#[rustfmt::skip]
const EXPLICIT_DISTANCES: [DistanceCode; EXPLICIT_DISTANCE_CLASS_COUNT] = [
    DistanceCode { base: 0, extra_bits: 4 },
    DistanceCode { base: 16, extra_bits: 4 },
    DistanceCode { base: 32, extra_bits: 5 },
    DistanceCode { base: 64, extra_bits: 6 },
    DistanceCode { base: 128, extra_bits: 7 },
    DistanceCode { base: 256, extra_bits: 8 },
    DistanceCode { base: 512, extra_bits: 8 },
    DistanceCode { base: 768, extra_bits: 8 },
    DistanceCode { base: 1024, extra_bits: 9 },
    DistanceCode { base: 1536, extra_bits: 9 },
    DistanceCode { base: 2048, extra_bits: 10 },
    DistanceCode { base: 3072, extra_bits: 10 },
    DistanceCode { base: 4096, extra_bits: 10 },
    DistanceCode { base: 5120, extra_bits: 10 },
    DistanceCode { base: 6144, extra_bits: 11 },
    DistanceCode { base: 8192, extra_bits: 12 },
    DistanceCode { base: 12288, extra_bits: 12 },
    DistanceCode { base: 16384, extra_bits: 13 },
    DistanceCode { base: 24576, extra_bits: 13 },
    DistanceCode { base: 32768, extra_bits: 14 },
    DistanceCode { base: 49152, extra_bits: 14 },
    DistanceCode { base: 65536, extra_bits: 15 },
    DistanceCode { base: 98304, extra_bits: 15 },
];

#[inline(always)]
pub fn classify_symbol(symbol: usize) -> Result<SymbolCode, Error> {
    if symbol < LITERAL_SYMBOLS {
        return Ok(SymbolCode::Literal(symbol as u8));
    }

    if symbol >= SYMBOL_COUNT {
        return Err(Error::InvalidSymbol(symbol));
    }

    let token = symbol - LITERAL_SYMBOLS;
    if token < RECENT_TOKEN_COUNT {
        return Ok(SymbolCode::Recent {
            selector_bits: 2,
            length: RECENT_LENGTHS[token],
        });
    }

    let explicit = token - RECENT_TOKEN_COUNT;
    let length_index = explicit / EXPLICIT_DISTANCE_CLASS_COUNT;
    let distance_index = explicit % EXPLICIT_DISTANCE_CLASS_COUNT;
    Ok(SymbolCode::Explicit {
        distance: EXPLICIT_DISTANCES[distance_index],
        length: EXPLICIT_LENGTHS[length_index],
    })
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Error {
    Truncated,
    InvalidSymbolCount(usize),
    InvalidSymbol(usize),
    SymbolsNotIncreasing,
    InvalidCodeLength(u8),
    InvalidRun,
    InvalidRiceBits(u8),
    NonCanonical,
    MissingModel,
    EmptyModel,
    InvalidHuffmanCode,
    InvalidMatchDistance { distance: usize, produced: usize },
    OutputOverrun { requested: usize, remaining: usize },
    TrailingPayloadBits(usize),
    NonZeroPadding,
    UnsupportedDecoder(crate::DecoderType),
    Frame(crate::Error),
}

impl core::fmt::Display for Error {
    fn fmt(&self, f: &mut core::fmt::Formatter<'_>) -> core::fmt::Result {
        write!(f, "{self:?}")
    }
}

impl std::error::Error for Error {}

impl From<crate::Error> for Error {
    fn from(value: crate::Error) -> Self {
        Self::Frame(value)
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct HuffmanModel {
    pub code_lengths: Vec<u8>,
    pub used_symbols: usize,
    pub top_symbol: Option<usize>,
    pub min_code_len: u8,
    pub max_code_len: u8,
    pub one_char: Option<usize>,
    pub consumed_bits: usize,
}

impl HuffmanModel {
    pub fn parse_lzh(input: &[u8]) -> Result<Self, Error> {
        Self::parse(input, SYMBOL_COUNT, MAX_CODE_LEN)
    }

    pub fn parse(input: &[u8], symbol_count: usize, max_code_len: u8) -> Result<Self, Error> {
        if symbol_count < 2 {
            return Err(Error::InvalidSymbolCount(symbol_count));
        }

        let symbol_bits = usize::BITS as usize - (symbol_count - 1).leading_zeros() as usize;
        let mut bits = MsbBitReader::new(input);
        let method = bits.read_bit()?;
        let mut lengths = vec![0u8; symbol_count];
        let mut one_char = None;

        if !method {
            let used = bits.read_bits(symbol_bits)? as usize;
            if used > symbol_count {
                return Err(Error::InvalidSymbolCount(used));
            }

            if used == 0 {
                return Ok(Self {
                    code_lengths: lengths,
                    used_symbols: 0,
                    top_symbol: None,
                    min_code_len: 0,
                    max_code_len: 0,
                    one_char: None,
                    consumed_bits: bits.position(),
                });
            }

            if used == 1 {
                let symbol = bits.read_bits(symbol_bits)? as usize;
                if symbol >= symbol_count {
                    return Err(Error::InvalidSymbol(symbol));
                }
                one_char = Some(symbol);
                return Ok(Self {
                    code_lengths: lengths,
                    used_symbols: 1,
                    top_symbol: Some(symbol),
                    min_code_len: 0,
                    max_code_len: 0,
                    one_char,
                    consumed_bits: bits.position(),
                });
            }

            let len_bits = bits.read_bits(3)? as usize;
            let mut previous = None;
            for _ in 0..used {
                let symbol = bits.read_bits(symbol_bits)? as usize;
                if symbol >= symbol_count {
                    return Err(Error::InvalidSymbol(symbol));
                }
                if previous.is_some_and(|p| symbol <= p) {
                    return Err(Error::SymbolsNotIncreasing);
                }
                previous = Some(symbol);

                let encoded_len = if len_bits == 0 {
                    0
                } else {
                    bits.read_bits(len_bits)? as u8
                };
                let code_len = encoded_len + 1;
                if code_len > max_code_len {
                    return Err(Error::InvalidCodeLength(code_len));
                }
                lengths[symbol] = code_len;
            }
        } else {
            let rice_bits = bits.read_bits(2)? as u8;
            if rice_bits > 3 {
                return Err(Error::InvalidRiceBits(rice_bits));
            }
            let first_is_on = bits.read_bit()?;
            let mut predictor_state = (symbol_bits as i32) * 4;
            let mut symbol = 0usize;

            if !first_is_on {
                let zero_run = bits.read_exp_golomb(1)? as usize + 1;
                symbol = symbol.checked_add(zero_run).ok_or(Error::InvalidRun)?;
                if symbol > symbol_count {
                    return Err(Error::InvalidRun);
                }
            }

            while symbol < symbol_count {
                let nonzero_run = bits.read_exp_golomb(1)? as usize + 1;
                if nonzero_run > symbol_count - symbol {
                    return Err(Error::InvalidRun);
                }

                for _ in 0..nonzero_run {
                    let folded_delta = bits.read_rice(rice_bits)? as i32;
                    let delta = unfold_signed(folded_delta);
                    let predicted = (predictor_state + 2) >> 2;
                    let code_len_i32 = predicted + delta;
                    if !(1..=i32::from(max_code_len)).contains(&code_len_i32) {
                        return Err(Error::InvalidCodeLength(
                            u8::try_from(code_len_i32.max(0)).unwrap_or(u8::MAX),
                        ));
                    }
                    let code_len = code_len_i32 as u8;
                    lengths[symbol] = code_len;
                    predictor_state = ((predictor_state * 3 + 2) >> 2) + code_len_i32;
                    symbol += 1;
                }

                if symbol == symbol_count {
                    break;
                }

                let zero_run = bits.read_exp_golomb(1)? as usize + 1;
                if zero_run > symbol_count - symbol {
                    return Err(Error::InvalidRun);
                }
                symbol += zero_run;
            }
        }

        let used_symbols = lengths.iter().filter(|&&len| len != 0).count();
        let top_symbol = lengths.iter().rposition(|&len| len != 0);
        let min_code_len = lengths
            .iter()
            .copied()
            .filter(|&len| len != 0)
            .min()
            .unwrap_or(0);
        let max_seen = lengths.iter().copied().max().unwrap_or(0);

        if used_symbols >= 2 && !kraft_complete(&lengths, max_seen) {
            return Err(Error::NonCanonical);
        }

        Ok(Self {
            code_lengths: lengths,
            used_symbols,
            top_symbol,
            min_code_len,
            max_code_len: max_seen,
            one_char,
            consumed_bits: bits.position(),
        })
    }
}

#[derive(Debug, Clone, Copy, Default)]
struct FastEntry {
    symbol: u16,
    len: u8,
}

#[derive(Debug, Clone)]
struct CanonicalDecoder {
    counts: [u16; MAX_CODE_LEN as usize + 1],
    first_code: [u32; MAX_CODE_LEN as usize + 1],
    first_symbol: [usize; MAX_CODE_LEN as usize + 1],
    symbols: Vec<u16>,
    fast: [FastEntry; 1 << FAST_DECODE_BITS],
    long_prefix: [i16; 1 << FAST_DECODE_BITS],
    long_tables: Vec<[FastEntry; 1 << (MAX_CODE_LEN - FAST_DECODE_BITS)]>,
    max_len: u8,
    one_char: Option<usize>,
}

impl CanonicalDecoder {
    fn new(model: &HuffmanModel) -> Result<Self, Error> {
        if let Some(one_char) = model.one_char {
            return Ok(Self {
                counts: [0; MAX_CODE_LEN as usize + 1],
                first_code: [0; MAX_CODE_LEN as usize + 1],
                first_symbol: [0; MAX_CODE_LEN as usize + 1],
                symbols: Vec::new(),
                fast: [FastEntry::default(); 1 << FAST_DECODE_BITS],
                long_prefix: [-1; 1 << FAST_DECODE_BITS],
                long_tables: Vec::new(),
                max_len: 0,
                one_char: Some(one_char),
            });
        }
        if model.used_symbols == 0 || model.max_code_len == 0 {
            return Err(Error::EmptyModel);
        }

        let mut counts = [0u16; MAX_CODE_LEN as usize + 1];
        for &len in &model.code_lengths {
            if len != 0 {
                counts[usize::from(len)] += 1;
            }
        }

        let mut first_code = [0u32; MAX_CODE_LEN as usize + 1];
        let mut first_symbol = [0usize; MAX_CODE_LEN as usize + 1];
        let mut code = 0u32;
        let mut symbol_index = 0usize;
        for len in 1..=usize::from(model.max_code_len) {
            code = (code + u32::from(counts[len - 1])) << 1;
            first_code[len] = code;
            first_symbol[len] = symbol_index;
            symbol_index += usize::from(counts[len]);
        }

        let mut symbols = Vec::with_capacity(model.used_symbols);
        for len in 1..=model.max_code_len {
            for (symbol, &symbol_len) in model.code_lengths.iter().enumerate() {
                if symbol_len == len {
                    symbols.push(symbol as u16);
                }
            }
        }
        if symbols.len() != model.used_symbols {
            return Err(Error::NonCanonical);
        }

        let mut fast = [FastEntry::default(); 1 << FAST_DECODE_BITS];
        let mut long_prefix = [-1i16; 1 << FAST_DECODE_BITS];
        let mut long_tables: Vec<[FastEntry; 1 << (MAX_CODE_LEN - FAST_DECODE_BITS)]> = Vec::new();
        let mut next_code = first_code;
        for (symbol, &len) in model.code_lengths.iter().enumerate() {
            if len == 0 {
                continue;
            }
            let code = next_code[usize::from(len)];
            next_code[usize::from(len)] += 1;
            let entry = FastEntry {
                symbol: symbol as u16,
                len,
            };
            if len <= FAST_DECODE_BITS {
                let shift = usize::from(FAST_DECODE_BITS - len);
                let start = (code as usize) << shift;
                let end = start + (1usize << shift);
                fast[start..end].fill(entry);
            } else {
                let suffix_bits = usize::from(len - FAST_DECODE_BITS);
                let prefix = (code as usize) >> suffix_bits;
                let table_index = if long_prefix[prefix] >= 0 {
                    long_prefix[prefix] as usize
                } else {
                    let index = long_tables.len();
                    if index > i16::MAX as usize {
                        return Err(Error::NonCanonical);
                    }
                    long_tables
                        .push([FastEntry::default(); 1 << (MAX_CODE_LEN - FAST_DECODE_BITS)]);
                    long_prefix[prefix] = index as i16;
                    index
                };
                let suffix_mask = (1usize << suffix_bits) - 1;
                let suffix = (code as usize) & suffix_mask;
                let fill_shift = usize::from(MAX_CODE_LEN - len);
                let start = suffix << fill_shift;
                let end = start + (1usize << fill_shift);
                long_tables[table_index][start..end].fill(entry);
            }
        }

        Ok(Self {
            counts,
            first_code,
            first_symbol,
            symbols,
            fast,
            long_prefix,
            long_tables,
            max_len: model.max_code_len,
            one_char: None,
        })
    }

    #[inline(always)]
    fn decode(&self, bits: &mut MsbBitReader<'_>) -> Result<usize, Error> {
        if let Some(symbol) = self.one_char {
            return Ok(symbol);
        }

        if bits.remaining_bits() >= usize::from(FAST_DECODE_BITS) {
            let prefix = bits.peek_bits(usize::from(FAST_DECODE_BITS))? as usize;
            let entry = self.fast[prefix];
            if entry.len != 0 {
                bits.skip_bits(usize::from(entry.len))?;
                return Ok(usize::from(entry.symbol));
            }

            if bits.remaining_bits() >= usize::from(MAX_CODE_LEN) {
                let table_index = self.long_prefix[prefix];
                if table_index >= 0 {
                    let window = bits.peek_bits(usize::from(MAX_CODE_LEN))? as usize;
                    let suffix_mask = (1usize << (MAX_CODE_LEN - FAST_DECODE_BITS)) - 1;
                    let long_entry = self.long_tables[table_index as usize][window & suffix_mask];
                    if long_entry.len != 0 {
                        bits.skip_bits(usize::from(long_entry.len))?;
                        return Ok(usize::from(long_entry.symbol));
                    }
                }
            }
        }

        // Only the final <16 payload bits should normally reach this proven
        // canonical fallback.
        let mut code = 0u32;
        for len in 1..=usize::from(self.max_len) {
            code = (code << 1) | u32::from(bits.read_bit()?);
            let first = self.first_code[len];
            let count = u32::from(self.counts[len]);
            if code >= first && code - first < count {
                let index = self.first_symbol[len] + (code - first) as usize;
                return self
                    .symbols
                    .get(index)
                    .copied()
                    .map(usize::from)
                    .ok_or(Error::InvalidHuffmanCode);
            }
        }
        Err(Error::InvalidHuffmanCode)
    }
}

#[derive(Debug, Default, Clone)]
pub struct Decoder {
    model: Option<HuffmanModel>,
    huffman: Option<CanonicalDecoder>,
}

impl Decoder {
    pub const fn new() -> Self {
        Self {
            model: None,
            huffman: None,
        }
    }

    pub fn reset(&mut self) {
        self.model = None;
        self.huffman = None;
    }

    pub fn decode_quantum_into(
        &mut self,
        payload: &[u8],
        output: &mut [u8],
        output_pos: &mut usize,
        raw_len: usize,
        has_new_model: bool,
    ) -> Result<(), Error> {
        let mut payload_offset = 0usize;
        if has_new_model {
            let model = HuffmanModel::parse_lzh(payload)?;
            payload_offset = model.consumed_bits.div_ceil(8);
            if payload_offset > payload.len() {
                return Err(Error::Truncated);
            }
            let huffman = CanonicalDecoder::new(&model)?;
            self.model = Some(model);
            self.huffman = Some(huffman);
        }

        let huffman = self.huffman.as_ref().ok_or(Error::MissingModel)?;
        let mut bits = MsbBitReader::new(&payload[payload_offset..]);
        let output_end = output_pos
            .checked_add(raw_len)
            .ok_or(Error::OutputOverrun {
                requested: raw_len,
                remaining: 0,
            })?;
        if output_end > output.len() {
            return Err(Error::OutputOverrun {
                requested: raw_len,
                remaining: output.len().saturating_sub(*output_pos),
            });
        }
        let mut recent = [20usize, 24, 28, 32];

        while *output_pos < output_end {
            let symbol = huffman.decode(&mut bits)?;
            match classify_symbol(symbol)? {
                SymbolCode::Literal(byte) => {
                    output[*output_pos] = byte;
                    *output_pos += 1;
                }
                SymbolCode::Recent {
                    selector_bits,
                    length,
                } => {
                    let selector = bits.read_bits(usize::from(selector_bits))? as usize;
                    if selector >= recent.len() {
                        return Err(Error::InvalidRun);
                    }
                    let distance = recent[selector];
                    recent[..=selector].rotate_right(1);
                    let match_len = decode_length(&mut bits, length)?;
                    copy_match_into(output, output_pos, output_end, distance, match_len)?;
                }
                SymbolCode::Explicit { distance, length } => {
                    let match_distance = usize::try_from(distance.base)
                        .map_err(|_| Error::InvalidRun)?
                        + bits.read_bits(usize::from(distance.extra_bits))? as usize
                        + 1;

                    // Oodle 2.3 LZH does not cache the shortest explicit
                    // distance class (1..=16). Longer explicit distances are
                    // inserted at rank 1 while rank 0 is preserved.
                    if distance.base != 0 {
                        recent[3] = recent[2];
                        recent[2] = recent[1];
                        recent[1] = match_distance;
                    }

                    let match_len = decode_length(&mut bits, length)?;
                    copy_match_into(output, output_pos, output_end, match_distance, match_len)?;
                }
            }
        }

        let remaining_bits = bits.remaining_bits();
        if remaining_bits > 7 {
            return Err(Error::TrailingPayloadBits(remaining_bits));
        }
        if remaining_bits != 0 && bits.read_bits(remaining_bits)? != 0 {
            return Err(Error::NonZeroPadding);
        }

        Ok(())
    }
}

fn decode_length(bits: &mut MsbBitReader<'_>, code: LengthCode) -> Result<usize, Error> {
    let base = usize::from(code.base);
    if code.extra_bits == 0 {
        return Ok(base);
    }
    if !code.extended {
        return Ok(base + bits.read_bits(usize::from(code.extra_bits))? as usize);
    }

    if !bits.read_bit()? {
        return Ok(157 + bits.read_bits(6)? as usize);
    }
    if !bits.read_bit()? {
        return Ok(221 + bits.read_bits(7)? as usize);
    }
    if !bits.read_bit()? {
        return Ok(349 + bits.read_bits(8)? as usize);
    }
    if !bits.read_bit()? {
        return Ok(605 + bits.read_bits(10)? as usize);
    }
    Ok(1629 + bits.read_bits(14)? as usize)
}

#[inline(always)]
fn copy_match_into(
    output: &mut [u8],
    output_pos: &mut usize,
    output_end: usize,
    distance: usize,
    length: usize,
) -> Result<(), Error> {
    if distance == 0 || distance > *output_pos {
        return Err(Error::InvalidMatchDistance {
            distance,
            produced: *output_pos,
        });
    }
    let remaining = output_end - *output_pos;
    if length > remaining {
        return Err(Error::OutputOverrun {
            requested: length,
            remaining,
        });
    }
    if length == 0 {
        return Ok(());
    }

    let match_start = *output_pos;
    let source_start = match_start - distance;
    let seed = length.min(distance);
    output.copy_within(source_start..source_start + seed, match_start);
    *output_pos += seed;

    // Preserve LZ overlap semantics by doubling from already-produced output.
    // This takes O(log(length)) bulk copies for tiny match distances.
    let mut produced = seed;
    while produced < length {
        let chunk = (length - produced).min(produced);
        output.copy_within(match_start..match_start + chunk, match_start + produced);
        produced += chunk;
        *output_pos += chunk;
    }
    Ok(())
}

pub fn decode_stream_into(input: &[u8], output: &mut [u8]) -> Result<(), Error> {
    let expected_raw_len = output.len();
    let spans = crate::scan_frame(input, expected_raw_len)?;
    let mut decoder = Decoder::new();
    let mut output_pos = 0usize;

    for span in spans {
        if span.block.decoder_type != crate::DecoderType::Lzh {
            return Err(Error::UnsupportedDecoder(span.block.decoder_type));
        }
        if span.output_offset.is_multiple_of(crate::BLOCK_LEN) && span.block.restart_decoder {
            decoder.reset();
        }

        match span.kind {
            crate::QuantumKind::Compressed {
                stored_size, flag1, ..
            } => {
                let header = crate::parse_quantum_header(
                    &input[span.input_offset..],
                    span.block,
                    span.raw_len,
                )?;
                let payload_start = span.input_offset + header.header_len;
                let payload_end = payload_start + stored_size;
                let payload = input
                    .get(payload_start..payload_end)
                    .ok_or(Error::Truncated)?;
                decoder.decode_quantum_into(
                    payload,
                    output,
                    &mut output_pos,
                    span.raw_len,
                    flag1,
                )?;
            }
            crate::QuantumKind::Raw => {
                let (payload_start, payload_end) = if span.block.uncompressed {
                    (
                        span.input_offset,
                        span.input_offset
                            .checked_add(span.raw_len)
                            .ok_or(Error::Truncated)?,
                    )
                } else {
                    let header = crate::parse_quantum_header(
                        &input[span.input_offset..],
                        span.block,
                        span.raw_len,
                    )?;
                    let start = span.input_offset + header.header_len;
                    (
                        start,
                        start.checked_add(span.raw_len).ok_or(Error::Truncated)?,
                    )
                };
                let payload = input
                    .get(payload_start..payload_end)
                    .ok_or(Error::Truncated)?;
                let end = output_pos
                    .checked_add(span.raw_len)
                    .ok_or(Error::OutputOverrun {
                        requested: span.raw_len,
                        remaining: 0,
                    })?;
                output
                    .get_mut(output_pos..end)
                    .ok_or(Error::OutputOverrun {
                        requested: span.raw_len,
                        remaining: output.len().saturating_sub(output_pos),
                    })?
                    .copy_from_slice(payload);
                output_pos = end;
            }
            crate::QuantumKind::Memset { value } => {
                let end = output_pos
                    .checked_add(span.raw_len)
                    .ok_or(Error::OutputOverrun {
                        requested: span.raw_len,
                        remaining: 0,
                    })?;
                output
                    .get_mut(output_pos..end)
                    .ok_or(Error::OutputOverrun {
                        requested: span.raw_len,
                        remaining: output.len().saturating_sub(output_pos),
                    })?
                    .fill(value);
                output_pos = end;
            }
            crate::QuantumKind::WholeMatch { distance } => {
                let output_end =
                    output_pos
                        .checked_add(span.raw_len)
                        .ok_or(Error::OutputOverrun {
                            requested: span.raw_len,
                            remaining: 0,
                        })?;
                copy_match_into(output, &mut output_pos, output_end, distance, span.raw_len)?;
            }
        }
    }

    if output_pos != expected_raw_len {
        return Err(Error::OutputOverrun {
            requested: expected_raw_len,
            remaining: expected_raw_len.saturating_sub(output_pos),
        });
    }
    Ok(())
}

pub fn decode_stream(input: &[u8], expected_raw_len: usize) -> Result<Vec<u8>, Error> {
    let mut output = vec![0u8; expected_raw_len];
    decode_stream_into(input, &mut output)?;
    Ok(output)
}

fn kraft_complete(lengths: &[u8], max_len: u8) -> bool {
    if max_len == 0 {
        return false;
    }
    let target = 1u64 << max_len;
    let mut sum = 0u64;
    for &len in lengths {
        if len != 0 {
            sum = match sum.checked_add(1u64 << (max_len - len)) {
                Some(value) => value,
                None => return false,
            };
        }
    }
    sum == target
}

#[inline]
fn unfold_signed(value: i32) -> i32 {
    if (value & 1) != 0 {
        -((value + 1) >> 1)
    } else {
        value >> 1
    }
}

#[derive(Debug, Clone, Copy)]
struct MsbBitReader<'a> {
    input: &'a [u8],
    bit_pos: usize,
}

impl<'a> MsbBitReader<'a> {
    const fn new(input: &'a [u8]) -> Self {
        Self { input, bit_pos: 0 }
    }

    const fn position(self) -> usize {
        self.bit_pos
    }

    fn remaining_bits(&self) -> usize {
        self.input
            .len()
            .saturating_mul(8)
            .saturating_sub(self.bit_pos)
    }

    fn read_bit(&mut self) -> Result<bool, Error> {
        Ok(self.read_bits(1)? != 0)
    }

    #[inline(always)]
    fn peek_bits(&self, count: usize) -> Result<u64, Error> {
        if count > 64 || self.bit_pos.saturating_add(count) > self.input.len().saturating_mul(8) {
            return Err(Error::Truncated);
        }
        if count == 0 {
            return Ok(0);
        }

        let byte_pos = self.bit_pos >> 3;
        let bit_offset = self.bit_pos & 7;

        // The payload hot path never asks for more than 16 bits. An aligned
        // 64-bit big-endian window lets those reads collapse to a load+shifts.
        if count <= 56 && byte_pos + 8 <= self.input.len() {
            let word = u64::from_be_bytes(
                self.input[byte_pos..byte_pos + 8]
                    .try_into()
                    .map_err(|_| Error::Truncated)?,
            );
            let shifted = word << bit_offset;
            return Ok(shifted >> (64 - count));
        }

        // Boundary/large-read fallback. This executes mainly while reading the
        // final bytes of a quantum and keeps the general 64-bit API intact.
        let byte_count = (bit_offset + count).div_ceil(8);
        let mut acc = 0u128;
        for &byte in self
            .input
            .get(byte_pos..byte_pos + byte_count)
            .ok_or(Error::Truncated)?
        {
            acc = (acc << 8) | u128::from(byte);
        }
        let shift = byte_count * 8 - bit_offset - count;
        let mask = if count == 64 {
            u128::from(u64::MAX)
        } else {
            (1u128 << count) - 1
        };
        Ok(((acc >> shift) & mask) as u64)
    }

    #[inline(always)]
    fn skip_bits(&mut self, count: usize) -> Result<(), Error> {
        if self.bit_pos.saturating_add(count) > self.input.len().saturating_mul(8) {
            return Err(Error::Truncated);
        }
        self.bit_pos += count;
        Ok(())
    }

    #[inline(always)]
    fn read_bits(&mut self, count: usize) -> Result<u64, Error> {
        let value = self.peek_bits(count)?;
        self.bit_pos += count;
        Ok(value)
    }

    fn read_unary(&mut self) -> Result<u32, Error> {
        let mut zeros = 0u32;
        while !self.read_bit()? {
            zeros = zeros.checked_add(1).ok_or(Error::InvalidRun)?;
        }
        Ok(zeros)
    }

    fn read_rice(&mut self, rice_bits: u8) -> Result<u32, Error> {
        let quotient = self.read_unary()?;
        let remainder = self.read_bits(usize::from(rice_bits))? as u32;
        quotient
            .checked_shl(u32::from(rice_bits))
            .and_then(|head| head.checked_add(remainder))
            .ok_or(Error::InvalidRun)
    }

    fn read_exp_golomb(&mut self, suffix_bits: u8) -> Result<u32, Error> {
        let zeros = self.read_unary()?;
        if zeros >= 32 {
            return Err(Error::InvalidRun);
        }
        let information = self.read_bits(zeros as usize)? as u32;
        let head = ((1u32 << zeros) - 1)
            .checked_add(information)
            .ok_or(Error::InvalidRun)?;
        let suffix = self.read_bits(usize::from(suffix_bits))? as u32;
        head.checked_shl(u32::from(suffix_bits))
            .and_then(|value| value.checked_add(suffix))
            .ok_or(Error::InvalidRun)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn signed_fold_inverse_examples() {
        assert_eq!(unfold_signed(0), 0);
        assert_eq!(unfold_signed(1), -1);
        assert_eq!(unfold_signed(2), 1);
        assert_eq!(unfold_signed(3), -2);
        assert_eq!(unfold_signed(10), 5);
    }

    #[test]
    fn bit_primitives_are_msb_first() {
        let mut bits = MsbBitReader::new(&[0b1011_0010, 0b0110_0000]);
        assert_eq!(bits.read_bits(4).unwrap(), 0b1011);
        assert_eq!(bits.read_bits(4).unwrap(), 0b0010);
        assert_eq!(bits.read_bits(3).unwrap(), 0b011);
    }

    #[test]
    fn canonical_kraft_validation() {
        assert!(kraft_complete(&[1, 2, 2], 2));
        assert!(!kraft_complete(&[2, 2], 2));
    }

    #[test]
    fn lzh_alphabet_decomposes_exactly() {
        assert_eq!(LITERAL_SYMBOLS + TOKEN_SYMBOLS, SYMBOL_COUNT);
        assert_eq!(TOKEN_SYMBOLS, 457);

        assert_eq!(classify_symbol(0).unwrap(), SymbolCode::Literal(0));
        assert_eq!(classify_symbol(255).unwrap(), SymbolCode::Literal(255));

        assert_eq!(
            classify_symbol(256).unwrap(),
            SymbolCode::Recent {
                selector_bits: 2,
                length: LengthCode {
                    base: 2,
                    extra_bits: 0,
                    extended: false,
                },
            }
        );
        assert_eq!(
            classify_symbol(275).unwrap(),
            SymbolCode::Recent {
                selector_bits: 2,
                length: LengthCode {
                    base: 157,
                    extra_bits: 6,
                    extended: true,
                },
            }
        );

        assert_eq!(
            classify_symbol(276).unwrap(),
            SymbolCode::Explicit {
                distance: DistanceCode {
                    base: 0,
                    extra_bits: 4,
                },
                length: LengthCode {
                    base: 3,
                    extra_bits: 0,
                    extended: false,
                },
            }
        );
        assert_eq!(
            classify_symbol(712).unwrap(),
            SymbolCode::Explicit {
                distance: DistanceCode {
                    base: 98304,
                    extra_bits: 15,
                },
                length: LengthCode {
                    base: 157,
                    extra_bits: 7,
                    extended: true,
                },
            }
        );
    }
}
