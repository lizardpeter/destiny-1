#[path = "../../t6_fastfile/src/candidate.rs"]
mod fastfile;

use flate2::{write::DeflateEncoder, Compression};
use sha1::{Digest as _, Sha1};
use sha2::Sha256;
use std::{env,fs,hint::black_box,io::Write,path::Path,time::Instant};

fn pseudo_random(seed:u32,n:usize,mode:usize)->Vec<u8>{
    let mut x=seed|1;
    (0..n).map(|i|{
        x^=x<<13; x^=x>>17; x^=x<<5;
        match mode {
            0 => (i%4) as u8,
            1 => if i%8 < 6 {0x42} else {x as u8},
            2 => x as u8,
            _ => 0,
        }
    }).collect()
}
fn hex(bytes:&[u8])->String{
    const H:&[u8;16]=b"0123456789abcdef";
    let mut s=String::with_capacity(bytes.len()*2);
    for b in bytes { s.push(H[(b>>4) as usize] as char); s.push(H[(b&15) as usize] as char); }
    s
}
fn cases()->[(&'static str,usize,usize,usize);4]{
    [("small",192,400,0),("mixed",8192,320,1),("random",16384,240,2),("zeros",32768,240,3)]
}
fn generate(path:&Path){
    fs::create_dir_all(path).unwrap();
    let zone=b"t6_benchmark";
    for (name,n,records,mode) in cases(){
        let mut file=vec![0u8;0x138];
        file[0..8].copy_from_slice(b"TAff0100");
        file[8..12].copy_from_slice(&0x93u32.to_le_bytes());
        file[12..20].copy_from_slice(b"PHEEBs71");
        file[24..24+zone.len()].copy_from_slice(zone);
        let mut table=vec![0u8;800*20];
        for d in 0..4000 {table[d*4..d*4+4].fill(zone[d%zone.len()]);}
        let mut counters=[0usize;4];
        let mut expected=Vec::new();
        for i in 0..records {
            let stream=i%4;
            let index=(counters[stream]*4+stream)%800;
            let nonce: [u8;8]=table[index*20..index*20+8].try_into().unwrap();
            let input=pseudo_random((i as u32).wrapping_mul(1231)+47,n,mode);
            let mut encoder=DeflateEncoder::new(Vec::new(),Compression::new(6));
            encoder.write_all(&input).unwrap();
            let compressed=encoder.finish().unwrap();
            assert!(compressed.len()<=32768,"cannot fit encrypted record");
            let encrypted=fastfile::benchmark_encrypt(&compressed,&nonce);
            file.extend_from_slice(&(encrypted.len() as u32).to_le_bytes());
            file.extend_from_slice(&encrypted);
            expected.extend_from_slice(&input);
            let digest=Sha1::digest(&compressed);
            counters[stream]+=1;
            let next=(counters[stream]*4+stream)%800;
            for j in 0..20 {table[next*20+j]^=digest[j];}
        }
        file.extend_from_slice(&[0u8;4]);
        fs::write(path.join(format!("{name}.ff")),&file).unwrap();
        fs::write(path.join(format!("{name}.sha256")),hex(&Sha256::digest(&expected))).unwrap();
        println!("GENERATED profile={name} records={records} encrypted={} expanded={}",file.len(),expected.len());
    }
}
fn bench(path:&Path, no_audit:bool){
    for (name,_,count,_) in cases(){
        let file=fs::read(path.join(format!("{name}.ff"))).unwrap();
        let expected=fs::read_to_string(path.join(format!("{name}.sha256"))).unwrap();
        let mut result_hash=None;
        for _ in 0..2 {
            let (out,summary)=if no_audit {
                fastfile::decode_bytes_without_audit(black_box(&file)).unwrap()
            } else {
                let (out,audits,summary)=fastfile::decode_bytes(black_box(&file)).unwrap();
                assert_eq!(audits.len(),count);
                (out,summary)
            };
            assert_eq!(summary.records,count);
            assert_eq!(summary.expanded_sha256,expected);
            result_hash=Some(summary.expanded_sha256);
            black_box(out);
        }
        let start=Instant::now();
        for _ in 0..5 {
            if no_audit {
                let (expanded,summary)=fastfile::decode_bytes_without_audit(black_box(&file)).unwrap();
                assert_eq!(summary.expanded_sha256,expected);
                black_box((expanded,summary));
            } else {
                let (expanded,audit,summary)=fastfile::decode_bytes(black_box(&file)).unwrap();
                assert_eq!(summary.expanded_sha256,expected);
                black_box((expanded,audit,summary));
            }
        }
        let secs=start.elapsed().as_secs_f64()/5.0;
        println!("BENCH\t{name}\t{secs:.9}\t{}\t{}",file.len(),result_hash.unwrap());
    }
}
fn main(){
    let args=env::args().collect::<Vec<_>>();
    assert_eq!(args.len(),3,"usage: binary --generate|--bench folder");
    let path=Path::new(&args[2]);
    match args[1].as_str(){"--generate"=>generate(path),"--bench"=>bench(path,false),"--bench-no-audit"=>bench(path,true),_=>panic!("unknown command")}
}
