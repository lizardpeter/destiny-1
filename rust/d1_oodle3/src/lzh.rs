//! Clean-room decoder primitives for the legacy Oodle LZH stream used by Destiny 1.
//!
//! This module starts with the transmitted canonical-Huffman model.  The retail
//! Oodle 2.3 runtime uses a 713-symbol alphabet, a 10-bit fast-decode prefix,
//! and permits code lengths through 16 bits.

pub const SYMBOL_COUNT: usize = 713;
pub const FAST_DECODE_BITS: u8 = 11;
pub const MAX_CODE_LEN: u8 = 16;

pub const LITERAL_SYMBOLS: usize = 256;
pub const RECENT_TOKEN_COUNT: usize = 20;
pub const EXPLICIT_LENGTH_CLASS_COUNT: usize = 19;
pub const EXPLICIT_DISTANCE_CLASS_COUNT: usize = 23;
pub const TOKEN_SYMBOLS: usize =
    RECENT_TOKEN_COUNT + EXPLICIT_LENGTH_CLASS_COUNT * EXPLICIT_DISTANCE_CLASS_COUNT;

#[cfg(feature = "profile")]
mod profile {
    use std::sync::atomic::{AtomicU64, Ordering};

    #[derive(Debug, Clone, Copy, Default)]
    pub struct ProfileSnapshot {
        pub models: u64,
        pub model_symbols: u64,
        pub quanta: u64,
        pub huffman_fast: u64,
        pub huffman_long: u64,
        pub huffman_tail: u64,
        pub literals: u64,
        pub recent_matches: u64,
        pub explicit_matches: u64,
        pub distance_1: u64,
        pub distance_2: u64,
        pub distance_3: u64,
        pub distance_4: u64,
        pub distance_5_8: u64,
        pub distance_9_16: u64,
        pub distance_17_32: u64,
        pub distance_33_plus: u64,
        pub length_2_4: u64,
        pub length_5_8: u64,
        pub length_9_16: u64,
        pub length_17_32: u64,
        pub length_33_64: u64,
        pub length_65_plus: u64,
        pub refill_32: u64,
        pub refill_8: u64,
    }

    static MODELS: AtomicU64 = AtomicU64::new(0);
    static MODEL_SYMBOLS: AtomicU64 = AtomicU64::new(0);
    static QUANTA: AtomicU64 = AtomicU64::new(0);
    static HUFFMAN_FAST: AtomicU64 = AtomicU64::new(0);
    static HUFFMAN_LONG: AtomicU64 = AtomicU64::new(0);
    static HUFFMAN_TAIL: AtomicU64 = AtomicU64::new(0);
    static LITERALS: AtomicU64 = AtomicU64::new(0);
    static RECENT_MATCHES: AtomicU64 = AtomicU64::new(0);
    static EXPLICIT_MATCHES: AtomicU64 = AtomicU64::new(0);
    static DISTANCE: [AtomicU64; 8] = [
        AtomicU64::new(0), AtomicU64::new(0), AtomicU64::new(0), AtomicU64::new(0),
        AtomicU64::new(0), AtomicU64::new(0), AtomicU64::new(0), AtomicU64::new(0),
    ];
    static LENGTH: [AtomicU64; 6] = [
        AtomicU64::new(0), AtomicU64::new(0), AtomicU64::new(0),
        AtomicU64::new(0), AtomicU64::new(0), AtomicU64::new(0),
    ];
    static REFILL_32: AtomicU64 = AtomicU64::new(0);
    static REFILL_8: AtomicU64 = AtomicU64::new(0);

    #[inline(always)]
    fn inc(a: &AtomicU64) { a.fetch_add(1, Ordering::Relaxed); }

    pub(super) fn model(used: usize) {
        inc(&MODELS);
        MODEL_SYMBOLS.fetch_add(used as u64, Ordering::Relaxed);
    }
    pub(super) fn quantum() { inc(&QUANTA); }
    pub(super) fn huffman_fast() { inc(&HUFFMAN_FAST); }
    pub(super) fn huffman_long() { inc(&HUFFMAN_LONG); }
    pub(super) fn huffman_tail() { inc(&HUFFMAN_TAIL); }
    pub(super) fn literal() { inc(&LITERALS); }
    pub(super) fn recent_match() { inc(&RECENT_MATCHES); }
    pub(super) fn explicit_match() { inc(&EXPLICIT_MATCHES); }
    pub(super) fn distance(v: usize) {
        let i = match v {
            1 => 0, 2 => 1, 3 => 2, 4 => 3,
            5..=8 => 4, 9..=16 => 5, 17..=32 => 6, _ => 7,
        };
        inc(&DISTANCE[i]);
    }
    pub(super) fn length(v: usize) {
        let i = match v {
            0..=4 => 0, 5..=8 => 1, 9..=16 => 2,
            17..=32 => 3, 33..=64 => 4, _ => 5,
        };
        inc(&LENGTH[i]);
    }
    pub(super) fn refill32() { inc(&REFILL_32); }
    pub(super) fn refill8() { inc(&REFILL_8); }

    pub fn reset() {
        for a in [
            &MODELS, &MODEL_SYMBOLS, &QUANTA, &HUFFMAN_FAST, &HUFFMAN_LONG, &HUFFMAN_TAIL,
            &LITERALS, &RECENT_MATCHES, &EXPLICIT_MATCHES, &REFILL_32, &REFILL_8,
        ] { a.store(0, Ordering::Relaxed); }
        for a in &DISTANCE { a.store(0, Ordering::Relaxed); }
        for a in &LENGTH { a.store(0, Ordering::Relaxed); }
    }

    pub fn snapshot() -> ProfileSnapshot {
        let g = |a: &AtomicU64| a.load(Ordering::Relaxed);
        ProfileSnapshot {
            models: g(&MODELS), model_symbols: g(&MODEL_SYMBOLS), quanta: g(&QUANTA),
            huffman_fast: g(&HUFFMAN_FAST), huffman_long: g(&HUFFMAN_LONG),
            huffman_tail: g(&HUFFMAN_TAIL), literals: g(&LITERALS),
            recent_matches: g(&RECENT_MATCHES), explicit_matches: g(&EXPLICIT_MATCHES),
            distance_1: g(&DISTANCE[0]), distance_2: g(&DISTANCE[1]),
            distance_3: g(&DISTANCE[2]), distance_4: g(&DISTANCE[3]),
            distance_5_8: g(&DISTANCE[4]), distance_9_16: g(&DISTANCE[5]),
            distance_17_32: g(&DISTANCE[6]), distance_33_plus: g(&DISTANCE[7]),
            length_2_4: g(&LENGTH[0]), length_5_8: g(&LENGTH[1]),
            length_9_16: g(&LENGTH[2]), length_17_32: g(&LENGTH[3]),
            length_33_64: g(&LENGTH[4]), length_65_plus: g(&LENGTH[5]),
            refill_32: g(&REFILL_32), refill_8: g(&REFILL_8),
        }
    }
}

#[cfg(feature = "profile")]
pub use profile::{reset as profile_reset, snapshot as profile_snapshot, ProfileSnapshot};

#[cfg(feature = "stage_profile")]
mod stage_profile {
    use std::sync::atomic::{AtomicU64, Ordering};

    #[derive(Debug, Clone, Copy, Default)]
    pub struct StageProfileSnapshot {
        pub model_parse_ns: u64,
        pub table_build_ns: u64,
        pub payload_ns: u64,
        pub models: u64,
        pub quanta: u64,
    }

    static MODEL_PARSE_NS: AtomicU64 = AtomicU64::new(0);
    static TABLE_BUILD_NS: AtomicU64 = AtomicU64::new(0);
    static PAYLOAD_NS: AtomicU64 = AtomicU64::new(0);
    static MODELS: AtomicU64 = AtomicU64::new(0);
    static QUANTA: AtomicU64 = AtomicU64::new(0);

    #[inline(always)]
    pub(super) fn model_parse(ns: u64) {
        MODEL_PARSE_NS.fetch_add(ns, Ordering::Relaxed);
        MODELS.fetch_add(1, Ordering::Relaxed);
    }

    #[inline(always)]
    pub(super) fn table_build(ns: u64) {
        TABLE_BUILD_NS.fetch_add(ns, Ordering::Relaxed);
    }

    #[inline(always)]
    pub(super) fn payload(ns: u64) {
        PAYLOAD_NS.fetch_add(ns, Ordering::Relaxed);
        QUANTA.fetch_add(1, Ordering::Relaxed);
    }

    pub fn reset() {
        for counter in [
            &MODEL_PARSE_NS,
            &TABLE_BUILD_NS,
            &PAYLOAD_NS,
            &MODELS,
            &QUANTA,
        ] {
            counter.store(0, Ordering::Relaxed);
        }
    }

    pub fn snapshot() -> StageProfileSnapshot {
        let load = |counter: &AtomicU64| counter.load(Ordering::Relaxed);
        StageProfileSnapshot {
            model_parse_ns: load(&MODEL_PARSE_NS),
            table_build_ns: load(&TABLE_BUILD_NS),
            payload_ns: load(&PAYLOAD_NS),
            models: load(&MODELS),
            quanta: load(&QUANTA),
        }
    }
}

#[cfg(feature = "stage_profile")]
pub use stage_profile::{
    reset as stage_profile_reset, snapshot as stage_profile_snapshot, StageProfileSnapshot,
};

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

#[derive(Debug, Clone, Copy)]
#[repr(C)]
struct TokenMeta {
    distance_base: u32,
    length_base: u16,
    distance_info: u8,
    length_info: u8,
}

const TOKEN_RECENT_FLAG: u8 = 0x80;
const TOKEN_EXTENDED_FLAG: u8 = 0x80;

const fn encode_length_info(code: LengthCode) -> u8 {
    code.extra_bits
        | if code.extended {
            TOKEN_EXTENDED_FLAG
        } else {
            0
        }
}

const fn build_token_meta() -> [TokenMeta; TOKEN_SYMBOLS] {
    let mut meta = [TokenMeta {
        distance_base: 0,
        length_base: 0,
        distance_info: 0,
        length_info: 0,
    }; TOKEN_SYMBOLS];

    let mut recent = 0usize;
    while recent < RECENT_TOKEN_COUNT {
        let length = RECENT_LENGTHS[recent];
        meta[recent] = TokenMeta {
            distance_base: 0,
            length_base: length.base,
            distance_info: TOKEN_RECENT_FLAG | 2,
            length_info: encode_length_info(length),
        };
        recent += 1;
    }

    let mut length_index = 0usize;
    while length_index < EXPLICIT_LENGTH_CLASS_COUNT {
        let mut distance_index = 0usize;
        while distance_index < EXPLICIT_DISTANCE_CLASS_COUNT {
            let token =
                RECENT_TOKEN_COUNT + length_index * EXPLICIT_DISTANCE_CLASS_COUNT + distance_index;
            let distance = EXPLICIT_DISTANCES[distance_index];
            let length = EXPLICIT_LENGTHS[length_index];
            meta[token] = TokenMeta {
                distance_base: distance.base,
                length_base: length.base,
                distance_info: distance.extra_bits,
                length_info: encode_length_info(length),
            };
            distance_index += 1;
        }
        length_index += 1;
    }
    meta
}

const TOKEN_META: [TokenMeta; TOKEN_SYMBOLS] = build_token_meta();

#[inline(always)]
const fn token_length(meta: TokenMeta) -> LengthCode {
    LengthCode {
        base: meta.length_base,
        extra_bits: meta.length_info & !TOKEN_EXTENDED_FLAG,
        extended: (meta.length_info & TOKEN_EXTENDED_FLAG) != 0,
    }
}

#[inline(always)]
pub fn classify_symbol(symbol: usize) -> Result<SymbolCode, Error> {
    if symbol < LITERAL_SYMBOLS {
        return Ok(SymbolCode::Literal(symbol as u8));
    }
    if symbol >= SYMBOL_COUNT {
        return Err(Error::InvalidSymbol(symbol));
    }

    let meta = TOKEN_META[symbol - LITERAL_SYMBOLS];
    let length = token_length(meta);
    if (meta.distance_info & TOKEN_RECENT_FLAG) != 0 {
        Ok(SymbolCode::Recent {
            selector_bits: meta.distance_info & !TOKEN_RECENT_FLAG,
            length,
        })
    } else {
        Ok(SymbolCode::Explicit {
            distance: DistanceCode {
                base: meta.distance_base,
                extra_bits: meta.distance_info,
            },
            length,
        })
    }
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

struct FixedLzhModel {
    code_lengths: [u8; SYMBOL_COUNT],
    used_list: [u16; SYMBOL_COUNT],
    counts: [u16; MAX_CODE_LEN as usize + 1],
    used_symbols: usize,
    max_code_len: u8,
    one_char: Option<usize>,
    consumed_bits: usize,
}

impl FixedLzhModel {
    #[inline]
    fn parse(input: &[u8]) -> Result<Self, Error> {
        const SYMBOL_BITS: usize = 10;
        let mut bits = MsbBitReader::new(input);
        let method = bits.read_bit()?;
        let mut lengths = [0u8; SYMBOL_COUNT];
        let mut used_list = [0u16; SYMBOL_COUNT];
        let mut counts = [0u16; MAX_CODE_LEN as usize + 1];
        let mut used_symbols = 0usize;
        let mut max_seen = 0u8;
        let mut one_char = None;

        if !method {
            let used = bits.read_bits(SYMBOL_BITS)? as usize;
            if used > SYMBOL_COUNT {
                return Err(Error::InvalidSymbolCount(used));
            }
            if used == 0 {
                return Ok(Self {
                    code_lengths: lengths,
                    used_list,
                    counts,
                    used_symbols: 0,
                    max_code_len: 0,
                    one_char: None,
                    consumed_bits: bits.position(),
                });
            }
            if used == 1 {
                let symbol = bits.read_bits(SYMBOL_BITS)? as usize;
                if symbol >= SYMBOL_COUNT {
                    return Err(Error::InvalidSymbol(symbol));
                }
                one_char = Some(symbol);
                used_list[0] = symbol as u16;
                return Ok(Self {
                    code_lengths: lengths,
                    used_list,
                    counts,
                    used_symbols: 1,
                    max_code_len: 0,
                    one_char,
                    consumed_bits: bits.position(),
                });
            }

            let len_bits = bits.read_bits(3)? as usize;
            let mut previous = None;
            for _ in 0..used {
                let symbol = bits.read_bits(SYMBOL_BITS)? as usize;
                if symbol >= SYMBOL_COUNT {
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
                if code_len > MAX_CODE_LEN {
                    return Err(Error::InvalidCodeLength(code_len));
                }
                lengths[symbol] = code_len;
                used_list[used_symbols] = symbol as u16;
                counts[usize::from(code_len)] += 1;
                used_symbols += 1;
                max_seen = max_seen.max(code_len);
            }
        } else {
            let rice_bits = bits.read_bits(2)? as u8;
            if rice_bits > 3 {
                return Err(Error::InvalidRiceBits(rice_bits));
            }
            let first_is_on = bits.read_bit()?;
            let mut predictor_state = (SYMBOL_BITS as i32) * 4;
            let mut symbol = 0usize;

            if !first_is_on {
                let zero_run = bits.read_exp_golomb(1)? as usize + 1;
                symbol = symbol.checked_add(zero_run).ok_or(Error::InvalidRun)?;
                if symbol > SYMBOL_COUNT {
                    return Err(Error::InvalidRun);
                }
            }

            while symbol < SYMBOL_COUNT {
                let nonzero_run = bits.read_exp_golomb(1)? as usize + 1;
                if nonzero_run > SYMBOL_COUNT - symbol {
                    return Err(Error::InvalidRun);
                }
                for _ in 0..nonzero_run {
                    let folded_delta = bits.read_rice(rice_bits)? as i32;
                    let delta = unfold_signed(folded_delta);
                    let predicted = (predictor_state + 2) >> 2;
                    let code_len_i32 = predicted + delta;
                    if !(1..=i32::from(MAX_CODE_LEN)).contains(&code_len_i32) {
                        return Err(Error::InvalidCodeLength(
                            u8::try_from(code_len_i32.max(0)).unwrap_or(u8::MAX),
                        ));
                    }
                    let code_len = code_len_i32 as u8;
                    lengths[symbol] = code_len;
                    used_list[used_symbols] = symbol as u16;
                    counts[usize::from(code_len)] += 1;
                    used_symbols += 1;
                    max_seen = max_seen.max(code_len);
                    predictor_state = ((predictor_state * 3 + 2) >> 2) + code_len_i32;
                    symbol += 1;
                }
                if symbol == SYMBOL_COUNT {
                    break;
                }
                let zero_run = bits.read_exp_golomb(1)? as usize + 1;
                if zero_run > SYMBOL_COUNT - symbol {
                    return Err(Error::InvalidRun);
                }
                symbol += zero_run;
            }
        }

        if used_symbols >= 2 {
            let target = 1u64 << max_seen;
            let mut sum = 0u64;
            for len in 1..=usize::from(max_seen) {
                sum += u64::from(counts[len]) << (usize::from(max_seen) - len);
            }
            if sum != target {
                return Err(Error::NonCanonical);
            }
        }

        Ok(Self {
            code_lengths: lengths,
            used_list,
            counts,
            used_symbols,
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
    max_len: u8,
    one_char: Option<usize>,
}

impl CanonicalDecoder {
    fn empty() -> Self {
        Self {
            counts: [0; MAX_CODE_LEN as usize + 1],
            first_code: [0; MAX_CODE_LEN as usize + 1],
            first_symbol: [0; MAX_CODE_LEN as usize + 1],
            symbols: Vec::new(),
            fast: [FastEntry::default(); 1 << FAST_DECODE_BITS],
            max_len: 0,
            one_char: None,
        }
    }

    fn new(model: &HuffmanModel) -> Result<Self, Error> {
        let mut decoder = Self::empty();
        decoder.rebuild(model)?;
        Ok(decoder)
    }

    fn rebuild(&mut self, model: &HuffmanModel) -> Result<(), Error> {
        self.rebuild_parts(
            &model.code_lengths,
            model.used_symbols,
            model.max_code_len,
            model.one_char,
        )
    }

    #[inline]
    fn rebuild_fixed(&mut self, model: &FixedLzhModel) -> Result<(), Error> {
        self.rebuild_parts_with_counts(
            &model.code_lengths,
            model.used_symbols,
            model.max_code_len,
            model.one_char,
            Some(&model.counts),
            Some(&model.used_list[..model.used_symbols]),
        )
    }

    fn rebuild_parts(
        &mut self,
        code_lengths: &[u8],
        used_symbols: usize,
        max_code_len: u8,
        one_char: Option<usize>,
    ) -> Result<(), Error> {
        self.rebuild_parts_with_counts(
            code_lengths,
            used_symbols,
            max_code_len,
            one_char,
            None,
            None,
        )
    }

    fn rebuild_parts_with_counts(
        &mut self,
        code_lengths: &[u8],
        used_symbols: usize,
        max_code_len: u8,
        one_char: Option<usize>,
        precomputed_counts: Option<&[u16; MAX_CODE_LEN as usize + 1]>,
        used_list: Option<&[u16]>,
    ) -> Result<(), Error> {
        self.one_char = one_char;
        self.max_len = max_code_len;
        self.counts.fill(0);
        self.first_code.fill(0);
        self.first_symbol.fill(0);
        self.symbols.clear();
        // Every accepted multi-symbol model is Kraft-complete. Therefore every
        // FAST_DECODE_BITS prefix is overwritten by either a short-code fill
        // or an explicit long-prefix sentinel below; zeroing the full 8 KiB
        // table here is redundant memory traffic.
        if one_char.is_some() {
            return Ok(());
        }
        if used_symbols == 0 || max_code_len == 0 {
            return Err(Error::EmptyModel);
        }

        if let Some(counts) = precomputed_counts {
            self.counts = *counts;
        } else {
            for &len in code_lengths {
                if len != 0 {
                    self.counts[usize::from(len)] += 1;
                }
            }
        }

        let mut code = 0u32;
        let mut symbol_index = 0usize;
        for len in 1..=usize::from(max_code_len) {
            code = (code + u32::from(self.counts[len - 1])) << 1;
            self.first_code[len] = code;
            self.first_symbol[len] = symbol_index;
            symbol_index += usize::from(self.counts[len]);
        }

        if self.symbols.capacity() < used_symbols {
            self.symbols.reserve(used_symbols - self.symbols.capacity());
        }
        self.symbols.resize(used_symbols, 0);

        // Build canonical symbol order and decode tables. Fixed D1 models
        // provide the already-collected nonzero symbol list, avoiding a scan
        // across all 713 possible symbols on every model rebuild.
        let mut next_symbol = self.first_symbol;
        let mut next_code = self.first_code;

        macro_rules! install_symbol {
            ($symbol:expr, $len:expr) => {{
                let symbol = $symbol;
                let len = $len;
                let len_index = usize::from(len);
                let symbol_index = next_symbol[len_index];
                if symbol_index >= used_symbols {
                    return Err(Error::NonCanonical);
                }
                self.symbols[symbol_index] = symbol as u16;
                next_symbol[len_index] += 1;

                let code = next_code[len_index];
                next_code[len_index] += 1;
                let entry = FastEntry {
                    symbol: symbol as u16,
                    len,
                };
                if len <= FAST_DECODE_BITS {
                    let shift = usize::from(FAST_DECODE_BITS - len);
                    let start = (code as usize) << shift;
                    let end = start + (1usize << shift);
                    self.fast[start..end].fill(entry);
                } else {
                    let suffix_bits = usize::from(len - FAST_DECODE_BITS);
                    let prefix = (code as usize) >> suffix_bits;
                    // Long codes are rare in D1. Mark the shared fast prefix as
                    // a canonical fallback instead of constructing a secondary
                    // table for it.
                    self.fast[prefix] = FastEntry::default();
                }
            }};
        }

        if let Some(symbols) = used_list {
            for &symbol in symbols {
                let symbol = usize::from(symbol);
                let len = unsafe { *code_lengths.get_unchecked(symbol) };
                debug_assert!(len != 0);
                install_symbol!(symbol, len);
            }
        } else {
            for (symbol, &len) in code_lengths.iter().enumerate() {
                if len != 0 {
                    install_symbol!(symbol, len);
                }
            }
        }

        Ok(())
    }

    #[inline(always)]
    fn decode_fast_multi(&self, bits: &mut MsbBitReader<'_>) -> usize {
        debug_assert!(self.one_char.is_none());

        bits.ensure_bits_fast(usize::from(FAST_DECODE_BITS));
        let prefix = bits.peek_buffered(usize::from(FAST_DECODE_BITS)) as usize;
        let entry = unsafe { *self.fast.get_unchecked(prefix) };
        if entry.len != 0 {
            #[cfg(feature = "profile")]
            profile::huffman_fast();
            bits.consume_buffered(usize::from(entry.len));
            return usize::from(entry.symbol);
        }

        bits.ensure_bits_fast(usize::from(MAX_CODE_LEN));
        let window = bits.peek_buffered(usize::from(MAX_CODE_LEN)) as u32;
        for len in (usize::from(FAST_DECODE_BITS) + 1)..=usize::from(self.max_len) {
            let code = window >> (usize::from(MAX_CODE_LEN) - len);
            let first = self.first_code[len];
            let count = u32::from(self.counts[len]);
            if code >= first && code - first < count {
                let index = self.first_symbol[len] + (code - first) as usize;
                let symbol = unsafe { *self.symbols.get_unchecked(index) };
                #[cfg(feature = "profile")]
                profile::huffman_long();
                bits.consume_buffered(len);
                return usize::from(symbol);
            }
        }
        debug_assert!(false, "invalid canonical long code");
        0
    }

    #[inline(always)]
    fn decode(&self, bits: &mut MsbBitReader<'_>) -> Result<usize, Error> {
        if let Some(symbol) = self.one_char {
            return Ok(symbol);
        }

        let remaining_bits = bits.remaining_bits();
        if remaining_bits >= usize::from(FAST_DECODE_BITS) {
            bits.ensure_bits(usize::from(FAST_DECODE_BITS))?;
            let prefix = bits.peek_buffered(usize::from(FAST_DECODE_BITS)) as usize;
            let entry = self.fast[prefix];
            if entry.len != 0 {
                #[cfg(feature = "profile")]
                profile::huffman_fast();
                bits.consume_buffered(usize::from(entry.len));
                return Ok(usize::from(entry.symbol));
            }


        }

        let mut code = 0u32;
        for len in 1..=usize::from(self.max_len) {
            code = (code << 1) | u32::from(bits.read_bit()?);
            let first = self.first_code[len];
            let count = u32::from(self.counts[len]);
            if code >= first && code - first < count {
                let index = self.first_symbol[len] + (code - first) as usize;
                #[cfg(feature = "profile")]
                profile::huffman_tail();
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

#[derive(Debug, Clone)]
pub struct Decoder {
    has_model: bool,
    huffman: CanonicalDecoder,
}

impl Default for Decoder {
    fn default() -> Self {
        Self::new()
    }
}

impl Decoder {
    pub fn new() -> Self {
        Self {
            has_model: false,
            huffman: CanonicalDecoder::empty(),
        }
    }

    pub fn reset(&mut self) {
        self.has_model = false;
    }

    #[inline(always)]
    fn decode_quantum_into_impl(
        &mut self,
        payload: &[u8],
        output: &mut [u8],
        output_pos: &mut usize,
        raw_len: usize,
        has_new_model: bool,
    ) -> Result<(), Error> {
        #[cfg(feature = "profile")]
        profile::quantum();
        let mut payload_offset = 0usize;
        if has_new_model {
            #[cfg(feature = "stage_profile")]
            let parse_started = std::time::Instant::now();
            let model = FixedLzhModel::parse(payload)?;
            #[cfg(feature = "stage_profile")]
            stage_profile::model_parse(
                parse_started.elapsed().as_nanos().min(u128::from(u64::MAX)) as u64,
            );

            payload_offset = model.consumed_bits.div_ceil(8);
            if payload_offset > payload.len() {
                return Err(Error::Truncated);
            }
            #[cfg(feature = "profile")]
            profile::model(model.used_symbols);

            #[cfg(feature = "stage_profile")]
            let table_started = std::time::Instant::now();
            self.huffman.rebuild_fixed(&model)?;
            #[cfg(feature = "stage_profile")]
            stage_profile::table_build(
                table_started.elapsed().as_nanos().min(u128::from(u64::MAX)) as u64,
            );

            self.has_model = true;
        }

        if !self.has_model {
            return Err(Error::MissingModel);
        }
        let huffman = &self.huffman;
        let mut bits = MsbBitReader::new(&payload[payload_offset..]);
        let start_pos = *output_pos;
        let output_end = start_pos
            .checked_add(raw_len)
            .ok_or(Error::OutputOverrun {
                requested: raw_len,
                remaining: 0,
            })?;
        if output_end > output.len() {
            return Err(Error::OutputOverrun {
                requested: raw_len,
                remaining: output.len().saturating_sub(start_pos),
            });
        }
        let mut op = start_pos;
        let mut recent = [20usize, 24, 28, 32];

        #[cfg(feature = "stage_profile")]
        let payload_started = std::time::Instant::now();

        if huffman.one_char.is_none() {
            'fast_decode: while op < output_end && bits.has_fast_margin() {
                let mut symbol = huffman.decode_fast_multi(&mut bits);

                // D1 LZH is strongly literal-heavy. Stay in a compact literal-only
                // loop until a match token appears instead of returning through the
                // full token-dispatch loop for every literal.
                while symbol < LITERAL_SYMBOLS {
                    #[cfg(feature = "profile")]
                    profile::literal();
                    unsafe {
                        *output.get_unchecked_mut(op) = symbol as u8;
                    }
                    op += 1;

                    if op >= output_end || !bits.has_fast_margin() {
                        break 'fast_decode;
                    }
                    symbol = huffman.decode_fast_multi(&mut bits);
                }

                debug_assert!(symbol < SYMBOL_COUNT);
                if symbol < LITERAL_SYMBOLS + RECENT_TOKEN_COUNT {
                    #[cfg(feature = "profile")]
                    profile::recent_match();
                    let length =
                        unsafe { *RECENT_LENGTHS.get_unchecked(symbol - LITERAL_SYMBOLS) };
                    let selector = bits.read_bits_fast(2) as usize;
                    let distance = match selector {
                        0 => recent[0],
                        1 => {
                            recent.swap(0, 1);
                            recent[0]
                        }
                        2 => {
                            recent.swap(1, 2);
                            recent.swap(0, 1);
                            recent[0]
                        }
                        3 => {
                            recent.swap(2, 3);
                            recent.swap(1, 2);
                            recent.swap(0, 1);
                            recent[0]
                        }
                        _ => unreachable!(),
                    };
                    let match_len = decode_length_parts_fast(
                        &mut bits,
                        length.base,
                        length.extra_bits,
                        length.extended,
                    );
                    #[cfg(feature = "profile")]
                    {
                        profile::distance(distance);
                        profile::length(match_len);
                    }
                    copy_match_into(output, &mut op, output_end, distance, match_len)?;
                } else {
                    #[cfg(feature = "profile")]
                    profile::explicit_match();
                    let meta = unsafe { *TOKEN_META.get_unchecked(symbol - LITERAL_SYMBOLS) };
                    let match_distance = meta.distance_base as usize
                        + bits.read_bits_fast(usize::from(meta.distance_info)) as usize
                        + 1;

                    if meta.distance_base != 0 {
                        recent[3] = recent[2];
                        recent[2] = recent[1];
                        recent[1] = match_distance;
                    }

                    let match_len = decode_length_parts_fast(
                        &mut bits,
                        meta.length_base,
                        meta.length_info & !TOKEN_EXTENDED_FLAG,
                        (meta.length_info & TOKEN_EXTENDED_FLAG) != 0,
                    );
                    #[cfg(feature = "profile")]
                    {
                        profile::distance(match_distance);
                        profile::length(match_len);
                    }
                    copy_match_into(output, &mut op, output_end, match_distance, match_len)?;
                }
            }

        }

        // Only the final input-boundary region uses the fully checked reader.
        while op < output_end {
            let symbol = huffman.decode(&mut bits)?;
            if symbol < LITERAL_SYMBOLS {
                #[cfg(feature = "profile")]
                profile::literal();
                debug_assert!(op < output_end);
                unsafe {
                    *output.get_unchecked_mut(op) = symbol as u8;
                }
                op += 1;
                continue;
            }
            if symbol >= SYMBOL_COUNT {
                return Err(Error::InvalidSymbol(symbol));
            }

            let meta = TOKEN_META[symbol - LITERAL_SYMBOLS];
            if (meta.distance_info & TOKEN_RECENT_FLAG) != 0 {
                #[cfg(feature = "profile")]
                profile::recent_match();
                let selector_bits = meta.distance_info & !TOKEN_RECENT_FLAG;
                let selector = bits.read_bits(usize::from(selector_bits))? as usize;
                let distance = match selector {
                    0 => recent[0],
                    1 => {
                        recent.swap(0, 1);
                        recent[0]
                    }
                    2 => {
                        recent.swap(1, 2);
                        recent.swap(0, 1);
                        recent[0]
                    }
                    3 => {
                        recent.swap(2, 3);
                        recent.swap(1, 2);
                        recent.swap(0, 1);
                        recent[0]
                    }
                    _ => return Err(Error::InvalidRun),
                };
                let match_len = decode_length_parts(
                    &mut bits,
                    meta.length_base,
                    meta.length_info & !TOKEN_EXTENDED_FLAG,
                    (meta.length_info & TOKEN_EXTENDED_FLAG) != 0,
                )?;
                #[cfg(feature = "profile")]
                {
                    profile::distance(distance);
                    profile::length(match_len);
                }
                copy_match_into(output, &mut op, output_end, distance, match_len)?;
            } else {
                #[cfg(feature = "profile")]
                profile::explicit_match();
                let match_distance = meta.distance_base as usize
                    + bits.read_bits(usize::from(meta.distance_info))? as usize
                    + 1;

                // Oodle 2.3 LZH does not cache the shortest explicit
                // distance class (1..=16). Longer explicit distances are
                // inserted at rank 1 while rank 0 is preserved.
                if meta.distance_base != 0 {
                    recent[3] = recent[2];
                    recent[2] = recent[1];
                    recent[1] = match_distance;
                }

                let match_len = decode_length_parts(
                    &mut bits,
                    meta.length_base,
                    meta.length_info & !TOKEN_EXTENDED_FLAG,
                    (meta.length_info & TOKEN_EXTENDED_FLAG) != 0,
                )?;
                #[cfg(feature = "profile")]
                {
                    profile::distance(match_distance);
                    profile::length(match_len);
                }
                copy_match_into(output, &mut op, output_end, match_distance, match_len)?;
            }
        }

        *output_pos = op;

        let remaining_bits = bits.remaining_bits();
        if remaining_bits > 7 {
            return Err(Error::TrailingPayloadBits(remaining_bits));
        }
        if remaining_bits != 0 && bits.read_bits(remaining_bits)? != 0 {
            return Err(Error::NonZeroPadding);
        }

        #[cfg(feature = "stage_profile")]
        stage_profile::payload(
            payload_started.elapsed().as_nanos().min(u128::from(u64::MAX)) as u64,
        );

        Ok(())
    }

    #[inline]
    pub fn decode_quantum_into(
        &mut self,
        payload: &[u8],
        output: &mut [u8],
        output_pos: &mut usize,
        raw_len: usize,
        has_new_model: bool,
    ) -> Result<(), Error> {
        self.decode_quantum_into_impl(
            payload,
            output,
            output_pos,
            raw_len,
            has_new_model,
        )
    }

    #[cfg(any(target_arch = "x86", target_arch = "x86_64"))]
    #[target_feature(enable = "bmi2,lzcnt")]
    unsafe fn decode_quantum_into_bmi2_lzcnt(
        &mut self,
        payload: &[u8],
        output: &mut [u8],
        output_pos: &mut usize,
        raw_len: usize,
        has_new_model: bool,
    ) -> Result<(), Error> {
        self.decode_quantum_into_impl(
            payload,
            output,
            output_pos,
            raw_len,
            has_new_model,
        )
    }
}

#[inline(always)]
fn decode_length_parts_fast(
    bits: &mut MsbBitReader<'_>,
    base: u16,
    extra_bits: u8,
    extended: bool,
) -> usize {
    let base = usize::from(base);
    if extra_bits == 0 {
        return base;
    }
    if !extended {
        return base + bits.read_bits_fast(usize::from(extra_bits)) as usize;
    }

    if bits.read_bits_fast(1) == 0 {
        return 157 + bits.read_bits_fast(6) as usize;
    }
    if bits.read_bits_fast(1) == 0 {
        return 221 + bits.read_bits_fast(7) as usize;
    }
    if bits.read_bits_fast(1) == 0 {
        return 349 + bits.read_bits_fast(8) as usize;
    }
    if bits.read_bits_fast(1) == 0 {
        return 605 + bits.read_bits_fast(10) as usize;
    }
    1629 + bits.read_bits_fast(14) as usize
}

#[inline(always)]
fn decode_length_parts(
    bits: &mut MsbBitReader<'_>,
    base: u16,
    extra_bits: u8,
    extended: bool,
) -> Result<usize, Error> {
    let base = usize::from(base);
    if extra_bits == 0 {
        return Ok(base);
    }
    if !extended {
        return Ok(base + bits.read_bits(usize::from(extra_bits))? as usize);
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

    if distance == 1 {
        let value = unsafe { *output.get_unchecked(*output_pos - 1) };
        unsafe {
            core::ptr::write_bytes(output.as_mut_ptr().add(*output_pos), value, length);
        }
        *output_pos += length;
        return Ok(());
    }

    let match_start = *output_pos;
    let source_start = match_start - distance;

    // Oodle's scalar LZH kernel uses fixed-width short-match copies.  For
    // distance >= 8, an 8-byte source chunk cannot overlap its destination.
    // It is safe to write past the logical match end as long as the backing
    // output slice has physical slack; subsequent output overwrites those bytes.
    if distance >= 8 {
        let physical_remaining = output.len() - match_start;
        if length <= 8 && physical_remaining >= 8 {
            unsafe {
                let base = output.as_mut_ptr();
                let word = core::ptr::read_unaligned(base.add(source_start).cast::<u64>());
                core::ptr::write_unaligned(base.add(match_start).cast::<u64>(), word);
            }
            *output_pos += length;
            return Ok(());
        }
        if length <= 16 && physical_remaining >= 16 {
            unsafe {
                let base = output.as_mut_ptr();
                let first = core::ptr::read_unaligned(base.add(source_start).cast::<u64>());
                core::ptr::write_unaligned(base.add(match_start).cast::<u64>(), first);
                let second =
                    core::ptr::read_unaligned(base.add(source_start + 8).cast::<u64>());
                core::ptr::write_unaligned(base.add(match_start + 8).cast::<u64>(), second);
            }
            *output_pos += length;
            return Ok(());
        }
    }

    // For the next two common length buckets, use fixed 16-byte sequential
    // chunks when the match distance is at least 16. Sequential chunks preserve
    // LZ overlap semantics for distance == 16 while avoiding memcpy dispatch.
    if distance >= 16 {
        let physical_remaining = output.len() - match_start;
        if length <= 32 && physical_remaining >= 32 {
            unsafe {
                let base = output.as_mut_ptr();
                for offset in [0usize, 16] {
                    let a =
                        core::ptr::read_unaligned(base.add(source_start + offset).cast::<u64>());
                    let b = core::ptr::read_unaligned(
                        base.add(source_start + offset + 8).cast::<u64>(),
                    );
                    core::ptr::write_unaligned(
                        base.add(match_start + offset).cast::<u64>(),
                        a,
                    );
                    core::ptr::write_unaligned(
                        base.add(match_start + offset + 8).cast::<u64>(),
                        b,
                    );
                }
            }
            *output_pos += length;
            return Ok(());
        }
        if length <= 64 && physical_remaining >= 64 {
            unsafe {
                let base = output.as_mut_ptr();
                for offset in [0usize, 16, 32, 48] {
                    let a =
                        core::ptr::read_unaligned(base.add(source_start + offset).cast::<u64>());
                    let b = core::ptr::read_unaligned(
                        base.add(source_start + offset + 8).cast::<u64>(),
                    );
                    core::ptr::write_unaligned(
                        base.add(match_start + offset).cast::<u64>(),
                        a,
                    );
                    core::ptr::write_unaligned(
                        base.add(match_start + offset + 8).cast::<u64>(),
                        b,
                    );
                }
            }
            *output_pos += length;
            return Ok(());
        }
    }

    let seed = length.min(distance);

    // seed <= distance, so source and destination do not overlap. Subsequent
    // doubling copies are also adjacent/non-overlapping because chunk <= produced.
    // The full destination range was validated above.
    unsafe {
        let base = output.as_mut_ptr();
        core::ptr::copy_nonoverlapping(base.add(source_start), base.add(match_start), seed);
    }
    *output_pos += seed;

    let mut produced = seed;
    while produced < length {
        let chunk = (length - produced).min(produced);
        unsafe {
            let base = output.as_mut_ptr();
            core::ptr::copy_nonoverlapping(
                base.add(match_start),
                base.add(match_start + produced),
                chunk,
            );
        }
        produced += chunk;
        *output_pos += chunk;
    }
    Ok(())
}

fn decode_stream_into_generic(input: &[u8], output: &mut [u8]) -> Result<(), Error> {
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
                let remaining = output.len().saturating_sub(output_pos);
                output
                    .get_mut(output_pos..end)
                    .ok_or(Error::OutputOverrun {
                        requested: span.raw_len,
                        remaining,
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
                let remaining = output.len().saturating_sub(output_pos);
                output
                    .get_mut(output_pos..end)
                    .ok_or(Error::OutputOverrun {
                        requested: span.raw_len,
                        remaining,
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

#[inline]
fn decode_stream_into_b7_common(input: &[u8], output: &mut [u8]) -> Result<(), Error> {
    let output_len = output.len();
    if output_len == 0 || output_len > crate::BLOCK_LEN || input.first().copied() != Some(0xb7) {
        return decode_stream_into_generic(input, output);
    }

    let mut decoder = Decoder::new();
    decoder.reset();
    let mut input_pos = 1usize;
    let mut output_pos = 0usize;

    #[cfg(any(target_arch = "x86", target_arch = "x86_64"))]
    let use_bmi2_lzcnt =
        std::arch::is_x86_feature_detected!("bmi2")
            && std::arch::is_x86_feature_detected!("lzcnt");
    #[cfg(not(any(target_arch = "x86", target_arch = "x86_64")))]
    let use_bmi2_lzcnt = false;

    while output_pos < output_len {
        let header_bytes = input
            .get(input_pos..input_pos + 2)
            .ok_or(Error::Truncated)?;
        let header = u16::from_be_bytes([header_bytes[0], header_bytes[1]]) as usize;

        // Rare legacy special quanta (raw/memset/whole-match) stay on the
        // fully general path. Restarting from the beginning is correct and
        // costs nothing for the overwhelmingly common all-compressed D1 case.
        if (header & 0x3fff) == 0x3fff {
            return decode_stream_into_generic(input, output);
        }

        input_pos += 2;
        let stored_size = (header & 0x3fff) + 1;
        let raw_len = crate::LEGACY_QUANTUM_LEN.min(output_len - output_pos);
        if stored_size > raw_len {
            return Err(Error::Frame(crate::Error::StoredSizeExceedsRaw {
                stored: stored_size,
                raw: raw_len,
            }));
        }

        let payload_end = input_pos
            .checked_add(stored_size)
            .ok_or(Error::Truncated)?;
        let payload = input
            .get(input_pos..payload_end)
            .ok_or(Error::Frame(crate::Error::StoredSizeExceedsInput {
                stored: stored_size,
                available: input.len().saturating_sub(input_pos),
            }))?;

        if use_bmi2_lzcnt {
            #[cfg(any(target_arch = "x86", target_arch = "x86_64"))]
            unsafe {
                decoder.decode_quantum_into_bmi2_lzcnt(
                    payload,
                    output,
                    &mut output_pos,
                    raw_len,
                    (header & 0x4000) != 0,
                )?;
            }
            #[cfg(not(any(target_arch = "x86", target_arch = "x86_64")))]
            unreachable!();
        } else {
            decoder.decode_quantum_into(
                payload,
                output,
                &mut output_pos,
                raw_len,
                (header & 0x4000) != 0,
            )?;
        }
        input_pos = payload_end;
    }

    if input_pos != input.len() {
        return Err(Error::Frame(crate::Error::TrailingInput {
            remaining: input.len() - input_pos,
        }));
    }
    Ok(())
}

pub fn decode_stream_into(input: &[u8], output: &mut [u8]) -> Result<(), Error> {
    if input.first().copied() == Some(0xb7) {
        decode_stream_into_b7_common(input, output)
    } else {
        decode_stream_into_generic(input, output)
    }
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
    start: *const u8,
    ptr: *const u8,
    end: *const u8,
    fast_limit: usize,
    bit_buf: u64,
    bit_count: u8,
    marker: core::marker::PhantomData<&'a [u8]>,
}

impl<'a> MsbBitReader<'a> {
    #[inline(always)]
    fn new(input: &'a [u8]) -> Self {
        let start = input.as_ptr();
        let end = unsafe { start.add(input.len()) };
        let fast_limit = if input.len() >= 8 {
            start as usize + input.len() - 8
        } else {
            0
        };
        Self {
            start,
            ptr: start,
            end,
            fast_limit,
            bit_buf: 0,
            bit_count: 0,
            marker: core::marker::PhantomData,
        }
    }

    #[inline(always)]
    fn bytes_remaining(&self) -> usize {
        debug_assert!((self.ptr as usize) <= (self.end as usize));
        unsafe { self.end.offset_from(self.ptr) as usize }
    }

    #[inline(always)]
    fn position(self) -> usize {
        let consumed = unsafe { self.ptr.offset_from(self.start) as usize };
        consumed * 8 - usize::from(self.bit_count)
    }

    #[inline(always)]
    fn remaining_bits(&self) -> usize {
        usize::from(self.bit_count) + self.bytes_remaining() * 8
    }

    #[inline(always)]
    fn has_fast_margin(&self) -> bool {
        self.ptr as usize <= self.fast_limit
    }

    #[inline(always)]
    fn ensure_bits_fast(&mut self, count: usize) {
        debug_assert!(count <= 32);
        while usize::from(self.bit_count) < count {
            debug_assert!(self.bytes_remaining() >= 4);
            debug_assert!(self.bit_count <= 32);
            let word = unsafe { u32::from_be(core::ptr::read_unaligned(self.ptr.cast::<u32>())) };
            self.ptr = unsafe { self.ptr.add(4) };
            let shift = 32 - usize::from(self.bit_count);
            self.bit_buf |= u64::from(word) << shift;
            self.bit_count += 32;
            #[cfg(feature = "profile")]
            profile::refill32();
        }
    }

    #[inline(always)]
    fn read_bits_fast(&mut self, count: usize) -> u64 {
        if count == 0 {
            return 0;
        }
        self.ensure_bits_fast(count);
        let value = self.bit_buf >> (64 - count);
        self.bit_buf <<= count;
        self.bit_count -= count as u8;
        value
    }

    #[inline(always)]
    fn ensure_bits(&mut self, count: usize) -> Result<(), Error> {
        if count > 56 {
            return Err(Error::Truncated);
        }
        if usize::from(self.bit_count) >= count {
            return Ok(());
        }
        if self.remaining_bits() < count {
            return Err(Error::Truncated);
        }

        while usize::from(self.bit_count) < count {
            if self.bytes_remaining() >= 4 && self.bit_count <= 32 {
                let word =
                    unsafe { u32::from_be(core::ptr::read_unaligned(self.ptr.cast::<u32>())) };
                self.ptr = unsafe { self.ptr.add(4) };
                let shift = 32 - usize::from(self.bit_count);
                self.bit_buf |= u64::from(word) << shift;
                self.bit_count += 32;
                #[cfg(feature = "profile")]
                profile::refill32();
            } else {
                if self.ptr == self.end {
                    return Err(Error::Truncated);
                }
                let byte = unsafe { *self.ptr };
                self.ptr = unsafe { self.ptr.add(1) };
                let shift = 56 - usize::from(self.bit_count);
                self.bit_buf |= u64::from(byte) << shift;
                self.bit_count += 8;
                #[cfg(feature = "profile")]
                profile::refill8();
            }
        }
        Ok(())
    }

    #[inline(always)]
    fn peek_buffered(&self, count: usize) -> u64 {
        debug_assert!(count <= usize::from(self.bit_count));
        self.bit_buf >> (64 - count)
    }

    #[inline(always)]
    fn consume_buffered(&mut self, count: usize) {
        debug_assert!(count <= usize::from(self.bit_count));
        self.bit_buf <<= count;
        self.bit_count -= count as u8;
    }

    #[inline(always)]
    fn read_bit(&mut self) -> Result<bool, Error> {
        Ok(self.read_bits(1)? != 0)
    }

    #[inline(always)]
    fn read_bits(&mut self, count: usize) -> Result<u64, Error> {
        if count > 64 {
            return Err(Error::Truncated);
        }
        if count > 56 {
            let tail = count - 56;
            let high = self.read_bits(56)?;
            let low = self.read_bits(tail)?;
            return Ok((high << tail) | low);
        }
        if count == 0 {
            return Ok(0);
        }
        self.ensure_bits(count)?;
        let value = self.bit_buf >> (64 - count);
        self.bit_buf <<= count;
        self.bit_count -= count as u8;
        Ok(value)
    }

    #[inline]
    fn read_unary(&mut self) -> Result<u32, Error> {
        let mut zeros = 0u32;
        loop {
            if self.bit_count == 0 {
                self.ensure_bits(1)?;
            }

            let available = usize::from(self.bit_count);
            let leading = self.bit_buf.leading_zeros() as usize;
            if leading < available {
                let consume = leading + 1;
                self.bit_buf <<= consume;
                self.bit_count -= consume as u8;
                zeros = zeros
                    .checked_add(leading as u32)
                    .ok_or(Error::InvalidRun)?;
                return Ok(zeros);
            }

            zeros = zeros
                .checked_add(available as u32)
                .ok_or(Error::InvalidRun)?;
            self.bit_buf = 0;
            self.bit_count = 0;
        }
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
