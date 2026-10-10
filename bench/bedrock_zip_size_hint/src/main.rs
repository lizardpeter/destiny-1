use std::{io::{Cursor,Read,Write},hint::black_box,time::Instant};
use zip::{ZipArchive,ZipWriter,CompressionMethod,write::SimpleFileOptions};
const LIMIT:u64=256*1024;
fn make_archive(count:usize,size:usize,compress:bool)->Vec<u8>{
 let cursor=Cursor::new(Vec::new());let mut writer=ZipWriter::new(cursor);
 let method=if compress{CompressionMethod::Deflated}else{CompressionMethod::Stored};
 let options=SimpleFileOptions::default().compression_method(method);
 for i in 0..count {
  writer.start_file(format!("textures/item_{i:05}.png"),options).unwrap();
  let mut data=vec![0u8;size];
  let mut state=0x2345_6789u32.wrapping_add(i as u32*3);
  for (j,b) in data.iter_mut().enumerate(){
   state^=state<<13;state^=state>>17;state^=state<<5;
   *b=if compress{((j+i)%31)as u8}else{state as u8};
  }
  writer.write_all(&data).unwrap();
 }
 writer.finish().unwrap().into_inner()
}
fn read_files(bytes:&[u8],with_hint:bool)->Vec<(usize,u64)>{
 let cursor=Cursor::new(bytes);
 let mut zip=ZipArchive::new(cursor).unwrap();
 let mut outputs=Vec::with_capacity(zip.len());
 for i in 0..zip.len(){
  let mut entry=zip.by_index(i).unwrap();
  let mut buffer=if with_hint{Vec::with_capacity(entry.size().min(LIMIT) as usize)}else{Vec::new()};
  entry.read_to_end(&mut buffer).unwrap();
  let digest=buffer.iter().step_by(7).fold(0u64,|a,&x|a.wrapping_mul(33).wrapping_add(x as u64));
  outputs.push((buffer.len(),digest));
 }
 outputs
}
fn main(){
 for compressed in [false,true] {
  for size in [64usize,512,4096,32768,262144]{
    let count=if size>=262144{12}else if size>=32768{48}else{256};
    let archive=make_archive(count,size,compressed);
    let baseline=read_files(&archive,false);
    let presized=read_files(&archive,true);
    assert_eq!(baseline,presized);
    let runs=if size>=32768{5}else{9};
    let old=||{let start=Instant::now();let out=read_files(black_box(&archive),false);black_box(out);start.elapsed().as_secs_f64()};
    let new=||{let start=Instant::now();let out=read_files(black_box(&archive),true);black_box(out);start.elapsed().as_secs_f64()};
    let (mut a,mut b)=(Vec::new(),Vec::new());
    for round in 0..runs{
      let (o,n)=if round%2==0{(old(),new())}else{let n=new();(old(),n)};
      a.push(o);b.push(n);
    }
    a.sort_by(f64::total_cmp);b.sort_by(f64::total_cmp);
    println!("compression={} bytes={} entries={} old_ms={:.3} hint_ms={:.3} ratio={:.3}x",compressed,size,count,a[runs/2]*1000.,b[runs/2]*1000.,a[runs/2]/b[runs/2]);
  }
 }
 println!("PASS: ZIP2.4 preallocation parity across Stored and Deflate resources");
}
