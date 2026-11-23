
undefined4 FUN_00108470(uint *param_1)

{
  long lVar1;
  undefined4 uVar2;
  ulong uVar3;
  long lVar4;
  long lVar5;
  uint uVar6;
  
  uVar6 = (int)*param_1 >> 0xd;
  lVar5 = (ulong)((uVar6 >> 0x12 | 0x3ff) & uVar6) * 0x40;
  lVar4 = *DAT_01a238a0;
  lVar1 = *(long *)(lVar4 + 0x10 + lVar5);
  uVar3 = (ulong)((*param_1 & 0x1fff) * *(int *)(lVar4 + 0x30 + lVar5));
  lVar4 = FUN_001073f0(*(long *)(param_1 + 2) + 0x40 +
                       ((lVar1 + uVar3) -
                       ((long)*(int *)(lVar4 + 0x34 + lVar5) & *(ulong *)(lVar1 + 8 + uVar3))));
  uVar2 = 0xffffffff;
  if (lVar4 != 0) {
    uVar2 = *(undefined4 *)(lVar4 + 0xd9c);
  }
  return uVar2;
}

