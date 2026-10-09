#![allow(dead_code)]
#[path = "retail_ipak_crc.rs"]
mod retail_ipak_crc;
use std::{hint::black_box,time::Instant};

#[inline(never)]
fn baseline(bytes: &[u8]) -> u32 {
    let mut crc = !0u32;
    for &byte in bytes {
        crc ^= u32::from(byte);
        for _ in 0..8 {
            crc = (crc >> 1) ^ (0xedb8_8320u32 & (crc & 1).wrapping_neg());
        }
    }
    !crc
}
fn main() {
    let lengths=[32_768usize,262_144,4*1024*1024];
    let mut speedups=Vec::new();
    for len in lengths {
        let mut input=vec![0u8;len];
        let mut v=0x12345678u32;
        for x in &mut input {
            v ^= v << 13;v ^= v >> 17;v ^= v << 5;*x=v as u8;
        }
        assert_eq!(baseline(&input),retail_ipak_crc::crc32(&input));
        let mut measurements=Vec::new();
        // Each trial executes both implementations on the same input.
        for round in 0..7 {
            let mut rates=[0f64;2];
            for index in 0..2 {
                let optimized=(index==0)==(round%2==0);
                let n=(128*1024*1024/len).max(32);
                let t=Instant::now();
                let mut sink=0u32;
                for _ in 0..n {
                    sink ^= if optimized {retail_ipak_crc::crc32(black_box(&input))}
                                    else {baseline(black_box(&input))};
                }
                black_box(sink);
                rates[usize::from(optimized)]=(len*n) as f64/t.elapsed().as_secs_f64()/(1024.0*1024.0);
            }
            measurements.push(rates);
        }
        let ratio:Vec<f64>=measurements.iter().map(|r|r[1]/r[0]).collect();
        let mut sorted=ratio.clone();
        sorted.sort_by(|a,b|a.total_cmp(b));
        let median=sorted[sorted.len()/2];
        println!("IPAK_CRC_BENCH size={} rounds=7 paired_median_speedup={:.4}x baseline_mib_s={:.2} optimized_mib_s={:.2}",
                 len,median,
                 measurements.iter().map(|r|r[0]).sum::<f64>()/7.0,
                 measurements.iter().map(|r|r[1]).sum::<f64>()/7.0);
        speedups.push(median);
    }
    assert!(speedups.iter().all(|x|x.is_finite()&&*x>0.0));
}
