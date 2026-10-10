use std::{hint::black_box,time::Instant};
const HEADER:usize=128;
const MAX_COMMANDS:usize=31;
const RAW:u8=0;
const SKIP:u8=0xcf;
const MASK:u32=0x1fff_ffff;
fn make(count:usize,size:usize,skip_mod:usize)->(Vec<u8>,Vec<u8>){
    let mut encoded=vec![0u8;HEADER];
    encoded[..4].copy_from_slice(&((count as u32)<<24).to_le_bytes());
    let mut expected=Vec::new();
    for i in 0..count {
        let skip=i%skip_mod==1;
        let kind=if skip{SKIP}else{RAW};
        let word=((kind as u32)<<24)|(size as u32);
        encoded[4+i*4..8+i*4].copy_from_slice(&word.to_le_bytes());
        for j in 0..size{
            let v=((i*97+j*13)&255)as u8;
            encoded.push(v);
            if !skip { expected.push(v); }
        }
    }
    (encoded,expected)
}
// One RAW/SKIP IPAK block; reproduces bounded-header parsing,
// command order, output accumulation, and CRC29 verification.
fn decode(encoded:&[u8], optimized:bool, expected_crc:u32)->Result<Vec<u8>,&'static str>{
    if encoded.len()<HEADER {return Err("truncated header")}
    let word=u32::from_le_bytes(encoded[..4].try_into().unwrap());
    let count=(word>>24) as usize;
    if count>MAX_COMMANDS{return Err("too many commands")}
    if word&MASK !=0 {return Err("offset mismatch")}
    let mut commands=[(0usize,0u8);MAX_COMMANDS];
    let mut total=0usize;
    let mut raw_bytes=0usize;
    let mut has_lzo=false;
    for (i,slot) in commands.iter_mut().enumerate().take(count){
        let word=u32::from_le_bytes(encoded[4+i*4..8+i*4].try_into().unwrap());
        let len=(word&MASK)as usize;
        let kind=(word>>24)as u8;
        total=total.checked_add(len).ok_or("overflow")?;
        if kind==RAW {raw_bytes+=len}
        if kind==1 {has_lzo=true}
        *slot=(len,kind);
    }
    if HEADER+total>encoded.len(){return Err("truncated payload")}
    let mut output=Vec::new();
    if optimized && count>1 && !has_lzo && raw_bytes>=1024 {output.reserve(raw_bytes);}
    let mut cursor=HEADER;
    for (size,kind) in commands.into_iter().take(count) {
        let end=cursor+size;
        let payload=&encoded[cursor..end];
        match kind {RAW=>output.extend_from_slice(payload),SKIP=>{},_=>return Err("unsupported command")}
        cursor=end;
    }
    if crc32fast::hash(&output)&MASK !=expected_crc {return Err("CRC29 mismatch")}
    Ok(output)
}
fn main() {
    for count in [2usize,8,31] {
        for chunk in [64usize,256,1024,4096]{
            for skip_mod in [2usize,4,100]{
                let (encoded,expected)=make(count,chunk,skip_mod);
                let crc=crc32fast::hash(&expected)&MASK;
                assert_eq!(decode(&encoded,false,crc).unwrap(),expected);
                assert_eq!(decode(&encoded,true,crc).unwrap(),expected);
                assert_eq!(decode(&encoded,false,crc^1).unwrap_err(),decode(&encoded,true,crc^1).unwrap_err());
                let iterations=if chunk>=4096 {120} else {800};
                let before=||{
                    let start=Instant::now();
                    for _ in 0..iterations {
                        let out=decode(black_box(&encoded),false,crc).unwrap();black_box(out);
                    }
                    start.elapsed().as_secs_f64()
                };
                let after=||{
                    let start=Instant::now();
                    for _ in 0..iterations {
                        let out=decode(black_box(&encoded),true,crc).unwrap();black_box(out);
                    }
                    start.elapsed().as_secs_f64()
                };
                let mut old=Vec::new();
                let mut new=Vec::new();
                for round in 0..11{
                    let (a,b)=if round%2==0 {(before(),after())}else{let b=after();(before(),b)};
                    old.push(a);new.push(b);
                }
                old.sort_by(f64::total_cmp);new.sort_by(f64::total_cmp);
                println!("commands={count}, chunk={chunk}, skip_mod={skip_mod}, raw_bytes={}, ratio={:.3}x",
                    expected.len(),old[5]/new[5]);
            }
        }
    }
    println!("PASS: 36 mixed RAW/SKIP cases with equal CRC29 success/failure");
}
