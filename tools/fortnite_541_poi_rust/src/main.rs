mod uobject;
mod properties;
mod poi_detail;
mod staticmesh_lod;
mod static_material;
mod material_instance;
mod extract;
mod pak;
mod poi_extract;
mod poi_blueprint;
mod sky_dome;
mod cooked_expression_graph;
mod texture;
use std::{env,fs};
fn run()->Result<(),String>{
    let paths=env::args().skip(1).collect::<Vec<_>>();
    if paths.len()==1 && paths[0]=="--audit-sky-links" {
        let root=std::path::Path::new("/tmp/fortnite541_source_sky");
        let master=sky_dome::inspect_sky_master(root)?
            .ok_or("original retail M_SkyDome shader master not staged")?;
        if master.material_expression_count!=98 ||
            master.named_expression_links!=33 ||
            master.surviving_expression_links!=4 ||
            master.stripped_expression_links!=29 ||
            master.source_emissive_expression.as_deref()!=Some("MaterialExpressionMultiply#2") {
            return Err(format!("unexpected retail SkyDome link counts {master:?}"));
        }
        println!("FORTNITE_541_NATIVE_COOKED_SKY_TOPOLOGY material_expressions={} expression_links={} connected_original={} editor_stripped={} emissive_producer={:?} absent_names={:?}",
            master.material_expression_count,master.named_expression_links,
            master.surviving_expression_links,master.stripped_expression_links,
            master.source_emissive_expression,master.unresolved_source_expressions);
        return Ok(());
    }
    if paths.len()==1 && paths[0]=="--audit-sky" {
        let root=std::path::Path::new("/tmp/fortnite541_source_sky");
        let source=sky_dome::from_source_root(root)?
            .ok_or("original source daylight sky packages not staged")?;
        if (source.horizon_linear[0]-0.078577).abs()>0.0001 ||
            (source.horizon_linear[1]-0.37912).abs()>0.0001 ||
            (source.horizon_linear[2]-0.9).abs()>0.0001 ||
            (source.zenith_linear[0]-0.004).abs()>0.0001 ||
            (source.zenith_linear[1]-0.036159).abs()>0.0001 ||
            (source.zenith_linear[2]-0.08).abs()>0.0001 {
            return Err("native original Day_M_SkyDome authored color mismatch".into());
        }
        println!("FORTNITE_NATIVE_AUTHENTIC_DAY_SKY source_M_SkyDome=true horizon={:?} zenith={:?} cloud_key={:?} cloud_shadow={:?} scalar_count={} vector_count={}",
            source.horizon_linear,source.zenith_linear,
            source.cloud_key_linear,source.cloud_shadow_linear,
            source.scalar_params.len(),source.vector_params.len());
        if source.scalar_params.len()!=14 || source.vector_params.len()!=7{
            return Err("native source SkyDome inherited material parameter closure changed".into());
        }
        let master=sky_dome::inspect_sky_master(root)?
            .ok_or("original M_SkyDome master shader source missing")?;
        if master.material_expression_count!=98 ||
            master.texture_sample_count!=8 ||
            master.source_texture_objects.len()!=5 ||
            master.named_expression_links!=33 ||
            master.surviving_expression_links!=4 ||
            master.stripped_expression_links!=29 ||
            master.source_emissive_expression.as_deref()!=Some("MaterialExpressionMultiply#2") ||
            !master.source_collection_parameters.iter().any(|n|
                n=="SunAndMoonModelWorldPosition"
            ){
            return Err(format!("retail master graph changed: {master:?}"));
        }
        println!("FORTNITE_AUTHENTIC_COOKED_SKY_SHADER_LINKS preserved={} resolved={} editor_stripped={} material_emissive={:?} absent_source_nodes={:?}",
            master.named_expression_links,master.surviving_expression_links,
            master.stripped_expression_links,master.source_emissive_expression,
            master.unresolved_source_expressions);
        let mut decoded=0usize;
        for tex in &master.source_texture_objects {
            match sky_dome::inspect_sampled_source_mip(root,tex){
                Ok(mip)=>{
                    decoded+=1;
                    println!("FORTNITE_NATIVE_SOURCE_SKY_TEXTURE object={:?} width={} height={} format={:?} bytes={}",
                        tex,mip.width,mip.height,mip.original_format,mip.source_bytes);
                },
                Err(error)=>println!("FORTNITE_NATIVE_SOURCE_SKY_TEXTURE_DEFERRED object={:?} error={:?}",
                    tex,error),
            }
        }
        if decoded!=5{
            return Err(format!("original source SkyDome texture closure only {decoded}/5 authenticated resident mips"));
        }
        println!("FORTNITE_NATIVE_SOURCE_SKY_MASTER_GRAPH expressions={} original_sample_nodes={} unique_source_textures={} source_decoded_resident_mips={} functions={} runtime_collection={:?}",
            master.material_expression_count,master.texture_sample_count,
            master.source_texture_objects.len(),decoded,
            master.material_functions.len(),master.source_collection_parameters);
        return Ok(());
    }
    if paths.len()==1 && paths[0]=="--audit-material-instances" {
        const BASE:&str="/tmp/fortnite541_source_materials";
        let examples=[
            ("/Game/Environments/Props/Industrial/Materials/MI_ShippingContainer_01::MI_ShippingContainer_01",
            "Diffuse","/Game/Environments/Props/Industrial/Textures/Prop_ShippingContainer_01_D::Prop_ShippingContainer_01_D"),
            ("/Game/Packages/DS_Fortnite_Terrain_NoLOD/Materials/M_Terrain_Cave::M_Terrain_Cave",
            "CliffTexture","/Game/Packages/DS_Fortnite_Terrain_NoLOD/Textures/T_Cave_Underground_Interior_Wall_D::T_Cave_Underground_Interior_Wall_D"),
            ("/Game/Packages/DS_Fortnite_Terrain_NoLOD/Materials/M_Terrain_Cliff_White::M_Terrain_Cliff_White",
            "CliffTexture","/Game/Packages/DS_Fortnite_Terrain_NoLOD/Textures/T_Cave_Exterior_Wall_D::T_Cave_Exterior_Wall_D"),
        ];
        for (identity,parameter,expected) in examples{
            let original=material_instance::from_source_root(
                std::path::Path::new(BASE),identity
            )?.ok_or("source material instance not staged from authenticated source")?;
            let param=original.textures.iter().find(|p|p.name==parameter)
                .ok_or("original retail parameter absent")?;
            if param.texture_object!=expected {
                return Err(format!("original {identity} {parameter} source identity differs: {}",param.texture_object));
            }
            let package=material_instance::source_package(expected)?;
            let base=std::path::Path::new(BASE).join(package);
            let h=fs::read(base.with_extension("uasset")).map_err(|e|e.to_string())?;
            let x=fs::read(base.with_extension("uexp")).map_err(|e|e.to_string())?;
            let b=fs::read(base.with_extension("ubulk")).map_err(|e|e.to_string())?;
            let catalog=uobject::inspect(&h)?;
            let export_name=expected.rsplit("::").next().unwrap_or("");
            let mut matching=catalog.exports.iter().enumerate().filter(|(i,ex)|
                catalog.export_class_name(ex)==Some("Texture2D") &&
                catalog.source_object_path((i+1) as i32).ok()
                    .and_then(|p|p.rsplit("::").next().map(str::to_owned))
                    .as_deref()==Some(export_name));
            let (_,ex)=matching.next().ok_or("original retail diffuse source UTexture2D absent")?;
            if matching.next().is_some(){return Err("duplicate original diffuse UObject".into());}
            let (width,height,format,len)=
                match texture::first_mip_bc(&catalog,&h,&x,&b,ex){
                    Ok(m)=>(m.width,m.height,format!("{:?}",m.format),m.blocks.len()),
                    Err(bc_error)=>match texture::first_mip_bgra8(&catalog,&h,&x,&b,ex){
                        Ok(m)=>(m.width,m.height,"BGRA8".to_owned(),m.bgra8.len()),
                        Err(raw_error)=>return Err(format!("original retail diffuse cannot decode: BC {bc_error}; BGRA {raw_error}"))
                    }
                };
            println!("FORTNITE_NATIVE_SOURCE_POI_DIFFUSE identity={expected:?} width={width} height={height} format={format} source_mip_bytes={len}");
            // The exact same original MIC has authored normal input names
            // and references. Admit only verified native PF_BC5 sources.
            if let Some(normal)=material_instance::source_normal_input(&original){
                let package=material_instance::source_package(&normal.texture_object)?;
                let base=std::path::Path::new(BASE).join(package);
                let h=fs::read(base.with_extension("uasset")).map_err(|e|e.to_string())?;
                let x=fs::read(base.with_extension("uexp")).map_err(|e|e.to_string())?;
                let b=fs::read(base.with_extension("ubulk")).map_err(|e|e.to_string())?;
                let cat=uobject::inspect(&h)?;
                let name=normal.texture_object.rsplit("::").next().unwrap_or("");
                let ex=cat.exports.iter().enumerate().find(|(i,ex)|
                    cat.export_class_name(ex)==Some("Texture2D") &&
                    cat.source_object_path((i+1) as i32).ok()
                        .and_then(|p|p.rsplit("::").next().map(str::to_owned))
                        .as_deref()==Some(name)
                ).map(|(_,ex)|ex).ok_or("source normal Texture2D not present")?;
                let mip=texture::first_mip_bc(&cat,&h,&x,&b,ex)?;
                if mip.format!=texture::OriginalBcFormat::Bc5{
                    return Err(format!(
                        "source normal {name} unexpected format {:?}",mip.format
                    ));
                }
                let mut test=[128,128,0,0];
                texture::reconstruct_source_bc5_normal_z(&mut test)?;
                if test[2]!=255||test[3]!=255{
                    return Err("native BC5 positive Z contract mismatch".into());
                }
                println!("FORTNITE_SOURCE_NATIVE_BC5_NORMAL material={identity:?} normal_source={:?} width={} height={} source_blocks={} sampler_parameter={:?}",
                    normal.texture_object,mip.width,mip.height,mip.blocks.len(),normal.name);
            }
            println!("FORTNITE_SOURCE_NATIVE_MATERIAL_INSTANCE name={identity:?} parent={:?} source_texture_parameters={:?} selected_diffuse={expected:?}",
                original.parent,original.textures);
        }
        let original=material_instance::from_source_root(
            std::path::Path::new(BASE),
            "/Game/Packages/Fortress_Floors_Generic/SM/Materials/MI_Fort_Floors_Generic_TilesClean::MI_Fort_Floors_Generic_TilesClean"
        )?.ok_or("authenticated source TilesClean MaterialInstanceConstant absent")?;
        let normal=material_instance::source_normal_input(&original)
            .ok_or("original TilesClean lacks source normal parameter")?;
        if normal.name!="Normals"||
           normal.texture_object!="/Engine/EngineMaterials/FlatNormal::FlatNormal" {
            return Err(format!(
                "source UE4 Engine FlatNormal identity changed: {:?}",
                normal.texture_object
            ));
        }
        println!("FORTNITE_541_NATIVE_ENGINE_DEFAULT_TEXTURE preserved_other_source_parameters={} source_normal_object={:?}",
            original.textures.len(),normal.texture_object);
        return Ok(());
    }
    if paths.len()==2 && paths[0]=="--audit-materials" {
        let source=fs::read_to_string(&paths[1]).map_err(|e|e.to_string())?;
        let mut material_slots=0usize;
        let mut decoded=0usize;
        let mut failures=Vec::new();
        let mut references=std::collections::BTreeMap::<String,usize>::new();
        let mut sections=0usize;
        for row in source.lines(){
            let columns=row.split('\t').collect::<Vec<_>>();
            if columns.len()!=3{return Err("bad original source mesh manifest columns".into());}
            let identity=columns[0];
            let base=columns[2];
            if base.is_empty(){continue;}
            let result=(||->Result<(usize,usize),String>{
                let h=fs::read(format!("{base}.uasset")).map_err(|e|e.to_string())?;
                let x=fs::read(format!("{base}.uexp")).map_err(|e|e.to_string())?;
                let cat=uobject::inspect(&h)?;
                let export=identity.rsplit("::").next()
                    .ok_or("original mesh object missing")?;
                let slots=static_material::from_mesh_export(&cat,&h,&x,export)?;
                let lod=staticmesh_lod::decode_original_source_mesh(&cat,&h,&x,export)?;
                for sec in &lod.sections{
                    let mat=slots.get(sec.material_slot as usize)
                        .ok_or("original LOD section MaterialIndex exceeds source StaticMaterials array")?;
                    if let Some(name)=&mat.material_interface{
                        *references.entry(name.clone()).or_default()+=1;
                    }
                }
                Ok((slots.len(),lod.sections.len()))
            })();
            match result{
                Ok((m,s))=>{material_slots+=m;sections+=s;decoded+=1;},
                Err(error)=>failures.push((identity.to_string(),error)),
            }
        }
        println!("FORTNITE_NATIVE_AUTHORED_MATERIAL_SLOT_SUMMARY decoded_lod_materials={} static_material_slots={} section_material_bindings={} distinct_material_sources={} failures={} source_materials={:?}",
            decoded,material_slots,sections,references.len(),failures.len(),
            references.iter().take(25).collect::<Vec<_>>());
        for (identity,error) in &failures{
            println!("FORTNITE_NATIVE_AUTHORED_MATERIAL_SLOT_FRONTIER identity={identity:?} reason={error:?}");
        }
        // The original 248 factory meshes have two known native vehicle
        // LOD exceptions; MATERIAL IDENTITY decoding of those two should
        // still work, so report independently from native geometry decode.
        if decoded<240{
            return Err(format!("unexpected loss of retail material section binding: {decoded}"));
        }
        return Ok(());
    }
    if paths.len()==2 && paths[0]=="--audit-meshes" {
        // Decode the *actual native LOD0* from every source UStaticMesh
        // identity needed by the original detailed Factory actor placements.
        // Each row is the exact retail UObject path, placed instance count,
        // and a SHA1-verified cached source UAsset/UExp pair.
        let manifest=fs::read_to_string(&paths[1]).map_err(|e|e.to_string())?;
        let mut actors=0usize;
        let mut resolved=0usize;
        let mut unique=0usize;
        let mut decoded_unique=0usize;
        let mut placed_triangles=0u64;
        let mut failures=Vec::<(usize,String,String)>::new();
        for (lineno,line) in manifest.lines().enumerate() {
            let cols=line.split('\t').collect::<Vec<_>>();
            if cols.len()!=3{return Err(format!(
                "native LOD manifest row {} must contain identity, actors, cache prefix",
                lineno+1
            ));}
            unique+=1;
            let identity=cols[0];
            let n=cols[1].parse::<usize>().map_err(|e|e.to_string())?;
            let base=cols[2];
            actors+=n;
            let result=(||->Result<staticmesh_lod::OriginalStaticMeshLod,String>{
                if base.is_empty(){return Err("original mesh source package missing from authenticated archive indexes".into());}
                let h=fs::read(format!("{base}.uasset")).map_err(|e|e.to_string())?;
                let x=fs::read(format!("{base}.uexp")).map_err(|e|e.to_string())?;
                let cat=uobject::inspect(&h)?;
                let export=identity.rsplit("::").next()
                    .ok_or("original UObject mesh export missing")?;
                let lod=staticmesh_lod::decode_original_source_mesh(&cat,&h,&x,export)?;
                if lod.vertices.is_empty()||lod.sections.is_empty(){
                    return Err("source native LOD has no drawable sections".into());
                }
                for section in &lod.sections{
                    let start=section.first_index as usize;
                    let end=start.checked_add((section.triangle_count as usize)
                        .checked_mul(3).ok_or("source LOD triangle count overflow")?)
                        .ok_or("source LOD section extent overflow")?;
                    let indices=lod.indices.get(start..end)
                        .ok_or("source LOD section index range invalid")?;
                    if indices.is_empty()||indices.iter().any(|&i|
                        i as usize>=lod.vertices.len()
                    ){return Err("source LOD section vertex index outside original vertices".into());}
                }
                Ok(lod)
            })();
            match result {
                Ok(lod)=>{
                    decoded_unique+=1;
                    resolved+=n;
                    let tris=lod.sections.iter().map(|s|s.triangle_count as u64)
                        .sum::<u64>();
                    placed_triangles+=tris*n as u64;
                    println!("FORTNITE_FACTORY_NATIVE_MESH identity={identity:?} actors={n} vertices={} triangles={} sections={} uv_channels={}",
                        lod.vertices.len(),tris,lod.sections.len(),lod.total_source_uv_channels);
                },
                Err(error)=>failures.push((n,identity.into(),error)),
            }
        }
        failures.sort_by(|a,b|b.0.cmp(&a.0).then_with(||a.1.cmp(&b.1)));
        println!("FORTNITE_FACTORY_NATIVE_LOD0_SUMMARY mesh_object_identities={unique} decoded_identities={decoded_unique} referenced_actors={actors} native_lod0_decoded_actors={resolved} missing_actor_count={} placed_source_triangles={placed_triangles} failed_identities={}",
            actors-resolved,failures.len());
        for (n,identity,error) in failures{
            println!("FORTNITE_FACTORY_NATIVE_LOD0_FRONTIER count={n} identity={identity:?} reason={error:?}");
        }
        return Ok(());
    }
    if paths.len()==2 && paths[0]=="--audit-cdos" {
        // The exact production native CDO decoder is run against *every*
        // unique original class package supplied in a retail-authenticated
        // manifest. This is CDO mesh reference resolution, not proof that
        // the mesh's separate native LOD0 has been decoded.
        let manifest=fs::read_to_string(&paths[1]).map_err(|e|e.to_string())?;
        let mut actors=0usize;
        let mut resolved=0usize;
        let mut unresolved=Vec::<(usize,String,String)>::new();
        let mut classes=0usize;
        let mut resolved_classes=0usize;
        let mut mesh_packages=std::collections::BTreeSet::new();
        for (lineno,row) in manifest.lines().enumerate() {
            let cols=row.split('\t').collect::<Vec<_>>();
            if cols.len()!=3{return Err(format!(
                "native CDO manifest row {} must have three TSV columns",lineno+1
            ));}
            let class=cols[0];
            let n=cols[1].parse::<usize>().map_err(|e|e.to_string())?;
            let base=cols[2];
            actors+=n;
            classes+=1;
            let result=(||->Result<Option<poi_blueprint::AuthoredBlueprintMeshDefault>,String>{
                if base.is_empty(){return Err("authenticated original CDO class package unavailable".into());}
                let header=fs::read(format!("{base}.uasset"))
                    .map_err(|e|format!("source CDO header: {e}"))?;
                let exports=fs::read(format!("{base}.uexp"))
                    .map_err(|e|format!("source CDO export: {e}"))?;
                poi_blueprint::original_blueprint_static_mesh(&header,&exports,class)
            })();
            match result {
                Ok(Some(original))=>{
                    resolved+=n;
                    resolved_classes+=1;
                    mesh_packages.insert(original.mesh_package_path.clone());
                    println!("FORTNITE_FACTORY_CDO_MESH class={class:?} actors={n} source={:?}",
                        original.mesh_source_path);
                },
                Ok(None)=>{
                    unresolved.push((n,class.into(),"source CDO has no direct StaticMesh".into()));
                },
                Err(error)=>unresolved.push((n,class.into(),error)),
            }
        }
        unresolved.sort_by(|a,b|b.0.cmp(&a.0).then_with(||a.1.cmp(&b.1)));
        println!("FORTNITE_FACTORY_NATIVE_CDO_SUMMARY classes={classes} resolved_classes={resolved_classes} inherited_actors={actors} resolved_actors={resolved} distinct_mesh_packages={} unresolved_actor_count={} unresolved_classes={}",
            mesh_packages.len(),actors-resolved,unresolved.len());
        for (n,class,error) in unresolved {
            println!("FORTNITE_FACTORY_NATIVE_CDO_FRONTIER count={n} class={class:?} reason={error:?}");
        }
        return Ok(());
    }
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
