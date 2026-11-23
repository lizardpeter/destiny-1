
bool FUN_00bc3c00(undefined8 param_1,undefined4 param_2,undefined8 param_3,undefined8 param_4,
                 undefined8 param_5,undefined8 param_6)

{
  long lVar1;
  long lVar2;
  undefined4 uVar3;
  uint uVar4;
  ulong uVar5;
  long lVar6;
  undefined1 auVar7 [16];
  
  uVar3 = FUN_00ba7f80(param_2);
  auVar7 = FUN_00105e80(uVar3);
  uVar4 = auVar7._0_4_;
  if (uVar4 != 0xffffffff) {
    lVar6 = (ulong)(((uint)((int)uVar4 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar4 >> 0xd) * 0x40;
    lVar1 = *DAT_01a238a0;
    lVar2 = *(long *)(lVar1 + 0x10 + lVar6);
    uVar5 = (ulong)((uVar4 & 0x1fff) * *(int *)(lVar1 + 0x30 + lVar6));
    lVar1 = auVar7._8_8_ + 0x250 +
            ((lVar2 + uVar5) -
            ((long)*(int *)(lVar1 + 0x34 + lVar6) & *(ulong *)(lVar2 + 8 + uVar5)));
    FUN_002c9610(*(undefined4 *)PTR_DAT_0191a858,param_5,param_3,0,lVar1,lVar1,param_6);
  }
  return uVar4 != 0xffffffff;
}

