use std::{fs, hint::black_box, path::PathBuf, time::Instant, sync::atomic::{AtomicUsize, Ordering}};
extern crate self as d1_oodle3;
pub mod lzh { pub fn decode_stream(_: &[u8], _: usize) -> Result<Vec<u8>, String> {
    Err("synthetic Tiger benchmark does not include Oodle streams".into())
}}
pub mod sha1 {
    use sha1_external::{Digest,Sha1};
    pub fn digest(bytes:&[u8])->[u8;20] {
        let mut s=Sha1::new(); s.update(bytes);
        let out=s.finalize();let mut raw=[0u8;20];raw.copy_from_slice(&out);raw
    }
}
#[derive(Debug)]
pub enum Error{Invalid(String),Unsupported(String),IoContext(String,std::io::Error),Io(std::io::Error)}
pub type Result<T>=std::result::Result<T,Error>;
impl From<std::io::Error> for Error {
 fn from(e:std::io::Error)->Self{Self::Io(e)}
}
impl std::fmt::Display for Error {
 fn fmt(&self,f:&mut std::fmt::Formatter<'_>)->std::fmt::Result {
  match self{Self::Invalid(s)|Self::Unsupported(s)=>write!(f,"{s}"),
   Self::IoContext(s,e)=>write!(f,"{s}: {e}"),Self::Io(e)=>write!(f,"{e}")}
 }
}
impl std::error::Error for Error{}
mod baseline;
mod optimized;
const BLOCK:usize=optimized::LOGICAL_BLOCK_SIZE;
fn fixture(count:usize)->(PathBuf,Vec<[u8;20]>,Vec<u8>){
 let dir=std::env::temp_dir().join(format!("d1_seq_tiger_{}_{}",std::process::id(),std::env::consts::OS));
 let _=fs::create_dir_all(&dir);
 let path=dir.join("ps4_arch_cabal_005b_0.pkg.bin");
 let mut data=vec![0u8;BLOCK*count];let mut hashes=Vec::new();
 for (i,chunk) in data.chunks_exact_mut(BLOCK).enumerate(){
  let mut r=0x1234_5678u32.wrapping_add(i as u32*7907);
  for byte in chunk {r^=r<<13;r^=r>>17;r^=r<<5;*byte=r as u8;}
 }
 for chunk in data.chunks_exact(BLOCK){hashes.push(sha1::digest(chunk));}
 fs::write(&path,&data).unwrap();(path,hashes,data)
}
static TALLY:AtomicUsize=AtomicUsize::new(0);
fn correctness(path:&PathBuf, hashes:&[[u8;20]], original:&[u8], size:usize, off:usize, cache:bool){
 let a=baseline::synthetic_raw_package(path.clone(),hashes,off,size,cache);
 let b=optimized::synthetic_raw_package(path.clone(),hashes,off,size,cache);
 let lhs=a.read_entry(0,None).unwrap();
 let rhs=b.read_entry(0,None).unwrap();
 assert_eq!(lhs,rhs);
 assert_eq!(rhs,original[off..off+size]);
 TALLY.fetch_add(1,Ordering::Relaxed);
}
fn bench(path:&PathBuf, hashes:&[[u8;20]],size:usize,off:usize,cache:bool){
 let a=baseline::synthetic_raw_package(path.clone(),hashes,off,size,cache);
 let b=optimized::synthetic_raw_package(path.clone(),hashes,off,size,cache);
 let iterations=if size>12*BLOCK{12}else if size>4*BLOCK{25}else{60};
 let run_old=||{let t=Instant::now();let mut checksum=0u8;
  for _ in 0..iterations{let v=a.read_entry(0,None).unwrap();checksum^=v[0];black_box(v);}
  black_box(checksum);t.elapsed().as_secs_f64()};
 let run_new=||{let t=Instant::now();let mut checksum=0u8;
  for _ in 0..iterations{let v=b.read_entry(0,None).unwrap();checksum^=v[0];black_box(v);}
  black_box(checksum);t.elapsed().as_secs_f64()};
 let(mut old,mut new)=(Vec::new(),Vec::new());
 for k in 0..5{if k%2==0{old.push(run_old());new.push(run_new());}
  else{new.push(run_new());old.push(run_old());}}
 old.sort_by(f64::total_cmp);new.sort_by(f64::total_cmp);
 println!("blocks={} offset={} cache={} iterations={} old_ms={:.3} streaming_ms={:.3} speedup={:.3}x", 
   (size+off+BLOCK-1)/BLOCK,off,cache,iterations,old[2]*1000.,new[2]*1000.,old[2]/new[2]);
}
fn main(){
 let (path,hashes,data)=fixture(48);
 for &(off,size) in &[(0,1),(0,BLOCK),(BLOCK-1,2),(63,2*BLOCK-63),
   (BLOCK-2048,7*BLOCK),(0,16*BLOCK),(509,32*BLOCK-509)]{
  for cache in [false,true]{correctness(&path,&hashes,&data,size,off,cache);}
 }
 let(mut bad_hashes)=hashes.clone();bad_hashes[0][5]^=0xFF;
 let a=baseline::synthetic_raw_package(path.clone(),&bad_hashes,0,BLOCK,false);
 let b=optimized::synthetic_raw_package(path.clone(),&bad_hashes,0,BLOCK,false);
 assert!(a.read_entry(0,None).is_err()&&b.read_entry(0,None).is_err());
 println!("PASS: {} exact source entry reconstructions, boundary offsets, cache + invalid SHA-1",TALLY.load(Ordering::Relaxed));
 for &(off,size) in &[(0,BLOCK),(63,4*BLOCK-63),(0,16*BLOCK),(509,32*BLOCK-509)] {
  for cache in [false,true]{bench(&path,&hashes,size,off,cache);}
 }
 fs::remove_file(&path).unwrap();fs::remove_dir(path.parent().unwrap()).unwrap();
}
