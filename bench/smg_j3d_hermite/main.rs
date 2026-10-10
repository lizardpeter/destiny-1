use std::{hint::black_box,time::Instant};
mod baseline;
mod optimized;
fn check(n:usize,duplicate:bool){
 let old=baseline::BenchmarkTrack::new(n,duplicate);
 let new=optimized::BenchmarkTrack::new(n,duplicate);
 for i in -100..(n as i32 * 11+100){
  let frame=i as f32/10.0;
  assert_eq!(old.sample(frame).to_bits(),new.sample(frame).to_bits(),"n={n} duplicate={duplicate} frame={frame}");
 }
 for frame in [f32::INFINITY,f32::NEG_INFINITY,f32::NAN]{
  assert_eq!(old.sample(frame).to_bits(),new.sample(frame).to_bits(),"n={n} special={frame:?}");
 }
}
fn bench(n:usize,duplicate:bool,pattern:u8){
 let old=baseline::BenchmarkTrack::new(n,duplicate);
 let new=optimized::BenchmarkTrack::new(n,duplicate);
 let mut queries=Vec::with_capacity(4096);
 for k in 0..4096usize{
   let f=match pattern{
    0=>(k%60) as f32/4.0,
    1=>(k.wrapping_mul(13)%((n*10).max(10))) as f32 / 10.0,
    2=>(n as f32)+100.0,
    _=>0.0
   };
   queries.push(f);
 }
 let iter=if n>=512{75}else{150};
 let original=||{
  let t=Instant::now();let mut sum=0.0;
  for _ in 0..iter{for &frame in &queries{sum+=old.sample(black_box(frame));}}
  black_box(sum);t.elapsed().as_secs_f64()
 };
 let updated=||{
  let t=Instant::now();let mut sum=0.0;
  for _ in 0..iter{for &frame in &queries{sum+=new.sample(black_box(frame));}}
  black_box(sum);t.elapsed().as_secs_f64()
 };
 let(mut a,mut b)=(Vec::new(),Vec::new());
 for k in 0..7{
  if k%2==0{a.push(original());b.push(updated())}
  else{b.push(updated());a.push(original())}
 }
 a.sort_by(f64::total_cmp);b.sort_by(f64::total_cmp);
 println!("keys={n} duplicate={duplicate} pattern={pattern} samples={} old_ms={:.3} binary_ms={:.3} speedup={:.3}x",iter*4096,a[3]*1000.,b[3]*1000.,a[3]/b[3]);
}
fn main(){
 for n in [1usize,2,8,15,16,17,32,64,128,512]{
  check(n,false);check(n,true);
 }
 println!("PASS: bitwise Hermite interpolation equivalence, duplicate keys and NaN query");
 for n in [4usize,8,15,16,32,128,512]{
  for duplicate in [false,true]{
   for pattern in [0u8,1,2]{bench(n,duplicate,pattern);}
  }
 }
}
