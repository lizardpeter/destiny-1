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

fn queries(count:usize,mode:usize,n:usize)->Vec<String>{
 (0..n).map(|i|{
   let idx=(i*151+79)%count;
   match mode{
    0=>format!("texture_{idx:05}.bti"),
    1=>format!("/texture_{idx:05}.bti/"),
    2=>format!("TEXTURE_{idx:05}.BTI"),
    3=>format!(r"\texture_{idx:05}.bti\"),
    4=>format!("missing/texture_{idx:05}.bti"),
    _=>format!("missing/TEXTURE_{idx:05}.BTI")
   }
 }).collect()
}
fn consume_base(a:&baseline::RarcArchive,q:&[String])->u64{
 let mut digest=0u64;
 for item in q{
  let byte=a.get(black_box(item)).unwrap();
  digest=digest.wrapping_add(byte[7] as u64);
 }digest
}
fn consume_opt(a:&optimized::RarcArchive,q:&[String])->u64{
 let mut digest=0u64;
 for item in q{
  let byte=a.get(black_box(item)).unwrap();
  digest=digest.wrapping_add(byte[7] as u64);
 }digest
}
fn bench(count:usize,mode:usize){
 let raw=fixture(count);
 let old=baseline::RarcArchive::parse(&raw).unwrap();
 let new=optimized::RarcArchive::parse(&raw).unwrap();
 let requests=if count>=4096 {20000}else{40000};
 let q=queries(count,mode,requests);
 for item in q.iter().take(300){assert_eq!(old.get(item),new.get(item));}
 assert_eq!(consume_base(&old,&q),consume_opt(&new,&q));
 let run_old=||{let t=Instant::now();black_box(consume_base(&old,black_box(&q)));t.elapsed().as_secs_f64()};
 let run_new=||{let t=Instant::now();black_box(consume_opt(&new,black_box(&q)));t.elapsed().as_secs_f64()};
 let(mut olds,mut news)=(Vec::new(),Vec::new());
 for round in 0..9{
  let(a,b)=if round%2==0{(run_old(),run_new())}else{let b=run_new();(run_old(),b)};
  olds.push(a);news.push(b);
 }
 olds.sort_by(f64::total_cmp);news.sort_by(f64::total_cmp);
 println!("entries={count} mode={mode} queries={requests} old_ms={:.3} borrowed_ms={:.3} speedup={:.3}x",olds[4]*1000.,news[4]*1000.,olds[4]/news[4]);
}
fn main(){
 for count in [16usize,256,1024,4096]{
  for mode in 0..6{bench(count,mode);}
 }
 println!("PASS: exact-source RARC normalized path, slash, case and fallback parity");
}
