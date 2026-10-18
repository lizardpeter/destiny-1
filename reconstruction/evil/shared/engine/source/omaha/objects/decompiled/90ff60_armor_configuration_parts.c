
void FUN_0090ff60(long param_1,long param_2,undefined4 *param_3,undefined4 *param_4)

{
  long lVar1;
  char cVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  undefined8 uVar5;
  undefined4 *puVar6;
  long lVar7;
  char *extraout_RDX;
  undefined4 local_40 [2];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  uVar5 = FUN_005494c0();
  FUN_0054b0c0(uVar5);
  lVar7 = 0;
  do {
    if (7 < (int)lVar7) break;
    *param_4 = *(undefined4 *)(param_1 + lVar7 * 4);
    lVar1 = lVar7 * 4;
    lVar7 = lVar7 + 1;
  } while (*(int *)(param_1 + lVar1) == -1);
  if (param_3 != (undefined4 *)0x0) {
    param_4[1] = *param_3;
    param_4[2] = (float)(int)param_3[1];
  }
  cVar2 = *extraout_RDX;
  uVar5 = FUN_005494c0();
  uVar3 = 0xffffffff;
  uVar4 = 0xffffffff;
  if (cVar2 != -1) {
    lVar7 = 0;
    do {
      if (*(char *)(param_2 + lVar7 * 4) == cVar2) {
        puVar6 = (undefined4 *)FUN_0054c6b0(uVar5,*(undefined2 *)(param_2 + 2 + lVar7 * 4));
        uVar4 = 0xffffffff;
        if (puVar6 != (undefined4 *)0x0) {
          uVar5 = FUN_0033fa20();
          local_40[0] = *puVar6;
          uVar4 = FUN_0033fc20(uVar5,local_40);
        }
        goto LAB_00910039;
      }
      lVar7 = lVar7 + 1;
    } while ((int)lVar7 < 6);
    uVar4 = 0xffffffff;
  }
LAB_00910039:
  param_4[3] = uVar4;
  cVar2 = extraout_RDX[1];
  uVar5 = FUN_005494c0();
  if (cVar2 != -1) {
    lVar7 = 0;
    do {
      if (*(char *)(param_2 + lVar7 * 4) == cVar2) {
        puVar6 = (undefined4 *)FUN_0054c6b0(uVar5,*(undefined2 *)(param_2 + 2 + lVar7 * 4));
        if (puVar6 != (undefined4 *)0x0) {
          uVar5 = FUN_0033fa20();
          local_40[0] = *puVar6;
          uVar3 = FUN_0033fc20(uVar5,local_40);
        }
        break;
      }
      lVar7 = lVar7 + 1;
    } while ((int)lVar7 < 6);
  }
  param_4[4] = uVar3;
  cVar2 = extraout_RDX[2];
  uVar5 = FUN_005494c0();
  uVar3 = 0xffffffff;
  uVar4 = 0xffffffff;
  if (cVar2 != -1) {
    lVar7 = 0;
    do {
      if (*(char *)(param_2 + lVar7 * 4) == cVar2) {
        puVar6 = (undefined4 *)FUN_0054c6b0(uVar5,*(undefined2 *)(param_2 + 2 + lVar7 * 4));
        uVar4 = 0xffffffff;
        if (puVar6 != (undefined4 *)0x0) {
          uVar5 = FUN_0033fa20();
          local_40[0] = *puVar6;
          uVar4 = FUN_0033fc20(uVar5,local_40);
        }
        goto LAB_009100f9;
      }
      lVar7 = lVar7 + 1;
    } while ((int)lVar7 < 6);
    uVar4 = 0xffffffff;
  }
LAB_009100f9:
  param_4[5] = uVar4;
  cVar2 = extraout_RDX[4];
  uVar5 = FUN_005494c0();
  if (cVar2 != -1) {
    lVar7 = 0;
    do {
      if (*(char *)(param_2 + lVar7 * 4) == cVar2) {
        puVar6 = (undefined4 *)FUN_0054c6b0(uVar5,*(undefined2 *)(param_2 + 2 + lVar7 * 4));
        if (puVar6 != (undefined4 *)0x0) {
          uVar5 = FUN_0033fa20();
          local_40[0] = *puVar6;
          uVar3 = FUN_0033fc20(uVar5,local_40);
        }
        break;
      }
      lVar7 = lVar7 + 1;
    } while ((int)lVar7 < 6);
  }
  param_4[7] = uVar3;
  cVar2 = extraout_RDX[3];
  uVar5 = FUN_005494c0();
  uVar4 = 0xffffffff;
  if (cVar2 != -1) {
    lVar7 = 0;
    do {
      if (*(char *)(param_2 + lVar7 * 4) == cVar2) {
        puVar6 = (undefined4 *)FUN_0054c6b0(uVar5,*(undefined2 *)(param_2 + 2 + lVar7 * 4));
        if (puVar6 != (undefined4 *)0x0) {
          uVar5 = FUN_0033fa20();
          local_40[0] = *puVar6;
          uVar4 = FUN_0033fc20(uVar5,local_40);
        }
        break;
      }
      lVar7 = lVar7 + 1;
    } while ((int)lVar7 < 6);
  }
  param_4[6] = uVar4;
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

