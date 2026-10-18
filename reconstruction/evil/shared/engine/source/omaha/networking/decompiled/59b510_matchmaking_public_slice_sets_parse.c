
long FUN_0059b510(long param_1,undefined4 param_2)

{
  int iVar1;
  char cVar2;
  int iVar3;
  undefined4 uVar4;
  undefined8 uVar5;
  undefined8 uVar6;
  long lVar7;
  long lVar8;
  int local_190 [2];
  int local_188 [2];
  undefined4 local_180 [2];
  undefined1 local_178 [320];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  local_180[0] = param_2;
  FUN_0075cfd0();
  local_188[0] = -0x7ee3623b;
  local_190[0] = -0x7ee3623b;
  FUN_0075cff0(param_2,local_188,local_190);
  lVar7 = param_1 + 0x94;
  if (local_188[0] == -0x7ee3623b) {
    cVar2 = FUN_000e4d70(6,2);
    if (cVar2 == '\0') goto LAB_0059b77e;
    if ((DAT_026bd170 == '\0') && (iVar3 = thunk_FUN_012aa7d6(&DAT_026bd170), iVar3 != 0)) {
      DAT_026bd168 = FUN_000e4a10(s_networking_online_matchmaking_bu_0163fe46);
      thunk_FUN_012aa7e6(&DAT_026bd170);
    }
    FUN_01008290(local_178,s_networking_online_matchmaking_bu_0163fe46);
    uVar4 = DAT_026bd168;
  }
  else {
    if (local_190[0] != -0x7ee3623b) {
      if (0 < *(int *)(param_1 + 0xd0)) {
        lVar8 = param_1 + 0xd8;
        iVar3 = 0;
        do {
          if ((*(int *)(lVar8 + 4) == local_188[0]) && (*(int *)(lVar8 + 0xc) == local_190[0])) {
            cVar2 = FUN_000e4d70(6,2);
            lVar7 = lVar8;
            if (cVar2 != '\0') {
              if ((DAT_026bd190 == '\0') && (iVar3 = thunk_FUN_012aa7d6(&DAT_026bd190), iVar3 != 0))
              {
                DAT_026bd188 = FUN_000e4a10(s_networking_online_matchmaking_bu_0163ff11);
                thunk_FUN_012aa7e6(&DAT_026bd190);
              }
              uVar5 = FUN_00079a30(&DAT_01620037,local_188[0]);
              iVar1 = local_188[0];
              uVar6 = FUN_00079a30(&DAT_01620037,local_190[0]);
              iVar3 = local_190[0];
              uVar4 = FUN_0012d700(local_180);
              FUN_01008290(local_178,s_networking_online_matchmaking_bu_0163ff11,uVar5,iVar1,uVar6,
                           iVar3,uVar4);
              FUN_000e4aa0(DAT_026bd188,local_178);
            }
            break;
          }
          lVar8 = lVar8 + 0x38;
          iVar3 = iVar3 + 1;
        } while (iVar3 < *(int *)(param_1 + 0xd0));
      }
      goto LAB_0059b77e;
    }
    cVar2 = FUN_000e4d70(6,2);
    if (cVar2 == '\0') goto LAB_0059b77e;
    if ((DAT_026bd180 == '\0') && (iVar3 = thunk_FUN_012aa7d6(&DAT_026bd180), iVar3 != 0)) {
      DAT_026bd178 = FUN_000e4a10(s_networking_online_matchmaking_bu_0163fea6);
      thunk_FUN_012aa7e6(&DAT_026bd180);
    }
    FUN_01008290(local_178,s_networking_online_matchmaking_bu_0163fea6);
    uVar4 = DAT_026bd178;
  }
  FUN_000e4aa0(uVar4,local_178);
LAB_0059b77e:
  if (*DAT_01a1f100 != local_38) {
    lVar7 = thunk_FUN_012aa7f6();
    return lVar7;
  }
  return lVar7;
}

