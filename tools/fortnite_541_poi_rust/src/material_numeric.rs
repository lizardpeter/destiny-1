//! Source-typed UE4.21 cooked MaterialInstanceConstant scalar/vector overrides.
//! Exact original FMaterialParameterInfo.Name and per-record tagged values.
//! These are shader inputs, NOT a synthesized executable source shader graph.
use crate::{properties,uobject::{self,PackageCatalog}};
#[derive(Clone,Debug,PartialEq)]
pub struct OriginalScalarParameter{pub name:String,pub value:f32}
#[derive(Clone,Debug,PartialEq)]
pub struct OriginalVectorParameter{pub name:String,pub linear_rgba:[f32;4]}
#[derive(Clone,Debug,PartialEq)]
pub struct OriginalNumericMaterialParameters{
    pub original:String,
    pub scalars:Vec<OriginalScalarParameter>,
    pub vectors:Vec<OriginalVectorParameter>,
}
fn named(c:&PackageCatalog,bytes:&[u8])->Result<String,String>{
    if bytes.len()!=8{return Err("source FMaterialParameterInfo FName width invalid".into());}
    let index=u32::from_le_bytes(bytes[0..4].try_into().unwrap()) as usize;
    let number=u32::from_le_bytes(bytes[4..8].try_into().unwrap());
    let name=c.names.get(index).ok_or("source material parameter FName unknown")?;
    Ok(if number==0{name.clone()}else{format!("{name}#{number}")})
}
fn field<'a>(props:&properties::Properties,bytes:&'a[u8],name:&str,kind:&str)
    ->Result<&'a[u8],String>{
    let mut matches=props.fields.iter().filter(|p|p.name==name);
    let tag=matches.next().ok_or_else(||format!("source MaterialParameter {name} absent"))?;
    if matches.next().is_some()||tag.kind!=kind{
        return Err(format!("original MaterialParameter {name} ambiguous/wrong type"));
    }
    bytes.get(tag.payload.clone()).ok_or_else(||"material parameter payload out of bounds".into())
}
fn terminator(c:&PackageCatalog,b:&[u8])->Result<Vec<u8>,String>{
    let none=c.names.iter().position(|name|name=="None")
        .ok_or("source MaterialInstance has no None terminator")?;
    let id=u32::try_from(none).map_err(|_|"source MaterialInstance FName count overflow")?;
    let mut value=b.to_vec();
    value.extend_from_slice(&id.to_le_bytes());
    value.extend_from_slice(&0u32.to_le_bytes());
    Ok(value)
}
fn numeric_fields(
    c:&PackageCatalog,root:&properties::Properties,raw:&[u8],
    tag:&str,
)->Result<Vec<(String,Vec<u8>,String)>,String>{
    let mut tags=root.fields.iter().filter(|p|p.name==tag);
    let Some(array)=tags.next() else{return Ok(Vec::new())};
    if tags.next().is_some()||array.kind!="ArrayProperty"||
       array.metadata.first().map(String::as_str)!=Some("StructProperty"){
        return Err(format!("original source {tag} must be one StructProperty array"));
    }
    let encoded=&raw[array.payload.clone()];
    if encoded.len()<4{return Err(format!("original source {tag} missing count"));}
    let count=u32::from_le_bytes(encoded[..4].try_into().unwrap()) as usize;
    if count>256{return Err(format!("original source {tag} excessively many entries"));}
    let wrapped=terminator(c,&encoded[4..])?;
    let outer=properties::scan(c,&wrapped)?;
    if outer.fields.len()!=1||outer.fields[0].name!=tag||
       outer.fields[0].kind!="StructProperty"{
        return Err(format!("original source {tag} nested struct wrapper mismatch"));
    }
    let body=&wrapped[outer.fields[0].payload.clone()];
    let mut out=Vec::with_capacity(count);
    let mut cursor=0usize;
    for _ in 0..count{
        if cursor>=body.len(){return Err(format!("original source {tag} ends before counted records"));}
        let fields=properties::scan(c,&body[cursor..])?;
        if fields.bytes_consumed==0||
            cursor+fields.bytes_consumed>body.len(){
            return Err(format!("original source {tag} record size malformed"));
        }
        let b=&body[cursor..cursor+fields.bytes_consumed];
        let info=field(&fields,b,"ParameterInfo","StructProperty")?;
        let info_props=properties::scan(c,info)?;
        let name=named(c,field(&info_props,info,"Name","NameProperty")?)?;
        let value_tag=fields.fields.iter().find(|p|p.name=="ParameterValue")
            .ok_or("source numeric ParameterValue absent")?;
        let value=field(&fields,b,"ParameterValue",&value_tag.kind)?;
        // These are offsets into synthetic wrapper bytes, so only use the
        // actual owned body inside this call. Return owned value next.
        out.push((name,value.to_vec(),value_tag.kind.clone()));
        cursor+=fields.bytes_consumed;
    }
    if cursor!=body.len(){return Err(format!("source {tag} has unexplained trailing bytes"));}
    Ok(out)
}
pub fn inspect_original_numeric_parameters(
    h:&[u8],x:&[u8],original:&str,
)->Result<OriginalNumericMaterialParameters,String>{
    let c=uobject::inspect(h)?;
    let object=original.rsplit("::").next()
        .ok_or("source MIC material UObject object name missing")?;
    let mut found=c.exports.iter().enumerate().filter(|(i,e)|
        c.export_class_name(e)==Some("MaterialInstanceConstant") &&
        c.resolve_package_name((i+1) as i32)==Some(object));
    let (_,mat)=found.next().ok_or("source material numeric MIC export not found")?;
    if found.next().is_some(){return Err("duplicate source material numeric MIC".into());}
    let bytes=c.export_data(h,x,mat)?;
    let p=properties::scan(&c,bytes)?;
    let mut scalars=Vec::new();
    for (name,encoded,kind) in numeric_fields(&c,&p,bytes,"ScalarParameterValues")?{
        if kind!="FloatProperty"||encoded.len()!=4{
            return Err(format!("source ScalarParameterValue {name} not float32"));
        }
        let value=f32::from_le_bytes(encoded.try_into().unwrap());
        if !value.is_finite(){return Err("source scalar shader parameter nonfinite".into());}
        scalars.push(OriginalScalarParameter{name,value});
    }
    let mut vectors=Vec::new();
    for (name,encoded,kind) in numeric_fields(&c,&p,bytes,"VectorParameterValues")?{
        if kind!="StructProperty"||encoded.len()!=16{
            return Err(format!("source VectorParameterValue {name} not LinearColor"));
        }
        let linear_rgba=std::array::from_fn(|i|
            f32::from_le_bytes(encoded[4*i..4*i+4].try_into().unwrap()));
        if linear_rgba.iter().any(|x|!x.is_finite()){
            return Err("source vector shader parameter nonfinite".into());
        }
        vectors.push(OriginalVectorParameter{name,linear_rgba});
    }
    Ok(OriginalNumericMaterialParameters{
        original:original.to_owned(),scalars,vectors
    })
}
#[cfg(test)]
mod tests{
    use super::*;
    use crate::uobject::{PackageCatalog,PackageSummary};
    #[test]fn original_numbered_numeric_shader_fnames_are_exact(){
        let c=PackageCatalog{
            summary:PackageSummary{total_header_size:0,folder_name:String::new(),
                flags:0,unversioned:true,name_count:2,name_offset:0,
                export_count:0,export_offset:0,import_count:0,
                import_offset:0,depends_offset:0},
            names:vec!["None".into(),"FlameSpeed".into()],
            imports:Vec::new(),exports:Vec::new(),
        };
        assert_eq!(named(&c,&[1,0,0,0,3,0,0,0]).unwrap(),"FlameSpeed#3");
        assert!(named(&c,&[4,0,0,0,0,0,0,0]).is_err());
    }
}
