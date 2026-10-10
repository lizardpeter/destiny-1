//! Strict source-backed Athena landscape placement census across all six
//! original Fortnite 5.41 landscape sublevel packages.
//! No mesh generation or engine-specific rendering behavior.
use std::{collections::BTreeMap, env, fs, path::PathBuf, process::ExitCode};
use fortnite_541_importer::{landscape, uobject};

fn run() -> Result<(), String> {
    let root = env::args_os().nth(1).map(PathBuf::from)
        .ok_or("usage: landscape_catalog PATH_TO_ATHENA_SOURCE_ROOT")?;
    let mut total_components=0usize;
    let mut all_textures=BTreeMap::<String,usize>::new();
    let mut min=[i32::MAX;2];
    let mut max=[i32::MIN;2];
    for section in 0..6 {
        let base=root.join(format!("FortniteGame/Content/Athena/Maps/Landscape/Athena_Terrain_LS_{section:02}"));
        let package_file=fs::read(base.with_extension("umap"))
            .map_err(|e| format!("read source LS_{section:02} UMAP: {e}"))?;
        let companion=fs::read(base.with_extension("uexp"))
            .map_err(|e| format!("read source LS_{section:02} UEXP: {e}"))?;
        let catalog=uobject::inspect(&package_file)?;
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
            total_components+=1;
            landscape_objects+=1;
            for axis in 0..2 {
                min[axis]=min[axis].min(component.section_base[axis]);
                max[axis]=max[axis].max(component.section_base[axis]+component.component_size_quads as i32);
            }
            if let Some(name)=&component.heightmap_texture_name {
                *all_textures.entry(name.clone()).or_insert(0)+=1;
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
        if landscape_objects==0 {
            return Err(format!("source LS_{section:02} contains no LandscapeComponent objects"));
        }
        println!("SECTION LS_{section:02} source_landscape_components={landscape_objects}");
    }
    println!("FORTNITE_541_LANDSCAPE_SOURCE_COMPONENTS={total_components} range_x={}..{} range_y={}..{} heightmaps={:?}",
        min[0],max[0],min[1],max[1],all_textures);
    Ok(())
}
fn main() -> ExitCode {
    match run() {
        Ok(())=>ExitCode::SUCCESS,
        Err(e)=>{eprintln!("Fortnite landscape source catalog FAILED: {e}");ExitCode::FAILURE}
    }
}
