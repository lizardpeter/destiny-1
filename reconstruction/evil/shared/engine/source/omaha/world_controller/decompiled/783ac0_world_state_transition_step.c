
void FUN_00783ac0(long param_1)

{
  int iVar1;
  long *plVar2;
  char cVar3;
  int iVar4;
  int iVar5;
  undefined8 uVar6;
  undefined *puVar7;
  undefined *puVar8;
  undefined1 local_178 [320];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  if ((*(int *)(param_1 + 0x1c0) != *(int *)(param_1 + 0x1b0)) ||
     (*(int *)(param_1 + 0x1c4) != *(int *)(param_1 + 0x1b4))) {
    FUN_00771a20();
    FUN_007937b0();
    iVar5 = *(int *)(param_1 + 0x1b0);
    iVar1 = *(int *)(param_1 + 0x1c0);
    iVar4 = iVar1;
    if (iVar5 != -1) {
      cVar3 = FUN_000e4d70(5,2);
      if (cVar3 != '\0') {
        if ((DAT_026cc1a8 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_026cc1a8), iVar4 != 0)) {
          DAT_026cc1a0 = FUN_000e4a10(s_world_controller_state_manager__L_016562ab);
          thunk_FUN_012aa7e6(&DAT_026cc1a8);
        }
        puVar7 = &DAT_01615ab5;
        puVar8 = &DAT_01615ab5;
        if ((long)*(int *)(param_1 + 0x1b0) != -1) {
          puVar8 = (&PTR_s_pregame_01945340)[*(int *)(param_1 + 0x1b0)];
        }
        if ((long)*(int *)(param_1 + 0x1c4) != -1) {
          puVar7 = *(undefined **)(&DAT_026caf40 + (long)*(int *)(param_1 + 0x1c4) * 0x10);
        }
        FUN_01008290(local_178,s_world_controller_state_manager__L_016562ab,puVar8,puVar7);
        FUN_000e4aa0(DAT_026cc1a0,local_178);
      }
      plVar2 = *(long **)(param_1 + 0x80 + (long)*(int *)(param_1 + 0x1b0) * 8);
      (**(code **)(*plVar2 + 0x28))(plVar2,iVar1,*(undefined4 *)(param_1 + 0x1c4));
      iVar4 = *(int *)(param_1 + 0x1c0);
    }
    *(int *)(param_1 + 0x1b0) = iVar4;
    *(undefined4 *)(param_1 + 0x1b4) = *(undefined4 *)(param_1 + 0x1c4);
    uVar6 = DAT_026553b0;
    if (DAT_026553a8 == '\0') {
      uVar6 = FUN_000694d0();
      iVar4 = *(int *)(param_1 + 0x1c0);
    }
    *(undefined8 *)(param_1 + 0x1b8) = uVar6;
    if (iVar4 != -1) {
      if ((DAT_026cc1b8 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_026cc1b8), iVar4 != 0)) {
        DAT_026cc1b0 = FUN_000e4a10(s_world_controller_state_manager__E_01656693);
        thunk_FUN_012aa7e6(&DAT_026cc1b8);
      }
      puVar7 = &DAT_01615ab5;
      puVar8 = &DAT_01615ab5;
      if ((long)*(int *)(param_1 + 0x1c0) != -1) {
        puVar8 = (&PTR_s_pregame_01945340)[*(int *)(param_1 + 0x1c0)];
      }
      if ((long)*(int *)(param_1 + 0x1c4) != -1) {
        puVar7 = *(undefined **)(&DAT_026caf40 + (long)*(int *)(param_1 + 0x1c4) * 0x10);
      }
      FUN_01008290(local_178,s_world_controller_state_manager__E_01656693,puVar8,puVar7);
      FUN_000e4aa0(DAT_026cc1b0,local_178);
      plVar2 = *(long **)(param_1 + 0x80 + (long)*(int *)(param_1 + 0x1c0) * 8);
      (**(code **)(*plVar2 + 0x20))(plVar2,iVar5,*(undefined4 *)(param_1 + 0x1c4));
    }
    if ((DAT_026cc1c8 == '\0') && (iVar5 = thunk_FUN_012aa7d6(&DAT_026cc1c8), iVar5 != 0)) {
      DAT_026cc1c0 = FUN_00241890(s_state__016566d8);
      thunk_FUN_012aa7e6(&DAT_026cc1c8);
    }
    if (iVar1 == -1) {
      puVar8 = &DAT_01615ab5;
    }
    else {
      puVar8 = (&PTR_s_pregame_01945340)[iVar1];
    }
    FUN_00241a20(DAT_026cc1c0,puVar8,1);
  }
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

