use std::{env, fs, hint::black_box};

use d1_oodle3::lzh::{decode_stream, profile_reset, profile_snapshot};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut args = env::args().skip(1);
    let raw_len: usize = args
        .next()
        .ok_or("usage: profile_decode <raw_len> <compressed>...")?
        .parse()?;
    let paths: Vec<_> = args.collect();
    if paths.is_empty() {
        return Err("at least one compressed input is required".into());
    }

    profile_reset();
    let mut decoded_bytes = 0usize;
    for path in &paths {
        let input = fs::read(path)?;
        let decoded = decode_stream(&input, raw_len)?;
        decoded_bytes += decoded.len();
        black_box(decoded);
    }

    let s = profile_snapshot();
    println!("PROFILE_FILES {}", paths.len());
    println!("PROFILE_RAW_BYTES {}", decoded_bytes);
    println!("PROFILE_MODELS {}", s.models);
    println!("PROFILE_MODEL_SYMBOLS {}", s.model_symbols);
    println!("PROFILE_MODEL_SPARSE {}", s.model_sparse);
    println!("PROFILE_MODEL_RICE {}", s.model_rice);
    println!("PROFILE_LONG_TABLES_TOTAL {}", s.long_tables_total);
    println!("PROFILE_LONG_TABLES_MAX {}", s.long_tables_max);
    println!("PROFILE_QUANTA {}", s.quanta);
    println!("PROFILE_HUFFMAN_FAST {}", s.huffman_fast);
    println!("PROFILE_HUFFMAN_LONG {}", s.huffman_long);
    println!("PROFILE_HUFFMAN_TAIL {}", s.huffman_tail);
    println!("PROFILE_LITERALS {}", s.literals);
    println!("PROFILE_RECENT_MATCHES {}", s.recent_matches);
    println!("PROFILE_EXPLICIT_MATCHES {}", s.explicit_matches);
    println!("PROFILE_DISTANCE_1 {}", s.distance_1);
    println!("PROFILE_DISTANCE_2 {}", s.distance_2);
    println!("PROFILE_DISTANCE_3 {}", s.distance_3);
    println!("PROFILE_DISTANCE_4 {}", s.distance_4);
    println!("PROFILE_DISTANCE_5_8 {}", s.distance_5_8);
    println!("PROFILE_DISTANCE_9_16 {}", s.distance_9_16);
    println!("PROFILE_DISTANCE_17_32 {}", s.distance_17_32);
    println!("PROFILE_DISTANCE_33_PLUS {}", s.distance_33_plus);
    println!("PROFILE_LENGTH_2_4 {}", s.length_2_4);
    println!("PROFILE_LENGTH_5_8 {}", s.length_5_8);
    println!("PROFILE_LENGTH_9_16 {}", s.length_9_16);
    println!("PROFILE_LENGTH_17_32 {}", s.length_17_32);
    println!("PROFILE_LENGTH_33_64 {}", s.length_33_64);
    println!("PROFILE_LENGTH_65_PLUS {}", s.length_65_plus);
    println!("PROFILE_REFILL_32 {}", s.refill_32);
    println!("PROFILE_REFILL_8 {}", s.refill_8);
    Ok(())
}
