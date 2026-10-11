//! Native UE4.21 cooked UStaticMesh LOD0 geometry decoding.
//!
//! Original source proof: Fortnite 5.41 Athena HLOD:
//! 1 section, 124 triangles, 184 FVectors, 2 UV channels, 8-byte
//! tangent records, 4-byte half-float UV records, and 372 u16 indices.
//! Decode by the ORIGINAL serial stream fields, NEVER by byte-pattern scans.
//! Unknown source variants are rejected rather than fabricated.
use crate::{properties,uobject::{PackageCatalog,PackageExport}};
#[derive(Debug,Clone)]
pub struct OriginalStaticMeshSection {
    pub material_slot:u32,
    pub first_index:u32,
    pub triangle_count:u32,
    pub min_vertex:u32,
    pub max_vertex:u32,
}
#[derive(Debug,Clone)]
pub struct OriginalStaticMeshVertex {
    pub position_cm:[f32;3],
    pub tangent_x:[f32;3],
    pub normal_z:[f32;3],
    pub tangent_handedness:f32,
    pub uv0:[f32;2],
    pub uv1:[f32;2],
}
#[derive(Debug,Clone)]
pub struct OriginalStaticMeshLod {
    pub vertices:Vec<OriginalStaticMeshVertex>,
    pub indices:Vec<u32>,
    pub sections:Vec<OriginalStaticMeshSection>,
    pub total_source_uv_channels:usize,
}
struct Reader<'a>{s:&'a[u8],p:usize}
impl<'a> Reader<'a>{
    fn at(s:&'a[u8],p:usize)->Result<Self,String>{
        if p>s.len(){return Err("UE4 UStaticMesh cursor outside source export".into());}
        Ok(Self{s,p})
    }
    fn bytes(&mut self,n:usize)->Result<&'a[u8],String>{
        let q=self.p.checked_add(n).ok_or("UE4 mesh source offset overflow")?;
        let data=self.s.get(self.p..q).ok_or("UE4 mesh source buffer truncated")?;
        self.p=q;Ok(data)
    }
    fn u8(&mut self)->Result<u8,String>{Ok(self.bytes(1)?[0])}
    fn u32(&mut self)->Result<u32,String>{
        Ok(u32::from_le_bytes(self.bytes(4)?.try_into().unwrap()))
    }
    fn i32(&mut self)->Result<i32,String>{Ok(self.u32()? as i32)}
    fn f32(&mut self)->Result<f32,String>{
        let value=f32::from_bits(self.u32()?);
        if !value.is_finite()||value.abs()>1e8{return Err("non-finite or excessive source mesh float".into());}
        Ok(value)
    }
}
fn half(raw:u16)->f32{
    let sign=((raw as u32&0x8000)<<16);
    let exp=((raw>>10)&31) as i32;
    let mant=(raw&0x03ff) as u32;
    let bits=if exp==0 {
        if mant==0{sign}else{
            let mut m=mant;
            let mut e=113u32;
            while m&0x0400==0 {m<<=1;e-=1;}
            sign|(e<<23)|((m&0x03ff)<<13)
        }
    }else if exp==31{sign|0x7f80_0000|(mant<<13)}
    else{sign|(((exp+112) as u32)<<23)|(mant<<13)};
    f32::from_bits(bits)
}
fn packed_xyz(b:&[u8])->[f32;3]{
    let v=std::array::from_fn(|i|(b[i] as f32*(2./255.)-1.).clamp(-1.,1.));
    let norm=(v.iter().map(|f|f*f).sum::<f32>()).sqrt();
    if norm>0.00001{v.map(|f|f/norm)}else{[0.,0.,1.]}
}
/// Strictly parse known original UE4.21 LOD0 data with source-authored
/// per-section counts, buffer strides, UV layout and triangle bounds.
pub fn decode_cooked_static_mesh_lod0(
    native:&[u8],
)->Result<OriginalStaticMeshLod,String>{
    if native.len()<100||native.len()>64*1024*1024{
        return Err("source StaticMesh native byte span is outside bounds".into());
    }
    let mut rd=Reader::at(native,0)?;
    let global_strip=rd.u8()?;
    let class_strip=rd.u8()?;
    let extra_strip=rd.bytes(4)?;
    // Original UE4 5.41 serialized the prelude's bCooked at byte 6,
    // two refs (BodySetup/NavCollision), a GUID and a zero-socket list.
    if global_strip&2!=0 ||class_strip!=0 ||
        extra_strip!=[0,0,1,0] ||
        rd.u32()?!=1{
        return Err("UE4.21 UStaticMesh prelude/source Cooked variant unsupported".into());
    }
    let _body=rd.i32()?;
    let _nav=rd.i32()?;
    rd.bytes(16)?; // source LightingGuid
    let sockets=rd.u32()? as usize;
    if sockets>64{return Err("unbounded UE4 mesh socket references".into());}
    for _ in 0..sockets{rd.i32()?;}
    let lod_count=rd.u32()? as usize;
    if lod_count==0||lod_count>8{return Err("invalid original StaticMesh LOD count".into());}
    let flags_global=rd.u8()?;
    let flags_class=rd.u8()?;
    if flags_global&2!=0||flags_class&2!=0{
        return Err("source StaticMesh first LOD is stripped".into());
    }
    let section_count=rd.u32()? as usize;
    if section_count==0||section_count>64{return Err("unbounded source UStaticMesh LOD sections".into());}
    let mut sections=Vec::with_capacity(section_count);
    for _ in 0..section_count{
        let mat=rd.u32()?;
        let start=rd.u32()?;
        let tris=rd.u32()?;
        let min=rd.u32()?;
        let max=rd.u32()?;
        let _collision=rd.u32()?;
        let _shadow=rd.u32()?;
        if tris==0 ||tris>2_000_000 ||max<min{
            return Err("source UStaticMesh LOD section has invalid source triangle bounds".into());
        }
        sections.push(OriginalStaticMeshSection{
            material_slot:mat,first_index:start,
            triangle_count:tris,min_vertex:min,max_vertex:max,
        });
    }
    rd.f32()?; // MaxDeviation
    let position_stride=rd.u32()? as usize;
    let vertex_count=rd.u32()? as usize;
    let position_bulk_item=rd.u32()? as usize;
    let position_bulk_count=rd.u32()? as usize;
    if position_stride!=12 ||position_bulk_item!=12 ||
        vertex_count==0 ||vertex_count>1_000_000 ||
        position_bulk_count!=vertex_count{
        return Err("original UE4 FPositionVertexBuffer source metadata mismatch".into());
    }
    let mut positions=Vec::with_capacity(vertex_count);
    for _ in 0..vertex_count{
        positions.push([rd.f32()?,rd.f32()?,rd.f32()?]);
    }
    let uv_strip_global=rd.u8()?;
    rd.u8()?; // UV buffer class strip flags
    if uv_strip_global&2!=0{return Err("source UStaticMesh tangent/UV data stripped".into());}
    let num_uv=rd.u32()? as usize;
    let tangent_vertices=rd.u32()? as usize;
    let full_precision=rd.u32()?;
    let high_precision_tangents=rd.u32()?;
    if !(1..=8).contains(&num_uv)||tangent_vertices!=vertex_count||
        full_precision>1||high_precision_tangents>1{
        return Err("source UE4 StaticMesh tangent/UV metadata disagrees with positions".into());
    }
    let tangent_stride=rd.u32()? as usize;
    let tangent_count=rd.u32()? as usize;
    let expected_tangent_stride=if high_precision_tangents!=0{16}else{8};
    if tangent_stride!=expected_tangent_stride ||tangent_count!=vertex_count{
        return Err("source UE4 tangent buffer bulk stride/count mismatch".into());
    }
    let mut tangents=Vec::with_capacity(vertex_count);
    for _ in 0..vertex_count{
        let bytes=rd.bytes(tangent_stride)?;
        if tangent_stride==8{
            tangents.push((packed_xyz(&bytes[..4]),packed_xyz(&bytes[4..8]),
                if bytes[7]<128{-1.}else{1.}));
        }else{
            // A future source case requiring 16-bit packed tangents must
            // preserve its original semantics before geometry admission.
            return Err("high precision original tangent basis not translated yet".into());
        }
    }
    let texcoord_stride=rd.u32()? as usize;
    let uv_count=rd.u32()? as usize;
    let expected_uv_stride=if full_precision!=0{8}else{4};
    if texcoord_stride!=expected_uv_stride ||
        uv_count!=vertex_count.checked_mul(num_uv).ok_or("UV count overflow")?{
        return Err("original source UV bulk count or packed format mismatch".into());
    }
    let mut uvs=Vec::with_capacity(vertex_count);
    for _ in 0..vertex_count{
        let mut vertex_uv=[[0.;2];2];
        for channel in 0..num_uv{
            let uv=if full_precision!=0 {
                [rd.f32()?,rd.f32()?]
            }else{
                let source=rd.bytes(4)?;
                [half(u16::from_le_bytes(source[0..2].try_into().unwrap())),
                 half(u16::from_le_bytes(source[2..4].try_into().unwrap()))]
            };
            if uv.iter().any(|f|!f.is_finite()||f.abs()>1e6){
                return Err("original UE4 mesh UV source value non-finite/out of bounds".into());
            }
            if channel<2{vertex_uv[channel]=uv;}
        }
        uvs.push(vertex_uv);
    }
    let color_strip=rd.u8()?;
    rd.u8()?;
    if color_strip&2!=0{return Err("original source mesh color buffer stripped".into());}
    let color_stride=rd.u32()? as usize;
    let color_count=rd.u32()? as usize;
    if color_count>0{
        if color_count!=vertex_count||color_stride!=4{
            return Err("source UE4 vertex colors stride/count inconsistent".into());
        }
        let item=rd.u32()? as usize;
        let count=rd.u32()? as usize;
        if item!=4||count!=color_count{return Err("source vertex color bulk data inconsistent".into());}
        rd.bytes(color_count*4)?;
    }else if color_stride!=0{
        return Err("empty source vertex color buffer had nonzero stride".into());
    }
    let index_is_32=rd.u32()?;
    let index_bulk_stride=rd.u32()? as usize;
    let index_byte_count=rd.u32()? as usize;
    if index_is_32>1 ||index_bulk_stride!=1 ||
        index_byte_count==0 ||index_byte_count>48*1024*1024 ||
        index_byte_count%(if index_is_32!=0{4}else{2})!=0{
        return Err("original StaticMesh index bulk header inconsistent".into());
    }
    let index_data=rd.bytes(index_byte_count)?;
    let index_size=if index_is_32!=0{4}else{2};
    let mut indices=Vec::with_capacity(index_byte_count/index_size);
    for record in index_data.chunks_exact(index_size){
        let index=if index_size==4{
            u32::from_le_bytes(record.try_into().unwrap())
        }else{
            u16::from_le_bytes(record.try_into().unwrap()) as u32
        };
        if index as usize>=vertex_count{
            return Err("source StaticMesh triangle index exceeds original vertex stream".into());
        }
        indices.push(index);
    }
    for section in &sections{
        let end=(section.first_index as usize)
            .checked_add(section.triangle_count as usize*3)
            .ok_or("source triangle section index span overflow")?;
        if end>indices.len() ||section.max_vertex as usize>=vertex_count{
            return Err("UE4 original source StaticMesh LOD index/section bounds invalid".into());
        }
    }
    let mut vertices=Vec::with_capacity(vertex_count);
    for i in 0..vertex_count{
        let (tx,nz,hand)=tangents[i];
        vertices.push(OriginalStaticMeshVertex{
            position_cm:positions[i],tangent_x:tx,normal_z:nz,
            tangent_handedness:hand,uv0:uvs[i][0],uv1:uvs[i][1],
        });
    }
    Ok(OriginalStaticMeshLod{
        vertices,indices,sections,total_source_uv_channels:num_uv,
    })
}
/// Decode by a specific original UObject identity, never the first/nearest
/// mesh found in a package containing several original StaticMesh exports.
pub fn decode_original_source_mesh(
    catalog:&PackageCatalog,header:&[u8],companion:&[u8],source_object:&str
)->Result<OriginalStaticMeshLod,String>{
    let mut chosen:Option<&PackageExport>=None;
    for (index,export) in catalog.exports.iter().enumerate(){
        if catalog.export_class_name(export)!=Some("StaticMesh"){continue;}
        let original_path=catalog.source_object_path((index+1) as i32)?;
        if original_path.split("::").last()!=Some(source_object){continue;}
        if chosen.replace(export).is_some(){
            return Err("ambiguous original HLOD StaticMesh export identity".into());
        }
    }
    let export=chosen.ok_or("original source package lacks referenced UStaticMesh export")?;
    let source=catalog.export_data(header,companion,export)?;
    let props=properties::scan(catalog,source)?;
    decode_cooked_static_mesh_lod0(
        source.get(props.bytes_consumed..).ok_or("original StaticMesh cooked bytes absent")?
    )
}
#[cfg(test)]
mod tests{
    use super::*;
    #[test]fn half_precision_uv_values(){
        assert_eq!(half(0x3c00),1.);
        assert_eq!(half(0xbc00),-1.);
        assert_eq!(half(0),0.);
        assert!(half(0x7c00).is_infinite());
    }
}
