use std::{hint::black_box,time::Instant};
mod baseline;
mod optimized;
fn setup(fields:usize,rows:usize,duplicate:bool)->Vec<u8>{
 let record_size=fields*4;
 let record_off=0x10+fields*12;
 let mut b=vec![0;record_off+record_size*rows];
 b[0..4].copy_from_slice(&(rows as u32).to_be_bytes());
 b[4..8].copy_from_slice(&(fields as u32).to_be_bytes());
 b[8..12].copy_from_slice(&(record_off as u32).to_be_bytes());
 b[12..16].copy_from_slice(&(record_size as u32).to_be_bytes());
 for col in 0..fields {
  let name=if duplicate && col==fields-1{format!("field_{:03}",3)}else{format!("field_{col:03}")};
  let h=baseline::bcsv_hash_smg(&name);
  let i=16+col*12;
  b[i..i+4].copy_from_slice(&h.to_be_bytes());
  b[i+4..i+8].copy_from_slice(&u32::MAX.to_be_bytes());
  b[i+8..i+10].copy_from_slice(&((col*4)as u16).to_be_bytes());
  for row in 0..rows{
   let val=(row as u32).wrapping_mul(41).wrapping_add(col as u32*3);
   let at=record_off+row*record_size+col*4;
   b[at..at+4].copy_from_slice(&val.to_be_bytes());
  }
 }b
}
fn check(fields:usize,rows:usize,duplicate:bool){
 let bytes=setup(fields,rows,duplicate);
 let base=baseline::Bcsv::parse(&bytes).unwrap();
 let next=optimized::Bcsv::parse(&bytes).unwrap();
 assert_eq!(base.records,next.records);
 for row in 0..rows {
  for col in 0..fields{
   let name=if duplicate && col==fields-1{"field_003".to_string()}else{format!("field_{col:03}")};
   assert_eq!(base.field_index(&name),next.field_index(&name));
   assert_eq!(base.int(row,&name),next.int(row,&name));
  }
 }
 assert_eq!(base.field_index("missing"),next.field_index("missing"));
 assert_eq!(base.int(rows,"field_000"),next.int(rows,"field_000"));
}
fn loop_before(t:&baseline::Bcsv,names:&[String],repeat:usize)->i64{
 let mut sum=0i64;
 for i in 0..repeat {
  let row=i%t.records.len();
  let name=&names[(i*37+7)%names.len()];
  sum+=t.int(row,black_box(name)).unwrap_or(-1) as i64;
 }
 black_box(sum)
}
fn loop_next(t:&optimized::Bcsv,names:&[String],repeat:usize)->i64{
 let mut sum=0i64;
 for i in 0..repeat {
  let row=i%t.records.len();
  let name=&names[(i*37+7)%names.len()];
  sum+=t.int(row,black_box(name)).unwrap_or(-1) as i64;
 }
 black_box(sum)
}
fn bench(fields:usize,misses:bool){
 let source=setup(fields,128,false);
 let base=baseline::Bcsv::parse(&source).unwrap();
 let next=optimized::Bcsv::parse(&source).unwrap();
 let mut names=(0..fields).map(|i|format!("field_{i:03}")).collect::<Vec<_>>();
 if misses{names.extend((0..fields).map(|i|format!("unknown_{i:03}")));}
 let repeat=if fields>128{100_000}else{250_000};
 assert_eq!(loop_before(&base,&names,repeat),loop_next(&next,&names,repeat));
 let measure=|new:bool|{
  let start=Instant::now();
  if new{black_box(loop_next(&next,black_box(&names),repeat));}
  else{black_box(loop_before(&base,black_box(&names),repeat));}
  start.elapsed().as_secs_f64()
 };
 let(mut old,mut new)=(Vec::new(),Vec::new());
 for k in 0..9{
  if k%2==0{old.push(measure(false));new.push(measure(true))}
  else{new.push(measure(true));old.push(measure(false))}
 }
 old.sort_by(f64::total_cmp);new.sort_by(f64::total_cmp);
 println!("fields={fields} misses={misses} lookups={repeat} old_ms={:.3} indexed_ms={:.3} speedup={:.3}x",
  old[4]*1000.,new[4]*1000.,old[4]/new[4]);
}
fn main(){
 for n in [0usize,1,8,16,23,24,32,64,128,256]{
   if n>0{check(n,3,n>=5);}
 }
 println!("PASS: real BCSV decode parity, duplicates, missing fields and row bounds");
 for count in [8,16,23,24,32,64,128,256]{
  bench(count,false);bench(count,true);
 }
}
