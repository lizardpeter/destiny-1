use std::{
 fs::{self,File},io::{Read,Seek,SeekFrom,Write},path::{Path,PathBuf},
 sync::{Arc,Mutex},time::Instant,hint::black_box
};
#[cfg(windows)] use std::sync::atomic::{AtomicUsize,Ordering};
const PAYLOAD:usize=32*1024*1024;
struct Index{
 path:PathBuf, payload_start:u64, len:u64,
 #[cfg(unix)] file:File,
 #[cfg(windows)] files:Vec<Mutex<File>>,
 #[cfg(windows)] next:AtomicUsize,
}
impl Index{
 fn new(path:&Path)->Self{
  let retained=File::open(path).unwrap();
  let mut tar=tar::Archive::new(File::open(path).unwrap());
  let mut members=tar.entries_with_seek().unwrap();
  let e=members.next().unwrap().unwrap();
  let start=e.raw_file_position();let len=e.size();
  drop(e); drop(members);drop(tar);
  #[cfg(windows)] let files={
   let mut files=vec![Mutex::new(retained)];
   for _ in 1..4{if let Ok(file)=File::open(path){files.push(Mutex::new(file))}}
   files
  };
  Self{path:path.to_path_buf(),payload_start:start,len,
    #[cfg(unix)] file:retained,
    #[cfg(windows)] files,
    #[cfg(windows)] next:AtomicUsize::new(0),
  }
 }
 fn valid(&self,offset:u64,n:usize)->Result<u64,String>{
   let end=offset.checked_add(n as u64).ok_or("overflow")?;
   if end>self.len{return Err("out of range".into())}
   self.payload_start.checked_add(offset).ok_or("overflow".into())
 }
 fn original(&self,offset:u64,n:usize)->Result<Vec<u8>,String>{
  let absolute=self.valid(offset,n)?;
  let mut file=File::open(&self.path).map_err(|e|e.to_string())?;
  file.seek(SeekFrom::Start(absolute)).map_err(|e|e.to_string())?;
  let mut bytes=vec![0;n];
  file.read_exact(&mut bytes).map_err(|e|e.to_string())?;
  Ok(bytes)
 }
 fn retained(&self,offset:u64,n:usize)->Result<Vec<u8>,String>{
  let absolute=self.valid(offset,n)?;
  let mut bytes=vec![0;n];
  #[cfg(unix)] {
   use std::os::unix::fs::FileExt;
   let mut consumed=0;
   while consumed<n{
    match self.file.read_at(&mut bytes[consumed..],absolute+consumed as u64){
     Ok(0)=>return Err("EOF".into()),
     Ok(k)=>consumed+=k,
     Err(e) if e.kind()==std::io::ErrorKind::Interrupted=>continue,
     Err(e)=>return Err(e.to_string()),
    }
   }
  }
  #[cfg(windows)] {
    let slot=self.next.fetch_add(1,Ordering::Relaxed)%self.files.len();
    let mut file=self.files[slot].lock().unwrap();
    file.seek(SeekFrom::Start(absolute)).map_err(|e|e.to_string())?;
    file.read_exact(&mut bytes).map_err(|e|e.to_string())?;
  }
  #[cfg(not(any(unix,windows)))]{
    let mut file=File::open(&self.path).map_err(|e|e.to_string())?;
    file.seek(SeekFrom::Start(absolute)).map_err(|e|e.to_string())?;
    file.read_exact(&mut bytes).map_err(|e|e.to_string())?;
  }
  Ok(bytes)
 }
}
fn make_tar(path:&Path){
 let f=File::create(path).unwrap();let mut t=tar::Builder::new(f);
 let mut seed=0x7872_3a3bu32;
 let mut payload=vec![0;PAYLOAD];
 for b in &mut payload{seed^=seed<<13;seed^=seed>>17;seed^=seed<<5;*b=seed as u8;}
 let mut hdr=tar::Header::new_gnu();hdr.set_size(PAYLOAD as u64);hdr.set_mode(0o644);hdr.set_cksum();
 t.append_data(&mut hdr,"packages/ps4_arch_cabal_005b_0.pkg.bin",&payload[..]).unwrap();
 t.finish().unwrap();
}
fn verify(index:&Arc<Index>){
 for n in [0usize,1,64,4096,32768,262144]{
  for offset in [0usize,17,4096,524287,PAYLOAD-n]{
   assert_eq!(index.original(offset as u64,n),index.retained(offset as u64,n));
  }
 }
 assert!(index.original((PAYLOAD-4)as u64,5).is_err());
 assert!(index.retained((PAYLOAD-4)as u64,5).is_err());
 std::thread::scope(|scope|{
  for tid in 0..16{let i=Arc::clone(index);
   scope.spawn(move||for iter in 0..100{
    let off=(tid*8191+iter*65537)%(PAYLOAD-32768);
    let new=i.retained(off as u64,32768).unwrap();
    assert_eq!(new,i.original(off as u64,32768).unwrap());
   });
  }
 });
 println!("PASS: TAR raw_file_position parity, exact bounds, 16 concurrent readers");
}
fn bench(i:&Arc<Index>){
 for workers in [1usize,4,16]{
  for n in [64usize,4096,32768,262144]{
   let iterations=if n>=262144{64}else{256};
   let measure=|use_new:bool|{
    let start=Instant::now();
    std::thread::scope(|scope|{
     for tid in 0..workers{
      let idx=Arc::clone(i);
      scope.spawn(move||{
       let mut digest=0u8;
       for k in 0..iterations{
        let at=((tid*38947+k*9901)%(PAYLOAD-n))as u64;
        let bytes=if use_new{idx.retained(at,n).unwrap()}else{idx.original(at,n).unwrap()};
        digest^=bytes[0];black_box(bytes);
       }
       black_box(digest);
      });
     }
    });
    start.elapsed().as_secs_f64()
   };
   let(mut originals,mut retained)=(Vec::new(),Vec::new());
   for turn in 0..7{
    let(a,b)=if turn%2==0{(measure(false),measure(true))}else{let b=measure(true);(measure(false),b)};
    originals.push(a);retained.push(b);
   }
   originals.sort_by(f64::total_cmp);retained.sort_by(f64::total_cmp);
   println!("workers={workers} bytes={n} requests={} old_ms={:.3} retained_ms={:.3} speedup={:.2}x",
    workers*iterations,originals[3]*1000.,retained[3]*1000.,originals[3]/retained[3]);
  }
 }
}
fn main(){
 let path=std::env::temp_dir().join(format!("d1_tiger_tar_{}_{}.tar",std::process::id(),std::env::consts::OS));
 make_tar(&path);
 {let index=Arc::new(Index::new(&path));assert_eq!(index.len,PAYLOAD as u64);verify(&index);bench(&index);}
 fs::remove_file(path).unwrap();
}
