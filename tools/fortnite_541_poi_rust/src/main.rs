mod uobject;
mod properties;
mod poi_detail;
mod staticmesh_lod;
mod extract;
mod pak;
mod poi_extract;
mod poi_blueprint;
use std::{env,fs};
fn run()->Result<(),String>{
    let paths=env::args().skip(1).collect::<Vec<_>>();
    if paths.len()==2 {
        let header=fs::read(&paths[0]).map_err(|e|e.to_string())?;
        let exports=fs::read(&paths[1]).map_err(|e|e.to_string())?;
        let class="/Game/Building/ActorBlueprints/Wall/Factory_Wall#4::Factory_Wall_3_C";
        let source=poi_blueprint::original_blueprint_static_mesh(&header,&exports,class)?
            .ok_or("retail Factory_Wall_3 Blueprint did not serialize its original CDO mesh")?;
        println!("FORTNITE_ORIGINAL_FACTORY_BUILDING_CDO_MESH source={:?}",source);
        if source.mesh_package_path!=
            "FortniteGame/Content/Environments/Sets/Factory/Meshes/Factory_Wall_1" {
            return Err("original Factory_Wall_3 CDO mesh identity unexpectedly changed".into());
        }
        println!("FORTNITE_AUTHORED_BLUEPRINT_HIGH_DETAIL_VERIFIED class=Factory_Wall_3_C source=Factory_Wall_1");
        return Ok(());
    }
    if paths.len()!=8 && paths.len()!=12{
        return Err("Expected 8 original POI proof asset paths or 12 including actual Factory Wall and Floor meshes".into());
    }
    if paths.len()==12 {
        for (p,e,kind) in [(8usize,9usize,"factory_wall"),(10,11,"floor_tile")] {
            let h=fs::read(&paths[p]).map_err(|e|e.to_string())?;
            let x=fs::read(&paths[e]).map_err(|e|e.to_string())?;
            let c=uobject::inspect(&h)?;
            let refs=c.exports.iter().enumerate().filter_map(|(i,ex)|
                (c.export_class_name(ex)==Some("StaticMesh"))
                    .then(||c.source_object_path((i+1) as i32))
            ).collect::<Result<Vec<_>,_>>()?;
            println!("FORTNITE_AUTHENTIC_{}_UOBJECT_NAMES {:?}",kind,refs);
            if refs.len()!=1{return Err(format!("original {kind} source must have exactly one mesh export"));}
            let actual=refs[0].rsplit("::").next().unwrap();
            let lod=staticmesh_lod::decode_original_source_mesh(&c,&h,&x,actual)?;
            println!("FORTNITE_SOURCE_FULL_DETAIL_{}_LOD0 vertices={} triangles={} sections={} uv_channels={}",
                kind,lod.vertices.len(),lod.indices.len()/3,lod.sections.len(),lod.total_source_uv_channels);
        }
    }

        return Err("Expected authored foundation.umap foundation.uexp ToiletFactory.umap .uexp HedgeMaze.umap .uexp".into());
    }
    let bytes=paths.iter().map(|p|fs::read(p).map_err(|e|e.to_string()))
        .collect::<Result<Vec<_>,_>>()?;
    let levels=poi_detail::original_poi_foundation_placements(&bytes[0],&bytes[1])?;
    let actual=levels.iter().find(|l|l.world_package.ends_with(
        "/Athena_POI_ToiletFactory_001"
    )).ok_or("original ToiletFactory placement missing")?;
    if actual.streaming_bounds_local_cm.is_none() ||
        !poi_detail::source_hlod_inside_poi_xy(actual,[-62976.,-64512.,0.]) ||
        poi_detail::source_hlod_inside_poi_xy(actual,[-46592.,-65024.,5376.]) {
        return Err("original source-authored POI streaming bounds/HLOD intersection failed".into());
    }
    println!("FORTNITE_SOURCE_DETAILED_POI_BOUNDING_BOX verified={:?}",
        actual.streaming_bounds_local_cm);
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
    let source_mesh_head=fs::read(&paths[6]).map_err(|e|e.to_string())?;
    let source_mesh_exp=fs::read(&paths[7]).map_err(|e|e.to_string())?;
    let meshcat=uobject::inspect(&source_mesh_head)?;
    let lod=staticmesh_lod::decode_original_source_mesh(
        &meshcat,&source_mesh_head,&source_mesh_exp,"S_Cave_Outer_Middle",
    )?;
    println!("FORTNITE_ORIGINAL_HIGH_DETAIL_MESH_LOD0 vertices={} triangles={} sections={} uv_channels={}",
        lod.vertices.len(),lod.indices.len()/3,lod.sections.len(),
        lod.total_source_uv_channels);
    if lod.vertices.len()<24||lod.indices.len()<72 {
        return Err("authenticated original high-detail mesh source decoded incomplete".into());
    }
    println!("FORTNITE_SOURCE_FULL_DETAIL_VALIDATED foundation={} factory_direct={} hedge_direct={}",
        levels.len(),factory.static_mesh_actors.len(),hedge.static_mesh_actors.len());
    Ok(())
}
fn main(){if let Err(e)=run(){eprintln!("FORTNITE_SOURCE_FULL_DETAIL_ERROR: {e}");std::process::exit(1);}}
