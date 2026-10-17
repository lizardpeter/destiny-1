
long FUN_0054c5f0(uint *param_1)

{
  long lVar1;
  uint uVar2;
  long lVar3;
  ulong uVar4;
  long lVar5;
  
  if (DAT_026b95a0 == 0) {
    uVar2 = (int)*param_1 >> 0xd;
    lVar3 = *DAT_01a238a0;
    lVar5 = (ulong)((uVar2 >> 0x12 | 0x3ff) & uVar2) * 0x40;
    lVar1 = *(long *)(lVar3 + 0x10 + lVar5);
    uVar4 = (ulong)((*param_1 & 0x1fff) * *(int *)(lVar3 + 0x30 + lVar5));
    DAT_026b95a0 = (lVar1 + uVar4) -
                   ((long)*(int *)(lVar3 + 0x34 + lVar5) & *(ulong *)(lVar1 + 8 + uVar4));
  }
  if (DAT_026b9710 == 0) {
    uVar2 = (int)*(uint *)(DAT_026b95a0 + 0x310) >> 0xd;
    lVar3 = *DAT_01a238a0;
    lVar5 = (ulong)((uVar2 >> 0x12 | 0x3ff) & uVar2) * 0x40;
    lVar1 = *(long *)(lVar3 + 0x10 + lVar5);
    uVar4 = (ulong)((*(uint *)(DAT_026b95a0 + 0x310) & 0x1fff) * *(int *)(lVar3 + 0x30 + lVar5));
    DAT_026b9710 = (lVar1 + uVar4) -
                   ((long)*(int *)(lVar3 + 0x34 + lVar5) & *(ulong *)(lVar1 + 8 + uVar4));
  }
  lVar3 = DAT_026b9710 + 8;
  if (DAT_026b9710 == 0) {
    lVar3 = 0;
  }
  return lVar3;
}

