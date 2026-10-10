use std::{hint::black_box, time::Instant};
mod baseline; mod optimized;
#[derive(Clone,Copy)] enum Tok{Lit(u8),Match{distance:usize,length:usize}}
fn frame(tokens:&[Tok], size:usize)->Vec<u8>{
 let mut out=b"Yaz0".to_vec();
 out.extend_from_slice(&(size as u32).to_be_bytes());
 out.extend_from_slice(&[0;8]);
 for group in tokens.chunks(8) {
  let mut control=0u8;
  for (i,t) in group.iter().enumerate(){if matches!(t,Tok::Lit(_)){control|=1<<(7-i)}}
  out.push(control);
  for token in group{
    match *token{
      Tok::Lit(x)=>out.push(x),
      Tok::Match{distance,length}=>{
        assert!((1..=4096).contains(&distance)&&(3..=273).contains(&length));
        let d=distance-1;
        if length>=18{
          out.extend_from_slice(&[((d>>8)&15) as u8,d as u8,(length-18) as u8]);
        }else{
          out.extend_from_slice(&[(((length-2)<<4)|((d>>8)&15)) as u8,d as u8]);
        }
      }
    }
  }
 }
 out
}
fn fixture(bytes:usize,distance:usize)->Vec<u8>{
 let mut tokens=Vec::new();
 for i in 0..distance{tokens.push(Tok::Lit((i as u8).wrapping_mul(53).wrapping_add(13)));}
 let mut position=distance;
 while position<bytes{
    let rem=bytes-position;
    if rem>=3 {
        let len=rem.min(273);
        tokens.push(Tok::Match{distance,length:len});
        position+=len;
    } else {
        for i in 0..rem {tokens.push(Tok::Lit(i as u8));}
        position=bytes;
    }
 }
 frame(&tokens,bytes)
}
fn parity(){
 for distance in [1usize,2,3,4,16,64,255,4096]{
  for size in [0,1,2,3,17,18,273,274,512,4096,32768] {
   if size<distance{continue}
   let data=fixture(size,distance);
   assert_eq!(baseline::decompress_yaz0(&data),optimized::decompress_yaz0(&data),"distance={distance} len={size}");
  }
 }
 for distance in [1,2,4]{
  for size in [256usize,4096,32768]{
   let data=fixture(size,distance);
   for trim in 1..=5.min(data.len()-16){
    let corrupted=&data[..data.len()-trim];
    assert_eq!(baseline::decompress_yaz0(corrupted),optimized::decompress_yaz0(corrupted));
   }
  }
 }
 println!("PASS: exact Yaz0 byte/error parity across 8 distances, lengths, truncations");
}
fn bench(){
 for distance in [1usize,2,4,64]{
  for size in [4096usize,32768,262144,1048576]{
   let input=fixture(size,distance);
   let a=baseline::decompress_yaz0(&input).unwrap();
   let b=optimized::decompress_yaz0(&input).unwrap();
   assert_eq!(a,b);
   let iters= if size<32768 {160} else if size<262144{50} else if size<1048576{12}else{4};
   let old=||{let start=Instant::now();for _ in 0..iters{let x=baseline::decompress_yaz0(black_box(&input)).unwrap();black_box(x);}start.elapsed().as_secs_f64()};
   let new=||{let start=Instant::now();for _ in 0..iters{let x=optimized::decompress_yaz0(black_box(&input)).unwrap();black_box(x);}start.elapsed().as_secs_f64()};
   let (mut olds,mut news)=(Vec::new(),Vec::new());
   for round in 0..11{let(a,b)=if round%2==0{(old(),new())}else{let b=new();(old(),b)};olds.push(a);news.push(b);}
   olds.sort_by(f64::total_cmp);news.sort_by(f64::total_cmp);
   println!("distance={distance} size={size} old_ms={:.5} opt_ms={:.5} speedup={:.3}x",olds[5]*1000.,news[5]*1000.,olds[5]/news[5]);
  }
 }
}
fn main(){parity();bench()}
