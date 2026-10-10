//! Strict source-backed Athena landscape placement census across all six
//! original Fortnite 5.41 landscape sublevel packages.
//! No mesh generation or engine-specific rendering behavior.
use std::{collections::{BTreeMap,BTreeSet}, env, fs, path::PathBuf, process::ExitCode};
use fortnite_541_importer::{landscape, texture, terrain, uobject};

fn run() -> Result<(), String> {
    let root = env::args_os().nth(1).map(PathBuf::from)
        .ok_or("usage: landscape_catalog PATH_TO_ATHENA_SOURCE_ROOT")?;
    let mut total_components=0usize;
    let mut triangles=0usize;
    let mut vertices=0usize;
    let mut seam_audit=terrain::LandscapeSeamAudit::default();
    let mut all_textures=BTreeMap::<String,usize>::new();
    let mut occupied=BTreeSet::<(i32,i32)>::new();
    let mut omitted_grid_components=0usize;
    let mut height_min=u16::MAX;
    let mut height_max=u16::MIN;
    let mut decoded_height_texels=0usize;
    let mut min=[i32::MAX;2];
    let mut max=[i32::MIN;2];
    for section in 0..6 {
        let base=root.join(format!("FortniteGame/Content/Athena/Maps/Landscape/Athena_Terrain_LS_{section:02}"));
        let package_file=fs::read(base.with_extension("umap"))
            .map_err(|e| format!("read source LS_{section:02} UMAP: {e}"))?;
        let companion=fs::read(base.with_extension("uexp"))
            .map_err(|e| format!("read source LS_{section:02} UEXP: {e}"))?;
        let catalog=uobject::inspect(&package_file)?;
        let external_bulk=fs::read(base.with_extension("ubulk"))
            .map_err(|e| format!("read original LS_{section:02} UBULK: {e}"))?;
        let mut section_top_mips=0usize;
        let mut landscape_objects=0usize;
        for export in &catalog.exports {
            if catalog.export_class_name(export) != Some("LandscapeComponent") {continue;}
            let bytes=catalog.export_data(&package_file,&companion,export)?;
            let component=match landscape::inspect(&catalog, bytes) {
                Ok(component) => component,
                Err(error) => {
                    let props=fortnite_541_importer::properties::scan(&catalog,bytes);
                    let names=match props {
                        Ok(p)=>p.fields.iter().map(|f| f.name.as_str()).collect::<Vec<_>>().join(","),
                        Err(e)=>format!("UNPARSEABLE:{e}"),
                    };
                    eprintln!("LANDSCAPE_DIAGNOSTIC LS_{section:02} export_ref={} error={error} properties={names}",
                        catalog.exports.iter().position(|e| std::ptr::eq(e,export)).unwrap_or(usize::MAX)+1);
                    landscape_objects+=1;
                    continue;
                }
            };
            let ref_id=usize::try_from(component.heightmap_texture_ref.checked_sub(1)
                .ok_or("heightmap reference is zero or negative")?)
                .map_err(|_| "heightmap is an unresolved source import")?;
            let tex_export=catalog.exports.get(ref_id).ok_or("source heightmap export out of range")?;
            let mip=texture::first_mip_bgra8(
                &catalog,&package_file,&companion,&external_bulk,tex_export
            )?;
            let patch=terrain::build_patch(&component,&mip)?;
            seam_audit.admit(&patch)?;
            vertices+=patch.vertex_count();
            triangles+=patch.triangle_count();
            for pixel in mip.bgra8.chunks_exact(4) {
                let h=((pixel[2] as u16)<<8)|pixel[1] as u16;
                height_min=height_min.min(h);
                height_max=height_max.max(h);
                decoded_height_texels+=1;
            }
            section_top_mips+=1;
            println!("HEIGHTMAP_SOURCE LS_{section:02} component_base={:?} ref={} dimensions={}x{} bulk_offset={} height0={} height_end={}",
                component.section_base,component.heightmap_texture_ref,mip.width,mip.height,
                mip.source_bulk_offset,mip.height_u16(0,0)?,mip.height_u16(mip.width-1,mip.height-1)?);
            total_components+=1;
            landscape_objects+=1;
            if component.section_base_serialized.iter().any(|stored| !stored) {
                omitted_grid_components+=1;
            }
            if !occupied.insert((component.section_base[0],component.section_base[1])) {
                return Err(format!("duplicate source landscape grid position {:?}",component.section_base));
            }
            for axis in 0..2 {
                min[axis]=min[axis].min(component.section_base[axis]);
                max[axis]=max[axis].max(component.section_base[axis]+component.component_size_quads as i32);
            }
            if let Some(name)=&component.heightmap_texture_name {
                *all_textures.entry(format!("LS_{section:02} {name} ref={}",component.heightmap_texture_ref)).or_insert(0)+=1;
            } else {
                return Err(format!("source LS_{section:02} has unresolved heightmap texture index {}",
                    component.heightmap_texture_ref));
            }
            println!("LANDSCAPE LS_{section:02} base={:?} quad_size={} subquad_size={} subdivisions={} heightmap={:?} bias={:?} weightmap_refs={} material_refs={}",
                component.section_base,component.component_size_quads,
                component.subsection_size_quads,component.num_subsections,
                component.heightmap_texture_name,component.heightmap_scale_bias,
                component.weightmap_texture_refs.len(),component.material_instance_refs.len());
        }
        let mut audited_textures=0usize;
        for (export_idx,export) in catalog.exports.iter().enumerate() {
            if catalog.export_class_name(export) != Some("Texture2D") { continue; }
            let data=catalog.export_data(&package_file,&companion,export)?;
            match fortnite_541_importer::properties::scan(&catalog,data) {
                Ok(properties) => {
                    if audited_textures < 3 {
                        let at=properties.bytes_consumed;
                        let end=(at+112).min(data.len());
                        let head=&data[at..end];
                        let printable=String::from_utf8_lossy(head).chars()
                            .map(|c| if c.is_ascii_graphic() { c } else { '.' }).collect::<String>();
                        let prefix=head.iter().map(|x| format!("{x:02x}")).collect::<String>();
                        println!("TEXTURE_SOURCE LS_{section:02} export={} object={} bytes={} tagged_end={} raw_hex={} raw_ascii={}",
                            export_idx+1,catalog.names.get(export.object_name.name_index as usize).map_or("?",String::as_str),
                            data.len(),at,prefix,printable);
                    }
                    audited_textures += 1;
                }
                Err(error)=>eprintln!("TEXTURE_SOURCE_UNPROVEN LS_{section:02} export={} {error}",export_idx+1),
            }
        }
        println!("TEXTURE_SOURCE_SUMMARY LS_{section:02} entries={audited_textures}");
        if landscape_objects==0 {
            return Err(format!("source LS_{section:02} contains no LandscapeComponent objects"));
        }
        println!("SECTION LS_{section:02} source_landscape_components={landscape_objects} verified_first_mips={section_top_mips} original_ubulk_bytes={}",external_bulk.len());
    }
    println!("FORTNITE_541_LANDSCAPE_SOURCE_COMPONENTS={total_components} range_x={}..{} range_y={}..{} heightmaps={:?}",
        min[0],max[0],min[1],max[1],all_textures);
    println!("LANDSCAPE_GRID_COVERAGE decoded={total_components} unique_positions={} omitted_zero_default_fields={omitted_grid_components} first_mip_texels={decoded_height_texels} raw_height_min={height_min} raw_height_max={height_max}",occupied.len());
    println!("SOURCE_TERRAIN_MESH_PROOF vertices={vertices} triangles={triangles} shared_exact_heights={} shared_mismatched_heights={} unique_boundary_points={} mismatch_samples={:?}",
        seam_audit.matching_shared_samples,seam_audit.mismatched_shared_samples,
        seam_audit.unique_boundary_vertices(),seam_audit.mismatches);
    Ok(())
}
fn main() -> ExitCode {
    match run() {
        Ok(())=>ExitCode::SUCCESS,
        Err(e)=>{eprintln!("Fortnite landscape source catalog FAILED: {e}");ExitCode::FAILURE}
    }
}
