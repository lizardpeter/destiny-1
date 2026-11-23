
void FUN_00910380(long param_1,int *param_2,int *param_3)

{
  char cVar1;
  int iVar2;
  int iVar3;
  undefined8 uVar4;
  long lVar5;
  ulong uVar6;
  undefined4 *puVar7;
  long lVar8;
  ushort uVar9;
  long extraout_RDX;
  uint uVar10;
  bool bVar11;
  undefined4 local_40 [2];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  lVar8 = *(long *)(PTR_DAT_019b1b90 + 8);
  uVar4 = FUN_000e8680(lVar8,0,0xffffffff);
  thunk_FUN_012aa986(param_3,0,uVar4);
  uVar9 = *(ushort *)(lVar8 + 0x1c) & 0x78;
  bVar11 = uVar9 != 0;
  if (uVar9 == 0) {
    uVar10 = *(uint *)(lVar8 + 0x20);
    if ((*(ushort *)(lVar8 + 0x1c) & 0x40) != 0) {
      if ((param_3 == (int *)0x0) || (lVar5 = FUN_000e8a90(lVar8,param_3), lVar5 == 0)) {
        uVar10 = uVar10 | 0x5488bf;
      }
      else {
        uVar10 = uVar10 | *(uint *)(lVar5 + 0x20) & 0x5488bf;
      }
    }
    bVar11 = (uVar10 & 0xc08070) != 0;
  }
  if (bVar11) {
    FUN_000e6730(lVar8,param_3,0,0xffffffff,0);
  }
  uVar4 = FUN_005494c0();
  FUN_0054b0c0(uVar4);
  bVar11 = *param_2 != -1;
  if (bVar11) {
    *param_3 = *param_2;
  }
  uVar6 = (ulong)bVar11;
  if (param_2[1] != -1) {
    param_3[uVar6] = param_2[1];
    uVar6 = (ulong)(bVar11 + 1);
  }
  uVar10 = (uint)uVar6;
  if ((param_2[2] != -1) && (uVar10 < 6)) {
    param_3[(int)uVar10] = param_2[2];
    uVar10 = uVar10 + 1;
  }
  if ((param_2[3] != -1) && (uVar10 < 6)) {
    param_3[(int)uVar10] = param_2[3];
    uVar10 = uVar10 + 1;
  }
  if ((param_2[4] != -1) && (uVar10 < 6)) {
    param_3[(int)uVar10] = param_2[4];
    uVar10 = uVar10 + 1;
  }
  if ((param_2[5] != -1) && (uVar10 < 6)) {
    param_3[(int)uVar10] = param_2[5];
    uVar10 = uVar10 + 1;
  }
  if ((param_2[6] != -1) && (uVar10 < 6)) {
    param_3[(int)uVar10] = param_2[6];
    uVar10 = uVar10 + 1;
  }
  if ((param_2[7] != -1) && (uVar10 < 6)) {
    param_3[(int)uVar10] = param_2[7];
  }
  cVar1 = *(char *)(extraout_RDX + 8);
  uVar4 = FUN_005494c0();
  iVar3 = -1;
  iVar2 = -1;
  if (cVar1 != -1) {
    lVar8 = 0;
    do {
      if (*(char *)(param_1 + 0x28 + lVar8 * 4) == cVar1) {
        puVar7 = (undefined4 *)FUN_0054c6b0(uVar4,*(undefined2 *)(param_1 + 0x2a + lVar8 * 4));
        iVar2 = -1;
        if (puVar7 != (undefined4 *)0x0) {
          uVar4 = FUN_0033fa20();
          local_40[0] = *puVar7;
          iVar2 = FUN_0033fc20(uVar4,local_40);
        }
        goto LAB_0091057b;
      }
      lVar8 = lVar8 + 1;
    } while ((int)lVar8 < 6);
    iVar2 = -1;
  }
LAB_0091057b:
  param_3[6] = iVar2;
  cVar1 = *(char *)(extraout_RDX + 9);
  uVar4 = FUN_005494c0();
  if (cVar1 != -1) {
    lVar8 = 0;
    do {
      if (*(char *)(param_1 + 0x28 + lVar8 * 4) == cVar1) {
        puVar7 = (undefined4 *)FUN_0054c6b0(uVar4,*(undefined2 *)(param_1 + 0x2a + lVar8 * 4));
        if (puVar7 != (undefined4 *)0x0) {
          uVar4 = FUN_0033fa20();
          local_40[0] = *puVar7;
          iVar3 = FUN_0033fc20(uVar4,local_40);
        }
        break;
      }
      lVar8 = lVar8 + 1;
    } while ((int)lVar8 < 6);
  }
  param_3[7] = iVar3;
  cVar1 = *(char *)(extraout_RDX + 10);
  uVar4 = FUN_005494c0();
  iVar3 = -1;
  iVar2 = -1;
  if (cVar1 != -1) {
    lVar8 = 0;
    do {
      if (*(char *)(param_1 + 0x28 + lVar8 * 4) == cVar1) {
        puVar7 = (undefined4 *)FUN_0054c6b0(uVar4,*(undefined2 *)(param_1 + 0x2a + lVar8 * 4));
        iVar2 = -1;
        if (puVar7 != (undefined4 *)0x0) {
          uVar4 = FUN_0033fa20();
          local_40[0] = *puVar7;
          iVar2 = FUN_0033fc20(uVar4,local_40);
        }
        goto LAB_0091065b;
      }
      lVar8 = lVar8 + 1;
    } while ((int)lVar8 < 6);
    iVar2 = -1;
  }
LAB_0091065b:
  param_3[8] = iVar2;
  cVar1 = *(char *)(extraout_RDX + 0xb);
  uVar4 = FUN_005494c0();
  if (cVar1 != -1) {
    lVar8 = 0;
    do {
      if (*(char *)(param_1 + 0x28 + lVar8 * 4) == cVar1) {
        puVar7 = (undefined4 *)FUN_0054c6b0(uVar4,*(undefined2 *)(param_1 + 0x2a + lVar8 * 4));
        if (puVar7 != (undefined4 *)0x0) {
          uVar4 = FUN_0033fa20();
          local_40[0] = *puVar7;
          iVar3 = FUN_0033fc20(uVar4,local_40);
        }
        break;
      }
      lVar8 = lVar8 + 1;
    } while ((int)lVar8 < 6);
  }
  param_3[9] = iVar3;
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

