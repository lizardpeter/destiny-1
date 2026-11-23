
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0075fb20(long param_1,int param_2)

{
  int *piVar1;
  uint uVar2;
  char cVar3;
  int iVar4;
  undefined4 uVar5;
  long lVar6;
  undefined8 uVar7;
  long lVar8;
  long *plVar9;
  long lVar10;
  undefined8 uVar11;
  long lVar12;
  undefined1 local_2a0 [256];
  undefined8 local_1a0;
  undefined8 local_198;
  undefined8 local_190;
  undefined8 local_188;
  undefined4 local_180;
  undefined1 local_178 [320];
  long local_38;
  
  lVar10 = DAT_026c96f8;
  local_38 = *DAT_01a1f100;
  lVar12 = (long)param_2 * 0x1f0;
  iVar4 = *(int *)(param_1 + 0x4f0 + lVar12);
  if (((8 < iVar4) || (iVar4 - 7U < 2)) || (iVar4 == -1)) goto LAB_00760190;
  piVar1 = (int *)(param_1 + 0x4f0 + lVar12);
  if (3 < iVar4 - 2U) goto LAB_0075fdf1;
  lVar6 = FUN_0075bdb0(param_1);
  uVar2 = *(uint *)(lVar6 + 0x8c48);
  if (uVar2 < 0xb) {
    if ((0x500U >> (uVar2 & 0x1f) & 1) == 0) {
      if ((0x3f0U >> (uVar2 & 0x1f) & 1) == 0) goto LAB_0075fd83;
      lVar6 = FUN_00b74340(lVar6);
      lVar8 = (long)*(int *)(lVar6 + 0x10) * 0x168;
      local_190 = *(undefined8 *)(lVar6 + 0x40 + lVar8);
      local_188 = *(undefined8 *)(lVar6 + 0x48 + lVar8);
      local_180 = *(undefined4 *)(lVar6 + 0x50 + lVar8);
      local_1a0 = *(undefined8 *)(lVar6 + 0x30 + lVar8);
      local_198 = *(undefined8 *)(lVar6 + 0x38 + lVar8);
      lVar6 = 0;
      if (*(int *)(param_1 + 0x5b8 + lVar12) != -1) {
        lVar6 = FUN_002a0010();
      }
      cVar3 = FUN_002e8cb0(&local_1a0,param_1 + 0x584 + lVar12);
      if (cVar3 == '\0') {
        if ((lVar6 == 0) || ((*(byte *)(lVar6 + 0x130) & 8) == 0)) {
          cVar3 = FUN_000e4d70(2,4);
          if (cVar3 != '\0') {
            if (DAT_026c9c20 == '\0') {
              iVar4 = thunk_FUN_012aa7d6(&DAT_026c9c20);
              if (iVar4 != 0) {
                DAT_026c9c18 = FUN_000e4a10(s_world_controller_activity_manage_0164c30a);
                thunk_FUN_012aa7e6(&DAT_026c9c20);
              }
            }
            FUN_01008290(local_178,s_world_controller_activity_manage_0164c30a,
                         param_1 + 0x6c8 + lVar12);
            uVar5 = DAT_026c9c18;
            goto LAB_0075fc2e;
          }
          goto LAB_0075fc36;
        }
        iVar4 = FUN_000697a0();
        if (5000 < (uint)(iVar4 - _DAT_026c9c08)) {
          cVar3 = FUN_000e4d70(2,3);
          if (cVar3 != '\0') {
            if (DAT_026c9c10 == '\0') {
              iVar4 = thunk_FUN_012aa7d6(&DAT_026c9c10);
              if (iVar4 != 0) {
                DAT_026c9c0c = FUN_000e4a10(s_world_controller_activity_manage_0164c272);
                thunk_FUN_012aa7e6(&DAT_026c9c10);
              }
            }
            FUN_01008290(local_178,s_world_controller_activity_manage_0164c272,
                         param_1 + 0x6c8 + lVar12);
            FUN_000e4aa0(DAT_026c9c0c,local_178);
          }
          _DAT_026c9c08 = FUN_000697a0();
        }
      }
    }
    else {
      if (DAT_026c9bf0 == '\0') {
        iVar4 = thunk_FUN_012aa7d6(&DAT_026c9bf0);
        if (iVar4 != 0) {
          DAT_026c9be8 = FUN_000e4a10(s_world_controller_activity_manage_0164c1a9);
          thunk_FUN_012aa7e6(&DAT_026c9bf0);
        }
      }
      uVar7 = FUN_00b6e670(lVar6);
      FUN_01008290(local_178,s_world_controller_activity_manage_0164c1a9,param_1 + 0x6c8 + lVar12,
                   uVar7);
      uVar5 = DAT_026c9be8;
LAB_0075fc2e:
      FUN_000e4aa0(uVar5,local_178);
LAB_0075fc36:
      *piVar1 = 0x20;
    }
  }
  else {
LAB_0075fd83:
    if (DAT_026c9c00 == '\0') {
      iVar4 = thunk_FUN_012aa7d6(&DAT_026c9c00);
      if (iVar4 != 0) {
        DAT_026c9bf8 = FUN_000e4a10(s_world_controller_activity_manage_0164c21a);
        thunk_FUN_012aa7e6(&DAT_026c9c00);
      }
    }
    FUN_01008290(local_178,s_world_controller_activity_manage_0164c21a,param_1 + 0x6c8 + lVar12);
    FUN_000e4aa0(DAT_026c9bf8,local_178);
    *piVar1 = 0x1f;
  }
LAB_0075fdf1:
  cVar3 = FUN_00752150(0);
  if ((cVar3 == '\0') && (*piVar1 - 4U < 5)) {
    uVar7 = FUN_002a0010(*(undefined4 *)(param_1 + 0x5b8 + lVar12));
    cVar3 = FUN_002998a0(uVar7);
    if (cVar3 == '\0') {
      cVar3 = FUN_000e4d70(3,4);
      if (cVar3 != '\0') {
        if (DAT_026c9c30 == '\0') {
          iVar4 = thunk_FUN_012aa7d6(&DAT_026c9c30);
          if (iVar4 != 0) {
            DAT_026c9c28 = FUN_000e4a10(s_world_controller_activity_manage_0164c398);
            thunk_FUN_012aa7e6(&DAT_026c9c30);
          }
        }
        FUN_01008290(local_178,s_world_controller_activity_manage_0164c398,param_1 + 0x6c8 + lVar12)
        ;
        FUN_000e4aa0(DAT_026c9c28,local_178);
      }
      *piVar1 = 0x21;
    }
    else if (*piVar1 == 6) {
      lVar6 = FUN_001db3f0();
      lVar8 = FUN_0034e340();
      iVar4 = *(int *)(lVar8 + 0x28);
      plVar9 = (long *)FUN_002a0010(*(undefined4 *)(param_1 + 0x5b8 + lVar12));
      uVar7 = FUN_002a00c0(*(undefined4 *)(lVar10 + 0x14 + (long)param_2 * 8));
      cVar3 = (**(code **)(*plVar9 + 0x18))(plVar9);
      if (cVar3 == '\0') {
        cVar3 = FUN_000e4d70(3,4);
        if (cVar3 != '\0') {
          if (DAT_026c9c40 == '\0') {
            iVar4 = thunk_FUN_012aa7d6(&DAT_026c9c40);
            if (iVar4 != 0) {
              DAT_026c9c38 = FUN_000e4a10(s_world_controller_activity_manage_0164c3ec);
              thunk_FUN_012aa7e6(&DAT_026c9c40);
            }
          }
          FUN_01008290(local_178,s_world_controller_activity_manage_0164c3ec,
                       param_1 + 0x6c8 + lVar12);
          FUN_000e4aa0(DAT_026c9c38,local_178);
        }
        *piVar1 = 0x22;
      }
      else {
        cVar3 = FUN_0029dd00(plVar9);
        if (cVar3 == '\0') {
          lVar10 = FUN_0029d400(plVar9);
          if (iVar4 + lVar6 <= lVar10) {
            uVar11 = FUN_0029d400(plVar9);
            lVar10 = FUN_0034e340();
            FUN_010156f0(local_2a0,s___s__Lost_connection_to_activity_0164c48a,
                         param_1 + 0x6c8 + lVar12,uVar11,*(undefined4 *)(lVar10 + 0x28),lVar6);
            cVar3 = FUN_002a4de0(local_2a0,1);
            if (cVar3 != '\0') {
              *piVar1 = 0x24;
              goto LAB_00760190;
            }
          }
          cVar3 = FUN_002a2990(uVar7);
          if (cVar3 == '\0') {
            cVar3 = FUN_002a2af0(uVar7);
            if (cVar3 != '\0') {
              *piVar1 = 0x26;
            }
          }
          else {
            *piVar1 = 0x25;
          }
        }
        else {
          cVar3 = FUN_000e4d70(3,4);
          if (cVar3 != '\0') {
            if (DAT_026c9c50 == '\0') {
              iVar4 = thunk_FUN_012aa7d6(&DAT_026c9c50);
              if (iVar4 != 0) {
                DAT_026c9c48 = FUN_000e4a10(s_world_controller_activity_manage_0164c43a);
                thunk_FUN_012aa7e6(&DAT_026c9c50);
              }
            }
            uVar5 = FUN_0029dd10(plVar9);
            uVar7 = FUN_002a55e0(uVar5);
            FUN_01008290(local_178,s_world_controller_activity_manage_0164c43a,
                         param_1 + 0x6c8 + lVar12,uVar7);
            FUN_000e4aa0(DAT_026c9c48,local_178);
          }
          *piVar1 = 0x23;
          uVar5 = FUN_0029dd10(plVar9);
          *(undefined4 *)(param_1 + 0x4f4 + lVar12) = uVar5;
        }
      }
    }
  }
LAB_00760190:
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

