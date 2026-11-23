
void FUN_00344bd0(long param_1)

{
  uint uVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  int iVar4;
  ulong uVar5;
  long lVar6;
  undefined4 *puVar7;
  long lVar8;
  uint uVar9;
  long lVar10;
  long lVar11;
  undefined4 local_40 [2];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  if (*(int *)(&DAT_00002114 + *(long *)(param_1 + 8)) != -1) {
    puVar7 = (undefined4 *)(&DAT_00002114 + *(long *)(param_1 + 8));
    uVar2 = FUN_0012d700(puVar7);
    FUN_00836520(uVar2);
    uVar2 = FUN_0012d700(puVar7);
    FUN_0083fae0(uVar2);
    uVar2 = FUN_0012d700(puVar7);
    FUN_007d76d0(uVar2);
    uVar2 = FUN_00240880();
    uVar3 = FUN_00240840();
    local_40[0] = *puVar7;
    lVar10 = *(long *)(param_1 + 8);
    iVar4 = FUN_00057e60(local_40);
    uVar1 = *(uint *)(lVar10 + 0x10 + (long)iVar4 * 0x10);
    uVar9 = (int)uVar1 >> 0xd;
    lVar11 = *DAT_01a238a0;
    lVar8 = (ulong)((uVar9 >> 0x12 | 0x3ff) & uVar9) * 0x40;
    lVar6 = *(long *)(lVar11 + 0x10 + lVar8);
    uVar5 = (ulong)((uVar1 & 0x1fff) * *(int *)(lVar11 + 0x30 + lVar8));
    uVar1 = *(uint *)(*(long *)(lVar10 + 0x18 + (long)iVar4 * 0x10) + 0x18 +
                     ((lVar6 + uVar5) -
                     ((long)*(int *)(lVar11 + 0x34 + lVar8) & *(ulong *)(lVar6 + 8 + uVar5))));
    uVar9 = (int)uVar1 >> 0xd;
    lVar6 = (ulong)((uVar9 >> 0x12 | 0x3ff) & uVar9) * 0x40;
    lVar10 = *(long *)(lVar11 + 0x10 + lVar6);
    uVar5 = (ulong)((uVar1 & 0x1fff) * *(int *)(lVar11 + 0x30 + lVar6));
    uVar1 = *(uint *)(((lVar10 + uVar5) -
                      ((long)*(int *)(lVar11 + 0x34 + lVar6) & *(ulong *)(lVar10 + 8 + uVar5))) +
                     0x1c);
    uVar9 = (int)uVar1 >> 0xd;
    lVar6 = (ulong)((uVar9 >> 0x12 | 0x3ff) & uVar9) * 0x40;
    lVar10 = *(long *)(lVar11 + 0x10 + lVar6);
    uVar5 = (ulong)((uVar1 & 0x1fff) * *(int *)(lVar11 + 0x30 + lVar6));
    lVar10 = (lVar10 + uVar5) -
             ((long)*(int *)(lVar11 + 0x34 + lVar6) & *(ulong *)(lVar10 + 8 + uVar5));
    if (0 < *(long *)(lVar10 + 8)) {
      lVar11 = 0;
      do {
        FUN_00106df0(*(undefined4 *)(*(long *)(lVar10 + 0x10) + lVar10 + 0x20 + lVar11 * 4),uVar2);
        lVar11 = lVar11 + 1;
      } while (lVar11 < *(long *)(lVar10 + 8));
    }
    if (0 < *(long *)(lVar10 + 0x18)) {
      lVar11 = 0;
      do {
        FUN_00106df0(*(undefined4 *)(*(long *)(lVar10 + 0x20) + lVar10 + 0x30 + lVar11 * 4),uVar3);
        lVar11 = lVar11 + 1;
      } while (lVar11 < *(long *)(lVar10 + 0x18));
    }
    if (0 < *(long *)(lVar10 + 0x28)) {
      lVar11 = 0;
      do {
        FUN_00106df0(*(undefined4 *)(*(long *)(lVar10 + 0x30) + lVar10 + 0x40 + lVar11 * 4),uVar2);
        lVar11 = lVar11 + 1;
      } while (lVar11 < *(long *)(lVar10 + 0x28));
    }
  }
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

