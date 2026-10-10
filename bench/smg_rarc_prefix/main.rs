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

fn checksum_base(a:&baseline::RarcArchive,prefix:&str)->u64{
 let mut output=0u64;
 for e in a.entries_under(black_box(prefix)){output=output.wrapping_add(e.data[4]as u64);}
 output
}
fn checksum_new(a:&optimized::RarcArchive,prefix:&str)->u64{
 let mut output=0u64;
 for e in a.entries_under(black_box(prefix)){output=output.wrapping_add(e.data[4]as u64);}
 output
}
fn bench(count:usize,prefix:&str){
 let data=fixture(count);
 let base=baseline::RarcArchive::parse(&data).unwrap();
 let opt=optimized::RarcArchive::parse(&data).unwrap();
 let original=base.entries_under(prefix).map(|e|e.path.clone()).collect::<Vec<_>>();
 let changed=opt.entries_under(prefix).map(|e|e.path.clone()).collect::<Vec<_>>();
 assert_eq!(original,changed);
 assert_eq!(checksum_base(&base,prefix),checksum_new(&opt,prefix));
 let repeat=if count>=16384{300}else{1000};
 let old=||{let t=Instant::now();for _ in 0..repeat{black_box(checksum_base(&base,prefix));}t.elapsed().as_secs_f64()};
 let new=||{let t=Instant::now();for _ in 0..repeat{black_box(checksum_new(&opt,prefix));}t.elapsed().as_secs_f64()};
 let(mut before,mut after)=(Vec::new(),Vec::new());
 for round in 0..7 {
  let(a,b)=if round%2==0{(old(),new())}else{let b=new();(old(),b)};
  before.push(a);after.push(b);
 }
 before.sort_by(f64::total_cmp);after.sort_by(f64::total_cmp);
 println!("entries={count} prefix={prefix:?} matches={} repeats={repeat} old_ms={:.3} range_ms={:.3} speedup={:.3}x",
  original.len(),before[3]*1000.,after[3]*1000.,before[3]/after[3]);
}
fn main(){
 for count in [256usize,1024,4096,16384] {
  for prefix in ["texture_000","texture_00","texture_","zzz","texture_00001","TEXTURE_000","/texture_000/"] {
    bench(count,prefix);
  }
 }
 println!("PASS: exact-source RARC prefix enumeration parity and ordering");
}
