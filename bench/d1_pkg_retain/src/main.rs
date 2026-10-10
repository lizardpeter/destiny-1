use std::{collections::HashMap,fs::{self,File},hint::black_box,
io::{Read,Seek,SeekFrom},path::{Path,PathBuf},sync::{Arc,Mutex},time::Instant};
#[cfg(windows)] use std::sync::atomic::{AtomicUsize,Ordering};
const MAX_RETAINED_PACKAGE_FILES:usize=8;
const BYTES_PER_PATCH:usize=4*1024*1024;

struct Reader{
 #[cfg(unix)] file:File,
 #[cfg(windows)] files:Vec<Mutex<File>>,
 #[cfg(windows)] next:AtomicUsize,
 #[cfg(not(any(unix,windows)))] file:Mutex<File>,
}
impl Reader {
 fn new(path:&Path)->Result<Self,String>{
  let file=File::open(path).map_err(|e|e.to_string())?;
  #[cfg(windows)] let files={let mut v=vec![Mutex::new(file)];
   for _ in 1..4 { if let Ok(f)=File::open(path){v.push(Mutex::new(f));} }v};
  Ok(Self{
   #[cfg(unix)] file,
   #[cfg(windows)] files,
   #[cfg(windows)] next:AtomicUsize::new(0),
   #[cfg(not(any(unix,windows)))] file:Mutex::new(file)
  })
 }
 fn read_range(&self,path:&Path,offset:u64,len:usize)->Result<Vec<u8>,String>{
  #[cfg(unix)] let size=self.file.metadata().map_err(|e|e.to_string())?.len();
  #[cfg(windows)] let size=self.files[0].lock().unwrap().metadata().map_err(|e|e.to_string())?.len();
  #[cfg(not(any(unix,windows)))] let size=self.file.lock().unwrap().metadata().map_err(|e|e.to_string())?.len();
  let end=offset.checked_add(len as u64).ok_or("overflow")?;
  if end>size{return Err("out of range".into())}
  let mut bytes=vec![0;len];
  #[cfg(unix)]{
    use std::os::unix::fs::FileExt;
    let mut consumed=0usize;
    while consumed<len{
     match self.file.read_at(&mut bytes[consumed..],offset+consumed as u64){
      Ok(0)=>return Err("EOF".into()),
      Ok(n)=>consumed+=n,
      Err(e) if e.kind()==std::io::ErrorKind::Interrupted=>continue,
      Err(e)=>return Err(e.to_string())
     }
    }
  }
  #[cfg(windows)]{
    let slot=self.next.fetch_add(1,Ordering::Relaxed)%self.files.len();
    let mut f=self.files[slot].lock().unwrap();
    f.seek(SeekFrom::Start(offset)).map_err(|e|e.to_string())?;
    f.read_exact(&mut bytes).map_err(|e|e.to_string())?;
  }
  #[cfg(not(any(unix,windows)))]{
    let mut f=self.file.lock().unwrap();
    f.seek(SeekFrom::Start(offset)).map_err(|e|e.to_string())?;
    f.read_exact(&mut bytes).map_err(|e|e.to_string())?;
  }
  black_box(path);
  Ok(bytes)
 }
}
#[derive(Default)]struct Cache{handles:Mutex<HashMap<PathBuf,Arc<Reader>>>}
impl Cache{
 fn read(&self,path:&Path,offset:u64,len:usize)->Result<Vec<u8>,String>{
  let reader={
   let mut g=self.handles.lock().unwrap();
   if let Some(reader)=g.get(path){Some(Arc::clone(reader))}
   else if g.len()>=MAX_RETAINED_PACKAGE_FILES{None}
   else {
    let reader=Arc::new(Reader::new(path)?);
    g.insert(path.to_path_buf(),Arc::clone(&reader));
    Some(reader)
   }
  };
  match reader{Some(reader)=>reader.read_range(path,offset,len),None=>old(path,offset,len)}
 }
}
fn old(path:&Path,offset:u64,len:usize)->Result<Vec<u8>,String>{
 let mut f=File::open(path).map_err(|e|e.to_string())?;
 let size=f.metadata().map_err(|e|e.to_string())?.len();
 let end=offset.checked_add(len as u64).ok_or("overflow")?;
 if end>size{return Err("out of range".into())}
 f.seek(SeekFrom::Start(offset)).map_err(|e|e.to_string())?;
 let mut bytes=vec![0;len];f.read_exact(&mut bytes).map_err(|e|e.to_string())?;Ok(bytes)
}
fn setup()->(PathBuf,Vec<PathBuf>){
 let dir=std::env::temp_dir().join(format!("d1_pkg_read_bench_{}_{}",std::process::id(),std::env::consts::OS));
 let _=fs::remove_dir_all(&dir);fs::create_dir(&dir).unwrap();
 let mut files=Vec::new();
 for patch in 0..12usize{
  let path=dir.join(format!("ps4_arch_cabal_005b_{patch}.pkg.bin"));
  let mut data=vec![0;BYTES_PER_PATCH];
  let mut seed=(0x34567193u32).wrapping_add(patch as u32);
  for b in &mut data{seed^=seed<<13;seed^=seed>>17;seed^=seed<<5;*b=seed as u8;}
  fs::write(&path,&data).unwrap();files.push(path);
 }(dir,files)
}
fn verify(cache:&Cache,paths:&[PathBuf]){
 for path in paths{
  for len in [0usize,1,32,4096,32768,262144]{
   for offset in [0,1,4096,BYTES_PER_PATCH-len]{
    assert_eq!(old(path,offset as u64,len),cache.read(path,offset as u64,len));
   }
  }
  assert!(old(path,(BYTES_PER_PATCH-3)as u64,4).is_err());
  assert!(cache.read(path,(BYTES_PER_PATCH-3)as u64,4).is_err());
 }
 assert_eq!(cache.handles.lock().unwrap().len(),8);
 std::thread::scope(|scope|{
  for tid in 0..12 {
   scope.spawn(move||{
    for i in 0..80{
     let owner=(tid*7+i*11)%paths.len();
     let offset=(tid*97+i*1741)%(BYTES_PER_PATCH-32768);
     assert_eq!(old(&paths[owner],offset as u64,32768),cache.read(&paths[owner],offset as u64,32768));
    }
   });
  }
 });
 println!("PASS: 12 owners, bounded eight-file cache, exact bounds and 12 concurrent readers");
}
fn bench(paths:&[PathBuf],owners:usize,workers:usize,len:usize){
 let cache=Arc::new(Cache::default());
 let reads_per_worker=if len>=32768 {60}else{160};
 // Warm reader pool without timing the initial opens; compare steady state.
 for path in &paths[..owners.min(MAX_RETAINED_PACKAGE_FILES)]{cache.read(path,0,64).unwrap();}
 let measure=|reuse:bool|{
  let start=Instant::now();
  std::thread::scope(|scope|{
   for tid in 0..workers{
    let cache=Arc::clone(&cache);
    scope.spawn(move||{
     let mut check=0u8;
     for i in 0..reads_per_worker{
      let owner=(tid*37+i*11)%owners;
      let at=((i*3359+tid*12133)%(BYTES_PER_PATCH-len))as u64;
      let bytes=if reuse{cache.read(&paths[owner],at,len).unwrap()}else{old(&paths[owner],at,len).unwrap()};
      check^=bytes[0];black_box(bytes);
     }black_box(check);
    });
   }
  });start.elapsed().as_secs_f64()
 };
 let(mut olds,mut optimized)=(Vec::new(),Vec::new());
 for round in 0..7{
  let(a,b)=if round%2==0{(measure(false),measure(true))}else{let b=measure(true);(measure(false),b)};
  olds.push(a);optimized.push(b);
 }
 olds.sort_by(f64::total_cmp);optimized.sort_by(f64::total_cmp);
 println!("patch_owners={owners} workers={workers} bytes={len} requests={} old_ms={:.3} retained_ms={:.3} speedup={:.2}x",
  workers*reads_per_worker,olds[3]*1000.,optimized[3]*1000.,olds[3]/optimized[3]);
}
fn main(){
 let (dir,paths)=setup();
 {let cache=Cache::default();verify(&cache,&paths);}
 for owners in [4usize,12]{
  for workers in [1usize,8]{
   for len in [4096usize,32768]{bench(&paths,owners,workers,len);}
  }
 }
 fs::remove_dir_all(dir).unwrap();
}
