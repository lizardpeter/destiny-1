use smg_intensity_perf::{original,optimized};
use std::{hint::black_box,time::Instant};
fn image(width:usize,height:usize,format:u8)->Vec<u8>{
    let block_h=if format==0x00{8}else{4};
    let mut source=vec![0u8;width.div_ceil(8)*height.div_ceil(block_h)*32];
    let mut seed=0x12345678u32;
    for b in &mut source {seed ^= seed<<13;seed ^= seed>>17;seed ^= seed<<5;*b=seed as u8;}
    source
}
fn main(){
    for format in [0x00u8,0x01u8] {
        for (w,h) in [(256,256),(1024,1024),(257,259)] {
            let compressed=image(w,h,format);
            let prior=original::decode_gx_texture_level(format,0,None,&compressed,w,h).unwrap();
            let next=optimized::decode_gx_texture_level(format,0,None,&compressed,w,h).unwrap();
            assert_eq!(prior,next);
            let mut pairs=Vec::new();
            for round in 0..11 {
                let mut rates=[0f64;2];
                for step in 0..2 {
                    let fast=(step==0)==(round%2==0);
                    let reps=if w>1023{24}else{64};
                    let t=Instant::now();
                    for _ in 0..reps {
                        let output=if fast {
                            optimized::decode_gx_texture_level(format,0,None,black_box(&compressed),w,h).unwrap()
                        } else {
                            original::decode_gx_texture_level(format,0,None,black_box(&compressed),w,h).unwrap()
                        };
                        black_box(output);
                    }
                    rates[usize::from(fast)]=(w*h*4*reps)as f64/(1024.0*1024.0)/t.elapsed().as_secs_f64();
                }
                pairs.push(rates);
            }
            let mut ratio=pairs.iter().map(|r|r[1]/r[0]).collect::<Vec<_>>();
            ratio.sort_by(f64::total_cmp);
            println!("SMG_INTENSITY_BENCH format={format:#04x} dims={w}x{h} rounds=11 paired_median_ratio={:.4} baseline_avg_mib_s={:.2} optimized_avg_mib_s={:.2}",
                ratio[5],
                pairs.iter().map(|r|r[0]).sum::<f64>()/11.0,
                pairs.iter().map(|r|r[1]).sum::<f64>()/11.0);
        }
    }
}