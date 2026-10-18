
void FUN_0059b0e0(long param_1,long param_2,long param_3)

{
  char cVar1;
  int iVar2;
  long lVar3;
  long lVar4;
  long lVar5;
  undefined8 uVar6;
  undefined1 local_178 [320];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  cVar1 = FUN_00599870(param_1,param_3);
  if (cVar1 == '\0') {
    cVar1 = FUN_000e4d70(6,4);
    if (cVar1 != '\0') {
      if ((DAT_026bd150 == '\0') && (iVar2 = thunk_FUN_012aa7d6(&DAT_026bd150), iVar2 != 0)) {
        DAT_026bd148 = FUN_000e4a10(s_networking_online_matchmaking_bu_0163fcdc);
        thunk_FUN_012aa7e6(&DAT_026bd150);
      }
      uVar6 = FUN_00058050(param_1);
      FUN_01008290(local_178,s_networking_online_matchmaking_bu_0163fcdc,uVar6,
                   *(undefined8 *)(param_3 + 8));
      FUN_000e4aa0(DAT_026bd148,local_178);
    }
  }
  else {
    lVar3 = thunk_FUN_00768060();
    lVar4 = FUN_00078970(param_1);
    lVar5 = DAT_026553b0;
    if (DAT_026553a8 == '\0') {
      lVar5 = FUN_000694d0();
    }
    if ((&DAT_00001de0)[param_2] == '\0') {
      cVar1 = FUN_000e4d70(6,3);
      if (cVar1 != '\0') {
        if ((DAT_026bd140 == '\0') && (iVar2 = thunk_FUN_012aa7d6(&DAT_026bd140), iVar2 != 0)) {
          DAT_026bd138 = FUN_000e4a10(s_networking_online_matchmaking_bu_0163fc64);
          thunk_FUN_012aa7e6(&DAT_026bd140);
        }
        uVar6 = FUN_00058050(param_1);
        FUN_01008290(local_178,s_networking_online_matchmaking_bu_0163fc64,uVar6);
        FUN_000e4aa0(DAT_026bd138,local_178);
      }
      *(undefined1 *)(param_1 + 0x30) = 0;
      *(undefined4 *)(param_1 + 0x2c) = 5;
      FUN_00599a10(param_1 + 0x18);
    }
    else {
      cVar1 = FUN_000e4d70(6,1);
      if (cVar1 != '\0') {
        if ((DAT_026bd130 == '\0') && (iVar2 = thunk_FUN_012aa7d6(&DAT_026bd130), iVar2 != 0)) {
          DAT_026bd128 = FUN_000e4a10(s_networking_online_matchmaking_bu_0163fbf7);
          thunk_FUN_012aa7e6(&DAT_026bd130);
        }
        uVar6 = FUN_00058050(param_1);
        FUN_01008290(local_178,s_networking_online_matchmaking_bu_0163fbf7,uVar6,lVar5 - lVar4);
        FUN_000e4aa0(DAT_026bd128,local_178);
      }
      *(undefined1 *)(param_1 + 0x30) = 1;
      thunk_FUN_012aa7c6(param_1 + 0x38,&DAT_00001de8 + param_2,0x420);
      *(undefined4 *)(param_1 + 0x2c) = 0;
      FUN_00599a00(param_1 + 0x18);
    }
    if (lVar3 != 0) {
      FUN_00770f60(lVar3,lVar5 - lVar4,*(undefined1 *)(param_1 + 0x30));
    }
    FUN_0050fa40(param_1);
  }
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

