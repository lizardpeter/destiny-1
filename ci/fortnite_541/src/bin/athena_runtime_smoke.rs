//! Public CI integration check against exactly the original 94 source terrain patches.
use std::{env,path::PathBuf,process::ExitCode};
fn run()->Result<(),String>{
    let root=env::args_os().nth(1).map(PathBuf::from)
        .ok_or("expected source extraction folder")?;
    let terrain=fortnite_541_importer::athena::load_verified_athena(&root)?;
    let spawn=terrain.preview_spawn_source_xyz()?;
    let verts:usize=terrain.patches.iter().map(|p|p.vertex_count()).sum();
    let triangles:usize=terrain.patches.iter().map(|p|p.triangle_count()).sum();
    println!("FORTNITE_RUNTIME_SOURCE_TERRAIN patches={} vertices={verts} triangles={triangles} seams={} source_spawn={spawn:?}",
        terrain.patches.len(),terrain.shared_height_samples);
    if terrain.patches.len()!=94 || verts!=1540096 || triangles!=3032252 ||
        terrain.shared_height_samples!=20413{
        return Err("retail Athena source mesh census changed or incomplete".into());
    }
    let allocations=terrain.paint_patches.iter().map(|p|p.layers.len()).sum::<usize>();
    println!("FORTNITE_SOURCE_PAINT_CLOSED references={} allocations={} unique_layers={} patches={} layer_names={:?}",
        terrain.source_weightmap_texture_refs,allocations,terrain.source_layer_info_paths.len(),
        terrain.paint_patches.len(),terrain.source_layer_info_paths);
    if terrain.source_weightmap_texture_refs!=208
        ||terrain.source_layer_allocation_count!=669
        ||allocations!=669||terrain.paint_patches.len()!=94 {
        return Err("original retail Athena paint allocation/weightmap census does not close".into());
    }
    if !terrain.paint_patches.iter().zip(&terrain.patches).all(|(paint,patch)|
        paint.section_base==patch.section_base
        &&paint.side==patch.side()
        &&paint.layers.iter().all(|l|l.weights.len()==patch.vertex_count())
    ){
        return Err("original Athena paint samples do not align to exact source heightfield vertices".into());
    }
    println!("PASS: source verified and in-game-neutral-admission terrain geometry ready");
    Ok(())
}
fn main()->ExitCode{match run(){Ok(())=>ExitCode::SUCCESS,Err(e)=>{eprintln!("{e}");ExitCode::FAILURE}}}
