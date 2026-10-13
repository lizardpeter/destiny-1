
void FUN_00299e30(long *param_1,undefined8 param_2,int param_3,undefined8 param_4,undefined4 param_5
                 )

{
  int *piVar1;
  char cVar2;
  char cVar3;
  char cVar4;
  uint uVar5;
  int iVar6;
  undefined4 uVar7;
  undefined8 uVar8;
  int *piVar9;
  undefined *puVar10;
  undefined *puVar11;
  undefined1 local_178 [320];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  uVar5 = 0xffffffff;
  piVar1 = &DAT_01910480;
  do {
    piVar9 = piVar1;
    uVar5 = uVar5 + 1;
    if (0x10 < uVar5) {
      if (DAT_02655418 == '\0') {
        iVar6 = thunk_FUN_012aa7d6(&DAT_02655418);
        if (iVar6 != 0) {
          DAT_02655410 = FUN_000e4a10(s_networking_activity_client_recei_01621d62);
          thunk_FUN_012aa7e6(&DAT_02655418);
        }
      }
      cVar2 = (**(code **)(*(long *)param_1[0x1ca] + 0x18))();
      cVar3 = (**(code **)(*param_1 + 0x18))(param_1);
      cVar4 = (**(code **)(*param_1 + 0x18))(param_1);
      puVar10 = &DAT_01621de5;
      puVar11 = &DAT_01621de5;
      if (cVar2 != '\0') {
        puVar11 = &DAT_01621de3;
      }
      if (cVar3 != '\0') {
        puVar10 = &DAT_01621de3;
      }
      if (cVar4 == '\0') {
        uVar8 = FUN_00001df0();
      }
      else {
        uVar8 = (**(code **)(*param_1 + 0x10))(param_1);
      }
      uVar7 = FUN_00057e60(param_1 + 0x1ce);
      FUN_01008290(local_178,s_networking_activity_client_recei_01621d62,param_1 + 4,puVar11,puVar10
                   ,uVar8,uVar7,param_3,param_5);
      uVar7 = DAT_02655410;
      goto LAB_0029a082;
    }
    piVar1 = piVar9 + 4;
  } while (*piVar9 != param_3);
  cVar2 = (**(code **)(piVar9 + 2))(param_1,param_4,param_5);
  if (cVar2 == '\0') {
    if (DAT_02655428 == '\0') {
      iVar6 = thunk_FUN_012aa7d6(&DAT_02655428);
      if (iVar6 != 0) {
        DAT_02655420 = FUN_000e4a10(s_networking_activity_client_recei_01621de7);
        thunk_FUN_012aa7e6(&DAT_02655428);
      }
    }
    cVar2 = (**(code **)(*(long *)param_1[0x1ca] + 0x18))();
    cVar3 = (**(code **)(*param_1 + 0x18))(param_1);
    cVar4 = (**(code **)(*param_1 + 0x18))(param_1);
    puVar11 = &DAT_01621de5;
    puVar10 = &DAT_01621de5;
    if (cVar2 != '\0') {
      puVar10 = &DAT_01621de3;
    }
    if (cVar3 != '\0') {
      puVar11 = &DAT_01621de3;
    }
    if (cVar4 == '\0') {
      uVar8 = FUN_00001df0();
    }
    else {
      uVar8 = (**(code **)(*param_1 + 0x10))(param_1);
    }
    uVar7 = FUN_00057e60(param_1 + 0x1ce);
    FUN_01008290(local_178,s_networking_activity_client_recei_01621de7,param_1 + 4,puVar10,puVar11,
                 uVar8,uVar7,param_3);
    uVar7 = DAT_02655420;
LAB_0029a082:
    FUN_000e4aa0(uVar7,local_178);
  }
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

