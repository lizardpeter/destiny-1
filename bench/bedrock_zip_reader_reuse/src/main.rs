use std::{hint::black_box,io::{Cursor,Read,Write},time::Instant};
use zip::{ZipArchive,ZipWriter,CompressionMethod,write::SimpleFileOptions};
fn fixture(count:usize,len:usize)->Vec<u8>{
 let mut w=ZipWriter::new(Cursor::new(Vec::new()));
 let opts=SimpleFileOptions::default().compression_method(CompressionMethod::Deflated);
 for i in 0..count {
  w.start_file(format!("textures/pack/file_{i:05}.png"),opts).unwrap();
  let mut bytes=vec![0;len];
  for (j,b) in bytes.iter_mut().enumerate(){*b=((i*17+j*13)&255) as u8;}
  w.write_all(&bytes).unwrap();
 }
 w.finish().unwrap().into_inner()
}
fn read_all_old(data:&[u8],count:usize)->u64{
 let mut digest=0u64;
 for i in 0..count {
  // Old TextureCatalog::read_resource_bytes constructs a fresh ZipArchive
  // from the same resource pack on every texture look-up.
  let mut zip=ZipArchive::new(Cursor::new(data)).unwrap();
  let name=format!("textures/pack/file_{i:05}.png");
  let mut entry=zip.by_name(&name).unwrap();
  let mut decoded=Vec::with_capacity(entry.size().min(262144) as usize);
  entry.read_to_end(&mut decoded).unwrap();
  digest=digest.wrapping_add(decoded.len() as u64).wrapping_add(decoded[0] as u64);
 }
 digest
}
fn read_all_reused(data:&[u8],count:usize)->u64{
 let mut zip=ZipArchive::new(Cursor::new(data)).unwrap();
 let mut digest=0u64;
 for i in 0..count {
  let name=format!("textures/pack/file_{i:05}.png");
  let mut entry=zip.by_name(&name).unwrap();
  let mut decoded=Vec::with_capacity(entry.size().min(262144) as usize);
  entry.read_to_end(&mut decoded).unwrap();
  digest=digest.wrapping_add(decoded.len() as u64).wrapping_add(decoded[0] as u64);
 }
 digest
}
fn main(){
 for count in [16usize,64,256,512]{
  for len in [512usize,4096]{
   let data=fixture(count,len);
   assert_eq!(read_all_old(&data,count),read_all_reused(&data,count));
   let repetitions=if count>=512 {5}else{9};
   let old=||{let now=Instant::now();black_box(read_all_old(black_box(&data),count));now.elapsed().as_secs_f64()};
   let new=||{let now=Instant::now();black_box(read_all_reused(black_box(&data),count));now.elapsed().as_secs_f64()};
   let (mut olds,mut news)=(Vec::new(),Vec::new());
   for round in 0..repetitions {let (a,b)=if round%2==0{(old(),new())}else{let b=new();(old(),b)};olds.push(a);news.push(b);}
   olds.sort_by(f64::total_cmp);news.sort_by(f64::total_cmp);
   println!("archive_entries={count} entry_bytes={len} archive_size={} old_ms={:.3} reused_ms={:.3} speedup={:.2}x",
     data.len(),olds[repetitions/2]*1000.,news[repetitions/2]*1000.,olds[repetitions/2]/news[repetitions/2]);
  }
 }
 println!("PASS: exact synthetic ZIP2.4 resource lookups with a reusable archive index");
}
