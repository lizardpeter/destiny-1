use std::{hint::black_box,time::Instant};

const HEADER:usize=128;
const CRC29:u32=0x1fff_ffff;

#[derive(Clone,Copy,Debug)]
enum Endian { Little, Big }
fn read_word(input:&[u8],offset:usize,endian:Endian)->Result<u32,&'static str> {
    let bytes:[u8;4]=input.get(offset..offset+4).ok_or("truncated header")?.try_into().unwrap();
    Ok(match endian { Endian::Little=>u32::from_le_bytes(bytes), Endian::Big=>u32::from_be_bytes(bytes) })
}
fn crc(payload:&[u8])->u32 {crc32fast::hash(payload) & CRC29}
fn verify(payload:&[u8],expected:u32)->Result<(),&'static str>{
    if crc(payload)==expected & CRC29 {Ok(())} else {Err("CRC29 mismatch")}
}
// Old single-raw case: length and command header validation, output allocation
// and copying, and mandatory accelerated CRC29 verification.
fn old_single_raw(input:&[u8],endian:Endian,expected:u32)->Result<Vec<u8>,&'static str>{
    let block=read_word(input,0,endian)?;
    if block>>24!=1 || block&0x00ff_ffff!=0 {return Err("invalid output offset or command count")}
    let command=read_word(input,4,endian)?;
    if command>>24!=0 {return Err("not raw")}
    let size=(command&0x00ff_ffff)as usize;
    if input.len()!=HEADER+size {return Err("invalid command size")}
    let mut output=Vec::new();
    output.extend_from_slice(&input[HEADER..]);
    verify(&output,expected)?;
    Ok(output)
}
// Owned-byte single-raw fast-path. No new output allocation.
// General IPAK decoder is intentionally not reproduced in this public harness.
fn new_single_raw(mut input:Vec<u8>,endian:Endian,expected:u32)->Result<Vec<u8>,&'static str>{
    if input.len()<HEADER {return Err("truncated header")}
    let block=read_word(&input,0,endian)?;
    let command=read_word(&input,4,endian)?;
    if block>>24!=1 || block&0x00ff_ffff!=0 {return Err("invalid output offset or command count")}
    if command>>24!=0 {return Err("not raw")}
    let size=(command&0x00ff_ffff)as usize;
    if input.len()-HEADER!=size {return Err("invalid command size")}
    verify(&input[HEADER..],expected)?;
    input.copy_within(HEADER..,0);
    input.truncate(size);
    Ok(input)
}
fn fixture(len:usize,endian:Endian)->Vec<u8>{
    assert!(len<=0x00ff_ffff);
    let mut encoded=vec![0;HEADER+len];
    let w1=1u32<<24;
    encoded[..4].copy_from_slice(&match endian{Endian::Little=>w1.to_le_bytes(),Endian::Big=>w1.to_be_bytes()});
    encoded[4..8].copy_from_slice(&match endian{Endian::Little=>(len as u32).to_le_bytes(),Endian::Big=>(len as u32).to_be_bytes()});
    let mut state=0xcafe_babeu32;
    for out in &mut encoded[HEADER..]{
        state^=state<<13;state^=state>>17;state^=state<<5;*out=state as u8;
    }
    encoded
}
fn check() {
    for endian in [Endian::Little,Endian::Big]{
        for size in [0,1,4,7,15,16,64,255,512,4096,32768,262144,1_048_576]{
            let bytes=fixture(size,endian); let hash=crc(&bytes[HEADER..]);
            let old=old_single_raw(&bytes,endian,hash).unwrap();
            let fast=new_single_raw(bytes.clone(),endian,hash).unwrap();
            assert_eq!(old,fast);
            assert_eq!(old_single_raw(&bytes,endian,hash^1).unwrap_err(),new_single_raw(bytes.clone(),endian,hash^1).unwrap_err());
            let buf=bytes.clone();let ptr=buf.as_ptr();
            let output=new_single_raw(buf,endian,hash).unwrap();
            assert_eq!(ptr,output.as_ptr());
            if size>0{
                let mut corrupted=bytes.clone();corrupted[HEADER]^=0x01;
                assert_eq!(old_single_raw(&corrupted,endian,hash).is_ok(),new_single_raw(corrupted,endian,hash).is_ok());
            }
        }
    }
    println!("PASS: 26 sizes/endian fixtures, pointer identity, CRC failure and mutation parity");
}
fn benchmark(){
    for len in [64,512,4096,32768,262144,1048576] {
        let input=fixture(len,Endian::Little);
        let hash=crc(&input[HEADER..]);
        let iterations=match len {0..=4096=>1200,4097..=32768=>500,32769..=262144=>100,_=>30};
        let old_run=||{
            let start=Instant::now();
            let mut digest=0u8;
            for _ in 0..iterations {
                let input=black_box(input.clone());
                let out=old_single_raw(&input,Endian::Little,hash).unwrap();
                digest^=out[0];black_box(out);
            }
            black_box(digest);start.elapsed().as_secs_f64()
        };
        let new_run=||{
            let start=Instant::now();
            let mut digest=0u8;
            for _ in 0..iterations {
                let input=black_box(input.clone());
                let out=new_single_raw(input,Endian::Little,hash).unwrap();
                digest^=out[0];black_box(out);
            }
            black_box(digest);start.elapsed().as_secs_f64()
        };
        let mut old=Vec::new();
        let mut new=Vec::new();
        for round in 0..13 {
            let (a,b)=if round%2==0 {(old_run(),new_run())}
                 else{let b=new_run();let a=old_run();(a,b)};
            old.push(a);new.push(b);
        }
        old.sort_by(f64::total_cmp);new.sort_by(f64::total_cmp);
        println!("single-RAW payload={} bytes, iterations={}, old={:.4}ms, owned={:.4}ms, speedup={:.3}x",len,iterations,old[6]*1000.0,new[6]*1000.0,old[6]/new[6]);
    }
}
fn main(){check();benchmark()}
#[cfg(test)]
mod tests{
    #[test] fn single_raw_correctness(){super::check();}
}
