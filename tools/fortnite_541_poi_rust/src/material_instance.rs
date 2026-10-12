//! Authored Fortnite 5.41 UE4.21 MaterialInstanceConstant texture parameters.
//!
//! FTextureParameterValue is an array of tagged structs with nested
//! FMaterialParameterInfo and one exact UObject Texture2D reference.
//! Retain source identities and never choose an unrelated texture by filename.
use crate::{properties,uobject::{self,PackageCatalog}};
use std::{path::Path,fs};

#[derive(Debug,Clone,PartialEq,Eq)]
pub struct OriginalTextureParameter {
    pub name:String,
    pub texture_object:String,
}
#[derive(Debug,Clone)]
pub struct OriginalMaterialInstance {
    pub source_object:String,
    pub parent:Option<String>,
    pub textures:Vec<OriginalTextureParameter>,
}
fn source_field<'a>(
    props:&properties::Properties,raw:&'a[u8],name:&str,kind:&str,
)->Result<&'a[u8],String>{
    let mut found=props.fields.iter().filter(|p|p.name==name);
    let p=found.next().ok_or_else(||format!("original material lacks {name}"))?;
    if found.next().is_some()||p.kind!=kind{return Err(format!("original {name} ambiguous/wrong UE4 type"));}
    raw.get(p.payload.clone()).ok_or_else(||"source material field out of bounds".into())
}
fn named(c:&PackageCatalog,bytes:&[u8])->Result<String,String>{
    if bytes.len()!=8{return Err("source material parameter FName length invalid".into());}
    let number=u32::from_le_bytes(bytes[4..8].try_into().unwrap());
    let base=c.names.get(u32::from_le_bytes(bytes[..4].try_into().unwrap()) as usize)
        .ok_or("source texture parameter FName missing from package")?;
    Ok(if number==0{base.clone()}else{format!("{base}#{number}")})
}
fn terminated(c:&PackageCatalog,raw:&[u8])->Result<Vec<u8>,String>{
    let id=c.names.iter().position(|n|n=="None")
        .ok_or("original MaterialInstance FName None absent")?;
    let id=u32::try_from(id).map_err(|_|"source FName map size invalid")?;
    let mut out=raw.to_vec();
    out.extend_from_slice(&id.to_le_bytes());
    out.extend_from_slice(&0u32.to_le_bytes());
    Ok(out)
}
pub fn source_package(source:&str)->Result<String,String>{
    let rest=source.strip_prefix("/Game/").ok_or("original material identity not /Game/")?;
    let (package,object)=rest.split_once("::").ok_or("material lacks original UObject export")?;
    if object.is_empty()||object.contains('/')||object.contains('\\') {
        return Err("original material UObject export name unsafe".into());
    }
    // UE4 cooked FName WoodenCrates#3 resolves to the retail package
    // filename WoodenCrates_2, but the UObject export remains numbered.
    // The identical filename convention applies to original mesh/Blueprint
    // packages, and is source-verified rather than filename guessing.
    let filename=match package.rsplit_once('#'){
        Some((path,raw)) if !raw.is_empty()&&raw.bytes().all(|b|b.is_ascii_digit())=>{
            let n=raw.parse::<u32>().map_err(|_|"numbered material FName overflow")?;
            if n==0{return Err("original material FName number cannot be zero".into());}
            format!("{path}_{}",n-1)
        },
        Some(_)=>return Err("original numbered material FName malformed".into()),
        None=>package.to_owned(),
    };
    if filename.is_empty()||filename.len()>1024||
       filename.split('/').any(|part|part.is_empty()||part=="."||part=="..")||
       !filename.bytes().all(|b|b.is_ascii_alphanumeric()||b==b'/'||b==b'_'||b==b'-') {
       return Err("original material package identity unsafe".into());
    }
    Ok(format!("FortniteGame/Content/{filename}"))
}
pub fn inspect_instance(
    header:&[u8],exports:&[u8],original:&str,
)->Result<OriginalMaterialInstance,String>{
    let catalog=uobject::inspect(header)?;
    let source_export_name=original.rsplit("::").next()
        .ok_or("original material instance source export name missing")?;
    let mut matches=catalog.exports.iter().enumerate().filter(|(i,e)|
        catalog.export_class_name(e)==Some("MaterialInstanceConstant") &&
        catalog.source_object_path((i+1) as i32).ok()
            .and_then(|p|p.rsplit("::").next().map(str::to_owned))
            .as_deref()==Some(source_export_name)
    );
    let (_,material)=matches.next().ok_or("original material object is not MaterialInstanceConstant")?;
    if matches.next().is_some(){return Err("duplicate retail MaterialInstance UObject export".into());}
    let raw=catalog.export_data(header,exports,material)?;
    let props=properties::scan(&catalog,raw)?;
    let parent=props.fields.iter().find(|p|p.name=="Parent")
        .map(|p|->Result<Option<String>,String>{
            if p.kind!="ObjectProperty"||p.payload.len()!=4{return Err("material Parent property not UObject".into());}
            let ref_id=i32::from_le_bytes(raw[p.payload.clone()].try_into().unwrap());
            if ref_id==0 {Ok(None)}
            else{catalog.source_object_path(ref_id).map(Some)}
        }).transpose()?.flatten();
    let mut textures=Vec::new();
    if let Some(param)=props.fields.iter().find(|p|p.name=="TextureParameterValues"){
        if param.kind!="ArrayProperty"||
            param.metadata.first().map(String::as_str)!=Some("StructProperty"){
            return Err("retail TextureParameterValues not typed struct array".into());
        }
        let data=&raw[param.payload.clone()];
        if data.len()<4{return Err("source TextureParameterValues truncated".into());}
        let count=u32::from_le_bytes(data[..4].try_into().unwrap()) as usize;
        if count>128{return Err("too many source TextureParameterValues".into());}
        let wrapped=terminated(&catalog,&data[4..])?;
        let outer=properties::scan(&catalog,&wrapped)?;
        if outer.fields.len()!=1||outer.fields[0].name!="TextureParameterValues"||
           outer.fields[0].kind!="StructProperty"{
            return Err("retail texture parameter wrapper differs from authenticated source".into());
        }
        let items=&wrapped[outer.fields[0].payload.clone()];
        let mut cursor=0usize;
        for _ in 0..count{
            if cursor>=items.len(){return Err("source texture parameters end before array count".into());}
            let fields=properties::scan(&catalog,&items[cursor..])?;
            let consumed=fields.bytes_consumed;
            if consumed==0||cursor+consumed>items.len(){
                return Err("retail material parameter element span invalid".into());
            }
            let rec=&items[cursor..cursor+consumed];
            let info=source_field(&fields,rec,"ParameterInfo","StructProperty")?;
            let info_props=properties::scan(&catalog,info)?;
            let name=named(&catalog,source_field(&info_props,info,"Name","NameProperty")?)?;
            let value=source_field(&fields,rec,"ParameterValue","ObjectProperty")?;
            if value.len()!=4{return Err("TextureParameterValue UObject reference width invalid".into());}
            let ref_id=i32::from_le_bytes(value.try_into().unwrap());
            if ref_id!=0{
                let texture=catalog.source_object_path(ref_id)?;
                // An original UE4 MaterialInstanceConstant may use the
                // Engine-provided default normal (FlatNormal), white or
                // black textures while its *diffuse* is a valid /Game/
                // asset. Rejecting that legitimate /Engine reference used
                // to discard the ENTIRE otherwise-valid material instance
                // and leave its diffuse source completely gray.
                // Preserve source identity; source_package intentionally
                // refuses /Engine assets because they are not in the game's
                // authenticated Fortnite PAK material cache.
                if !texture.starts_with("/Game/") &&
                    !texture.starts_with("/Engine/"){
                    return Err(format!(
                        "texture parameter {name} has unsupported source root {texture}"
                    ));
                }
                textures.push(OriginalTextureParameter{
                    name,texture_object:texture
                });
            }
            cursor+=consumed;
        }
        if cursor!=items.len(){return Err("source texture parameter array has unexplained trailing bytes".into());}
    }
    Ok(OriginalMaterialInstance{source_object:original.into(),parent,textures})
}
pub fn from_source_root(
    root:&Path,original:&str,
)->Result<Option<OriginalMaterialInstance>,String>{
    let base=root.join(source_package(original)?);
    let h=base.with_extension("uasset");
    let x=base.with_extension("uexp");
    if !h.is_file()&&!x.is_file(){return Ok(None);}
    if h.is_file()!=x.is_file(){
        return Err(format!("partial original material instance cache {}",base.display()));
    }
    inspect_instance(&fs::read(h).map_err(|e|e.to_string())?,
        &fs::read(x).map_err(|e|e.to_string())?,original).map(Some)
}
/// Original texture parameter identities proven by the retail materials in
/// M_Terrain_Cave, M_Terrain_Cliff_White and MI_ShippingContainer_01.
/// These indicate source diffuse texture inputs, NOT whole-shader parity.
pub fn source_diffuse_input(
    material:&OriginalMaterialInstance,
)->Option<&OriginalTextureParameter>{
    const AUTHORED_SOURCE_NAMES:[&str;3]=[
        "Diffuse","CliffTexture","Base Tiling Texture"
    ];
    AUTHORED_SOURCE_NAMES.iter().find_map(|name|
        material.textures.iter().find(|t|t.name==*name)
    )
}
/// Source-authored tangent-space normal input, not a filename suffix guess.
/// The native original shipping container and cave MICs use precisely these
/// FMaterialParameterInfo names; actual PF_BC5 format is checked on decode.
pub fn source_normal_input(
    material:&OriginalMaterialInstance,
)->Option<&OriginalTextureParameter>{
    ["Normals","CliffNormal"].iter().find_map(|name|
        material.textures.iter().find(|t|t.name==*name)
    )
}

#[cfg(test)]
mod tests{
    use super::*;
    #[test]fn reject_nonoriginal_material_paths(){
        assert_eq!(source_package(
            "/Game/Athena/Materials/M_Floor::M_Floor"
        ).unwrap(),"FortniteGame/Content/Athena/Materials/M_Floor");
        assert!(source_package("/Game/../../unrelated::unrelated").is_err());
        assert!(source_package("/Script/Engine::Material").is_err());
        assert_eq!(
            source_package("/Game/Environments/Props/Boxes/Materials/WoodenCrates#3::WoodenCrates#3").unwrap(),
            "FortniteGame/Content/Environments/Props/Boxes/Materials/WoodenCrates_2"
        );
        assert!(source_package("/Game/Props/WoodenCrates#0::WoodenCrates#0").is_err());
        assert!(source_package("/Game/Props/WoodenCrates#abc::WoodenCrates#abc").is_err());
        assert!(source_package("/Game/Props/WoodenCrates#4294967296::WoodenCrates").is_err());

    }
    #[test]fn original_engine_flat_normal_does_not_shadow_authored_diffuse(){
        let material=OriginalMaterialInstance{
            source_object:"/Game/SomeMaterial::SomeMaterial".into(),
            parent:None,
            textures:vec![
                OriginalTextureParameter{
                    name:"Normals".into(),
                    texture_object:"/Engine/EngineMaterials/FlatNormal::FlatNormal".into(),
                },
                OriginalTextureParameter{
                    name:"Diffuse".into(),
                    texture_object:"/Game/Props/Cliff_D::Cliff_D".into(),
                },
            ],
        };
        assert_eq!(
            source_diffuse_input(&material).unwrap().texture_object,
            "/Game/Props/Cliff_D::Cliff_D"
        );
        assert!(source_package(
            &source_normal_input(&material).unwrap().texture_object
        ).is_err(),"/Engine/ defaults are not retail source PAK assets");
    }
    #[test]fn explicit_source_diffuse_contract_only(){
        let m=OriginalMaterialInstance{
            source_object:"source".into(),parent:None,
            textures:vec![
                OriginalTextureParameter{name:"Normals".into(),texture_object:"normal".into()},
                OriginalTextureParameter{name:"CliffTexture".into(),texture_object:"retail diffuse".into()},
            ]
        };
        assert_eq!(source_diffuse_input(&m).unwrap().texture_object,"retail diffuse");
        assert_eq!(source_normal_input(&m).unwrap().texture_object,"normal");
    }
}
