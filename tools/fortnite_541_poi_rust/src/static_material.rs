//! Original UE4.21 StaticMesh FStaticMaterial identity closure.
//!
//! Material slots are FStaticMaterial tagged source structs. Each LOD section
//! stores MaterialIndex; that index selects an original MaterialInterface
//! UObject and original authored MaterialSlotName. Never infer materials
//! from filenames or use just the first imported material in the package.
use crate::{properties,uobject::{PackageCatalog,PackageExport}};
#[derive(Debug,Clone,PartialEq,Eq)]
pub struct OriginalStaticMaterial {
    pub slot:u32,
    pub material_interface:Option<String>,
    pub material_slot_name:String,
    pub imported_slot_name:String,
}
fn fname(catalog:&PackageCatalog,raw:&[u8])->Result<String,String>{
    if raw.len()!=8{return Err("original UE StaticMaterial FName width mismatch".into());}
    let index=u32::from_le_bytes(raw[..4].try_into().unwrap()) as usize;
    let number=u32::from_le_bytes(raw[4..8].try_into().unwrap());
    let name=catalog.names.get(index).ok_or("original StaticMaterial unknown source FName")?;
    Ok(if number==0{name.clone()}else{format!("{name}#{number}")})
}
fn exact_field<'a>(
    fields:&properties::Properties,bytes:&'a[u8],
    field:&str,kind:&str,width:usize,
)->Result<&'a[u8],String>{
    let mut hits=fields.fields.iter().filter(|p|p.name==field);
    let p=hits.next().ok_or_else(||format!("source FStaticMaterial {field} absent"))?;
    if hits.next().is_some()||p.kind!=kind||p.payload.len()!=width{
        return Err(format!("original FStaticMaterial {field} duplicated or wrong tagged type"));
    }
    bytes.get(p.payload.clone()).ok_or_else(||"original FStaticMaterial field out of bounds".into())
}
fn with_none_terminator(
    catalog:&PackageCatalog,raw:&[u8],
)->Result<Vec<u8>,String>{
    let none=catalog.names.iter().position(|x|x=="None")
        .ok_or("source mesh package lacks FName None terminator")?;
    let none=u32::try_from(none).map_err(|_|"original source name index overflow")?;
    let mut out=Vec::with_capacity(raw.len()+8);
    out.extend_from_slice(raw);
    out.extend_from_slice(&none.to_le_bytes());
    out.extend_from_slice(&0u32.to_le_bytes());
    Ok(out)
}
pub fn from_mesh_export(
    catalog:&PackageCatalog,header:&[u8],uexp:&[u8],
    source_object:&str,
)->Result<Vec<OriginalStaticMaterial>,String>{
    let mut source=None;
    for (index,e) in catalog.exports.iter().enumerate(){
        if catalog.export_class_name(e)!=Some("StaticMesh"){continue;}
        let object=catalog.source_object_path((index+1) as i32)?;
        if object.split("::").last()!=Some(source_object){continue;}
        if source.replace(e).is_some(){
            return Err(format!("ambiguous original UStaticMesh object for material slots {source_object}"));
        }
    }
    let mesh=source.ok_or_else(||format!("original mesh material object not found: {source_object}"))?;
    inspect_static_materials(catalog,header,uexp,mesh)
}
pub fn inspect_static_materials(
    catalog:&PackageCatalog,header:&[u8],uexp:&[u8],
    mesh:&PackageExport,
)->Result<Vec<OriginalStaticMaterial>,String>{
    if catalog.export_class_name(mesh)!=Some("StaticMesh"){
        return Err("material slot reader requires original StaticMesh export".into());
    }
    let data=catalog.export_data(header,uexp,mesh)?;
    let props=properties::scan(catalog,data)?;
    let mut arr=props.fields.iter().filter(|p|p.name=="StaticMaterials");
    let original=arr.next().ok_or("original mesh has no source StaticMaterials")?;
    if arr.next().is_some()||original.kind!="ArrayProperty"||
        original.metadata.first().map(String::as_str)!=Some("StructProperty"){
        return Err("original source StaticMaterials is not unique StructProperty array".into());
    }
    let b=&data[original.payload.clone()];
    if b.len()<4{return Err("source StaticMaterials array count missing".into());}
    let count=u32::from_le_bytes(b[..4].try_into().unwrap()) as usize;
    if count==0||count>256{return Err("original source StaticMaterials slot count invalid".into());}
    // UE4 packed source FScriptArray: u32 number followed by one
    // StructProperty tag whose payload holds 'count' consecutive
    // FStaticMaterial tagged records, each with its own None terminator.
    let wrapper=with_none_terminator(catalog,&b[4..])?;
    let outer=properties::scan(catalog,&wrapper)?;
    if outer.fields.len()!=1||outer.fields[0].name!="StaticMaterials"||
        outer.fields[0].kind!="StructProperty"||
        outer.fields[0].metadata.first().map(String::as_str)!=Some("StaticMaterial"){
        return Err("original StaticMaterials source struct wrapper not authenticated".into());
    }
    let bytes=&wrapper[outer.fields[0].payload.clone()];
    let mut offset=0usize;
    let mut output=Vec::with_capacity(count);
    for index in 0..count {
        if offset>=bytes.len(){return Err("original material slots terminate before source count".into());}
        let fields=properties::scan(catalog,&bytes[offset..])?;
        let read=fields.bytes_consumed;
        if read==0||read>bytes.len()-offset {
            return Err("original material record malformed source size".into());
        }
        let record=&bytes[offset..offset+read];
        let ref_raw=exact_field(&fields,record,"MaterialInterface","ObjectProperty",4)?;
        let material_id=i32::from_le_bytes(ref_raw.try_into().unwrap());
        let material_interface=if material_id==0{None}
            else{
                let identity=catalog.source_object_path(material_id)?;
                if !identity.starts_with("/Game/") &&
                   !identity.starts_with("/Engine/") {
                    return Err(format!("source material object outside known UE roots: {identity}"));
                }
                Some(identity)
            };
        let slot=fname(catalog,exact_field(
            &fields,record,"MaterialSlotName","NameProperty",8
        )?)?;
        let imported=fname(catalog,exact_field(
            &fields,record,"ImportedMaterialSlotName","NameProperty",8
        )?)?;
        output.push(OriginalStaticMaterial{
            slot:u32::try_from(index).map_err(|_|"source material slot overflow")?,
            material_interface,material_slot_name:slot,imported_slot_name:imported,
        });
        offset+=read;
    }
    if offset!=bytes.len(){
        return Err(format!("original StaticMaterials records leave {} unexplained bytes",bytes.len()-offset));
    }
    Ok(output)
}
#[cfg(test)]
mod tests{
    use super::*;
    use crate::uobject::{PackageCatalog,PackageSummary};
    fn fixture()->PackageCatalog{
        PackageCatalog{
            summary:PackageSummary{
                total_header_size:0,folder_name:String::new(),flags:0,unversioned:true,
                name_count:2,name_offset:0,export_count:0,export_offset:0,
                import_count:0,import_offset:0,depends_offset:0,
            },names:vec!["None".into(),"M_Cave".into()],
            imports:Vec::new(),exports:Vec::new(),
        }
    }
    #[test]fn original_slot_fnames_preserve_ue4_numbered_object_identity(){
        let cat=fixture();
        assert_eq!(fname(&cat,&[1,0,0,0,0,0,0,0]).unwrap(),"M_Cave");
        assert_eq!(fname(&cat,&[1,0,0,0,3,0,0,0]).unwrap(),"M_Cave#3");
        assert!(fname(&cat,&[99,0,0,0,0,0,0,0]).is_err());
    }
    #[test]fn reject_fake_or_incomplete_original_material_slot_metadata(){
        let cat=fixture();
        let bytes=with_none_terminator(&cat,&[1,2,3,4]).unwrap();
        assert_eq!(bytes.len(),12);
        assert!(properties::scan(&cat,&bytes).is_err());
    }
}
