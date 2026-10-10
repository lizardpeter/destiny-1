use std::{hint::black_box,time::Instant};
mod baseline;mod optimized;
fn raw_input(len:usize,pattern:u8)->Vec<u8>{
 let mut rng=0x83abc412u32;
 (0..len).map(|i|{
   rng^=rng<<13;rng^=rng>>17;rng^=rng<<5;
   match pattern{
    0=>(rng%256)as u8,
    1=>(rng%9)as u8,
    2=>if i%13==0{200}else{0},
    _=>255
   }
 }).collect()
}
fn check(){
 for code in 0..=255u8{
  let mut base=[0u8;1];let mut next=[0u8;1];
  baseline::convert(&[code],&mut base);
  optimized::convert(&[code],&mut next);
  assert_eq!(base,next,"source gamma mismatch at {code}");
  assert_eq!(next[0],optimized::get_single(code));
 }
 for len in [0usize,1,32,255,256,257,1024,65536]{
  for pattern in 0..4{
   let data=raw_input(len,pattern);
   let mut old=vec![0;len];let mut new=vec![0;len];
   baseline::convert(&data,&mut old);optimized::convert(&data,&mut new);
   assert_eq!(old,new,"length={len},pattern={pattern}");
  }
 }
 println!("PASS: 256-byte exhaustive f32 sRGB parity and 32 varying-image conversions");
}
fn bench(len:usize,pattern:u8){
 let input=raw_input(len,pattern);
 let repeats=if len<=1024{1200}else if len<=16384{100}else{8};
 let run_old=||{
  let mut output=vec![0u8;len];
  let t=Instant::now();let mut sum=0usize;
  for _ in 0..repeats{baseline::convert(black_box(&input),black_box(&mut output));sum+=output[0]as usize;}
  black_box(sum);t.elapsed().as_secs_f64()
 };
 let run_new=||{
  let mut output=vec![0u8;len];
  let t=Instant::now();let mut sum=0usize;
  for _ in 0..repeats{optimized::convert(black_box(&input),black_box(&mut output));sum+=output[0]as usize;}
  black_box(sum);t.elapsed().as_secs_f64()
 };
 let(mut a,mut b)=(Vec::new(),Vec::new());
 for k in 0..9{
  if k%2==0{a.push(run_old());b.push(run_new());}
  else{b.push(run_new());a.push(run_old());}
 }
 a.sort_by(f64::total_cmp);b.sort_by(f64::total_cmp);
 println!("emissive_bytes={len} pattern={pattern} repeats={repeats} old_ms={:.3} lut_ms={:.3} speedup={:.2}x",
  a[4]*1000.,b[4]*1000.,a[4]/b[4]);
}
fn main(){check();for n in [32usize,1024,16*1024,256*1024]{for pattern in [0u8,1,2]{bench(n,pattern);}}}
