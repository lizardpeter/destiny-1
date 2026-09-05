#!/usr/bin/env python3
"""Instruction-proven D1 PS4 pixel-shader texture/register semantics.

This module is intentionally tiny and dependency-free so exact extraction,
semantic inventory and portable adapters can share one canonical role table.
Every entry below must be backed by native GCN dataflow, not texture appearance
or a generic `t0 == albedo` assumption.

Role strings describe what the sampled channel(s) do in the native shader. They
are not promises that a one-to-one glTF PBR slot exists.
"""
from __future__ import annotations

PROVEN_PIXEL_SHADER_ROLES: dict[str, dict[int, str]] = {
    # Vex main surface / deferred material.
    '80AAE14B': {
        0: 'surface_rgb',
        1: 'primary_normal_rg',
        2: 'detail_normal_rg',
        3: 'environment_cubemap',
        4: 'surface_alpha_reflection_control',
    },

    # Vex circuitry/parallax palette pass.
    '816CE0A8': {
        0: 'height_pre_displacement',
        1: 'displaced_image',
    },

    # Common Tower deferred surfaces: t1.xy reconstructs +Z normal; t0.a
    # changes deferred-normal packing magnitude while t0.rgb reaches MRT0.
    '809DF9A4': {
        0: 'surface_rgb_alpha_deferred_normal_control',
        1: 'primary_normal_rg',
    },
    '80AADCB3': {
        0: 'surface_rgb_alpha_deferred_normal_control',
        1: 'primary_normal_rg',
    },

    # Tower colored surfaces: t1 is sampled only as Y and controls deferred
    # normal-vector packing. It is not a second color texture or normal map.
    '8093EB1E': {
        0: 'surface_rgb',
        1: 'deferred_normal_magnitude_control_y',
    },
    '80AAE1C6': {
        0: 'surface_rgb',
        1: 'deferred_normal_magnitude_control_y',
    },

    # Simple one-texture Tower surface.
    '80AADC40': {
        0: 'surface_rgb',
    },

    # Tower reflective surface family. Native cube-coordinate instructions and
    # image_get_lod/image_sample_l prove t1 as the environment cube. t2.y sets
    # the minimum cube LOD/reflection amount and deferred-normal pack magnitude.
    '80CA0DD5': {
        0: 'surface_rgb',
        1: 'environment_cubemap',
        2: 'reflection_lod_intensity_and_deferred_normal_control_y',
    },

    # Reflective sibling. t2 is sampled XZ and applies exactly
    # adjusted_rgb = t0.rgb * t2.z + t2.x before reflection contribution.
    # t3.y has the same reflection/deferred-normal control role as above.
    '80AAE2AD': {
        0: 'surface_rgb',
        1: 'environment_cubemap',
        2: 'surface_rgb_bias_x_scale_z',
        3: 'reflection_lod_intensity_and_deferred_normal_control_y',
    },

    # Reflective normal-mapped Tower family. t0.a drives both cubemap
    # LOD/intensity and deferred-normal packing; t1.xy reconstructs the normal.
    '80AADCA6': {
        0: 'surface_rgb_alpha_reflection_and_deferred_normal_control',
        1: 'primary_normal_rg',
        2: 'environment_cubemap',
    },

    # Normal-mapped color/mask family. t2.x interpolates the surface RGB toward
    # a material-authored color branch; t0.a controls deferred-normal packing.
    '8093EB1C': {
        0: 'surface_rgb_alpha_deferred_normal_control',
        1: 'primary_normal_rg',
        2: 'surface_rgb_mix_control_x',
    },

    # Alpha-only cutout/depth-style pass. Surviving pixels output constant 1.
    '80AAE1AC': {
        0: 'alpha_test_mask_a',
    },

    # Alpha sampled after authored UV transform; it scales material-authored RGB.
    '80CA08C4': {
        0: 'material_rgb_intensity_mask_a',
    },

    # Scalar/palette material. t0.r chooses a material palette at base UV; t1.r
    # is sampled at a view-dependent displaced UV and modulates the resulting RGB.
    # Neither texture is a direct RGB base-color image.
    '809DCD66': {
        0: 'base_uv_palette_scalar_r',
        1: 'parallax_displaced_rgb_modulation_scalar_r',
    },

    # Tower common-layer emissive/color pass. The sampled t0.xyz components are
    # independently multiplied by authored constants and reach MRT0 directly.
    # There is no alpha/mask-only reinterpretation in this shader.
    '8093E96F': {
        0: 'surface_rgb',
    },

    # Common-layer authored-color mask siblings. All three emit RGB assembled
    # from material constants; the sampled texture contributes only one scalar
    # control channel, so binding the whole texture as glTF base color is wrong.
    '80CA08B1': {
        0: 'material_rgb_intensity_mask_r',
    },
    '80CA08C1': {
        0: 'material_rgb_intensity_mask_a',
    },
    '80CA08C3': {
        0: 'material_rgb_intensity_mask_a',
    },

    # Common reflective/normal-mapped family. t2.xy is transformed into a
    # tangent-space normal and reconstructs +Z. Cube-coordinate instructions,
    # image_get_lod and image_sample_l prove t1 as the environment cube. t0.r is
    # folded into the chosen cube LOD rather than used as surface RGB. The shader
    # also samples a runtime resource-table t11 which is not a material t# binding.
    '80CA08B0': {
        0: 'reflection_lod_control_r',
        1: 'environment_cubemap',
        2: 'primary_normal_rg',
    },

    # Common-layer RGBA surface. t0.rgb reaches MRT0 after authored scaling;
    # t0.a participates in the common intensity multiplier applied to the RGB.
    '80CA0BFA': {
        0: 'surface_rgb_alpha_intensity_control',
    },
}

# Roles that have a safe direct *portable preview* interpretation. This is kept
# separate from the richer native semantics above.
PORTABLE_BASE_COLOR_ROLES = {
    'surface_rgb',
    'surface_rgb_alpha_deferred_normal_control',
    'surface_rgb_alpha_reflection_and_deferred_normal_control',
    'surface_rgb_alpha_intensity_control',
}

PORTABLE_NORMAL_ROLES = {
    'primary_normal_rg',
}
