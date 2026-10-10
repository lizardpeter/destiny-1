use std::{hint::black_box,time::Instant};
mod baseline;
mod optimized;
fn placement(p:u32)->[f32;12]{
 let t=p as f32;
 [
  0.8+(t*0.0037).cos(),(t*0.009).sin()*0.23,0.1,(t*0.125).sin()*9.0,
  (t*0.01).cos()*0.1,1.1+(t*0.003).sin(),0.03,(t*0.07).cos()*13.0,
  0.05,(t*0.0021).cos()*0.18,1.3+(t*0.004).sin(),t*0.02
 ]
}
fn bounds(m:u32)->[f32;4]{
 let t=m as f32;
 [t*0.031-3.0,(t*0.08).cos()*6.0,(t*0.029).sin()*2.0,0.1+t*0.01]
}
fn check(){
 for p in 0..160u32{
  let tr=placement(p);
  let matrix=optimized::affine_rows_to_mat4(tr);
  let scale=optimized::world_motion_radius_scale(matrix);
  for m in 0..64{
   let bound=bounds(m);
   let lhs=baseline::world_motion_bounds(tr,bound);
   let rhs=optimized::world_motion_bounds_prepared(matrix,scale,bound);
   for i in 0..4{assert_eq!(lhs[i].to_bits(),rhs[i].to_bits(),"placement={p},mesh={m},i={i}");}
  }
 }
 println!("PASS: 10,240 exact world-bound sphere outputs; camera translation, nonuniform scale and shear");
}
fn bench(meshes:usize,placements:usize){
 let placements=(0..placements as u32).map(placement).collect::<Vec<_>>();
 let mesh_bounds=(0..meshes as u32).map(bounds).collect::<Vec<_>>();
 let loops=if placements.len()*meshes>10000{30}else{150};
 let old=||{
  let started=Instant::now();let mut sum=0.0;
  for _ in 0..loops{for transform in &placements{for bound in &mesh_bounds {
   let result=baseline::world_motion_bounds(black_box(*transform),black_box(*bound));
   sum+=result[3];}}}
  black_box(sum);started.elapsed().as_secs_f64()
 };
 let new=||{
  let started=Instant::now();let mut sum=0.0;
  for _ in 0..loops{for transform in &placements{
   let matrix=optimized::affine_rows_to_mat4(black_box(*transform));
   let radius=optimized::world_motion_radius_scale(matrix);
   for bound in &mesh_bounds{
    let result=optimized::world_motion_bounds_prepared(matrix,radius,black_box(*bound));
    sum+=result[3];
   }}}
  black_box(sum);started.elapsed().as_secs_f64()
 };
 let(mut a,mut b)=(Vec::new(),Vec::new());
 for i in 0..7{if i%2==0{a.push(old());b.push(new());}else{b.push(new());a.push(old());}}
 a.sort_by(f64::total_cmp);b.sort_by(f64::total_cmp);
 println!("mesh_segments={meshes} placements={} loops={} before_ms={:.3} reused_ms={:.3} speedup={:.3}x",
  placements.len(),loops,a[3]*1000.,b[3]*1000.,a[3]/b[3]);
}
fn main(){check();for meshes in [1usize,2,8,32,64]{bench(meshes,256);}}
