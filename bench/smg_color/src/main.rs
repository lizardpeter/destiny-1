use smg_color_perf::{original,optimized};
use std::{hint::black_box,time::Instant};
fn image(format:u8,w:usize,h:usize)->Vec<u8> {
    let (bw,bh,block_size)=if format==0x02 {(8,4,32)} else if format==0x06 {(4,4,64)} else {(4,4,32)};
    let mut data=vec![0u8;w.div_ceil(bw)*h.div_ceil(bh)*block_size];
    let mut seed=0xf1ec_1729_u32;
    for b in &mut data {seed^=seed<<13;seed^=seed>>17;seed^=seed<<5;*b=seed as u8;}
    data
}
fn main(){
    for format in [0x02u8,0x03,0x04,0x05,0x06] {
        for (w,h) in [(256,256),(1024,1024),(257,259)] {
            let source=image(format,w,h);
            let prev=original::decode_gx_texture_level(format,0,None,&source,w,h).unwrap();
            let next=optimized::decode_gx_texture_level(format,0,None,&source,w,h).unwrap();
            assert_eq!(prev,next,"benchmark preflight {format:#04x} {w}x{h}");
            for _ in 0..2 {
                black_box(original::decode_gx_texture_level(format,0,None,black_box(&source),w,h).unwrap());
                black_box(optimized::decode_gx_texture_level(format,0,None,black_box(&source),w,h).unwrap());
            }
            let reps=if w>1023{16}else{48};
            let mut ratios=Vec::new();
            let mut old_mibs=Vec::new();
            let mut new_mibs=Vec::new();
            for round in 0..9 {
                let mut seconds=[0.0f64;2];
                for step in 0..2 {
                    let do_new=(step==0)==(round%2==0);
                    let start=Instant::now();
                    for _ in 0..reps {
                        let v=if do_new {
                            optimized::decode_gx_texture_level(format,0,None,black_box(&source),w,h).unwrap()
                        } else {
                            original::decode_gx_texture_level(format,0,None,black_box(&source),w,h).unwrap()
                        };
                        black_box(v);
                    }
                    seconds[usize::from(do_new)]=start.elapsed().as_secs_f64();
                }
                ratios.push(seconds[0]/seconds[1]);
                old_mibs.push(w as f64*h as f64*4.0*reps as f64/1048576.0/seconds[0]);
                new_mibs.push(w as f64*h as f64*4.0*reps as f64/1048576.0/seconds[1]);
            }
            ratios.sort_by(f64::total_cmp);
            println!("SMG_COLOR_ROW format={format:#04x} dimensions={w}x{h} median_speedup={:.4}x previous_mib_s={:.1} candidate_mib_s={:.1}",
                ratios[4],old_mibs.iter().sum::<f64>()/9.0,new_mibs.iter().sum::<f64>()/9.0);
        }
    }
}
