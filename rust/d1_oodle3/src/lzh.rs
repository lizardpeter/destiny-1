//! Clean-room decoder primitives for the legacy Oodle LZH stream used by Destiny 1.
//!
//! This module starts with the transmitted canonical-Huffman model.  The retail
//! Oodle 2.3 runtime uses a 713-symbol alphabet, a 10-bit fast-decode prefix,
//! and permits code lengths through 16 bits.

pub const SYMBOL_COUNT: usize = 713;
pub const FAST_DECODE_BITS: u8 = 10;
pub const MAX_CODE_LEN: u8 = 16;

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
}

impl core::fmt::Display for Error {
    fn fmt(&self, f: &mut core::fmt::Formatter<'_>) -> core::fmt::Result {
        write!(f, "{self:?}")
    }
}

impl std::error::Error for Error {}

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
        let min_code_len = lengths.iter().copied().filter(|&len| len != 0).min().unwrap_or(0);
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

    fn read_bit(&mut self) -> Result<bool, Error> {
        Ok(self.read_bits(1)? != 0)
    }

    fn read_bits(&mut self, count: usize) -> Result<u64, Error> {
        if count > 64 || self.bit_pos.saturating_add(count) > self.input.len().saturating_mul(8) {
            return Err(Error::Truncated);
        }

        let mut value = 0u64;
        for _ in 0..count {
            let byte = self.input[self.bit_pos >> 3];
            let shift = 7 - (self.bit_pos & 7);
            value = (value << 1) | u64::from((byte >> shift) & 1);
            self.bit_pos += 1;
        }
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
}
