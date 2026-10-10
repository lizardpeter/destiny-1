use std::{hint::black_box,time::Instant};
fn decompress_yaz0(_: &[u8]) -> Result<Vec<u8>,String> {Err("Yaz0 fixture not used".into())}
mod baseline;mod optimized;
fn be16(a:&mut[u8],p:usize,v:u16){a[p..p+2].copy_from_slice(&v.to_be_bytes());}
fn be32(a:&mut[u8],p:usize,v:u32){a[p..p+4].copy_from_slice(&v.to_be_bytes());}
fn align(v:usize,a:usize)->usize{(v+a-1)&!(a-1)}
fn fixture(count:usize)->Vec<u8>{
 assert!(count<65536);
 let node_pos=0x40;
 let entries_pos=node_pos+16;
 let string_pos=entries_pos+count*0x14;
 let mut names=vec![0u8];
 let mut offsets=Vec::new();
 for i in 0..count{
   let name=format!("texture_{i:05}.bti");
   offsets.push(names.len());
   names.extend_from_slice(name.as_bytes());names.push(0);
 }
 let data_pos=align(string_pos+names.len(),32);
 let mut result=vec![0u8;data_pos+count*64];
 result[..4].copy_from_slice(b"RARC");
 be32(&mut result,0x08,0x20);
 be32(&mut result,0x0c,(data_pos-0x20)as u32);
 be32(&mut result,0x20,1);be32(&mut result,0x24,(node_pos-0x20)as u32);
 be32(&mut result,0x28,count as u32);
 be32(&mut result,0x2c,(entries_pos-0x20)as u32);
 be32(&mut result,0x34,(string_pos-0x20)as u32);
 be32(&mut result,node_pos+4,0);
 be16(&mut result,node_pos+10,count as u16);
 be32(&mut result,node_pos+12,0);
 result[string_pos..string_pos+names.len()].copy_from_slice(&names);
 for i in 0..count {
   let at=entries_pos+i*0x14;
   be32(&mut result,at+4,offsets[i]as u32);
   be32(&mut result,at+8,(i*64)as u32);
   be32(&mut result,at+12,64);
   for j in 0..64 { result[data_pos+i*64+j]=((i*37+j*11)&255)as u8; }
 }
 result
}
fn consume_baseline(a:&baseline::RarcArchive,count:usize,queries:usize)->u64{
 let mut checksum=0u64;
 for i in 0..queries{
  let n=(i*151+79)%count;
  let path=format!("invalid_prefix/texture_{n:05}.bti");
  let bytes=a.get(black_box(&path)).unwrap();
  checksum=checksum.wrapping_add(bytes[(i%64)]as u64);
 }
 checksum
}
fn consume_optimized(a:&optimized::RarcArchive,count:usize,queries:usize)->u64{
 let mut checksum=0u64;
 for i in 0..queries{
  let n=(i*151+79)%count;
  let path=format!("invalid_prefix/texture_{n:05}.bti");
  let bytes=a.get(black_box(&path)).unwrap();
  checksum=checksum.wrapping_add(bytes[(i%64)]as u64);
 }
 checksum
}
fn bench(count:usize,queries:usize){
 let raw=fixture(count);
 let a=baseline::RarcArchive::parse(&raw).unwrap();
 let b=optimized::RarcArchive::parse(&raw).unwrap();
 assert_eq!(a.entries().count(),count);assert_eq!(b.entries().count(),count);
 for i in 0..count{
  let path=format!("wrong/texture_{i:05}.bti");
  assert_eq!(a.get(&path),b.get(&path));
  let direct=format!("texture_{i:05}.bti");
  assert_eq!(a.get(&direct),b.get(&direct));
 }
 assert_eq!(a.get("does-not-exist.bti"),b.get("does-not-exist.bti"));
 assert_eq!(consume_baseline(&a,count,queries),consume_optimized(&b,count,queries));
 let old=||{let t=Instant::now();black_box(consume_baseline(&a,count,queries));t.elapsed().as_secs_f64()};
 let new=||{let t=Instant::now();black_box(consume_optimized(&b,count,queries));t.elapsed().as_secs_f64()};
 let(mut olds,mut news)=(Vec::new(),Vec::new());
 for turn in 0..9 {let (a,b)=if turn%2==0{(old(),new())}else{let b=new();(old(),b)};olds.push(a);news.push(b);}
 olds.sort_by(f64::total_cmp);news.sort_by(f64::total_cmp);
 println!("entries={count} fallback_queries={queries} old_ms={:.3} indexed_ms={:.3} speedup={:.2}x",
  olds[4]*1000.,news[4]*1000.,olds[4]/news[4]);
}
fn main(){
 for count in [16usize,256,1024,4096]{
  let queries=if count>=4096{800}else if count>=1024{1600}else{3000};
  bench(count,queries);
 }
 println!("PASS: exact RARC source module parse/lookup result parity");
}
