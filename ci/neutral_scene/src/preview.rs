//! CPU reference renderer for a `NeutralScene`, mirroring the engine's
//! generic environment shading closely enough to check an importer's output
//! without a GPU.

use std::env;

use crate::{NeutralAlpha, NeutralScene, NeutralVertex, LIGHTMAP_RGBM_RANGE};

pub const W: usize = 960;
pub const H: usize = 540;

/// Render a view to packed RGB8 (W x H). `eye` in engine space, yaw/pitch in radians.
pub fn xf(rows: &[[f32; 4]; 3], p: [f32; 3], w: f32) -> [f32; 3] {
    [
        rows[0][0] * p[0] + rows[0][1] * p[1] + rows[0][2] * p[2] + rows[0][3] * w,
        rows[1][0] * p[0] + rows[1][1] * p[1] + rows[1][2] * p[2] + rows[1][3] * w,
        rows[2][0] * p[0] + rows[2][1] * p[1] + rows[2][2] * p[2] + rows[2][3] * w,
    ]
}

pub fn srgb_to_linear(c: f32) -> f32 {
    if c <= 0.04045 { c / 12.92 } else { ((c + 0.055) / 1.055).powf(2.4) }
}
pub fn linear_to_srgb(c: f32) -> f32 {
    let c = c.clamp(0.0, 1.0);
    if c <= 0.003_130_8 { c * 12.92 } else { 1.055 * c.powf(1.0 / 2.4) - 0.055 }
}
/// Engine fog: exact height-fog optical depth (negative distance = sky),
/// sun-fog colour/opacity cone, amount scaled by max opacity.
pub fn apply_fog(fog: &crate::NeutralFog, eye: [f32; 3], dir: [f32; 3], distance: f32, c: [f32; 3]) -> [f32; 3] {
    let at_camera = fog.density * (-(eye[1] - fog.base_height) * fog.height_falloff).clamp(-30.0, 30.0).exp();
    let a = fog.height_falloff * dir[1];
    let depth = if distance < 0.0 {
        if a <= 1e-6 { 1e9 } else { at_camera / a }
    } else if (a * distance).abs() < 1e-4 {
        at_camera * distance
    } else {
        at_camera * (1.0 - (-a * distance).exp()) / a
    };
    let (mut color, mut opacity) = (fog.color, fog.max_opacity);
    if let Some(sun) = fog.sun {
        let (co, ci) = (sun.outer_angle.to_radians().cos(), sun.inner_angle.min(sun.outer_angle).to_radians().cos());
        let t = ((dot(dir, sun.direction) - co) / (ci - co).max(1e-4)).clamp(0.0, 1.0);
        color = [0, 1, 2].map(|k| color[k] + (sun.color[k] - color[k]) * t);
        opacity += (sun.max_opacity - opacity) * t;
    }
    let amount = (1.0 - (-depth).exp()).clamp(0.0, 1.0) * opacity;
    [0, 1, 2].map(|k| c[k] + (color[k] - c[k]) * amount)
}

/// Scene radiance -> display value, as the engine's graded display transform.
pub fn display_grade(grade: &crate::NeutralDisplayGrade, c: [f32; 3]) -> [f32; 3] {
    let knee = grade.shoulder_knee;
    let slope = 1.0 / ((1.0 - knee) * std::f32::consts::LN_2);
    let e = c.map(|v| {
        let e = (v.max(0.0) * grade.exposure).powf(grade.encode_gamma);
        if e > knee { knee + (1.0 - knee) * (1.0 - (-(e - knee) * slope).exp2()) } else { e }
    });
    let Some(lut) = &grade.lut else { return e };
    // Trilinear 32^3 lookup at texel centres.
    let f = e.map(|v| v.clamp(0.0, 1.0) * 31.0);
    let i0 = f.map(|v| (v.floor() as usize).min(30));
    let t = [0, 1, 2].map(|k| f[k] - i0[k] as f32);
    let at = |r: usize, g: usize, b: usize, k: usize| lut[((b * 32 + g) * 32 + r) * 4 + k] as f32 / 255.0;
    [0, 1, 2].map(|k| {
        let mut acc = 0.0;
        for (db, wb) in [(0, 1.0 - t[2]), (1, t[2])] {
            for (dg, wg) in [(0, 1.0 - t[1]), (1, t[1])] {
                for (dr, wr) in [(0, 1.0 - t[0]), (1, t[0])] {
                    acc += wb * wg * wr * at(i0[0] + dr, i0[1] + dg, i0[2] + db, k);
                }
            }
        }
        acc
    })
}

pub fn aces(x: f32) -> f32 {
    ((x * (2.51 * x + 0.03)) / (x * (2.43 * x + 0.59) + 0.14)).clamp(0.0, 1.0)
}

pub fn sh9(sh: &[[f32; 3]; 9], n: [f32; 3]) -> [f32; 3] {
    let [x, y, z] = n;
    let b = [
        0.282_095,
        0.488_603 * y,
        0.488_603 * z,
        0.488_603 * x,
        1.092_548 * x * y,
        1.092_548 * y * z,
        0.315_392 * (3.0 * z * z - 1.0),
        1.092_548 * x * z,
        0.546_274 * (x * x - y * y),
    ];
    let mut out = [0.0; 3];
    for (c, b) in sh.iter().zip(b) {
        for k in 0..3 {
            out[k] += c[k] * b;
        }
    }
    out.map(|v| v.max(0.0))
}

pub fn sample(rgba: &[u8], w: u32, h: u32, u: f32, v: f32) -> [f32; 4] {
    let tx = ((u.rem_euclid(1.0)) * w as f32) as usize % w as usize;
    let ty = ((v.rem_euclid(1.0)) * h as f32) as usize % h as usize;
    let s = &rgba[(ty * w as usize + tx) * 4..][..4];
    [s[0] as f32 / 255.0, s[1] as f32 / 255.0, s[2] as f32 / 255.0, s[3] as f32 / 255.0]
}

pub fn rgbm(p: [f32; 4]) -> [f32; 3] {
    [p[0] * p[3] * LIGHTMAP_RGBM_RANGE, p[1] * p[3] * LIGHTMAP_RGBM_RANGE, p[2] * p[3] * LIGHTMAP_RGBM_RANGE]
}

pub fn render(scene: &NeutralScene, eye: [f32; 3], yaw: f32, pitch: f32, baked: bool) -> Vec<u8> {
    let forward = [-yaw.sin() * pitch.cos(), pitch.sin(), -yaw.cos() * pitch.cos()];
    let right = normalize(cross(forward, [0.0, 1.0, 0.0]));
    let up = cross(right, forward);
    let focal = (H as f32 * 0.5) / (35f32.to_radians()).tan();
    let sun = scene.sun;
    let exposure: f32 = env::var("EXPOSURE").ok().and_then(|v| v.parse().ok()).unwrap_or(1.0);
    // Engine direct diffuse is albedo / pi * radiance * n.l (no shadows here).
    let sun_k: f32 = env::var("SUN_K").ok().and_then(|v| v.parse().ok()).unwrap_or(1.0 / std::f32::consts::PI);
    let square = env::var("LM_SQUARE").is_ok();
    let engine_mode = env::var("ENGINE").is_ok();
    let green_sign: f32 = if env::var("FLIP_GREEN").is_ok() { -1.0 } else { 1.0 };

    // Background: sky cubemap (engine faces) or flat colour. Stored linear.
    let mut color = vec![[0.0f32; 3]; W * H];
    for py in 0..H {
        for px in 0..W {
            let dx = (px as f32 + 0.5 - W as f32 * 0.5) / focal;
            let dy = -(py as f32 + 0.5 - H as f32 * 0.5) / focal;
            let d = normalize([
                forward[0] + right[0] * dx + up[0] * dy,
                forward[1] + right[1] * dx + up[1] * dy,
                forward[2] + right[2] * dx + up[2] * dy,
            ]);
            color[py * W + px] = match &scene.sky {
                Some(sky) => {
                    let (f, u, v) = cube_lookup(d);
                    let t = &sky.faces[f];
                    let s = sample(&t.rgba, t.width, t.height, u, v);
                    let c = [srgb_to_linear(s[0]), srgb_to_linear(s[1]), srgb_to_linear(s[2])].map(|c| c * sky.intensity);
                    match &scene.fog {
                        Some(fog) => apply_fog(fog, eye, d, -1.0, c),
                        None => c,
                    }
                }
                None => [0.3, 0.4, 0.6],
            };
        }
    }
    let mut depth = vec![f32::MAX; W * H];
    // Debug: PICK=x,y reports the instance drawn at that pixel.
    let pick: Option<usize> = env::var("PICK").ok().and_then(|v| {
        let p: Vec<usize> = v.split(',').filter_map(|x| x.parse().ok()).collect();
        (p.len() == 2).then(|| p[1] * W + p[0])
    });
    let mut picked: Option<usize> = None;

    let mut passes: Vec<usize> = (0..scene.instances.len())
        .filter(|&i| scene.materials[scene.meshes[scene.instances[i].mesh].material].visible)
        .collect();
    passes.sort_by_key(|&i| {
        !matches!(scene.materials[scene.meshes[scene.instances[i].mesh].material].alpha, NeutralAlpha::Opaque | NeutralAlpha::Mask(_))
    });

    for instance_index in passes {
        let instance = &scene.instances[instance_index];
        let mesh = &scene.meshes[instance.mesh];
        let material = &scene.materials[mesh.material];
        let texture = material.base_color_texture.map(|t| &scene.textures[t]);
        let lightmap = mesh.lightmap.map(|l| &scene.lightmaps[l]);
        // World-space vertices; normals are transformed here so clipping can lerp them.
        let world: Vec<NeutralVertex> = mesh
            .vertices
            .iter()
            .enumerate()
            .map(|(vi, v)| {
                let mut w = *v;
                // Preview-only: carry per-vertex baked light in the layer UV slots.
                if let Some(light) = &mesh.vertex_light {
                    let l = light[vi];
                    w.layer_uvs = [[l[0], l[1]], [l[2], l[3]]];
                }
                w.position = xf(&instance.rows, v.position, 1.0);
                w.normal = xf(&instance.rows, v.normal, 0.0);
                let t = xf(&instance.rows, [v.tangent[0], v.tangent[1], v.tangent[2]], 0.0);
                w.tangent = [t[0], t[1], t[2], v.tangent[3]];
                w
            })
            .collect();
        let project = |v: &NeutralVertex| {
            let d = sub(v.position, eye);
            let z = dot(d, forward);
            (W as f32 * 0.5 + dot(d, right) * focal / z, H as f32 * 0.5 - dot(d, up) * focal / z, z)
        };
        const NEAR: f32 = 0.05;
        let mut clipped: Vec<[NeutralVertex; 3]> = Vec::new();
        for tri in mesh.indices.chunks_exact(3) {
            let corners = [world[tri[0] as usize], world[tri[1] as usize], world[tri[2] as usize]];
            let depth_of = |v: &NeutralVertex| dot(sub(v.position, eye), forward);
            clipped.clear();
            if corners.iter().all(|v| depth_of(v) >= NEAR) {
                clipped.push(corners);
            } else if corners.iter().any(|v| depth_of(v) >= NEAR) {
                // Sutherland-Hodgman against the near plane, then fan.
                let mut poly: Vec<NeutralVertex> = Vec::with_capacity(4);
                for i in 0..3 {
                    let (p0, p1) = (corners[i], corners[(i + 1) % 3]);
                    let (d0, d1) = (depth_of(&p0), depth_of(&p1));
                    if d0 >= NEAR {
                        poly.push(p0);
                    }
                    if (d0 >= NEAR) != (d1 >= NEAR) {
                        poly.push(lerp_vertex(&p0, &p1, (NEAR - d0) / (d1 - d0)));
                    }
                }
                for k in 1..poly.len().saturating_sub(1) {
                    clipped.push([poly[0], poly[k], poly[k + 1]]);
                }
            }
          for [va, vb, vc] in clipped.iter().map(|t| [&t[0], &t[1], &t[2]]) {
            let (a, b, c) = (project(va), project(vb), project(vc));
            let area = (b.0 - a.0) * (c.1 - a.1) - (b.1 - a.1) * (c.0 - a.0);
            if area.abs() < 1e-6 {
                continue;
            }
            let min_x = a.0.min(b.0).min(c.0).floor().max(0.0) as usize;
            let max_x = a.0.max(b.0).max(c.0).ceil().min(W as f32 - 1.0) as usize;
            let min_y = a.1.min(b.1).min(c.1).floor().max(0.0) as usize;
            let max_y = a.1.max(b.1).max(c.1).ceil().min(H as f32 - 1.0) as usize;
            if min_x > max_x || min_y > max_y {
                continue;
            }
            for py in min_y..=max_y {
                for px in min_x..=max_x {
                    let (fx, fy) = (px as f32 + 0.5, py as f32 + 0.5);
                    let w0 = ((b.0 - fx) * (c.1 - fy) - (b.1 - fy) * (c.0 - fx)) / area;
                    let w1 = ((c.0 - fx) * (a.1 - fy) - (c.1 - fy) * (a.0 - fx)) / area;
                    let w2 = 1.0 - w0 - w1;
                    if w0 < 0.0 || w1 < 0.0 || w2 < 0.0 {
                        continue;
                    }
                    let z = 1.0 / (w0 / a.2 + w1 / b.2 + w2 / c.2);
                    let slot = py * W + px;
                    if z >= depth[slot] {
                        continue;
                    }
                    let p = |fa: f32, fb: f32, fc: f32| (fa * w0 / a.2 + fb * w1 / b.2 + fc * w2 / c.2) * z;
                    let n = normalize([
                        p(va.normal[0], vb.normal[0], vc.normal[0]),
                        p(va.normal[1], vb.normal[1], vc.normal[1]),
                        p(va.normal[2], vb.normal[2], vc.normal[2]),
                    ]);
                    let vcol = [0, 1, 2, 3].map(|k| p(va.color[k], vb.color[k], vc.color[k]));
                    let (tu, tv) = (p(va.uv[0], vb.uv[0], vc.uv[0]), p(va.uv[1], vb.uv[1], vc.uv[1]));
                    // Surface program: evaluated per pixel (mip 0, no quad
                    // neighbours) and lit like any other surface.
                    if let (Some(binding), false) = (&material.program, env::var("NO_PROGRAMS").is_ok()) {
                        let program = &scene.programs[binding.program];
                        let front = area > 0.0;
                        let input = |i: crate::program::Input, c: u8| -> f32 {
                            use crate::program::Input;
                            let c = c as usize;
                            match i {
                                Input::WorldPosition => p(va.position[c.min(2)], vb.position[c.min(2)], vc.position[c.min(2)]),
                                Input::WorldNormal => p(va.normal[c.min(2)], vb.normal[c.min(2)], vc.normal[c.min(2)]),
                                Input::WorldTangent => p(va.tangent[c], vb.tangent[c], vc.tangent[c]),
                                Input::Uv => p(va.uv[c.min(1)], vb.uv[c.min(1)], vc.uv[c.min(1)]),
                                Input::VertexColor => p(va.color[c], vb.color[c], vc.color[c]),
                                Input::VertexData => p(va.data[c], vb.data[c], vc.data[c]),
                                Input::CameraPosition => eye[c.min(2)],
                                Input::Time => 0.0,
                                Input::ExposureMultiplier => exposure,
                                Input::PrimaryDirectionalLightDirectionToLight => match sun {
                                    Some(sun) if c < 3 => sun.direction_to_light[c],
                                    Some(_) if c == 3 => 1.0,
                                    _ => 0.0,
                                },
                                Input::PrimaryDirectionalShadow => 1.0,
                                Input::PrimaryDirectionalLightColorIntensity => match sun {
                                    Some(sun) if c < 3 => sun.color[c],
                                    Some(sun) if c == 3 => sun.intensity,
                                    _ => 0.0,
                                },
                                Input::ViewportSize => {
                                    let width = W as f32;
                                    let height = H as f32;
                                    [width, height, 1.0 / width, 1.0 / height][c]
                                }
                                Input::FragCoord => [fx, fy, z, 1.0][c],
                                Input::FrontFacing => f32::from(u8::from(front)),
                                // The CPU preview has no vertex stage; programs
                                // with one are shown through their fallback.
                                Input::SourceAttribute
                                | Input::SkinnedLocalPosition
                                | Input::SkinnedLocalNormal
                                | Input::SkinnedLocalTangent
                                | Input::SelectedJointSkinMatrix
                                | Input::ObjectToWorld
                                | Input::CameraRelativeViewProjection
                                | Input::WorldToViewRotation
                                | Input::InstanceData
                                | Input::Varying
                                | Input::SurfacePayload
                                | Input::LightAccumulation => 0.0,
                            }
                        };
                        let fetch = |slot: u8| -> Option<(&crate::NeutralTexture, crate::program::ProgramTextureSlot, usize)> {
                            let first = binding.textures.get(slot as usize).copied().flatten()?;
                            Some((&scene.textures[first], program.textures[slot as usize], first))
                        };
                        let linear = |s: [f32; 4], srgb: bool| if srgb { [srgb_to_linear(s[0]), srgb_to_linear(s[1]), srgb_to_linear(s[2]), s[3]] } else { s };
                        let sample_program = |slot: u8, _sampler: u8, coords: [f32; 3], _lod: Option<f32>| -> [f32; 4] {
                            let Some((t, kind, first)) = fetch(slot) else { return [0.0; 4] };
                            match kind.kind {
                                crate::program::ProgramTextureKind::D2 => linear(sample(&t.rgba, t.width, t.height, coords[0], coords[1]), kind.srgb),
                                crate::program::ProgramTextureKind::D3 => [0.0; 4],
                                crate::program::ProgramTextureKind::Cube => {
                                    let (face, u, v) = cube_lookup(coords);
                                    let f = &scene.textures[first + face];
                                    linear(sample(&f.rgba, f.width, f.height, u, v), kind.srgb)
                                }
                            }
                        };
                        let load_program = |slot: u8, xy: [i32; 2], _level: u32| -> [f32; 4] {
                            let Some((t, kind, _)) = fetch(slot) else { return [0.0; 4] };
                            let (x, y) = (xy[0].rem_euclid(t.width as i32) as usize, xy[1].rem_euclid(t.height as i32) as usize);
                            let o = (y * t.width as usize + x) * 4;
                            linear([0, 1, 2, 3].map(|k| t.rgba[o + k] as f32 / 255.0), kind.srgb)
                        };
                        let out = crate::program::evaluate(program, &input, &binding.constants, &sample_program, &load_program);
                        if out.discard {
                            continue;
                        }
                        let wp = [0, 1, 2].map(|k| p(va.position[k], vb.position[k], vc.position[k]));
                        let alpha = out.alpha.unwrap_or(1.0).clamp(0.0, 1.0);
                        // Source framebuffer/code output is not linear scene
                        // radiance. Unlike final_color, it must not pick up the
                        // preview exposure multiplier a second time.
                        let source_framebuffer_color = out
                            .source_framebuffer_color
                            .map(|c| c.map(|v| v.clamp(0.0, 1.0)));
                        let final_color = out
                            .final_color
                            .map(|c| c.map(|v| v.max(0.0) * exposure));
                        let source_color = source_framebuffer_color.or(final_color);
                        let mut lit = match program.blend {
                            _ if source_color.is_some() => source_color.unwrap(),
                            crate::program::ProgramBlend::Additive => out.emissive.unwrap_or([0.0; 3]).map(|c| c.max(0.0) * exposure),
                            _ => {
                                let mut geometric = n;
                                if !front {
                                    geometric = geometric.map(|c| -c);
                                }
                                let normal = out.world_normal.map(normalize).filter(|v| v.iter().all(|c| c.is_finite())).unwrap_or(geometric);
                                let albedo = out.base_color.unwrap_or([1.0; 3]).map(|c| c.clamp(0.0, 1.0));
                                let light = add_sun([0.18; 3], normal, sun, sun_k);
                                let emissive = out.emissive.unwrap_or([0.0; 3]);
                                [0, 1, 2].map(|k| (albedo[k] * light[k] + emissive[k].max(0.0)) * exposure)
                            }
                        };
                        // Source-composed colours arrive after the source
                        // material/fog presentation path and must not receive
                        // generic preview fog.
                        if let (Some(fog), false) = (&scene.fog, program.blend == crate::program::ProgramBlend::Additive || source_color.is_some()) {
                            let ray = sub(wp, eye);
                            let distance = dot(ray, ray).sqrt();
                            lit = apply_fog(fog, eye, normalize(ray), distance, lit);
                        }
                        let target = &mut color[slot];
                        if program.blend == crate::program::ProgramBlend::Additive {
                            for k in 0..3 {
                                target[k] += lit[k] * alpha;
                            }
                        } else {
                            depth[slot] = z;
                            *target = lit;
                            if pick == Some(slot) {
                                picked = Some(instance_index);
                            }
                        }
                        continue;
                    }
                    let mut base = match texture {
                        Some(t) => sample(&t.rgba, t.width, t.height, tu, tv),
                        None => [0.6, 0.6, 0.6, 1.0],
                    };
                    for (layer_index, layer) in material.layers.iter().enumerate() {
                        let Some(t) = layer.color_texture.map(|t| &scene.textures[t]) else { continue };
                        let (lu, lv) = (
                            p(va.layer_uvs[layer_index][0], vb.layer_uvs[layer_index][0], vc.layer_uvs[layer_index][0]),
                            p(va.layer_uvs[layer_index][1], vb.layer_uvs[layer_index][1], vc.layer_uvs[layer_index][1]),
                        );
                        let s2 = sample(&t.rgba, t.width, t.height, lu, lv);
                        let weight = p(va.layer_weights[layer_index], vb.layer_weights[layer_index], vc.layer_weights[layer_index]).clamp(0.0, 1.0);
                        use crate::NeutralLayerMode;
                        for k in 0..3 {
                            base[k] = match layer.mode {
                                NeutralLayerMode::Blend => base[k] + (s2[k] - base[k]) * (s2[3] * weight),
                                NeutralLayerMode::Multiply => base[k] * (1.0 + (s2[k] - 1.0) * weight),
                                NeutralLayerMode::Add => (base[k] + s2[k] * s2[3] * weight).min(1.0),
                            };
                        }
                    }
                    let alpha = base[3] * vcol[3];
                    if let NeutralAlpha::Mask(cut) = material.alpha {
                        if alpha < cut.max(0.02) {
                            continue;
                        }
                    }
                    // Engine-equivalent normal mapping (tangent frame as in native_environment.wgsl).
                    let geometric_n = n;
                    let n = match (engine_mode, material.normal_texture.map(|t| &scene.textures[t])) {
                        (true, Some(t)) => {
                            let s_n = sample(&t.rgba, t.width, t.height, tu, tv);
                            let tn = normalize([s_n[0] * 2.0 - 1.0, (s_n[1] * 2.0 - 1.0) * green_sign, s_n[2] * 2.0 - 1.0]);
                            let tw = p(va.tangent[3], vb.tangent[3], vc.tangent[3]);
                            let t_raw = [0, 1, 2].map(|k| p(va.tangent[k], vb.tangent[k], vc.tangent[k]));
                            let t_o = sub(t_raw, [0, 1, 2].map(|k| n[k] * dot(n, t_raw)));
                            if dot(t_o, t_o) < 1e-8 {
                                n
                            } else {
                                let tg = normalize(t_o);
                                let bt = cross(n, tg).map(|c| c * tw.signum());
                                normalize([0, 1, 2].map(|k| tg[k] * tn[0] + bt[k] * tn[1] + n[k] * tn[2]))
                            }
                        }
                        _ => n,
                    };
                    let _ = geometric_n;
                    let tint = if env::var("NO_VCOL").is_ok() { [1.0; 4] } else { vcol };
                    let albedo = [0, 1, 2].map(|k| srgb_to_linear(base[k]) * tint[k]);
                    let light = if material.unlit {
                        [material.emissive_scale; 3]
                    } else if let (true, Some(lm)) = (baked, lightmap) {
                        let (u, v) = (p(va.lightmap_uv[0], vb.lightmap_uv[0], vc.lightmap_uv[0]), p(va.lightmap_uv[1], vb.lightmap_uv[1], vc.lightmap_uv[1]));
                        let amb = rgbm(sample(&lm.ambient_rgbm, lm.width, lm.height, u, v));
                        let dir_col = rgbm(sample(&lm.directional_rgbm, lm.width, lm.height, u, v));
                        let d = sample(&lm.direction, lm.width, lm.height, u, v);
                        let dir = normalize([d[0] * 2.0 - 1.0, d[1] * 2.0 - 1.0, d[2] * 2.0 - 1.0]);
                        let ndl = dot(n, dir).max(0.0);
                        let v = [0, 1, 2].map(|k| amb[k] + dir_col[k] * ndl);
                        let v = if square { v.map(|x| x * x) } else { v };
                        // Direction alpha: baked sun visibility.
                        add_sun(v, n, sun, sun_k * d[3])
                    } else if let (true, true) = (baked, mesh.vertex_light.is_some()) {
                        let lv = [0, 1].map(|j| [0, 1].map(|k| p(va.layer_uvs[j][k], vb.layer_uvs[j][k], vc.layer_uvs[j][k])));
                        let mut v = [lv[0][0], lv[0][1], lv[1][0]];
                        if let Some(sh) = instance.irradiance_sh.as_ref() {
                            let (num, den) = (sh9(sh, n), sh9(sh, geometric_n));
                            for k in 0..3 {
                                v[k] *= (num[k] / den[k].max(0.02)).clamp(0.0, 4.0);
                            }
                        }
                        add_sun(v, n, sun, sun_k * lv[1][1])
                    } else if let (true, Some(sh)) = (baked, instance.irradiance_sh.as_ref()) {
                        let v = sh9(sh, n);
                        let v = if square { v.map(|x| x * x) } else { v };
                        add_sun(v, n, sun, sun_k * instance.sun_visibility.unwrap_or(1.0))
                    } else {
                        add_sun([0.18; 3], n, sun, sun_k)
                    };
                    let albedo = if env::var("LIGHT_ONLY").is_ok() { [0.5; 3] } else { albedo };
                    let mut lit = [0, 1, 2].map(|k| albedo[k] * light[k] * exposure);
                    if engine_mode && !material.unlit {
                        // Specular like the engine: GGX sun + environment reflection.
                        let spec_sample = material
                            .specular_texture
                            .map(|t| &scene.textures[t])
                            .map(|t| sample(&t.rgba, t.width, t.height, tu, tv));
                        let (f0, roughness) = match spec_sample {
                            Some(sg) => ([0, 1, 2].map(|k| srgb_to_linear(sg[k])), (1.0 - sg[3]).clamp(0.045, 1.0)),
                            None if material.gloss_from_color_alpha => ([0.04; 3], (1.0 - base[3]).clamp(0.045, 1.0)),
                            None => ([0.04; 3], material.roughness),
                        };
                        // Specular-glossiness: diffuse loses what specular reflects.
                        let keep = 1.0 - f0[0].max(f0[1]).max(f0[2]);
                        for k in 0..3 {
                            lit[k] *= keep;
                        }
                        let wp = [0, 1, 2].map(|k| p(va.position[k], vb.position[k], vc.position[k]));
                        let view = normalize(sub(eye, wp));
                        let probe = instance.reflection_probe.map(|i| &scene.reflection_probes[i]);
                        let spec = engine_specular(n, view, roughness, f0, sun, scene, light, probe);
                        for k in 0..3 {
                            lit[k] += spec[k] * exposure;
                        }
                    }
                    if let Some(fog) = &scene.fog {
                        let wp = [0, 1, 2].map(|k| p(va.position[k], vb.position[k], vc.position[k]));
                        let ray = sub(wp, eye);
                        let distance = dot(ray, ray).sqrt();
                        lit = apply_fog(fog, eye, normalize(ray), distance, lit);
                    }
                    let out = &mut color[slot];
                    match material.alpha {
                        NeutralAlpha::Blend => {
                            for k in 0..3 {
                                out[k] = lit[k] * alpha + out[k] * (1.0 - alpha);
                            }
                        }
                        NeutralAlpha::Additive => {
                            for k in 0..3 {
                                out[k] += lit[k] * alpha;
                            }
                        }
                        NeutralAlpha::Multiply => {
                            for k in 0..3 {
                                out[k] *= srgb_to_linear(base[k]) * vcol[k];
                            }
                        }
                        _ => {
                            depth[slot] = z;
                            *out = lit;
                            if pick == Some(slot) {
                                picked = Some(instance_index);
                            }
                        }
                    }
                }
            }
          }
        }
    }
    if let Some(i) = picked {
        let inst = &scene.instances[i];
        let mesh = &scene.meshes[inst.mesh];
        println!("PICK instance {i} mesh {} ({}) material {} at [{:.1} {:.1} {:.1}]", inst.mesh, mesh.name, scene.materials[mesh.material].name, inst.rows[0][3], inst.rows[1][3], inst.rows[2][3]);
    }
    let volume_grade = scene.grade.as_ref().map(|grade| {
        let mut g = grade.clone();
        if let Some((index, (_, m))) = grade.exposure_volumes.iter().enumerate().find(|(_, (planes, _))| {
            planes.iter().all(|p| p[0] * eye[0] + p[1] * eye[1] + p[2] * eye[2] + p[3] <= 0.0)
        }) {
            println!("camera in exposure volume {index}: multiplier {m} (map {})", grade.exposure);
            g.exposure = *m;
        }
        g
    });
    match &volume_grade {
        Some(grade) if env::var("ACES").is_err() => color
            .into_iter()
            .flat_map(|c| display_grade(grade, c).map(|v| (v.clamp(0.0, 1.0) * 255.0 + 0.5) as u8))
            .collect(),
        _ => color
            .into_iter()
            .flat_map(|c| c.map(|v| (linear_to_srgb(aces(v)) * 255.0) as u8))
            .collect(),
    }
}

/// Specular terms of native_environment.wgsl for a dielectric (F0 = 0.04):
/// GGX from the sun plus environment reflection at `ibl_specular_strength` 0.12,
/// occluded by baked light as in the shader.
#[allow(clippy::too_many_arguments)]
pub fn engine_specular(
    n: [f32; 3],
    v: [f32; 3],
    roughness: f32,
    f0c: [f32; 3],
    sun: Option<crate::NeutralSun>,
    scene: &NeutralScene,
    baked: [f32; 3],
    probe: Option<&crate::NeutralReflectionProbe>,
) -> [f32; 3] {
    let f0 = (f0c[0] + f0c[1] + f0c[2]) / 3.0;
    let n_dot_v = dot(n, v).max(0.0);
    let mut out = [0.0f32; 3];
    if let Some(sun) = sun {
        let l = sun.direction_to_light;
        let n_dot_l = dot(n, l);
        if n_dot_l > 0.0 {
            let h = normalize([v[0] + l[0], v[1] + l[1], v[2] + l[2]]);
            let a2 = roughness.powi(4);
            let nh = dot(n, h).max(0.0);
            let denom = nh * nh * (a2 - 1.0) + 1.0;
            let ndf = a2 / (std::f32::consts::PI * denom * denom).max(1e-6);
            let k = (roughness + 1.0).powi(2) / 8.0;
            let g = (n_dot_v / (n_dot_v * (1.0 - k) + k)) * (n_dot_l / (n_dot_l * (1.0 - k) + k));
            for c in 0..3 {
                let f = f0c[c] + (1.0 - f0c[c]) * (1.0 - dot(h, v).max(0.0)).powi(5);
                let spec = f * ndf * g / (4.0 * n_dot_v * n_dot_l).max(1e-4);
                out[c] += spec * sun.color[c] * sun.intensity * n_dot_l;
            }
        }
    }
    let r = [0, 1, 2].map(|k| 2.0 * dot(n, v) * n[k] - v[k]);
    let brdf_c = |f0: f32| {
        let c0 = [-1.0f32, -0.0275, -0.572, 0.022];
        let c1 = [1.0f32, 0.0425, 1.04, -0.04];
        let rr: [f32; 4] = std::array::from_fn(|i| roughness * c0[i] + c1[i]);
        let a004 = (rr[0] * rr[0]).min((-9.28 * n_dot_v).exp2()) * rr[0] + rr[1];
        let ab = [-1.04 * a004 + rr[2], 1.04 * a004 + rr[3]];
        (f0 * ab[0] + ab[1]).max(0.0)
    };
    if let Some(probe) = probe {
        let level = ((roughness * (probe.mips.len() - 1) as f32).round() as usize).min(probe.mips.len() - 1);
        let side = (probe.size >> level).max(1);
        let (face, u, w) = cube_lookup(normalize(r));
        let t = sample(&probe.mips[level][face], side, side, u, w);
        let mut env = rgbm(t);
        // Engine: scale by local baked light / probe mean luminance.
        let last = probe.mips.len() - 1;
        let lside = (probe.size >> last).max(1) as usize;
        let (mut sum, mut count) = (0.0f32, 0usize);
        for f in 0..6 {
            for p in probe.mips[last][f].chunks_exact(4).take(lside * lside) {
                let m = p[3] as f32 / 255.0 * LIGHTMAP_RGBM_RANGE;
                sum += (0.2126 * p[0] as f32 + 0.7152 * p[1] as f32 + 0.0722 * p[2] as f32) / 255.0 * m;
                count += 1;
            }
        }
        let probe_lum = sum / count.max(1) as f32;
        let local = 0.2126 * baked[0] + 0.7152 * baked[1] + 0.0722 * baked[2];
        if probe_lum > 1e-4 {
            let k = (local / probe_lum.max(0.1)).clamp(0.0, 2.0);
            env = env.map(|e| e * k);
        }
        for c in 0..3 {
            out[c] += env[c] * brdf_c(f0c[c]);
        }
        return out;
    }
    if let Some(sky) = &scene.sky {
        let (face, u, w) = cube_lookup(normalize(r));
        let t = &sky.faces[face];
        let env = sample(&t.rgba, t.width, t.height, u, w);
        // environment_brdf_approximation
        let c0 = [-1.0f32, -0.0275, -0.572, 0.022];
        let c1 = [1.0f32, 0.0425, 1.04, -0.04];
        let rr: [f32; 4] = std::array::from_fn(|i| roughness * c0[i] + c1[i]);
        let a004 = (rr[0] * rr[0]).min((-9.28 * n_dot_v).exp2()) * rr[0] + rr[1];
        let ab = [-1.04 * a004 + rr[2], 1.04 * a004 + rr[3]];
        let brdf = (f0 * ab[0] + ab[1]).max(0.0);
        let lum = 0.2126 * baked[0] + 0.7152 * baked[1] + 0.0722 * baked[2];
        let occlusion = (lum * 2.0).clamp(0.05, 1.0);
        for c in 0..3 {
            out[c] += srgb_to_linear(env[c]) * brdf * 0.12 * occlusion;
        }
    }
    out
}

pub fn add_sun(v: [f32; 3], n: [f32; 3], sun: Option<crate::NeutralSun>, k: f32) -> [f32; 3] {
    let Some(sun) = sun else { return v };
    let ndl = dot(n, sun.direction_to_light).max(0.0);
    [0, 1, 2].map(|c| v[c] + sun.color[c] * sun.intensity * k * ndl)
}

pub fn lerp_vertex(a: &NeutralVertex, b: &NeutralVertex, t: f32) -> NeutralVertex {
    let l = |x: f32, y: f32| x + (y - x) * t;
    NeutralVertex {
        position: [0, 1, 2].map(|k| l(a.position[k], b.position[k])),
        normal: [0, 1, 2].map(|k| l(a.normal[k], b.normal[k])),
        tangent: [0, 1, 2, 3].map(|k| l(a.tangent[k], b.tangent[k])),
        uv: [0, 1].map(|k| l(a.uv[k], b.uv[k])),
        color: [0, 1, 2, 3].map(|k| l(a.color[k], b.color[k])),
        data: [0, 1, 2, 3].map(|k| l(a.data[k], b.data[k])),
        lightmap_uv: [0, 1].map(|k| l(a.lightmap_uv[k], b.lightmap_uv[k])),
        layer_weights: [0, 1].map(|k| l(a.layer_weights[k], b.layer_weights[k])),
        layer_uvs: [0, 1].map(|j| [0, 1].map(|k| l(a.layer_uvs[j][k], b.layer_uvs[j][k]))),
    }
}

pub fn cube_lookup(d: [f32; 3]) -> (usize, f32, f32) {
    let [x, y, z] = d;
    let (ax, ay, az) = (x.abs(), y.abs(), z.abs());
    let (face, sc, tc, ma) = if ax >= ay && ax >= az {
        if x > 0.0 { (0, -z, -y, ax) } else { (1, z, -y, ax) }
    } else if ay >= az {
        if y > 0.0 { (2, x, z, ay) } else { (3, x, -z, ay) }
    } else if z > 0.0 {
        (4, x, -y, az)
    } else {
        (5, -x, -y, az)
    };
    (face, (sc / ma + 1.0) * 0.5, (tc / ma + 1.0) * 0.5)
}

pub fn sub(a: [f32; 3], b: [f32; 3]) -> [f32; 3] {
    [a[0] - b[0], a[1] - b[1], a[2] - b[2]]
}
pub fn dot(a: [f32; 3], b: [f32; 3]) -> f32 {
    a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
}
pub fn cross(a: [f32; 3], b: [f32; 3]) -> [f32; 3] {
    [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
}
pub fn normalize(a: [f32; 3]) -> [f32; 3] {
    let l = dot(a, a).sqrt().max(1e-9);
    [a[0] / l, a[1] / l, a[2] / l]
}
