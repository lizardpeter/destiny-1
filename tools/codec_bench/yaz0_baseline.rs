//! Nintendo Yaz0 decompression used by SMG retail archives.

pub fn decompress_yaz0(src: &[u8]) -> Result<Vec<u8>, String> {
    if src.len() < 16 || &src[..4] != b"Yaz0" {
        return Err("not a Yaz0 stream".to_owned());
    }
    let out_len = u32::from_be_bytes(src[4..8].try_into().unwrap()) as usize;
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

            for _ in 0..length {
                if out.len() == out_len {
                    break;
                }
                let value = out[out.len() - distance];
                out.push(value);
            }
        }

        code <<= 1;
        bits_left -= 1;
    }

    Ok(out)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn literal_only_stream_decodes() {
        let mut src = b"Yaz0".to_vec();
        src.extend_from_slice(&4u32.to_be_bytes());
        src.extend_from_slice(&[0; 8]);
        src.push(0xF0);
        src.extend_from_slice(b"test");
        assert_eq!(decompress_yaz0(&src).unwrap(), b"test");
    }

    #[test]
    fn rejects_non_yaz0() {
        assert!(decompress_yaz0(b"RARC").is_err());
    }
}
