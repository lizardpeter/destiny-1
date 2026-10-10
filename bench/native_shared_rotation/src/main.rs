use std::{hint::black_box,time::Instant};
use glam::{Mat4,Vec3};
mod source;
fn matrices()->Vec<[[f32;4];4]> {
 (0..1024).map(|i|{
  let t=i as f32;
  let eye=Vec3::new(t*0.000031+1.0,(t*0.031).sin()*20.0, (t*0.075).cos()*12.0+40.0);
  let view=Mat4::look_at_rh(eye,eye+Vec3::new(-1.0,-0.1,-0.31),Vec3::Y);
  (Mat4::perspective_rh(1.07,16.0/9.0,0.12,4_000.0)*view).to_cols_array_2d()
 }).collect()
}
fn parity(xs:&[[[f32;4];4]]){
 for x in xs{
  let before=[source::world_to_view_rotation(*x),source::world_to_view_rotation(*x)];
  let basis=source::world_to_view_rotation(*x);
  let after=[basis,basis];
  for j in 0..2 {for k in 0..3 {for l in 0..4 {
   assert_eq!(before[j][k][l].to_bits(),after[j][k][l].to_bits());
  }}}
 }
 println!("PASS: 1024 camera transforms, bitwise shared-basis parity across both GPU frame consumers");
}
fn time_one(xs:&[[[f32;4];4]],iters:usize)->(f64,f64){
 let original=||{
  let start=Instant::now();let mut checksum=0f32;
  for i in 0..iters{
   let v=*black_box(&xs[i%xs.len()]);
   let first=source::world_to_view_rotation(black_box(v));
   let second=source::world_to_view_rotation(black_box(v));
   checksum+=black_box(first[0][0]+second[1][1]);
  }
  black_box(checksum);
  start.elapsed().as_secs_f64()
 };
 let optimized=||{
  let start=Instant::now();let mut checksum=0f32;
  for i in 0..iters{
   let v=*black_box(&xs[i%xs.len()]);
   let basis=source::world_to_view_rotation(black_box(v));
   checksum+=black_box(basis[0][0]+basis[1][1]);
  }
  black_box(checksum);
  start.elapsed().as_secs_f64()
 };
 let(mut before,mut after)=(Vec::new(),Vec::new());
 for r in 0..9{
   if r%2==0{before.push(original());after.push(optimized());}
   else{after.push(optimized());before.push(original());}
 }
 before.sort_by(f64::total_cmp);after.sort_by(f64::total_cmp);
 (before[4],after[4])
}
fn main(){
 let xs=matrices();parity(&xs);
 for samples in [5000usize,50_000]{
 let (old,new)=time_one(&xs,samples);
 println!("camera_views={samples} two_consumer_old_ms={:.3} one_shared_basis_ms={:.3} speedup={:.3}x",old*1000.0,new*1000.0,old/new);
 }
}