
void FUN_007e0430(long param_1)

{
  long lVar1;
  float fVar2;
  undefined1 auVar3 [16];
  undefined1 auVar4 [16];
  
  fVar2 = *(float *)(&DAT_0000258c + param_1) - *(float *)(&DAT_00002588 + param_1);
  auVar3._0_4_ = DAT_0165fea0 / fVar2;
  auVar3._4_12_ = SUB6012((undefined1  [60])0x0,0);
  auVar4._0_4_ = *(float *)(&DAT_00002588 + param_1) / fVar2;
  auVar4._4_12_ = SUB6012((undefined1  [60])0x0,0);
  lVar1 = *(long *)(param_1 + 0x50);
  FUN_00f8f4b0(auVar3._0_8_,auVar4._0_8_,lVar1,*(undefined4 *)(param_1 + 0x2578),
               *(undefined4 *)(param_1 + 0x257c),*(undefined4 *)(param_1 + 0x2580),
               *(undefined4 *)(&DAT_00002584 + param_1));
  FUN_00f7e740(lVar1,*(undefined4 *)
                      (&DAT_015d16e0 + (ulong)*(uint *)(FUN_000025b0 + param_1 + 4) * 0x24));
  FUN_00f7e7c0(lVar1,0,*(undefined4 *)(param_1 + 0x25d8));
  FUN_00f7e7c0(lVar1,1,*(undefined4 *)(param_1 + 0x25d8));
  FUN_00f7e7c0(lVar1,2,*(undefined4 *)(param_1 + 0x25d8));
  FUN_00f7e7c0(lVar1,3,*(undefined4 *)(param_1 + 0x25d8));
  FUN_00f7e950(lVar1,*(undefined4 *)(param_1 + 0x25dc));
  FUN_00f8f0e0(lVar1,0,param_1 + 0x26e4);
  FUN_00f8f0e0(lVar1,1,param_1 + 10000);
  FUN_00f8f0e0(lVar1,2,param_1 + 0x273c);
  FUN_00f8f0e0(lVar1,3,param_1 + 0x2768);
  FUN_00f8f0e0(lVar1,4,param_1 + 0x2794);
  FUN_00f7eec0(lVar1,param_1 + 0x26b0);
  *(undefined8 *)(param_1 + 0x1d28) = 1;
  *(undefined8 *)(param_1 + 0x1d30) = 1;
  FUN_00f8b790(lVar1 + 0xc0,0,0,0);
  FUN_00f8b8c0(lVar1 + 0xc0,0);
  *(undefined4 *)(*(long *)(param_1 + 0x50) + 0x3a8) = *(undefined4 *)(FUN_000025f0 + param_1);
  FUN_00f7fe20();
  return;
}

