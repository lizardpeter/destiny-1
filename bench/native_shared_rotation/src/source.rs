use glam::{Mat4,Vec3,Vec4};
pub fn world_to_view_rotation(view_projection: [[f32; 4]; 4]) -> [[f32; 4]; 3] {
    let inverse = Mat4::from_cols_array_2d(&view_projection).inverse();
    if !inverse.is_finite() {
        return [
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
        ];
    }

    let unproject = |x: f32, y: f32| -> Option<Vec3> {
        // z=0 is sufficient: differences between points on the same clip-space
        // depth plane recover the camera right/up axes even for an asymmetric
        // perspective projection.
        let h = inverse * Vec4::new(x, y, 0.0, 1.0);
        if !h.is_finite() || !h.w.is_finite() || h.w.abs() <= 1.0e-8 {
            return None;
        }
        let p = h.truncate() / h.w;
        p.is_finite().then_some(p)
    };

    let Some(left) = unproject(-1.0, 0.0) else {
        return identity_world_to_view_rotation();
    };
    let Some(right_point) = unproject(1.0, 0.0) else {
        return identity_world_to_view_rotation();
    };
    let Some(down) = unproject(0.0, -1.0) else {
        return identity_world_to_view_rotation();
    };
    let Some(up_point) = unproject(0.0, 1.0) else {
        return identity_world_to_view_rotation();
    };

    let right = (right_point - left).normalize_or_zero();
    let up_seed = (up_point - down).normalize_or_zero();
    let backward = right.cross(up_seed).normalize_or_zero();
    if right.length_squared() <= 0.5 || backward.length_squared() <= 0.5 {
        return identity_world_to_view_rotation();
    }
    // Re-orthogonalize the second row so projection jitter/skew cannot leak
    // scale into the source-neutral view rotation.
    let up = backward.cross(right).normalize_or_zero();
    if up.length_squared() <= 0.5 {
        return identity_world_to_view_rotation();
    }
    [
        [right.x, right.y, right.z, 0.0],
        [up.x, up.y, up.z, 0.0],
        [backward.x, backward.y, backward.z, 0.0],
    ]
}

#[inline]
fn identity_world_to_view_rotation() -> [[f32; 4]; 3] {
    [
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
    ]
}

