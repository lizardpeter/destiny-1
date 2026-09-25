#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum BitOrder {
    LsbFirst,
    MsbFirst,
}

#[derive(Debug, Clone, Copy)]
pub struct BitReader<'a> {
    data: &'a [u8],
    bit_pos: usize,
    order: BitOrder,
}

impl<'a> BitReader<'a> {
    pub fn new(data: &'a [u8], order: BitOrder) -> Self {
        Self { data, bit_pos: 0, order }
    }

    pub fn bit_position(&self) -> usize {
        self.bit_pos
    }

    pub fn remaining_bits(&self) -> usize {
        self.data.len().saturating_mul(8).saturating_sub(self.bit_pos)
    }

    pub fn read_bits(&mut self, n: u32) -> Option<u64> {
        if n > 64 || self.remaining_bits() < n as usize {
            return None;
        }
        let mut v = 0u64;
        match self.order {
            BitOrder::LsbFirst => {
                for i in 0..n {
                    let p = self.bit_pos + i as usize;
                    let bit = (self.data[p >> 3] >> (p & 7)) & 1;
                    v |= (bit as u64) << i;
                }
            }
            BitOrder::MsbFirst => {
                for _ in 0..n {
                    let p = self.bit_pos;
                    let bit = (self.data[p >> 3] >> (7 - (p & 7))) & 1;
                    v = (v << 1) | bit as u64;
                    self.bit_pos += 1;
                }
                return Some(v);
            }
        }
        self.bit_pos += n as usize;
        Some(v)
    }

    pub fn align_byte(&mut self) {
        self.bit_pos = (self.bit_pos + 7) & !7;
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn lsb_first() {
        let mut b = BitReader::new(&[0b1011_0010, 0b0110_0001], BitOrder::LsbFirst);
        assert_eq!(b.read_bits(4), Some(0b0010));
        assert_eq!(b.read_bits(4), Some(0b1011));
        assert_eq!(b.read_bits(8), Some(0b0110_0001));
    }

    #[test]
    fn msb_first() {
        let mut b = BitReader::new(&[0b1011_0010], BitOrder::MsbFirst);
        assert_eq!(b.read_bits(3), Some(0b101));
        assert_eq!(b.read_bits(5), Some(0b10010));
    }
}
