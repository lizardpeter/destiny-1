//! Public, dependency-free read-only file-range parity/performance harness.
//! Uses synthetic data only; no private assets or decoder source.
use std::{fs::{self, File}, io::{Read, Seek, SeekFrom}, path::{Path, PathBuf},
    sync::Arc, thread, time::Instant};
#[cfg(windows)]
use std::sync::{atomic::{AtomicUsize, Ordering}, Mutex};

#[cfg(windows)]
#[derive(Debug)]
struct WindowsReadPool { handles: Vec<Mutex<File>>, next: AtomicUsize }
#[cfg(windows)]
impl WindowsReadPool {
    fn new(path: &Path, first: File) -> Self {
        let mut handles = vec![Mutex::new(first)];
        for _ in 1..4 {
            match File::open(path) { Ok(f) => handles.push(Mutex::new(f)), Err(_) => break }
        }
        Self { handles, next: AtomicUsize::new(0) }
    }
    fn read(&self, offset: u64, len: usize) -> std::io::Result<Vec<u8>> {
        let slot = self.next.fetch_add(1, Ordering::Relaxed) % self.handles.len();
        let mut file = self.handles[slot].lock().unwrap();
        baseline_read_handle(&mut file, offset, len)
    }
}
fn baseline_read_handle(file: &mut File, offset: u64, len: usize) -> std::io::Result<Vec<u8>> {
    file.seek(SeekFrom::Start(offset))?;
    let mut buf = vec![0; len];
    file.read_exact(&mut buf)?;
    Ok(buf)
}
fn baseline(path: &Path, offset: u64, len: usize) -> Vec<u8> {
    baseline_read_handle(&mut File::open(path).unwrap(), offset, len).unwrap()
}
struct Reader {
    #[cfg(windows)]
    pool: Arc<WindowsReadPool>,
    #[cfg(not(windows))]
    file: Arc<File>,
}
impl Reader {
    fn open(path: &Path) -> Self {
        let file = File::open(path).unwrap();
        Self {
            #[cfg(windows)]
            pool: Arc::new(WindowsReadPool::new(path, file)),
            #[cfg(not(windows))]
            file: Arc::new(file),
        }
    }
    fn read(&self, offset: u64, len: usize) -> std::io::Result<Vec<u8>> {
        #[cfg(windows)]
        { self.pool.read(offset, len) }
        #[cfg(unix)]
        {
            let mut out = vec![0u8; len];
            let mut cursor = 0;
            while cursor < out.len() {
                let position = offset.checked_add(cursor as u64).unwrap();
                let read = std::os::unix::fs::FileExt::read_at(&*self.file, &mut out[cursor..], position);
                match read {
                    Ok(0) => return Err(std::io::Error::from(std::io::ErrorKind::UnexpectedEof)),
                    Ok(n) => cursor += n,
                    Err(e) if e.kind() == std::io::ErrorKind::Interrupted => continue,
                    Err(e) => return Err(e)
                }
            }
            Ok(out)
        }
        #[cfg(not(any(windows,unix)))]
        { let _=(offset,len); unreachable!() }
    }
}
fn main() {
    let path: PathBuf = std::env::temp_dir().join(format!("ipak_range_bench_{}.tmp", std::process::id()));
    let mut data = vec![0u8; 32*1024*1024];
    let mut seed: u32 = 0x1234_5678;
    for byte in &mut data { seed ^= seed << 13; seed ^= seed >> 17; seed ^= seed << 5; *byte = seed as u8; }
    fs::write(&path, &data).unwrap();
    {
        let reader = Arc::new(Reader::open(&path));
        for size in [0,1,64,4096,32768,262144] {
            for i in 0..40 {
                let offset = ((i * 763_591) % (data.len()-size+1)) as u64;
                let reference = baseline(&path, offset, size);
                assert_eq!(reference, data[offset as usize..offset as usize+size]);
                assert_eq!(reader.read(offset, size).unwrap(), reference);
            }
        }
        assert!(reader.read((data.len()-4) as u64, 16).is_err());
        thread::scope(|scope| {
            for id in 0..16 {
                let reader=Arc::clone(&reader);
                let data=&data;
                scope.spawn(move || {
                    for i in 0..100 {
                        let size=if i%3==0 {65536} else {4096};
                        let offset=(id*712_661 + i*97_123) % (data.len()-size);
                        assert_eq!(reader.read(offset as u64,size).unwrap(),data[offset..offset+size]);
                    }
                });
            }
        });
        println!("PASS: cross-offset, parallel (16 threads), EOF parity");
        for size in [64, 4096, 32768, 262144] {
            let count=if size>=262144 {100} else {500};
            let offsets: Vec<u64>=(0..count).map(|i| ((i*765_431)%(data.len()-size)) as u64).collect();
            let mut original=Vec::new();
            let mut pooled=Vec::new();
            for round in 0..9 {
                let timed_old=||{let start=Instant::now();let mut digest=0usize;
                    for &at in &offsets { let bytes=baseline(&path,at,size);digest^=bytes[0] as usize;}
                    std::hint::black_box(digest);start.elapsed().as_secs_f64()};
                let timed_new=||{let start=Instant::now();let mut digest=0usize;
                    for &at in &offsets { let bytes=reader.read(at,size).unwrap();digest^=bytes[0] as usize;}
                    std::hint::black_box(digest);start.elapsed().as_secs_f64()};
                let (a,b)=if round%2==0 {(timed_old(),timed_new())} else {let b=timed_new();let a=timed_old();(a,b)};
                original.push(a);pooled.push(b);
            }
            original.sort_by(|a,b|a.total_cmp(b));
            pooled.sort_by(|a,b|a.total_cmp(b));
            println!("size={} B, old={:.3} ms, pooled={:.3} ms, speedup={:.2}x",
                size,1000.0*original[4],1000.0*pooled[4],original[4]/pooled[4]);
        }
    }
    fs::remove_file(&path).unwrap();
}
