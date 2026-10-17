
void FUN_009109b0(long param_1,int *param_2,int *param_3)

{
  char cVar1;
  int iVar2;
  int iVar3;
  undefined8 uVar4;
  long lVar5;
  undefined4 *puVar6;
  long lVar7;
  ushort uVar8;
  long extraout_RDX;
  uint uVar9;
  bool bVar10;
  undefined4 local_40 [2];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  lVar7 = *(long *)(PTR_DAT_019b1b50 + 8);
  uVar4 = FUN_000e8680(lVar7,0,0xffffffff);
  thunk_FUN_012aa986(param_3,0,uVar4);
  uVar8 = *(ushort *)(lVar7 + 0x1c) & 0x78;
  bVar10 = uVar8 != 0;
  if (uVar8 == 0) {
    uVar9 = *(uint *)(lVar7 + 0x20);
    if ((*(ushort *)(lVar7 + 0x1c) & 0x40) != 0) {
      if ((param_3 == (int *)0x0) || (lVar5 = FUN_000e8a90(lVar7,param_3), lVar5 == 0)) {
        uVar9 = uVar9 | 0x5488bf;
      }
      else {
        uVar9 = uVar9 | *(uint *)(lVar5 + 0x20) & 0x5488bf;
      }
    }
    bVar10 = (uVar9 & 0xc08070) != 0;
  }
  if (bVar10) {
    FUN_000e6730(lVar7,param_3,0,0xffffffff,0);
  }
  uVar4 = FUN_005494c0();
  FUN_0054b0c0(uVar4);
  if (*param_2 != -1) {
    *param_3 = *param_2;
  }
  if (param_2[1] != -1) {
    param_3[1] = param_2[1];
  }
  if (param_2[2] != -1) {
    param_3[2] = param_2[2];
  }
  if (param_2[3] != -1) {
    param_3[3] = param_2[3];
  }
  if (param_2[4] != -1) {
    param_3[4] = param_2[4];
  }
  if (param_2[5] != -1) {
    param_3[5] = param_2[5];
  }
  if (param_2[6] != -1) {
    param_3[6] = param_2[6];
  }
  cVar1 = *(char *)(extraout_RDX + 5);
  uVar4 = FUN_005494c0();
  iVar2 = -1;
  iVar3 = -1;
  if (cVar1 != -1) {
    lVar7 = 0;
    do {
      if (*(char *)(param_1 + 0x28 + lVar7 * 4) == cVar1) {
        puVar6 = (undefined4 *)FUN_0054c6b0(uVar4,*(undefined2 *)(param_1 + 0x2a + lVar7 * 4));
        iVar3 = -1;
        if (puVar6 != (undefined4 *)0x0) {
          uVar4 = FUN_0033fa20();
          local_40[0] = *puVar6;
          iVar3 = FUN_0033fc20(uVar4,local_40);
        }
        goto LAB_00910b4b;
      }
      lVar7 = lVar7 + 1;
    } while ((int)lVar7 < 6);
    iVar3 = -1;
  }
LAB_00910b4b:
  param_3[7] = iVar3;
  cVar1 = *(char *)(extraout_RDX + 6);
  uVar4 = FUN_005494c0();
  if (cVar1 != -1) {
    lVar7 = 0;
    do {
      if (*(char *)(param_1 + 0x28 + lVar7 * 4) == cVar1) {
        puVar6 = (undefined4 *)FUN_0054c6b0(uVar4,*(undefined2 *)(param_1 + 0x2a + lVar7 * 4));
        if (puVar6 != (undefined4 *)0x0) {
          uVar4 = FUN_0033fa20();
          local_40[0] = *puVar6;
          iVar2 = FUN_0033fc20(uVar4,local_40);
        }
        break;
      }
      lVar7 = lVar7 + 1;
    } while ((int)lVar7 < 6);
  }
  param_3[8] = iVar2;
  cVar1 = *(char *)(extraout_RDX + 7);
  uVar4 = FUN_005494c0();
  iVar3 = -1;
  if (cVar1 != -1) {
    lVar7 = 0;
    do {
      if (*(char *)(param_1 + 0x28 + lVar7 * 4) == cVar1) {
        puVar6 = (undefined4 *)FUN_0054c6b0(uVar4,*(undefined2 *)(param_1 + 0x2a + lVar7 * 4));
        if (puVar6 != (undefined4 *)0x0) {
          uVar4 = FUN_0033fa20();
          local_40[0] = *puVar6;
          iVar3 = FUN_0033fc20(uVar4,local_40);
        }
        break;
      }
      lVar7 = lVar7 + 1;
    } while ((int)lVar7 < 6);
  }
  param_3[9] = iVar3;
  param_3[10] = *(int *)(param_1 + 0x20);
  param_3[0xb] = (int)(float)*(int *)(param_1 + 0x24);
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

