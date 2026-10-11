//! Authenticated Fortnite 5.41 daytime SkyDome material-instance parameters.
//!
//! Cooked UE4.21 serializes MaterialInstanceConstant parameter arrays as
//! an outer StructProperty wrapper containing exactly N tagged property
//! structs. Preserve the original FNames and linear FLinearColor values.
//! This module does not claim to translate M_SkyDome's pixel shader.
use crate::{properties::{self,Properties},uobject::{self,PackageCatalog}};
use std::{collections::BTreeMap,fs,path::Path};

const PREFIX:&str="FortniteGame/Content/Packages/Fortress_Sky/SkyDome";
const MORNING:&str="Morn_M_SkyDome_Inst_Basic01";
const DAY:&str="Day_M_SkyDome_Inst_Basic01";
const PARENT_DAY:&str="/Game/Packages/Fortress_Sky/SkyDome/MaterialInstances/SkyDomeBasic01/Morn_M_SkyDome_Inst_Basic01::Morn_M_SkyDome_Inst_Basic01";
const PARENT_MORNING:&str="/Game/Packages/Fortress_Sky/SkyDome/Master/M_SkyDome::M_SkyDome";

#[derive(Clone,Debug)]
pub struct OriginalDaySky {
    pub horizon_linear:[f32;3],
    pub zenith_linear:[f32;3],
    pub cloud_key_linear:[f32;3],
    pub cloud_shadow_linear:[f32;3],
    pub cloud_horizon_linear:[f32;3],
    pub scalar_params:BTreeMap<String,f32>,
    pub vector_params:BTreeMap<String,[f32;4]>,
}
fn exactly_one<'a>(source:&'a[u8],props:&Properties,name:&str,kind:&str)
    ->Result<&'a[u8],String>{
    let matches=props.fields.iter().filter(|p|p.name==name).collect::<Vec<_>>();
    if matches.len()!=1||matches[0].kind!=kind{
        return Err(format!("original SkyDome {name} missing/ambiguous/wrong UE4 type"));
    }
    source.get(matches[0].payload.clone()).ok_or_else(||
        format!("original SkyDome {name} payload outside source"))
}
fn append_none(cat:&PackageCatalog,raw:&[u8])->Result<(Vec<u8>,Properties),String>{
    let none=cat.names.iter().position(|n|n=="None")
        .ok_or("SkyDome source NameMap lacks tagged None terminator")?;
    let none=u32::try_from(none).map_err(|_|"source sky None FName exceeds u32")?;
    let mut bytes=Vec::with_capacity(raw.len()+8);
    bytes.extend_from_slice(raw);
    bytes.extend_from_slice(&none.to_le_bytes());
    bytes.extend_from_slice(&0u32.to_le_bytes());
    let props=properties::scan(cat,&bytes)?;
    Ok((bytes,props))
}
fn source_fname(cat:&PackageCatalog,b:&[u8])->Result<String,String>{
    if b.len()!=8{return Err("original SkyDome FName not eight bytes".into());}
    let index=u32::from_le_bytes(b[..4].try_into().unwrap()) as usize;
    let number=u32::from_le_bytes(b[4..].try_into().unwrap());
    let base=cat.names.get(index).ok_or("original SkyDome parameter FName index absent")?;
    Ok(if number==0{base.clone()}else{format!("{base}#{number}")})
}
#[derive(Debug,Default)]
struct MaterialParams {
    parent:String,
    scalars:BTreeMap<String,f32>,
    vectors:BTreeMap<String,[f32;4]>,
}
fn parse_array(
    cat:&PackageCatalog,source:&[u8],props:&Properties,
    tag:&str,vector:bool,
)->Result<BTreeMap<String,Vec<f32>>,String>{
    let data=exactly_one(source,props,tag,"ArrayProperty")?;
    if data.len()<4{return Err(format!("original {tag} count missing"));}
    let count=u32::from_le_bytes(data[..4].try_into().unwrap()) as usize;
    if count>128{return Err(format!("original {tag} exceeds safe count"));}
    let (outer_bytes,outer)=append_none(cat,&data[4..])?;
    if outer.fields.len()!=1||
       outer.fields[0].name!=tag||
       outer.fields[0].kind!="StructProperty"||
       outer.fields[0].metadata.first().map(String::as_str)!=Some(
           if vector{"VectorParameterValue"}else{"ScalarParameterValue"}
       ){
        return Err(format!("original {tag} aggregate StructProperty metadata mismatch"));
    }
    let array=&outer_bytes[outer.fields[0].payload.clone()];
    let mut offset=0usize;
    let mut params=BTreeMap::new();
    for _ in 0..count{
        let (element_bytes,element)=append_none(cat,&array[offset..])?;
        let consumed=element.bytes_consumed;
        if consumed==0||consumed>element_bytes.len() ||
            consumed>array.len()-offset+8{
            return Err(format!("original {tag} element bounds invalid"));
        }
        let info=exactly_one(&element_bytes,&element,"ParameterInfo","StructProperty")?;
        let (info_bytes,info_fields)=append_none(cat,info)?;
        let name=source_fname(cat,exactly_one(
            &info_bytes,&info_fields,"Name","NameProperty"
        )?)?;
        let value=exactly_one(&element_bytes,&element,"ParameterValue",
            if vector{"StructProperty"}else{"FloatProperty"})?;
        let floats=if vector{
            if value.len()!=16{return Err(format!("original {tag} color not FLinearColor"));}
            (0..4).map(|i|f32::from_le_bytes(
                value[i*4..i*4+4].try_into().unwrap()
            )).collect::<Vec<_>>()
        }else{
            if value.len()!=4{return Err(format!("original {tag} float not f32"));}
            vec![f32::from_le_bytes(value.try_into().unwrap())]
        };
        if floats.iter().any(|x|!x.is_finite()){
            return Err(format!("nonfinite original SkyDome parameter {name}"));
        }
        if params.insert(name.clone(),floats).is_some(){
            return Err(format!("duplicate original SkyDome parameter {name}"));
        }
        offset=offset.checked_add(consumed)
            .ok_or("SkyDome parameter offset overflow")?;
        if offset>array.len(){
            // The last element may require the synthetic None only if all
            // source payload bytes were already consumed.
            if offset!=array.len()+8{return Err("source SkyDome parameter overrun".into());}
            offset=array.len();
        }
    }
    if offset!=array.len(){
        return Err(format!("source {tag} contains {} unexplained bytes",array.len()-offset));
    }
    Ok(params)
}
fn parse_material(head:&[u8],exports:&[u8])->Result<MaterialParams,String>{
    let cat=uobject::inspect(head)?;
    let candidates=cat.exports.iter().filter(|e|
        cat.export_class_name(e)==Some("MaterialInstanceConstant")
    ).collect::<Vec<_>>();
    if candidates.len()!=1{return Err("SkyDome source MaterialInstanceConstant export not unique".into());}
    let raw=cat.export_data(head,exports,candidates[0])?;
    let props=properties::scan(&cat,raw)?;
    let parent_ref=exactly_one(raw,&props,"Parent","ObjectProperty")?;
    if parent_ref.len()!=4{return Err("SkyDome material parent source index malformed".into());}
    let parent_id=i32::from_le_bytes(parent_ref.try_into().unwrap());
    let parent=cat.source_object_path(parent_id)?;
    let scalars=parse_array(&cat,raw,&props,"ScalarParameterValues",false)?
        .into_iter().map(|(k,v)|(k,v[0])).collect();
    let vectors=parse_array(&cat,raw,&props,"VectorParameterValues",true)?
        .into_iter().map(|(k,v)|(k,[v[0],v[1],v[2],v[3]])).collect();
    Ok(MaterialParams{parent,scalars,vectors})
}
fn load(root:&Path,asset:&str)->Result<Option<MaterialParams>,String>{
    let base=root.join(PREFIX).join("MaterialInstances/SkyDomeBasic01").join(asset);
    let header=base.with_extension("uasset");
    let exports=base.with_extension("uexp");
    if header.is_file()!=exports.is_file(){
        return Err(format!("original SkyDome {asset} cache package incomplete"));
    }
    if !header.is_file(){return Ok(None);}
    let h=fs::read(&header).map_err(|e|e.to_string())?;
    let e=fs::read(&exports).map_err(|e|e.to_string())?;
    parse_material(&h,&e).map(Some)
}
pub fn from_source_root(root:&Path)->Result<Option<OriginalDaySky>,String>{
    let Some(morn)=load(root,MORNING)? else{return Ok(None)};
    let Some(day)=load(root,DAY)? else{return Ok(None)};
    if morn.parent!=PARENT_MORNING||day.parent!=PARENT_DAY{
        return Err("authored Fortnite sky inheritance no longer matches M_SkyDome -> Morn -> Day".into());
    }
    let mut vectors=morn.vectors;
    vectors.extend(day.vectors);
    let mut scalars=morn.scalars;
    scalars.extend(day.scalars);
    let required=|name:&str|->Result<[f32;3],String>{
        let c=vectors.get(name).ok_or_else(||
            format!("original day sky missing source vector {name}")
        )?;
        if c[..3].iter().any(|x|*x<0.||*x>16.){
            return Err(format!("original sky source radiance invalid for {name}"));
        }
        Ok([c[0],c[1],c[2]])
    };
    Ok(Some(OriginalDaySky{
        horizon_linear:required("Sky-HorizonColor")?,
        zenith_linear:required("Sky-ZenithColor")?,
        cloud_key_linear:required("Clouds-KeyLightColor")?,
        cloud_shadow_linear:required("Cloud-ShadowColor")?,
        cloud_horizon_linear:required("Clouds-Horizon Color")?,
        scalar_params:scalars,vector_params:vectors,
    }))
}
/// Build a source-COLOR-ONLY daytime cube from actual authored material
/// FLinearColor endpoints. This is a deliberately limited compatibility
/// presentation until the original sky material shader is translated. It
/// does NOT manufacture source clouds, stars, horizon scatter or sun direction.
/// Outputs engine Y-up (+X,-X,+Y,-Y,+Z,-Z) sRGB cubemap faces.
pub fn provisional_day_cubemap_rgba(
    day:&OriginalDaySky,side:u32
)->Result<[Vec<u8>;6],String>{
    if !(4..=512).contains(&side){
        return Err("source day SkyDome cube side outside 4..=512".into());
    }
    let side=side as usize;
    fn ray(face:usize,u:f32,v:f32)->[f32;3]{
        match face{
            0=>[1.,-v,-u],1=>[-1.,-v,u],
            2=>[u,1.,v],3=>[u,-1.,-v],
            4=>[u,-v,1.],5=>[-u,-v,-1.],
            _=>unreachable!("six cubemap faces"),
        }
    }
    fn srgb(value:f32)->u8{
        let v=value.max(0.);
        let encoded=if v<=0.003_130_8{12.92*v}
            else{1.055*v.powf(1./2.4)-0.055};
        (encoded.clamp(0.,1.)*255.).round() as u8
    }
    Ok(std::array::from_fn(|face|{
        let mut pixels=Vec::with_capacity(side*side*4);
        for y in 0..side{
            for x in 0..side{
                let u=(x as f32+0.5)/side as f32*2.-1.;
                let v=(y as f32+0.5)/side as f32*2.-1.;
                let dir=ray(face,u,v);
                let length=(dir.iter().map(|n|n*n).sum::<f32>()).sqrt();
                // The original zenith and horizon colors are source-exact;
                // this elevation-based mixing is a provisional presentation
                // and is NOT a claim of M_SkyDome shader parity.
                let elevation=(dir[1]/length).clamp(0.,1.);
                for channel in 0..3{
                    let linear=day.horizon_linear[channel]*(1.-elevation)+
                        day.zenith_linear[channel]*elevation;
                    pixels.push(srgb(linear));
                }
                pixels.push(255);
            }
        }
        pixels
    }))
}
/// Original material graph contract for the actual M_SkyDome master. These
/// are typed UObject dependencies, not source shader execution or a guessed
/// sky rasterizer.
#[derive(Clone,Debug)]
pub struct OriginalSkyMasterGraph{
    pub material_expression_count:usize,
    pub texture_sample_count:usize,
    pub source_texture_objects:Vec<String>,
    pub material_functions:Vec<String>,
    pub source_collection_parameters:Vec<String>,
}
pub fn inspect_sky_master(root:&Path)->Result<Option<OriginalSkyMasterGraph>,String>{
    let base=root.join(PREFIX).join("Master/M_SkyDome");
    let header=base.with_extension("uasset");
    let exports=base.with_extension("uexp");
    if header.is_file()!=exports.is_file(){
        return Err("original SkyDome master shader package incomplete".into());
    }
    if !header.is_file(){return Ok(None);}
    let h=fs::read(&header).map_err(|e|format!("original SkyDome master header: {e}"))?;
    let x=fs::read(&exports).map_err(|e|format!("original SkyDome master exports: {e}"))?;
    let cat=uobject::inspect(&h)?;
    let mut material_roots=0usize;
    let mut expressions=0usize;
    let mut samples=0usize;
    let mut textures=std::collections::BTreeSet::new();
    let mut functions=std::collections::BTreeSet::new();
    let mut collections=std::collections::BTreeSet::new();
    for ex in &cat.exports{
        let Some(kind)=cat.export_class_name(ex) else{continue};
        if kind=="Material"{material_roots+=1;}
        if !kind.starts_with("MaterialExpression"){continue;}
        expressions+=1;
        let raw=cat.export_data(&h,&x,ex)?;
        let props=properties::scan(&cat,raw)?;
        if kind=="MaterialExpressionTextureSample"{
            samples+=1;
            let b=exactly_one(raw,&props,"Texture","ObjectProperty")?;
            if b.len()!=4{return Err("SkyDome TextureSample object index malformed".into());}
            let index=i32::from_le_bytes(b.try_into().unwrap());
            let object=cat.source_object_path(index)?;
            if !object.starts_with("/Game/"){
                return Err(format!("original SkyDome TextureSample not from source /Game/: {object}"));
            }
            textures.insert(object);
        }
        if kind=="MaterialExpressionMaterialFunctionCall"{
            for p in props.fields.iter().filter(|p|p.name=="MaterialFunction"
                && p.kind=="ObjectProperty"){
                let b=&raw[p.payload.clone()];
                if b.len()!=4{return Err("SkyDome function import index malformed".into());}
                functions.insert(cat.source_object_path(i32::from_le_bytes(
                    b.try_into().unwrap()
                ))?);
            }
        }
        if kind=="MaterialExpressionCollectionParameter"{
            let name=exactly_one(raw,&props,"ParameterName","NameProperty")?;
            collections.insert(source_fname(&cat,name)?);
        }
    }
    if material_roots!=1||expressions<1||samples<1||textures.is_empty(){
        return Err("original SkyDome root/material expression graph incomplete".into());
    }
    Ok(Some(OriginalSkyMasterGraph{
        material_expression_count:expressions,
        texture_sample_count:samples,
        source_texture_objects:textures.into_iter().collect(),
        material_functions:functions.into_iter().collect(),
        source_collection_parameters:collections.into_iter().collect(),
    }))
}

/// Independently validated original material-texture input. The source
/// image is not bound to the sky until the authored shader graph and its
/// texture coordinate expressions are reproduced.
#[derive(Clone,Debug)]
pub struct OriginalSkySourceMip {
    pub original_object:String,
    pub width:u32,
    pub height:u32,
    pub original_format:String,
    pub source_bytes:usize,
}
pub fn inspect_sampled_source_mip(
    root:&Path,original_object:&str,
)->Result<OriginalSkySourceMip,String>{
    let source=original_object.strip_prefix("/Game/")
        .ok_or("original sky sample is not a UE /Game/ object")?;
    let (package,object)=source.split_once("::")
        .ok_or("original sky source texture object identity lacks ::")?;
    if package.is_empty()||object.is_empty()||
        package.split('/').any(|v|v.is_empty()||v=="."||v=="..")||
        !package.bytes().all(|b|b.is_ascii_alphanumeric()||b==b'_'||b==b'/'||b==b'-'){
        return Err("untrusted original SkyDome package path".into());
    }
    let base=root.join("FortniteGame/Content").join(package);
    let h=fs::read(base.with_extension("uasset"))
        .map_err(|e|format!("original sky texture header {package}: {e}"))?;
    let x=fs::read(base.with_extension("uexp"))
        .map_err(|e|format!("original sky texture exports {package}: {e}"))?;
    let b=fs::read(base.with_extension("ubulk"))
        .map_err(|e|format!("original sky external top mip {package}: {e}"))?;
    let cat=uobject::inspect(&h)?;
    let meshes=cat.exports.iter().filter(|ex|
        cat.export_class_name(ex)==Some("Texture2D") &&
        cat.names.get(ex.object_name.name_index as usize)
            .is_some_and(|name|name==object)
    ).collect::<Vec<_>>();
    if meshes.len()!=1{
        return Err(format!("original sky texture {original_object} has {} matching Texture2D exports",meshes.len()));
    }
    let ex=meshes[0];
    // The source SkyDome mixes real BC1 galaxy textures, raw BGRA8
    // height/normal images and grayscale PF_G8 cloud-detail masks.
    // These are DISTINCT original formats, not reinterpretations of one
    // guessed byte stride. Admit only a strict, source-validated decoder.
    let (w,h,format,bytes)=match crate::texture::first_mip_bc(&cat,&h,&x,&b,ex){
        Ok(mip)=>(mip.width,mip.height,format!("{:?}",mip.format),mip.blocks.len()),
        Err(bc_err)=>match crate::texture::first_mip_bgra8(&cat,&h,&x,&b,ex){
            Ok(mip)=>(mip.width,mip.height,mip.format.to_string(),mip.bgra8.len()),
            Err(rgb_err)=>match crate::texture::first_mip_g8(&cat,&h,&x,&b,ex){
                Ok(mip)=>(mip.width,mip.height,"PF_G8".to_string(),mip.pixels.len()),
                Err(g8_err)=>return Err(format!(
                    "no supported original cooked source format for {original_object}: BC: {bc_err}; BGRA: {rgb_err}; G8: {g8_err}"
                )),
            }
        }
    };
    Ok(OriginalSkySourceMip{
        original_object:original_object.into(),
        width:w,height:h,original_format:format,source_bytes:bytes,
    })
}

#[cfg(test)]
mod tests{
    use super::*;
    #[test]fn real_daylight_source_color_cube_has_blue_horizon_and_darker_zenith(){
        let day=OriginalDaySky{
            horizon_linear:[0.078577,0.37912,0.9],
            zenith_linear:[0.004,0.036159,0.08],
            cloud_key_linear:[0.4,0.39,0.36],
            cloud_shadow_linear:[0.040346,0.075151,0.15],
            cloud_horizon_linear:[0.12,0.52376,1.2],
            scalar_params:BTreeMap::new(),vector_params:BTreeMap::new(),
        };
        let cube=provisional_day_cubemap_rgba(&day,96).unwrap();
        assert!(cube.iter().all(|c|c.len()==96*96*4));
        let sky_top=&cube[2][((96/2)*96+96/2)*4..][..4];
        let sky_horizon=&cube[0][((96/2)*96+96/2)*4..][..4];
        assert!(sky_horizon[2]>sky_top[2]);
        assert!(cube.iter().all(|c|c.chunks_exact(4).all(|px|px[3]==255)));
        assert!(provisional_day_cubemap_rgba(&day,0).is_err());
    }
    #[test]fn reject_missing_original_sky_package_without_synthetic_color(){
        let path=std::env::temp_dir().join("source_sky_missing_unmounted");
        assert!(from_source_root(&path).unwrap().is_none());
    }
}
