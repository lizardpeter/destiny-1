
undefined8
FUN_0055e460(long *param_1,undefined8 *param_2,int param_3,int param_4,undefined4 *param_5,
            undefined8 *param_6)

{
  char cVar1;
  char cVar2;
  int iVar3;
  undefined4 uVar4;
  undefined8 uVar5;
  undefined1 local_178 [320];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  iVar3 = (**(code **)(*param_1 + 8))();
  if (iVar3 == param_3) {
    iVar3 = (**(code **)(*param_1 + 8))(param_1);
    if (param_4 < iVar3) {
      cVar1 = FUN_000e4d70(7,4);
      cVar2 = '\0';
      if (cVar1 != '\0') {
        if (DAT_026ba5a0 == '\0') {
          iVar3 = thunk_FUN_012aa7d6(&DAT_026ba5a0);
          if (iVar3 != 0) {
            DAT_026ba598 = FUN_000e4a10(s_networking_investment_bap_servic_01639c61);
            thunk_FUN_012aa7e6(&DAT_026ba5a0);
          }
        }
        uVar4 = (**(code **)(*param_1 + 8))(param_1);
        cVar2 = '\0';
        FUN_01008290(local_178,s_networking_investment_bap_servic_01639c61,param_4,uVar4);
        FUN_000e4aa0(DAT_026ba598,local_178);
      }
    }
    else {
      param_6[3] = param_2[3];
      param_6[2] = param_2[2];
      uVar5 = *param_2;
      param_6[1] = param_2[1];
      *param_6 = uVar5;
      cVar2 = FUN_00b34840(param_2,param_4,param_6);
      if (cVar2 != '\0') {
        uVar5 = swap_bytes(*(undefined8 *)((long)param_6 + 6));
        *(undefined8 *)((long)param_6 + 6) = uVar5;
        uVar5 = swap_bytes(*(undefined8 *)((long)param_6 + 0xe));
        *(undefined8 *)((long)param_6 + 0xe) = uVar5;
        FUN_002a3620(param_6 + 3);
      }
      uVar4 = (**(code **)(*param_1 + 8))(param_1);
      *param_5 = uVar4;
    }
  }
  else {
    cVar1 = FUN_000e4d70(7,4);
    cVar2 = '\0';
    if (cVar1 != '\0') {
      if (DAT_026ba590 == '\0') {
        iVar3 = thunk_FUN_012aa7d6(&DAT_026ba590);
        if (iVar3 != 0) {
          DAT_026ba588 = FUN_000e4a10(s_networking_investment_bap_servic_01639c04);
          thunk_FUN_012aa7e6(&DAT_026ba590);
        }
      }
      uVar4 = (**(code **)(*param_1 + 8))(param_1);
      cVar2 = '\0';
      FUN_01008290(local_178,s_networking_investment_bap_servic_01639c04,param_3,uVar4);
      FUN_000e4aa0(DAT_026ba588,local_178);
    }
  }
  if (*DAT_01a1f100 == local_38) {
    return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),cVar2);
  }
  uVar5 = thunk_FUN_012aa7f6();
  return uVar5;
}

