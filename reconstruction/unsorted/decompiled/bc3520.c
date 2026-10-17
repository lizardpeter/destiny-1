
undefined8 FUN_00bc3520(undefined8 param_1,undefined4 param_2)

{
  long lVar1;
  long lVar2;
  undefined4 uVar3;
  uint uVar4;
  ulong uVar5;
  long lVar6;
  bool bVar7;
  undefined1 auVar8 [16];
  
  uVar3 = FUN_00ba7f80(param_2);
  auVar8 = FUN_00105e80(uVar3);
  uVar5 = auVar8._0_8_;
  bVar7 = false;
  uVar4 = auVar8._0_4_;
  if (uVar4 != 0xffffffff) {
    lVar6 = (ulong)(((uint)((int)uVar4 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar4 >> 0xd) * 0x40;
    lVar1 = *DAT_01a238a0;
    lVar2 = *(long *)(lVar1 + 0x10 + lVar6);
    uVar5 = (ulong)((uVar4 & 0x1fff) * *(int *)(lVar1 + 0x30 + lVar6));
    bVar7 = ((lVar2 + uVar5) -
            ((long)*(int *)(lVar1 + 0x34 + lVar6) & *(ulong *)(lVar2 + 8 + uVar5))) + auVar8._8_8_
            != 0;
  }
  return CONCAT71((int7)(uVar5 >> 8),bVar7);
}

