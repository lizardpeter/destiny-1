use lzxd::{Lzxd, WindowSize};
use lzxd_fast::Lzxd as FastLzxd;

/// Valid independent LZXD record with one uncompressed block. Header is
/// MSB-first within little-endian words: first-chunk 0, block kind 0b011,
/// 24-bit block length. Then three u32 repeated distances (all 1) and data.
pub fn uncompressed_frame(payload: &[u8]) -> Vec<u8> {
    assert!(!payload.is_empty() && payload.len() <= 32768);
    let size = payload.len() as u32;
    let mut data = Vec::with_capacity(16 + payload.len() + 2);
    let first = (3u16 << 12) | ((size >> 12) as u16);
    let second = ((size & 0xfff) as u16) << 4;
    data.extend_from_slice(&first.to_le_bytes());
    data.extend_from_slice(&second.to_le_bytes());
    for _ in 0..3 { data.extend_from_slice(&1u32.to_le_bytes()); }
    data.extend_from_slice(payload);
    data
}
pub fn seeded_payload(size: usize, seed: u32) -> Vec<u8> {
    let mut state=seed;
    (0..size).map(|_| {
        state^=state<<13; state^=state>>17; state^=state<<5;
        state as u8
    }).collect()
}
pub fn fresh(frame: &[u8], n:usize)->Result<Vec<u8>,String>{
    Lzxd::new(WindowSize::KB32).decompress_next(frame,n)
        .map(|b|b.to_vec()).map_err(|e|e.to_string())
}
pub fn reusable(frame: &[u8], n:usize, decoder:&mut FastLzxd)->Result<Vec<u8>,String>{
    decoder.reset_reuse();
    decoder.decompress_next(frame,n)
        .map(|b|b.to_vec()).map_err(|e|e.to_string())
}
#[test]
fn frames_are_valid_and_match_known_payloads(){
    for len in [1usize,2,3,4,15,16,17,128,1023,4096,32767,32768] {
        let src=seeded_payload(len,len as u32 + 1);
        let frame=uncompressed_frame(&src);
        assert_eq!(fresh(&frame,len).unwrap(),src,"size {len}");
        let mut fast=FastLzxd::new(lzxd_fast::WindowSize::KB32);
        assert_eq!(reusable(&frame,len,&mut fast).unwrap(),src,"size {len}");
    }
}
#[test]
fn independent_records_match_original_after_reset(){
    let mut decoder=FastLzxd::new(lzxd_fast::WindowSize::KB32);
    for i in 0..200 {
        let n=[3usize,32,256,32768,1,32767][i%6];
        let frame=uncompressed_frame(&seeded_payload(n,i as u32 + 456));
        let expected=fresh(&frame,n).unwrap();
        assert_eq!(reusable(&frame,n,&mut decoder).unwrap(),expected,"record {i}");
    }
}
#[test]
fn malformed_record_failure_and_reset_recovery(){
    let mut decoder=FastLzxd::new(lzxd_fast::WindowSize::KB32);
    let valid=uncompressed_frame(&seeded_payload(4096,9));
    let mut broken=valid.clone();
    broken.truncate(broken.len()-10);
    assert_eq!(reusable(&broken,4096,&mut decoder),fresh(&broken,4096));
    assert_eq!(reusable(&valid,4096,&mut decoder),fresh(&valid,4096));
}
