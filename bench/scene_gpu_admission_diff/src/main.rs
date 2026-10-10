use std::{hint::black_box,time::Instant};
use bytemuck::{cast_slice,cast_slice_mut};
mod real_source;
use real_source::{changed_byte_range,commit_uploaded_bytes};
fn prepare_before_admission(source:&[u32],last:&[u32])->real_source::StreamChange{
 changed_byte_range(source,last)
}
fn verify(){
 for size in [0,1,32,63,64,255,256,257,1024,30000]{
 let mut old=vec![0u32;size];
 let mut new=old.clone();
 for attempt in 0..30usize{
  let mut source=(0..size).map(|v|v as u32 ^ attempt as u32).collect::<Vec<_>>();
  if size>0{source[attempt%size]^=127;}
  let diff=prepare_before_admission(&source,&old);
  if attempt%5==4{
   let late=changed_byte_range(&source,&new);
   assert_eq!(diff,late);
   commit_uploaded_bytes(&source,&mut old,&diff);
   commit_uploaded_bytes(&source,&mut new,&late);
   assert_eq!(cast_slice::<u32,u8>(&old),cast_slice::<u32,u8>(&new));
  }
 }
 }
 println!("PASS exact late-vs-eager dirty byte ranges and committed scene bytes for varied lengths, changing and dropped frames");
}
fn bench(size:usize,admit_every:usize){
 let mut source=(0..size).map(|i|i as u32*37).collect::<Vec<_>>();
 let rounds=350usize;
 let old=||{
  let mut uploaded=source.clone();let t=Instant::now();
  for attempt in 0..rounds {
   let idx=(attempt*41)%size;
   source[idx]^=attempt as u32 + 97;
   let change=changed_byte_range(black_box(&source),black_box(&uploaded));
   if attempt%admit_every==admit_every-1 {commit_uploaded_bytes(&source,&mut uploaded,&change);}
  }
  black_box(uploaded);t.elapsed().as_secs_f64()
 };
 let new=||{
  let mut uploaded=source.clone();let t=Instant::now();
  for attempt in 0..rounds {
   let idx=(attempt*41)%size;
   source[idx]^=attempt as u32 + 97;
   if attempt%admit_every==admit_every-1 {
    let change=changed_byte_range(black_box(&source),black_box(&uploaded));
    commit_uploaded_bytes(&source,&mut uploaded,&change);
   }
  }
  black_box(uploaded);t.elapsed().as_secs_f64()
 };
 let (mut a,mut b)=(Vec::new(),Vec::new());
 for round in 0..7{if round%2==0{a.push(old());b.push(new());}else{b.push(new());a.push(old());}}
 a.sort_by(f64::total_cmp);b.sort_by(f64::total_cmp);
 println!("instance_buffer_u32={size} admit_one_of={admit_every} old_prepare_ms={:.3} deferred_ms={:.3} speedup={:.2}x",a[3]*1000.,b[3]*1000.,a[3]/b[3]);
}
fn main(){verify();for size in [16384usize,131072] {for admit in [1usize,2,5,10]{bench(size,admit);}}}
