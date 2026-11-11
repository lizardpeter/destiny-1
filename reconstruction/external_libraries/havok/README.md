# havok/

<!-- GENERATED: d1_reconstruction_tree.py -->
**Subsystem key:** `tp.havok`  
**Folder path evidence:** `CONFIRMED_BINARY`  
**Role:** Havok 2012.2.0 Physics + Cloth (d:\bungie\external_libraries\havok\2012-2-0_8)

## Source files named in the binary

19 verbatim path strings (`CONFIRMED_BINARY`). Third-party code is identified, not reconstructed.

- `C:\perforce\Clients\Tiger\Source\Cloth\Cloth\Buffer\ScratchBuffer\hclScratchBufferDefinition.cpp`
- `C:\perforce\Clients\Tiger\Source\Cloth\Cloth\Collide\Shape\TaperedCapsule\hclTaperedCapsuleShape.cpp`
- `C:\perforce\Clients\Tiger\Source\Cloth\Cloth\Operator\hclOperatorDispatcherCpu.cpp`
- `C:\perforce\Clients\Tiger\Source\Cloth\Cloth\TransformSet\hclTransformSetDefinition.cpp`
- `C:\perforce\Clients\Tiger\Source\Cloth\Cloth\Utilities\Instantiation\hclInstantiationUtil.cpp`
- `C:\perforce\Clients\Tiger\Source\Cloth\Cloth\World\hclWorld.cpp`
- `C:\perforce\Clients\Tiger\Source\Common\Base\System\Error\hkError.cpp`
- `C:\perforce\Clients\Tiger\Source\Common\Base\System\Io\Platform\Orbis\hkOrbisStreamWriter.cpp`
- `C:\perforce\Clients\Tiger\Source\Common\Base\Thread\Semaphore\Posix\hkPosixSemaphore.cpp`
- `C:\perforce\Clients\Tiger\Source\Common\Serialize\Util\hkStructureLayout.cpp`
- `C:\perforce\Clients\Tiger\Source\Physics\Constraint\Data\hkpConstraintDataUtils.cpp`
- `C:\perforce\Clients\Tiger\Source\Physics\Dynamics\World\hkpWorld.cpp`
- `C:\perforce\Clients\Tiger\Source\Physics\Dynamics\World\Simulation\Continuous\hkpContinuousSimulation.cpp`
- `C:\perforce\Clients\Tiger\Source\Physics\Internal\BroadPhase\TreeBroadPhase\hkpTreeBroadPhase.cpp`
- `C:\perforce\Clients\Tiger\Source\Physics\Internal\Collide\BvCompressedMesh\hkpBvCompressedMeshShape.cpp`
- `C:\perforce\Clients\Tiger\Source\Physics\Internal\Collide\StaticCompound\hkpStaticCompoundShape.cpp`
- `C:\perforce\Clients\Tiger\Source\Physics\Utilities\Actions\EaseConstraints\hkpEaseConstraintsAction.cpp`
- `d:\bungie\external_libraries\havok\2012-2-0_8\source\Common/Base/Thread/CriticalSection/Posix/hkPosixCriticalSection.inl`
- `d:\bungie\external_libraries\havok\2012-2-0_8\source\Physics/Collide/Shape/Convex/hkpConvexShape.h`

## Decompiled functions

_None yet._

## Classes (341)

Class data (name, typeinfo, vtable, bases) is `CONFIRMED_BINARY` from Itanium RTTI. Placement in this folder follows the library prefix.

| class | typeinfo | vtable | virtual slots | bases |
|---|---|---|---|---|
| `(anonymous namespace)::hkpStaticCompoundShape_RayHitCollectorWrapper` | `0x19f0720` | `0x19f0750` | 3 | hkpRayHitCollector |
| `hclAction` | `0x1a014a0` | `0x1a01460` | 7 | hkReferencedObject |
| `hclAntiPinchConstraintInstanceData` | `0x1a04690` | `0x1a045f0` | 4 | hkReferencedObject |
| `hclAntiPinchConstraintSet` | `0x1a04670` | `0x1a04620` | 12 | hclConstraintSet |
| `hclBendLinkConstraintSet` | `0x1a002b0` | `0x1a00260` | 12 | hclConstraintSet |
| `hclBendLinkConstraintSetMx` | `0x1a039e0` | `0x1a03990` | 12 | hclConstraintSet |
| `hclBendStiffnessConstraintSet` | `0x1a03f60` | `0x1a03f10` | 12 | hclConstraintSet |
| `hclBendStiffnessConstraintSetMx` | `0x19fd620` | `0x19fd5d0` | 12 | hclConstraintSet |
| `hclBlendSomeVerticesOperator` | `0x1a03a80` | `0x1a03a10` | 13 | hclOperator |
| `hclBonePlanesConstraintSet` | `0x1a02b10` | `0x1a02ac0` | 12 | hclConstraintSet |
| `hclBoneSpaceMeshMeshDeformOperator` | `0x1a04520` | `0x1a044b0` | 13 | hclOperator |
| `hclBoneSpaceMeshMeshDeformPNOperator` | `0x1a015a0` | `0x1a01530` | 13 | hclBoneSpaceMeshMeshDeformOperator |
| `hclBoneSpaceMeshMeshDeformPNTBOperator` | `0x1a01ff0` | `0x1a01f80` | 13 | hclBoneSpaceMeshMeshDeformOperator |
| `hclBoneSpaceMeshMeshDeformPNTOperator` | `0x1a01430` | `0x1a013c0` | 13 | hclBoneSpaceMeshMeshDeformOperator |
| `hclBoneSpaceMeshMeshDeformPOperator` | `0x1a040a0` | `0x1a04030` | 13 | hclBoneSpaceMeshMeshDeformOperator |
| `hclBoneSpaceSkinOperator` | `0x1a03cc0` | `0x1a03c50` | 13 | hclOperator |
| `hclBoneSpaceSkinPNOperator` | `0x1a03570` | `0x1a03500` | 13 | hclBoneSpaceSkinOperator |
| `hclBoneSpaceSkinPNTBOperator` | `0x1a031b0` | `0x1a03140` | 13 | hclBoneSpaceSkinOperator |
| `hclBoneSpaceSkinPNTOperator` | `0x19feda0` | `0x19fed30` | 13 | hclBoneSpaceSkinOperator |
| `hclBoneSpaceSkinPOperator` | `0x1a02a90` | `0x1a02a20` | 13 | hclBoneSpaceSkinOperator |
| `hclBroadPhasePhantom` | `0x19491a0` | `0x1949120` | 18 | hkpAabbPhantom |
| `hclBuffer` | `0x19ff8f0` | `0x19ff8a0` | 12 | hkReferencedObject |
| `hclBufferDefinition` | `0x1a01770` | `0x1a01740` | 8 | hkReferencedObject |
| `hclCapsuleShape` | `0x19fde00` | `0x19fddc0` | 7 | hclShape |
| `hclClothContainer` | `0x19ff170` | `0x19ff150` | 6 | hkReferencedObject |
| `hclClothData` | `0x19ffbf0` | `0x19ffbd0` | 6 | hkReferencedObject |
| `hclClothInstance` | `0x19fe010` | `0x19fdff0` | 6 | hkReferencedObject |
| `hclClothState` | `0x19fcaf0` | `0x19fcad0` | 6 | hkReferencedObject |
| `hclCollidable` | `0x19481b0` | `0x1948190` | 6 | hkReferencedObject |
| `hclCollisionConvexes` | `0x19fb800` | `0x19fb7e0` | 6 | hkReferencedObject |
| `hclCollisionTriangles` | `0x19fb220` | `0x19fb200` | 6 | hkReferencedObject |
| `hclCompressibleLinkConstraintSet` | `0x19febf0` | `0x19feba0` | 12 | hclConstraintSet |
| `hclCompressibleLinkConstraintSetMx` | `0x1a03b00` | `0x1a03ab0` | 12 | hclConstraintSet |
| `hclConstraintSet` | `0x1a01c80` | `0x1a01c30` | 12 | hkReferencedObject |
| `hclConvexGeometryShape` | `0x1a034d0` | `0x1a03490` | 7 | hclShape |
| `hclConvexHeightFieldShape` | `0x19fd420` | `0x19fd3e0` | 7 | hclShape |
| `hclConvexPlanesShape` | `0x1a033e0` | `0x1a033a0` | 7 | hclShape |
| `hclCopyVerticesOperator` | `0x1a03d60` | `0x1a03cf0` | 13 | hclOperator |
| `hclGatherAllVerticesOperator` | `0x1a01b80` | `0x1a01b10` | 13 | hclOperator |
| `hclGatherSomeVerticesOperator` | `0x1a04000` | `0x1a03f90` | 13 | hclOperator |
| `hclInputConvertOperator` | `0x1a03610` | `0x1a035a0` | 13 | hclOperator |
| `hclInstantiationUtil` | `0x19ff3f0` |  |  | hkReferencedObject |
| `hclLocalRangeConstraintSet` | `0x1a03960` | `0x1a03910` | 12 | hclConstraintSet |
| `hclMeshBoneDeformOperator` | `0x1a04730` | `0x1a046c0` | 13 | hclOperator |
| `hclMeshMeshDeformOperator` | `0x1a04480` | `0x1a04410` | 13 | hclOperator |
| `hclMoveParticlesOperator` | `0x1a00070` | `0x1a00000` | 13 | hclOperator |
| `hclObjectSpaceMeshMeshDeformOperator` | `0x1a043e0` | `0x1a04370` | 13 | hclOperator |
| `hclObjectSpaceMeshMeshDeformPNOperator` | `0x1a01030` | `0x1a00fc0` | 13 | hclObjectSpaceMeshMeshDeformOperator |
| `hclObjectSpaceMeshMeshDeformPNTBOperator` | `0x1a03700` | `0x1a03690` | 13 | hclObjectSpaceMeshMeshDeformOperator |
| `hclObjectSpaceMeshMeshDeformPNTOperator` | `0x1a038e0` | `0x1a03870` | 13 | hclObjectSpaceMeshMeshDeformOperator |
| `hclObjectSpaceMeshMeshDeformPOperator` | `0x1a037a0` | `0x1a03730` | 13 | hclObjectSpaceMeshMeshDeformOperator |
| `hclObjectSpaceSkinOperator` | `0x19fe340` | `0x19fe2d0` | 13 | hclOperator |
| `hclObjectSpaceSkinPNOperator` | `0x19fed00` | `0x19fec90` | 13 | hclObjectSpaceSkinOperator |
| `hclObjectSpaceSkinPNTBOperator` | `0x1a03840` | `0x1a037d0` | 13 | hclObjectSpaceSkinOperator |
| `hclObjectSpaceSkinPNTOperator` | `0x19ff120` | `0x19ff0b0` | 13 | hclObjectSpaceSkinOperator |
| `hclObjectSpaceSkinPOperator` | `0x19fc680` | `0x19fc610` | 13 | hclObjectSpaceSkinOperator |
| `hclOperator` | `0x1a022a0` | `0x1a02230` | 13 | hkReferencedObject |
| `hclOutputConvertOperator` | `0x1a03e00` | `0x1a03d90` | 13 | hclOperator |
| `hclPhysicsClothWorld` | `0x1949070` | `0x1948fe0` | 9 | hclWorldListener, hkpEntityListener @+0x8 |
| `hclPhysicsClothWorld::BroadphaseCollector` | `0x1948e40` |  |  | hkpBroadPhaseCastCollector |
| `hclPhysicsClothWorld::ClothCollidables` | `0x19490f0` | `0x19490d0` | 6 | hkReferencedObject |
| `hclPlaneShape` | `0x19fb540` | `0x19fb4e0` | 7 | hclShape |
| `hclPointContactPlanesShape` | `0x19fec60` | `0x19fec20` | 7 | hclShape |
| `hclScratchBuffer` | `0x1a03ee0` | `0x1a03e90` | 12 | hclBuffer |
| `hclScratchBufferDefinition` | `0x19ff870` | `0x19ff840` | 8 | hclBufferDefinition |
| `hclShadowBuffer` | `0x1a03460` | `0x1a03410` | 12 | hclBuffer |
| `hclShadowBufferDefinition` | `0x1a04100` | `0x1a040d0` | 8 | hclBufferDefinition |
| `hclShape` | `0x19fb520` |  |  | hkReferencedObject |
| `hclSimClothData` | `0x1a03660` | `0x1a03640` | 6 | hkReferencedObject |
| `hclSimClothInstance` | `0x19fcb40` | `0x19fcb20` | 6 | hkReferencedObject |
| `hclSimClothPose` | `0x19fe100` | `0x19fe0e0` | 6 | hkReferencedObject |
| `hclSimpleMeshBoneDeformOperator` | `0x1a04270` | `0x1a04200` | 13 | hclOperator |
| `hclSimpleWindAction` | `0x19ff3d0` | `0x19ff390` | 7 | hclAction |
| `hclSimulateOperator` | `0x1a045c0` | `0x1a04550` | 13 | hclOperator |
| `hclSkinOperator` | `0x1a03ba0` | `0x1a03b30` | 13 | hclOperator |
| `hclSphereShape` | `0x19ff620` | `0x19ff5e0` | 7 | hclShape |
| `hclStandardLinkConstraintSet` | `0x19fd900` | `0x19fd8b0` | 12 | hclConstraintSet |
| `hclStandardLinkConstraintSetMx` | `0x1a01620` | `0x1a015d0` | 12 | hclConstraintSet |
| `hclStaticShadowBuffer` | `0x1a01880` | `0x1a01830` | 12 | hclBuffer |
| `hclStaticShadowBufferDefinition` | `0x19fd5a0` | `0x19fd570` | 8 | hclBufferDefinition |
| `hclStretchLinkConstraintSet` | `0x19fe3c0` | `0x19fe370` | 12 | hclConstraintSet |
| `hclStretchLinkConstraintSetMx` | `0x1a03c20` | `0x1a03bd0` | 12 | hclConstraintSet |
| `hclTaperedCapsuleShape` | `0x1a005c0` | `0x1a00580` | 7 | hclShape |
| `hclTransformSet` | `0x19fc6e0` | `0x19fc6b0` | 8 | hkReferencedObject |
| `hclTransformSetDefinition` | `0x1a03e60` | `0x1a03e30` | 5 | hkReferencedObject |
| `hclTransitionConstraintInstanceData` | `0x19ff080` | `0x19fefe0` | 4 | hkReferencedObject |
| `hclTransitionConstraintSet` | `0x19ff060` | `0x19ff010` | 12 | hclConstraintSet |
| `hclUpdateAllVertexFramesOperator` | `0x1a02090` | `0x1a02020` | 13 | hclOperator |
| `hclUpdateSomeVertexFramesOperator` | `0x1a01390` | `0x1a01320` | 13 | hclOperator |
| `hclVolumeConstraint` | `0x1a04180` | `0x1a04130` | 12 | hclConstraintSet |
| `hclVolumeConstraintInstanceData` | `0x1a041d0` | `0x1a041b0` | 6 | hkReferencedObject |
| `hclVolumeConstraintMx` | `0x1a042f0` | `0x1a042a0` | 12 | hclConstraintSet |
| `hclVolumeConstraintMxInstanceData` | `0x1a04340` | `0x1a04320` | 6 | hkReferencedObject |
| `hclWorld` | `0x19fe410` | `0x19fe3f0` | 6 | hkReferencedObject |
| `hclWorldListener` | `0x19fe430` |  |  |  |
| `hkBaseObject` | `0x19ee850` | `0x19ef0e0` | 3 |  |
| `hkBufferedStreamReader` | `0x19ef170` | `0x19ef110` | 11 | hkSeekableStreamReader |
| `hkBufferedStreamWriter` | `0x19ee8e0` | `0x19ee890` | 12 | hkStreamWriter |
| `hkBuiltinTypeRegistry` | `0x19f54b0` |  |  | hkReferencedObject, hkSingleton<hkBuiltinTypeRegistry> |
| `hkClassNameRegistry` | `0x19f5600` |  |  | hkReferencedObject |
| `hkContainerDebugAllocator::Allocator` | `0x19eed00` | `0x19eec90` | 13 | hkMemoryAllocator |
| `hkContainerHeapAllocator::Allocator` | `0x19eeda0` | `0x19eed30` | 13 | hkMemoryAllocator |
| `hkContainerTempAllocator::Allocator` | `0x19eec60` | `0x19eebf0` | 13 | hkMemoryAllocator |
| `hkDefaultBuiltinTypeRegistry` | `0x19f5560` | `0x19f5510` | 9 | hkBuiltinTypeRegistry |
| `hkDefaultClassNameRegistry` | `0x19f5650` | `0x19f55a0` | 14 | hkDynamicClassNameRegistry, hkSingleton<hkDefaultClassNameRegistry> |
| `hkDefaultError` | `0x19ef400` | `0x19ef3a0` | 11 | hkError |
| `hkDummySingleton` | `0x19ee950` | `0x19ee910` | 7 | hkReferencedObject, hkSingleton<hkDummySingleton> |
| `hkDynamicClassNameRegistry` | `0x19f5620` | `0x19f56a0` | 12 | hkClassNameRegistry |
| `hkErrStream` | `0x19ee860` | `0x19ee830` | 8 | hkOstream |
| `hkError` | `0x1909b70` |  |  | hkReferencedObject, hkSingleton<hkError> |
| `hkFileSystem` | `0x19ee9a0` |  |  | hkReferencedObject, hkSingleton<hkFileSystem> |
| `hkFileSystem::Iterator::Impl` | `0x19eeea0` |  |  | hkReferencedObject |
| `hkFixedSizeAllocator` | `0x19efcc0` | `0x19efc50` | 13 | hkMemoryAllocator |
| `hkFreeListAllocator` | `0x19eeb10` | `0x19ee9f0` | 23 | hkMemoryAllocator, hkMemoryAllocator::ExtendedInterface @+0x8 |
| `hkLargeBlockAllocator` | `0x19ee7e0` | `0x19ee6a0` | 22 | hkMemoryAllocator, hkMemoryAllocator::ExtendedInterface @+0x8 |
| `hkLargeBlockAllocator::FixedMemoryBlockServer` | `0x19ee7c0` | `0x19ee620` | 13 | hkMemoryAllocator |
| `hkLifoAllocator` | `0x19eef40` | `0x19eeed0` | 13 | hkMemoryAllocator |
| `hkMallocAllocator` | `0x19efae0` | `0x19efa70` | 13 | hkMemoryAllocator |
| `hkMemoryAllocator` | `0x19ee578` |  |  |  |
| `hkMemoryAllocator::ExtendedInterface` | `0x1908dd8` |  |  |  |
| `hkMemorySystem` | `0x19ee558` |  |  |  |
| `hkMoppBvTreeShapeBase` | `0x19f1bb0` | `0x19f1a40` | 22 | hkpBvTreeShape |
| `hkOrbisFileSystem` | `0x19eee20` | `0x19eedd0` | 12 | hkFileSystem |
| `hkOrbisStreamReader` | `0x19efbf0` | `0x19efb90` | 11 | hkSeekableStreamReader |
| `hkOrbisStreamWriter` | `0x19efb60` | `0x19efb10` | 12 | hkStreamWriter |
| `hkOstream` | `0x19ef6a0` | `0x19ef680` | 6 | hkReferencedObject |
| `hkReferencedObject` | `0x19ef030` | `0x19ef010` | 6 | hkBaseObject |
| `hkReferencedObjectLock` | `0x19ef090` | `0x19ef060` | 8 | hkReferencedObject, hkSingleton<hkReferencedObjectLock> |
| `hkRegisterCheckUtil` | `0x1a14230` | `0x1a14200` | 8 | hkReferencedObject, hkSingleton<hkRegisterCheckUtil> |
| `hkSeekableStreamReader` | `0x19ef190` |  |  | hkStreamReader |
| `hkSingleton<hkBuiltinTypeRegistry>` | `0x19f54e8` |  |  |  |
| `hkSingleton<hkDefaultClassNameRegistry>` | `0x19f5638` |  |  |  |
| `hkSingleton<hkDummySingleton>` | `0x19ee938` |  |  |  |
| `hkSingleton<hkError>` | `0x1909b58` |  |  |  |
| `hkSingleton<hkFileSystem>` | `0x19ee988` |  |  |  |
| `hkSingleton<hkReferencedObjectLock>` | `0x19ef080` |  |  |  |
| `hkSingleton<hkRegisterCheckUtil>` | `0x1a14220` |  |  |  |
| `hkSingleton<hkStackTracer>` | `0x19f00f8` |  |  |  |
| `hkSingleton<hkTypeInfoRegistry>` | `0x1909c08` |  |  |  |
| `hkSingleton<hkVtableClassRegistry>` | `0x19f5578` |  |  |  |
| `hkSolverAllocator` | `0x19eefe0` | `0x19eef70` | 13 | hkMemoryAllocator |
| `hkStackTracer` | `0x19f00c0` | `0x19f00a0` | 6 | hkReferencedObject, hkSingleton<hkStackTracer> |
| `hkStaticClassNameRegistry` | `0x19f5750` | `0x19f5710` | 7 | hkClassNameRegistry |
| `hkStatsAllocator` | `0x19ef650` | `0x19ef5e0` | 13 | hkMemoryAllocator |
| `hkStreamReader` | `0x19efc20` |  |  | hkReferencedObject |
| `hkStreamWriter` | `0x19ef230` |  |  | hkReferencedObject |
| `hkThreadMemory` | `0x19ef5b0` | `0x19ef540` | 16 | hkMemoryAllocator |
| `hkTypeInfoRegistry` | `0x1909c20` | `0x1909c90` | 9 | hkReferencedObject, hkSingleton<hkTypeInfoRegistry> |
| `hkVtableClassRegistry` | `0x1a141b0` | `0x1a14170` | 10 | hkReferencedObject, hkSingleton<hkVtableClassRegistry> |
| `hkWorldMemoryAvailableWatchDog` | `0x19087e0` |  |  | hkReferencedObject |
| `hkcdGsk::Cache` | `0x19f01f0` |  |  |  |
| `hkcdGskBase::RayCastShapeInterface<hkcdGsk_Vector4Shape>` | `0x19f5da0` | `0x19f5d80` | 3 | hkcdGskBase::ShapeInterface, hkcdGsk::Cache @+0x8 |
| `hkcdGskBase::ShapeInterface` | `0x19f01e0` |  |  |  |
| `hkcdShape` | `0x19f1000` | `0x19f5fe0` | 4 | hkReferencedObject |
| `hkgpAbstractMesh<hkgpConvexHullImpl::Edge, hkgpConvexHullImpl::Vertex, hkgpConvexHullImpl::Triangle, hkContainerHeapAllocator>` | `0x19f01b0` | `0x19f0180` | 5 | hkReferencedObject |
| `hkgpConvexHull` | `0x19f0150` | `0x19f0130` | 6 | hkReferencedObject |
| `hkp3AxisSweep` | `0x19f4a20` | `0x19f4920` | 34 | hkpBroadPhase |
| `hkpAabbCastCollector` | `0x19f0798` |  |  |  |
| `hkpAabbPhantom` | `0x19f6430` | `0x19f63b0` | 18 | hkpPhantom |
| `hkpAction` | `0x19fae70` | `0x1a15050` | 17 | hkReferencedObject |
| `hkpAllCdBodyPairCollector` | `0x19f28e0` | `0x19f28c0` | 6 | hkpCdBodyPairCollector |
| `hkpArrayAction` | `0x1a15020` | `0x1a14fd0` | 9 | hkpAction |
| `hkpBallAndSocketConstraintData` | `0x19f8e60` | `0x19f8da0` | 26 | hkpConstraintData |
| `hkpBoxBoxAgent` | `0x19f3c30` | `0x19f3bb0` | 15 | hkpIterativeLinearCastAgent |
| `hkpBoxMotion` | `0x19f6e90` | `0x19f6db0` | 30 | hkpMotion |
| `hkpBoxShape` | `0x19f16b0` | `0x19f1610` | 22 | hkpConvexShape |
| `hkpBreakableConstraintData` | `0x19f7f80` | `0x19f7ec0` | 26 | hkpConstraintData |
| `hkpBroadPhase` | `0x19f0ef0` | `0x19f0df0` | 34 | hkReferencedObject |
| `hkpBroadPhaseBorder` | `0x19f6750` | `0x19f6670` | 10 | hkReferencedObject, hkpWorldDeletionListener @+0x10, hkpPhantomOverlapListener @+0x18, hkpWorldPostSimulationListener @+0x20 |
| `hkpBroadPhaseBorderListener` | `0x19f7600` | `0x19f75a0` | 6 | hkReferencedObject, hkpBroadPhaseListener @+0x10 |
| `hkpBroadPhaseCastCollector` | `0x1948e28` |  |  |  |
| `hkpBroadPhaseListener` | `0x19f70e8` |  |  |  |
| `hkpBvAgent` | `0x19f3350` | `0x19f32d0` | 15 | hkpCollisionAgent |
| `hkpBvCompressedMeshAgent` | `0x19f25c0` | `0x19f2540` | 15 | hkpBvTreeAgent |
| `hkpBvCompressedMeshShape` | `0x19f0b30` | `0x19f0a10` | 26 | hkpBvTreeShape, hkpShapeContainer @+0x20 |
| `hkpBvTreeAgent` | `0x19f1940` | `0x19f1870` | 15 | hkpCollisionAgent |
| `hkpBvTreeAgent::LinearCastAabbCastCollector` | `0x19f1920` | `0x19f1900` | 3 | hkpAabbCastCollector |
| `hkpBvTreeShape` | `0x19f2770` | `0x19f26c0` | 21 | hkpShape |
| `hkpBvTreeStreamAgent` | `0x19f22a0` | `0x19f2220` | 15 | hkpCollisionAgent |
| `hkpCapsuleCapsuleAgent` | `0x19f41e0` | `0x19f4160` | 15 | hkpIterativeLinearCastAgent |
| `hkpCapsuleShape` | `0x19f2e20` | `0x19f2d80` | 22 | hkpConvexShape |
| `hkpCapsuleTriangleAgent` | `0x19f4510` | `0x19f4490` | 15 | hkpIterativeLinearCastAgent |
| `hkpCdBodyPairCollector` | `0x1909318` |  |  |  |
| `hkpCdPointCollector` | `0x1908740` |  |  |  |
| `hkpCharacterMotion` | `0x19f78b0` | `0x19f77d0` | 30 | hkpMotion |
| `hkpClosestCdPointCollector` | `0x19f3e80` | `0x19f3e60` | 6 | hkpCdPointCollector |
| `hkpClosestRayHitCollector` | `0x19f4010` | `0x19f3ff0` | 3 | hkpRayHitCollector |
| `hkpCollidableCollidableFilter` | `0x19f1278` |  |  |  |
| `hkpCollisionAgent` | `0x19f2b20` |  |  | hkReferencedObject |
| `hkpCollisionCallbackUtil` | `0x19f7380` | `0x19f72f0` | 8 | hkpWorldExtension, hkpConstraintListener @+0x20 |
| `hkpCollisionDispatcher` | `0x19f3fa0` | `0x19f3f80` | 6 | hkReferencedObject |
| `hkpCollisionFilter` | `0x19f3920` | `0x19f3810` | 11 | hkReferencedObject, hkpCollidableCollidableFilter @+0x10, hkpShapeCollectionFilter @+0x18, hkpRayShapeCollectionFilter @+0x20, hkpRayCollidableFilter @+0x28 |
| `hkpCompressedMeshShape` | `0x19f2af0` | `0x19f29d0` | 25 | hkpShapeCollection |
| `hkpConstraintData` | `0x19f8d70` |  |  | hkReferencedObject |
| `hkpConstraintInstance` | `0x19f7410` | `0x19f73d0` | 10 | hkReferencedObject |
| `hkpConstraintListener` | `0x19f6fc8` |  |  |  |
| `hkpConstraintMotor` | `0x19f8d30` | `0x19f9340` | 5 | hkReferencedObject |
| `hkpConstraintOwner` | `0x19f7980` |  |  | hkReferencedObject |
| `hkpConstraintUtils::CollectConstraintsFilter` | `0x19faeb8` |  |  |  |
| `hkpContactListener` | `0x1908b88` |  |  |  |
| `hkpContactMgr` | `0x19f3280` |  |  | hkReferencedObject |
| `hkpContactMgrFactory` | `0x19f7020` |  |  | hkReferencedObject |
| `hkpContinuousSimulation` | `0x19f68b0` | `0x19f67f0` | 23 | hkpSimulation |
| `hkpConvexListAgent` | `0x19f3120` | `0x19f30a0` | 15 | hkpPredGskfAgent |
| `hkpConvexListFilter` | `0x19f3fc0` |  |  | hkReferencedObject |
| `hkpConvexShape` | `0x19f1100` | `0x19f1060` | 22 | hkpSphereRepShape |
| `hkpConvexTransformShape` | `0x19f4690` | `0x19f45f0` | 22 | hkpConvexTransformShapeBase |
| `hkpConvexTransformShapeBase` | `0x1908f70` | `0x1908ed0` | 22 | hkpConvexShape |
| `hkpConvexTranslateShape` | `0x19f3f50` | `0x19f3eb0` | 22 | hkpConvexTransformShapeBase |
| `hkpConvexVerticesConnectivity` | `0x19f53f0` | `0x19f53c0` | 5 | hkReferencedObject |
| `hkpConvexVerticesShape` | `0x19f2d50` | `0x19f2cb0` | 22 | hkpConvexShape |
| `hkpCylinderShape` | `0x19f1370` | `0x19f12d0` | 22 | hkpConvexShape |
| `hkpDefaultConvexListFilter` | `0x19f5450` | `0x19f5420` | 5 | hkpConvexListFilter |
| `hkpDefaultToiResourceMgr` | `0x1a14de0` | `0x1a14d90` | 9 | hkpToiResourceMgr |
| `hkpDefaultWorldMaintenanceMgr` | `0x19f7bd0` | `0x19f7b90` | 7 | hkpWorldMaintenanceMgr |
| `hkpDeformableFixedConstraintData` | `0x19f8c70` | `0x19f8bb0` | 26 | hkpConstraintData |
| `hkpDynamicsContactMgr` | `0x19f7d50` |  |  | hkpContactMgr |
| `hkpEaseConstraintsAction` | `0x19fae50` | `0x19fae00` | 9 | hkpArrayAction |
| `hkpEaseConstraintsAction::CollectSupportedConstraints` | `0x19faed0` | `0x19faea0` | 5 | hkpConstraintUtils::CollectConstraintsFilter |
| `hkpEndOfStepCallbackUtil` | `0x19f7b40` | `0x19f7ae0` | 5 | hkReferencedObject, hkpWorldPostSimulationListener @+0x10 |
| `hkpEntity` | `0x19f6920` | `0x19f68e0` | 10 | hkpWorldObject |
| `hkpEntityEntityBroadPhaseListener` | `0x19f7550` | `0x19f74f0` | 6 | hkReferencedObject, hkpBroadPhaseListener @+0x10 |
| `hkpEntityListener` | `0x19490a8` |  |  |  |
| `hkpFixedBufferCdPointCollector` | `0x1908750` | `0x1908720` | 8 | hkpCdPointCollector |
| `hkpFixedConstraintData` | `0x19f8820` | `0x19f8760` | 26 | hkpConstraintData |
| `hkpFixedRigidMotion` | `0x19f7ab0` | `0x19f79b0` | 31 | hkpKeyframedRigidMotion |
| `hkpFlagCdBodyPairCollector` | `0x19f1ea0` | `0x19f1e80` | 6 | hkpCdBodyPairCollector |
| `hkpGskBaseAgent` | `0x19f5340` | `0x19f52c0` | 15 | hkpIterativeLinearCastAgent |
| `hkpGskfAgent` | `0x19f4fe0` | `0x19f4f60` | 15 | hkpGskBaseAgent |
| `hkpHingeConstraintData` | `0x19f9040` | `0x19f8f80` | 26 | hkpConstraintData |
| `hkpHingeLimitsData` | `0x19f8730` | `0x19f8670` | 26 | hkpConstraintData |
| `hkpIslandActivationListener` | `0x1909078` |  |  |  |
| `hkpIterativeLinearCastAgent` | `0x19f3650` |  |  | hkpCollisionAgent |
| `hkpKeyframedRigidMotion` | `0x19f6c70` | `0x19f6b80` | 32 | hkpMotion |
| `hkpLimitedForceConstraintMotor` | `0x19f8d50` | `0x19f9300` | 5 | hkpConstraintMotor |
| `hkpLimitedHingeConstraintData` | `0x19f8f50` | `0x19f8e90` | 26 | hkpConstraintData |
| `hkpListAgent` | `0x19f4ad0` | `0x19f4a50` | 15 | hkpCollisionAgent |
| `hkpListShape` | `0x19f3570` | `0x19f3450` | 26 | hkpShapeCollection |
| `hkpMalleableConstraintData` | `0x19f8070` | `0x19f7fb0` | 26 | hkpConstraintData |
| `hkpMapPointsToSubShapeContactMgr` | `0x19f32a0` | `0x19f3220` | 11 | hkpContactMgr |
| `hkpMaxSizeMotion` | `0x19f6b50` | `0x19f6a60` | 32 | hkpKeyframedRigidMotion |
| `hkpMoppAgent` | `0x19f1510` | `0x19f1490` | 15 | hkpBvTreeAgent |
| `hkpMoppBvTreeShape` | `0x19f1bd0` | `0x19f1b00` | 24 | hkMoppBvTreeShapeBase |
| `hkpMoppCode` | `0x19082e0` | `0x19082c0` | 6 | hkReferencedObject |
| `hkpMotion` | `0x19f72c0` | `0x19f71e0` | 30 | hkReferencedObject |
| `hkpMultiSphereAgent` | `0x19f4c50` | `0x19f4bd0` | 15 | hkpCollisionAgent |
| `hkpMultiSphereTriangleAgent` | `0x19f4dd0` | `0x19f4d50` | 15 | hkpIterativeLinearCastAgent |
| `hkpNullAgent` | `0x19f29a0` | `0x19f2920` | 15 | hkpCollisionAgent |
| `hkpNullBroadPhaseListener` | `0x1a14f80` | `0x1a14f20` | 6 | hkReferencedObject, hkpBroadPhaseListener @+0x10 |
| `hkpNullCollisionFilter` | `0x19f1260` | `0x19f1150` | 11 | hkpCollisionFilter |
| `hkpNullContactMgr` | `0x19f70d0` | `0x19f7070` | 11 | hkpContactMgr |
| `hkpNullContactMgrFactory` | `0x19f7040` | `0x19f6ff0` | 5 | hkpContactMgrFactory |
| `hkpPhantom` | `0x19f6f40` | `0x19f6ec0` | 18 | hkpWorldObject |
| `hkpPhantomAgent` | `0x19f4f30` | `0x19f4eb0` | 15 | hkpCollisionAgent |
| `hkpPhantomBroadPhaseListener` | `0x19f74a0` | `0x19f7440` | 6 | hkReferencedObject, hkpBroadPhaseListener @+0x10 |
| `hkpPhantomOverlapListener` | `0x19f67b8` |  |  |  |
| `hkpPointToPathConstraintData` | `0x19f8550` | `0x19f8490` | 26 | hkpConstraintData |
| `hkpPointToPlaneConstraintData` | `0x19f8a00` | `0x19f8940` | 26 | hkpConstraintData |
| `hkpPositionConstraintMotor` | `0x19f92d0` | `0x19f92a0` | 5 | hkpLimitedForceConstraintMotor |
| `hkpPredGskfAgent` | `0x19f3620` | `0x19f35a0` | 15 | hkpGskfAgent |
| `hkpPrismaticConstraintData` | `0x19f8b80` | `0x19f8ac0` | 26 | hkpConstraintData |
| `hkpPulleyConstraintData` | `0x19f8910` | `0x19f8850` | 26 | hkpConstraintData |
| `hkpRagdollConstraintData` | `0x19f8640` | `0x19f8580` | 26 | hkpConstraintData |
| `hkpRagdollLimitsData` | `0x19fabe0` | `0x19fab20` | 26 | hkpConstraintData |
| `hkpRayCollidableFilter` | `0x19f12a8` |  |  |  |
| `hkpRayHitCollector` | `0x1908598` |  |  |  |
| `hkpRayShapeCollectionFilter` | `0x19f1298` |  |  |  |
| `hkpReportContactMgr` | `0x19f7e70` | `0x19f7d90` | 20 | hkpDynamicsContactMgr |
| `hkpReportContactMgr::Factory` | `0x19f7e90` | `0x19f7e40` | 5 | hkpContactMgrFactory |
| `hkpRigidBody` | `0x19f77a0` | `0x19f7750` | 9 | hkpEntity |
| `hkpShape` | `0x19f1430` | `0x19f13a0` | 20 | hkpShapeBase |
| `hkpShapeBase` | `0x19f37e0` | `0x19f3760` | 15 | hkcdShape |
| `hkpShapeCollection` | `0x19f4810` | `0x19f4710` | 21 | hkpShape, hkpShapeContainer @+0x18 |
| `hkpShapeCollectionAgent` | `0x19f5130` | `0x19f50b0` | 15 | hkpCollisionAgent |
| `hkpShapeCollectionFilter` | `0x19f1288` |  |  |  |
| `hkpShapeContainer` | `0x19f0d60` |  |  |  |
| `hkpShapePhantom` | `0x19f65d0` | `0x19f6530` | 22 | hkpPhantom |
| `hkpSimpleClosestContactCollector` | `0x19f46e0` | `0x19f46c0` | 6 | hkpCdPointCollector |
| `hkpSimpleConstraintContactMgr` | `0x19f7d10` | `0x19f7c20` | 21 | hkpDynamicsContactMgr |
| `hkpSimpleConstraintContactMgr::Factory` | `0x19f7d30` | `0x19f7ce0` | 5 | hkpContactMgrFactory |
| `hkpSimpleContactConstraintData` | `0x19f7720` | `0x19f7650` | 28 | hkpConstraintData |
| `hkpSimpleShapePhantom` | `0x19f6500` | `0x19f6460` | 22 | hkpShapePhantom |
| `hkpSimpleWorldRayCaster` | `0x1a14e50` | `0x1a14e30` | 3 | hkpBroadPhaseCastCollector |
| `hkpSimulation` | `0x19f71b0` | `0x19f7110` | 22 | hkReferencedObject |
| `hkpSimulationIsland` | `0x19f7960` | `0x19f7920` | 10 | hkpConstraintOwner |
| `hkpSingleShapeContainer` | `0x19f0dc0` | `0x19f0d80` | 10 | hkpShapeContainer |
| `hkpSphereBoxAgent` | `0x19f4300` | `0x19f4280` | 15 | hkpIterativeLinearCastAgent |
| `hkpSphereCapsuleAgent` | `0x19f2fc0` | `0x19f2f40` | 15 | hkpIterativeLinearCastAgent |
| `hkpSphereMotion` | `0x19f6d80` | `0x19f6ca0` | 30 | hkpMotion |
| `hkpSphereRepShape` | `0x19f1120` | `0x19f5010` | 18 | hkpShape |
| `hkpSphereShape` | `0x19f2510` | `0x19f2470` | 22 | hkpConvexShape |
| `hkpSphereSphereAgent` | `0x19f48e0` | `0x19f4860` | 15 | hkpIterativeLinearCastAgent |
| `hkpSphereTriangleAgent` | `0x19f2bd0` | `0x19f2b50` | 15 | hkpIterativeLinearCastAgent |
| `hkpStaticCompoundAgent` | `0x19f1760` | `0x19f16e0` | 15 | hkpBvTreeAgent |
| `hkpStaticCompoundShape` | `0x19f06e0` | `0x19f05c0` | 26 | hkpBvTreeShape, hkpShapeContainer @+0x20 |
| `hkpStaticCompoundShape_Internals::AabbCastQuery::AabbCastCollectorWrapper` | `0x19f07b0` | `0x19f0780` | 5 | hkpAabbCastCollector |
| `hkpStiffSpringConstraintData` | `0x19f9440` | `0x19f9380` | 26 | hkpConstraintData |
| `hkpSymmetricAgent<hkpBvAgent>` | `0x19f3420` | `0x19f3380` | 15 | hkpSymmetricAgentLinearCast<hkpBvAgent> |
| `hkpSymmetricAgent<hkpBvCompressedMeshAgent>` | `0x19f2690` | `0x19f25f0` | 15 | hkpSymmetricAgentLinearCast<hkpBvCompressedMeshAgent> |
| `hkpSymmetricAgent<hkpBvTreeAgent>` | `0x19f1a10` | `0x19f1970` | 15 | hkpSymmetricAgentLinearCast<hkpBvTreeAgent> |
| `hkpSymmetricAgent<hkpBvTreeStreamAgent>` | `0x19f2440` | `0x19f23a0` | 15 | hkpSymmetricAgentLinearCast<hkpBvTreeStreamAgent> |
| `hkpSymmetricAgent<hkpConvexListAgent>` | `0x19f31f0` | `0x19f3150` | 15 | hkpSymmetricAgentLinearCast<hkpConvexListAgent> |
| `hkpSymmetricAgent<hkpListAgent>` | `0x19f4ba0` | `0x19f4b00` | 15 | hkpSymmetricAgentLinearCast<hkpListAgent> |
| `hkpSymmetricAgent<hkpMoppAgent>` | `0x19f15e0` | `0x19f1540` | 15 | hkpSymmetricAgentLinearCast<hkpMoppAgent> |
| `hkpSymmetricAgent<hkpMultiSphereAgent>` | `0x19f4d20` | `0x19f4c80` | 15 | hkpSymmetricAgentLinearCast<hkpMultiSphereAgent> |
| `hkpSymmetricAgent<hkpShapeCollectionAgent>` | `0x19f2370` | `0x19f22d0` | 15 | hkpSymmetricAgentLinearCast<hkpShapeCollectionAgent> |
| `hkpSymmetricAgent<hkpTransformAgent>` | `0x19f1e20` | `0x19f1d80` | 15 | hkpSymmetricAgentLinearCast<hkpTransformAgent> |
| `hkpSymmetricAgentFlipBodyCollector` | `0x19f2f10` | `0x19f2ef0` | 6 | hkpCdBodyPairCollector |
| `hkpSymmetricAgentFlipCastCollector` | `0x19f2ec0` | `0x19f2ea0` | 6 | hkpCdPointCollector |
| `hkpSymmetricAgentFlipCollector` | `0x19f2e70` | `0x19f2e50` | 6 | hkpCdPointCollector |
| `hkpSymmetricAgentLinearCast<hkpBvAgent>` | `0x19f3400` |  |  | hkpBvAgent |
| `hkpSymmetricAgentLinearCast<hkpBvCompressedMeshAgent>` | `0x19f2670` |  |  | hkpBvCompressedMeshAgent |
| `hkpSymmetricAgentLinearCast<hkpBvTreeAgent>` | `0x19f19f0` |  |  | hkpBvTreeAgent |
| `hkpSymmetricAgentLinearCast<hkpBvTreeStreamAgent>` | `0x19f2420` |  |  | hkpBvTreeStreamAgent |
| `hkpSymmetricAgentLinearCast<hkpCapsuleTriangleAgent>` | `0x19f45c0` | `0x19f4540` | 15 | hkpCapsuleTriangleAgent |
| `hkpSymmetricAgentLinearCast<hkpConvexListAgent>` | `0x19f31d0` |  |  | hkpConvexListAgent |
| `hkpSymmetricAgentLinearCast<hkpListAgent>` | `0x19f4b80` |  |  | hkpListAgent |
| `hkpSymmetricAgentLinearCast<hkpMoppAgent>` | `0x19f15c0` |  |  | hkpMoppAgent |
| `hkpSymmetricAgentLinearCast<hkpMultiSphereAgent>` | `0x19f4d00` |  |  | hkpMultiSphereAgent |
| `hkpSymmetricAgentLinearCast<hkpMultiSphereTriangleAgent>` | `0x19f4e80` | `0x19f4e00` | 15 | hkpMultiSphereTriangleAgent |
| `hkpSymmetricAgentLinearCast<hkpShapeCollectionAgent>` | `0x19f2350` |  |  | hkpShapeCollectionAgent |
| `hkpSymmetricAgentLinearCast<hkpSphereBoxAgent>` | `0x19f43b0` | `0x19f4330` | 15 | hkpSphereBoxAgent |
| `hkpSymmetricAgentLinearCast<hkpSphereCapsuleAgent>` | `0x19f3070` | `0x19f2ff0` | 15 | hkpSphereCapsuleAgent |
| `hkpSymmetricAgentLinearCast<hkpSphereTriangleAgent>` | `0x19f2c80` | `0x19f2c00` | 15 | hkpSphereTriangleAgent |
| `hkpSymmetricAgentLinearCast<hkpTransformAgent>` | `0x19f1e00` |  |  | hkpTransformAgent |
| `hkpThinBoxMotion` | `0x19f6a30` | `0x19f6950` | 30 | hkpBoxMotion |
| `hkpToiResourceMgr` | `0x1a14e00` |  |  | hkReferencedObject |
| `hkpTransformAgent` | `0x19f1d50` | `0x19f1cd0` | 15 | hkpCollisionAgent |
| `hkpTreeBroadPhase` | `0x19f0340` | `0x19f0240` | 34 | hkpBroadPhase |
| `hkpTriangleShape` | `0x19f1ca0` | `0x19f1c00` | 22 | hkpConvexShape |
| `hkpTriggerVolume` | `0x19fad90` | `0x19fac60` | 13 | hkReferencedObject, hkpContactListener @+0x10, hkpWorldPostSimulationListener @+0x18, hkpEntityListener @+0x20 |
| `hkpWheelConstraintData` | `0x19fa780` | `0x19fa6c0` | 26 | hkpConstraintData |
| `hkpWorld` | `0x19f6f90` | `0x19f6f70` | 6 | hkReferencedObject |
| `hkpWorldCinfo` | `0x1908ac0` | `0x1908aa0` | 6 | hkReferencedObject |
| `hkpWorldDeletionListener` | `0x19f67a8` |  |  |  |
| `hkpWorldExtension` | `0x19f6fb0` | `0x19f78e0` | 6 | hkReferencedObject |
| `hkpWorldLinearCaster` | `0x1a14ea0` | `0x1a14e80` | 3 | hkpBroadPhaseCastCollector |
| `hkpWorldMaintenanceMgr` | `0x19f7bf0` |  |  | hkReferencedObject |
| `hkpWorldObject` | `0x19f6640` | `0x19f6600` | 7 | hkReferencedObject |
| `hkpWorldPostSimulationListener` | `0x1908a68` |  |  |  |
| `hkpWorldRayCaster` | `0x1a14ef0` | `0x1a14ed0` | 3 | hkpBroadPhaseCastCollector |

<!-- /GENERATED -->

## Notes

_Hand-written findings for this folder go here; regeneration keeps everything outside the generated block._
