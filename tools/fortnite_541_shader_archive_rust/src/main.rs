mod shader_archive;
mod material_shader_links;
use std::{env,fs::File};
use shader_archive::{ShaderArchiveIndex,embedded_dxbc_range};

fn run()->Result<(),String>{
    let path=env::args().nth(1).ok_or("usage: fortnite-541-shader-archive-proof ORIGINAL_SHADER_ARCHIVE.ushaderbytecode")?;
    let mut file=File::open(&path).map_err(|e|format!("source shader open: {e}"))?;
    let size=file.metadata().map_err(|e|format!("source shader stat: {e}"))?.len();
    let idx=ShaderArchiveIndex::parse(&mut file,0,size)?;
    println!("FORTNITE_NATIVE_RUST_SHADER_TABLE_OK file={} version={} records={} code_start={} stages={:?}",
        path,idx.version,idx.records.len(),idx.code_start,
        (0..=5).map(|s|idx.count_frequency(s)).collect::<Vec<_>>());
    let samples=[0usize,1,idx.records.len()/4,idx.records.len()/2,
        3*idx.records.len()/4,idx.records.len()-1];
    for number in samples{
        let raw=idx.decode_record(&mut file,0,number)?;
        let dxbc=embedded_dxbc_range(&raw);
        println!("FORTNITE_NATIVE_RUST_SHADER_DECODE ordinal={} stage={} raw={} dxbc={:?}",
            number,idx.records[number].frequency,raw.len(),dxbc);
    }
    Ok(())
}
fn main(){
    if let Err(error)=run(){
        eprintln!("FORTNITE_NATIVE_RUST_FAILED: {error}");
        std::process::exit(1);
    }
}
