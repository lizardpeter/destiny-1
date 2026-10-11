//! Retail SHA1-authenticated POI world and detailed static-mesh extraction.
//! Local original PAKs only; split s3 has different mount path conventions.
//! This is pre-game import, never inside the GPU submission/frame scheduler.
use crate::{extract,pak::{self,IndexStatus,PakEntry}};
use sha1::{Digest,Sha1};
use std::{collections::BTreeSet,env,fs,io::Write,path::{Path,Component}};
const MAIN:&str="fd1f4623c812f5fff47298f99cc3d0d8f2d0f11b";
const SPLIT_S3:&str="27376dab8f8a3488d0d2b5332a2a2da7d28fd73e";
const HISTORICAL_KEY:&str="81C42E03B21760A5C457C8DB7D52BA066F0633D0891FD9E37CF118F27687924A";
const MAX_REQUESTED_PACKAGES:usize=2048;
const MAX_NEW_SOURCE_BYTES:u64=512*1024*1024;
#[derive(Debug,Clone,Default)]
pub struct PreparedPoiSource{
    pub requested:usize,
    pub available:usize,
    pub unavailable:usize,
    pub verified_files:usize,
    pub extracted_files:usize,
    pub new_bytes:u64,
}
#[derive(Debug,Clone,Copy,PartialEq,Eq)]
pub enum SourceChunk{Main,S3,MainBlueprint}
fn authenticated_source_key()->Result<[u8;32],String>{
    extract::parse_aes_key(&env::var("RUST_TEST_FORTNITE_541_AES_KEY")
        .unwrap_or_else(|_|HISTORICAL_KEY.to_owned()))
}
fn validate_package(path:&str,chunk:SourceChunk)->Result<(),String>{
    let valid_root=match chunk{
        SourceChunk::Main=>path.starts_with("FortniteGame/Content/Athena/Maps/"),
        SourceChunk::MainBlueprint=>path.starts_with("FortniteGame/Content/"),
        SourceChunk::S3=>path.starts_with("FortniteGame/Content/Packages/")||
            path.starts_with("FortniteGame/Content/Environments/")||
            path.starts_with("FortniteGame/Content/Athena/"),
    };
    let relative=Path::new(path);
    if !valid_root||path.len()>1024||path.contains('\\')||path.contains(':')||
        !relative.components().all(|c|matches!(c,Component::Normal(_)))||
        path.split('/').any(|s|s=="."||s==".."||s.is_empty()){
        return Err(format!("original POI source path unsafe or wrong archive: {path}"));
    }
    Ok(())
}
fn find_entry<'a>(entries:&'a[PakEntry],pkg:&str,ext:&str,chunk:SourceChunk)
    ->Result<Option<&'a PakEntry>,String>{
    let source=match chunk {
        SourceChunk::Main|SourceChunk::MainBlueprint=>format!("{pkg}{ext}"),
        SourceChunk::S3=>format!("{}{ext}",
            pkg.strip_prefix("FortniteGame/Content/")
                .ok_or("source s3 package lacks canonical Content root")?),
    };
    let mut hits=entries.iter().filter(|x|x.path==source);
    let first=hits.next();
    if hits.next().is_some(){return Err(format!("ambiguous source POI PAK record {source}"));}
    Ok(first)
}
/// Fetch exact packages from the retail archive, verifying index SHA1, payload
/// SHA1 and any cached source files. Missing packages stay explicitly missing.
/// For meshes, optional source .ubulk is needed for full material closure.
pub fn prepare_original_poi_packages(
    main_pak:&Path,destination:&Path,
    requested:&BTreeSet<String>,chunk:SourceChunk,
)->Result<PreparedPoiSource,String>{
    if requested.len()>MAX_REQUESTED_PACKAGES{
        return Err("original POI package request exceeds safe bounded import".into());
    }
    if requested.is_empty(){return Ok(PreparedPoiSource::default());}
    let archive=match chunk{
        SourceChunk::Main|SourceChunk::MainBlueprint=>main_pak.to_path_buf(),
        SourceChunk::S3=>main_pak.with_file_name("pakchunk0_s3-WindowsClient.pak"),
    };
    let mut stats=PreparedPoiSource{
        requested:requested.len(),..Default::default()
    };
    if !archive.exists(){
        stats.unavailable=requested.len();
        return Ok(stats);
    }
    let report=pak::inspect_with_key(&archive,&authenticated_source_key()?)?;
    let expected=match chunk{SourceChunk::Main|SourceChunk::MainBlueprint=>MAIN,SourceChunk::S3=>SPLIT_S3};
    if report.footer.version!=7 ||
        report.footer.index_hash.iter().map(|x|format!("{x:02x}")).collect::<String>()!=expected{
        return Err(format!("original detailed POI {} archive index SHA1 mismatch",
            archive.display()));
    }
    let IndexStatus::Indexed{entries,..}=&report.status else{
        return Err("authentic POI archive index not available".into());
    };
    for pkg in requested{
        validate_package(pkg,chunk)?;
        let suffixes: &[&str]=match chunk{
            SourceChunk::Main=>&[".umap",".uexp"],
            SourceChunk::MainBlueprint=>&[".uasset",".uexp"],
            SourceChunk::S3=>&[".uasset",".uexp"],
        };
        let mut records=Vec::with_capacity(3);
        for &extension in suffixes{
            let Some(entry)=find_entry(entries,pkg,extension,chunk)? else{
                records.clear();break;
            };
            records.push(entry);
        }
        if records.len()!=2 || records.iter().any(|record|
            record.encrypted||record.compression_method!=0||
            record.compressed_size!=record.uncompressed_size){
            stats.unavailable+=1;
            continue;
        }
        if chunk==SourceChunk::S3{
            if let Some(bulk)=find_entry(entries,pkg,".ubulk",chunk)?{
                if !bulk.encrypted&&bulk.compression_method==0 &&
                    bulk.compressed_size==bulk.uncompressed_size {
                    records.push(bulk);
                }
            }
        }
        stats.available+=1;
        for record in records{
            let extension=Path::new(&record.path).extension()
                .and_then(|s|s.to_str()).ok_or("source POI extension invalid")?;
            let target=destination.join(format!("{pkg}.{extension}"));
            if target.exists(){
                let meta=fs::symlink_metadata(&target)
                    .map_err(|e|format!("original POI cache stat: {e}"))?;
                if !meta.file_type().is_file()||meta.len()!=record.uncompressed_size{
                    return Err(format!("unverified original POI cache file {}",target.display()));
                }
                let content=fs::read(&target).map_err(|e|e.to_string())?;
                if Sha1::digest(&content).as_slice()!=record.content_hash{
                    return Err(format!("cached source POI SHA1 mismatch {}",target.display()));
                }
            }else{
                if record.uncompressed_size>64*1024*1024 ||
                    stats.new_bytes.checked_add(record.uncompressed_size)
                        .is_none_or(|n|n>MAX_NEW_SOURCE_BYTES){
                    return Err("source detailed POI new-byte budget exceeded; cannot silently omit native mesh".into());
                }
                let content=pak::extract_plain_entry(&archive,&report,record)?;
                if let Some(parent)=target.parent(){
                    fs::create_dir_all(parent).map_err(|e|e.to_string())?;
                }
                let tmp=target.with_extension("source.part");
                let mut file=fs::OpenOptions::new().write(true).create_new(true)
                    .open(&tmp).map_err(|e|e.to_string())?;
                file.write_all(&content).map_err(|e|e.to_string())?;
                file.sync_all().map_err(|e|e.to_string())?;
                fs::rename(&tmp,&target).map_err(|e|e.to_string())?;
                stats.extracted_files+=1;
                stats.new_bytes+=record.uncompressed_size;
            }
            stats.verified_files+=1;
        }
    }
    Ok(stats)
}
#[cfg(test)]
mod tests{
    use super::*;
    #[test]fn correct_original_pak_mount_point_variants(){
        assert!(validate_package(
            "FortniteGame/Content/Athena/Maps/POI/Athena_POI_ToiletFactory_001",
            SourceChunk::Main).is_ok());
        assert!(validate_package(
            "FortniteGame/Content/Packages/DS_Fortnite_Terrain_NoLOD/Elevation/S_Cave_Outer_Middle",
            SourceChunk::S3).is_ok());
        assert!(validate_package("FortniteGame/Content/../../evil",SourceChunk::S3).is_err());
    }
}
