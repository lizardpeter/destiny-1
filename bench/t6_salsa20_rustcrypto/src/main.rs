use std::{hint::black_box,time::Instant};
use salsa20::cipher::{KeyIvInit,StreamCipher};
mod original;
fn new_xor(ciphertext:&[u8],key:&[u8;32],nonce:&[u8;8],output:&mut Vec<u8>){
 output.clear(); output.extend_from_slice(ciphertext);
 let mut cipher=salsa20::Salsa20::new_from_slices(key,nonce).unwrap();
 cipher.apply_keystream(output);
}
fn dataset(n:usize,profile:usize)->Vec<u8>{
 let mut state=0x1234_5678u32;
 (0..n).map(|i|{state^=state<<13;state^=state>>17;state^=state<<5;
  match profile {0=>(state>>8) as u8,1=>(i&7)as u8,_=>0}}).collect()
}
fn compare(){
 for len in [0,1,2,3,15,31,63,64,65,127,128,129,255,256,511,512,513,4095,4096,32768]{
  for seed in [0u8,1,37,99,255]{
   let key: [u8;32]=std::array::from_fn(|i|(i as u8).wrapping_mul(seed).wrapping_add(27));
   let nonce: [u8;8]=std::array::from_fn(|i|seed.wrapping_add(i as u8*5));
   let plaintext=dataset(len,0);
   let state=original::salsa20_key_state(&key);
   let mut old=Vec::new();let mut optimized=Vec::new();
   original::salsa20_xor_into(&plaintext,&state,&nonce,&mut old);
   new_xor(&plaintext,&key,&nonce,&mut optimized);
   assert_eq!(old,optimized,"key seed {seed} len {len}");
   new_xor(&optimized,&key,&nonce,&mut old);
   assert_eq!(old,plaintext,"round-trip {seed} {len}");
  }
 }
 println!("PASS: RustCrypto Salsa20 20-round exact plaintext, nonce, length and round-trip parity");
}
fn bench(){
 let key: [u8;32]=std::array::from_fn(|i|(i as u8).wrapping_mul(13));
 let state=original::salsa20_key_state(&key);
 for profile in [0usize,1]{
  for len in [64usize,512,4096,32768]{
   let payload=dataset(len,profile);
   let records=if len<4096{2048}else if len==4096{640}else{160};
   let old=||{
    let mut output=Vec::new(); let start=Instant::now(); let mut acc=0;
    for i in 0..records {let nonce=(i as u64).wrapping_mul(0x9e3779b97f4a7c15).to_le_bytes();
      original::salsa20_xor_into(black_box(&payload),&state,&nonce,&mut output);
      acc^=output[0];}
    black_box(acc);start.elapsed().as_secs_f64()
   };
   let new=||{
    let mut output=Vec::new(); let start=Instant::now(); let mut acc=0;
    for i in 0..records{let nonce=(i as u64).wrapping_mul(0x9e3779b97f4a7c15).to_le_bytes();
      new_xor(black_box(&payload),&key,&nonce,&mut output);
      acc^=output[0];}
    black_box(acc);start.elapsed().as_secs_f64()
   };
   let(mut originals,mut candidates)=(Vec::new(),Vec::new());
   for round in 0..11{let(a,b)=if round%2==0{(old(),new())}else{let b=new();(old(),b)};
    originals.push(a);candidates.push(b);}
   originals.sort_by(f64::total_cmp);candidates.sort_by(f64::total_cmp);
   println!("profile={profile} bytes={len} records={records} baseline_ms={:.3} rustcrypto_ms={:.3} ratio={:.3}x",
     originals[5]*1000.,candidates[5]*1000.,originals[5]/candidates[5]);
  }
 }
}
fn main(){compare();bench();}
