
void FUN_00bc3450(undefined8 param_1,undefined4 *param_2,undefined4 param_3)

{
  long lVar1;
  undefined4 uVar2;
  uint uVar3;
  ulong uVar4;
  undefined4 extraout_EDX;
  undefined4 extraout_var;
  long lVar5;
  long lVar6;
  
  uVar2 = FUN_00ba7f80(param_3);
  uVar3 = FUN_00105e80(uVar2);
  lVar5 = *DAT_01a238a0;
  lVar6 = (ulong)(((uint)((int)uVar3 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar3 >> 0xd) * 0x40;
  lVar1 = *(long *)(lVar5 + 0x10 + lVar6);
  uVar4 = (ulong)((uVar3 & 0x1fff) * *(int *)(lVar5 + 0x30 + lVar6));
  lVar5 = (lVar1 + uVar4) - ((long)*(int *)(lVar5 + 0x34 + lVar6) & *(ulong *)(lVar1 + 8 + uVar4));
  *param_2 = *(undefined4 *)(CONCAT44(extraout_var,extraout_EDX) + 0x250 + lVar5);
  param_2[1] = *(undefined4 *)(CONCAT44(extraout_var,extraout_EDX) + 0x254 + lVar5);
  return;
}

