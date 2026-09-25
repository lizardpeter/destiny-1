use std::{env, fs, hint::black_box, time::Instant};

use d1_oodle3::lzh::{decode_stream, stage_profile_reset, stage_profile_snapshot};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut args = env::args().skip(1);
    let raw_len: usize = args
        .next()
        .ok_or("usage: stage_profile_decode <raw_len> <repeats> <compressed>...")?
        .parse()?;
    let repeats: usize = args
        .next()
        .ok_or("usage: stage_profile_decode <raw_len> <repeats> <compressed>...")?
        .parse()?;
    let paths: Vec<_> = args.collect();
    if paths.is_empty() || repeats == 0 {
        return Err("at least one compressed input and one repeat are required".into());
    }

    let inputs: Vec<Vec<u8>> = paths
        .iter()
        .map(fs::read)
        .collect::<Result<_, _>>()?;

    // Warm the allocator, instruction cache, and branch predictors first.
    for input in &inputs {
        black_box(decode_stream(input, raw_len)?);
    }

    stage_profile_reset();
    let started = Instant::now();
    let mut decoded_bytes = 0usize;
    for _ in 0..repeats {
        for input in &inputs {
            let decoded = decode_stream(input, raw_len)?;
            decoded_bytes += decoded.len();
            black_box(decoded);
        }
    }
    let wall_ns = started.elapsed().as_nanos().min(u128::from(u64::MAX)) as u64;
    let s = stage_profile_snapshot();

    let measured_ns = s
        .model_parse_ns
        .saturating_add(s.table_build_ns)
        .saturating_add(s.payload_ns);
    let residual_ns = wall_ns.saturating_sub(measured_ns);

    let pct = |part: u64| -> f64 {
        if wall_ns == 0 {
            0.0
        } else {
            part as f64 * 100.0 / wall_ns as f64
        }
    };
    let mib_s = if wall_ns == 0 {
        0.0
    } else {
        decoded_bytes as f64 / (1024.0 * 1024.0) / (wall_ns as f64 / 1e9)
    };

    println!("STAGE_FILES {}", inputs.len());
    println!("STAGE_REPEATS {}", repeats);
    println!("STAGE_RAW_BYTES {}", decoded_bytes);
    println!("STAGE_MODELS {}", s.models);
    println!("STAGE_QUANTA {}", s.quanta);
    println!("STAGE_WALL_NS {}", wall_ns);
    println!("STAGE_MODEL_PARSE_NS {}", s.model_parse_ns);
    println!("STAGE_TABLE_BUILD_NS {}", s.table_build_ns);
    println!("STAGE_PAYLOAD_NS {}", s.payload_ns);
    println!("STAGE_RESIDUAL_NS {}", residual_ns);
    println!("STAGE_MODEL_PARSE_PCT {:.6}", pct(s.model_parse_ns));
    println!("STAGE_TABLE_BUILD_PCT {:.6}", pct(s.table_build_ns));
    println!("STAGE_PAYLOAD_PCT {:.6}", pct(s.payload_ns));
    println!("STAGE_RESIDUAL_PCT {:.6}", pct(residual_ns));
    println!("STAGE_THROUGHPUT_MIB_S {:.6}", mib_s);
    Ok(())
}
