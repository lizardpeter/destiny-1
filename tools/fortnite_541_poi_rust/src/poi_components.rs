//! Original UE4.21 Blueprint SCS child StaticMeshComponent geometry.
//! Cooked CDO root StaticMesh is not the complete actor: source SCS nodes
//! may own other mesh templates, such as torch flame and bloom planes.
use crate::{poi_blueprint,properties,uobject};
#[derive(Debug,Clone,PartialEq)]
pub struct OriginalBlueprintChildMesh{
    pub source_component:String,
    pub mesh_source_path:String,
    pub mesh_package_path:String,
    pub relative_location_cm:[f32;3],
    pub relative_rotation_pyr:[f32;3],
    pub relative_scale:[f32;3],
    pub override_materials:Vec<Option<String>>,
}
fn object(props:&properties::Properties,raw:&[u8],name:&str)
    ->Result<Option<i32>,String>{
    let mut x=props.fields.iter().filter(|p|p.name==name);
    let Some(p)=x.next() else{return Ok(None)};
    if x.next().is_some()||p.kind!="ObjectProperty"||p.payload.len()!=4{
        return Err(format!("source SCS {name} must be a unique UObject reference"));
    }
    Ok(Some(i32::from_le_bytes(raw[p.payload.clone()].try_into().unwrap())))
}
fn vec3(props:&properties::Properties,raw:&[u8],name:&str,kind:&str,default:[f32;3])
    ->Result<[f32;3],String>{
    let mut x=props.fields.iter().filter(|p|p.name==name);
    let Some(p)=x.next() else{return Ok(default)};
    if x.next().is_some()||p.kind!="StructProperty"||
       p.metadata.first().map(String::as_str)!=Some(kind)||p.payload.len()!=12{
        return Err(format!("source SCS {name} typed FVector/FRotator invalid"));
    }
    let b=&raw[p.payload.clone()];
    let n=std::array::from_fn(|i|f32::from_le_bytes(b[4*i..4*i+4].try_into().unwrap()));
    if n.iter().any(|x|!x.is_finite()||x.abs()>1e7){
        return Err(format!("source SCS {name} vector is nonfinite/out-of-bounds"));
    }
    Ok(n)
}
fn materials(cat:&uobject::PackageCatalog,props:&properties::Properties,raw:&[u8])
    ->Result<Vec<Option<String>>,String>{
    let mut x=props.fields.iter().filter(|p|p.name=="OverrideMaterials");
    let Some(p)=x.next() else{return Ok(Vec::new())};
    if x.next().is_some()||p.kind!="ArrayProperty"||
       p.metadata.first().map(String::as_str)!=Some("ObjectProperty"){
        return Err("source SCS OverrideMaterials is not UObject array".into());
    }
    let b=&raw[p.payload.clone()];
    if b.len()<4{return Err("original SCS override count absent".into());}
    let count=u32::from_le_bytes(b[..4].try_into().unwrap()) as usize;
    if count>32||b.len()!=4+count*4{
        return Err("original SCS override material array truncated or excessive".into());
    }
    (0..count).map(|i|{
        let ref_id=i32::from_le_bytes(b[4+4*i..8+4*i].try_into().unwrap());
        if ref_id==0{Ok(None)}else{cat.source_object_path(ref_id).map(Some)}
    }).collect()
}
pub fn original_blueprint_child_meshes(
    header:&[u8],uexp:&[u8],class_path:&str,
)->Result<Vec<OriginalBlueprintChildMesh>,String>{
    let cat=uobject::inspect(header)?;
    let class_name=class_path.rsplit("::").next()
        .ok_or("source SCS Blueprint class identity absent")?;
    let mut cls=cat.exports.iter().enumerate().filter(|(i,e)|
        cat.resolve_package_name((i+1) as i32)==Some(class_name) &&
        cat.export_class_name(e)==Some("BlueprintGeneratedClass"));
    let (i,_)=cls.next().ok_or("source BlueprintGeneratedClass export not found")?;
    if cls.next().is_some(){return Err("source Blueprint class duplicated".into());}
    let cls_ref=(i+1) as i32;
    let cdo_name=format!("Default__{class_name}");
    let mut cdo=cat.exports.iter().enumerate().filter(|(i,ex)|
        cat.resolve_package_name((i+1) as i32)==Some(cdo_name.as_str()) &&
        cat.export_class_name(ex)==Some(class_name));
    let (_,cdo_export)=cdo.next().ok_or("source SCS owning class CDO missing")?;
    if cdo.next().is_some(){return Err("source SCS class CDO duplicated".into());}
    let cdo_data=cat.export_data(header,uexp,cdo_export)?;
    let cdo_props=properties::scan(&cat,cdo_data)?;
    let root_ref=object(&cdo_props,cdo_data,"RootComponent")?
        .ok_or("source SCS Blueprint CDO RootComponent absent")?;
    if root_ref<=0{return Err("source SCS CDO root is not an owned component".into());}
    let root_name=cat.resolve_package_name(root_ref)
        .ok_or("source SCS CDO root FName missing")?.to_owned();
    let prefix=format!("{class_name}::");
    let mut output=Vec::new();
    for (index,node) in cat.exports.iter().enumerate(){
        if cat.export_class_name(node)!=Some("SCS_Node"){continue;}
        if !cat.source_object_path((index+1) as i32)?.starts_with(&prefix){continue;}
        let data=cat.export_data(header,uexp,node)?;
        let props=properties::scan(&cat,data)?;
        let Some(kind)=object(&props,data,"ComponentClass")? else{continue};
        if kind==0 || cat.source_object_path(kind)?!="/Script/Engine::StaticMeshComponent"{continue;}
        let Some(template_ref)=object(&props,data,"ComponentTemplate")? else{continue};
        if template_ref<=0{return Err("source SCS template is not owned exported UObject".into());}
        let template=cat.exports.get((template_ref-1) as usize)
            .ok_or("source SCS ComponentTemplate missing")?;
        if cat.export_class_name(template)!=Some("StaticMeshComponent")||
           template.outer_index!=cls_ref{
            return Err("source SCS child component ownership/class incorrect".into());
        }
        // The original castle torch Flame/Bloom SCS nodes explicitly
        // attach to the native CDO root StaticMeshComponent0. Following
        // that root object is exact; attaching to an unknown SCS parent
        // without its own transform chain is not.
        let mut parent=props.fields.iter().filter(|p|
            p.name=="ParentComponentOrVariableName");
        if let Some(name)=parent.next(){
            if parent.next().is_some()||name.kind!="NameProperty"||
                name.payload.len()!=8{
                return Err("original SCS parent FName malformed".into());
            }
            let b=&data[name.payload.clone()];
            let id=u32::from_le_bytes(b[..4].try_into().unwrap()) as usize;
            let number=u32::from_le_bytes(b[4..8].try_into().unwrap());
            let original=cat.names.get(id).ok_or("original SCS parent FName absent")?;
            let parent_name=if number==0{original.to_owned()}
                else{format!("{original}#{number}")};
            if parent_name!=root_name{continue;}
            let mut native=props.fields.iter().filter(|p|
                p.name=="bIsParentComponentNative");
            let flag=native.next().ok_or("original SCS parent root native flag absent")?;
            if native.next().is_some()||flag.kind!="BoolProperty"||
                flag.metadata.first().map(String::as_str)!=Some("bool_value=1"){
                continue;
            }
        }
        if props.fields.iter().any(|p|p.name=="ParentComponentOwnerClassName"){
            continue;
        }
        let bytes=cat.export_data(header,uexp,template)?;
        let cp=properties::scan(&cat,bytes)?;
        let Some(mesh_ref)=object(&cp,bytes,"StaticMesh")? else{continue};
        if mesh_ref==0{continue;}
        let identity=cat.source_object_path(mesh_ref)?;
        let package=poi_blueprint::source_mesh_package(&identity)?;
        let position=vec3(&cp,bytes,"RelativeLocation","Vector",[0.;3])?;
        let rotation=vec3(&cp,bytes,"RelativeRotation","Rotator",[0.;3])?;
        let scale=vec3(&cp,bytes,"RelativeScale3D","Vector",[1.;3])?;
        if scale.iter().any(|x|x.abs()<1e-6){
            return Err("source SCS child component scale degenerate".into());
        }
        output.push(OriginalBlueprintChildMesh{
            source_component:cat.source_object_path(template_ref)?,
            mesh_source_path:identity,mesh_package_path:package,
            relative_location_cm:position,relative_rotation_pyr:rotation,
            relative_scale:scale,
            override_materials:materials(&cat,&cp,bytes)?,
        });
        if output.len()>32{return Err("too many original Blueprint SCS mesh templates".into());}
    }
    Ok(output)
}
#[cfg(test)]
mod tests{
    use super::*;
    #[test]fn implicit_unreal_scs_transform_is_identity(){
        let b=Vec::<u8>::new();
        let p=properties::Properties{fields:Vec::new(),bytes_consumed:0};
        assert_eq!(vec3(&p,&b,"RelativeRotation","Rotator",[0.;3]).unwrap(),[0.;3]);
        assert_eq!(vec3(&p,&b,"RelativeScale3D","Vector",[1.;3]).unwrap(),[1.;3]);
    }
}
