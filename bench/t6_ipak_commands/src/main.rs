use std::{hint::black_box,time::Instant};

const BLOCK:usize=128;
const MAX:usize=31;
const KIND_RAW:u8=0;
const KIND_SKIP:u8=0xcf;

#[derive(Clone,Copy)]
enum Strategy{Heap,Stack}
fn decode_block(header:&[u8],payload:&[u8],strategy:Strategy)->Result<Vec<u8>,String>{
    let first=u32::from_le_bytes(header[0..4].try_into().unwrap());
    let count=(first>>24) as usize;
    if count>MAX {return Err("invalid command count".into());}
    let mut output=Vec::new();
    let mut bytes=0usize;
    match strategy {
        Strategy::Heap=>{
            let mut commands=Vec::with_capacity(count);
            for i in 0..count {
                let base=4+i*4;
                let word=u32::from_le_bytes(header[base..base+4].try_into().unwrap());
                let size=(word&0x00ff_ffff) as usize;
                let kind=(word>>24) as u8;
                bytes=bytes.checked_add(size).ok_or("sum overflow")?;
                commands.push((size,kind));
            }
            if bytes>payload.len(){return Err("invalid payload".into());}
            let mut pos=0usize;
            for (size,kind) in commands {
                match kind {
                    KIND_RAW=>output.extend_from_slice(&payload[pos..pos+size]),
                    KIND_SKIP=>{},
                    _=>return Err("unsupported".into()),
                }
                pos+=size;
            }
        }
        Strategy::Stack=>{
            let mut commands=[(0usize,0u8);MAX];
            for i in 0..count {
                let base=4+i*4;
                let word=u32::from_le_bytes(header[base..base+4].try_into().unwrap());
                let size=(word&0x00ff_ffff) as usize;
                let kind=(word>>24) as u8;
                bytes=bytes.checked_add(size).ok_or("sum overflow")?;
                commands[i]=(size,kind);
            }
            if bytes>payload.len(){return Err("invalid payload".into());}
            let mut pos=0usize;
            for (size,kind) in commands.into_iter().take(count) {
                match kind {
                    KIND_RAW=>output.extend_from_slice(&payload[pos..pos+size]),
                    KIND_SKIP=>{},
                    _=>return Err("unsupported".into()),
                }
                pos+=size;
            }
        }
    }
    Ok(output)
}
fn case(count:usize,kind:usize)->(Vec<u8>,Vec<u8>,Vec<u8>){
    let mut header=vec![0u8;BLOCK];
    header[0..4].copy_from_slice(&((count as u32)<<24).to_le_bytes());
    let mut payload=Vec::new();
    let mut expected=Vec::new();
    for i in 0..count {
        let skip=kind==1 && (i%3==1);
        let n=if kind==2 {96+i%10} else {8+i%7};
        let k=if skip{KIND_SKIP}else{KIND_RAW};
        header[4+i*4..8+i*4].copy_from_slice(&(((k as u32)<<24)|(n as u32)).to_le_bytes());
        for j in 0..n {
            let v=((i*23+j*17)&255) as u8;
            payload.push(v);
            if !skip {expected.push(v);}
        }
    }
    (header,payload,expected)
}
#[test]
fn validates_output_and_malformed_frames(){
    for count in [0usize,1,2,3,8,15,30,31]{
        for kind in [0usize,1,2]{
            let (header,payload,expected)=case(count,kind);
            assert_eq!(decode_block(&header,&payload,Strategy::Heap).unwrap(),expected);
            assert_eq!(decode_block(&header,&payload,Strategy::Stack).unwrap(),expected);
            let mut too_short=payload.clone();
            if too_short.len()>0 {
                too_short.pop();
                assert_eq!(decode_block(&header,&too_short,Strategy::Heap).is_err(),
                           decode_block(&header,&too_short,Strategy::Stack).is_err());
            }
        }
    }
    let mut bad=vec![0u8;128];
    bad[0..4].copy_from_slice(&(32u32<<24).to_le_bytes());
    assert!(decode_block(&bad,&[],Strategy::Heap).is_err());
    assert!(decode_block(&bad,&[],Strategy::Stack).is_err());
}
fn main(){
    for (count,kind,reps) in [(1,0,50000usize),(4,0,40000),(12,0,35000),(31,0,24000),(31,1,24000),(31,2,20000)] {
        let (header,payload,expected)=case(count,kind);
        let a=decode_block(&header,&payload,Strategy::Heap).unwrap();
        let b=decode_block(&header,&payload,Strategy::Stack).unwrap();
        assert_eq!(a,b);assert_eq!(a,expected);
        let mut ratios=Vec::<f64>::new();
        for round in 0..11 {
            let mut secs=[0.0f64;2];
            for step in 0..2 {
                let stack=(round+step)%2==0;
                let start=Instant::now();
                let mut total=0usize;
                for _ in 0..reps {
                    let output=decode_block(black_box(&header),black_box(&payload),if stack{Strategy::Stack}else{Strategy::Heap}).unwrap();
                    total=total.wrapping_add(output.len());
                    black_box(output);
                }
                black_box(total);
                secs[usize::from(stack)]=start.elapsed().as_secs_f64();
            }
            ratios.push(secs[0]/secs[1]);
        }
        ratios.sort_by(f64::total_cmp);
        println!("IPAK_COMMAND_AB count={count} profile={kind} reps={reps} ratio={:.4}x low={:.4}x high={:.4}x",ratios[5],ratios[0],ratios[10]);
    }
}
