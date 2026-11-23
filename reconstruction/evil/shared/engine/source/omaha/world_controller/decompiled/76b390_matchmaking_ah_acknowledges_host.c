
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_0076b390(int *param_1)

{
  char cVar1;
  undefined1 uVar2;
  int iVar3;
  undefined8 uVar4;
  long lVar5;
  undefined1 local_168 [320];
  long local_28;
  
  local_28 = *DAT_01a1f100;
  if ((char)param_1[2] == '\0') {
    uVar4 = FUN_00775180(param_1[1]);
  }
  else {
    uVar4 = FUN_00772ec0();
  }
  lVar5 = FUN_0075d700(uVar4);
  if (lVar5 == 0) {
    iVar3 = FUN_000697a0();
    uVar2 = 0;
    if (5000 < (uint)(iVar3 - _DAT_026ca318)) {
      cVar1 = FUN_000e4d70(6,1);
      if (cVar1 != '\0') {
        if (DAT_026ca320 == '\0') {
          iVar3 = thunk_FUN_012aa7d6(&DAT_026ca320);
          if (iVar3 != 0) {
            DAT_026ca31c = FUN_000e4a10(s_world_controller_matchmaking_man_0164d710);
            thunk_FUN_012aa7e6(&DAT_026ca320);
          }
        }
        FUN_01008290(local_168,s_world_controller_matchmaking_man_0164d710,
                     (&PTR_s_PRIVATE_activity_019450c0)[*param_1]);
        FUN_000e4aa0(DAT_026ca31c,local_168);
      }
      _DAT_026ca318 = FUN_000697a0();
    }
  }
  else {
    cVar1 = FUN_002999b0(lVar5);
    if (cVar1 == '\0') {
      iVar3 = FUN_000697a0();
      uVar2 = 0;
      if (1000 < (uint)(iVar3 - _DAT_026ca328)) {
        cVar1 = FUN_000e4d70(6,1);
        if (cVar1 != '\0') {
          if (DAT_026ca330 == '\0') {
            iVar3 = thunk_FUN_012aa7d6(&DAT_026ca330);
            if (iVar3 != 0) {
              DAT_026ca32c = FUN_000e4a10(s_world_controller_matchmaking_man_0164d76e);
              thunk_FUN_012aa7e6(&DAT_026ca330);
            }
          }
          FUN_01008290(local_168,s_world_controller_matchmaking_man_0164d76e,
                       (&PTR_s_PRIVATE_activity_019450c0)[*param_1]);
          FUN_000e4aa0(DAT_026ca32c,local_168);
        }
        _DAT_026ca328 = FUN_000697a0();
      }
    }
    else {
      uVar4 = FUN_0029c3b0(lVar5);
      uVar2 = FUN_002a0840(uVar4);
    }
  }
  if (*DAT_01a1f100 == local_28) {
    return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),uVar2);
  }
  uVar4 = thunk_FUN_012aa7f6();
  return uVar4;
}

