//! Original UE4.21 Athena root-map HLOD placements.
//!
//! Retains source StaticMesh object references, actor/scene transforms and
//! original level relationships exactly. NO guessed proxy boxes, invented
//! mesh vertices, game-specific rendering path or fake structure completion.
//! Visual admission waits for a verified native UStaticMesh LOD decoder.
use crate::{properties, uobject};
use std::collections::{BTreeMap,BTreeSet};

#[derive(Debug,Clone,PartialEq)]
pub struct SourceHlodPlacement {
    pub actor_reference:i32,
    pub component_reference:i32,
    pub actor_source_path:String,
    pub mesh_object_source_path:String,
    pub mesh_source_package:String,
    /// Original UFortHLODSMActor UniqueWorldLocation, centimetres, UE Z-up.
    pub authored_world_location_cm:[f32;3],
    /// Original UStaticMeshComponent RelativeLocation, centimetres.
    pub component_relative_location_cm:[f32;3],
    /// Original FRotator (Pitch,Yaw,Roll), degrees; not a fabricated quaternion.
    pub component_relative_rotation_pyr:[f32;3],
    /// Original component Scale3D; missing cooked source property is UE CDO 1.
    pub component_relative_scale:[f32;3],
}
#[derive(Debug,Clone,Default)]
pub struct AuthoredHlodScene {
    pub actors:Vec<SourceHlodPlacement>,
    pub unique_mesh_packages:BTreeSet<String>,
    pub referenced_original_mesh_objects:BTreeMap<String,usize>,
    pub relative_rotation_serialized:usize,
    pub relative_scale_serialized:usize,
    pub actors_with_location_disagreement:usize,
}
fn property<'a>(
    source:&'a [u8],
    fields:&'a properties::Properties,
    key:&str,
    kind:&str,
)->Result<Option<(&'a properties::Property,&'a [u8])>,String>{
    let mut matching=fields.fields.iter().filter(|f|f.name==key);
    let Some(field)=matching.next() else{return Ok(None)};
    if matching.next().is_some() ||field.kind!=kind {
        return Err(format!("original Athena HLOD unexpected/repeated {key}: {}",field.kind));
    }
    let raw=source.get(field.payload.clone())
        .ok_or_else(||format!("original HLOD {key} span exceeds source UObject"))?;
    Ok(Some((field,raw)))
}
fn source_ref(source:&[u8],properties:&properties::Properties,key:&str)->Result<i32,String>{
    let Some((_,raw))=property(source,properties,key,"ObjectProperty")? else{
        return Err(format!("original HLOD required ObjectProperty {key} missing"));
    };
    if raw.len()!=4{return Err(format!("original HLOD ObjectProperty {key} not four bytes"));}
    Ok(i32::from_le_bytes(raw.try_into().unwrap()))
}
fn source_xyz(source:&[u8],props:&properties::Properties,name:&str,expected_type:&str)
    ->Result<Option<[f32;3]>,String>
{
    let Some((prop,raw))=property(source,props,name,"StructProperty")? else{return Ok(None)};
    if prop.metadata.first().map(String::as_str)!=Some(expected_type) ||raw.len()!=12{
        return Err(format!("source HLOD {name} must be original 12-byte {expected_type}"));
    }
    let mut output=[0f32;3];
    for (i,result) in output.iter_mut().enumerate(){
        *result=f32::from_le_bytes(raw[i*4..i*4+4].try_into().unwrap());
        if !result.is_finite() ||result.abs()>100_000_000.{
            return Err(format!("original HLOD {name} value is nonfinite/unbounded"));
        }
    }
    Ok(Some(output))
}
fn original_mesh_package(path:&str)->Result<String,String>{
    let mut split=path.split("::");
    let package=split.next().ok_or("empty source StaticMesh path")?;
    let object=split.next().ok_or("StaticMesh reference has no original UObject export")?;
    if object.is_empty()||package.len()>1024||!package.starts_with("/Game/")||
        package.split('/').any(|s|s=="."||s==".."||s.contains('\\')||s.contains(':'))
        ||!object.starts_with("SM_"){
        return Err(format!("invalid HLOD original UStaticMesh identity {path}"));
    }
    Ok(format!("FortniteGame/Content/{}",&package[6..]))
}
/// Decode the source root Athena Terrain map HLOD actors. Strictly matches
/// actor.StaticMeshComponent FPackageIndex to source export class and then
/// reads that component's original mesh ObjectProperty. No name matching.
pub fn inspect_root_original_hlod(
    source_umap:&[u8],source_uexp:&[u8]
)->Result<AuthoredHlodScene,String>{
    let catalog=uobject::inspect(source_umap)?;
    if catalog.exports.len()>200_000{
        return Err("original Athena HLOD map exceeds source UObject bound".into());
    }
    let mut scene=AuthoredHlodScene::default();
    let mut visited=BTreeSet::<i32>::new();
    for (index,actor) in catalog.exports.iter().enumerate(){
        if catalog.export_class_name(actor)!=Some("FortHLODSMActor"){continue;}
        let actor_reference=i32::try_from(index+1)
            .map_err(|_|"original HLOD actor index exceeds i32")?;
        let serialized=catalog.export_data(source_umap,source_uexp,actor)?;
        let fields=properties::scan(&catalog,serialized)?;
        let component_reference=source_ref(serialized,&fields,"StaticMeshComponent")?;
        let root_reference=source_ref(serialized,&fields,"RootComponent")?;
        if component_reference<=0 ||root_reference!=component_reference ||
            !visited.insert(component_reference){
            return Err(format!("source HLOD actor #{actor_reference} has invalid/reused root StaticMeshComponent"));
        }
        let component=catalog.exports.get((component_reference-1) as usize)
            .ok_or("original HLOD StaticMeshComponent reference outside exports")?;
        if catalog.export_class_name(component)!=Some("StaticMeshComponent")
            ||component.outer_index!=actor_reference {
            return Err(format!("HLOD actor #{actor_reference} points at unrelated/non StaticMesh component"));
        }
        let object=catalog.export_data(source_umap,source_uexp,component)?;
        let component_props=properties::scan(&catalog,object)?;
        let mesh_reference=source_ref(object,&component_props,"StaticMesh")?;
        if mesh_reference==0{return Err("source HLOD component has missing mesh reference".into());}
        let mesh_object_source_path=catalog.source_object_path(mesh_reference)?;
        let mesh_source_package=original_mesh_package(&mesh_object_source_path)?;
        let authored_world_location_cm=source_xyz(
            serialized,&fields,"UniqueWorldLocation","Vector"
        )?.ok_or("original HLOD actor lacks authored UniqueWorldLocation")?;
        let component_relative_location_cm=source_xyz(
            object,&component_props,"RelativeLocation","Vector"
        )?.ok_or("original HLOD component lacks RelativeLocation")?;
        let rotation=source_xyz(object,&component_props,"RelativeRotation","Rotator")?;
        let scale=source_xyz(object,&component_props,"RelativeScale3D","Vector")?;
        if rotation.is_some(){scene.relative_rotation_serialized+=1;}
        if scale.is_some(){scene.relative_scale_serialized+=1;}
        // Record rather than silently overwriting two independent Unreal
        // source placements: any disagreements must be understood before
        // assigning a transform to actual original mesh geometry.
        if (0..3).any(|axis|(
            authored_world_location_cm[axis]-component_relative_location_cm[axis]
        ).abs()>1.0){
            scene.actors_with_location_disagreement+=1;
        }
        scene.unique_mesh_packages.insert(mesh_source_package.clone());
        *scene.referenced_original_mesh_objects
            .entry(mesh_object_source_path.clone()).or_default()+=1;
        scene.actors.push(SourceHlodPlacement{
            actor_reference,component_reference,
            actor_source_path:catalog.source_object_path(actor_reference)?,
            mesh_object_source_path,mesh_source_package,
            authored_world_location_cm,component_relative_location_cm,
            component_relative_rotation_pyr:rotation.unwrap_or([0.;3]),
            component_relative_scale:scale.unwrap_or([1.;3]),
        });
    }
    if scene.actors.is_empty(){
        return Err("original Athena root source has no authenticated HLOD actors".into());
    }
    Ok(scene)
}
#[cfg(test)]
mod tests{
    use super::*;
    #[test]fn original_mesh_package_keeps_authored_package_not_flat_name(){
        assert_eq!(
            original_mesh_package("/Game/Athena/Maps/Buildings/1x1/HLOD/Example::SM_Example#3").unwrap(),
            "FortniteGame/Content/Athena/Maps/Buildings/1x1/HLOD/Example"
        );
        assert!(original_mesh_package("/Game/Athena/Map/../Example::SM_Example").is_err());
        assert!(original_mesh_package("/Game/Athena/Map/Example").is_err());
        assert!(original_mesh_package("/Engine/Fake::SM_Example").is_err());
    }
}
