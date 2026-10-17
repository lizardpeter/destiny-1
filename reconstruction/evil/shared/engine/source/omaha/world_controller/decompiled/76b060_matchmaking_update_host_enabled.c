
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0076b060(int *param_1)

{
  uint uVar1;
  char cVar2;
  byte bVar3;
  int iVar4;
  long lVar5;
  long *plVar6;
  char *pcVar7;
  undefined8 uVar8;
  undefined1 local_168 [320];
  long local_28;
  
  local_28 = *DAT_01a1f100;
  if ((char)param_1[2] == '\0') {
    lVar5 = FUN_00775180(param_1[1]);
  }
  else {
    lVar5 = FUN_00772ec0();
  }
  uVar1 = *(uint *)(lVar5 + 0x8c48);
  if ((((uVar1 & 0xfffffffe) == 6) || (uVar1 == 8)) || (uVar1 == 9)) {
    bVar3 = 0;
    switch(uVar1) {
    case 3:
    case 5:
    case 7:
      goto switchD_0076b0d2_caseD_3;
    default:
      goto switchD_0076b0d2_caseD_4;
    case 8:
      pcVar7 = (char *)(lVar5 + 0x8c50);
      break;
    case 9:
      pcVar7 = (char *)(lVar5 + 0x8c54);
    }
    if (*pcVar7 == '\0') {
switchD_0076b0d2_caseD_4:
      cVar2 = FUN_0076b390(param_1);
      if (cVar2 == '\0') {
        iVar4 = FUN_000697a0();
        if (1000 < (uint)(iVar4 - _DAT_026ca208)) {
          cVar2 = FUN_000e4d70(6,1);
          if (cVar2 != '\0') {
            if ((DAT_026ca210 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_026ca210), iVar4 != 0)) {
              DAT_026ca20c = FUN_000e4a10(s_world_controller_matchmaking_man_0164d0ca);
              thunk_FUN_012aa7e6(&DAT_026ca210);
            }
            FUN_01008290(local_168,s_world_controller_matchmaking_man_0164d0ca,
                         (&PTR_s_PRIVATE_activity_019450c0)[*param_1]);
            FUN_000e4aa0(DAT_026ca20c,local_168);
          }
          _DAT_026ca208 = FUN_000697a0();
        }
      }
      else if (*param_1 == 1) {
        uVar8 = 1;
        bVar3 = 1;
LAB_0076b1e6:
        cVar2 = FUN_007636a0(uVar8,0);
        if (cVar2 == '\0') goto switchD_0076b0d2_caseD_3;
        iVar4 = FUN_000697a0();
        if (5000 < (uint)(iVar4 - _DAT_026ca218)) {
          cVar2 = FUN_000e4d70(6,2);
          if (cVar2 != '\0') {
            if ((DAT_026ca220 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_026ca220), iVar4 != 0)) {
              DAT_026ca21c = FUN_000e4a10(s_world_controller_matchmaking_man_0164d153);
              thunk_FUN_012aa7e6(&DAT_026ca220);
            }
            uVar8 = FUN_00b6db70(lVar5);
            FUN_01008290(local_168,s_world_controller_matchmaking_man_0164d153,uVar8);
            FUN_000e4aa0(DAT_026ca21c,local_168);
          }
          _DAT_026ca218 = FUN_000697a0();
        }
      }
      else if (*param_1 != 2) {
        plVar6 = (long *)FUN_005979c0();
        pcVar7 = (char *)(**(code **)(*plVar6 + 0x60))(plVar6,*param_1);
        if (*pcVar7 != '\0') {
          bVar3 = pcVar7[0x65];
          uVar8 = 0;
          if (bVar3 != 0) goto LAB_0076b1e6;
        }
      }
    }
  }
  bVar3 = 0;
switchD_0076b0d2_caseD_3:
  if ((*(byte *)((long)param_1 + 0x21) >> 1 & 1) != bVar3) {
    cVar2 = FUN_000e4d70(6,2);
    if (cVar2 != '\0') {
      if ((DAT_026ca230 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_026ca230), iVar4 != 0)) {
        DAT_026ca228 = FUN_000e4a10(s_world_controller_matchmaking_man_0164d1bd);
        thunk_FUN_012aa7e6(&DAT_026ca230);
      }
      pcVar7 = s_DISABLED_0164d217;
      if (bVar3 != 0) {
        pcVar7 = s_ENABLED_0164d20f;
      }
      FUN_01008290(local_168,s_world_controller_matchmaking_man_0164d1bd,
                   (&PTR_s_PRIVATE_activity_019450c0)[*param_1],pcVar7);
      FUN_000e4aa0(DAT_026ca228,local_168);
    }
    if (bVar3 == 0) {
      bVar3 = *(byte *)((long)param_1 + 0x21) & 0xfd;
    }
    else {
      bVar3 = *(byte *)((long)param_1 + 0x21) | 2;
    }
    *(byte *)((long)param_1 + 0x21) = bVar3;
  }
  if (*DAT_01a1f100 == local_28) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

