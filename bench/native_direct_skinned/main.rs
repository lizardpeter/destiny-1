use std::{hint::black_box,time::Instant};
mod source;
fn verify() {
 for n in [0usize,1,2,8,256]{
  for count in [0usize,1,2,17,32]{
   let input=source::fixture(n,count);
   let(mut a,mut b)=(source::Scratch::default(),source::Scratch::default());
   source::old_two_stage(&input,&mut a);
   source::new_direct(&input,&mut b);
   assert_eq!(a.final_draws,b.final_draws,"draws n={n} count={count}");
   assert_eq!(a.final_bones,b.final_bones,"bones n={n} count={count}");
  }
 }
 println!("PASS exact 256-byte draw and 48-byte bone records, remote/imported order and saturated palette offsets across 25 scene fixtures");
}
fn bench(draws_per_asset:usize,assets:usize){
 let input=source::fixture(draws_per_asset,assets);
 let mut old_scratch=source::Scratch::default();
 let mut new_scratch=source::Scratch::default();
 // Warm allocation/capacity: production vectors persist over many frames.
 source::old_two_stage(&input,&mut old_scratch);
 source::new_direct(&input,&mut new_scratch);
 let frames=if draws_per_asset*assets>10000 {150} else {400};
 let old=||{
  let start=Instant::now();
  for _ in 0..frames {source::old_two_stage(black_box(&input), &mut old_scratch); black_box(&old_scratch.final_draws);}
  start.elapsed().as_secs_f64()
 };
 let new=||{
  let start=Instant::now();
  for _ in 0..frames {source::new_direct(black_box(&input), &mut new_scratch); black_box(&new_scratch.final_draws);}
  start.elapsed().as_secs_f64()
 };
 let (mut a,mut b)=(Vec::new(),Vec::new());
 for i in 0..7{if i%2==0{a.push(old());b.push(new());}else{b.push(new());a.push(old());}}
 a.sort_by(f64::total_cmp);b.sort_by(f64::total_cmp);
 println!("mesh_instances={} bones={} frames={} old_ms={:.3} direct_ms={:.3} speedup={:.3}x",
 draws_per_asset*assets,32*assets,frames,a[3]*1000.,b[3]*1000.,a[3]/b[3]);
}
fn main(){verify();for (d,a) in [(1usize,1usize),(8,64),(64,64),(128,128),(256,128)]{bench(d,a);}}
