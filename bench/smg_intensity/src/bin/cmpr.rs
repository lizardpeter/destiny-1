use smg_intensity_perf::{original, optimized};
use std::{hint::black_box, time::Instant};
fn make_image(width:usize,height:usize)->Vec<u8>{
    let mut src=vec![0; width.div_ceil(8)*height.div_ceil(8)*32];
    let mut state=0x9e37_79b9_u32;
    for b in &mut src {
        state ^= state << 13;
        state ^= state >> 17;
        state ^= state << 5;
        *b=state as u8;
    }
    src
}
fn main(){
    for (w,h) in [(256,256),(1024,1024),(257,259)]{
        let src=make_image(w,h);
        let a=original::decode_gx_texture_level(0x0e,0,None,&src,w,h).unwrap();
        let b=optimized::decode_gx_texture_level(0x0e,0,None,&src,w,h).unwrap();
        assert_eq!(a,b);
        let mut results=Vec::new();
        for round in 0..11 {
            let mut times=[0f64;2];
            for step in 0..2 {
                let fast=(step==0)==(round%2==0);
                let iter=if w>1023 {24} else {64};
                let start=Instant::now();
                for _ in 0..iter {
                    let out=if fast {optimized::decode_gx_texture_level(0x0e,0,None,black_box(&src),w,h).unwrap()}
                                     else {original::decode_gx_texture_level(0x0e,0,None,black_box(&src),w,h).unwrap()};
                    black_box(out);
                }
                times[usize::from(fast)]=(w*h*4*iter) as f64/(1024.0*1024.0)/start.elapsed().as_secs_f64();
            }
            results.push(times);
        }
        let mut ratios=results.iter().map(|r|r[1]/r[0]).collect::<Vec<_>>();
        ratios.sort_by(f64::total_cmp);
        println!("SMG_CMPR_BENCH dims={}x{} trials={} paired_median_ratio={:.4} baseline_avg_mib_s={:.2} optimized_avg_mib_s={:.2}",
            w,h,11,ratios[5],results.iter().map(|x|x[0]).sum::<f64>()/11.0,
            results.iter().map(|x|x[1]).sum::<f64>()/11.0);
    }
}