
undefined8
FUN_00562c70(undefined8 param_1,undefined4 *param_2,int param_3,int param_4,int *param_5,
            undefined8 param_6)

{
  char cVar1;
  uint uVar2;
  int iVar3;
  undefined8 uVar4;
  undefined1 local_168 [320];
  long local_28;
  
  local_28 = *DAT_01a1f100;
  uVar2 = swap_bytes(*param_2);
  if ((CONCAT44((int)((ulong)local_28 >> 0x20),uVar2) == (long)param_3 + -4) && (uVar2 < 0x5d)) {
    if (param_4 < param_3) {
      cVar1 = FUN_000e4d70(7,4);
      if (cVar1 != '\0') {
        if (DAT_026ba7b8 == '\0') {
          iVar3 = thunk_FUN_012aa7d6(&DAT_026ba7b8);
          if (iVar3 != 0) {
            DAT_026ba7b0 = FUN_000e4a10(s_networking_investment_bap_hello__0163aa9d);
            thunk_FUN_012aa7e6(&DAT_026ba7b8);
          }
        }
        FUN_01008290(local_168,s_networking_investment_bap_hello__0163aa9d,param_4,param_3);
        FUN_000e4aa0(DAT_026ba7b0,local_168);
      }
    }
    else {
      thunk_FUN_012aa7c6(param_6);
      *param_5 = param_3;
    }
  }
  else {
    cVar1 = FUN_000e4d70(7,4);
    if (cVar1 != '\0') {
      if (DAT_026ba7a8 == '\0') {
        iVar3 = thunk_FUN_012aa7d6(&DAT_026ba7a8);
        if (iVar3 != 0) {
          DAT_026ba7a0 = FUN_000e4a10(s_networking_investment_bap_hello__0163aa55);
          thunk_FUN_012aa7e6(&DAT_026ba7a8);
        }
      }
      FUN_01008290(local_168,s_networking_investment_bap_hello__0163aa55,param_3);
      FUN_000e4aa0(DAT_026ba7a0,local_168);
    }
  }
  if (*DAT_01a1f100 == local_28) {
    return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),1);
  }
  uVar4 = thunk_FUN_012aa7f6();
  return uVar4;
}

