//! Source-authentic full-detail Fortnite Athena streamed POI placement graph.
//!
//! The original root Athena_POI_Foundations UWorld owns LF_Athena_POI_*
//! actors; each actor serializes AdditionalWorlds (TArray<FSoftObjectPath>)
//! and an owned StaticMeshComponent root with UE4 world location/rotation.
//! Thus the real 5.41 POI world transform is RECOVERABLE, not guessed.
//! An individual POI UWorld owns the real, high-resolution StaticMeshActor
//! and FortStaticMeshActor building/terrain pieces, plus Blueprint actors.
//! No HLOD-only proxies, random placement, or substitute models.
use crate::{properties,uobject::{self,PackageCatalog,PackageExport}};
use std::collections::BTreeSet;

#[derive(Debug,Clone,PartialEq)]
pub struct SourcePoiWorld {
    pub original_foundation_actor:String,
    pub source_world_asset:String,
    pub world_package:String,
    pub location_cm:[f32;3],
    pub rotation_pyr_deg:[f32;3],
    pub scale_xyz:[f32;3],
}
#[derive(Debug,Clone,PartialEq)]
pub struct SourceDetailedStaticPlacement {
    pub source_actor:String,
    pub source_actor_class:String,
    pub source_mesh_object:String,
    pub source_mesh_package:String,
    pub location_cm:[f32;3],
    pub rotation_pyr_deg:[f32;3],
    pub scale_xyz:[f32;3],
}
#[derive(Debug,Clone,Default)]
pub struct SourceDetailedPoi {
    pub source_actors:usize,
    pub static_mesh_actors:Vec<SourceDetailedStaticPlacement>,
    pub inherited_blueprint_components:usize,
    pub unique_mesh_packages:BTreeSet<String>,
}
fn field<'a>(source:&'a[u8],props:&properties::Properties,
    name:&str,kind:&str)->Result<Option<&'a[u8]>,String>{
    let mut fields=props.fields.iter().filter(|p|p.name==name);
    let Some(f)=fields.next() else{return Ok(None)};
    if fields.next().is_some() || f.kind!=kind {
        return Err(format!("authored POI source {name} wrong/ambiguous property type"));
    }
    source.get(f.payload.clone()).map(Some)
        .ok_or_else(||format!("original POI source {name} byte range invalid"))
}
fn object_ref(source:&[u8],props:&properties::Properties,key:&str)
    ->Result<Option<i32>,String>{
    let Some(bytes)=field(source,props,key,"ObjectProperty")?else{return Ok(None)};
    if bytes.len()!=4{return Err(format!("original POI FPackageIndex {key} invalid")); }
    Ok(Some(i32::from_le_bytes(bytes.try_into().unwrap())))
}
fn source_xyz(source:&[u8],props:&properties::Properties,
    key:&str,kind:&str)->Result<Option<[f32;3]>,String>{
    let Some(f)=props.fields.iter().find(|f|f.name==key)else{return Ok(None)};
    if f.kind!="StructProperty"||f.metadata.first().map(String::as_str)!=Some(kind){
        return Err(format!("original POI {key} not authored UE4 {kind}"));
    }
    let bytes=source.get(f.payload.clone())
        .ok_or("original POI transform source bytes out of bounds")?;
    if bytes.len()!=12{return Err(format!("original POI {key} expected three 32-bit floats"));}
    let v=std::array::from_fn(|i|f32::from_le_bytes(
        bytes[i*4..i*4+4].try_into().unwrap()
    ));
    if v.iter().any(|f:&f32|!f.is_finite()||f.abs()>20_000_000.){
        return Err(format!("original POI {key} has invalid coordinate"));
    }
    Ok(Some(v))
}
fn transform(catalog:&PackageCatalog,header:&[u8],uexp:&[u8],
    component:&PackageExport)->Result<([f32;3],[f32;3],[f32;3]),String>{
    let bytes=catalog.export_data(header,uexp,component)?;
    let props=properties::scan(catalog,bytes)?;
    Ok((
        source_xyz(bytes,&props,"RelativeLocation","Vector")?.unwrap_or([0.;3]),
        source_xyz(bytes,&props,"RelativeRotation","Rotator")?.unwrap_or([0.;3]),
        source_xyz(bytes,&props,"RelativeScale3D","Vector")?.unwrap_or([1.;3])
    ))
}
fn world_package(original:&str)->Result<String,String>{
    let rest=original.strip_prefix("/Game/")
        .ok_or("source POI AdditionalWorlds ref not rooted in Game")?;
    let (pkg,asset)=rest.rsplit_once('.')
        .ok_or("POI source SoftObjectPath lacks world asset")?;
    if pkg.rsplit('/').next()!=Some(asset) ||
        pkg.split('/').any(|c|c.is_empty()||c=="."||c=="..")||
        !pkg.bytes().all(|b|b.is_ascii_alphanumeric()||b==b'_'||b==b'/'||b==b'-'){
        return Err("original POI Source WorldAsset package invalid".into());
    }
    Ok(format!("FortniteGame/Content/{pkg}"))
}
/// Source path is a nested Original FPackageIndex identity:
/// /Game/Packages/MyMesh::MyMesh. No filename-based mesh guessing.
fn mesh_package(identity:&str)->Result<String,String>{
    let (package,object)=identity.rsplit_once("::")
        .ok_or("original POI mesh identity missing exported object")?;
    if object.is_empty()||object.len()>1024{return Err("original POI UStaticMesh object empty".into());}
    let pkg=package.strip_prefix("/Game/")
        .ok_or("original POI mesh not a cooked Game package")?;
    if pkg.is_empty()||pkg.split('/').any(|x|x.is_empty()||x==".."||x==".")||
        !pkg.bytes().all(|b|b.is_ascii_alphanumeric()||b==b'_'||b==b'/'||b==b'-'){
        return Err("original POI mesh package identity invalid".into());
    }
    Ok(format!("FortniteGame/Content/{pkg}"))
}
pub fn original_poi_foundation_placements(
    foundation_umap:&[u8],foundation_uexp:&[u8]
)->Result<Vec<SourcePoiWorld>,String>{
    let cat=uobject::inspect(foundation_umap)?;
    let mut worlds=Vec::new();
    for (i,actor) in cat.exports.iter().enumerate(){
        if !cat.export_class_name(actor).unwrap_or("").starts_with("LF_Athena_POI_"){
            continue;
        }
        let raw=cat.export_data(foundation_umap,foundation_uexp,actor)?;
        let props=properties::scan(&cat,raw)?;
        let Some(worlds_array)=field(raw,&props,"AdditionalWorlds","ArrayProperty")?
            else{continue};
        if worlds_array.len()<4{return Err("source AdditionalWorlds missing count".into());}
        let count=u32::from_le_bytes(worlds_array[..4].try_into().unwrap()) as usize;
        if count>16||worlds_array.len()!=4+count*12{
            return Err("original POI AdditionalWorlds SoftObjectPath array length invalid".into());
        }
        let root=object_ref(raw,&props,"RootComponent")?
            .ok_or("source foundation actor has no owned root")?;
        if root<=0{return Err("original foundation root component not local UObject".into());}
        let root_component=cat.exports.get((root-1) as usize)
            .ok_or("original foundation root object index invalid")?;
        if root_component.outer_index!=(i+1) as i32 ||
            cat.export_class_name(root_component)!=Some("StaticMeshComponent"){
            return Err("original POI foundation component ownership/class mismatch".into());
        }
        let (location_cm,rotation_pyr_deg,scale_xyz)=
            transform(&cat,foundation_umap,foundation_uexp,root_component)?;
        for nth in 0..count{
            let off=4+nth*12;
            let name_idx=u32::from_le_bytes(worlds_array[off..off+4].try_into().unwrap()) as usize;
            let number=u32::from_le_bytes(worlds_array[off+4..off+8].try_into().unwrap());
            let subpath=i32::from_le_bytes(worlds_array[off+8..off+12].try_into().unwrap());
            if number!=0||subpath!=0{
                return Err("original POI AdditionalWorlds unsupported numbered/subpath".into());
            }
            let world_asset=cat.names.get(name_idx)
                .ok_or("source POI AdditionalWorlds FName missing")?.clone();
            let package=world_package(&world_asset)?;
            worlds.push(SourcePoiWorld{
                original_foundation_actor:cat.source_object_path((i+1) as i32)?,
                source_world_asset:world_asset,
                world_package:package,location_cm,rotation_pyr_deg,scale_xyz,
            });
            if worlds.len()>512{return Err("source POI foundation level count exceeds bound".into());}
        }
    }
    let mut unique=BTreeSet::new();
    for world in &worlds{
        if !unique.insert(world.world_package.clone()){
            return Err("source POI has duplicate world foundation placement".into());
        }
    }
    if worlds.is_empty(){return Err("no original POI Foundation AdditionalWorlds found".into());}
    Ok(worlds)
}
pub fn original_poi_direct_static_actors(
    poi_umap:&[u8],poi_uexp:&[u8],
)->Result<SourceDetailedPoi,String>{
    let cat=uobject::inspect(poi_umap)?;
    let mut result=SourceDetailedPoi::default();
    for (i,actor) in cat.exports.iter().enumerate(){
        let kind=cat.export_class_name(actor).unwrap_or("");
        if kind=="FortHLODSMActor" {continue;}
        // In Fortnite, Blueprint actors often inherit a StaticMeshComponent
        // with an unset local StaticMesh. That mesh lives in the CDO; it is
        // explicitly counted as unresolved rather than fabricated.
        if kind.ends_with("Component") ||kind=="World"||kind=="Level"{
            continue;
        }
        let raw=cat.export_data(poi_umap,poi_uexp,actor)?;
        let props=match properties::scan(&cat,raw){Ok(x)=>x,Err(_)=>continue};
        let Some(root)=object_ref(raw,&props,"RootComponent")? else{continue};
        if root<=0{continue;}
        let Some(comp)=cat.exports.get((root-1) as usize) else{continue};
        if comp.outer_index!=(i+1) as i32 ||
            cat.export_class_name(comp)!=Some("StaticMeshComponent"){
            continue;
        }
        result.source_actors+=1;
        let component_raw=cat.export_data(poi_umap,poi_uexp,comp)?;
        let component_props=properties::scan(&cat,component_raw)?;
        let Some(mesh_ref)=object_ref(component_raw,&component_props,"StaticMesh")?
            else{result.inherited_blueprint_components+=1;continue};
        if mesh_ref==0{result.inherited_blueprint_components+=1;continue;}
        let identity=cat.source_object_path(mesh_ref)?;
        let package=match mesh_package(&identity){
            Ok(pkg)=>pkg,
            Err(_)=>{result.inherited_blueprint_components+=1;continue},
        };
        let (location_cm,rotation_pyr_deg,scale_xyz)=
            transform(&cat,poi_umap,poi_uexp,comp)?;
        result.unique_mesh_packages.insert(package.clone());
        result.static_mesh_actors.push(SourceDetailedStaticPlacement{
            source_actor:cat.source_object_path((i+1) as i32)?,
            source_actor_class:kind.to_owned(),
            source_mesh_object:identity,source_mesh_package:package,
            location_cm,rotation_pyr_deg,scale_xyz,
        });
        if result.static_mesh_actors.len()>100_000{
            return Err("source POI full-resolution instance bound exceeded".into());
        }
    }
    Ok(result)
}
/// Source-local mesh vertices remain UE4 centimetres, converted separately
/// to engine Y-up metres. These are world-space 3x4 row transforms for the
/// shared renderer; parent=POI foundation, child=individual detailed actor.
pub fn engine_rows(position_cm:[f32;3],rotation_deg:[f32;3],
    scale:[f32;3])->[[f32;4];3]{
    let [pitch,yaw,roll]=rotation_deg.map(f32::to_radians);
    let (sp,cp)=pitch.sin_cos();let (sy,cy)=yaw.sin_cos();
    let (sr,cr)=roll.sin_cos();
    let x=[cp*cy,cp*sy,sp];
    let y=[sr*sp*cy-cr*sy,sr*sp*sy+cr*cy,-sr*cp];
    let z=[-(cr*sp*cy+sr*sy),cy*sr-cr*sp*sy,cr*cp];
    let into=|v:[f32;3]|[v[0],v[2],-v[1]];
    let [sx,sy,sz]=scale;
    let ex=into(x).map(|v|v*sx);let ey=into(z).map(|v|v*sz);
    let ez=into(y).map(|v|-v*sy);
    let t=into(position_cm).map(|v|v*0.01);
    [[ex[0],ey[0],ez[0],t[0]],
     [ex[1],ey[1],ez[1],t[1]],
     [ex[2],ey[2],ez[2],t[2]]]
}
pub fn compose_engine_rows(parent:[[f32;4];3],child:[[f32;4];3])
    ->[[f32;4];3]
{
    std::array::from_fn(|r|{
        std::array::from_fn(|c|{
            (0..3).map(|k|parent[r][k]*child[k][c]).sum::<f32>()+
                if c==3{parent[r][3]}else{0.}
        })
    })
}
#[cfg(test)]
mod tests{
    use super::*;
    #[test]fn correct_authored_world_assets(){
        assert_eq!(world_package(
            "/Game/Athena/Maps/POI/Athena_POI_ToiletFactory_001.Athena_POI_ToiletFactory_001"
        ).unwrap(),"FortniteGame/Content/Athena/Maps/POI/Athena_POI_ToiletFactory_001");
        assert!(world_package("/Game/POI/World.Wrong").is_err());
    }
    #[test]fn source_transforms_compose_without_fake_world_origins(){
        let base=engine_rows([-62976.,-64512.,0.],[0.,-90.,0.],[1.;3]);
        let local=engine_rows([100.,200.,300.],[0.;3],[1.;3]);
        let joined=compose_engine_rows(base,local);
        // Source -90-degree yaw maps +X to -Y; world (-62776,-64612,300)
        assert!((joined[0][3]+627.76).abs()<0.001);
        assert!((joined[1][3]-3.).abs()<0.001);
        assert!((joined[2][3]-646.12).abs()<0.001);
    }
    #[test]fn detect_negative_scale_preserve_source_reflection(){
        let rows=engine_rows([0.;3],[0.;3],[-1.,1.,1.]);
        assert_eq!(rows[0][0],-1.);
        assert_eq!(rows[1][1],1.);
        assert_eq!(rows[2][2],1.);
    }
}
