use std::{hint::black_box, time::Instant};
const BLOCK: &[u8] = &[34, 104, 101, 108, 108, 111, 44, 32, 108, 122, 111, 32, 119, 111, 114, 108, 100, 33, 17, 0, 0];
const MAX_OUTPUT: usize = 0x8000;

fn legacy(block: &[u8], output: &mut Vec<u8>) -> Result<(), lzo::Error> {
    let decoded = lzo::decompress(block, MAX_OUTPUT)?;
    output.extend_from_slice(&decoded);
    Ok(())
}
fn scratch(block: &[u8], output: &mut Vec<u8>, workspace: &mut [u8; MAX_OUTPUT]) -> Result<(), lzo::Error> {
    let n = lzo::decompress_into(block, workspace)?;
    output.extend_from_slice(&workspace[..n]);
    Ok(())
}
#[test]
fn exact_reference_block() {
    let mut old = Vec::new();
    let mut new = Vec::new();
    let mut workspace = [0u8; MAX_OUTPUT];
    for _ in 0..100 {
        legacy(BLOCK, &mut old).unwrap();
        scratch(BLOCK, &mut new, &mut workspace).unwrap();
        assert_eq!(old, new);
    }
    assert_eq!(&old[..17], b"hello, lzo world!");
}
#[test]
fn malformed_block_still_rejected() {
    let mut out = Vec::new();
    let mut workspace = [0u8; MAX_OUTPUT];
    assert!(legacy(&BLOCK[..3], &mut out).is_err());
    assert!(scratch(&BLOCK[..3], &mut out, &mut workspace).is_err());
}
fn main() {
    let mut output = Vec::with_capacity(32768);
    let mut workspace = [0u8; MAX_OUTPUT];
    let mut values=Vec::new();
    for round in 0..9 {
        let mut mib_per_second=[0f64;2];
        for phase in 0..2 {
            let use_scratch=(phase==0)==(round%2==0);
            let t=Instant::now();
            let n=1_000_000usize;
            for _ in 0..n {
                output.clear();
                if use_scratch {scratch(black_box(BLOCK),&mut output,&mut workspace).unwrap();}
                else {legacy(black_box(BLOCK),&mut output).unwrap();}
                black_box(&output);
            }
            mib_per_second[usize::from(use_scratch)]=(n*17) as f64/(1024.0*1024.0)/t.elapsed().as_secs_f64();
        }
        values.push(mib_per_second);
    }
    let mut ratios=values.iter().map(|r|r[1]/r[0]).collect::<Vec<_>>();
    ratios.sort_by(|a,b|a.total_cmp(b));
    println!("T6_IPAK_LZO_BLOCK_BENCH block_decoded_bytes=17 rounds=9 paired_median_speedup={:.3}x baseline_mib_s={:.2} scratch_mib_s={:.2}",
        ratios[ratios.len()/2],
        values.iter().map(|r|r[0]).sum::<f64>()/values.len() as f64,
        values.iter().map(|r|r[1]).sum::<f64>()/values.len() as f64);
}