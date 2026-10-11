mod uobject;
mod properties;
mod hlod;
mod streaming_levels;
mod cubemap_axis;
mod staticmesh_lod;
mod hlod_material;
mod texture;
use std::{env,fs};
fn run()->Result<(),String>{
    let paths=env::args().skip(1).collect::<Vec<_>>();
    if paths.len()!=4 &&paths.len()!=5 &&paths.len()!=6 {return Err("usage: fortnite-541-hlod-source-proof original.umap original.uexp original_mesh.uasset original_mesh.uexp [source_object_name]".into());}
    let umap=fs::read(&paths[0]).map_err(|e|format!("read source HLOD UMAP: {e}"))?;
    let uexp=fs::read(&paths[1]).map_err(|e|format!("read source HLOD UEXP: {e}"))?;
    let world=hlod::inspect_root_original_hlod(&umap,&uexp)?;
    let levels=streaming_levels::original_root_streaming_levels(&umap,&uexp)?;
    println!("FORTNITE_NATIVE_SOURCE_STREAMED_LEVELS count={} names={:?}",
        levels.len(),levels.iter().map(|l|&l.source_world_asset).collect::<Vec<_>>());
    if levels.len()!=16{return Err("verified Athena source root should have 16 streamed UWorld edges".into());}
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
    let source_header=fs::read(&paths[2]).map_err(|e|format!("original mesh header: {e}"))?;
    let source_exp=fs::read(&paths[3]).map_err(|e|format!("original mesh source export: {e}"))?;
    let cat=uobject::inspect(&source_header)?;
    let mesh=staticmesh_lod::decode_original_source_mesh(
        &cat,&source_header,&source_exp,
        paths.get(4).map(String::as_str)
            .unwrap_or("SM_Athena_REM_1x1_Shack_a_0_Boardwalk_Archway#29")
    )?;
    println!("FORTNITE_NATIVE_ORIGINAL_LOD0_GEOMETRY vertices={} indices={} tris={} sections={} uv_channels={} first_vertex={:?} first_indices={:?}",
        mesh.vertices.len(),mesh.indices.len(),mesh.indices.len()/3,
        mesh.sections.len(),mesh.total_source_uv_channels,
        mesh.vertices.first().map(|v|(v.position_cm,v.uv0,v.uv1)),
        mesh.indices.iter().take(16).collect::<Vec<_>>()
    );
    if paths.len()==4 &&
        (mesh.vertices.len()!=184 ||mesh.indices.len()!=372 ||
        mesh.sections.len()!=1 ||mesh.total_source_uv_channels!=2) {
        return Err("original Fortnite HLOD sample geometry inconsistent".into());
    }
    let slots=hlod_material::authored_static_mesh_diffuse_slots(
        &cat,&source_header,&source_exp,
        paths.get(4).map(String::as_str)
            .unwrap_or("SM_Athena_REM_1x1_Shack_a_0_Boardwalk_Archway#29")
    )?;
    println!("FORTNITE_AUTHORED_HLOD_DIFFUSE_SLOTS count={} mapped={} identities={:?}",
        slots.len(),slots.iter().filter(|v|v.diffuse_export_index.is_some()).count(),
        slots.iter().map(|s|(&s.source_material_identity,&s.authored_diffuse_identity))
            .collect::<Vec<_>>()
    );
    if let Some(source_bulk)=paths.get(5){
        let bulk=fs::read(source_bulk)
            .map_err(|e|format!("authenticated original texture bulk missing: {e}"))?;
        for (slot_index,slot) in slots.iter().enumerate(){
            let Some(export_idx)=slot.diffuse_export_index else{continue};
            let mip=texture::first_mip_bc(
                &cat,&source_header,&source_exp,&bulk,&cat.exports[export_idx],
            )?;
            println!("FORTNITE_ORIGINAL_HLOD_BC_DIFFUSE slot={} width={} height={} source_blocks={} format={:?} src_name={:?}",
                slot_index,mip.width,mip.height,mip.blocks.len(),mip.format,
                slot.authored_diffuse_identity
            );
            if mip.width<4 ||mip.height<4{return Err("original HLOD atlas source invalid".into());}
        }
    }
    Ok(())
}
fn main(){
    if let Err(e)=run(){eprintln!("FORTNITE_NATIVE_HLOD_FAILED: {e}");std::process::exit(1);}
}
