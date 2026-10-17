
undefined8 FUN_0076ad90(undefined4 *param_1)

{
  char cVar1;
  int iVar2;
  long *plVar3;
  long lVar4;
  uint *puVar5;
  char *pcVar6;
  uint uVar7;
  undefined8 uVar8;
  float fVar9;
  undefined1 local_178 [320];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  iVar2 = FUN_00b403e0();
  plVar3 = (long *)FUN_005979c0();
  lVar4 = (**(code **)(*plVar3 + 0x60))(plVar3,*param_1);
  uVar8 = 1;
  if ((iVar2 != 3) && (*(char *)(lVar4 + 100) == '\0')) {
    puVar5 = (uint *)FUN_003055e0();
    uVar7 = *puVar5 * 0x19660d + 0x3c6ef35f;
    *puVar5 = uVar7;
    fVar9 = (float)FUN_0076af00();
    if ((float)(uVar7 >> 0x10) * DAT_0164cdd0 + 0.0 <= fVar9) {
      uVar8 = 2;
    }
  }
  cVar1 = FUN_000e4d70(6,2);
  if (cVar1 != '\0') {
    if (DAT_026ca1f0 == '\0') {
      iVar2 = thunk_FUN_012aa7d6(&DAT_026ca1f0);
      if (iVar2 != 0) {
        DAT_026ca1e8 = FUN_000e4a10(s_world_controller_matchmaking_man_0164cfdc);
        thunk_FUN_012aa7e6(&DAT_026ca1f0);
      }
    }
    plVar3 = (long *)FUN_005979c0();
    lVar4 = (**(code **)(*plVar3 + 0x60))(plVar3,*param_1);
    if (*(char *)(lVar4 + 100) == '\0') {
      pcVar6 = s_FALSE_0164d03e;
    }
    else {
      pcVar6 = &DAT_0164d039;
    }
    FUN_01008290(local_178,s_world_controller_matchmaking_man_0164cfdc,uVar8,pcVar6);
    FUN_000e4aa0(DAT_026ca1e8,local_178);
  }
  if (*DAT_01a1f100 == local_38) {
    return uVar8;
  }
  uVar8 = thunk_FUN_012aa7f6();
  return uVar8;
}

