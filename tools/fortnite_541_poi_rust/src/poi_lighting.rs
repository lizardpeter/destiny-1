//! Source-authored UE4.21 Blueprint point-light component templates.
//!
//! An original Blueprint's directly serialized PointLightComponent may own
//! strict source color, radius, intensity and local placement even when
//! the level actor has no inline point-light component. Only use complete
//! source-valued templates attached to the precise original class/actor
//! export; never infer lights from names like "torch" or activate quest lights.
use crate::{properties,uobject};
#[derive(Clone,Debug,PartialEq)]
pub struct OriginalBlueprintPointLight {
    pub source_component:String,
    pub relative_location_cm:[f32;3],
    pub color_linear:[f32;3],
    pub attenuation_radius_cm:f32,
    pub source_intensity:f32,
}
fn float(c:&uobject::PackageCatalog,raw:&[u8],
    prop:&properties::Properties,name:&str)->Result<Option<f32>,String>{
    let mut fields=prop.fields.iter().filter(|p|p.name==name);
    let Some(p)=fields.next() else{return Ok(None)};
    if fields.next().is_some()||p.kind!="FloatProperty"||p.payload.len()!=4{
        return Err(format!("source PointLight {name} type/count invalid"));
    }
    let _=c;
    let n=f32::from_le_bytes(raw[p.payload.clone()].try_into().unwrap());
    if !n.is_finite(){return Err(format!("source PointLight {name} nonfinite"));}
    Ok(Some(n))
}
fn required_struct<'a>(raw:&'a[u8],prop:&properties::Properties,
    name:&str,kind:&str,len:usize)->Result<Option<&'a[u8]>,String>{
    let mut fields=prop.fields.iter().filter(|p|p.name==name);
    let Some(p)=fields.next() else{return Ok(None)};
    if fields.next().is_some()||p.kind!="StructProperty"||
       p.metadata.first().map(String::as_str)!=Some(kind)||
       p.payload.len()!=len{
        return Err(format!("source PointLight {name} typed payload invalid"));
    }
    raw.get(p.payload.clone()).map(Some)
        .ok_or_else(||"source PointLight tagged data bounds invalid".into())
}
fn tagged_bool(prop:&properties::Properties,name:&str)->Result<Option<bool>,String>{
    let mut values=prop.fields.iter().filter(|p|p.name==name);
    let Some(field)=values.next() else{return Ok(None)};
    if values.next().is_some()||field.kind!="BoolProperty"{
        return Err(format!("source PointLight {name} boolean type/count invalid"));
    }
    match field.metadata.first().map(String::as_str){
        Some("bool_value=0")=>Ok(Some(false)),
        Some("bool_value=1")=>Ok(Some(true)),
        _=>Err(format!("source PointLight {name} boolean value invalid")),
    }
}
fn srgb8_linear(v:u8)->f32{
    let c=v as f32/255.;
    if c<=0.04045{c/12.92}else{((c+0.055)/1.055).powf(2.4)}
}
/// Decode explicitly authored class-local point light values. The absence
/// of a serialized property is not permission to invent a UE inherited value;
/// a partially defined template is left for the runtime class evaluator.
pub fn original_blueprint_point_lights(
    header:&[u8],uexp:&[u8],class_path:&str,
)->Result<Vec<OriginalBlueprintPointLight>,String>{
    let cat=uobject::inspect(header)?;
    let class_name=class_path.rsplit("::").next().ok_or("source Blueprint class object missing")?;
    let expected_cdo=format!("Default__{class_name}");
    let mut class_index=None;
    let mut cdo_index=None;
    for (i,ex) in cat.exports.iter().enumerate(){
        let ordinal=i32::try_from(i+1).map_err(|_|"source Blueprint export index too large")?;
        let name=cat.resolve_package_name(ordinal);
        if name==Some(class_name) && cat.export_class_name(ex)==Some("BlueprintGeneratedClass"){
            if class_index.replace(ordinal).is_some(){
                return Err("duplicate original BlueprintGeneratedClass export".into());
            }
        }
        if name==Some(expected_cdo.as_str())&&cat.export_class_name(ex)==Some(class_name){
            if cdo_index.replace(ordinal).is_some(){
                return Err("duplicate original class CDO export".into());
            }
        }
    }
    let class_index=class_index.ok_or("original PointLight owning BlueprintGeneratedClass missing")?;
    let cdo_index=cdo_index.ok_or("original PointLight class CDO missing")?;
    let mut lights=Vec::new();
    for (i,ex) in cat.exports.iter().enumerate(){
        if cat.export_class_name(ex)!=Some("PointLightComponent") ||
            (ex.outer_index!=class_index && ex.outer_index!=cdo_index){
            continue;
        }
        let raw=cat.export_data(header,uexp,ex)?;
        let p=properties::scan(&cat,raw)?;
        if tagged_bool(&p,"bVisible")?==Some(false)||
           tagged_bool(&p,"bHiddenInGame")?==Some(true)||
           tagged_bool(&p,"bAffectsWorld")?==Some(false) {
            continue;
        }
        // These four explicit source values distinguish the torch's
        // real authored light from incomplete/inherited quest components.
        let Some(intensity)=float(&cat,raw,&p,"Intensity")? else{continue};
        let Some(radius)=float(&cat,raw,&p,"AttenuationRadius")? else{continue};
        let Some(color)=required_struct(raw,&p,"LightColor","Color",4)? else{continue};
        let Some(position)=required_struct(raw,&p,"RelativeLocation","Vector",12)? else{continue};
        if intensity<=0.||radius<=0.||intensity>1e7||radius>1e7 {
            return Err("original authored PointLight radius/intensity invalid".into());
        }
        let local=std::array::from_fn(|n|
            f32::from_le_bytes(position[n*4..(n+1)*4].try_into().unwrap())
        );
        if local.iter().any(|v|!v.is_finite()||v.abs()>1e7){
            return Err("source Blueprint light placement nonfinite/out of bounds".into());
        }
        let original=cat.source_object_path(
            i32::try_from(i+1).map_err(|_|"PointLight UObject export overflow")?
        )?;
        lights.push(OriginalBlueprintPointLight{
            source_component:original,
            relative_location_cm:local,
            // Original Unreal FColor is serialized as BGRA. A PBR light
            // uses linear RGB, not the raw 8-bit gamma-encoded channels.
            color_linear:[
                srgb8_linear(color[2]),srgb8_linear(color[1]),
                srgb8_linear(color[0])
            ],
            attenuation_radius_cm:radius,source_intensity:intensity,
        });
        if lights.len()>16{return Err("excessive authored Blueprint point lights per class".into());}
    }
    Ok(lights)
}
#[cfg(test)]
mod tests{
    use super::*;
    #[test]fn exact_ue4_bgra_light_converts_to_linear_rgb(){
        // Original authentic Castle Torch FColor is BGRA 5c a6 ff ff.
        assert_eq!(srgb8_linear(255),1.);
        let warm=[srgb8_linear(255),srgb8_linear(166),srgb8_linear(92)];
        assert!(warm[0]>warm[1]&&warm[1]>warm[2]);
        assert!((warm[1]-0.3813).abs()<0.002);
        assert!((warm[2]-0.1070).abs()<0.002);
    }
    #[test]fn missing_inherited_light_defaults_do_not_activate_quest_light(){
        let p=properties::Properties{fields:Vec::new(),bytes_consumed:8};
        assert_eq!(tagged_bool(&p,"bVisible").unwrap(),None);
    }
}
