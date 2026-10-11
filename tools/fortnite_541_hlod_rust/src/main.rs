mod uobject;
mod properties;
mod hlod;
mod cubemap_axis;
use std::{env,fs};
fn run()->Result<(),String>{
    let paths=env::args().skip(1).collect::<Vec<_>>();
    if paths.len()!=2 {return Err("usage: fortnite-541-hlod-source-proof original.umap original.uexp".into());}
    let umap=fs::read(&paths[0]).map_err(|e|format!("read source HLOD UMAP: {e}"))?;
    let uexp=fs::read(&paths[1]).map_err(|e|format!("read source HLOD UEXP: {e}"))?;
    let world=hlod::inspect_root_original_hlod(&umap,&uexp)?;
    println!("FORTNITE_NATIVE_ORIGINAL_HLOD_WORLD actors={} mesh_objects={} unique_mesh_packages={} rotations_serialized={} scales_serialized={} world_loc_mismatches={}",
        world.actors.len(),world.referenced_original_mesh_objects.len(),
        world.unique_mesh_packages.len(),world.relative_rotation_serialized,
        world.relative_scale_serialized,world.actors_with_location_disagreement);
    for actor in world.actors.iter().take(4){
        println!("FORTNITE_NATIVE_ORIGINAL_HLOD_ACTOR actor={} ref={} mesh={} position_cm={:?} component_cm={:?} rotation_pyr={:?}",
            actor.actor_source_path,actor.actor_reference,actor.mesh_object_source_path,
            actor.authored_world_location_cm,actor.component_relative_location_cm,
            actor.component_relative_rotation_pyr);
    }
    if world.actors.len()!=429 ||world.referenced_original_mesh_objects.len()!=270||
        world.unique_mesh_packages.len()!=255 {
        return Err("original Fortnite 5.41 HLOD actor and material source population inconsistent".into());
    }
    Ok(())
}
fn main(){
    if let Err(e)=run(){eprintln!("FORTNITE_NATIVE_HLOD_FAILED: {e}");std::process::exit(1);}
}
