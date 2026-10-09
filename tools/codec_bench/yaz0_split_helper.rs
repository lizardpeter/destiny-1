//! Exact Nintendo Yaz0 decoding with chunked, overlap-correct match expansion.
//! The source and output validation rules are the same as Rust-test's original.

pub fn decompress_yaz0(src: &[u8]) -> Result<Vec<u8>, String> {
    if src.len() < 16 || &src[..4] != b"Yaz0" {
        return Err("not a Yaz0 stream".to_owned());
    }
    let out_len = u32::from_be_bytes(src[4..8].try_into().unwrap()) as usize;
    // Reserve once, but do not expose uninitialized bytes on a malformed
    // stream. Vec::extend_from_within only copies previously decoded bytes.
    let mut out = Vec::with_capacity(out_len);
    let mut sp = 16usize;
    let mut code = 0u8;
    let mut bits_left = 0u8;

    while out.len() < out_len {
        if bits_left == 0 {
            code = *src.get(sp).ok_or("truncated Yaz0 code byte")?;
            sp += 1;
            bits_left = 8;
        }

        if code & 0x80 != 0 {
            out.push(*src.get(sp).ok_or("truncated Yaz0 literal")?);
            sp += 1;
        } else {
            let a = *src.get(sp).ok_or("truncated Yaz0 backreference")?;
            let b = *src.get(sp + 1).ok_or("truncated Yaz0 backreference")?;
            sp += 2;

            let distance = ((((a as usize) & 0x0f) << 8) | b as usize) + 1;
            if distance > out.len() {
                return Err(format!("invalid Yaz0 distance {distance} at output {}", out.len()));
            }
            let mut length = (a >> 4) as usize;
            if length == 0 {
                length = *src.get(sp).ok_or("truncated Yaz0 long length")? as usize + 0x12;
                sp += 1;
            } else {
                length += 2;
            }

            // Preserve the inlined original literal path; keep bulk-copy
            // code outside the main token-dispatch loop.
            let count = length.min(out_len - out.len());
            append_match(&mut out, distance, count);
        }

        code <<= 1;
        bits_left -= 1;
    }
    Ok(out)
}

#[inline(never)]
fn append_match(out: &mut Vec<u8>, distance: usize, count: usize) {
    debug_assert!(distance > 0 && distance <= out.len());
    if count == 0 {
        return;
    }
    let start = out.len() - distance;
    let initial = distance.min(count);
    out.extend_from_within(start..start + initial);
    let mut written = initial;
    while written < count {
        let step = written.min(count - written);
        let copied_start = out.len() - written;
        out.extend_from_within(copied_start..copied_start + step);
        written += step;
    }
}


#[cfg(test)]
#[path = "yaz0_baseline.rs"]
mod original;

#[cfg(test)]
mod tests {
    use super::*;

    #[derive(Clone, Copy)]
    enum Token {
        Byte(u8),
        Match { distance: usize, length: usize },
    }

    fn frame(tokens: &[Token], output_len: usize) -> Vec<u8> {
        let mut src = b"Yaz0".to_vec();
        src.extend_from_slice(&(output_len as u32).to_be_bytes());
        src.extend_from_slice(&[0; 8]);
        for group in tokens.chunks(8) {
            let flags = group.iter().enumerate().fold(0u8, |flags, (i, token)| {
                flags | if matches!(token, Token::Byte(_)) { 1 << (7 - i) } else { 0 }
            });
            src.push(flags);
            for token in group {
                match token {
                    Token::Byte(byte) => src.push(*byte),
                    Token::Match { distance, length } => {
                        assert!((1..=4096).contains(distance));
                        assert!((3..=273).contains(length));
                        let offset = distance - 1;
                        if *length >= 18 {
                            src.push(((offset >> 8) & 15) as u8);
                            src.push(offset as u8);
                            src.push((length - 18) as u8);
                        } else {
                            src.push((((length - 2) << 4) | ((offset >> 8) & 15)) as u8);
                            src.push(offset as u8);
                        }
                    }
                }
            }
        }
        src
    }

    #[test]
    fn literal_only_matches_reference() {
        let f = frame(&[Token::Byte(b't'), Token::Byte(b'e'), Token::Byte(b's'), Token::Byte(b't')], 4);
        assert_eq!(decompress_yaz0(&f).unwrap(), b"test");
        assert_eq!(decompress_yaz0(&f), original::decompress_yaz0(&f));
    }

    #[test]
    fn every_distance_and_length_class_matches_reference() {
        for distance in [1usize, 2, 3, 4, 7, 15, 16, 31, 32, 63, 64, 255, 256, 4096] {
            let mut tokens = vec![Token::Byte(0x65); distance];
            for length in [3, 4, 7, 8, 15, 16, 17, 18, 19, 32, 64, 128, 273] {
                tokens.push(Token::Match { distance, length });
            }
            let n: usize = distance + [3usize, 4, 7, 8, 15, 16, 17, 18, 19, 32, 64, 128, 273].iter().sum::<usize>();
            let encoded = frame(&tokens, n);
            assert_eq!(decompress_yaz0(&encoded), original::decompress_yaz0(&encoded), "distance={distance}");
        }
    }

    #[test]
    fn deterministic_compressed_and_literal_mixtures_match_reference() {
        let mut seed = 0x5379_54dau32;
        for case in 0..80 {
            let mut tokens = Vec::with_capacity(501);
            tokens.push(Token::Byte(case as u8));
            let mut produced = 1usize;
            for _ in 0..500 {
                seed ^= seed << 13;
                seed ^= seed >> 17;
                seed ^= seed << 5;
                if seed & 3 == 0 {
                    tokens.push(Token::Byte((seed >> 16) as u8));
                    produced += 1;
                } else {
                    let distance = (seed as usize % produced.min(4096)) + 1;
                    let length = 3 + ((seed >> 8) as usize % 271);
                    tokens.push(Token::Match { distance, length });
                    produced += length;
                }
            }
            let encoded = frame(&tokens, produced);
            let actual = decompress_yaz0(&encoded).unwrap();
            assert_eq!(actual, original::decompress_yaz0(&encoded).unwrap(), "case={case}");
            assert_eq!(actual.len(), produced);
        }
    }

    #[test]
    fn match_that_crosses_declared_output_end_is_clipped() {
        let f = frame(&[Token::Byte(0x42), Token::Match { distance: 1, length: 273 }], 11);
        assert_eq!(decompress_yaz0(&f).unwrap(), vec![0x42; 11]);
        assert_eq!(decompress_yaz0(&f), original::decompress_yaz0(&f));
    }

    #[test]
    fn malformed_headers_and_truncated_tokens_preserve_original_errors() {
        let candidates: &[&[u8]] = &[b"", b"RARC", b"Yaz0", b"Yaz0\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00",
          b"Yaz0\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x80",
          b"Yaz0\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00",
          b"Yaz0\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
          b"Yaz0\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"];
        for bytes in candidates {
            assert_eq!(decompress_yaz0(bytes), original::decompress_yaz0(bytes));
        }
    }

    #[test]
    fn empty_output_does_not_consume_tokens() {
        let src = frame(&[], 0);
        assert_eq!(decompress_yaz0(&src), Ok(Vec::new()));
        assert_eq!(decompress_yaz0(&src), original::decompress_yaz0(&src));
    }
}
