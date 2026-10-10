//! Original UE4.21 LandscapeComponent placement and heightmap reference
//! extraction. This does NOT generate a fake mesh. Until source Texture2D
//! bulk height samples are decoded, geometry remains explicitly unavailable.
use crate::{properties::{self, Properties, Property}, uobject::PackageCatalog};

#[derive(Clone, Debug)]
pub struct LandscapeComponent {
    /// Original UE4 component grid origin (landscape quads, not metres).
    pub section_base: [i32; 2],
    /// True when original cooked UObject explicitly serialized the value;
    /// false means UE4 ULandscapeComponent CDO's zero default was applied.
    pub section_base_serialized: [bool; 2],
    pub component_size_quads: u32,
    pub subsection_size_quads: u32,
    pub num_subsections: u32,
    pub heightmap_scale_bias: [f32; 4],
    /// Exact FPackageIndex referring to an original source texture export/import.
    pub heightmap_texture_ref: i32,
    pub heightmap_texture_name: Option<String>,
    pub weightmap_texture_refs: Vec<i32>,
    pub material_instance_refs: Vec<i32>,
}

fn named<'a>(props: &'a Properties, name: &str, kind: &str, bytes: &[u8]) -> Result<&'a Property, String> {
    let matches = props.fields.iter().filter(|p| p.name == name).collect::<Vec<_>>();
    if matches.len() != 1 {
        return Err(format!("expected one source LandscapeComponent {name} property; got {}", matches.len()));
    }
    let prop = matches[0];
    if prop.kind != kind || prop.payload.end > bytes.len() {
        return Err(format!("source landscape property {name} wrong kind/range"));
    }
    Ok(prop)
}

fn integer(props: &Properties, bytes: &[u8], name: &str, kind: &str) -> Result<i32, String> {
    let p = named(props, name, kind, bytes)?;
    let raw = bytes.get(p.payload.clone()).ok_or("source landscape integer missing")?;
    if raw.len() != 4 { return Err(format!("source {name} is not a 32-bit value")); }
    Ok(i32::from_le_bytes(raw.try_into().unwrap()))
}
/// ULandscapeComponent class defaults SectionBaseX/Y to zero in UE4.
/// Cooked UObject property tagging omits fields equal to their class defaults.
/// Track that provenance rather than misreporting zero as an explicit value.
fn section_base(props: &Properties, bytes: &[u8], name: &str) -> Result<(i32, bool), String> {
    let matches=props.fields.iter().filter(|p| p.name==name).count();
    if matches==0 { return Ok((0,false)); }
    if matches!=1 { return Err(format!("duplicate source {name} tags")); }
    Ok((integer(props,bytes,name,"IntProperty")?,true))
}

fn vec4(props: &Properties, bytes: &[u8], name: &str) -> Result<[f32;4], String> {
    let p = named(props, name, "StructProperty", bytes)?;
    if p.metadata.first().map(String::as_str) != Some("Vector4") {
        return Err(format!("source {name} is not a FVector4"));
    }
    let raw = bytes.get(p.payload.clone()).ok_or("source landscape FVector4 missing")?;
    if raw.len() != 16 { return Err(format!("source {name} is not four f32 values")); }
    let mut out=[0f32;4];
    for i in 0..4 {
        out[i]=f32::from_le_bytes(raw[i*4..i*4+4].try_into().unwrap());
        if !out[i].is_finite() { return Err(format!("source {name} contains non-finite component")); }
    }
    Ok(out)
}
fn object_refs(props: &Properties, bytes: &[u8], name: &str) -> Result<Vec<i32>, String> {
    let p = named(props, name, "ArrayProperty", bytes)?;
    if p.metadata.first().map(String::as_str) != Some("ObjectProperty") {
        return Err(format!("source {name} is not an object reference array"));
    }
    let raw = bytes.get(p.payload.clone()).ok_or("source landscape refs missing")?;
    if raw.len() < 4 {return Err(format!("source {name} array has no count"));}
    let count=u32::from_le_bytes(raw[0..4].try_into().unwrap()) as usize;
    if count>100000 {return Err(format!("source {name} array count too large"));}
    if count.checked_mul(4).and_then(|n| n.checked_add(4)) != Some(raw.len()) {
        return Err(format!("source {name} array payload length disagrees with count"));
    }
    Ok(raw[4..].chunks_exact(4).map(|data| i32::from_le_bytes(data.try_into().unwrap())).collect())
}

/// Produce a source-backed landscape component descriptor, never interpolated
/// or guessed source transforms, heights or materials.
pub fn inspect(catalog: &PackageCatalog, data: &[u8]) -> Result<LandscapeComponent, String> {
    let p=properties::scan(catalog,data)?;
    let heightmap_texture_ref=integer(&p,data,"HeightmapTexture","ObjectProperty")?;
    let component_size_quads=integer(&p,data,"ComponentSizeQuads","IntProperty")?;
    let subsection_size_quads=integer(&p,data,"SubsectionSizeQuads","IntProperty")?;
    let num_subsections=integer(&p,data,"NumSubsections","IntProperty")?;
    if component_size_quads<=0 || subsection_size_quads<=0 || num_subsections<=0 ||
        subsection_size_quads.checked_mul(num_subsections)!=Some(component_size_quads) {
        return Err("source landscape subsection size does not close to component quad size".into());
    }
    let heightmap_scale_bias=vec4(&p,data,"HeightmapScaleBias")?;
    let weightmap_texture_refs=object_refs(&p,data,"WeightmapTextures")?;
    let material_instance_refs=object_refs(&p,data,"MaterialInstances")?;
    let (section_x, serialized_x)=section_base(&p,data,"SectionBaseX")?;
    let (section_y, serialized_y)=section_base(&p,data,"SectionBaseY")?;
    Ok(LandscapeComponent {
        section_base: [section_x,section_y],
        section_base_serialized: [serialized_x,serialized_y],
        component_size_quads: component_size_quads as u32,
        subsection_size_quads: subsection_size_quads as u32,
        num_subsections: num_subsections as u32,
        heightmap_scale_bias,
        heightmap_texture_ref,
        heightmap_texture_name: catalog.resolve_package_name(heightmap_texture_ref).map(str::to_owned),
        weightmap_texture_refs,
        material_instance_refs,
    })
}
