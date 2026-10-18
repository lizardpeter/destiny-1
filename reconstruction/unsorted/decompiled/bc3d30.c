
undefined8
FUN_00bc3d30(undefined8 param_1,long param_2,undefined8 param_3,undefined8 param_4,
            undefined8 param_5)

{
  long lVar1;
  long lVar2;
  undefined4 uVar3;
  uint uVar4;
  undefined8 in_RAX;
  ulong uVar5;
  long lVar6;
  long extraout_RDX;
  uint uVar7;
  
  uVar7 = (uint)((ulong)in_RAX >> 0x20);
  uVar3 = FUN_00ba7f80(*(undefined4 *)(param_2 + 4));
  uVar4 = FUN_00105e80(uVar3);
  lVar6 = (ulong)(((uint)((int)uVar4 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar4 >> 0xd) * 0x40;
  lVar1 = *DAT_01a238a0;
  lVar2 = *(long *)(lVar1 + 0x10 + lVar6);
  uVar5 = (ulong)((uVar4 & 0x1fff) * *(int *)(lVar1 + 0x30 + lVar6));
  FUN_002c9520(*(undefined4 *)PTR_DAT_0191a858,
               extraout_RDX + 0x250 +
               ((lVar2 + uVar5) -
               ((long)*(int *)(lVar1 + 0x34 + lVar6) & *(ulong *)(lVar2 + 8 + uVar5))),0,param_5,
               param_5,param_3,(ulong)uVar7 << 0x20);
  return 1;
}

