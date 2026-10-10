use std::{hint::black_box,time::Instant};
mod baseline;
mod optimized;
fn parity(runs:usize,width:usize) {
 let old=baseline::BenchmarkGrid::new(runs,width);
 let new=optimized::BenchmarkGrid::new(runs,width);
 for col in 0..(runs*width+3) {
  if col<=u16::MAX as usize {
   assert_eq!(old.locate(col as u16),new.locate(col as u16),"runs={runs} width={width} col={col}");
  }
 }
}
fn bench(runs:usize,width:usize,pattern:u8) {
 let a=baseline::BenchmarkGrid::new(runs,width);
 let b=optimized::BenchmarkGrid::new(runs,width);
 let cols=runs*width;
 let requests=if runs>128{250_000usize}else{500_000usize};
 let queries=(0..4096usize).map(|i|{
  let at=match pattern {
    0=>i%cols.min(width*4),
    1=>(i*701+263)%cols,
    2=>cols-1,
    _=>cols
  }; at as u16
 }).collect::<Vec<_>>();
 let original=||{
  let t=Instant::now();let mut checksum=0usize;
  for i in 0..requests {checksum^=a.locate(black_box(queries[i%queries.len()])).unwrap_or(777777);}
  black_box(checksum);t.elapsed().as_secs_f64()
 };
 let changed=||{
  let t=Instant::now();let mut checksum=0usize;
  for i in 0..requests {checksum^=b.locate(black_box(queries[i%queries.len()])).unwrap_or(777777);}
  black_box(checksum);t.elapsed().as_secs_f64()
 };
 let(mut before,mut after)=(Vec::new(),Vec::new());
 for round in 0..7{
  if round%2==0{before.push(original());after.push(changed());}
  else{after.push(changed());before.push(original());}
 }
 before.sort_by(f64::total_cmp);after.sort_by(f64::total_cmp);
 println!("runs={runs} width={width} pattern={pattern} queries={requests} old_ms={:.3} new_ms={:.3} speedup={:.3}x",
   before[3]*1000.,after[3]*1000.,before[3]/after[3]);
}
fn main(){
 for n in [1usize,2,4,16,31,32,33,64,128,512] {
  for w in [1usize,4] {parity(n,w);}
 }
 println!("PASS: source-exact BO2 light-grid RLE row validation and lookup parity");
 for n in [4usize,16,31,32,64,128,512] {
  for mode in [0u8,1,2]{bench(n,4,mode);}
 }
}
