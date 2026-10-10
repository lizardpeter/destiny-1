use std::{hint::black_box,io::{Read,Write,Cursor},time::Instant};
use flate2::{Compression,bufread::DeflateDecoder,write::DeflateEncoder};
fn make(len:usize,variant:usize)->Vec<u8>{
 let mut seed=0xcafe_ab5eu32;
 let bytes=(0..len).map(|i|{
  seed^=seed<<13;seed^=seed>>17;seed^=seed<<5;
  match variant {0=>0,1=>(i%17) as u8,_=>seed as u8}
 }).collect::<Vec<_>>();
 let mut encoder=DeflateEncoder::new(Vec::new(),Compression::new(6));
 encoder.write_all(&bytes).unwrap();encoder.finish().unwrap()
}
fn old_decode(records:&[Vec<u8>])->Result<Vec<u8>,String>{
 let mut expanded=Vec::new();
 for compressed in records{
  let mut decoder=DeflateDecoder::new(compressed.as_slice());
  decoder.read_to_end(&mut expanded).map_err(|e|e.to_string())?;
 }
 Ok(expanded)
}
fn reuse_decode(records:&[Vec<u8>])->Result<Vec<u8>,String>{
 let mut expanded=Vec::new();
 let mut decoder=DeflateDecoder::new(Cursor::new(Vec::<u8>::new()));
 for compressed in records{
  // Large incompressible records regress on Linux with owned-Cursor
  // decompressor reuse; keep the proven baseline above this byte limit.
  if compressed.len()>4096 {
   let mut fallback=DeflateDecoder::new(compressed.as_slice());
   fallback.read_to_end(&mut expanded).map_err(|e|e.to_string())?;
   continue;
  }
  let mut reused=decoder.reset(Cursor::new(Vec::new())).into_inner();
  reused.clear();reused.extend_from_slice(compressed);
  decoder.reset(Cursor::new(reused));
  decoder.read_to_end(&mut expanded).map_err(|e|e.to_string())?;
  black_box(decoder.get_ref().get_ref().len());
 }
 Ok(expanded)
}
fn verify(){
 for n in [0usize,1,64,255,512,4096,16384,32768]{
  for variant in [0,1,2]{
   let compressed=make(n,variant);
   let records=vec![compressed.clone();4];
   assert_eq!(old_decode(&records),reuse_decode(&records),"valid n={n} var={variant}");
   for trim in [1,2,3] {
    if compressed.len()<=trim {continue}
    let invalid=vec![compressed[..compressed.len()-trim].to_vec()];
    let a=old_decode(&invalid);let b=reuse_decode(&invalid);
    assert_eq!(a.is_ok(),b.is_ok(),"truncated n={n} var={variant} trim={trim}");
    if let (Ok(a),Ok(b))=(a,b){assert_eq!(a,b)}
   }
   let mut corrupt=compressed.clone();if !corrupt.is_empty(){corrupt[0]^=255;}
   let a=old_decode(&[corrupt.clone()]);let b=reuse_decode(&[corrupt]);
   assert_eq!(a.is_ok(),b.is_ok(),"corrupt n={n} var={variant}");
   if let (Ok(a),Ok(b))=(a,b){assert_eq!(a,b)}
  }
 }
 println!("PASS: 24 payloads, byte parity, truncated and corrupt DEFLATE statuses");
}
fn bench(){
 for n in [64usize,1024,4096,32768]{
  for variant in [0usize,1,2] {
   let compressed=make(n,variant);
   let count=if n>=32768{128}else if n>=4096{512}else{2048};
   let records=vec![compressed;count];
   let old=||{let now=Instant::now();black_box(old_decode(black_box(&records)).unwrap());now.elapsed().as_secs_f64()};
   let new=||{let now=Instant::now();black_box(reuse_decode(black_box(&records)).unwrap());now.elapsed().as_secs_f64()};
   let (mut olds,mut news)=(Vec::new(),Vec::new());
   for round in 0..11{
    let (a,b)=if round%2==0{(old(),new())}else{let b=new();(old(),b)};
    olds.push(a);news.push(b);
   }
   olds.sort_by(f64::total_cmp);news.sort_by(f64::total_cmp);
   println!("bytes={n} variant={variant} records={count} compressed={} old_ms={:.3} reuse_ms={:.3} ratio={:.3}x",records[0].len(),olds[5]*1000.,news[5]*1000.,olds[5]/news[5]);
  }
 }
}
fn main(){verify();bench()}
