
void FUN_00910c60(undefined1 param_1,undefined8 *param_2,undefined8 param_3,long param_4,
                 undefined8 param_5,int *param_6)

{
  short sVar1;
  char cVar2;
  int iVar3;
  int iVar4;
  long *plVar5;
  long lVar6;
  undefined8 uVar7;
  int *piVar8;
  long lVar9;
  undefined8 extraout_XMM0_Qa;
  undefined1 auVar10 [16];
  undefined1 extraout_var [56];
  int local_138 [64];
  long local_38;
  undefined1 auVar11 [64];
  
  local_38 = *DAT_01a1f100;
  plVar5 = (long *)FUN_0025cbd0();
  lVar6 = (**(code **)(*plVar5 + 0x68))(plVar5);
  *(undefined8 *)(param_6 + 6) = *param_2;
  *(undefined1 *)(param_6 + 8) = param_1;
  uVar7 = FUN_005494c0();
  piVar8 = (int *)FUN_0054c7b0(uVar7,*(undefined2 *)((long)param_2 + 10));
  *param_6 = -1;
  param_6[3] = -0x7ee3623b;
  param_6[4] = -0x7ee3623b;
  if (piVar8 != (int *)0x0) {
    param_6[3] = piVar8[1];
    param_6[4] = piVar8[2];
    uVar7 = FUN_0033fa20();
    local_138[0] = *piVar8;
    iVar3 = FUN_0033fc20(uVar7,local_138);
    if (iVar3 != -1) {
      *param_6 = iVar3;
    }
  }
  FUN_009109b0(param_2,param_3,param_6 + 9);
  lVar9 = 0;
  iVar3 = 0;
  do {
    sVar1 = *(short *)(param_4 + lVar9 * 2);
    piVar8 = (int *)CONCAT62((int6)((ulong)piVar8 >> 0x10),sVar1);
    uVar7 = FUN_005494c0();
    if (sVar1 != -1) {
      piVar8 = (int *)FUN_0054c9b0(uVar7,(ulong)piVar8 & 0xffffffff);
      if ((piVar8 != (int *)0x0) && (*piVar8 != -0x7ee3623b)) {
        uVar7 = FUN_0033fa20();
        local_138[0] = *piVar8;
        iVar4 = FUN_0033fc20(uVar7,local_138);
        if ((iVar4 != -1) && (iVar3 < 0x10)) {
          param_6[(long)iVar3 + 0xb6] = iVar4;
          iVar3 = iVar3 + 1;
        }
      }
    }
    lVar9 = lVar9 + 1;
  } while ((int)lVar9 != 0x10);
  FUN_0028a2f0(param_5,local_138);
  piVar8 = param_6 + 0x16;
  iVar3 = 0;
  do {
    cVar2 = FUN_00553610(iVar3);
    auVar11._8_56_ = extraout_var;
    auVar11._0_8_ = extraout_XMM0_Qa;
    if (cVar2 != -1) {
      auVar10._0_4_ = (float)local_138[cVar2];
      auVar10._4_12_ = auVar11._4_12_;
      FUN_00673800(auVar10._0_8_,piVar8);
    }
    piVar8 = piVar8 + 8;
    iVar3 = iVar3 + 1;
  } while (iVar3 != 0x14);
  iVar3 = FUN_00282210(local_138[*(char *)(lVar6 + 0x14c)]);
  plVar5 = DAT_01a1f100;
  param_6[0xc6] = iVar3;
  if (*plVar5 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

