
ulong FUN_00640160(int param_1)

{
  short *psVar1;
  long lVar2;
  long lVar3;
  long *plVar4;
  uint *puVar5;
  uint uVar6;
  int iVar7;
  undefined8 uVar8;
  ulong uVar9;
  long lVar10;
  undefined1 local_138 [256];
  long local_38;
  
  puVar5 = DAT_026bea70;
  plVar4 = DAT_01a1f100;
  local_38 = *DAT_01a1f100;
  uVar6 = *DAT_026bea70;
  if (uVar6 == 0xffffffff) {
    uVar8 = FUN_00346d20();
    FUN_010156f0(local_138,s_gear_manager_combined_request_01643dc1);
    uVar6 = FUN_00349c50(uVar8,3,1,param_1,local_138);
    *puVar5 = uVar6;
    uVar9 = 0xffffffff;
    if (uVar6 == 0xffffffff) goto LAB_00640340;
    lVar10 = (ulong)(((uint)((int)uVar6 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar6 >> 0xd) * 0x40;
    lVar2 = *DAT_01a238a0;
    lVar3 = *(long *)(lVar2 + 0x10 + lVar10);
    uVar9 = (ulong)((uVar6 & 0x1fff) * *(int *)(lVar2 + 0x30 + lVar10));
    psVar1 = (short *)(((lVar3 + uVar9) -
                       ((long)*(int *)(lVar2 + 0x34 + lVar10) & *(ulong *)(lVar3 + 8 + uVar9))) +
                      0x40);
    *psVar1 = *psVar1 + 1;
    *(undefined1 *)(puVar5 + 1) = 1;
  }
  else {
    lVar10 = (ulong)(((uint)((int)uVar6 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar6 >> 0xd) * 0x40;
    lVar2 = *DAT_01a238a0;
    lVar3 = *(long *)(lVar2 + 0x10 + lVar10);
    uVar9 = (ulong)((uVar6 & 0x1fff) * *(int *)(lVar2 + 0x30 + lVar10));
    iVar7 = FUN_00346c90((lVar3 + uVar9) -
                         ((long)*(int *)(lVar2 + 0x34 + lVar10) & *(ulong *)(lVar3 + 8 + uVar9)));
    uVar9 = 0xffffffff;
    if (0 < iVar7) goto LAB_00640340;
    uVar6 = (int)*puVar5 >> 0xd;
    lVar2 = *DAT_01a238a0;
    lVar10 = (ulong)((uVar6 >> 0x12 | 0x3ff) & uVar6) * 0x40;
    lVar3 = *(long *)(lVar2 + 0x10 + lVar10);
    uVar9 = (ulong)((*puVar5 & 0x1fff) * *(int *)(lVar2 + 0x30 + lVar10));
    if (*(char *)(((lVar3 + uVar9) -
                  ((long)*(int *)(lVar2 + 0x34 + lVar10) & *(ulong *)(lVar3 + 8 + uVar9))) + 4) <
        param_1) {
      uVar8 = FUN_00346d20();
      FUN_0034a120(uVar8,*puVar5,param_1);
    }
  }
  uVar6 = *puVar5;
  uVar9 = 0xffffffff;
  if (uVar6 != 0xffffffff) {
    lVar10 = (ulong)(((uint)((int)uVar6 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar6 >> 0xd) * 0x40;
    lVar2 = *DAT_01a238a0;
    lVar3 = *(long *)(lVar2 + 0x10 + lVar10);
    uVar9 = (ulong)((uVar6 & 0x1fff) * *(int *)(lVar2 + 0x30 + lVar10));
    psVar1 = (short *)(((lVar3 + uVar9) -
                       ((long)*(int *)(lVar2 + 0x34 + lVar10) & *(ulong *)(lVar3 + 8 + uVar9))) +
                      0x40);
    *psVar1 = *psVar1 + 1;
    uVar9 = (ulong)uVar6;
  }
LAB_00640340:
  if (*plVar4 == local_38) {
    return uVar9;
  }
  uVar9 = thunk_FUN_012aa7f6();
  return uVar9;
}

