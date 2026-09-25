//! Native compatibility work for Destiny-era Oodle 3 streams.
//!
//! This crate is deliberately evidence-driven.  The public API and low-level
//! LZ primitives are in place first; framing and entropy decode stages are only
//! enabled once proven against exact synthetic oracle vectors.

mod bit;

pub use bit::{BitOrder, BitReader};

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum DecodeError {
    OutputTooSmall,
    TruncatedInput,
    InvalidDistance { distance: usize, produced: usize },
    InvalidStream(&'static str),
    UnsupportedFormat,
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
            Self::UnsupportedFormat => write!(f, "Oodle 3 stream format stage not yet implemented"),
        }
    }
}

impl std::error::Error for DecodeError {}

/// Copy an LZ match with standard overlapping-copy semantics.
///
/// Kept as a small independently tested primitive because the legacy Oodle
/// decoder uses repeated-history copies heavily; exact overlap behavior matters
/// when differential testing starts.
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
/// The ABI-facing wrapper will use this function once top-level framing and the
/// legacy entropy/LZ stages are proven from the exact reference runtime.
pub fn decode_into(_compressed: &[u8], _output: &mut [u8]) -> Result<usize, DecodeError> {
    Err(DecodeError::UnsupportedFormat)
}

#[cfg(test)]
mod tests {
    use super::*;

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
