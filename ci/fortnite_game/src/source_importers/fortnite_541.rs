//! Native in-game admission of Fortnite 5.41 Athena's VERIFIED source terrain.
//!
//! This is an explicit heightfield DIAGNOSTIC preview, not a claim of Fortnite
//! albedo/shader/sky parity. Geometry + collisions derive from original UE4
//! heightmaps. No importer-specific Vulkan paths or fabricated map geometry.
use std::{env, path::{Path,PathBuf}, sync::{Arc,Mutex,OnceLock}, time::Instant};
use crate::mesh_render_data::{environment::LoadedMapVisuals,GeneratedSourceMap};
use neutral_scene::{
    NeutralScene,NeutralMesh,NeutralVertex,NeutralMaterial,NeutralTexture,
    NeutralInstance,NeutralAlpha,NeutralLayer,IDENTITY_ROWS,
};
use super::{neutral_bridge,SourceImportManifest};

pub const MAP_ID: &str="fortnite_541_athena_terrain_preview";

pub(super) fn can_generate(map_id:&str)->bool{map_id==MAP_ID}
pub(super) fn generated_map_list()->Vec<(String,String)>{
    vec![(MAP_ID.to_owned(),"Fortnite 5.41 — Athena (source terrain diagnostic)".to_owned())]
}
pub(super) fn generated_menu_hierarchy(map_id:&str)->Option<(String,String)>{
    can_generate(map_id).then(||("Fortnite 5.41".to_owned(),"Athena — source heightfield preview".to_owned()))
}
pub(super) fn generated_source_map(map_id:&str)->Result<GeneratedSourceMap,String>{
    if !can_generate(map_id){return Err(format!("unrecognized Fortnite source map {map_id}"));}
    let terrain=source_terrain()?;
    let src=terrain.preview_spawn_source_xyz()?;
    // UE4 local Z up -> engine Y up. The spawn is lifted by standing eye
    // height, only for navigating this source diagnostic preview.
    let authored_world=terrain.world_transform.world_meters(src);
    let mut spawn=engine_point(authored_world);
    spawn[1]+=1.8;
    Ok(GeneratedSourceMap{
        display_name:"Fortnite 5.41 — Athena (source terrain diagnostic)".to_owned(),
        spawns:vec![(spawn,0.0)],
    })
}
fn source_directory()->Result<PathBuf,String>{
    if let Some(path)=env::var_os("RUST_TEST_FORTNITE_541_ATHENA_SOURCE_ROOT"){
        let path=PathBuf::from(path);
        if path.is_dir(){return Ok(path);}
        return Err(format!("RUST_TEST_FORTNITE_541_ATHENA_SOURCE_ROOT={} does not exist",path.display()));
    }
    let relative=Path::new("asset_import/work/fortnite_541/athena/source");
    let candidates=[
        Path::new(env!("CARGO_MANIFEST_DIR")).join(relative),
        env::current_dir().unwrap_or_default().join(relative),
    ];
    if let Some(folder)=candidates.iter().find(|p|p.join(
        "FortniteGame/Content/Athena/Maps/Landscape/Athena_Terrain_LS_00.umap"
    ).is_file()) {
        return Ok(folder.clone());
    }
    // Prefer an already-owned local Fortnite build over external tooling:
    // native authenticated extraction happens once when a map is selected,
    // never on the renderer/input/audio paths. Reuse the ignored work cache.
    let local_pak=env::var_os("RUST_TEST_FORTNITE_541_PAK").map(PathBuf::from)
        .or_else(||fortnite_541_importer::locate_source_root().map(|root|
            root.join("FortniteGame/Content/Paks/pakchunk0-WindowsClient.pak")
        ));
    if let Some(pak)=local_pak {
        let target=Path::new(env!("CARGO_MANIFEST_DIR")).join(relative);
        let result=fortnite_541_importer::extract::prepare_local_athena(&pak,&target)?;
        println!("Fortnite 5.41: {} original SHA-1-verified landscape packages ready ({} extracted, {} bytes newly written) from {}",
            result.verified_files,result.extracted_files,result.bytes_extracted,pak.display());
        return Ok(target);
    }
    Err("Fortnite 5.41 Athena terrain requires source data. Set RUST_TEST_FORTNITE_541_PAK to your local pakchunk0-WindowsClient.pak for automatic native extraction, or run python asset_import/importers/fortnite_541/tools/fetch_athena_541.py --all-landscape --with-terrain-materials for original R2 packages.".into())
}
type TerrainCache=Mutex<Option<Arc<fortnite_541_importer::athena::AthenaTerrain>>>;
fn terrain_cache()->&'static TerrainCache {
    static CACHE:OnceLock<TerrainCache>=OnceLock::new();
    CACHE.get_or_init(||Mutex::new(None))
}
fn source_terrain()->Result<Arc<fortnite_541_importer::athena::AthenaTerrain>,String>{
    // Cache only between map selection (which needs a ground spawn) and map
    // scene build; do NOT pin ~50 MB of source meshes for the lifetime of
    // the process or cache a failed source lookup after the user adds files.
    let mut cache=terrain_cache().lock().map_err(|_|"Athena terrain cache lock poisoned")?;
    if let Some(t)=cache.as_ref(){return Ok(Arc::clone(t));}
    let root=source_directory()?;
    let t=Arc::new(fortnite_541_importer::athena::load_verified_athena(&root)?);
    *cache=Some(Arc::clone(&t));
    Ok(t)
}

/// Convert source UE Z-up right-handed position into the generic Y-up world.
fn engine_point(source:[f32;3])->[f32;3]{
    [source[0],source[2],-source[1]]
}
fn source_patch_normal(
    patch:&fortnite_541_importer::terrain::LocalTerrainPatch,
    world:&fortnite_541_importer::landscape::LandscapeWorldTransform,
    x:usize,y:usize
)->[f32;3]{
    let n=patch.side()-1;
    let left=patch.vertices_source_xyz[y*patch.side()+x.saturating_sub(1)][2];
    let right=patch.vertices_source_xyz[y*patch.side()+(x+1).min(n)][2];
    let up=patch.vertices_source_xyz[y.saturating_sub(1)*patch.side()+x][2];
    let down=patch.vertices_source_xyz[(y+1).min(n)*patch.side()+x][2];
    let dx=(right-left)/((x+1).min(n)-x.saturating_sub(1)).max(1) as f32;
    let dy=(down-up)/((y+1).min(n)-y.saturating_sub(1)).max(1) as f32;
    // UE5/UE4 source height is unscaled relative to the actor root.
    // The six authenticated 5.41 roots scale XY by 200.7874 and Z by 50;
    // normals must use the same derivatives as the physical world mesh.
    let sx=world.local_scale_cm[2]/world.local_scale_cm[0];
    let sy=world.local_scale_cm[2]/world.local_scale_cm[1];
    let v=[-dx*sx,1.,dy*sy];
    let len=(v[0]*v[0]+v[1]*v[1]+v[2]*v[2]).sqrt().max(1e-8);
    [v[0]/len,v[1]/len,v[2]/len]
}
/// Exact source elevation visualizer. RGB is synthesized solely for
/// diagnostics and MUST NOT be mistaken for Fortnite's authored textures.
fn diagnostic_value(h:u16,min:u16,max:u16)->u8{
    let span=(max as u32).saturating_sub(min as u32).max(1);
    (64+((h as u32-min as u32)*191/span)).min(255) as u8
}
/// Convert source-authenticated UE4 BC1/BC3 top mip bytes into an actual
/// source-neutral texture asset. Do not assign this to a terrain material
/// until its ORIGINAL TextureSample UV/sampler/material-function binding is
/// reconstructed; otherwise the engine would display falsely colored land.
///
/// This runs only when invoked for material admission, not per frame or on
/// input/camera submission. The generic renderer can upload original BC data
/// without recompression or a Fortnite-specific Vulkan shader.
pub(super) fn source_original_terrain_bc_texture(
    root:&Path,
    source_name:&str,
)->Result<NeutralTexture,String>{
    let source_path=match source_name {
        "T_Athena_Terrain_CombinedColors_01"=>
            "Athena/Environments/Landscape/Textures/T_Athena_Terrain_CombinedColors_01",
        "T_Athena_Terrain_Topo_Mask"=>
            "Athena/Environments/Landscape/Textures/T_Athena_Terrain_Topo_Mask",
        _=>return Err(format!("unresolved original Athena texture identity {source_name}")),
    };
    let base=root.join("FortniteGame/Content").join(source_path);
    let source_package=std::fs::read(base.with_extension("uasset"))
        .map_err(|e|format!("original Athena {source_name}.uasset: {e}"))?;
    let source_export=std::fs::read(base.with_extension("uexp"))
        .map_err(|e|format!("original Athena {source_name}.uexp: {e}"))?;
    let source_bulk=std::fs::read(base.with_extension("ubulk"))
        .map_err(|e|format!("original Athena {source_name}.ubulk: {e}"))?;
    let catalog=fortnite_541_importer::uobject::inspect(&source_package)?;
    let source_textures=catalog.exports.iter().filter(|export|
        catalog.export_class_name(export)==Some("Texture2D")).collect::<Vec<_>>();
    if source_textures.len()!=1 {
        return Err(format!("expected one authenticated Texture2D export in {source_name}, got {}",source_textures.len()));
    }
    let mip=fortnite_541_importer::texture::first_mip_bc(
        &catalog,&source_package,&source_export,&source_bulk,source_textures[0],
    )?;
    let (kind,format)=match mip.format{
        fortnite_541_importer::texture::OriginalBcFormat::Bc1=>
            (neutral_scene::BcKind::Bc1,neutral_scene::NeutralBlockFormat::Bc1),
        fortnite_541_importer::texture::OriginalBcFormat::Bc3=>
            (neutral_scene::BcKind::Bc3,neutral_scene::NeutralBlockFormat::Bc3),
    };
    let rgba=neutral_scene::decode_bc(mip.blocks,mip.width,mip.height,kind)
        .ok_or("original Fortnite BC texel decoding rejected authenticated mip")?;
    if rgba.len()!=mip.width as usize*mip.height as usize*4 {
        return Err(format!("original {source_name} BC texel count mismatch"));
    }
    Ok(NeutralTexture{
        name:format!("FORTNITE_541_ORIGINAL_{source_name}_TOP_MIP"),
        width:mip.width,height:mip.height,rgba,
        mips:Vec::new(),
        compressed:Some(neutral_scene::NeutralCompressedTexture{
            format,
            levels:vec![neutral_scene::NeutralCompressedLevel {
                width:mip.width,height:mip.height,blocks:mip.blocks.to_vec(),
            }],
        }),
    })
}

/// Best-effort admission of *original* Fortnite BR time-of-day source.
/// The s4 archive is next to the already auto-discovered main PAK, so no
/// manual command or user-specific path is needed. Missing optional split
/// files remain explicit and never manufacture a replacement sky/sun.
fn original_timeofday(root:&Path)->Result<Option<fortnite_541_importer::timeofday::OriginalTimeOfDay>,String>{
    let file=root.join("FortniteGame/Content/TimeOfDay/TODM/BR/TODM_BR");
    let header=file.with_extension("uasset");
    let export=file.with_extension("uexp");
    if header.is_file()!=export.is_file(){
        return Err("Fortnite TODM_BR original source cache contains only half the package".into());
    }
    if !header.is_file(){
        let main=env::var_os("RUST_TEST_FORTNITE_541_PAK").map(PathBuf::from)
            .or_else(||fortnite_541_importer::locate_source_root().map(|r|
                r.join("FortniteGame/Content/Paks/pakchunk0-WindowsClient.pak")));
        let Some(main)=main else{return Ok(None)};
        if !main.with_file_name("pakchunk0_s4-WindowsClient.pak").is_file(){
            return Ok(None);
        }
        let prepared=fortnite_541_importer::extract::prepare_original_todm_br(&main,root)?;
        println!("Fortnite 5.41: TODM_BR original time-of-day: {} SHA-1-authenticated files, {} newly extracted bytes from original split s4 PAK",
            prepared.verified_files,prepared.bytes_extracted);
    }
    fortnite_541_importer::timeofday::from_source_root(root).map(Some)
}

fn scene_from_source(t:&fortnite_541_importer::athena::AthenaTerrain)->Result<NeutralScene,String>{
    let min=t.patches.iter().flat_map(|p|p.height_samples.iter().copied())
        .min().ok_or("Athena source contains no terrain samples")?;
    let max=t.patches.iter().flat_map(|p|p.height_samples.iter().copied())
        .max().ok_or("Athena source contains no terrain samples")?;
    let mut scene=NeutralScene{
        programs:Vec::new(),meshes:Vec::with_capacity(t.patches.len()),
        instances:Vec::with_capacity(t.patches.len()),
        program_data_controllers:Vec::new(),
        materials:Vec::with_capacity(t.patches.len()),
        textures:Vec::with_capacity(t.patches.len()),
        lightmaps:Vec::new(),irradiance_field:None,source_volume:None,
        local_lights:Vec::new(),sun:None,sky:None,fog:None,grade:None,
        reflection_probes:Vec::new(),lighting:None,instance_vertex_data:Vec::new(),
        collision:Vec::with_capacity(t.patches.iter().map(|p|p.triangle_count()).sum()),
        report:Default::default(),
    };
    let mut collision_triangles=0usize;
    for (index,patch) in t.patches.iter().enumerate(){
        let side=patch.side();
        let mut vertices=Vec::with_capacity(patch.vertices_source_xyz.len());
        let mut diagnostic_pixels=Vec::with_capacity(patch.height_samples.len()*4);
        for (j,source) in patch.vertices_source_xyz.iter().copied().enumerate(){
            let x=j%side;
            let y=j/side;
            let h=patch.height_samples[j];
            let v=diagnostic_value(h,min,max);
            diagnostic_pixels.extend_from_slice(&[v,v,v,255]);
            vertices.push(NeutralVertex{
                position:engine_point(t.world_transform.world_meters(source)),
                normal:source_patch_normal(patch,&t.world_transform,x,y),
                tangent:[1.,0.,0.,1.],
                uv:[x as f32/(side-1) as f32,y as f32/(side-1) as f32],
                color:[1.;4],data:[0.;4],lightmap_uv:[0.;2],
                layer_weights:[0.;2],layer_uvs:[[0.;2];2],
            });
        }
        // Our source->engine transform preserves handedness, but the
        // source heightfield's [a,c,b] index order points *down* in Y-up.
        // Reverse it for visible/collidable upward-facing terrain.
        let mut indices=Vec::with_capacity(patch.indices.len());
        for tri in patch.indices.chunks_exact(3){
            indices.extend_from_slice(&[tri[0],tri[2],tri[1]]);
        }
        collision_triangles+=indices.len()/3;
        for tri in indices.chunks_exact(3){
            scene.collision.push([
                vertices[tri[0] as usize].position,
                vertices[tri[1] as usize].position,
                vertices[tri[2] as usize].position,
            ]);
        }
        scene.meshes.push(NeutralMesh{
            name:format!("Athena_Landscape_{}_{}",patch.section_base[0],patch.section_base[1]),
            material:index,vertices,indices,lightmap:None,model_vertex_base:0,
            vertex_light:None,source_vertices:None,
        });
        scene.instances.push(NeutralInstance{
            mesh:index,rows:IDENTITY_ROWS,motion:None,camera_relative:false,
            irradiance_sh:None,reflection_probe:None,source_reflection_probe:None,
            sun_visibility:None,program_data:[[0.;4];8],program_data_valid_rows:0,
            vertex_data_override:None,
        });
        scene.textures.push(NeutralTexture{
            name:format!("FORTNITE_541_DIAGNOSTIC_HEIGHT_NOT_ALBEDO_{index}"),
            width:side as u32,height:side as u32,rgba:diagnostic_pixels,
            mips:Vec::new(),compressed:None,
        });
        scene.materials.push(NeutralMaterial{
            name:format!("DIAGNOSTIC_ONLY_SOURCE_HEIGHT_NOT_FORTNITE_MATERIAL_{index}"),
            base_color_texture:Some(index),normal_texture:None,
            specular_texture:None,metallic_roughness_texture:None,emissive_texture:None,
            metallic:0.,emissive:[0.;3],roughness:1.,point_sampled:false,
            gloss_from_color_alpha:false,alpha:NeutralAlpha::Opaque,
            double_sided:false,front_culled:false,unlit:true,emissive_scale:1.,
            layers:[NeutralLayer::default();2],visible:true,collides:true,program:None,
        });
    }
    scene.report.lines.push(format!(
        "Athena source geometry: {} verified components, {} exact heightfield triangles; {} matching source seam samples", 
        scene.meshes.len(),collision_triangles,t.shared_height_samples
    ));
    scene.report.lines.push(format!(
        "Original Athena landscape world transform verified across all six proxy roots: origin_cm={:?}, local_scale_cm={:?}, displayed in physical metres (Y-up).",
        t.world_transform.grid_origin_cm,t.world_transform.local_scale_cm
    ));
    scene.report.lines.push(format!(
        "DIAGNOSTIC ONLY: height-derived grayscale, not source Fortnite albedo/normal/material shader. No original sky, sunlight, world props or authored player starts yet."
    ));
    // These are AUTHORED landscape paint-control inputs recovered from their
    // original 5.41 BGRA8 channels. They are not RGB terrain albedo and must
    // NOT be mixed into diagnostic colors or silently renamed as shaders.
    if t.paint_patches.len()!=t.patches.len() {
        return Err("Fortnite original painted patches do not match terrain".into());
    }
    scene.report.lines.push(format!(
        "Original terrain paint data recovered: {} source weightmap Texture2D references, {} tagged LayerInfo allocations, {} unique LayerInfo objects over {} patches. Original RGB/normal/shader dependencies still unavailable for SurfaceProgram admission.",
        t.source_weightmap_texture_refs,t.source_layer_allocation_count,
        t.source_layer_info_paths.len(),t.paint_patches.len()
    ));
    scene.report.lines.push(format!(
        "Original source material references (NOT admitted as render shaders): {:?}",t.source_material_paths
    ));
    Ok(scene)
}
pub(super) fn import_visuals(
    map_id:&str,_map_directory:&Path,_manifest:&SourceImportManifest
)->Result<LoadedMapVisuals,String>{
    if !can_generate(map_id){return Err(format!("unknown Fortnite diagnostic map '{map_id}'"));}
    let started=Instant::now();
    let source=source_terrain()?;
    let mut scene=scene_from_source(&source)?;
    drop(source);
    // The original game Blueprint identifies phase 1 as daytime, 07:00 to
    // 19:00. Select that AUTHORED phase for this static preview, not an
    // invented day/night clock. Preserve missing dynamic sun direction.
    let original_asset_root=source_directory()?;
    let main_pak=env::var_os("RUST_TEST_FORTNITE_541_PAK").map(PathBuf::from)
        .or_else(||fortnite_541_importer::locate_source_root().map(|r|
            r.join("FortniteGame/Content/Paks/pakchunk0-WindowsClient.pak")));
    // An explicitly pre-extracted source root (e.g. the public original-byte
    // test harness) owns its own source admission. Never try to re-extract
    // omitted sparse fixture spans from that fixture's logical original PAK.
    if env::var_os("RUST_TEST_FORTNITE_541_ATHENA_SOURCE_ROOT").is_none() {
    if let Some(main)=main_pak.filter(|p|p.is_file()) {
        // Source-specific import happens ONCE at map load. All original
        // assets stay outside Git and the performance-sensitive frame loop.
        let prepared=fortnite_541_importer::extract::prepare_original_environment_sources(
            &main,&original_asset_root
        )?;
        scene.report.lines.push(format!(
            "Recovered {} SHA1-authenticated original 5.41 sky/ambient/terrain-material source files, {} newly extracted bytes from local retail PAKs (including split archives). Assets are not claimed as executable shaders until their graph contracts close.",
            prepared.verified_files,prepared.bytes_extracted
        ));
    }
    }
    let source_day=original_timeofday(&original_asset_root)?
        .map(|time|time.phases[1]);
    let mut source_ambient_rgb=[1.;3];
    let mut source_ambient_strength=0.;
    if let Some(day)=source_day {
        source_ambient_rgb.copy_from_slice(&day.skylight_linear_rgba[..3]);
        // The generic renderer uses normalized environment intensity;
        // the original FLinearColor alpha is not presumed to be the
        // Unreal SkyLightComponent intensity scale.
        source_ambient_strength=1.;
        scene.report.lines.push(format!(
            "Original BR daytime phase recovered from source TODM_BR (07:00-19:00):              skylight linear RGB={:?}, author alpha={}, directional brightness={}              (sun direction not yet reconstructed), source fog RGB={:?},              fog density={}, fog falloff={}. Universal ambient color uses              source RGB with neutral unit strength, NOT complete retail              sun/shadow/sky/fog parity.",
            source_ambient_rgb,day.skylight_linear_rgba[3],
            day.directional_light_brightness,
            &day.fog_color_linear_rgba[..3],day.fog_density,day.fog_height_falloff
        ));
    }else{
        scene.report.lines.push(
            "Fortnite BR TODM source is unavailable from cache and nearby split s4 archive; no inferred sky, fog or sunlight admitted.".into()
        );
    }
    // Release cached source bytes as soon as the runtime scene owns the
    // decoded engine-space geometry; later maps do not retain Fortnite RAM.
    *terrain_cache().lock().map_err(|_|"Athena terrain cache lock poisoned")?=None;
    for line in &scene.report.lines{println!("Fortnite 5.41: {line}");}
    let environment=neutral_bridge::environment_from_neutral(
        map_id,scene,
        &neutral_bridge::BridgeOptions{
            label:"Fortnite 5.41 (source terrain diagnostic)",
            id_prefix:"fortnite_541_athena",ambient_color:source_ambient_rgb,
            ambient_strength:source_ambient_strength,
            ibl_diffuse_strength:0.,ibl_specular_strength:0.,
            studio_shading_strength:0.,
            // A zero shadow distance is INVALID for the shared native Vulkan
            // render-settings contract, even if this source preview has no
            // recovered original sun, local lights or authored shadow data.
            // Use the native-safe positive distance; absence of light sources
            // remains explicit, and no invented sunlight/shadows are added.
            shadow_distance:120.,
        },
        started,
    );
    Ok(LoadedMapVisuals{environment:Some(Arc::new(environment)),skinned_assets:Vec::new()})
}
#[cfg(test)]
mod tests{
    use super::*;
    #[test] fn only_explicit_preview_id_is_generated(){
        assert!(can_generate(MAP_ID));
        assert!(!can_generate("fortnite_541_athena"));
    }
    #[test] fn raw_height_diagnostics_are_bounded(){
        assert_eq!(diagnostic_value(10,10,100),64);
        assert_eq!(diagnostic_value(100,10,100),255);
    }
    #[test] fn coordinates_convert_source_up_to_engine_up(){
        assert_eq!(engine_point([2.,3.,4.]),[2.,4.,-3.]);
    }
    #[test] fn source_landscape_normals_use_authored_xy_and_z_scale(){
        let patch=fortnite_541_importer::terrain::LocalTerrainPatch{
            section_base:[0,0],component_size_quads:1,
            vertices_source_xyz:vec![[0.,0.,0.],[1.,0.,1.],[0.,1.,0.],[1.,1.,1.]],
            height_samples:vec![32768;4],indices:vec![0,2,1,1,2,3],
        };
        let t=fortnite_541_importer::landscape::LandscapeWorldTransform{
            grid_origin_cm:[0.;3],local_scale_cm:[200.7874,200.7874,50.],
        };
        let n=source_patch_normal(&patch,&t,0,0);
        // Physical slope is 50/200.7874, NOT the old 100/100 = 1.
        assert!((n[0]/n[1]+50./200.7874).abs()<0.0001);
        assert!(n[1]>0.9 && n[2].abs()<0.001);
    }
}
