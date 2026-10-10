#![cfg(native_vulkan)]

use std::{env, fs, path::{Path, PathBuf}};

use serde::Deserialize;

pub(crate) const NATIVE_RENDER_SETTINGS_NAME: &str = "rendering.rfrender.json";

#[derive(Clone, Copy, Debug, Deserialize)]
pub(crate) struct NativeRenderSettings {
    #[serde(default = "default_version")]
    version: u32,
    #[serde(default)]
    pub exposure_ev: f32,
    #[serde(default = "default_fog_color")]
    pub fog_color: [f32; 3],
    #[serde(default)]
    pub fog_density: f32,
    #[serde(default)]
    pub fog_base_height: f32,
    #[serde(default = "default_fog_height_falloff")]
    pub fog_height_falloff: f32,
    #[serde(default = "default_ibl_color")]
    pub ibl_color: [f32; 3],
    #[serde(default = "default_ibl_diffuse_strength")]
    pub ibl_diffuse_strength: f32,
    #[serde(default = "default_ibl_specular_strength")]
    pub ibl_specular_strength: f32,
    #[serde(default = "default_shadow_distance")]
    pub shadow_distance: f32,
    #[serde(default = "default_shadow_bias")]
    pub shadow_bias: f32,
    #[serde(default = "default_shadow_normal_bias")]
    pub shadow_normal_bias: f32,
    #[serde(default = "default_shadow_map_size")]
    pub shadow_map_size: u32,
}

impl Default for NativeRenderSettings {
    fn default() -> Self {
        Self {
            version: default_version(),
            exposure_ev: 0.0,
            fog_color: default_fog_color(),
            fog_density: 0.0,
            fog_base_height: 0.0,
            fog_height_falloff: default_fog_height_falloff(),
            ibl_color: default_ibl_color(),
            ibl_diffuse_strength: default_ibl_diffuse_strength(),
            ibl_specular_strength: default_ibl_specular_strength(),
            shadow_distance: default_shadow_distance(),
            shadow_bias: default_shadow_bias(),
            shadow_normal_bias: default_shadow_normal_bias(),
            shadow_map_size: default_shadow_map_size(),
        }
    }
}

impl NativeRenderSettings {
    /// Authored settings file, else defaults adjusted by importer hints.
    pub(crate) fn load_or_hinted(
        map_id: &str,
        hints: Option<crate::mesh_render_data::environment::EnvironmentRenderHints>,
    ) -> Result<Self, String> {
        if resolve_map_asset(map_id, NATIVE_RENDER_SETTINGS_NAME).is_some() {
            return Self::load_or_default(map_id);
        }
        let mut settings = Self::default();
        if let Some(hints) = hints {
            settings.exposure_ev = hints.exposure_ev;
            settings.ibl_diffuse_strength = hints.ibl_diffuse_strength;
            settings.ibl_specular_strength = hints.ibl_specular_strength;
            settings.shadow_distance = hints.shadow_distance;
            settings.fog_color = hints.fog_color;
            settings.fog_density = hints.fog_density;
            settings.fog_base_height = hints.fog_base_height;
            settings.fog_height_falloff = hints.fog_height_falloff;
            settings.validate(map_id)?;
        }
        Ok(settings)
    }

    pub(crate) fn load_or_default(map_id: &str) -> Result<Self, String> {
        let Some(path) = resolve_map_asset(map_id, NATIVE_RENDER_SETTINGS_NAME) else {
            return Ok(Self::default());
        };
        let json = fs::read_to_string(&path)
            .map_err(|error| format!("failed to read {}: {error}", path.display()))?;
        let settings: Self = serde_json::from_str(&json)
            .map_err(|error| format!("failed to parse {}: {error}", path.display()))?;
        settings.validate(map_id)?;
        println!(
            "Native render settings ready for {} from {}",
            map_id,
            path.display()
        );
        Ok(settings)
    }

    #[inline]
    pub(crate) fn exposure_multiplier(self) -> f32 {
        2.0_f32.powf(self.exposure_ev)
    }

    fn validate(self, map_id: &str) -> Result<(), String> {
        if self.version != 1 {
            return Err(format!(
                "native render settings for '{map_id}' use unsupported version {} (expected 1)",
                self.version
            ));
        }
        if [
            self.exposure_ev,
            self.fog_density,
            self.fog_base_height,
            self.fog_height_falloff,
            self.ibl_diffuse_strength,
            self.ibl_specular_strength,
            self.shadow_distance,
            self.shadow_bias,
            self.shadow_normal_bias,
        ]
        .iter()
        .any(|value| !value.is_finite())
            || self.fog_color.iter().chain(self.ibl_color.iter()).any(|value| !value.is_finite())
        {
            return Err(format!("native render settings for '{map_id}' contain non-finite values"));
        }
        if self.shadow_distance <= 0.0 {
            return Err(format!(
                "native render settings for '{map_id}' require shadow_distance > 0 (received {})",
                self.shadow_distance
            ));
        }
        if self.fog_color.iter().chain(self.ibl_color.iter()).any(|value| *value < 0.0)
            || self.fog_density < 0.0
            || self.fog_height_falloff < 0.0
            || self.ibl_diffuse_strength < 0.0
            || self.ibl_specular_strength < 0.0
            || self.shadow_distance <= 0.0
            || self.shadow_bias < 0.0
            || self.shadow_normal_bias < 0.0
            || !(512..=8192).contains(&self.shadow_map_size)
            || !self.shadow_map_size.is_power_of_two()
        {
            return Err(format!("native render settings for '{map_id}' contain out-of-range values"));
        }
        Ok(())
    }
}

const fn default_version() -> u32 { 1 }
const fn default_fog_color() -> [f32; 3] { [0.58, 0.67, 0.78] }
const fn default_fog_height_falloff() -> f32 { 0.035 }
const fn default_ibl_color() -> [f32; 3] { [1.0, 1.0, 1.0] }
const fn default_ibl_diffuse_strength() -> f32 { 0.06 }
const fn default_ibl_specular_strength() -> f32 { 0.10 }
const fn default_shadow_distance() -> f32 { 120.0 }
const fn default_shadow_bias() -> f32 { 0.0015 }
const fn default_shadow_normal_bias() -> f32 { 0.02 }
const fn default_shadow_map_size() -> u32 { 2048 }

fn resolve_map_asset(map_id: &str, name: &str) -> Option<PathBuf> {
    let relative = Path::new("maps").join(map_id).join(name);
    let mut candidates = Vec::new();
    if let Ok(root) = env::var("RUST_TEST_ASSET_ROOT") {
        candidates.push(Path::new(&root).join(&relative));
    }
    if let Ok(current) = env::current_dir() {
        candidates.push(current.join("assets").join(&relative));
    }
    if let Ok(executable) = env::current_exe() {
        if let Some(directory) = executable.parent() {
            candidates.push(directory.join("assets").join(&relative));
        }
    }
    candidates.push(Path::new(env!("CARGO_MANIFEST_DIR")).join("assets").join(&relative));
    candidates.into_iter().find(|candidate| candidate.is_file())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn defaults_are_safe_and_shadow_ready() {
        let settings = NativeRenderSettings::default();
        assert_eq!(settings.version, 1);
        assert_eq!(settings.fog_density, 0.0);
        assert!(settings.exposure_multiplier().is_finite());
        assert!(settings.shadow_map_size.is_power_of_two());
        assert!(settings.shadow_map_size >= 512);
    }

    #[test]
    fn missing_sun_does_not_allow_zero_shadow_distance_hint() {
        let map_id = "fortnite_541_athena_terrain_preview";
        let invalid = NativeRenderSettings {
            shadow_distance: 0.0,
            ..NativeRenderSettings::default()
        };
        let error = invalid.validate(map_id).unwrap_err();
        assert!(error.contains("shadow_distance > 0"), "{error}");

        // The scene may have no recovered source sun/shadow records, but the
        // shared Vulkan settings contract still requires a positive range.
        // 120 metres is the regular engine default, not a new light source.
        let valid = NativeRenderSettings {
            shadow_distance: 120.0,
            ..NativeRenderSettings::default()
        };
        assert!(valid.validate(map_id).is_ok());
    }
}
