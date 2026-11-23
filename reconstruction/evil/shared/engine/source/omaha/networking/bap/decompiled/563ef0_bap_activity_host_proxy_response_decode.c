
undefined8
FUN_00563ef0(undefined8 param_1,undefined8 *param_2,int param_3,uint param_4,undefined4 *param_5,
            undefined8 *param_6)

{
  char cVar1;
  int iVar2;
  undefined8 uVar3;
  undefined4 uVar4;
  undefined1 uVar5;
  undefined1 local_178 [320];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  if (param_3 == 0x10) {
    if (0xf < param_4) {
      uVar3 = *param_2;
      param_6[1] = param_2[1];
      *param_6 = uVar3;
      FUN_002a3620(param_6);
      uVar4 = swap_bytes(*(undefined4 *)(param_6 + 1));
      *(undefined4 *)(param_6 + 1) = uVar4;
      uVar5 = 1;
      uVar4 = swap_bytes(*(undefined4 *)((long)param_6 + 0xc));
      *(undefined4 *)((long)param_6 + 0xc) = uVar4;
      *param_5 = 0x10;
      goto LAB_00564065;
    }
    cVar1 = FUN_000e4d70(7,4);
    uVar5 = 0;
    if (cVar1 == '\0') goto LAB_00564065;
    if (DAT_026ba8d8 == '\0') {
      iVar2 = thunk_FUN_012aa7d6(&DAT_026ba8d8);
      if (iVar2 != 0) {
        DAT_026ba8d0 = FUN_000e4a10(s_networking_investment_bap_get_ac_0163b087);
        thunk_FUN_012aa7e6(&DAT_026ba8d8);
      }
    }
    FUN_01008290(local_178,s_networking_investment_bap_get_ac_0163b087,param_4,0x10);
    uVar4 = DAT_026ba8d0;
  }
  else {
    cVar1 = FUN_000e4d70(7,4);
    uVar5 = 0;
    if (cVar1 == '\0') goto LAB_00564065;
    if (DAT_026ba8c8 == '\0') {
      iVar2 = thunk_FUN_012aa7d6(&DAT_026ba8c8);
      if (iVar2 != 0) {
        DAT_026ba8c0 = FUN_000e4a10(s_networking_investment_bap_get_ac_0163b029);
        thunk_FUN_012aa7e6(&DAT_026ba8c8);
      }
    }
    FUN_01008290(local_178,s_networking_investment_bap_get_ac_0163b029,param_3,0x10);
    uVar4 = DAT_026ba8c0;
  }
  uVar5 = 0;
  FUN_000e4aa0(uVar4,local_178);
LAB_00564065:
  if (*DAT_01a1f100 == local_38) {
    return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),uVar5);
  }
  uVar3 = thunk_FUN_012aa7f6();
  return uVar3;
}

