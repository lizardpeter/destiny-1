# physics/

<!-- GENERATED: d1_reconstruction_tree.py -->
**Subsystem key:** `engine.physics`  
**Folder path evidence:** `HYPOTHESIS` (folder name is a proposal from RTTI/log-channel clustering, not a recovered path)  
**Role:** Havok physics bridge, physics components and collectors

## Source files named in the binary

_None recovered (retail build stripped most asserts)._

## Decompiled functions

_None yet._

## Classes (66)

Class data (name, typeinfo, vtable, bases) is `CONFIRMED_BINARY` from Itanium RTTI. Placement in this folder is `HYPOTHESIS` (name-token rule).

| class | typeinfo | vtable | virtual slots | bases |
|---|---|---|---|---|
| `c_action_impl_physics_driven_ai_locomotion` | `0x19355f0` | `0x1935560` | 17 | c_action_api |
| `c_action_impl_physics_driven_locomotion` | `0x19356c0` | `0x1935630` | 17 | c_action_api |
| `c_anti_vehicle_summoning_physics_component_type_system` | `0x1948660` | `0x1948640` | 6 | c_physics_component_type_system_interface |
| `c_async_raycast_multi_hit_collector` | `0x19085b0` | `0x1908580` | 5 | hkpRayHitCollector |
| `c_bubble_transition_wall_contact_listener` | `0x19486e0` | `0x19486a0` | 10 | hkpContactListener |
| `c_bubble_transition_wall_physics_component_type_system` | `0x1948750` | `0x1948730` | 6 | c_physics_component_type_system_interface |
| `c_camera_obstruction_cd_point_collector` | `0x1949dc0` | `0x1949da0` | 6 | hkpClosestCdPointCollector |
| `c_camera_obstruction_ray_hit_collector` | `0x1949d70` | `0x1949d50` | 3 | hkpRayHitCollector |
| `c_character_obstruction_early_out_penetration_collector` | `0x194c580` | `0x194c560` | 6 | c_early_out_penetration_collector |
| `c_character_physics_game_system` | `0x1937b60` | `0x1937b30` | 8 | c_game_system_interface |
| `c_closest_point_collector` | `0x194c5a0` | `0x194c480` | 4 | hkpCdPointCollector |
| `c_cloth_audio` | `0x19478e0` | `0x1947850` | 3 | i_cloth_audio |
| `c_cloth_display_buffer` | `0x1948a40` | `0x19489f0` | 12 | hclBuffer |
| `c_cloth_instantiation_util` | `0x1948ae0` | `0x1948a80` | 14 | hclInstantiationUtil |
| `c_cloth_large_block_allocator` | `0x1948c30` | `0x1948b10` | 22 | hkLargeBlockAllocator |
| `c_cloth_physics_bridge` | `0x1948dd0` | `0x1948d40` | 9 | hclPhysicsClothWorld |
| `c_cloth_physics_bridge_collector` | `0x1948e60` | `0x1948e00` | 7 | hclPhysicsClothWorld::BroadphaseCollector |
| `c_cloth_physics_bridge_filter` | `0x1948fa0` | `0x1948e90` | 11 | hkpCollisionFilter |
| `c_cloth_wind` | `0x1948d10` | `0x1948cd0` | 7 | hclSimpleWindAction |
| `c_cloth_world_game_system` | `0x1948ca0` | `0x1948c70` | 8 | c_game_system_interface |
| `c_confinement_volume_contact_listener` | `0x1908b70` | `0x1908b30` | 10 | hkpContactListener |
| `c_confinement_volume_physics_component_type_system` | `0x1908bf0` | `0x1908bd0` | 6 | c_physics_component_type_system_interface |
| `c_dead_sphere_contact_listener` | `0x1937cc0` | `0x1937c80` | 10 | hkpContactListener |
| `c_dumpling_physics_component_type_system` | `0x1947bf0` | `0x1947bd0` | 6 | c_physics_component_type_system_interface |
| `c_early_out_penetration_collector` | `0x194c530` | `0x194c510` | 6 | hkpCdBodyPairCollector |
| `c_early_out_ray_hit_collector` | `0x1908850` | `0x1908830` | 3 | hkpRayHitCollector |
| `c_environment_physics_component_type_system` | `0x1908c40` | `0x1908c20` | 6 | c_physics_component_type_system_interface |
| `c_ghost_light_volume_physics_component_type_system` | `0x1914530` | `0x1914510` | 6 | c_physics_component_type_system_interface |
| `c_ground_contact_point_collector` | `0x1937c40` | `0x1937c20` | 6 | hkpFixedBufferCdPointCollector |
| `c_havok_error_handler` | `0x1909b40` | `0x1909af0` | 12 | hkError |
| `c_havok_runtime_system_game_system` | `0x1941640` | `0x1941610` | 8 | c_game_system_interface |
| `c_havok_shape_phantom` | `0x1909300` | `0x1909210` | 20 | hkpSimpleShapePhantom |
| `c_havok_thread_safe_allocator` | `0x1908da0` | `0x1908c80` | 22 | hkMemoryAllocator, hkMemoryAllocator::ExtendedInterface @+0x8 |
| `c_havok_transform_shape` | `0x1908ea0` | `0x1908e00` | 22 | hkpConvexTransformShape |
| `c_havok_trigger_volume` | `0x1906940` | `0x1906810` | 13 | hkpTriggerVolume |
| `c_havok_type_info_registry` | `0x1909c60` | `0x1909bc0` | 11 | hkTypeInfoRegistry |
| `c_havok_verifying_allocator` | `0x1909010` | `0x1908fa0` | 13 | hkMemoryAllocator |
| `c_keyframed_contact_listener` | `0x1909160` | `0x1909120` | 10 | hkpContactListener |
| `c_kill_volume_game_system` | `0x1906730` | `0x1906700` | 8 | c_game_system_interface |
| `c_object_physics_component_type_system` | `0x19091c0` | `0x19091a0` | 6 | c_physics_component_type_system_interface |
| `c_phantom_accelerator_component_pair_collector` | `0x19092e0` | `0x19092c0` | 6 | hkpCdBodyPairCollector |
| `c_physics_component_filter_collector` | `0x19093d0` | `0x19093b0` | 6 | hkpAllCdBodyPairCollector |
| `c_physics_component_filter_point_collector` | `0x1909420` | `0x1909400` | 6 | hkpClosestCdPointCollector |
| `c_physics_component_toi_contact_listener` | `0x19090e0` | `0x19090a0` | 10 | hkpContactListener |
| `c_physics_component_type_system_interface` | `0x1906990` | `0x1909340` | 4 |  |
| `c_physics_constants_game_system` | `0x1941040` | `0x1941010` | 8 | c_game_system_interface |
| `c_physics_filter` | `0x19086f0` | `0x19085e0` | 11 | hkpCollisionFilter |
| `c_physics_game_system` | `0x1940b30` | `0x1940b00` | 8 | c_game_system_interface |
| `c_physics_island_activation_listener` | `0x1909060` | `0x1909040` | 6 | hkpIslandActivationListener |
| `c_physics_memory_interface` | `0x1908a08` |  |  |  |
| `c_physics_memory_watch_dog` | `0x19087c0` | `0x1908780` | 7 | hkWorldMemoryAvailableWatchDog |
| `c_player_spawning_penetration_collector` | `0x1937040` | `0x1937020` | 6 | c_character_obstruction_early_out_penetration_collector |
| `c_point_physics_game_system` | `0x1940e90` | `0x1940e60` | 8 | c_game_system_interface |
| `c_projectile_closest_point_collector` | `0x194c5c0` | `0x194c4b0` | 4 | c_closest_point_collector |
| `c_projectile_closest_point_collector_ignore_water` | `0x194c5e0` | `0x194c4e0` | 4 | c_projectile_closest_point_collector |
| `c_reject_biped_contact_listener` | `0x1937bd0` | `0x1937b90` | 10 | hkpContactListener |
| `c_simple_cd_collector` | `0x1909470` | `0x1909450` | 6 | hkpCdPointCollector |
| `c_smooth_surface_point_collector` | `0x1944150` | `0x1944130` | 6 | hkpCdPointCollector |
| `c_spawn_volume_game_system` | `0x1940a70` | `0x1940a40` | 8 | c_game_system_interface |
| `c_trigger_volume_game_system` | `0x19067d0` | `0x19067a0` | 8 | c_game_system_interface |
| `c_trigger_volume_physics_component_type_system` | `0x19069a0` | `0x1906970` | 8 | c_physics_component_type_system_interface |
| `c_vehicle_contact_point_collector` | `0x1943890` | `0x1943870` | 6 | c_closest_point_collector |
| `c_vehicle_physics_component_game_system` | `0x19438f0` | `0x19438c0` | 8 | c_game_system_interface |
| `c_vehicle_physics_component_type_system` | `0x1943960` | `0x1943940` | 6 | c_physics_component_type_system_interface |
| `c_water_contact_listener` | `0x1949710` | `0x19496d0` | 10 | hkpContactListener |
| `i_cloth_audio` | `0x1947958` |  |  |  |

<!-- /GENERATED -->

## Notes

_Hand-written findings for this folder go here; regeneration keeps everything outside the generated block._
