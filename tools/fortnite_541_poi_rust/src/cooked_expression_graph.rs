//! Source-authored UE4 cooked material expression links.
//!
//! Retail-cooked UE4.21 FExpressionInput stores an optional UObject pointer
//! in bytes 0..4 and a surviving original FName expression identity at
//! bytes 32..40. Editor-only expression nodes may be stripped completely,
//! so it is incorrect to interpret a null pointer as an unconnected input.
//! Retain dangling original links and their exact source names, preserving
//! a truthful compiler frontier rather than inventing missing shader math.
use crate::{properties, uobject::PackageCatalog};
use std::collections::BTreeMap;

#[derive(Debug,Clone)]
pub struct OriginalCookedExpressionLink {
    pub consumer:String,
    pub consumer_export_index:i32,
    pub source_port:String,
    pub source_array_index:i32,
    pub source_pointer:i32,
    pub target_expression_name:String,
    /// Some authored nodes survive in the cooked export table; many editor
    /// shader nodes do not. Missing identities are not null connections.
    pub target_export_index:Option<i32>,
}
#[derive(Debug,Clone,Default)]
pub struct OriginalCookedMaterialTopology {
    pub original_expression_exports:usize,
    pub original_material_roots:usize,
    pub links:Vec<OriginalCookedExpressionLink>,
    pub absent_expression_targets:Vec<String>,
}
impl OriginalCookedMaterialTopology {
    pub fn connected_links(&self)->usize{
        self.links.iter().filter(|l|l.target_export_index.is_some()).count()
    }
    pub fn stripped_links(&self)->usize{
        self.links.iter().filter(|l|l.target_export_index.is_none()).count()
    }
}
fn source_expression_name(cat:&PackageCatalog,raw:&[u8])->Result<Option<String>,String>{
    if raw.len()<40 {return Err("cooked FExpressionInput shorter than source FName field".into());}
    let id=u32::from_le_bytes(raw[32..36].try_into().unwrap()) as usize;
    let instance=u32::from_le_bytes(raw[36..40].try_into().unwrap());
    let name=cat.names.get(id)
        .ok_or("cooked FExpressionInput references absent source FName")?;
    if name=="None" && instance==0{return Ok(None);}
    if name.is_empty(){return Err("cooked expression FName has empty text".into());}
    Ok(Some(if instance==0{name.clone()}else{format!("{name}#{instance}")}))
}
fn expression_export_name(cat:&PackageCatalog,ordinal:usize)->Result<String,String>{
    let export=cat.exports.get(ordinal).ok_or("source expression export index invalid")?;
    let name=cat.names.get(export.object_name.name_index as usize)
        .ok_or("original expression export missing source FName")?;
    let number=export.object_name.instance_number;
    Ok(if number==0{name.clone()}else{format!("{name}#{number}")})
}
fn supported_input(kind:&str)->bool{
    matches!(kind,
        "ExpressionInput" | "ColorMaterialInput" |
        "ScalarMaterialInput" | "VectorMaterialInput" |
        "MaterialAttributesInput")
}
/// Decode original source expression input FName dependencies for ALL
/// material graph nodes, including the material's authored EmissiveColor root.
/// This is a dependency model, NOT executable shader IR. UE strips many
/// arithmetic nodes from cooked export tables but retains their FNames.
pub fn inspect_cooked_material_topology(
    cat:&PackageCatalog,header:&[u8],exports:&[u8],
)->Result<OriginalCookedMaterialTopology,String>{
    let mut map=BTreeMap::<String,i32>::new();
    let mut graph=OriginalCookedMaterialTopology::default();
    for (i,ex) in cat.exports.iter().enumerate(){
        let Some(class)=cat.export_class_name(ex) else{continue};
        if class=="Material"{graph.original_material_roots+=1;}
        if !class.starts_with("MaterialExpression"){continue;}
        graph.original_expression_exports+=1;
        let name=expression_export_name(cat,i)?;
        let id=i32::try_from(i+1).map_err(|_|"source expression index exceeds i32")?;
        if map.insert(name.clone(),id).is_some(){
            return Err(format!("ambiguous duplicate original cooked material node {name}"));
        }
    }
    let mut missing=std::collections::BTreeSet::new();
    for (i,ex) in cat.exports.iter().enumerate(){
        let Some(class)=cat.export_class_name(ex) else{continue};
        if !(class=="Material"||class.starts_with("MaterialExpression")||
             class=="MaterialFunction"){continue;}
        let raw=cat.export_data(header,exports,ex)?;
        let props=properties::scan(cat,raw)?;
        let consumer=expression_export_name(cat,i)?;
        for p in &props.fields{
            if p.kind!="StructProperty"||
                !p.metadata.first().is_some_and(|m|supported_input(m)){
                continue;
            }
            let bytes=&raw[p.payload.clone()];
            let Some(name)=source_expression_name(cat,bytes)? else{continue};
            let pointer=i32::from_le_bytes(bytes[..4].try_into().unwrap());
            let target=map.get(&name).copied();
            if target.is_none(){missing.insert(name.clone());}
            graph.links.push(OriginalCookedExpressionLink {
                consumer:consumer.clone(),
                consumer_export_index:i32::try_from(i+1)
                    .map_err(|_|"cooked source link index overflow")?,
                source_port:p.name.clone(),
                source_array_index:p.array_index,
                source_pointer:pointer,
                target_expression_name:name,
                target_export_index:target,
            });
        }
    }
    graph.absent_expression_targets=missing.into_iter().collect();
    Ok(graph)
}

#[cfg(test)]
mod tests{
    use super::*;
    use crate::uobject::{PackageSummary,PackageCatalog};
    fn catalog(names:&[&str])->PackageCatalog{
        PackageCatalog{
            summary:PackageSummary{
                total_header_size:0,folder_name:String::new(),flags:0,
                unversioned:true,name_count:names.len() as u32,
                name_offset:0,export_count:0,export_offset:0,
                import_count:0,import_offset:0,depends_offset:0,
            },
            names:names.iter().map(|n|n.to_string()).collect(),
            imports:Vec::new(),exports:Vec::new(),
        }
    }
    #[test]fn named_expression_survives_cooked_null_uobject_pointer(){
        let cat=catalog(&["None","MaterialExpressionMultiply","MaterialExpressionTextureSample"]);
        let mut raw=[0u8;40];
        raw[32..36].copy_from_slice(&1u32.to_le_bytes());
        raw[36..40].copy_from_slice(&8u32.to_le_bytes());
        assert_eq!(source_expression_name(&cat,&raw).unwrap(),
            Some("MaterialExpressionMultiply#8".into()));
        assert_eq!(i32::from_le_bytes(raw[..4].try_into().unwrap()),0);
        raw[32..36].copy_from_slice(&0u32.to_le_bytes());
        raw[36..40].copy_from_slice(&0u32.to_le_bytes());
        assert_eq!(source_expression_name(&cat,&raw).unwrap(),None);
    }
    #[test]fn original_expression_fnames_reject_corruption(){
        let cat=catalog(&["None"]);
        let mut raw=[0u8;40];
        raw[32..36].copy_from_slice(&999u32.to_le_bytes());
        assert!(source_expression_name(&cat,&raw).is_err());
        assert!(source_expression_name(&cat,&raw[..39]).is_err());
    }
}
