//! Native compatibility work for Destiny-era Oodle 3 streams.
//!
//! This crate is evidence-driven.  The outer frame header and stored/raw path
//! below are implemented only from behavior reproduced by deterministic oracle
//! vectors from the exact D1 reference runtime.

mod bit;

pub use bit::{BitOrder, BitReader};

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum RawCodec {
    Lzhlw,
    Lznib,
    Lzb16,
    Lzblw,
    Lza,
    Lzna,
    Kraken,
    Lzh,
    MermaidSelkie,
    Bitknit,
    Unknown(u8),
}

impl RawCodec {
    pub fn from_id(id: u8) -> Self {
        match id {
            0 => Self::Lzhlw,
            1 => Self::Lznib,
            2 => Self::Lzb16,
            3 => Self::Lzblw,
            4 => Self::Lza,
            5 => Self::Lzna,
            6 => Self::Kraken,
            7 => Self::Lzh,
            10 => Self::MermaidSelkie,
            11 => Self::Bitknit,
            other => Self::Unknown(other),
        }
    }

    pub fn id(self) -> u8 {
        match self {
            Self::Lzhlw => 0,
            Self::Lznib => 1,
            Self::Lzb16 => 2,
            Self::Lzblw => 3,
            Self::Lza => 4,
            Self::Lzna => 5,
            Self::Kraken => 6,
            Self::Lzh => 7,
            Self::MermaidSelkie => 10,
            Self::Bitknit => 11,
            Self::Unknown(id) => id,
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct FrameHeader {
    /// Bit 7 of the first header byte.  D1 independent oracle streams use this.
    pub restart_decoder: bool,
    /// Bit 6 of the first header byte.  When set, the post-header bytes are raw.
    pub uncompressed: bool,
    /// Low seven bits of the second header byte.
    pub codec: RawCodec,
    /// High bit of the second header byte.
    pub checksums: bool,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum DecodeError {
    OutputTooSmall,
    TruncatedInput,
    InvalidDistance { distance: usize, produced: usize },
    InvalidStream(&'static str),
    UnsupportedChecksums,
    UnsupportedCompressedCodec(RawCodec),
}

impl core::fmt::Display for DecodeError {
    fn fmt(&self, f: &mut core::fmt::Formatter<'_>) -> core::fmt::Result {
        match self {
            Self::OutputTooSmall => write!(f, "output buffer is too small"),
            Self::TruncatedInput => write!(f, "truncated input"),
            Self::InvalidDistance { distance, produced } => {
                write!(f, "invalid match distance {distance} after {produced} output bytes")
            }
            Self::InvalidStream(s) => write!(f, "invalid stream: {s}"),
            Self::UnsupportedChecksums => write!(f, "checksummed Oodle stream is not implemented yet"),
            Self::UnsupportedCompressedCodec(codec) => {
                write!(f, "compressed {:?} decoder is not implemented yet", codec)
            }
        }
    }
}

impl std::error::Error for DecodeError {}

/// Parse Oodle's two-byte outer stream header.
///
/// Exact D1 Oodle-3 oracle vectors prove the independent-stream forms 0x8c
/// (compressed) and 0xcc (stored/raw).  The low nibble is always 0xc, bits 4-5
/// are reserved in this runtime family, bit 7 is restart, and bit 6 is raw.
pub fn parse_frame_header(compressed: &[u8]) -> Result<FrameHeader, DecodeError> {
    if compressed.len() < 2 {
        return Err(DecodeError::TruncatedInput);
    }

    let control = compressed[0];
    if control & 0x0f != 0x0c || control & 0x30 != 0 {
        return Err(DecodeError::InvalidStream("invalid outer Oodle header"));
    }

    let codec_flags = compressed[1];
    Ok(FrameHeader {
        restart_decoder: control & 0x80 != 0,
        uncompressed: control & 0x40 != 0,
        codec: RawCodec::from_id(codec_flags & 0x7f),
        checksums: codec_flags & 0x80 != 0,
    })
}


pub const LEGACY_QUANTUM_LEN: usize = 0x4000;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum LegacyQuantumKind {
    /// Low 14 bits encode compressed_size - 1. The two high bits are retained.
    Compressed { compressed_len: usize, flags: u8 },
    /// Oracle-proven special header 0x7fff: the quantum bytes are stored verbatim.
    StoredRaw,
    /// Reserved/special legacy form not yet behaviorally classified.
    Special { selector: u8 },
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct LegacyQuantum {
    pub raw_offset: usize,
    pub raw_len: usize,
    pub compressed_offset: usize,
    pub compressed_len: usize,
    pub kind: LegacyQuantumKind,
}

/// Parse the 16 KiB quantum framing used by legacy Oodle codecs such as LZH.
///
/// D1's exact Oodle 3 oracle establishes a big-endian 16-bit header per quantum.
/// For normal compressed quanta, bits 0..13 store `compressed_len - 1` and the
/// two high bits are flags. A low-14 value of 0x3fff selects a special form.
/// The `0x7fff` special form is proven to store the raw quantum bytes directly.
pub fn scan_legacy_quanta(
    compressed: &[u8],
    raw_len: usize,
) -> Result<Vec<LegacyQuantum>, DecodeError> {
    let header = parse_frame_header(compressed)?;
    if header.checksums {
        return Err(DecodeError::UnsupportedChecksums);
    }
    if header.uncompressed {
        return Err(DecodeError::InvalidStream(
            "whole-stream stored frame has no legacy quantum headers",
        ));
    }
    if matches!(
        header.codec,
        RawCodec::Kraken | RawCodec::MermaidSelkie | RawCodec::Unknown(_)
    ) {
        return Err(DecodeError::InvalidStream(
            "codec does not use the legacy 16 KiB quantum framing",
        ));
    }

    let mut result = Vec::new();
    let mut cp = 2usize;
    let mut rp = 0usize;

    while rp < raw_len {
        if cp.checked_add(2).filter(|&end| end <= compressed.len()).is_none() {
            return Err(DecodeError::TruncatedInput);
        }
        let word = u16::from_be_bytes([compressed[cp], compressed[cp + 1]]);
        cp += 2;

        let qraw = core::cmp::min(LEGACY_QUANTUM_LEN, raw_len - rp);
        let size_code = (word & 0x3fff) as usize;
        let selector = (word >> 14) as u8;

        let (kind, payload_len) = if size_code != 0x3fff {
            let n = size_code + 1;
            (
                LegacyQuantumKind::Compressed {
                    compressed_len: n,
                    flags: selector,
                },
                n,
            )
        } else if selector == 1 {
            (LegacyQuantumKind::StoredRaw, qraw)
        } else {
            // The byte count of the other legacy special selectors is not yet
            // proven, so do not guess and desynchronize the stream.
            return Err(DecodeError::InvalidStream(
                "unclassified legacy special quantum",
            ));
        };

        let end = cp.checked_add(payload_len).ok_or(DecodeError::TruncatedInput)?;
        if end > compressed.len() {
            return Err(DecodeError::TruncatedInput);
        }

        result.push(LegacyQuantum {
            raw_offset: rp,
            raw_len: qraw,
            compressed_offset: cp,
            compressed_len: payload_len,
            kind,
        });
        cp = end;
        rp += qraw;
    }

    if cp != compressed.len() {
        return Err(DecodeError::InvalidStream(
            "trailing bytes after legacy quantum stream",
        ));
    }
    Ok(result)
}

/// Copy an LZ match with standard overlapping-copy semantics.
pub fn copy_match(
    output: &mut [u8],
    produced: &mut usize,
    distance: usize,
    len: usize,
) -> Result<(), DecodeError> {
    if distance == 0 || distance > *produced {
        return Err(DecodeError::InvalidDistance {
            distance,
            produced: *produced,
        });
    }
    let end = produced.checked_add(len).ok_or(DecodeError::OutputTooSmall)?;
    if end > output.len() {
        return Err(DecodeError::OutputTooSmall);
    }

    for _ in 0..len {
        let src = *produced - distance;
        output[*produced] = output[src];
        *produced += 1;
    }
    Ok(())
}

/// Decode one independently decodable Oodle 3 buffer into an exact-size output.
///
/// The stored/raw path is already fully native.  Compressed codec bodies are
/// deliberately rejected until their individual formats pass oracle tests.
pub fn decode_into(compressed: &[u8], output: &mut [u8]) -> Result<usize, DecodeError> {
    let header = parse_frame_header(compressed)?;
    if header.checksums {
        return Err(DecodeError::UnsupportedChecksums);
    }

    if header.uncompressed {
        let raw = &compressed[2..];
        if raw.len() != output.len() {
            return Err(DecodeError::InvalidStream(
                "stored/raw payload length does not match requested output length",
            ));
        }
        output.copy_from_slice(raw);
        return Ok(raw.len());
    }

    Err(DecodeError::UnsupportedCompressedCodec(header.codec))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parses_exact_oracle_outer_headers() {
        let lzh = parse_frame_header(&[0x8c, 0x07]).unwrap();
        assert!(lzh.restart_decoder);
        assert!(!lzh.uncompressed);
        assert_eq!(lzh.codec, RawCodec::Lzh);
        assert!(!lzh.checksums);

        let kraken = parse_frame_header(&[0x8c, 0x06]).unwrap();
        assert_eq!(kraken.codec, RawCodec::Kraken);

        let bitknit = parse_frame_header(&[0x8c, 0x0b]).unwrap();
        assert_eq!(bitknit.codec, RawCodec::Bitknit);
    }

    #[test]
    fn decodes_exact_lzh_stored_oracle_shape() {
        // Exact form emitted by the reference DLL for the 64-byte all-zero
        // synthetic vector: cc 07 followed by the raw bytes.
        let mut comp = vec![0xcc, 0x07];
        comp.extend_from_slice(&[0u8; 64]);
        let mut out = [0xa5u8; 64];
        assert_eq!(decode_into(&comp, &mut out), Ok(64));
        assert_eq!(out, [0u8; 64]);
    }

    #[test]
    fn decodes_stored_lzb16_ramp() {
        let raw: Vec<u8> = (0..64u8).collect();
        let mut comp = vec![0xcc, 0x02];
        comp.extend_from_slice(&raw);
        let mut out = vec![0u8; raw.len()];
        assert_eq!(decode_into(&comp, &mut out), Ok(raw.len()));
        assert_eq!(out, raw);
    }

    #[test]
    fn rejects_wrong_stored_raw_length() {
        let mut out = [0u8; 4];
        assert!(matches!(
            decode_into(&[0xcc, 0x07, 1, 2, 3], &mut out),
            Err(DecodeError::InvalidStream(_))
        ));
    }

    #[test]
    fn compressed_codec_is_parsed_before_rejection() {
        let mut out = [0u8; 16];
        assert_eq!(
            decode_into(&[0x8c, 0x07, 0x40, 0x0b], &mut out),
            Err(DecodeError::UnsupportedCompressedCodec(RawCodec::Lzh))
        );
    }

    #[test]
    fn scans_oracle_proven_legacy_quantum_layout() {
        // Shape of the reference LZH 0x4001-byte boundary vector:
        // first 16 KiB compressed quantum, then a one-byte 0x7fff stored quantum.
        let comp = [
            0x8c, 0x07,
            0x40, 0x02, 0xaa, 0xbb, 0xcc,
            0x7f, 0xff, 0xa3,
        ];
        let q = scan_legacy_quanta(&comp, 0x4001).unwrap();
        assert_eq!(q.len(), 2);
        assert_eq!(q[0].raw_len, 0x4000);
        assert_eq!(
            q[0].kind,
            LegacyQuantumKind::Compressed {
                compressed_len: 3,
                flags: 1
            }
        );
        assert_eq!(q[1].raw_len, 1);
        assert_eq!(q[1].kind, LegacyQuantumKind::StoredRaw);
        assert_eq!(comp[q[1].compressed_offset], 0xa3);
    }

    #[test]
    fn rejects_modern_whole_block_codec_as_legacy() {
        let comp = [0x8c, 0x06, 0x40, 0x00, 0xaa];
        assert!(matches!(
            scan_legacy_quanta(&comp, 0x4000),
            Err(DecodeError::InvalidStream(_))
        ));
    }

    #[test]
    fn scans_four_legacy_quanta_with_reset_flag_only_on_first() {
        let mut comp = vec![0x8c, 0x07];
        for flags in [1u16, 0, 0, 0] {
            // one-byte compressed payload for each synthetic quantum
            let word = (flags << 14) | 0;
            comp.extend_from_slice(&word.to_be_bytes());
            comp.push(0x55);
        }
        let q = scan_legacy_quanta(&comp, 0x10000).unwrap();
        assert_eq!(q.len(), 4);
        assert!(matches!(
            q[0].kind,
            LegacyQuantumKind::Compressed { flags: 1, .. }
        ));
        assert!(q[1..].iter().all(|x| matches!(
            x.kind,
            LegacyQuantumKind::Compressed { flags: 0, .. }
        )));
    }

    #[test]
    fn overlapping_match_repeats_history() {
        let mut out = [0u8; 12];
        out[..3].copy_from_slice(b"ABC");
        let mut produced = 3;
        copy_match(&mut out, &mut produced, 3, 9).unwrap();
        assert_eq!(&out, b"ABCABCABCABC");
    }

    #[test]
    fn rejects_zero_distance() {
        let mut out = [0u8; 4];
        let mut produced = 1;
        assert!(matches!(
            copy_match(&mut out, &mut produced, 0, 1),
            Err(DecodeError::InvalidDistance { .. })
        ));
    }
}
