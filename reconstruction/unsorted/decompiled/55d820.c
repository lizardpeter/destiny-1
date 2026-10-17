
undefined8
FUN_0055d820(long *param_1,undefined4 *param_2,int param_3,int param_4,undefined4 *param_5,
            undefined4 *param_6)

{
  char cVar1;
  undefined1 uVar2;
  int iVar3;
  undefined4 uVar4;
  undefined8 uVar5;
  undefined1 local_178 [320];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  iVar3 = (**(code **)(*param_1 + 8))();
  if (iVar3 == param_3) {
    iVar3 = (**(code **)(*param_1 + 8))(param_1);
    if (iVar3 <= param_4) {
      *(undefined2 *)(param_6 + 1) = *(undefined2 *)(param_2 + 1);
      *param_6 = *param_2;
      uVar2 = FUN_00b34840(param_2,param_4,param_6);
      uVar4 = (**(code **)(*param_1 + 8))(param_1);
      *param_5 = uVar4;
      goto LAB_0055d9c0;
    }
    cVar1 = FUN_000e4d70(7,4);
    uVar2 = 0;
    if (cVar1 == '\0') goto LAB_0055d9c0;
    if (DAT_026ba500 == '\0') {
      iVar3 = thunk_FUN_012aa7d6(&DAT_026ba500);
      if (iVar3 != 0) {
        DAT_026ba4f8 = FUN_000e4a10(s_networking_investment_bap_client_016398df);
        thunk_FUN_012aa7e6(&DAT_026ba500);
      }
    }
    uVar4 = (**(code **)(*param_1 + 8))(param_1);
    FUN_01008290(local_178,s_networking_investment_bap_client_016398df,param_4,uVar4);
    uVar4 = DAT_026ba4f8;
  }
  else {
    cVar1 = FUN_000e4d70(7,4);
    uVar2 = 0;
    if (cVar1 == '\0') goto LAB_0055d9c0;
    if (DAT_026ba4f0 == '\0') {
      iVar3 = thunk_FUN_012aa7d6(&DAT_026ba4f0);
      if (iVar3 != 0) {
        DAT_026ba4e8 = FUN_000e4a10(s_networking_investment_bap_client_0163988c);
        thunk_FUN_012aa7e6(&DAT_026ba4f0);
      }
    }
    uVar4 = (**(code **)(*param_1 + 8))(param_1);
    FUN_01008290(local_178,s_networking_investment_bap_client_0163988c,param_3,uVar4);
    uVar4 = DAT_026ba4e8;
  }
  uVar2 = 0;
  FUN_000e4aa0(uVar4,local_178);
LAB_0055d9c0:
  if (*DAT_01a1f100 == local_38) {
    return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),uVar2);
  }
  uVar5 = thunk_FUN_012aa7f6();
  return uVar5;
}

