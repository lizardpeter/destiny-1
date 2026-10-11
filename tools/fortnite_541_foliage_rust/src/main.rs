mod uobject;
mod properties;
mod foliage;
mod staticmesh_lod;
use std::{env,fs};
fn run()->Result<(),String>{
    let args=env::args().skip(1).collect::<Vec<_>>();
    if args.len()!=8 {
        return Err("usage: proof root.umap root.uexp LS01.umap LS01.uexp Hedge.umap Hedge.uexp Grass.uasset Grass.uexp".into());
    }
    let mut worlds=Vec::new();
    for (i,expected) in [0usize,0,3320].iter().enumerate(){
        let a=fs::read(&args[i*2]).map_err(|e|e.to_string())?;
        let b=fs::read(&args[i*2+1]).map_err(|e|e.to_string())?;
        let world=foliage::inspect_original_foliage_level(&a,&b)?;
        println!("FORTNITE_ORIGINAL_FOLIAGE_WORLD source={} components={} instances={} assets={:?}",
            i,world.components.len(),world.total_instances,world.mesh_packages);
        if world.total_instances!=*expected{
            return Err(format!("source foliage expected count {expected} got {}",world.total_instances));
        }
        for c in &world.components {
            println!("FORTNITE_ORIGINAL_FOLIAGE_COMPONENT mesh={} matrices={} trailing={}",
                c.mesh_identity,c.instances.len(),c.trailing_native_bytes);
            for m in c.instances.iter().take(3){
                println!("FORTNITE_ORIGINAL_FOLIAGE_MATRIX {:?}",m.engine_rows());
            }
        }
        worlds.push(world);
    }
    let vegetation=&worlds[2];
    if vegetation.components.len()!=1 ||
        !vegetation.components[0].mesh_identity.ends_with("::Athena_SM_WavyGrass_TopologyColor"){
        return Err("HedgeMaze source foliage mesh reference changed".into());
    }
    let header=fs::read(&args[6]).map_err(|e|e.to_string())?;
    let exp=fs::read(&args[7]).map_err(|e|e.to_string())?;
    let cat=uobject::inspect(&header)?;
    let mesh=staticmesh_lod::decode_original_source_mesh(
        &cat,&header,&exp,"Athena_SM_WavyGrass_TopologyColor")?;
    println!("FORTNITE_ORIGINAL_FOLIAGE_GRASS_GEOMETRY vertices={} triangles={} sections={} UV_sets={}",
        mesh.vertices.len(),mesh.indices.len()/3,mesh.sections.len(),mesh.total_source_uv_channels);
    if mesh.vertices.is_empty()||mesh.indices.is_empty(){
        return Err("source grass has no actual cooked geometry".into());
    }
    println!("FORTNITE_ORIGINAL_FOLIAGE_NATIVE_PROOF_OK hedge_grass_instances=3320 true_source_mesh=true");
    Ok(())
}
fn main(){if let Err(e)=run(){eprintln!("FOLIAGE_SOURCE_PROOF_FAILED: {e}");std::process::exit(1);}}
