use smg_palette_perf::{original,optimized};
use std::{hint::black_box,time::Instant};
fn input(format:u8,palette_format:u8,w:usize,h:usize)->(Vec<u8>,Vec<u8>) {
    let (bw,bh,entries) = match format {
        0x08 => (8usize,8usize,16usize),
        0x09 => (8,4,256),
        _ => (4,4,16384)
    };
    let mut seed=0x185b_1353_u32;
    let mut rng=||{seed^=seed<<13; seed^=seed>>17; seed^=seed<<5; seed as u8};
    let mut colors=vec![0u8;entries*2];
    for v in &mut colors {*v=rng();}
    let mut data=vec![0u8;w.div_ceil(bw)*h.div_ceil(bh)*32];
    for v in &mut data {*v=rng();}
    if format==0x0a {
       // Ensure every C14 14-bit index is valid for a 16k palette, including
       // the two unused high bits in the packed GX source.
       for pair in data.chunks_exact_mut(2) {
          let index=u16::from_be_bytes([pair[0],pair[1]]) & 0x3fff;
          let n=index.to_be_bytes();
          pair.copy_from_slice(&n);
       }
    }
    black_box(palette_format);
    (data,colors)
}
fn main() {
    for format in [0x08u8,0x09,0x0a] {
        for pf in [0u8,1,2] {
            for (w,h) in [(256usize,256usize),(1024,1024),(257,259)] {
                let (data,palette)=input(format,pf,w,h);
                let prior=original::decode_gx_texture_level(format,pf,Some(&palette),&data,w,h).unwrap();
                let next=optimized::decode_gx_texture_level(format,pf,Some(&palette),&data,w,h).unwrap();
                assert_eq!(prior,next,"preflight format={format:#04x} pf={pf} {w}x{h}");
                let reps=if w>1023 {12} else {32};
                let mut ratios=Vec::new();
                for round in 0..9 {
                    let mut seconds=[0.0f64;2];
                    for step in 0..2 {
                        let fast=(step==0)==(round%2==0);
                        let start=Instant::now();
                        for _ in 0..reps {
                            let out=if fast {
                                optimized::decode_gx_texture_level(format,pf,Some(black_box(&palette)),black_box(&data),w,h).unwrap()
                            } else {
                                original::decode_gx_texture_level(format,pf,Some(black_box(&palette)),black_box(&data),w,h).unwrap()
                            };
                            black_box(out);
                        }
                        seconds[usize::from(fast)]=start.elapsed().as_secs_f64();
                    }
                    ratios.push(seconds[0]/seconds[1]);
                }
                ratios.sort_by(f64::total_cmp);
                println!("SMG_PALETTE_BENCH format={format:#04x} palette_format={pf} dims={w}x{h} median_ratio={:.4}x",ratios[4]);
            }
        }
    }
}
