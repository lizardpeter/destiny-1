//! Universal source-facing contract for a cooked UE4.21 UMaterial root.
//!
//! Only literal surviving input expressions are admitted as exact constants.
//! A linked-but-cooked-out node is a shader dependency, NEVER literal zero.
//! This is source compiler input metadata, not a source-game renderer.
use crate::{properties,uobject::{self,PackageCatalog}};
#[derive(Clone,Debug,PartialEq)]
pub struct OriginalCookedMaterialContract {
    pub material_source:String,
    pub blend_mode:String,
    pub shading_model:String,
    pub double_sided:bool,
    pub emissive_linear_rgba:Option<[f32;4]>,
    pub original_emissive_expression:Option<String>,
    pub world_position_offset_expression:Option<String>,
    pub original_opacity_expression:Option<String>,
}
fn name(c:&PackageCatalog,raw:&[u8])->Result<String,String>{
    if raw.len()!=8{return Err("original UMaterial FName width invalid".into());}
    let id=u32::from_le_bytes(raw[..4].try_into().unwrap()) as usize;
    let number=u32::from_le_bytes(raw[4..8].try_into().unwrap());
    let base=c.names.get(id).ok_or("original UMaterial source FName absent")?;
    Ok(if number==0{base.to_owned()}else{format!("{base}#{number}")})
}
fn field<'a>(p:&properties::Properties,raw:&'a[u8],key:&str,kind:&str)
    ->Result<Option<&'a[u8]>,String>{
    let mut matches=p.fields.iter().filter(|x|x.name==key);
    let Some(v)=matches.next() else{return Ok(None)};
    if matches.next().is_some()||v.kind!=kind{
        return Err(format!("original UMaterial {key} wrong type or duplicated"));
    }
    raw.get(v.payload.clone()).map(Some)
        .ok_or_else(||"original UMaterial property payload out of bounds".into())
}
fn linked_name(c:&PackageCatalog,bytes:&[u8])->Result<Option<String>,String>{
    if bytes.len()<40{return Err("original cooked material root input smaller than FExpressionInput".into());}
    let n=name(c,&bytes[32..40])?;
    Ok(if n=="None"{None}else{Some(n)})
}
pub fn inspect_original_cooked_material(
    h:&[u8],x:&[u8],source:&str
)->Result<OriginalCookedMaterialContract,String>{
    let cat=uobject::inspect(h)?;
    let object=source.rsplit("::").next().ok_or("source material UObject export name missing")?;
    let mut match_ex=cat.exports.iter().enumerate().filter(|(i,ex)|
        cat.export_class_name(ex)==Some("Material") &&
        cat.resolve_package_name((i+1) as i32)==Some(object)
    );
    let (_,original)=match_ex.next().ok_or("actual UMaterial export not found")?;
    if match_ex.next().is_some(){return Err("duplicate cooked source UMaterial export".into());}
    let raw=cat.export_data(h,x,original)?;
    let props=properties::scan(&cat,raw)?;
    let blend_mode=name(&cat,field(&props,raw,"BlendMode","ByteProperty")?
        .ok_or("original UMaterial BlendMode not explicitly authored")?)?;
    let shading_model=name(&cat,field(&props,raw,"ShadingModel","ByteProperty")?
        .ok_or("original UMaterial ShadingModel not explicitly authored")?)?;
    let mut two_sided=false;
    if let Some(p)=props.fields.iter().find(|p|p.name=="TwoSided"){
        if p.kind!="BoolProperty"{
            return Err("original UMaterial TwoSided type wrong".into());
        }
        two_sided=match p.metadata.first().map(String::as_str){
            Some("bool_value=1")=>true,
            Some("bool_value=0")=>false,
            _=>return Err("original UMaterial TwoSided source boolean malformed".into()),
        };
    }
    let original_emissive_expression=field(&props,raw,"EmissiveColor","StructProperty")?
        .map(|b|linked_name(&cat,b)).transpose()?.flatten();
    let world_position_offset_expression=field(&props,raw,"WorldPositionOffset","StructProperty")?
        .map(|b|linked_name(&cat,b)).transpose()?.flatten();
    let original_opacity_expression=field(&props,raw,"Opacity","StructProperty")?
        .map(|b|linked_name(&cat,b)).transpose()?.flatten();
    let mut emissive_linear_rgba=None;
    if let Some(target)=&original_emissive_expression{
        // Only a surviving, uniquely identified MaterialExpressionVectorParameter
        // directly referenced by the UMaterial EmissiveColor root qualifies
        // as a literal source-known emissive program. Missing arithmetic
        // nodes, material functions or texture samplers must remain uncompiled.
        for (i,ex) in cat.exports.iter().enumerate(){
            let actual=cat.source_object_path((i+1) as i32)?;
            if cat.export_class_name(ex)!=Some("MaterialExpressionVectorParameter")||
               actual.rsplit("::").next()!=Some(target.as_str()){
                continue;
            }
            if emissive_linear_rgba.is_some(){
                return Err("duplicate original emissive vector parameter node".into());
            }
            let data=cat.export_data(h,x,ex)?;
            let p=properties::scan(&cat,data)?;
            let input_name=field(&p,data,"ParameterName","NameProperty")?
                .map(|b|name(&cat,b)).transpose()?
                .ok_or("source emissive vector has no parameter name")?;
            if input_name!="EmissiveColour"{continue;}
            let value=field(&p,data,"DefaultValue","StructProperty")?
                .ok_or("original EmissiveColour vector literal missing")?;
            if value.len()!=16{return Err("original EmissiveColour linear RGBA width invalid".into());}
            let v=std::array::from_fn(|i|
                f32::from_le_bytes(value[i*4..i*4+4].try_into().unwrap()));
            if v.iter().any(|x|!x.is_finite()||x.abs()>1e5){
                return Err("original EmissiveColour literal nonfinite/unbounded".into());
            }
            emissive_linear_rgba=Some(v);
        }
    }
    Ok(OriginalCookedMaterialContract{
        material_source:source.to_owned(),blend_mode,shading_model,
        double_sided:two_sided,emissive_linear_rgba,
        original_emissive_expression,world_position_offset_expression,
        original_opacity_expression,
    })
}
#[cfg(test)]
mod tests{
    use super::*;
    use crate::uobject::{PackageCatalog,PackageSummary};
    fn cat()->PackageCatalog{
        PackageCatalog{
            summary:PackageSummary{total_header_size:0,folder_name:String::new(),
                flags:0,unversioned:true,name_count:4,name_offset:0,
                export_count:0,export_offset:0,import_count:0,
                import_offset:0,depends_offset:0},
            names:vec!["None".into(),"MaterialExpressionVectorParameter".into(),
                "BLEND_Translucent".into(),"MSM_Unlit".into()],
            imports:Vec::new(),exports:Vec::new(),
        }
    }
    #[test]fn original_cooked_expression_name_retains_numbered_identity(){
        let c=cat();
        let mut bytes=vec![0u8;48];
        bytes[32..36].copy_from_slice(&1u32.to_le_bytes());
        bytes[36..40].copy_from_slice(&2u32.to_le_bytes());
        assert_eq!(linked_name(&c,&bytes).unwrap(),
                   Some("MaterialExpressionVectorParameter#2".into()));
        bytes[32..36].copy_from_slice(&0u32.to_le_bytes());
        bytes[36..40].copy_from_slice(&0u32.to_le_bytes());
        assert_eq!(linked_name(&c,&bytes).unwrap(),None);
    }
    #[test]fn material_blend_and_shading_are_real_source_fnames(){
        let c=cat();
        assert_eq!(name(&c,&[2,0,0,0,0,0,0,0]).unwrap(),"BLEND_Translucent");
        assert_eq!(name(&c,&[3,0,0,0,0,0,0,0]).unwrap(),"MSM_Unlit");
        assert!(name(&c,&[99,0,0,0,0,0,0,0]).is_err());
    }
}
