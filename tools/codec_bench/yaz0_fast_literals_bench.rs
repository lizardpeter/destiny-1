//! Paired in-process A/B speed comparisons for Rust-test SMG Yaz0 decoders.
#[path = "yaz0_baseline.rs"]
mod baseline;
#[path = "yaz0_fast_literals.rs"]
mod candidate;

use std::hint::black_box;
use std::time::Instant;

#[derive(Clone, Copy)]
enum Token {
    Literal(u8),
    Copy { distance: usize, length: usize },
}
fn pack(tokens: &[Token], target: usize) -> Vec<u8> {
    let mut frame = b"Yaz0".to_vec();
    frame.extend_from_slice(&(target as u32).to_be_bytes());
    frame.extend_from_slice(&[0; 8]);
    for window in tokens.chunks(8) {
        let mut flag = 0u8;
        for (i,token) in window.iter().enumerate() {
            if matches!(token,Token::Literal(_)) { flag |= 0x80 >> i; }
        }
        frame.push(flag);
        for token in window {
            match *token {
                Token::Literal(b) => frame.push(b),
                Token::Copy{distance,length} => {
                    assert!((1..=4096).contains(&distance));
                    assert!((3..=273).contains(&length));
                    let back=distance-1;
                    if length<18 {
                        frame.push(((length-2) << 4 | (back >> 8)) as u8);
                        frame.push(back as u8);
                    } else {
                        frame.push((back >> 8) as u8);
                        frame.push(back as u8);
                        frame.push((length-18) as u8);
                    }
                }
            }
        }
    }
    frame
}

fn fixture_literal(target: usize) -> Vec<u8> {
    let tokens:Vec<_>=(0..target).map(|i| Token::Literal(((i*131)^ (i>>3)) as u8)).collect();
    pack(&tokens,target)
}

fn fixture_repeated(target: usize) -> Vec<u8> {
    let mut tokens=vec![Token::Literal(0x6e)];
    let mut produced=1;
    while produced<target {
        let take=(target-produced).min(273);
        if take>=3 {
            tokens.push(Token::Copy{distance:1,length:take});
        } else {
            tokens.push(Token::Literal(0x6e));
        }
        produced+=take.max(1);
    }
    pack(&tokens,target)
}

fn fixture_mixed(target: usize) -> Vec<u8> {
    let mut tokens=Vec::new();
    for i in 0..4096 { tokens.push(Token::Literal((i*13^(i>>2)) as u8)); }
    let mut produced=4096usize;
    let mut seed=0x39e5_4b77u32;
    while produced<target {
        seed^=seed<<13;seed^=seed>>17;seed^=seed<<5;
        let remaining=target-produced;
        let length=(3 + ((seed>>8) as usize % 271)).min(remaining);
        if seed & 3 == 0 || length < 3 {
            tokens.push(Token::Literal((seed>>16) as u8));
            produced+=1;
        } else {
            let distance=1+(seed as usize%produced.min(4096));
            tokens.push(Token::Copy{distance,length});
            produced+=length;
        }
    }
    pack(&tokens,target)
}

fn median(mut values:Vec<f64>)->f64 {
    values.sort_by(|a,b|a.total_cmp(b));
    values[values.len()/2]
}

fn test_decode(label:&str,frame:&[u8],target:usize,rounds:usize,iterations:usize) {
    let expected=baseline::decompress_yaz0(frame).expect("original fixture must decode");
    assert_eq!(expected.len(),target);
    assert_eq!(candidate::decompress_yaz0(frame).expect("candidate must decode"),expected);
    println!("CORRECTNESS: {} {} bytes identical; source={} bytes",label,target,frame.len());
    let mut first=Vec::new();
    let mut second=Vec::new();
    for round in 0..rounds {
        for (which,ref mut samples) in if round % 2 == 0 {
            [(0,&mut first),(1,&mut second)]
        } else {
            [(1,&mut second),(0,&mut first)]
        } {
            let start=Instant::now();
            for _ in 0..iterations {
                let result=if which==0 {
                    baseline::decompress_yaz0(black_box(frame))
                } else {
                    candidate::decompress_yaz0(black_box(frame))
                }.expect("bench decode");
                black_box(result);
            }
            let seconds=start.elapsed().as_secs_f64();
            let mib=(target*iterations) as f64/(1024.0*1024.0);
            samples.push(mib/seconds);
        }
    }
    let a=median(first);
    let b=median(second);
    println!("BENCH_RESULT {} baseline_mib_s={:.3} candidate_mib_s={:.3} ratio={:.5}",label,a,b,b/a);
}
fn main() {
    let bytes=1024*1024;
    println!("BENCHMARK_CONFIG target={} bytes, 11 rounds, 75 iterations, native CPU, optimized",bytes);
    test_decode("literal", &fixture_literal(bytes),bytes,11,75);
    test_decode("repeated", &fixture_repeated(bytes),bytes,11,75);
    test_decode("mixed", &fixture_mixed(bytes),bytes,11,75);
}
