use std::{hint::black_box,time::Instant};
use lzxd::{Lzxd,WindowSize};
use lzxd_fast::{Lzxd as FastLzxd,WindowSize as FastWindowSize};
use xbox_lzx_reset_bench::{seeded_payload,uncompressed_frame};
fn main(){
    for (len,reps) in [(3usize,4000usize),(256,2400),(4096,1000),(32768,240)] {
        let frame=uncompressed_frame(&seeded_payload(len,len as u32 + 99));
        let mut fork=FastLzxd::new(FastWindowSize::KB32);
        for _ in 0..20{
            let a=Lzxd::new(WindowSize::KB32).decompress_next(&frame,len).unwrap().to_vec();
            fork.reset_reuse();
            assert_eq!(a,fork.decompress_next(&frame,len).unwrap());
        }
        let mut ratios=Vec::new();
        let mut baseline_mibps=Vec::new();
        let mut candidate_mibps=Vec::new();
        for round in 0..11 {
            let mut sec=[0.0f64;2];
            for phase in 0..2 {
                let fast=(phase==0)==(round%2==0);
                let now=Instant::now();
                if fast {
                    let mut decoder=FastLzxd::new(FastWindowSize::KB32);
                    for _ in 0..reps {
                        decoder.reset_reuse();
                        black_box(decoder.decompress_next(black_box(&frame),len).unwrap());
                    }
                } else {
                    for _ in 0..reps {
                        let mut decoder=Lzxd::new(WindowSize::KB32);
                        black_box(decoder.decompress_next(black_box(&frame),len).unwrap());
                    }
                }
                sec[usize::from(fast)]=now.elapsed().as_secs_f64();
            }
            let mib=(len*reps)as f64/1048576.0;
            ratios.push(sec[0]/sec[1]);
            baseline_mibps.push(mib/sec[0]);
            candidate_mibps.push(mib/sec[1]);
        }
        ratios.sort_by(f64::total_cmp);
        println!("XBOX_LZX_RESET_BENCH size={len} records={reps} ratio={:.4}x original_mib_s={:.2} reset_reuse_mib_s={:.2}",
           ratios[5],baseline_mibps.iter().sum::<f64>()/11.0,candidate_mibps.iter().sum::<f64>()/11.0);
    }
}
