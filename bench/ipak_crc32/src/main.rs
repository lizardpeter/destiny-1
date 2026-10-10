use std::{hint::black_box, time::Instant};

const POLYNOMIAL: u32 = 0xedb8_8320;
const fn make_table() -> [u32; 256] {
    let mut values = [0u32; 256];
    let mut i = 0usize;
    while i < 256 {
        let mut crc = i as u32;
        let mut bit = 0;
        while bit < 8 {
            let mask = (crc & 1).wrapping_neg();
            crc = (crc >> 1) ^ (POLYNOMIAL & mask);
            bit += 1;
        }
        values[i] = crc;
        i += 1;
    }
    values
}
static CRC32_TABLE: [u32; 256] = make_table();

#[inline]
fn original_crc32(bytes: &[u8]) -> u32 {
    let mut crc = !0u32;
    for &byte in bytes {
        let index = ((crc as u8) ^ byte) as usize;
        crc = (crc >> 8) ^ CRC32_TABLE[index];
    }
    !crc
}

fn fill(size: usize, pattern: usize) -> Vec<u8> {
    let mut v = Vec::with_capacity(size + 11);
    let mut x=0x9e37_79b9u32;
    for i in 0..size+11 {
        x^=x<<13; x^=x>>17; x^=x<<5;
        v.push(match pattern {
            0 => x as u8,
            1 => if i % 64 < 52 {0x42} else { x as u8 },
            2 => 0,
            _ => (i & 255) as u8,
        });
    }
    v
}

#[test]
fn correct_vectors_masks_and_unaligned_slices() {
    assert_eq!(original_crc32(b""), 0);
    assert_eq!(original_crc32(b"123456789"), 0xcbf4_3926);
    assert_eq!(original_crc32(b"The quick brown fox jumps over the lazy dog"), 0x414f_a339);
    for pattern in 0..4 {
        for size in [0,1,2,3,4,7,8,15,16,31,32,64,127,128,256,257,1024,4096,8192,32768,65536,262144,1048576] {
            let v=fill(size,pattern);
            for offset in [0,1,3,7,11] {
                let buf=&v[offset..offset+size];
                let reference=original_crc32(buf);
                assert_eq!(reference,crc32fast::hash(buf),"size={size} pattern={pattern} offset={offset}");
                assert_eq!(reference&0x1fff_ffff,crc32fast::hash(buf)&0x1fff_ffff);
                let mut h=crc32fast::Hasher::new();
                for chunk in buf.chunks(31) {h.update(chunk);}
                assert_eq!(reference,h.finalize(),"chunked size={size} pattern={pattern}");
            }
        }
    }
}

fn main() {
    // A/B alternating order protects against OS jitter. Separate timings for
    // each payload, exact equality prior to benchmark and in each pass.
    for (size,repetitions,pattern) in [
        (64usize,50000usize,0usize),
        (512,30000,0),
        (4096,7000,0),
        (32768,900,0),
        (262144,140,0),
        (1048576,36,0),
        (262144,140,1),
        (1048576,36,2),
    ] {
        let v=fill(size,pattern);
        let input=&v[7..7+size];
        assert_eq!(original_crc32(input),crc32fast::hash(input));
        let mut rounds=Vec::<f64>::new();
        for round in 0..11 {
            let mut times=[0f64;2];
            for step in 0..2 {
                let optimized=(round+step)%2==0;
                let started=Instant::now();
                let mut accumulator=0u64;
                for _ in 0..repetitions {
                    let val=if optimized {
                        crc32fast::hash(black_box(input))
                    }else{
                        original_crc32(black_box(input))
                    };
                    accumulator=accumulator.wrapping_add(black_box(val) as u64);
                }
                black_box(accumulator);
                times[usize::from(optimized)]=started.elapsed().as_secs_f64();
            }
            rounds.push(times[0]/times[1]);
        }
        rounds.sort_by(f64::total_cmp);
        println!("IPAK_CRC32_AB size={size} profile={pattern} iterations={repetitions} median={:.4}x min={:.4}x max={:.4}x",rounds[5],rounds[0],rounds[10]);
    }
}
