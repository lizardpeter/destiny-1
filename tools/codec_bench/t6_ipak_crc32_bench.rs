//! Differential correctness and same-run native-CPU speed for T6 IPAK CRC29 verification.
#[path="t6_ipak_crc32_baseline.rs"]
mod baseline;
#[path="t6_ipak_crc32_fast.rs"]
mod optimized;
use std::hint::black_box;
use std::time::Instant;

fn main() {
    let mut seed=0x6349_b4e3u32;
    for n in [0usize,1,2,3,7,8,15,16,31,32,255,256,1024,32768,1048576] {
        let mut bytes=vec![0u8;n];
        for v in &mut bytes {
            seed ^= seed<<13;
            seed ^= seed>>17;
            seed ^= seed<<5;
            *v=seed as u8;
        }
        assert_eq!(baseline::crc32(&bytes),optimized::crc32(&bytes),"n={n}");
    }
    assert_eq!(optimized::crc32(b"123456789"),0xcbf4_3926);
    for n in 0..=2000usize {
        let bytes=vec![((n*13)^ (n>>3)) as u8;n];
        assert_eq!(baseline::crc32(&bytes),optimized::crc32(&bytes),"n={n}");
    }
    println!("CRC32_DIFFERENTIAL_PASS 2016 lengths including 1 MiB, standard IEEE check");

    for size in [32768usize,1048576] {
        let mut corpus=vec![0u8;size];
        for b in &mut corpus {
            seed ^= seed<<13;
            seed ^= seed>>17;
            seed ^= seed<<5;
            *b=seed as u8;
        }
        let mut scalar=Vec::new();
        let mut table=Vec::new();
        let count=if size>32768 {30} else {400};
        for round in 0..11 {
            for which in if round % 2==0 {[0,1]} else {[1,0]} {
                let begin=Instant::now();
                for _ in 0..count {
                    let result=if which==0 {
                        baseline::crc32(black_box(&corpus))
                    } else {
                        optimized::crc32(black_box(&corpus))
                    };
                    black_box(result);
                }
                let mib=(size*count) as f64/(1024.0*1024.0);
                let value=mib/begin.elapsed().as_secs_f64();
                if which==0 {scalar.push(value);}else{table.push(value);}
            }
        }
        scalar.sort_by(f64::total_cmp);
        table.sort_by(f64::total_cmp);
        let a=scalar[scalar.len()/2];
        let b=table[table.len()/2];
        println!("CRC32_BENCH size={} scalar_mib_s={:.3} table_mib_s={:.3} ratio={:.4}",size,a,b,b/a);
    }
}
