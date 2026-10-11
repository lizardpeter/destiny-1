/// Standard GPU cubemap face basis. This is the SAME source-neutral
/// convention as the engine's Destiny and Minecraft sky paths:
/// (+X,-X,+Y,-Y,+Z,-Z), u rightward, v downward.
fn source_cube_texel_direction(face:usize,u:f32,v:f32)->[f32;3]{
    match face{
        0=>[1.,-v,-u],
        1=>[-1.,-v,u],
        2=>[u,1.,v],
        3=>[u,-1.,-v],
        4=>[u,-v,1.],
        5=>[-u,-v,-1.],
        _=>unreachable!("six original cube faces only"),
    }
}
/// Find the original source face and u/v for the D3D cubemap direction.
/// A 90-degree change of world axes is NOT only a face permutation:
/// most faces also require a 90-degree in-plane texture rotation.
fn source_cube_face_uv(d:[f32;3])->(usize,f32,f32){
    let [x,y,z]=d;
    let [ax,ay,az]=[x.abs(),y.abs(),z.abs()];
    if ax>=ay &&ax>=az{
        if x>=0.{(0,-z/ax,-y/ax)}else{(1,z/ax,-y/ax)}
    }else if ay>=az{
        if y>=0.{(2,x/ay,z/ay)}else{(3,x/ay,-z/ay)}
    }else if z>=0.{
        (4,x/az,-y/az)
    }else{
        (5,-x/az,-y/az)
    }
}
/// Resample source UE4 Z-up cube faces onto engine Y-up cube face pixel
/// coordinates, using the exact rigid axis mapping source x,y,z ->
/// engine x,z,-y. Each target texel samples a physical direction in the
/// original cubemap; arbitrary face UV copying would introduce seams.
/// Standard 90-degree rotation maps texel centers without scaling.
pub fn rotate_source_cube_face_to_engine(
    original_faces:&[Vec<u8>;6],side:u32,engine_face:usize,
)->Result<Vec<u8>,String>{
    if side==0 ||side>4096 ||engine_face>=6{return Err("invalid source cubemap extent or face".into());}
    let side=side as usize;
    let byte_len=side.checked_mul(side).and_then(|n|n.checked_mul(4))
        .ok_or("source cube face length overflow")?;
    if original_faces.iter().any(|face|face.len()!=byte_len){
        return Err("source cubemap faces have inconsistent RGBA byte lengths".into());
    }
    let mut result=vec![0u8;byte_len];
    for y in 0..side{
        for x in 0..side{
            let u=(x as f32+0.5)/side as f32*2.-1.;
            let v=(y as f32+0.5)/side as f32*2.-1.;
            let e=source_cube_texel_direction(engine_face,u,v);
            let source_dir=[e[0],-e[2],e[1]];
            let (source_face,su,sv)=source_cube_face_uv(source_dir);
            let sx=((su+1.)*0.5*side as f32).floor().clamp(0.,side as f32-1.) as usize;
            let sy=((sv+1.)*0.5*side as f32).floor().clamp(0.,side as f32-1.) as usize;
            let from=(sy*side+sx)*4;
            let to=(y*side+x)*4;
            result[to..to+4].copy_from_slice(&original_faces[source_face][from..from+4]);
        }
    }
    Ok(result)
}


#[cfg(test)]
mod tests{
    use super::*;
    #[test] fn source_cube_face_directions_transform_without_losing_face_uv_rotation(){
        let mappings=[0usize,1,4,5,3,2];
        for (engine,&source) in mappings.iter().enumerate(){
            let e=source_cube_texel_direction(engine,0.,0.);
            let (actual,su,sv)=source_cube_face_uv([e[0],-e[2],e[1]]);
            assert_eq!(actual,source);
            assert!(su.abs()<0.001 &&sv.abs()<0.001);
        }
        // Engine +X face image-left maps source +X image-top (90-deg
        // rotation). A face permutation without pixel rotation fails.
        let e=source_cube_texel_direction(0,-0.5,0.);
        let (face,u,v)=source_cube_face_uv([e[0],-e[2],e[1]]);
        assert_eq!(face,0);
        assert!(u.abs()<0.001);
        assert!(v>0.4);
    }
    #[test] fn source_cube_reorientation_preserves_original_rgba_texels(){
        const SIDE:usize=4;
        let faces=std::array::from_fn(|f|{
            let mut pixels=Vec::new();
            for y in 0..SIDE{for x in 0..SIDE{
                pixels.extend_from_slice(&[f as u8,x as u8,y as u8,255]);
            }}
            pixels
        });
        let mut used=std::collections::BTreeSet::new();
        for engine in 0..6{
            let output=rotate_source_cube_face_to_engine(&faces,SIDE as u32,engine).unwrap();
            assert_eq!(output.len(),SIDE*SIDE*4);
            for pixel in output.chunks_exact(4){
                assert_eq!(pixel[3],255);
                assert!(pixel[0]<6 &&pixel[1]<4 &&pixel[2]<4);
                used.insert(pixel[0]);
            }
        }
        assert_eq!(used,(0u8..6).collect());
        assert!(rotate_source_cube_face_to_engine(&faces,0,0).is_err());
    }
}
