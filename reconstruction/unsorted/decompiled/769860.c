
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00769860(int *param_1)

{
  int *piVar1;
  byte bVar2;
  bool bVar3;
  char cVar4;
  undefined1 uVar5;
  int iVar6;
  undefined8 uVar7;
  char *pcVar8;
  char *pcVar9;
  undefined1 local_178 [320];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  if ((char)param_1[2] == '\0') {
    uVar7 = FUN_00775180(param_1[1]);
  }
  else {
    uVar7 = FUN_00772ec0();
  }
  bVar2 = *(byte *)((long)param_1 + 0x21);
  piVar1 = param_1 + 10;
  cVar4 = FUN_00b2bda0(piVar1);
  if ((bVar2 & 1) == 0) {
    bVar3 = false;
    if (cVar4 != '\0') {
      cVar4 = FUN_000e4d70(6,1);
      if (cVar4 != '\0') {
        if (DAT_026ca2e0 == '\0') {
          iVar6 = thunk_FUN_012aa7d6(&DAT_026ca2e0);
          if (iVar6 != 0) {
            DAT_026ca2d8 = FUN_000e4a10(s_world_controller_matchmaking_man_0164d5a3);
            thunk_FUN_012aa7e6(&DAT_026ca2e0);
          }
        }
        FUN_01008290(local_178,s_world_controller_matchmaking_man_0164d5a3,
                     (&PTR_s_PRIVATE_activity_019450c0)[*param_1]);
        FUN_000e4aa0(DAT_026ca2d8,local_178);
      }
      FUN_00b2b730(piVar1,uVar7);
    }
  }
  else {
    if (cVar4 == '\0') {
      cVar4 = FUN_000e4d70(6,1);
      if (cVar4 != '\0') {
        if (DAT_026ca2d0 == '\0') {
          iVar6 = thunk_FUN_012aa7d6(&DAT_026ca2d0);
          if (iVar6 != 0) {
            DAT_026ca2c8 = FUN_000e4a10(s_world_controller_matchmaking_man_0164d567);
            thunk_FUN_012aa7e6(&DAT_026ca2d0);
          }
        }
        FUN_01008290(local_178,s_world_controller_matchmaking_man_0164d567,
                     (&PTR_s_PRIVATE_activity_019450c0)[*param_1]);
        FUN_000e4aa0(DAT_026ca2c8,local_178);
      }
      FUN_00b2b6b0(piVar1,(char)param_1[4],param_1[3]);
    }
    uVar5 = FUN_001616d0(param_1 + 0x7ec);
    FUN_00b2b7a0(piVar1,uVar5,uVar7);
    bVar3 = true;
  }
  bVar2 = *(byte *)((long)param_1 + 0x21);
  piVar1 = param_1 + 0x7ec;
  cVar4 = FUN_001616d0(piVar1);
  if ((bVar2 & 2) == 0) {
    if (cVar4 != '\0') {
      cVar4 = FUN_000e4d70(6,1);
      if (cVar4 != '\0') {
        if (DAT_026ca300 == '\0') {
          iVar6 = thunk_FUN_012aa7d6(&DAT_026ca300);
          if (iVar6 != 0) {
            DAT_026ca2f8 = FUN_000e4a10(s_world_controller_matchmaking_man_0164d61e);
            thunk_FUN_012aa7e6(&DAT_026ca300);
          }
        }
        FUN_01008290(local_178,s_world_controller_matchmaking_man_0164d61e,
                     (&PTR_s_PRIVATE_activity_019450c0)[*param_1]);
        FUN_000e4aa0(DAT_026ca2f8,local_178);
      }
      FUN_00b2af70(piVar1,uVar7);
    }
    if (!bVar3) goto LAB_00769c38;
    pcVar9 = s_INACTIVE_0163906a;
  }
  else {
    if (cVar4 == '\0') {
      cVar4 = FUN_000e4d70(6,1);
      if (cVar4 != '\0') {
        if (DAT_026ca2f0 == '\0') {
          iVar6 = thunk_FUN_012aa7d6(&DAT_026ca2f0);
          if (iVar6 != 0) {
            DAT_026ca2e8 = FUN_000e4a10(s_world_controller_matchmaking_man_0164d5df);
            thunk_FUN_012aa7e6(&DAT_026ca2f0);
          }
        }
        FUN_01008290(local_178,s_world_controller_matchmaking_man_0164d5df,
                     (&PTR_s_PRIVATE_activity_019450c0)[*param_1]);
        FUN_000e4aa0(DAT_026ca2e8,local_178);
      }
      FUN_00b2aef0(piVar1,*(undefined1 *)((long)param_1 + 0x11));
    }
    FUN_00b2b070(piVar1,uVar7);
    pcVar9 = s_ACTIVE_0162944c;
  }
  iVar6 = FUN_000697a0();
  if (3000 < (uint)(iVar6 - _DAT_026ca308)) {
    cVar4 = FUN_000e4d70(6,0);
    if (cVar4 != '\0') {
      if (DAT_026ca310 == '\0') {
        iVar6 = thunk_FUN_012aa7d6(&DAT_026ca310);
        if (iVar6 != 0) {
          DAT_026ca30c = FUN_000e4a10(s_world_controller_matchmaking_man_0164d65a);
          thunk_FUN_012aa7e6(&DAT_026ca310);
        }
      }
      pcVar8 = s_INACTIVE_0163906a;
      if (bVar3) {
        pcVar8 = s_ACTIVE_0162944c;
      }
      FUN_01008290(local_178,s_world_controller_matchmaking_man_0164d65a,
                   (&PTR_s_PRIVATE_activity_019450c0)[*param_1],pcVar8,pcVar9);
      FUN_000e4aa0(DAT_026ca30c,local_178);
    }
    _DAT_026ca308 = FUN_000697a0();
  }
LAB_00769c38:
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

