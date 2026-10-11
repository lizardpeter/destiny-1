//! Actual UE4.21 cooked Athena HLOD material-slot and flattened diffuse
//! texture binding. Decode nested, named FStaticMaterial/FTextureParameterValue
//! property records, never choose textures from a matching file name.
//! The original material shader permutation is still outstanding; the exact
//! baked diffuse texture can be used with source-neutral PBR meanwhile.
use crate::{properties, uobject::PackageCatalog};

const MAX_SLOTS:usize=64;
const MAX_TEXTURE_PARAMETERS:usize=64;
#[derive(Debug,Clone)]
pub struct HlodMaterialSlot{
    pub material_reference:i32,
    pub source_material_identity:Option<String>,
    pub diffuse_export_index:Option<usize>,
    pub authored_diffuse_identity:Option<String>,
}
fn u32_at(data:&[u8],pos:usize)->Result<u32,String>{
    Ok(u32::from_le_bytes(data.get(pos..pos+4)
        .ok_or("original HLOD material source field truncated")?
        .try_into().unwrap()))
}
fn i32_at(data:&[u8],pos:usize)->Result<i32,String>{
    Ok(u32_at(data,pos)? as i32)
}
fn source_name<'a>(catalog:&'a PackageCatalog,data:&[u8],pos:usize)
    ->Result<&'a str,String>{
    let idx=u32_at(data,pos)? as usize;
    let instance=u32_at(data,pos+4)?;
    if instance!=0 {return Err("unexpected numbered HLOD serialized property field".into());}
    catalog.names.get(idx).map(String::as_str)
        .ok_or("original HLOD property refers to missing source FName".into())
}
fn unique_field<'a>(
    fields:&'a properties::Properties,key:&str,kind:&str
)->Result<Option<&'a properties::Property>,String>{
    let mut matches=fields.fields.iter().filter(|f|f.name==key);
    let Some(item)=matches.next() else{return Ok(None)};
    if matches.next().is_some() ||item.kind!=kind {
        return Err(format!("original HLOD {key} property duplicated or wrong type"));
    }
    Ok(Some(item))
}
fn field_value<'a>(
    source:&'a [u8],fields:&properties::Properties,key:&str,kind:&str
)->Result<Option<&'a[u8]>,String>{
    let Some(field)=unique_field(fields,key,kind)? else{return Ok(None)};
    source.get(field.payload.clone()).map(Some)
        .ok_or_else(||format!("HLOD source {key} property extent invalid"))
}
/// Original 4.21 TArray<UStruct> cooked value:
/// u32 number of elements, one explicit FStructPropertyTag (49 bytes),
/// then tagged-property stream for each array element (with its own None).
fn original_struct_array<'a>(
    catalog:&PackageCatalog,source:&'a[u8],
    expected_property:&str,expected_struct:&str,max_count:usize
)->Result<Vec<&'a[u8]>,String>{
    if source.len()<53{
        return Err(format!("source {expected_property} lacks tagged struct array header"));
    }
    let count=u32_at(source,0)? as usize;
    if count>max_count {
        return Err(format!("source {expected_property} array count exceeds bound"));
    }
    if source_name(catalog,source,4)?!=expected_property ||
        source_name(catalog,source,12)?!="StructProperty" ||
        source_name(catalog,source,28)?!=expected_struct ||
        u32_at(source,24)?!=0 ||
        source[52]!=0 {
        return Err(format!("unexpected original HLOD {expected_property} inner UStruct tag"));
    }
    let payload_size=u32_at(source,20)? as usize;
    if 53usize.checked_add(payload_size)!=Some(source.len()){
        return Err(format!("source {expected_property} UStruct array length mismatch"));
    }
    let mut records=Vec::with_capacity(count);
    let mut pos=53;
    for _ in 0..count{
        let remaining=source.get(pos..)
            .ok_or("source UStruct record pointer out of bounds")?;
        let props=properties::scan(catalog,remaining)?;
        let end=pos.checked_add(props.bytes_consumed)
            .ok_or("HLOD tagged UStruct offset overflow")?;
        records.push(source.get(pos..end)
            .ok_or("HLOD tagged source UStruct record truncated")?);
        pos=end;
    }
    if pos!=source.len(){
        return Err(format!("original {expected_property} UStructs leave trailing unparsed bytes"));
    }
    Ok(records)
}
fn source_ref(catalog:&PackageCatalog,bytes:&[u8])->Result<(i32,Option<String>),String>{
    if bytes.len()!=4{return Err("original HLOD reference must be 4 bytes".into());}
    let r=i32_at(bytes,0)?;
    Ok((r,if r==0{None}else{Some(catalog.source_object_path(r)?)}))
}
fn diffuse_texture_from_material(
    catalog:&PackageCatalog,header:&[u8],companion:&[u8],material_ref:i32
)->Result<Option<(usize,String)>,String>{
    if material_ref<=0{return Ok(None);}
    let mat=catalog.exports.get((material_ref-1) as usize)
        .ok_or("material reference outside cooked package export table")?;
    if catalog.export_class_name(mat)!=Some("MaterialInstanceConstant"){
        return Ok(None);
    }
    let serial=catalog.export_data(header,companion,mat)?;
    let props=properties::scan(catalog,serial)?;
    let Some(array)=field_value(serial,&props,"TextureParameterValues","ArrayProperty")?
        else{return Ok(None)};
    let records=original_struct_array(catalog,array,
        "TextureParameterValues","TextureParameterValue",MAX_TEXTURE_PARAMETERS)?;
    let mut chosen:Option<(usize,String)>=None;
    for record in records{
        let fields=properties::scan(catalog,record)?;
        let Some(param)=field_value(record,&fields,"ParameterInfo","StructProperty")?
            else{continue};
        let info=properties::scan(catalog,param)?;
        let Some(raw_name)=field_value(param,&info,"Name","NameProperty")?
            else{continue};
        if source_name(catalog,raw_name,0)?!="DiffuseTexture"{continue;}
        let Some(texture)=field_value(record,&fields,"ParameterValue","ObjectProperty")?
            else{continue};
        let (reference,identity)=source_ref(catalog,texture)?;
        if reference<=0 {return Err("original HLOD DiffuseTexture reference was not local source export".into());}
        let index=(reference-1) as usize;
        let tex=catalog.exports.get(index).ok_or("source HLOD diffuse texture reference invalid")?;
        if catalog.export_class_name(tex)!=Some("Texture2D"){
            return Err("original HLOD DiffuseTexture points to non Texture2D export".into());
        }
        if chosen.replace((index,identity.ok_or("original diffuse texture has no source identity")?)).is_some(){
            return Err("ambiguous duplicate original HLOD DiffuseTexture parameters".into());
        }
    }
    Ok(chosen)
}
pub fn authored_static_mesh_diffuse_slots(
    catalog:&PackageCatalog,header:&[u8],companion:&[u8],mesh_source_name:&str
)->Result<Vec<HlodMaterialSlot>,String>{
    let mut source_mesh=None;
    for (i,ex) in catalog.exports.iter().enumerate(){
        if catalog.export_class_name(ex)!=Some("StaticMesh"){continue;}
        let path=catalog.source_object_path((i+1) as i32)?;
        if path.split("::").last()==Some(mesh_source_name){
            if source_mesh.replace(ex).is_some(){
                return Err("source UStaticMesh material lookup is ambiguous".into());
            }
        }
    }
    let mesh=source_mesh.ok_or("original HLOD UStaticMesh not found for materials")?;
    let source=catalog.export_data(header,companion,mesh)?;
    let props=properties::scan(catalog,source)?;
    let array=field_value(source,&props,"StaticMaterials","ArrayProperty")?
        .ok_or("original UStaticMesh StaticMaterials source property absent")?;
    let records=original_struct_array(catalog,array,"StaticMaterials","StaticMaterial",MAX_SLOTS)?;
    let mut result=Vec::with_capacity(records.len());
    for record in records{
        let fields=properties::scan(catalog,record)?;
        let reference=field_value(record,&fields,"MaterialInterface","ObjectProperty")?
            .ok_or("source StaticMaterial lacks MaterialInterface")?;
        let (material_reference,source_material_identity)=source_ref(catalog,reference)?;
        let diffuse=diffuse_texture_from_material(
            catalog,header,companion,material_reference,
        )?;
        result.push(HlodMaterialSlot{
            material_reference,
            source_material_identity,
            diffuse_export_index:diffuse.as_ref().map(|v|v.0),
            authored_diffuse_identity:diffuse.map(|v|v.1),
        });
    }
    Ok(result)
}
#[cfg(test)]
mod tests{
    use super::*;
    #[test]fn source_struct_array_rejects_truncated_metadata(){
        let catalog=PackageCatalog{
            summary:crate::uobject::PackageSummary{
                total_header_size:0,folder_name:String::new(),flags:0,unversioned:true,
                name_count:0,name_offset:0,export_count:0,export_offset:0,
                import_count:0,import_offset:0,depends_offset:0,
            },names:Vec::new(),imports:Vec::new(),exports:Vec::new()
        };
        assert!(original_struct_array(&catalog,b"\\x00","StaticMaterials","StaticMaterial",64).is_err());
    }
}
