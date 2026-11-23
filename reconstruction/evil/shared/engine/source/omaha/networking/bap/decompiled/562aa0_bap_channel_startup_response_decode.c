
undefined8
FUN_00562aa0(undefined8 param_1,undefined8 param_2,int param_3,int param_4,undefined4 *param_5,
            undefined8 param_6)

{
  char cVar1;
  int iVar2;
  undefined8 uVar3;
  undefined1 uVar4;
  undefined1 local_168 [320];
  long local_28;
  
  local_28 = *DAT_01a1f100;
  if (param_3 == 0x80) {
    if (param_4 < 0x80) {
      cVar1 = FUN_000e4d70(7,4);
      uVar4 = 0;
      if (cVar1 != '\0') {
        if (DAT_026ba798 == '\0') {
          iVar2 = thunk_FUN_012aa7d6(&DAT_026ba798);
          if (iVar2 != 0) {
            DAT_026ba790 = FUN_000e4a10(s_networking_investment_bap_push_r_0163aa03);
            thunk_FUN_012aa7e6(&DAT_026ba798);
          }
        }
        uVar4 = 0;
        FUN_01008290(local_168,s_networking_investment_bap_push_r_0163aa03,param_4,0x80);
        FUN_000e4aa0(DAT_026ba790,local_168);
      }
    }
    else {
      thunk_FUN_012aa7c6(param_6,param_2,0x80);
      *param_5 = 0x80;
      uVar4 = 1;
    }
  }
  else {
    cVar1 = FUN_000e4d70(7,4);
    uVar4 = 0;
    if (cVar1 != '\0') {
      if (DAT_026ba788 == '\0') {
        iVar2 = thunk_FUN_012aa7d6(&DAT_026ba788);
        if (iVar2 != 0) {
          DAT_026ba780 = FUN_000e4a10(s_networking_investment_bap_push_r_0163a9b9);
          thunk_FUN_012aa7e6(&DAT_026ba788);
        }
      }
      uVar4 = 0;
      FUN_01008290(local_168,s_networking_investment_bap_push_r_0163a9b9,param_3,0x80);
      FUN_000e4aa0(DAT_026ba780,local_168);
    }
  }
  if (*DAT_01a1f100 == local_28) {
    return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),uVar4);
  }
  uVar3 = thunk_FUN_012aa7f6();
  return uVar3;
}

