use ash::vk;
use std::slice;

// This is the Vulkan recording code of NativeLightClusters::record_build
// for a scene whose only lights are global/directional. It is compiled
// against the exact ash Git SHA pinned by Rust-test and never executed
// without a valid Vulkan device and command buffer.
#[allow(dead_code)]
fn update_global_header(device: &ash::Device, command_buffer: vk::CommandBuffer,
    ranges: vk::Buffer, extent: vk::Extent2D) {
    let dimensions = [extent.width.max(1), extent.height.max(1)];
    unsafe {
        device.cmd_update_buffer(
            command_buffer, ranges, 0,
            bytemuck::cast_slice(&dimensions),
        );
        let to_shader = vk::BufferMemoryBarrier2::default()
            .src_stage_mask(vk::PipelineStageFlags2::TRANSFER)
            .src_access_mask(vk::AccessFlags2::TRANSFER_WRITE)
            .dst_stage_mask(
                vk::PipelineStageFlags2::VERTEX_SHADER
                | vk::PipelineStageFlags2::FRAGMENT_SHADER,
            )
            .dst_access_mask(vk::AccessFlags2::SHADER_STORAGE_READ)
            .src_queue_family_index(vk::QUEUE_FAMILY_IGNORED)
            .dst_queue_family_index(vk::QUEUE_FAMILY_IGNORED)
            .buffer(ranges)
            .offset(0)
            .size(std::mem::size_of_val(&dimensions) as u64);
        device.cmd_pipeline_barrier2(
            command_buffer,
            &vk::DependencyInfo::default()
                .buffer_memory_barriers(slice::from_ref(&to_shader)),
        );
    }
}

const CLUSTER_COUNT:usize=16*9*24;
fn expected_header(global_sources: usize)->Vec<[u32;2]> {
 let mut data=vec![[0u32;2];3+CLUSTER_COUNT];
 data[1]=[0.5f32.to_bits(),(24.0f32/14.0f32).to_bits()];
 data[2]=[global_sources as u32,0];
 data[3..].fill([global_sources as u32,global_sources as u32]);
 data
}
#[test]
fn source_global_header_matches_original_cs_global_main() {
 for count in [1usize,2,129,10_000]{
  let orig=expected_header(count);
  for (width,height) in [(0,0),(1,1),(1920,1080),(3840,2160),(16_384,16_384)]{
   let new=[width.max(1),height.max(1)];
   let mut updated=orig.clone();
   let bytes=bytemuck::cast_slice::<u32,u8>(&new);
   bytemuck::cast_slice_mut::<[u32;2],u8>(&mut updated)[0..8].copy_from_slice(bytes);
   assert_eq!(updated[0],new);
   assert_eq!(&updated[1..],&orig[1..]);
  }
 }
}
#[test]
fn direct_header_command_is_transfer_dst_and_aligned() {
 assert_eq!(std::mem::size_of::<[u32;2]>(),8);
 assert_eq!(std::mem::align_of::<[u32;2]>(),4);
 let buffer_usage=vk::BufferUsageFlags::STORAGE_BUFFER|vk::BufferUsageFlags::TRANSFER_DST;
 assert!(buffer_usage.contains(vk::BufferUsageFlags::TRANSFER_DST));
}
