
void FUN_0062fec0(uint *param_1)

{
  long lVar1;
  long lVar2;
  int iVar3;
  ulong uVar4;
  long lVar5;
  uint uVar6;
  
  uVar6 = (int)*param_1 >> 0xd;
  lVar5 = (ulong)((uVar6 >> 0x12 | 0x3ff) & uVar6) * 0x40;
  lVar1 = *DAT_01a238a0;
  lVar2 = *(long *)(lVar1 + 0x10 + lVar5);
  uVar4 = (ulong)((*param_1 & 0x1fff) * *(int *)(lVar1 + 0x30 + lVar5));
  iVar3 = *(int *)(*(long *)(param_1 + 2) + 0x298 +
                  ((lVar2 + uVar4) -
                  ((long)*(int *)(lVar1 + 0x34 + lVar5) & *(ulong *)(lVar2 + 8 + uVar4))));
  if (iVar3 == -1) {
    iVar3 = FUN_0052ba70();
    if (iVar3 == -1) goto LAB_0062ff34;
  }
  FUN_0032ea00(param_1[0xb],iVar3,param_1[0xb]);
LAB_0062ff34:
  lVar1 = DAT_026be8a0;
  param_1[0xc1] = *(uint *)(DAT_026be8a0 + 0xc);
  *(uint *)(lVar1 + 0xc) = param_1[9];
  return;
}

