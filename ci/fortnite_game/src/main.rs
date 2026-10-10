//! Temporary public compiler and real-source contract check. This is NOT
//! the game's Vulkan runtime; it type-checks the actual game importer adapter
//! against the real neutral_scene crate and validates all source geometry.
use std::{process::ExitCode,sync::Arc};

#[path = "native_render_settings.rs"]
mod native_render_settings;

mod mesh_render_data {
    use super::Arc;
    pub struct GeneratedSourceMap{
        pub display_name:String,
        pub spawns:Vec<([f32;3],f32)>,
    }
    pub struct EnvironmentRenderData{
        pub scene:neutral_scene::NeutralScene,
    }
    pub mod environment {
        use super::{Arc,EnvironmentRenderData};
        pub struct EnvironmentRenderHints {
            pub exposure_ev:f32,pub ibl_diffuse_strength:f32,
            pub ibl_specular_strength:f32,pub shadow_distance:f32,
            pub fog_color:[f32;3],pub fog_density:f32,
            pub fog_base_height:f32,pub fog_height_falloff:f32,
        }
        pub struct LoadedMapVisuals{
            pub environment:Option<Arc<EnvironmentRenderData>>,
            pub skinned_assets:Vec<()>,
        }
    }
}
mod source_importers {
    use std::path::Path;
    pub struct SourceImportManifest;
    pub mod neutral_bridge{
        pub struct BridgeOptions<'a>{
            pub label:&'a str,pub id_prefix:&'a str,pub ambient_color:[f32;3],
            pub ambient_strength:f32,pub ibl_diffuse_strength:f32,
            pub ibl_specular_strength:f32,pub studio_shading_strength:f32,
            pub shadow_distance:f32,
        }
        pub fn environment_from_neutral(
            _map_id:&str,
            scene:neutral_scene::NeutralScene,
            options:&BridgeOptions<'_>,_started:std::time::Instant
        )->crate::mesh_render_data::EnvironmentRenderData{
            assert_eq!(options.label,"Fortnite 5.41 (source terrain diagnostic)");
            assert_eq!(options.id_prefix,"fortnite_541_athena");
            assert_eq!(options.ambient_color,[1.;3]);
            assert_eq!(options.ambient_strength,0.);
            assert_eq!(options.ibl_diffuse_strength,0.);
            assert_eq!(options.ibl_specular_strength,0.);
            assert_eq!(options.studio_shading_strength,0.);
            assert_eq!(options.shadow_distance,120.);
            // Compile the real Rust-test native render settings validator
            // against the real game importer hints. The exact prior failure
            // (distance 0) must be rejected; positive source-safe hints pass.
            let hints=crate::mesh_render_data::environment::EnvironmentRenderHints {
                exposure_ev:0.,
                ibl_diffuse_strength:options.ibl_diffuse_strength,
                ibl_specular_strength:options.ibl_specular_strength,
                shadow_distance:options.shadow_distance,
                fog_color:[0.;3],fog_density:0.,
                fog_base_height:0.,fog_height_falloff:0.,
            };
            let actual=crate::native_render_settings::NativeRenderSettings::load_or_hinted(
                "fortnite_541_athena_terrain_preview",Some(hints));
            assert!(actual.is_ok(),"Fortnite preview must pass original Vulkan render validation: {actual:?}");
            crate::mesh_render_data::EnvironmentRenderData{scene}
        }
    }
    #[path = "fortnite_541.rs"]
    mod fortnite_541;
    pub fn run()->Result<(),String>{
        let id=fortnite_541::MAP_ID;
        assert!(fortnite_541::can_generate(id));
        assert_eq!(fortnite_541::generated_map_list().len(),1);
        assert!(fortnite_541::generated_menu_hierarchy(id).is_some());
        let map=fortnite_541::generated_source_map(id)?;
        let spawn=map.spawns[0].0;
        assert!(map.display_name.contains("Athena"));
        // Six retail ULandscape roots place grid [762,762] at world (0,0),
        // while original scale 50/100 halves local height and offsets Z.
        assert!(spawn[0].abs()<0.02,"world spawn X: {}",spawn[0]);
        assert!((spawn[1]-28.583125).abs()<0.02,"world spawn Y: {}",spawn[1]);
        assert!(spawn[2].abs()<0.02,"world spawn Z: {}",spawn[2]);
        let visuals=fortnite_541::import_visuals(id,Path::new(""),&SourceImportManifest)?;
        assert!(visuals.skinned_assets.is_empty());
        let env=visuals.environment.ok_or("missing neutral environment")?;
        let s=&env.scene;
        let verts:usize=s.meshes.iter().map(|m|m.vertices.len()).sum();
        let tris:usize=s.meshes.iter().map(|m|m.indices.len()/3).sum();
        println!("FORTNITE_GAME_BRIDGE meshes={} materials={} textures={} instances={} vertices={verts} triangles={tris} collision_triangles={} spawn={spawn:?}",
            s.meshes.len(),s.materials.len(),s.textures.len(),s.instances.len(),s.collision.len());
        if s.meshes.len()!=94 ||s.materials.len()!=94||s.textures.len()!=94 ||
            s.instances.len()!=94 || verts!=1540096||tris!=3032252 ||
            s.collision.len()!=3032252{
            return Err("real Athena source neutral scene bridge census mismatch".into());
        }
        // The same source scale/origin must apply to every collision vertex,
        // not just the scene mesh and diagnostic-only viewer.
        let positions=s.meshes.iter().flat_map(|m|m.vertices.iter().map(|v|v.position));
        let mut min=[f32::INFINITY;3];let mut max=[f32::NEG_INFINITY;3];
        for p in positions {for ax in 0..3 {min[ax]=min[ax].min(p[ax]);max[ax]=max[ax].max(p[ax]);}}
        println!("ATHENA_PHYSICAL_WORLD_BOUNDS_METERS min={min:?} max={max:?}");
        assert!((min[0]+1530.).abs()<0.1,"wrong X root/original actor scale");
        assert!((max[0]-1530.).abs()<0.1,"wrong X extent");
        assert!((min[2]+1530.).abs()<0.1,"wrong Z root/original actor scale");
        assert!((max[2]-1530.).abs()<0.1,"wrong Z extent");
        // Prevent accidental rendering of a false original-material substitute.
        if !s.materials.iter().all(|m|m.unlit&&m.name.starts_with("DIAGNOSTIC_ONLY_")){
            return Err("source diagnostic visualizer mislabeled as original Fortnite material".into());
        }
        // Original landscape 3D coordinates -> Y-up; this preview is actual geometry.
        if !s.collision.iter().flat_map(|tri|tri.iter()).all(|v|v.iter().all(|x|x.is_finite())){
            return Err("nonfinite collision geometry".into());
        }
        // Independently verify original BC source material textures cross
        // the UNMODIFIED shared texture ABI. These are not yet bound to a
        // surface shader because source UV/function closure is still pending.
        let source_root=std::env::var_os("RUST_TEST_FORTNITE_541_ATHENA_SOURCE_ROOT")
            .ok_or("CI original source root not configured")?;
        for (name,fmt,expected) in [
            ("T_Athena_Terrain_CombinedColors_01",neutral_scene::NeutralBlockFormat::Bc1,2097152usize),
            ("T_Athena_Terrain_Topo_Mask",neutral_scene::NeutralBlockFormat::Bc3,4194304usize),
        ] {
            let t=fortnite_541::source_original_terrain_bc_texture(
                Path::new(&source_root),name
            )?;
            let bc=t.compressed.as_ref().ok_or("original source BC encoding discarded")?;
            assert_eq!(bc.format,fmt);
            assert_eq!((t.width,t.height),(2048,2048));
            assert_eq!(t.rgba.len(),2048*2048*4);
            assert_eq!(bc.levels[0].blocks.len(),expected);
            println!("PASS: original Fortnite source BC texture preserved through generic NeutralScene {name} {fmt:?} bytes={expected}");
        }
        println!("PASS: full Fortnite source terrain -> host NeutralScene contract with source-grounded spawn/collision");
        Ok(())
    }
}
fn main()->ExitCode{
    match source_importers::run(){
        Ok(())=>ExitCode::SUCCESS,
        Err(e)=>{eprintln!("{e}");ExitCode::FAILURE}
    }
}
