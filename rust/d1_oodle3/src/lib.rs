//! Clean-room framing compatibility for the Oodle 2.3 runtime used by Destiny 1.
//! No proprietary binary or copied proprietary source is contained here.

use core::fmt;

pub mod lzh;

pub const BLOCK_LEN: usize = 0x40000;
pub const LEGACY_QUANTUM_LEN: usize = 0x4000;
pub const NEWLZ_QUANTUM_LEN: usize = 0x40000;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
#[repr(u8)]
pub enum DecoderType {
    Lzhlw = 0,
    Lznib = 1,
    Lzb16 = 2,
    Lzblw = 3,
    Lza = 4,
    Lzna = 5,
    /// Wire decode type 6. Version 3 called this LZQ1; version 4 uses it for Kraken.
    Type6 = 6,
    Lzh = 7,
    Mermaid = 10,
    BitKnit = 11,
    Type12 = 12,
}

impl DecoderType {
    fn from_base_wire(v: u8) -> Result<Self, Error> {
        match v {
            0 => Ok(Self::Lzhlw),
            1 => Ok(Self::Lznib),
            2 => Ok(Self::Lzb16),
            3 => Ok(Self::Lzblw),
            4 => Ok(Self::Lza),
            5 => Ok(Self::Lzna),
            6 => Ok(Self::Type6),
            7 => Ok(Self::Lzh),
            10 => Ok(Self::Mermaid),
            11 => Ok(Self::BitKnit),
            12 => Ok(Self::Type12),
            _ => Err(Error::UnsupportedDecoderType(v)),
        }
    }

    pub const fn quantum_len(self) -> usize {
        match self {
            Self::Type6 | Self::Mermaid | Self::Type12 => NEWLZ_QUANTUM_LEN,
            Self::Lzhlw
            | Self::Lznib
            | Self::Lzb16
            | Self::Lzblw
            | Self::Lza
            | Self::Lzna
            | Self::Lzh
            | Self::BitKnit => LEGACY_QUANTUM_LEN,
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct BlockHeader {
    pub version: u8,
    pub restart_decoder: bool,
    pub uncompressed: bool,
    pub decoder_type: DecoderType,
    pub offset_shift: u8,
    pub use_checksums: bool,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum QuantumKind {
    Compressed {
        stored_size: usize,
        flag1: bool,
        flag2: bool,
        checksum24: Option<u32>,
    },
    Memset {
        value: u8,
    },
    WholeMatch {
        distance: usize,
    },
    Raw,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct QuantumHeader {
    pub kind: QuantumKind,
    pub header_len: usize,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Error {
    Truncated,
    InvalidBlockHeader(u8),
    UnsupportedBlockVersion(u8),
    UnsupportedDecoderType(u8),
    InvalidQuantumHeader,
    InvalidWholeMatch,
    StoredSizeExceedsRaw { stored: usize, raw: usize },
    StoredSizeExceedsInput { stored: usize, available: usize },
    TrailingInput { remaining: usize },
}

impl fmt::Display for Error {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{self:?}")
    }
}

impl std::error::Error for Error {}

#[inline]
fn be24(p: &[u8]) -> Result<u32, Error> {
    if p.len() < 3 {
        return Err(Error::Truncated);
    }
    Ok(((p[0] as u32) << 16) | ((p[1] as u32) << 8) | p[2] as u32)
}

pub fn parse_block_header(input: &[u8]) -> Result<(BlockHeader, usize), Error> {
    let b0 = *input.first().ok_or(Error::Truncated)?;

    // Version 4 introduced the two-byte header identified by low nibble 0xC.
    if (b0 & 0x0f) == 0x0c {
        if input.len() < 2 {
            return Err(Error::Truncated);
        }
        let version = 4 + ((b0 >> 4) & 0x03);
        if version != 4 {
            return Err(Error::UnsupportedBlockVersion(version));
        }

        let b1 = input[1];
        let mut raw_type = b1 & 0x7f;
        let mut offset_shift = 0;
        if (7..=9).contains(&raw_type) {
            offset_shift = raw_type - 7;
            raw_type = 7;
        }

        return Ok((
            BlockHeader {
                version,
                restart_decoder: (b0 & 0x80) != 0,
                uncompressed: (b0 & 0x40) != 0,
                decoder_type: DecoderType::from_base_wire(raw_type)?,
                offset_shift,
                use_checksums: (b1 & 0x80) != 0,
            },
            2,
        ));
    }

    // Destiny's Oodle 2.3 LZH corpus uses the historical version-3 one-byte
    // block header. Versions 0-2 are intentionally rejected until a real
    // corpus fixture requires them.
    let version = b0 & 0x03;
    if version != 3 {
        return Err(Error::UnsupportedBlockVersion(version));
    }

    let top = b0 >> 2;
    let (uncompressed, restart_decoder, use_checksums, mut raw_type) = if top < 16 {
        (true, top >= 8, false, top % 8)
    } else {
        let flags_and_type = top - 16;
        (
            false,
            (flags_and_type & 1) != 0,
            (flags_and_type & 2) != 0,
            flags_and_type >> 2,
        )
    };

    let mut offset_shift = 0;
    if raw_type >= 7 {
        offset_shift = raw_type - 7;
        if offset_shift > 3 {
            return Err(Error::UnsupportedDecoderType(raw_type));
        }
        raw_type = 7;
    }

    Ok((
        BlockHeader {
            version,
            restart_decoder,
            uncompressed,
            decoder_type: DecoderType::from_base_wire(raw_type)?,
            offset_shift,
            use_checksums,
        },
        1,
    ))
}

pub fn parse_quantum_header(
    input: &[u8],
    block: BlockHeader,
    raw_len: usize,
) -> Result<QuantumHeader, Error> {
    match block.decoder_type {
        DecoderType::Type6 | DecoderType::Mermaid | DecoderType::Type12 => {
            parse_newlz_quantum_header(input, block.use_checksums)
        }
        DecoderType::Lzhlw
        | DecoderType::Lznib
        | DecoderType::Lzb16
        | DecoderType::Lzblw
        | DecoderType::Lza
        | DecoderType::Lzna
        | DecoderType::Lzh
        | DecoderType::BitKnit => {
            parse_legacy_quantum_header(input, block.use_checksums, raw_len)
        }
    }
}

fn parse_newlz_quantum_header(input: &[u8], use_checksum: bool) -> Result<QuantumHeader, Error> {
    let v = be24(input)?;
    let size = (v & 0x3ffff) as usize;
    if size != 0x3ffff {
        let header_len = if use_checksum { 6 } else { 3 };
        if input.len() < header_len {
            return Err(Error::Truncated);
        }
        let checksum24 = if use_checksum {
            Some(be24(&input[3..])?)
        } else {
            None
        };
        return Ok(QuantumHeader {
            kind: QuantumKind::Compressed {
                stored_size: size + 1,
                flag1: ((v >> 18) & 1) != 0,
                flag2: ((v >> 19) & 1) != 0,
                checksum24,
            },
            header_len,
        });
    }

    if (v >> 18) == 1 {
        if input.len() < 4 {
            return Err(Error::Truncated);
        }
        return Ok(QuantumHeader {
            kind: QuantumKind::Memset { value: input[3] },
            header_len: 4,
        });
    }

    Err(Error::InvalidQuantumHeader)
}

fn parse_legacy_quantum_header(
    input: &[u8],
    use_checksum: bool,
    raw_len: usize,
) -> Result<QuantumHeader, Error> {
    if input.len() < 2 {
        return Err(Error::Truncated);
    }
    let v = ((input[0] as u32) << 8) | input[1] as u32;
    let size = (v & 0x3fff) as usize;
    if size != 0x3fff {
        let header_len = if use_checksum { 5 } else { 2 };
        if input.len() < header_len {
            return Err(Error::Truncated);
        }
        let checksum24 = if use_checksum {
            Some(be24(&input[2..])?)
        } else {
            None
        };
        return Ok(QuantumHeader {
            kind: QuantumKind::Compressed {
                stored_size: size + 1,
                flag1: ((v >> 14) & 1) != 0,
                flag2: ((v >> 15) & 1) != 0,
                checksum24,
            },
            header_len,
        });
    }

    match v >> 14 {
        0 => {
            let (distance, used) = parse_legacy_whole_match(&input[2..])?;
            Ok(QuantumHeader {
                kind: QuantumKind::WholeMatch { distance },
                header_len: 2 + used,
            })
        }
        1 => {
            if input.len() < 3 {
                return Err(Error::Truncated);
            }
            Ok(QuantumHeader {
                kind: QuantumKind::Memset { value: input[2] },
                header_len: 3,
            })
        }
        2 if raw_len > 0 => Ok(QuantumHeader {
            kind: QuantumKind::Raw,
            header_len: 2,
        }),
        _ => Err(Error::InvalidQuantumHeader),
    }
}

fn parse_legacy_whole_match(input: &[u8]) -> Result<(usize, usize), Error> {
    if input.len() < 2 {
        return Err(Error::Truncated);
    }
    let v = u16::from_be_bytes([input[0], input[1]]) as usize;
    if v >= 0x8000 {
        return Ok((v - 0x8000 + 1, 2));
    }

    let mut x = 0usize;
    let mut pos = 0usize;
    let mut n = 0usize;
    loop {
        let b = *input.get(2 + n).ok_or(Error::Truncated)? as usize;
        n += 1;
        if (b & 0x80) != 0 {
            x = x
                .checked_add((b - 0x80) << pos)
                .ok_or(Error::InvalidWholeMatch)?;
            break;
        }
        x = x
            .checked_add((b + 0x80) << pos)
            .ok_or(Error::InvalidWholeMatch)?;
        pos += 7;
        if pos >= usize::BITS as usize {
            return Err(Error::InvalidWholeMatch);
        }
    }

    let distance = 0x8000usize
        .checked_add(v)
        .and_then(|z| z.checked_add(x << 15))
        .and_then(|z| z.checked_add(1))
        .ok_or(Error::InvalidWholeMatch)?;
    Ok((distance, 2 + n))
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct QuantumSpan {
    pub output_offset: usize,
    pub raw_len: usize,
    pub input_offset: usize,
    pub input_len: usize,
    pub block: BlockHeader,
    pub kind: QuantumKind,
}

pub fn scan_frame(input: &[u8], expected_raw_len: usize) -> Result<Vec<QuantumSpan>, Error> {
    let mut spans = Vec::new();
    let mut ip = 0usize;
    let mut op = 0usize;
    let mut current = None;

    while op < expected_raw_len {
        if op.is_multiple_of(BLOCK_LEN) {
            let (header, used) = parse_block_header(input.get(ip..).ok_or(Error::Truncated)?)?;
            ip += used;
            current = Some(header);
        }

        let block = current.ok_or(Error::InvalidQuantumHeader)?;
        let raw_len = block
            .decoder_type
            .quantum_len()
            .min(expected_raw_len - op)
            .min(BLOCK_LEN - (op % BLOCK_LEN));
        let q_input_start = ip;

        let kind = if block.uncompressed {
            let available = input.len().saturating_sub(ip);
            if raw_len > available {
                return Err(Error::StoredSizeExceedsInput {
                    stored: raw_len,
                    available,
                });
            }
            ip += raw_len;
            QuantumKind::Raw
        } else {
            let q = parse_quantum_header(input.get(ip..).ok_or(Error::Truncated)?, block, raw_len)?;
            ip += q.header_len;
            match q.kind {
                QuantumKind::Compressed { stored_size, .. } => {
                    if stored_size > raw_len {
                        return Err(Error::StoredSizeExceedsRaw {
                            stored: stored_size,
                            raw: raw_len,
                        });
                    }
                    let available = input.len().saturating_sub(ip);
                    if stored_size > available {
                        return Err(Error::StoredSizeExceedsInput {
                            stored: stored_size,
                            available,
                        });
                    }
                    ip += stored_size;
                }
                QuantumKind::Raw => {
                    let available = input.len().saturating_sub(ip);
                    if raw_len > available {
                        return Err(Error::StoredSizeExceedsInput {
                            stored: raw_len,
                            available,
                        });
                    }
                    ip += raw_len;
                }
                QuantumKind::Memset { .. } | QuantumKind::WholeMatch { .. } => {}
            }
            q.kind
        };

        spans.push(QuantumSpan {
            output_offset: op,
            raw_len,
            input_offset: q_input_start,
            input_len: ip - q_input_start,
            block,
            kind,
        });
        op += raw_len;
    }

    if ip != input.len() {
        return Err(Error::TrailingInput {
            remaining: input.len() - ip,
        });
    }

    Ok(spans)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn block_header_kraken() {
        let (h, used) = parse_block_header(&[0x8c, 0x06]).unwrap();
        assert_eq!(used, 2);
        assert_eq!(h.version, 4);
        assert_eq!(h.decoder_type, DecoderType::Type6);
        assert_eq!(h.offset_shift, 0);
        assert!(h.restart_decoder);
        assert!(!h.uncompressed);
    }

    #[test]
    fn v4_wire_decoder_types() {
        for (wire, expected) in [
            (0, DecoderType::Lzhlw),
            (1, DecoderType::Lznib),
            (2, DecoderType::Lzb16),
            (3, DecoderType::Lzblw),
            (4, DecoderType::Lza),
            (5, DecoderType::Lzna),
            (6, DecoderType::Type6),
            (7, DecoderType::Lzh),
            (10, DecoderType::Mermaid),
            (11, DecoderType::BitKnit),
            (12, DecoderType::Type12),
        ] {
            let (h, _) = parse_block_header(&[0x0c, wire]).unwrap();
            assert_eq!(h.decoder_type, expected);
        }
    }

    #[test]
    fn destiny_v3_lzh_block_header() {
        let (h, used) = parse_block_header(&[0xb7]).unwrap();
        assert_eq!(used, 1);
        assert_eq!(h.version, 3);
        assert_eq!(h.decoder_type, DecoderType::Lzh);
        assert_eq!(h.offset_shift, 0);
        assert!(h.restart_decoder);
        assert!(!h.uncompressed);
        assert!(!h.use_checksums);
    }

    #[test]
    fn destiny_v3_lzh_quantum_headers() {
        let (h, _) = parse_block_header(&[0xb7]).unwrap();

        let first = parse_quantum_header(&[0x48, 0xb0], h, LEGACY_QUANTUM_LEN).unwrap();
        assert_eq!(first.header_len, 2);
        assert_eq!(
            first.kind,
            QuantumKind::Compressed {
                stored_size: 2225,
                flag1: true,
                flag2: false,
                checksum24: None,
            }
        );

        let second = parse_quantum_header(&[0x04, 0x29], h, LEGACY_QUANTUM_LEN).unwrap();
        assert_eq!(
            second.kind,
            QuantumKind::Compressed {
                stored_size: 1066,
                flag1: false,
                flag2: false,
                checksum24: None,
            }
        );
    }

    #[test]
    fn newlz_compressed_header() {
        let h = BlockHeader {
            version: 4,
            restart_decoder: false,
            uncompressed: false,
            decoder_type: DecoderType::Type6,
            offset_shift: 0,
            use_checksums: false,
        };
        let q = parse_quantum_header(&[0x00, 0x00, 0x0f], h, 0x40000).unwrap();
        assert_eq!(q.header_len, 3);
        assert!(matches!(
            q.kind,
            QuantumKind::Compressed {
                stored_size: 16,
                ..
            }
        ));
    }

    #[test]
    fn newlz_memset_header() {
        let h = BlockHeader {
            version: 4,
            restart_decoder: false,
            uncompressed: false,
            decoder_type: DecoderType::Type6,
            offset_shift: 0,
            use_checksums: false,
        };
        let q = parse_quantum_header(&[0x07, 0xff, 0xff, 0xaa], h, 0x40000).unwrap();
        assert_eq!(q.kind, QuantumKind::Memset { value: 0xaa });
    }
}
