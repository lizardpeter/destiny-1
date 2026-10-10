use std::mem::size_of;
#[repr(C)] #[derive(Clone,Copy,Debug,PartialEq,Eq)]
pub struct Draw {
 pub fixed:[u32;19],
 pub palette_offset:u32,
 pub data:[u32;44],
}
#[repr(C)] #[derive(Clone,Copy,Debug,PartialEq,Eq)]
pub struct Bone {pub data:[u32;12]}
#[derive(Clone)]
pub struct Asset {pub draws:Vec<Draw>,pub bones:Vec<Bone>}
pub struct Streams {
 pub remote_draws:Vec<Draw>,
 pub remote_bones:Vec<Bone>,
 pub assets:Vec<Asset>,
}
#[derive(Default)]
pub struct Scratch {pub local_draws:Vec<Draw>,pub local_bones:Vec<Bone>,pub final_draws:Vec<Draw>,pub final_bones:Vec<Bone>}
pub fn old_two_stage(src:&Streams,buf:&mut Scratch) {
 buf.local_draws.clear();buf.local_bones.clear();
 for asset in &src.assets{
  let palette_offset=buf.local_bones.len() as u32;
  for item in &asset.draws {
   let mut copy=*item;
   copy.palette_offset=copy.palette_offset.saturating_add(palette_offset);
   buf.local_draws.push(copy);
  }
  buf.local_bones.extend_from_slice(&asset.bones);
 }
 buf.final_draws.clear();buf.final_bones.clear();
 buf.final_draws.extend_from_slice(&src.remote_draws);
 buf.final_bones.extend_from_slice(&src.remote_bones);
 let bone_base=buf.final_bones.len() as u32;
 buf.final_bones.extend_from_slice(&buf.local_bones);
 let start=buf.final_draws.len();
 buf.final_draws.extend_from_slice(&buf.local_draws);
 for item in &mut buf.final_draws[start..] {
  item.palette_offset=item.palette_offset.saturating_add(bone_base);
 }
}
pub fn new_direct(src:&Streams,buf:&mut Scratch){
 buf.final_draws.clear();buf.final_bones.clear();
 buf.final_draws.extend_from_slice(&src.remote_draws);
 buf.final_bones.extend_from_slice(&src.remote_bones);
 let remote_bone_base=buf.final_bones.len() as u32;
 let mut imported_bone_count=0usize;
 for asset in &src.assets{
  let palette_offset=(imported_bone_count as u32).saturating_add(remote_bone_base);
  imported_bone_count+=asset.bones.len();
  buf.final_bones.extend_from_slice(&asset.bones);
  for item in &asset.draws{
   let mut copy=*item;
   copy.palette_offset=copy.palette_offset.saturating_add(palette_offset);
   buf.final_draws.push(copy);
  }
 }
}
pub fn fixture(segments_per_asset:usize,assets:usize)->Streams{
 let remote_draws=(0..8).map(|i|Draw{fixed:[i as u32;19],palette_offset:i as u32*10,data:[i as u32+31;44]}).collect();
 let remote_bones=(0..80).map(|i|Bone{data:[i as u32;12]}).collect();
 let assets=(0..assets).map(|a|{
  let draws=(0..segments_per_asset).map(|i|{
   let n=(a*segments_per_asset+i) as u32;
   Draw{fixed:[n;19],palette_offset:0,data:[n.wrapping_mul(47);44]}
  }).collect();
  let bones=(0..32).map(|j|Bone{data:[(a*32+j) as u32;12]}).collect();
  Asset{draws,bones}
 }).collect();
 assert_eq!(size_of::<Draw>(),256);
 assert_eq!(size_of::<Bone>(),48);
 Streams{remote_draws,remote_bones,assets}
}
