use sha1::{Digest, Sha1};
use flate2::{write::DeflateEncoder, Compression};
use std::{hint::black_box, io::Write, time::Instant};
use t6_fastfile_bench::{original, optimized, candidate};

fn sample(size: usize, seed: u32, profile: usize) -> Vec<u8> {
    let mut x=seed|1;
    (0..size).map(|i| {
        x ^= x << 13; x ^= x >> 17; x ^= x << 5;
        if profile == 0 { (i % 4) as u8 }
        else if profile == 1 {if i%8 < 6 {0x42} else { x as u8 }}
        else {x as u8}
    }).collect()
}
fn frame_stream(records: usize, decoded_size: usize, profile: usize) -> (Vec<u8>,Vec<u8>) {
    let zone=b"t6_benchmark";
    let mut file=vec![0u8;0x138];
    file[0..8].copy_from_slice(b"TAff0100");
    file[8..12].copy_from_slice(&0x93u32.to_le_bytes());
    file[12..20].copy_from_slice(b"PHEEBs71");
    file[24..24+zone.len()].copy_from_slice(zone);
    let mut table=vec![0u8;800*20];
    for d in 0..4000 {table[d*4..d*4+4].fill(zone[d%zone.len()]);}
    let mut counters=[0usize;4];
    let mut expected=Vec::with_capacity(decoded_size*records);
    for r in 0..records {
        let stream=r%4;
        let t=(counters[stream]*4+stream)%800;
        let mut nonce=[0u8;8];
        nonce.copy_from_slice(&table[t*20..t*20+8]);
        let payload=sample(decoded_size,0x124abcd1u32.wrapping_add(r as u32*113),profile);
        let mut encoder=DeflateEncoder::new(Vec::new(),Compression::new(6));
        encoder.write_all(&payload).unwrap();
        let deflated=encoder.finish().unwrap();
        assert!(deflated.len()<=0x8000);
        let encrypted=original::benchmark_encrypt(&deflated,&nonce);
        file.extend_from_slice(&(encrypted.len() as u32).to_le_bytes());
        file.extend_from_slice(&encrypted);
        expected.extend_from_slice(&payload);
        let digest=Sha1::digest(&deflated);
        counters[stream]+=1;
        let next=(counters[stream]*4+stream)%800;
        for i in 0..20 { table[next*20+i]^=digest[i]; }
    }
    file.extend_from_slice(&[0u8;4]);
    (file,expected)
}
fn median(ratios:&mut [f64])->f64{ratios.sort_by(f64::total_cmp);ratios[ratios.len()/2]}
fn main(){
    for (size,records,profile) in [(192usize,400usize,0usize),(8192,320,1),(16384,240,2)] {
        let (file,expected)=frame_stream(records,size,profile);
        let (orig,rec,summary)=original::decode_bytes(&file).unwrap();
        let (fast,fr,fsum)=optimized::decode_bytes(&file).unwrap();
        let (cand,cr,csum)=candidate::decode_bytes(&file).unwrap();
        assert_eq!(orig,expected); assert_eq!(fast,expected); assert_eq!(cand,expected);
        assert_eq!(serde_json::to_value(&rec).unwrap(),serde_json::to_value(&fr).unwrap());
        assert_eq!(serde_json::to_value(&summary).unwrap(),serde_json::to_value(&fsum).unwrap());
        assert_eq!(serde_json::to_value(&fr).unwrap(),serde_json::to_value(&cr).unwrap());
        assert_eq!(serde_json::to_value(&fsum).unwrap(),serde_json::to_value(&csum).unwrap());
        let mut ratios=Vec::new();
        let reps=if size<1000 {9} else {4};
        for round in 0..9 {
            let mut elapsed=[0f64;2];
            for step in 0..2 {
                let optimized_first=(step==0)==(round%2==0);
                let start=Instant::now();
                for _ in 0..reps {
                    let decoded_and_digest=if optimized_first {
                        let (decoded,_,summary)=candidate::decode_bytes(black_box(&file)).unwrap();
                        (decoded,summary.expanded_sha256)
                    } else {
                        let (decoded,_,summary)=optimized::decode_bytes(black_box(&file)).unwrap();
                        (decoded,summary.expanded_sha256)
                    };
                    black_box(decoded_and_digest);
                }
                elapsed[usize::from(optimized_first)]=start.elapsed().as_secs_f64();
            }
            ratios.push(elapsed[0]/elapsed[1]);
        }
        println!("T6_BUFREAD_AB size={size} records={records} profile={profile} compressed_file_bytes={} ratio={:.4}x",file.len(),median(&mut ratios));
    }
    let mut nonce=[0u8;8];
    for (i,b) in nonce.iter_mut().enumerate(){*b=(i*23) as u8;}
    for size in [64usize,4096,32768] {
        let input=sample(size,1231,2);
        let a=original::benchmark_encrypt(&input,&nonce);
        let b=optimized::benchmark_encrypt(&input,&nonce);
        assert_eq!(a,b);
        let mut ratios=Vec::new();
        for round in 0..9 {
            let mut times=[0f64;2];
            for step in 0..2 {
                let fast=(step==0)==(round%2==0);
                let mut scratch=Vec::new();
                let start=Instant::now();
                for _ in 0..1000 {
                    if fast {
                        optimized::benchmark_crypto_reuse(black_box(&input),&nonce,&mut scratch);
                    } else {
                        original::benchmark_crypto_reuse(black_box(&input),&nonce,&mut scratch);
                    }
                    black_box(&scratch);
                }
                times[usize::from(fast)]=start.elapsed().as_secs_f64();
            }
            ratios.push(times[0]/times[1]);
        }
        println!("T6_SALSA20_AB size={size} bytes ratio={:.4}x",median(&mut ratios));
    }
}
