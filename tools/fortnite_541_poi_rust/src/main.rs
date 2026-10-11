mod uobject;
mod properties;
mod poi_detail;
use std::{env,fs};
fn run()->Result<(),String>{
    let paths=env::args().skip(1).collect::<Vec<_>>();
    if paths.len()!=6{
        return Err("Expected authored foundation.umap foundation.uexp ToiletFactory.umap .uexp HedgeMaze.umap .uexp".into());
    }
    let bytes=paths.iter().map(|p|fs::read(p).map_err(|e|e.to_string()))
        .collect::<Result<Vec<_>,_>>()?;
    let levels=poi_detail::original_poi_foundation_placements(&bytes[0],&bytes[1])?;
    let actual=levels.iter().find(|l|l.world_package.ends_with(
        "/Athena_POI_ToiletFactory_001"
    )).ok_or("original ToiletFactory placement missing")?;
    if actual.location_cm!=[-62976.,-64512.,0.] ||
        (actual.rotation_pyr_deg[1]+90.).abs()>0.01{
        return Err(format!("authenticated ToiletFactory root transform changed: {actual:?}"));
    }
    println!("FORTNITE_SOURCE_POI_FOUNDATIONS decoded_worlds={} factory={:?}",
        levels.len(),actual);
    if levels.len()<35{return Err("source POI foundation list unreasonably incomplete".into());}
    let factory=poi_detail::original_poi_direct_static_actors(&bytes[2],&bytes[3])?;
    println!("FORTNITE_SOURCE_POI_FULL_DETAIL factory_source_actors={} direct_mesh_actors={} inherited_components={} unique_mesh_packages={} sample={:?}",
        factory.source_actors,factory.static_mesh_actors.len(),
        factory.inherited_blueprint_components,factory.unique_mesh_packages.len(),
        factory.static_mesh_actors.iter().take(3).collect::<Vec<_>>());
    if factory.static_mesh_actors.len()<150{
        return Err("original full detail factory static meshes not recovered".into());
    }
    let hedge=poi_detail::original_poi_direct_static_actors(&bytes[4],&bytes[5])?;
    println!("FORTNITE_SOURCE_POI_FULL_DETAIL hedge_source_actors={} direct_mesh_actors={} inherited_components={} unique_mesh_packages={}",
        hedge.source_actors,hedge.static_mesh_actors.len(),
        hedge.inherited_blueprint_components,hedge.unique_mesh_packages.len());
    if hedge.static_mesh_actors.is_empty(){
        return Err("original HedgeMaze detail static meshes unresolved".into());
    }
    for a in factory.static_mesh_actors.iter().take(5){
        let rows=poi_detail::compose_engine_rows(
            poi_detail::engine_rows(actual.location_cm,actual.rotation_pyr_deg,actual.scale_xyz),
            poi_detail::engine_rows(a.location_cm,a.rotation_pyr_deg,a.scale_xyz)
        );
        println!("FORTNITE_SOURCE_POI_WORLD_TRANSFORM actor={} mesh={} rows={:?}",
            a.source_actor,a.source_mesh_object,rows);
    }
    println!("FORTNITE_SOURCE_FULL_DETAIL_VALIDATED foundation={} factory_direct={} hedge_direct={}",
        levels.len(),factory.static_mesh_actors.len(),hedge.static_mesh_actors.len());
    Ok(())
}
fn main(){if let Err(e)=run(){eprintln!("FORTNITE_SOURCE_FULL_DETAIL_ERROR: {e}");std::process::exit(1);}}
