//! Read authored Fortnite 5.41 UE4.21 Athena root streamed-level edges.
//! The root map's HLOD proxies are NOT substitutes for actual POI/prop
//! levels. This retains the source FSoftObjectPath values without guessing
//! which assets are loaded or fabricating full-resolution meshes.
use crate::{properties,uobject};

#[derive(Clone,Debug,PartialEq,Eq)]
pub struct AuthoredStreamingLevel {
    pub source_stream_object:String,
    /// Original UE4 soft-object ref, including its .WorldAsset name.
    pub source_world_asset:String,
    /// Actual UWorld map source package, not a guessed mesh prefix.
    pub package_relative_path:String,
}
fn source_world_package(path:&str)->Result<String,String>{
    let rest=path.strip_prefix("/Game/")
        .ok_or("original streamed world source not rooted at /Game")?;
    let (package,world_object)=rest.rsplit_once('.')
        .ok_or("original streamed world FSoftObjectPath lacks asset identity")?;
    let basename=package.rsplit('/').next()
        .ok_or("original streamed world package basename missing")?;
    if world_object!=basename||package.is_empty()||package.len()>1000||
        !package.bytes().all(|b|b.is_ascii_alphanumeric() ||
            b=='/' as u8||b=='_' as u8||b=='-' as u8)||
        package.split('/').any(|s|s.is_empty()||s=="."||s==".."){
        return Err("original streamed world FSoftObjectPath failed asset identity validation".into());
    }
    Ok(format!("FortniteGame/Content/{package}"))
}
pub fn original_root_streaming_levels(
    umap:&[u8],uexp:&[u8]
)->Result<Vec<AuthoredStreamingLevel>,String>{
    let catalog=uobject::inspect(umap)?;
    let mut levels=Vec::new();
    for (index,entry) in catalog.exports.iter().enumerate(){
        let Some(kind)=catalog.export_class_name(entry) else{continue};
        if kind!="LevelStreamingAlwaysLoaded"&&kind!="LevelStreamingDynamic"{
            continue;
        }
        let raw=catalog.export_data(umap,uexp,entry)?;
        let props=properties::scan(&catalog,raw)?;
        let mut fields=props.fields.iter().filter(|p|p.name=="WorldAsset");
        let field=fields.next().ok_or("source ULevelStreaming missing WorldAsset")?;
        if fields.next().is_some()||field.kind!="SoftObjectProperty"{
            return Err("ambiguous/non soft-object WorldAsset source".into());
        }
        let bytes=raw.get(field.payload.clone())
            .ok_or("source streamed WorldAsset bytes out of bounds")?;
        if bytes.len()!=12{return Err("original streamed FSoftObjectPath unexpected byte size".into());}
        let name_idx=u32::from_le_bytes(bytes[0..4].try_into().unwrap()) as usize;
        let number=u32::from_le_bytes(bytes[4..8].try_into().unwrap());
        let subpath_len=i32::from_le_bytes(bytes[8..12].try_into().unwrap());
        if number!=0 ||subpath_len!=0 {
            return Err("original root streamed WorldAsset has unsupported numbered/subpath variant".into());
        }
        let world=catalog.names.get(name_idx)
            .ok_or("streamed WorldAsset source FName missing")?.clone();
        let pkg=source_world_package(&world)?;
        levels.push(AuthoredStreamingLevel{
            source_stream_object:catalog.source_object_path((index+1) as i32)?,
            source_world_asset:world,package_relative_path:pkg,
        });
        if levels.len()>128{return Err("original Athena root streaming count exceeds bound".into());}
    }
    if levels.is_empty(){return Err("original Athena root has no ULevelStreaming source edges".into());}
    Ok(levels)
}
#[cfg(test)]
mod tests{
    use super::*;
    #[test]fn original_root_references_real_streamed_worlds_not_hlod_meshes(){
        assert_eq!(
            source_world_package("/Game/Athena/Maps/Athena_Streaming_Grid.Athena_Streaming_Grid").unwrap(),
            "FortniteGame/Content/Athena/Maps/Athena_Streaming_Grid"
        );
        assert_eq!(
            source_world_package("/Game/Athena/Maps/Landscape/Athena_Terrain_LS_04.Athena_Terrain_LS_04").unwrap(),
            "FortniteGame/Content/Athena/Maps/Landscape/Athena_Terrain_LS_04"
        );
        assert!(source_world_package("/Game/Athena/Maps/../Evil.Evil").is_err());
        assert!(source_world_package("/Engine/Other.Other").is_err());
        assert!(source_world_package("/Game/Athena/Maps/World.Wrong").is_err());
    }
}
