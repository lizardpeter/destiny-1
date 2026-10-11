//! UE4.21 FShaderCodeLibrary .ushaderbytecode V1 decoder.
//!
//! Independently established from the authenticated original Fortnite 5.41
//! PCD3D_SM5 archives, not from arbitrary DXBC magic scans:
//!   u32 version=1, u32 count, count * 37 bytes of
//!   [FSHAHash:20, code_offset:u64, compressed:u32, raw:u32, frequency:u8],
//!   followed immediately by a contiguous zlib-compressed code stream.
//!
//! Bytecode often includes UE4 shader-parameter binding information BEFORE
//! the embedded DXBC. Retain all these bytes for the future exact resource ABI.
use std::{
    collections::BTreeSet,
    io::{Read,Seek,SeekFrom},
};

const RECORD_BYTES:usize=37;
const MAX_SHADERS:usize=200_000;
const MAX_ARCHIVE_BYTES:u64=512*1024*1024;
const MAX_COMPRESSED_CODE:usize=2*1024*1024;
const MAX_UNCOMPRESSED_CODE:usize=4*1024*1024;

#[derive(Debug,Clone,Copy,PartialEq,Eq)]
pub struct ShaderCodeRecord{
    /// Authored FShaderCode entry identity. This is NOT automatically a
    /// SHA-1 of the entire decompressed UE parameter-map + DXBC byte stream.
    pub hash:[u8;20],
    pub code_offset:u64,
    pub compressed_bytes:u32,
    pub uncompressed_bytes:u32,
    /// Unreal EShaderFrequency: Vertex=0,Hull=1,Domain=2,Pixel=3,
    /// Geometry=4,Compute=5. No renderer-stage shortcuts are inferred.
    pub frequency:u8,
}
#[derive(Debug,Clone)]
pub struct ShaderArchiveIndex{
    pub version:u32,
    pub archive_bytes:u64,
    /// Offset of shader code data relative to the beginning of the archive.
    pub code_start:u64,
    pub records:Vec<ShaderCodeRecord>,
}
fn err(msg:impl Into<String>)->String{msg.into()}
fn le32(raw:&[u8])->u32{u32::from_le_bytes(raw.try_into().expect("checked span"))}
fn le64(raw:&[u8])->u64{u64::from_le_bytes(raw.try_into().expect("checked span"))}
impl ShaderArchiveIndex{
    /// The archive may be a standalone original .ushaderbytecode file OR an
    /// authenticated FPakEntry payload inside a larger PAK file. The latter
    /// supplies `archive_start` (absolute source file offset) and length.
    pub fn parse<R:Read+Seek>(
        reader:&mut R,archive_start:u64,archive_bytes:u64,
    )->Result<Self,String>{
        if archive_bytes<8 ||archive_bytes>MAX_ARCHIVE_BYTES{
            return Err(err("UE4 shader archive outside bounded 8..512 MiB envelope"));
        }
        reader.seek(SeekFrom::Start(archive_start))
            .map_err(|e|format!("seek UE4 shader archive: {e}"))?;
        let mut header=[0u8;8];
        reader.read_exact(&mut header)
            .map_err(|e|format!("read UE4 shader archive header: {e}"))?;
        let version=le32(&header[0..4]);
        let count=le32(&header[4..8]) as usize;
        if version!=1 ||count==0 ||count>MAX_SHADERS {
            return Err(format!("unsupported UE4 source shader code library version={version} entries={count}"));
        }
        let table_bytes=count.checked_mul(RECORD_BYTES)
            .ok_or("UE4 shader archive index size overflow")?;
        let code_start=(8usize).checked_add(table_bytes)
            .ok_or("UE4 shader archive header size overflow")? as u64;
        if code_start>=archive_bytes{
            return Err(format!("UE4 shader index spans {code_start} of {archive_bytes} source bytes"));
        }
        let mut table=vec![0u8;table_bytes];
        reader.read_exact(&mut table)
            .map_err(|e|format!("read UE4 original shader code records: {e}"))?;
        let mut records=Vec::with_capacity(count);
        let mut identities=BTreeSet::new();
        let mut next_code=0u64;
        for (ordinal,src) in table.chunks_exact(RECORD_BYTES).enumerate(){
            let hash:[u8;20]=src[..20].try_into().unwrap();
            let code_offset=le64(&src[20..28]);
            let compressed_bytes=le32(&src[28..32]);
            let uncompressed_bytes=le32(&src[32..36]);
            let frequency=src[36];
            if !identities.insert(hash) {
                return Err(format!("duplicate original UE4 shader hash at #{ordinal}"));
            }
            if frequency>5 ||compressed_bytes==0 ||uncompressed_bytes==0
                ||compressed_bytes as usize>MAX_COMPRESSED_CODE
                ||uncompressed_bytes as usize>MAX_UNCOMPRESSED_CODE{
                return Err(format!("invalid source UE4 shader stage/byte lengths at #{ordinal}"));
            }
            if code_offset!=next_code {
                return Err(format!(
                    "UE4 source shader code gap/overlap at #{ordinal}: offset={code_offset}, expected={next_code}"
                ));
            }
            next_code=next_code.checked_add(compressed_bytes as u64)
                .ok_or("UE4 source code offset overflow")?;
            if code_start.checked_add(next_code).is_none_or(|end|end>archive_bytes) {
                return Err(format!("UE4 source shader #{ordinal} escapes authenticated archive"));
            }
            records.push(ShaderCodeRecord{
                hash,code_offset,compressed_bytes,uncompressed_bytes,frequency,
            });
        }
        if code_start+next_code!=archive_bytes{
            return Err(format!(
                "UE4 source shader data does not cover archive: ending={} expected={archive_bytes}",
                code_start+next_code
            ));
        }
        Ok(Self{version,archive_bytes,code_start,records})
    }

    /// Decode ONE source shader by exact source record, with a hard ceiling.
    /// No shader code is executed; return its original UE parameter-map
    /// prefix and DXBC bytes unchanged for later IR translation.
    pub fn decode_record<R:Read+Seek>(
        &self,reader:&mut R,archive_start:u64,ordinal:usize
    )->Result<Vec<u8>,String>{
        let record=self.records.get(ordinal)
            .ok_or_else(||format!("original UE4 shader index {ordinal} out of bounds"))?;
        let start=archive_start.checked_add(self.code_start)
            .and_then(|s|s.checked_add(record.code_offset))
            .ok_or("UE4 shader record source offset overflow")?;
        reader.seek(SeekFrom::Start(start))
            .map_err(|e|format!("seek original UE4 shader #{ordinal}: {e}"))?;
        let mut compressed=vec![0u8;record.compressed_bytes as usize];
        reader.read_exact(&mut compressed)
            .map_err(|e|format!("read original UE4 shader #{ordinal}: {e}"))?;
        let decoder=flate2::read::ZlibDecoder::new(&compressed[..]);
        let mut capped=decoder.take(record.uncompressed_bytes as u64+1);
        let mut raw=Vec::with_capacity(record.uncompressed_bytes as usize);
        capped.read_to_end(&mut raw)
            .map_err(|e|format!("decompress original UE4 shader #{ordinal}: {e}"))?;
        if raw.len()!=record.uncompressed_bytes as usize {
            return Err(format!(
                "original UE4 shader #{ordinal} expands to {} bytes, expected {}",
                raw.len(),record.uncompressed_bytes
            ));
        }
        Ok(raw)
    }

    pub fn count_frequency(&self,frequency:u8)->usize{
        self.records.iter().filter(|r|r.frequency==frequency).count()
    }
}

/// A checked embedded original SM4/SM5 DXBC container. UE's coded stream may
/// begin with a source parameter-map prelude; do NOT discard it when binding
/// the eventual exact shader resource descriptors.
pub fn embedded_dxbc_range(original_shader:&[u8])->Option<std::ops::Range<usize>>{
    let mut offset=0usize;
    while offset+32<=original_shader.len(){
        if &original_shader[offset..offset+4]!=b"DXBC"{
            offset+=1;continue;
        }
        let total=le32(&original_shader[offset+24..offset+28]) as usize;
        let chunk_count=le32(&original_shader[offset+28..offset+32]) as usize;
        let table_end=32usize.checked_add(chunk_count.checked_mul(4)?)?;
        if !(32..=MAX_UNCOMPRESSED_CODE).contains(&total)
            ||chunk_count==0 ||chunk_count>256
            ||table_end>total ||total>original_shader.len()-offset {
            offset+=1;continue;
        }
        let bytes=&original_shader[offset..offset+total];
        let mut valid=true;
        for chunk in 0..chunk_count{
            let at=32+chunk*4;
            let pos=le32(&bytes[at..at+4]) as usize;
            if pos.checked_add(8).is_none_or(|end|end>total){
                valid=false;break;
            }
            let size=le32(&bytes[pos+4..pos+8]) as usize;
            if pos.checked_add(8).and_then(|p|p.checked_add(size))
                .is_none_or(|end|end>total){
                valid=false;break;
            }
        }
        if valid{return Some(offset..offset+total);}
        offset+=1;
    }
    None
}

#[cfg(test)]
mod tests{
    use super::*;
    use std::io::{Cursor,Write};
    use flate2::{Compression,write::ZlibEncoder};
    fn encoded(source:&[u8])->Vec<u8>{
        let mut encoder=ZlibEncoder::new(Vec::new(),Compression::default());
        encoder.write_all(source).unwrap();
        encoder.finish().unwrap()
    }
    fn example(codes:&[(&[u8],u8)])->Vec<u8>{
        let mut bytes=Vec::new();
        bytes.extend_from_slice(&1u32.to_le_bytes());
        bytes.extend_from_slice(&(codes.len() as u32).to_le_bytes());
        let mut offset=0u64;
        let mut payload=Vec::new();
        for (i,(code,stage)) in codes.iter().enumerate(){
            let zipped=encoded(code);
            bytes.extend_from_slice(&[(i+1) as u8;20]);
            bytes.extend_from_slice(&offset.to_le_bytes());
            bytes.extend_from_slice(&(zipped.len() as u32).to_le_bytes());
            bytes.extend_from_slice(&(code.len() as u32).to_le_bytes());
            bytes.push(*stage);
            offset+=zipped.len() as u64;
            payload.extend_from_slice(&zipped);
        }
        bytes.extend_from_slice(&payload);
        bytes
    }
    #[test] fn ue_shader_library_v1_parses_unambiguous_packed_index(){
        let bytes=example(&[(b"VERTEX-0",0),(b"PIXEL-3",3),(b"COMPUTE-5",5)]);
        let mut input=Cursor::new(&bytes);
        let catalog=ShaderArchiveIndex::parse(&mut input,0,bytes.len() as u64).unwrap();
        assert_eq!(catalog.code_start,8+37*3);
        assert_eq!(catalog.records.len(),3);
        assert_eq!(catalog.count_frequency(3),1);
        assert_eq!(catalog.decode_record(&mut input,0,1).unwrap(),b"PIXEL-3");
        assert!(catalog.decode_record(&mut input,0,3).is_err());
    }
    #[test] fn packet_offset_is_part_of_archive_identity(){
        let original=example(&[(b"PIXEL",3)]);
        let mut padded=vec![0xAA;93];
        padded.extend_from_slice(&original);
        let mut input=Cursor::new(&padded);
        let catalog=ShaderArchiveIndex::parse(&mut input,93,original.len() as u64).unwrap();
        assert_eq!(catalog.decode_record(&mut input,93,0).unwrap(),b"PIXEL");
    }
    #[test] fn reject_corrupt_shader_bounds_stages_and_hash_repeats(){
        let mut bytes=example(&[(b"PS",3),(b"VS",0)]);
        let mut input=Cursor::new(&bytes);
        assert!(ShaderArchiveIndex::parse(&mut input,0,(bytes.len()-1) as u64).is_err());
        bytes[8+37+36]=6;
        assert!(ShaderArchiveIndex::parse(&mut Cursor::new(&bytes),0,bytes.len() as u64).is_err());
        bytes[8+37+36]=0;
        bytes[8+37..8+37+20].fill(1);
        assert!(ShaderArchiveIndex::parse(&mut Cursor::new(&bytes),0,bytes.len() as u64).is_err());
    }
    #[test] fn decode_ue_prefix_without_discarding_it(){
        let raw=b"UE4 header before DXBC must be retained, not forged";
        let archive=example(&[(raw,3)]);
        let mut input=Cursor::new(&archive);
        let index=ShaderArchiveIndex::parse(&mut input,0,archive.len() as u64).unwrap();
        assert_eq!(index.decode_record(&mut input,0,0).unwrap(),raw);
        assert!(embedded_dxbc_range(raw).is_none());
    }
}
