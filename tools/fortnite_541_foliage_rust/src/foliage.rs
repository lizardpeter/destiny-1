//! Original Fortnite 5.41 UE4.21 instanced foliage source decoder.
//! Retail HedgeMaze contains 3320 exact FMatrix records. Root/LS01 have zero.
use crate::{properties,uobject};
use std::collections::BTreeSet;
const MAX_INSTANCES:usize=200_000;
#[derive(Debug,Clone,PartialEq)]
pub struct OriginalFoliageInstance { pub source_matrix:[f32;16] }
impl OriginalFoliageInstance {
    /// Original Unreal row-major matrix to engine Y-up metres.
    pub fn engine_rows(&self)->[[f32;4];3]{
        let m=&self.source_matrix;
        [
            [m[0],m[8],-m[4],m[12]*0.01],
            [m[2],m[10],-m[6],m[14]*0.01],
            [-m[1],-m[9],m[5],-m[13]*0.01],
        ]
    }
}
#[derive(Debug,Clone)]
pub struct AuthoredFoliageComponent {
    pub source_component:String,
    pub mesh_identity:String,
    pub mesh_package:String,
    pub instances:Vec<OriginalFoliageInstance>,
    pub trailing_native_bytes:usize,
}
#[derive(Debug,Default,Clone)]
pub struct AuthoredFoliageLevel {
    pub components:Vec<AuthoredFoliageComponent>,
    pub total_instances:usize,
    pub mesh_packages:BTreeSet<String>,
}
fn u32_at(b:&[u8],p:usize)->Result<u32,String>{
    Ok(u32::from_le_bytes(b.get(p..p+4)
        .ok_or("source foliage property truncated")?.try_into().unwrap()))
}
/// Native UE4.21 component serial data: two zero flags, format=1,
/// matrix_stride=64, count, count original 4x4 FMatrix transforms.
/// The remaining serialized bytes are preserved as a boundary only.
pub fn decode_original_foliage_matrices(native:&[u8])
    ->Result<(Vec<OriginalFoliageInstance>,usize),String>
{
    if native.len()<36||native.len()>64*1024*1024{
        return Err("source foliage serialized data size out of bounds".into());
    }
    if u32_at(native,0)?!=0||u32_at(native,4)?!=0||
        u32_at(native,8)?!=1||u32_at(native,12)?!=64{
        return Err("unrecognized source cooked foliage transform format".into());
    }
    let count=u32_at(native,16)? as usize;
    if count>MAX_INSTANCES{return Err("source foliage count exceeds safe bound".into());}
    let end=count.checked_mul(64).and_then(|n|n.checked_add(20))
        .ok_or("source foliage matrix length overflow")?;
    if end>native.len(){return Err("source foliage matrices truncated".into());}
    let mut output=Vec::with_capacity(count);
    for bytes in native[20..end].chunks_exact(64){
        let mut m=[0f32;16];
        for (i,v) in m.iter_mut().enumerate(){
            *v=f32::from_le_bytes(bytes[i*4..i*4+4].try_into().unwrap());
            if !v.is_finite()||v.abs()>20_000_000.{
                return Err("source foliage matrix contains nonfinite value".into());
            }
        }
        if m[3].abs()>0.0001||m[7].abs()>0.0001||
            m[11].abs()>0.0001||(m[15]-1.).abs()>0.0001{
            return Err("source foliage matrix is not affine".into());
        }
        output.push(OriginalFoliageInstance{source_matrix:m});
    }
    Ok((output,native.len()-end))
}
/// Parse actual FoliageInstancedStaticMeshComponent source objects,
/// excluding shadow proxy InstancedStaticMeshComponent and other non-foliage.
pub fn inspect_original_foliage_level(
    umap:&[u8],uexp:&[u8],
)->Result<AuthoredFoliageLevel,String>{
    let catalog=uobject::inspect(umap)?;
    let mut level=AuthoredFoliageLevel::default();
    for (idx,export) in catalog.exports.iter().enumerate(){
        if catalog.export_class_name(export)!=Some("FoliageInstancedStaticMeshComponent"){
            continue;
        }
        if level.components.len()>=10_000{return Err("source foliage component bound exceeded".into());}
        let raw=catalog.export_data(umap,uexp,export)?;
        let props=properties::scan(&catalog,raw)?;
        let mut fields=props.fields.iter().filter(|f|f.name=="StaticMesh");
        let mesh=fields.next().ok_or("source foliage component has no StaticMesh identity")?;
        if fields.next().is_some()||mesh.kind!="ObjectProperty"{
            return Err("ambiguous original foliage StaticMesh ref".into());
        }
        let raw_ref=raw.get(mesh.payload.clone()).ok_or("foliage mesh ref outside source")?;
        if raw_ref.len()!=4{return Err("source foliage FPackageIndex length invalid".into());}
        let identity=catalog.source_object_path(i32::from_le_bytes(raw_ref.try_into().unwrap()))?;
        let package=identity.split("::").next().ok_or("foliage source mesh missing package")?;
        if !package.starts_with("/Game/")||package.len()>1024 ||
            package.trim_start_matches('/').split('/').any(|part|part==".."||part=="."||part.is_empty()){
            return Err("untrusted original foliage package identity".into());
        }
        let mesh_package=format!("FortniteGame/Content/{}",&package[6..]);
        let native=raw.get(props.bytes_consumed..)
            .ok_or("original foliage native instance records absent")?;
        let (instances,trailing_native_bytes)=decode_original_foliage_matrices(native)?;
        let reorder=props.fields.iter().filter(|p|p.name=="InstanceReorderTable")
            .collect::<Vec<_>>();
        if reorder.len()>1{return Err("duplicate original foliage InstanceReorderTable".into());}
        if let Some(field)=reorder.first(){
            if field.kind!="ArrayProperty"{return Err("foliage reorder source type invalid".into());}
            let bytes=raw.get(field.payload.clone())
                .ok_or("original foliage reorder source range invalid")?;
            if bytes.len()!=4+instances.len()*4 ||
                u32_at(bytes,0)? as usize!=instances.len(){
                return Err("source foliage reorder count differs from original affine matrices".into());
            }
        }
        level.total_instances+=instances.len();
        level.mesh_packages.insert(mesh_package.clone());
        level.components.push(AuthoredFoliageComponent{
            source_component:catalog.source_object_path((idx+1) as i32)?,
            mesh_identity:identity,mesh_package,instances,trailing_native_bytes,
        });
    }
    Ok(level)
}
#[cfg(test)]
mod tests {
    use super::*;
    fn native(n:usize)->Vec<u8>{
        let mut b=vec![0u8;36+n*64];
        b[8..12].copy_from_slice(&1u32.to_le_bytes());
        b[12..16].copy_from_slice(&64u32.to_le_bytes());
        b[16..20].copy_from_slice(&(n as u32).to_le_bytes());
        for x in 0..n {
            for (i,v) in [1.,0.,0.,0.,0.,1.,0.,0.,
                          0.,0.,1.,0.,100.,200.,300.,1f32].iter().enumerate(){
                let p=20+x*64+i*4;b[p..p+4].copy_from_slice(&v.to_le_bytes());
            }
        }
        b
    }
    #[test]fn original_matrix_converts_unreal_into_engine_metres(){
        let (m,tail)=decode_original_foliage_matrices(&native(1)).unwrap();
        assert_eq!(tail,16);
        assert_eq!(m[0].engine_rows(),[
            [1.,0.,0.,1.],[0.,1.,0.,3.],[0.,0.,1.,-2.],
        ]);
    }
    #[test]fn original_zero_instances_do_not_generate_random_plants(){
        let (m,tail)=decode_original_foliage_matrices(&native(0)).unwrap();
        assert!(m.is_empty());assert_eq!(tail,16);
    }
    #[test]fn malformed_source_matrix_is_rejected(){
        let mut b=native(1);
        b[20+60..20+64].copy_from_slice(&0f32.to_le_bytes());
        assert!(decode_original_foliage_matrices(&b).is_err());
        let mut b=native(1);b.truncate(48);
        assert!(decode_original_foliage_matrices(&b).is_err());
    }
}
