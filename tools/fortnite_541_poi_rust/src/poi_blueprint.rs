//! Source-authored UBlueprintGeneratedClass CDO -> original high-detail mesh.
//! Cooked instance components often omit StaticMesh when inherited from
//! their Blueprint. Recover it from the class's *original* default object,
//! not from a similar actor or HLOD proxy.
use crate::{properties,uobject};
use std::collections::BTreeSet;
#[derive(Debug,Clone,PartialEq,Eq)]
pub struct AuthoredBlueprintMeshDefault {
    pub class_path:String,
    pub package_path:String,
    pub component_path:String,
    pub mesh_source_path:String,
    pub mesh_package_path:String,
}
/// UE4 FName numbered package names have #N in the source ontology.
/// Their cooked filename is _{N-1}, not "#N". Preserve the class's
/// unmodified original UObject identity separately.
pub fn source_class_package(class_path:&str)->Result<String,String>{
    let (package,object)=class_path.rsplit_once("::")
        .ok_or("authored Blueprint source class object path absent")?;
    if object.is_empty()||!object.ends_with("_C"){
        return Err("original POI inherited Blueprint has no _C class object".into());
    }
    let raw=package.strip_prefix("/Game/")
        .ok_or("source Blueprint class package outside original /Game")?;
    let (prefix,number)=match raw.rsplit_once('#'){
        Some((p,n)) if !n.is_empty()&&n.bytes().all(|b|b.is_ascii_digit())=>{
            let number=n.parse::<u32>().map_err(|_|"source FName number overflow")?;
            if number==0{return Err("numbered original Blueprint FName is zero".into());}
            (p,Some(number-1))
        },
        Some(_)=>return Err("original Blueprint class source FName malformed".into()),
        None=>(raw,None),
    };
    let path=match number{
        Some(n)=>format!("FortniteGame/Content/{prefix}_{n}"),
        None=>format!("FortniteGame/Content/{prefix}"),
    };
    if path.len()>1024||
        path.split('/').any(|s|s.is_empty()||s=="."||s=="..")||
        !path.bytes().all(|b|b.is_ascii_alphanumeric()||b==b'_'||b==b'-'||b==b'/'){
        return Err("source class package path unsafe".into());
    }
    Ok(path)
}
pub fn source_mesh_package(mesh_path:&str)->Result<String,String>{
    let (package,object)=mesh_path.rsplit_once("::")
        .ok_or("original Blueprint mesh path lacks UObject")?;
    if object.is_empty(){return Err("original inherited UStaticMesh object name missing".into());}
    // The same source FName numbered-path resolution applies to imported
    // UStaticMesh package names; never collapse numbered mesh variants.
    source_class_package(&format!("{package}::{object}_C"))
}
fn obj_property(cat:&uobject::PackageCatalog,raw:&[u8],
    key:&str)->Result<Option<i32>,String>{
    let props=properties::scan(cat,raw)?;
    let mut fields=props.fields.iter().filter(|f|f.name==key);
    let Some(field)=fields.next() else{return Ok(None)};
    if fields.next().is_some()||field.kind!="ObjectProperty"{
        return Err(format!("original CDO source {key} property ambiguous/wrong type"));
    }
    let bytes=raw.get(field.payload.clone())
        .ok_or("original Blueprint CDO property range invalid")?;
    if bytes.len()!=4{return Err("original Blueprint CDO FPackageIndex not 4 bytes".into());}
    Ok(Some(i32::from_le_bytes(bytes.try_into().unwrap())))
}
/// Parse the original Blueprint class CDO and owned StaticMeshComponent.
/// Parent actor-level StaticMesh and template component's StaticMesh must
/// agree when both explicitly authored. Their absence is NOT a placeholder.
pub fn original_blueprint_static_mesh(
    header:&[u8],uexp:&[u8],class_path:&str
)->Result<Option<AuthoredBlueprintMeshDefault>,String>{
    let catalog=uobject::inspect(header)?;
    let (_,class_name)=class_path.rsplit_once("::")
        .ok_or("original Blueprint class path missing identity")?;
    let expected=format!("Default__{class_name}");
    let package=source_class_package(class_path)?;
    let mut matches=Vec::new();
    for (i,ex) in catalog.exports.iter().enumerate(){
        let name=catalog.resolve_package_name((i+1) as i32);
        if name==Some(expected.as_str()) && catalog.export_class_name(ex)==Some(class_name){
            matches.push((i,ex));
        }
    }
    if matches.len()!=1{
        return Err(format!("original source Blueprint CDO {expected} count {}",matches.len()));
    }
    let (i,default_actor)=matches[0];
    let source=catalog.export_data(header,uexp,default_actor)?;
    let actor_mesh=obj_property(&catalog,source,"StaticMesh")?.filter(|r|*r!=0);
    let mut selected_component=None;
    let component_ref=obj_property(&catalog,source,"StaticMeshComponent")?
        .or(obj_property(&catalog,source,"RootComponent")?);
    let mut component_mesh=None;
    if let Some(ref_id)=component_ref{
        if ref_id>0{
            let component=catalog.exports.get((ref_id-1) as usize)
                .ok_or("original Blueprint CDO component index invalid")?;
            if component.outer_index!=(i+1) as i32||
                catalog.export_class_name(component)!=Some("StaticMeshComponent"){
                return Err("source Blueprint CDO StaticMeshComponent ownership invalid".into());
            }
            selected_component=Some(catalog.source_object_path(ref_id)?);
            let component_raw=catalog.export_data(header,uexp,component)?;
            component_mesh=obj_property(&catalog,component_raw,"StaticMesh")?
                .filter(|r|*r!=0);
        }
    }
    if let (Some(a),Some(b))=(actor_mesh,component_mesh){
        if a!=b{
            return Err("original Blueprint CDO actor and component StaticMesh disagree".into());
        }
    }
    let Some(mesh_ref)=component_mesh.or(actor_mesh) else{return Ok(None)};
    let identity=catalog.source_object_path(mesh_ref)?;
    let mesh_package_path=source_mesh_package(&identity)?;
    Ok(Some(AuthoredBlueprintMeshDefault{
        class_path:class_path.to_owned(),package_path:package,
        component_path:selected_component.unwrap_or_default(),
        mesh_source_path:identity,mesh_package_path,
    }))
}
#[cfg(test)]
mod tests{
    use super::*;
    #[test]fn numbered_original_blueprint_names_retain_true_retail_package(){
        assert_eq!(source_class_package(
            "/Game/Building/ActorBlueprints/Wall/Factory_Wall#4::Factory_Wall_3_C"
        ).unwrap(),"FortniteGame/Content/Building/ActorBlueprints/Wall/Factory_Wall_3");
        assert_eq!(source_mesh_package(
            "/Game/Environments/Sets/Factory/Meshes/Factory_Wall#2::Factory_Wall#2"
        ).unwrap(),"FortniteGame/Content/Environments/Sets/Factory/Meshes/Factory_Wall_1");
        assert!(source_class_package("/Engine/Test::Thing_C").is_err());
    }
}
