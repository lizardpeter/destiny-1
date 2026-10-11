//! Independent source-authenticated Fortnite 5.41 TextureCube validator.
//! Mirrors the production Rust importer inline top-mip structure, using
//! metadata only in Git and ephemeral source bytes from the verified R2 PAK.
use std::{env,fs,path::Path};
fn u32at(bytes:&[u8],p:usize)->Result<u32,String>{
    let raw=bytes.get(p..p+4).ok_or("truncated cubemap field")?;
    Ok(u32::from_le_bytes(raw.try_into().unwrap()))
}
fn verify_cube(data:&[u8])->Result<[&[u8];6],String>{
    if u32at(data,28)?!=256||u32at(data,32)?!=256||
        u32at(data,36)?!=6||u32at(data,40)?!=8||
        data.get(44..52)!=Some(b"PF_DXT5\0".as_slice())||
        u32at(data,56)?!=9||u32at(data,60)?!=1||
        u32at(data,64)?!=72||u32at(data,68)?!=393_216||
        u32at(data,72)?!=393_216||u32at(data,76)?!=920||
        data.get(80..92)!=Some([0u8;12].as_slice()) {
        return Err("source cooked BC3 six-face header not verified".into());
    }
    let top=data.get(92..92+393_216).ok_or("truncated original sky source top mip")?;
    Ok(std::array::from_fn(|i|&top[i*65_536..(i+1)*65_536]))
}
#[cfg(test)]
mod tests{
    use super::*;
    #[test]fn exact_six_face_source_bounds(){
        let mut data=vec![0u8;92+393_216];
        for (p,v) in [(28,256u32),(32,256),(36,6),(40,8),(56,9),(60,1),(64,72),(68,393_216),(72,393_216),(76,920)]{
            data[p..p+4].copy_from_slice(&v.to_le_bytes());
        }
        data[44..52].copy_from_slice(b"PF_DXT5\0");
        for i in 0..6{data[92+i*65_536..92+(i+1)*65_536].fill(i as u8);}
        let faces=verify_cube(&data).unwrap();
        for (i,face) in faces.iter().enumerate(){
            assert_eq!(face.len(),65_536);
            assert!(face.iter().all(|x|*x==i as u8));
        }
        data[40..44].fill(0);
        assert!(verify_cube(&data).is_err());
    }
}
fn main(){
    let p=env::args().nth(1).unwrap_or_default();
    if p.is_empty(){eprintln!("usage: fortnite-541-sky-cube-proof /tmp/verified_original_cooked.bin");std::process::exit(2);}
    let raw=fs::read(Path::new(&p)).expect("SHA1-verified original cooked sky source unavailable");
    let faces=verify_cube(&raw).expect("original sky source cube failed exact Rust layout verification");
    let mut unique=std::collections::BTreeSet::new();
    for (i,face) in faces.iter().enumerate(){
        let digest=face.chunks_exact(256).fold(0u64,|s,chunk|
            s.wrapping_add(chunk.iter().map(|v|*v as u64).sum::<u64>()));
        println!("FORTNITE_ORIGINAL_SKY_RUST_CUBE_FACE source_face={} source_bc3_bytes={} byte_sum={}",i,face.len(),digest);
        unique.insert(digest);
    }
    assert_eq!(unique.len(),6,"all six original sky faces must differ");
    println!("FORTNITE_ORIGINAL_SKY_RUST_SOURCE_OK faces=6 face_size=256 compression=BC3 mip0_bytes=393216 inline=true");
}
