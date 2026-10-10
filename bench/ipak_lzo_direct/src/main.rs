use std::{hint::black_box,time::Instant};
const CAP:usize=0x8000;

fn scratch_decode(commands:&[Vec<u8>])->Result<Vec<u8>,lzo::Error>{
    let mut output=Vec::new();
    let mut scratch=[0u8;CAP];
    for command in commands {
        let size=lzo::decompress_into(command,&mut scratch)?;
        output.extend_from_slice(&scratch[..size]);
    }
    Ok(output)
}
fn direct_decode(commands:&[Vec<u8>])->Result<Vec<u8>,lzo::Error>{
    let mut output=Vec::new();
    for command in commands {
        let begin=output.len();
        output.resize(begin+CAP,0);
        let size=lzo::decompress_into(command,&mut output[begin..])?;
        output.truncate(begin+size);
    }
    Ok(output)
}
fn make_plaintext(n:usize,kind:usize)->Vec<u8>{
    let mut seed=0xa293_1f41u32;
    (0..n).map(|i|{
        seed^=seed<<13;seed^=seed>>17;seed^=seed<<5;
        match kind {0=>0,1=>((i*31)%251)as u8,_=>seed as u8}
    }).collect()
}
fn main(){
    let known:[u8;21]=[34,104,101,108,108,111,44,32,108,122,111,32,119,111,114,108,100,33,17,0,0];
    assert_eq!(scratch_decode(&[known.to_vec()]).unwrap(),b"hello, lzo world!");
    assert_eq!(direct_decode(&[known.to_vec()]).unwrap(),b"hello, lzo world!");
    for len in [17usize,256,4096,16384,32768]{
        for kind in 0..3{
            let plaintext=make_plaintext(len,kind);
            let compressed=lzo1x::compress(&plaintext,lzo1x::CompressLevel::default());
            let one=scratch_decode(&[compressed.clone()]).unwrap();
            assert_eq!(one,plaintext,"incompatible compressor/decoder len={len} kind={kind}");
            let count=if len<512 {256} else if len<8192 {128} else {48};
            let commands=vec![compressed.clone();count];
            let expected=plaintext.repeat(count);
            assert_eq!(scratch_decode(&commands).unwrap(),expected);
            assert_eq!(direct_decode(&commands).unwrap(),expected);
            for last_bytes in [0usize,1,2,3,compressed.len().saturating_sub(1)] {
                let n=last_bytes.min(compressed.len());
                let cases=vec![compressed[..n].to_vec()];
                let a=scratch_decode(&cases);
                let b=direct_decode(&cases);
                assert_eq!(a.is_ok(),b.is_ok(),"malformed parity len={len} kind={kind} bytes={n}");
                if let (Ok(a),Ok(b))=(a,b){assert_eq!(a,b);}
            }
            let mut original=Vec::new();
            let mut direct=Vec::new();
            let old=||{
                let start=Instant::now();
                for _ in 0..10 {
                    let result=scratch_decode(black_box(&commands)).unwrap();
                    black_box(result);
                }
                start.elapsed().as_secs_f64()
            };
            let new=||{
                let start=Instant::now();
                for _ in 0..10 {
                    let result=direct_decode(black_box(&commands)).unwrap();
                    black_box(result);
                }
                start.elapsed().as_secs_f64()
            };
            for round in 0..9{
                let (a,b)=if round%2==0 {(old(),new())} else {let b=new();let a=old();(a,b)};
                original.push(a);direct.push(b);
            }
            original.sort_by(f64::total_cmp);
            direct.sort_by(f64::total_cmp);
            println!("lzo output={} B kind={} commands={} compressed={} B old={:.3}ms direct={:.3}ms ratio={:.3}x",
                len,kind,count,compressed.len(),original[4]*1000.0,direct[4]*1000.0,original[4]/direct[4]);
        }
    }
    println!("PASS: LZO 0.1.3 output equality and malformed-input parity");
}
