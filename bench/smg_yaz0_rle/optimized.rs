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
            // Fast path for a complete all-literal code group. This bypasses
            // eight separate push/check/branch cycles without any speculative
            // input or output reads. The final partial group is also exact.
            if code == 0xff {
                let count = (out_len - out.len()).min(8);
                let literals = src
                    .get(sp..)
                    .and_then(|rest| rest.get(..count))
                    .ok_or("truncated Yaz0 literal")?;
                out.extend_from_slice(literals);
                sp += count;
                bits_left = 0;
                continue;
            }
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
    if distance == 1 {
        // A one-byte Yaz0 backreference is a repeated-byte fill, not a
        // general overlapping copy. Vec::resize appends exactly those bytes
        // without repeated doubling or temporary scratch allocations.
        let value = out[out.len() - 1];
        out.resize(out.len() + count, value);
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

