const FASTFILE_KEY: [u8;32] = [0;32];
const SALSA_SIGMA: [u8;16] = *b"expand 32-byte k";
pub fn salsa20_key_state(key: &[u8; 32]) -> [u32; 16] {
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
pub fn salsa20_xor_into(
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

