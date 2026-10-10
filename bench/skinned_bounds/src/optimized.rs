fn affine_rows_to_mat4(rows: [f32; 12]) -> glam::Mat4 {
    glam::Mat4::from_cols_array(&[
        rows[0], rows[4], rows[8], 0.0,
        rows[1], rows[5], rows[9], 0.0,
        rows[2], rows[6], rows[10], 0.0,
        rows[3], rows[7], rows[11], 1.0,
    ])
}

pub fn world_motion_radius_scale(matrix: glam::Mat4) -> f32 {
    let x = matrix.x_axis.truncate();
    let y = matrix.y_axis.truncate();
    let z = matrix.z_axis.truncate();
    let sx = x.length();
    let sy = y.length();
    let sz = z.length();
    let orthogonal = {
        let nx = x.normalize_or_zero();
        let ny = y.normalize_or_zero();
        let nz = z.normalize_or_zero();
        nx.dot(ny).abs() <= 1.0e-4
            && nx.dot(nz).abs() <= 1.0e-4
            && ny.dot(nz).abs() <= 1.0e-4
    };
    let radius_scale = if orthogonal {
        sx.max(sy).max(sz)
    } else {
        (sx * sx + sy * sy + sz * sz).sqrt()
    };

    radius_scale
}

pub fn world_motion_bounds_prepared(
    matrix: glam::Mat4,
    radius_scale: f32,
    local: [f32; 4],
) -> [f32; 4] {
    let center = matrix.transform_point3(glam::Vec3::new(local[0], local[1], local[2]));
    [
        center.x,
        center.y,
        center.z,
        local[3].max(0.0) * radius_scale.max(0.0),
    ]
}