use std::{fs, io::Read, path::Path};

use flate2::{read::DeflateDecoder, Decompress, FlushDecompress, Status};
use serde::Serialize;
use sha1::{Digest, Sha1};
use sha2::Sha256;

/// Ring buffer the game reads FastFile records through (see `decode_bytes`).
const VANILLA_BUFFER_SIZE: usize = 0x80000;
const HEADER_SIZE: usize = 0x138;
const MAX_ENCRYPTED_RECORD: usize = 0x8000;
const STREAM_COUNT: usize = 4;
const TABLE_ENTRIES: usize = 800;
const ENTRY_SIZE: usize = 20;
const TABLE_DWORDS: usize = TABLE_ENTRIES * (ENTRY_SIZE / 4);
const FASTFILE_VERSION: u32 = 0x93;
const FASTFILE_KEY: [u8; 32] = [0u8; 32];
// The benchmark uses a synthetic key, not the original retail key.
const SALSA_SIGMA: [u8; 16] = *b"expand 32-byte k";

#[derive(Debug, Clone, Serialize)]
pub struct FastFileRecordAudit {
    pub record: usize,
    pub stream: usize,
    pub stream_counter_before: usize,
    pub table_index: usize,
    pub nonce_hex: String,
    pub length_field_offset: usize,
    pub ciphertext_offset: usize,
    pub encrypted_bytes: usize,
    pub expanded_bytes: usize,
    pub plaintext_sha1: String,
}

#[derive(Debug, Clone, Serialize)]
pub struct FastFileSummary {
    pub zone_name: String,
    pub encrypted_file_bytes: usize,
    pub records: usize,
    pub expanded_stream_bytes: usize,
    pub stream_record_counts: [usize; STREAM_COUNT],
    pub encrypted_sha256: String,
    pub expanded_sha256: String,
}

#[derive(Debug, Serialize)]
struct AuditFile<'a> {
    summary: &'a FastFileSummary,
    records: &'a [FastFileRecordAudit],
}

pub fn decode_file(input: &Path, output: &Path, audit_output: Option<&Path>) -> Result<FastFileSummary, String> {
    let encrypted = fs::read(input)
        .map_err(|error| format!("failed to read {}: {error}", input.display()))?;
    let (expanded, records, summary) = decode_bytes(&encrypted)?;

    if let Some(parent) = output.parent() {
        fs::create_dir_all(parent)
            .map_err(|error| format!("failed to create {}: {error}", parent.display()))?;
    }
    fs::write(output, &expanded)
        .map_err(|error| format!("failed to write {}: {error}", output.display()))?;

    if let Some(audit_output) = audit_output {
        if let Some(parent) = audit_output.parent() {
            fs::create_dir_all(parent)
                .map_err(|error| format!("failed to create {}: {error}", parent.display()))?;
        }
        let json = serde_json::to_string_pretty(&AuditFile {
            summary: &summary,
            records: &records,
        })
        .map_err(|error| format!("failed to encode fastfile audit: {error}"))?;
        fs::write(audit_output, format!("{json}\n"))
            .map_err(|error| format!("failed to write {}: {error}", audit_output.display()))?;
    }

    Ok(summary)
}

pub fn decode_bytes(ff: &[u8]) -> Result<(Vec<u8>, Vec<FastFileRecordAudit>, FastFileSummary), String> {
    validate_header(ff)?;
    let zone_name = zone_name(ff)?;
    let mut table = initial_digest_table(&zone_name)?;
    let mut stream_counters = [0usize; STREAM_COUNT];
    let mut expanded_stream = Vec::new();
    let mut audits = Vec::new();
    // Reuse the largest per-record decrypted buffer; records are at most
    // 0x8000 bytes, and only the encrypted region is ever exposed to DEFLATE.
    let mut plaintext = Vec::<u8>::new();
    let salsa_key_state = salsa20_key_state(&FASTFILE_KEY);
    let mut inflate = Decompress::new(false);

    let mut pos = HEADER_SIZE;
    let mut record_index = 0usize;
    while pos + 4 <= ff.len() {
        // The game streams records through a 0x80000-byte ring buffer; a length
        // field that would straddle the buffer end is padded to the next buffer.
        let buffer_offset = pos % VANILLA_BUFFER_SIZE;
        if buffer_offset + 4 > VANILLA_BUFFER_SIZE {
            pos += VANILLA_BUFFER_SIZE - buffer_offset;
            if pos + 4 > ff.len() {
                break;
            }
        }
        let length_field_offset = pos;
        let encrypted_length = read_u32(ff, pos)? as usize;
        pos += 4;
        if encrypted_length == 0 {
            if ff[length_field_offset..].iter().any(|byte| *byte != 0) {
                return Err(format!(
                    "nonzero bytes after zero record marker at 0x{length_field_offset:X}"
                ));
            }
            break;
        }
        if encrypted_length > MAX_ENCRYPTED_RECORD {
            return Err(format!(
                "record {record_index}: encrypted length 0x{encrypted_length:X} exceeds 0x{MAX_ENCRYPTED_RECORD:X}"
            ));
        }
        let end = pos
            .checked_add(encrypted_length)
            .ok_or_else(|| "fastfile record length overflow".to_owned())?;
        let ciphertext = ff
            .get(pos..end)
            .ok_or_else(|| format!("record {record_index}: truncated ciphertext"))?;

        let stream = record_index % STREAM_COUNT;
        let counter_before = stream_counters[stream];
        let table_index = (counter_before * STREAM_COUNT + stream) % TABLE_ENTRIES;
        let table_offset = table_index * ENTRY_SIZE;
        let nonce: [u8; 8] = table[table_offset..table_offset + 8]
            .try_into()
            .map_err(|_| "invalid T6 digest table nonce".to_owned())?;

        salsa20_xor_into(ciphertext, &salsa_key_state, &nonce, &mut plaintext);
        let before = expanded_stream.len();
        inflate.reset(false);
        if inflate_raw_record(&mut inflate, &plaintext, &mut expanded_stream).is_err() {
            // Keep the exact original error path and accept all valid streams
            // the legacy read-to-end decoder could accept.
            expanded_stream.truncate(before);
            let mut decoder = DeflateDecoder::new(plaintext.as_slice());
            decoder
                .read_to_end(&mut expanded_stream)
                .map_err(|error| {
                    format!(
                        "record {record_index} stream {stream}: raw-DEFLATE failed; nonce={}: {error}",
                        hex(&nonce)
                    )
                })?;
        }
        let expanded_bytes = expanded_stream.len() - before;

        let digest = Sha1::digest(&plaintext);
        let next_counter = counter_before + 1;
        let next_table_index = (next_counter * STREAM_COUNT + stream) % TABLE_ENTRIES;
        let next_offset = next_table_index * ENTRY_SIZE;
        for (index, value) in digest.iter().enumerate() {
            table[next_offset + index] ^= *value;
        }
        stream_counters[stream] = next_counter;

        audits.push(FastFileRecordAudit {
            record: record_index,
            stream,
            stream_counter_before: counter_before,
            table_index,
            nonce_hex: hex(&nonce),
            length_field_offset,
            ciphertext_offset: pos,
            encrypted_bytes: encrypted_length,
            expanded_bytes,
            plaintext_sha1: hex(digest.as_slice()),
        });

        pos = end;
        record_index += 1;
    }

    if pos < ff.len() && ff[pos..].iter().any(|byte| *byte != 0) {
        return Err(format!("nonzero trailing bytes at 0x{pos:X}"));
    }

    let summary = FastFileSummary {
        zone_name,
        encrypted_file_bytes: ff.len(),
        records: audits.len(),
        expanded_stream_bytes: expanded_stream.len(),
        stream_record_counts: stream_counters,
        encrypted_sha256: hex(Sha256::digest(ff).as_slice()),
        expanded_sha256: hex(Sha256::digest(&expanded_stream).as_slice()),
    };
    Ok((expanded_stream, audits, summary))
}

/// Stream the raw-DEFLATE payload into the final expanded FastFile
/// buffer using one resettable inflater, retaining its internal history
/// allocations between independent records. Fall back to the reference
/// Read-based decoder if a stream cannot be proven complete.
fn inflate_raw_record(inflate: &mut Decompress, input: &[u8], output: &mut Vec<u8>) -> Result<(), ()> {
    let mut input_pos = 0usize;
    loop {
        // decompress_vec only writes to spare Vec capacity and will not
        // allocate or grow it itself.
        output.reserve(64 * 1024);
        let before_input = inflate.total_in();
        let before_output = output.len();
        let status = inflate
            .decompress_vec(&input[input_pos..], output, FlushDecompress::None)
            .map_err(|_| ())?;
        input_pos += (inflate.total_in() - before_input) as usize;
        if status == Status::StreamEnd {
            return Ok(());
        }
        if inflate.total_in() == before_input && output.len() == before_output {
            return Err(());
        }
    }
}

fn validate_header(ff: &[u8]) -> Result<(), String> {
    if ff.len() < HEADER_SIZE {
        return Err("file is too small to be a retail T6 signed fastfile".to_owned());
    }
    if ff.get(..8) != Some(b"TAff0100") {
        return Err(format!(
            "unexpected T6 fastfile magic: {}",
            ff.get(..8).map(hex).unwrap_or_else(|| "<truncated>".to_owned())
        ));
    }
    let version = read_u32(ff, 8)?;
    if version != FASTFILE_VERSION {
        return Err(format!(
            "unsupported T6 fastfile version 0x{version:X}; expected 0x{FASTFILE_VERSION:X}"
        ));
    }
    if ff.get(12..20) != Some(b"PHEEBs71") {
        return Err("fastfile is not the expected PHEEBs71 secure PC T6 format".to_owned());
    }
    Ok(())
}

fn zone_name(ff: &[u8]) -> Result<String, String> {
    let field = ff
        .get(24..56)
        .ok_or_else(|| "truncated T6 zone-name field".to_owned())?;
    let end = field.iter().position(|byte| *byte == 0).unwrap_or(field.len());
    if end == 0 {
        return Err("T6 zone-name field is empty".to_owned());
    }
    std::str::from_utf8(&field[..end])
        .map(str::to_owned)
        .map_err(|_| "T6 zone-name field is not ASCII/UTF-8".to_owned())
}

fn initial_digest_table(zone_name: &str) -> Result<Vec<u8>, String> {
    let zone = zone_name.as_bytes();
    if zone.is_empty() || !zone.is_ascii() {
        return Err("invalid T6 zone name for digest-table initialization".to_owned());
    }
    let mut table = vec![0u8; TABLE_ENTRIES * ENTRY_SIZE];
    for dword_index in 0..TABLE_DWORDS {
        let value = zone[dword_index % zone.len()];
        let offset = dword_index * 4;
        table[offset..offset + 4].fill(value);
    }
    Ok(table)
}

/// Pre-expanded Salsa20/20 key+sigma words. This never changes with the
/// FastFile's per-record nonces, so avoid rebuilding it for every 64-byte block.
#[inline]
fn salsa20_key_state(key: &[u8; 32]) -> [u32; 16] {
    let k = words8(key);
    let c = words4(&SALSA_SIGMA);
    [
        c[0], k[0], k[1], k[2], k[3], c[1],
        0, 0, 0, 0, c[2], k[4], k[5], k[6], k[7], c[3],
    ]
}

/// Decrypt directly into a retained per-stream scratch buffer, avoiding one
/// Vec allocation for each encrypted FastFile record. The stream uses Salsa20
/// counter zero at the start of every record, matching the original decoder.
fn salsa20_xor_into(
    ciphertext: &[u8],
    base_state: &[u32; 16],
    nonce: &[u8; 8],
    output: &mut Vec<u8>,
) {
    output.resize(ciphertext.len(), 0);
    let mut state = *base_state;
    let nonce_words = words2(nonce);
    state[6] = nonce_words[0];
    state[7] = nonce_words[1];
    for (block_index, (source, destination)) in ciphertext
        .chunks(64)
        .zip(output.chunks_mut(64))
        .enumerate()
    {
        state[8] = block_index as u32;
        state[9] = (block_index >> 32) as u32;
        let key_stream = salsa20_block_from_state(&state);
        for (dst, (&src, &key)) in destination.iter_mut().zip(source.iter().zip(key_stream.iter())) {
            *dst = src ^ key;
        }
    }
}

/// The original state-independent Salsa20 block kernel can still be exercised
/// by the known official reference-vector tests.
#[inline]
fn salsa20_block_from_state(initial: &[u32; 16]) -> [u8; 64] {
    let mut x = *initial;
    for _ in 0..10 {
        x[4] ^= x[0].wrapping_add(x[12]).rotate_left(7);
        x[8] ^= x[4].wrapping_add(x[0]).rotate_left(9);
        x[12] ^= x[8].wrapping_add(x[4]).rotate_left(13);
        x[0] ^= x[12].wrapping_add(x[8]).rotate_left(18);

        x[9] ^= x[5].wrapping_add(x[1]).rotate_left(7);
        x[13] ^= x[9].wrapping_add(x[5]).rotate_left(9);
        x[1] ^= x[13].wrapping_add(x[9]).rotate_left(13);
        x[5] ^= x[1].wrapping_add(x[13]).rotate_left(18);

        x[14] ^= x[10].wrapping_add(x[6]).rotate_left(7);
        x[2] ^= x[14].wrapping_add(x[10]).rotate_left(9);
        x[6] ^= x[2].wrapping_add(x[14]).rotate_left(13);
        x[10] ^= x[6].wrapping_add(x[2]).rotate_left(18);

        x[3] ^= x[15].wrapping_add(x[11]).rotate_left(7);
        x[7] ^= x[3].wrapping_add(x[15]).rotate_left(9);
        x[11] ^= x[7].wrapping_add(x[3]).rotate_left(13);
        x[15] ^= x[11].wrapping_add(x[7]).rotate_left(18);

        x[1] ^= x[0].wrapping_add(x[3]).rotate_left(7);
        x[2] ^= x[1].wrapping_add(x[0]).rotate_left(9);
        x[3] ^= x[2].wrapping_add(x[1]).rotate_left(13);
        x[0] ^= x[3].wrapping_add(x[2]).rotate_left(18);

        x[6] ^= x[5].wrapping_add(x[4]).rotate_left(7);
        x[7] ^= x[6].wrapping_add(x[5]).rotate_left(9);
        x[4] ^= x[7].wrapping_add(x[6]).rotate_left(13);
        x[5] ^= x[4].wrapping_add(x[7]).rotate_left(18);

        x[11] ^= x[10].wrapping_add(x[9]).rotate_left(7);
        x[8] ^= x[11].wrapping_add(x[10]).rotate_left(9);
        x[9] ^= x[8].wrapping_add(x[11]).rotate_left(13);
        x[10] ^= x[9].wrapping_add(x[8]).rotate_left(18);

        x[12] ^= x[15].wrapping_add(x[14]).rotate_left(7);
        x[13] ^= x[12].wrapping_add(x[15]).rotate_left(9);
        x[14] ^= x[13].wrapping_add(x[12]).rotate_left(13);
        x[15] ^= x[14].wrapping_add(x[13]).rotate_left(18);
    }

    let mut output = [0u8; 64];
    for index in 0..16 {
        let word = x[index].wrapping_add(initial[index]).to_le_bytes();
        output[index * 4..index * 4 + 4].copy_from_slice(&word);
    }
    output
}

fn salsa20_xor(data: &[u8], key: &[u8; 32], nonce: &[u8; 8]) -> Vec<u8> {
    let mut output = vec![0u8; data.len()];
    for (block_index, chunk) in data.chunks(64).enumerate() {
        let key_stream = salsa20_block(key, nonce, block_index as u64);
        let offset = block_index * 64;
        for (index, value) in chunk.iter().enumerate() {
            output[offset + index] = *value ^ key_stream[index];
        }
    }
    output
}

fn salsa20_block(key: &[u8; 32], nonce: &[u8; 8], counter: u64) -> [u8; 64] {
    let k = words8(key);
    let n = words2(nonce);
    let c = words4(&SALSA_SIGMA);
    let initial = [
        c[0],
        k[0],
        k[1],
        k[2],
        k[3],
        c[1],
        n[0],
        n[1],
        counter as u32,
        (counter >> 32) as u32,
        c[2],
        k[4],
        k[5],
        k[6],
        k[7],
        c[3],
    ];
    let mut x = initial;
    for _ in 0..10 {
        x[4] ^= x[0].wrapping_add(x[12]).rotate_left(7);
        x[8] ^= x[4].wrapping_add(x[0]).rotate_left(9);
        x[12] ^= x[8].wrapping_add(x[4]).rotate_left(13);
        x[0] ^= x[12].wrapping_add(x[8]).rotate_left(18);

        x[9] ^= x[5].wrapping_add(x[1]).rotate_left(7);
        x[13] ^= x[9].wrapping_add(x[5]).rotate_left(9);
        x[1] ^= x[13].wrapping_add(x[9]).rotate_left(13);
        x[5] ^= x[1].wrapping_add(x[13]).rotate_left(18);

        x[14] ^= x[10].wrapping_add(x[6]).rotate_left(7);
        x[2] ^= x[14].wrapping_add(x[10]).rotate_left(9);
        x[6] ^= x[2].wrapping_add(x[14]).rotate_left(13);
        x[10] ^= x[6].wrapping_add(x[2]).rotate_left(18);

        x[3] ^= x[15].wrapping_add(x[11]).rotate_left(7);
        x[7] ^= x[3].wrapping_add(x[15]).rotate_left(9);
        x[11] ^= x[7].wrapping_add(x[3]).rotate_left(13);
        x[15] ^= x[11].wrapping_add(x[7]).rotate_left(18);

        x[1] ^= x[0].wrapping_add(x[3]).rotate_left(7);
        x[2] ^= x[1].wrapping_add(x[0]).rotate_left(9);
        x[3] ^= x[2].wrapping_add(x[1]).rotate_left(13);
        x[0] ^= x[3].wrapping_add(x[2]).rotate_left(18);

        x[6] ^= x[5].wrapping_add(x[4]).rotate_left(7);
        x[7] ^= x[6].wrapping_add(x[5]).rotate_left(9);
        x[4] ^= x[7].wrapping_add(x[6]).rotate_left(13);
        x[5] ^= x[4].wrapping_add(x[7]).rotate_left(18);

        x[11] ^= x[10].wrapping_add(x[9]).rotate_left(7);
        x[8] ^= x[11].wrapping_add(x[10]).rotate_left(9);
        x[9] ^= x[8].wrapping_add(x[11]).rotate_left(13);
        x[10] ^= x[9].wrapping_add(x[8]).rotate_left(18);

        x[12] ^= x[15].wrapping_add(x[14]).rotate_left(7);
        x[13] ^= x[12].wrapping_add(x[15]).rotate_left(9);
        x[14] ^= x[13].wrapping_add(x[12]).rotate_left(13);
        x[15] ^= x[14].wrapping_add(x[13]).rotate_left(18);
    }

    let mut output = [0u8; 64];
    for index in 0..16 {
        let word = x[index].wrapping_add(initial[index]).to_le_bytes();
        output[index * 4..index * 4 + 4].copy_from_slice(&word);
    }
    output
}

fn words2(bytes: &[u8; 8]) -> [u32; 2] {
    [
        u32::from_le_bytes(bytes[0..4].try_into().unwrap()),
        u32::from_le_bytes(bytes[4..8].try_into().unwrap()),
    ]
}

fn words4(bytes: &[u8; 16]) -> [u32; 4] {
    std::array::from_fn(|index| {
        u32::from_le_bytes(bytes[index * 4..index * 4 + 4].try_into().unwrap())
    })
}

fn words8(bytes: &[u8; 32]) -> [u32; 8] {
    std::array::from_fn(|index| {
        u32::from_le_bytes(bytes[index * 4..index * 4 + 4].try_into().unwrap())
    })
}

fn read_u32(bytes: &[u8], offset: usize) -> Result<u32, String> {
    let end = offset
        .checked_add(4)
        .ok_or_else(|| "u32 offset overflow".to_owned())?;
    let raw: [u8; 4] = bytes
        .get(offset..end)
        .ok_or_else(|| format!("truncated u32 at 0x{offset:X}"))?
        .try_into()
        .map_err(|_| "invalid u32 slice".to_owned())?;
    Ok(u32::from_le_bytes(raw))
}

fn hex(bytes: &[u8]) -> String {
    const DIGITS: &[u8; 16] = b"0123456789abcdef";
    let mut output = String::with_capacity(bytes.len() * 2);
    for byte in bytes {
        output.push(DIGITS[(byte >> 4) as usize] as char);
        output.push(DIGITS[(byte & 0x0f) as usize] as char);
    }
    output
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn salsa20_reference_vector_zero_key_and_nonce() {
        let block = salsa20_block(&[0u8; 32], &[0u8; 8], 0);
        assert_eq!(
            hex(&block[..16]),
            "9a97f65b9b4c721b960a672145fca8d4"
        );
    }

    #[test]
    fn salsa20_retained_scratch_matches_original_for_all_record_boundaries() {
        let base = salsa20_key_state(&FASTFILE_KEY);
        let mut buffer = Vec::<u8>::new();
        let mut state = 0x1122_3344u32;
        for len in [0usize,1,2,3,15,16,31,32,63,64,65,127,128,129,511,512,513,4096,32767,32768] {
            let mut ciphertext = vec![0u8; len];
            for b in &mut ciphertext {
                state ^= state << 13; state ^= state >> 17; state ^= state << 5;
                *b = state as u8;
            }
            for seed in [0u8, 1, 57, 199, 255] {
                let mut nonce = [0u8; 8];
                for (i, b) in nonce.iter_mut().enumerate() {
                    *b = seed.wrapping_mul((i + 1) as u8);
                }
                salsa20_xor_into(&ciphertext, &base, &nonce, &mut buffer);
                let original = salsa20_xor(&ciphertext, &FASTFILE_KEY, &nonce);
                assert_eq!(buffer, original, "length={len} seed={seed}");
                let encoded = buffer.clone();
                salsa20_xor_into(&encoded, &base, &nonce, &mut buffer);
                assert_eq!(buffer, ciphertext, "Salsa20 involution length={len} seed={seed}");
            }
        }
    }

    #[test]
    fn digest_table_repeats_zone_name_bytes_per_dword() {
        let table = initial_digest_table("ab").unwrap();
        assert_eq!(&table[0..4], b"aaaa");
        assert_eq!(&table[4..8], b"bbbb");
        assert_eq!(&table[8..12], b"aaaa");
    }
    #[test]
    fn reusable_raw_inflater_matches_reference_variable_lengths() {
        use flate2::{write::DeflateEncoder, Compression};
        use std::io::Write;
        let mut inflater=Decompress::new(false);
        for (n,level) in [(1usize,0u32),(3,6),(64,1),(4096,6),(32768,6),(65536,9),(5,0),(8192,0)] {
            let payload=(0..n).map(|i| ((i.wrapping_mul(53)+n)&255)as u8).collect::<Vec<_>>();
            let mut enc=DeflateEncoder::new(Vec::new(),Compression::new(level));
            enc.write_all(&payload).unwrap();
            let compressed=enc.finish().unwrap();
            inflater.reset(false);
            let mut out=Vec::new();
            inflate_raw_record(&mut inflater,&compressed,&mut out).expect("valid raw DEFLATE");
            let mut original=Vec::new();
            DeflateDecoder::new(compressed.as_slice()).read_to_end(&mut original).unwrap();
            assert_eq!(out,original,"length {n}, level {level}");
        }
    }

    #[test]
    fn raw_inflater_rejects_incomplete_stream_for_reference_fallback() {
        let mut inflater=Decompress::new(false);
        let mut out=Vec::new();
        let input=[0xffu8];
        let result=inflate_raw_record(&mut inflater,&input,&mut out);
        assert!(result.is_err());
    }

}

pub fn benchmark_encrypt(plaintext: &[u8], nonce: &[u8; 8]) -> Vec<u8> {
    salsa20_xor(plaintext, &FASTFILE_KEY, nonce)
}
pub fn benchmark_crypto_reuse(plaintext: &[u8], nonce: &[u8; 8], output: &mut Vec<u8>) {
    let base = salsa20_key_state(&FASTFILE_KEY);
    salsa20_xor_into(plaintext, &base, nonce, output)
}
