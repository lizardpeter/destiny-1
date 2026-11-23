
undefined8
FUN_0055dcb0(long *param_1,undefined8 *param_2,int param_3,int param_4,undefined4 *param_5,
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
        if (DAT_026ba540 == '\0') {
          iVar3 = thunk_FUN_012aa7d6(&DAT_026ba540);
          if (iVar3 != 0) {
            DAT_026ba538 = FUN_000e4a10(s_networking_investment_bap_client_01639a38);
            thunk_FUN_012aa7e6(&DAT_026ba540);
          }
        }
        uVar4 = (**(code **)(*param_1 + 8))(param_1);
        cVar2 = '\0';
        FUN_01008290(local_178,s_networking_investment_bap_client_01639a38,param_4,uVar4);
        FUN_000e4aa0(DAT_026ba538,local_178);
      }
    }
    else {
      *(undefined2 *)((long)param_6 + 0xc) = *(undefined2 *)((long)param_2 + 0xc);
      *(undefined4 *)(param_6 + 1) = *(undefined4 *)(param_2 + 1);
      *param_6 = *param_2;
      cVar2 = FUN_00b34840(param_2,param_4,param_6);
      if (cVar2 != '\0') {
        FUN_002a3620((long)param_6 + 6);
      }
      uVar4 = (**(code **)(*param_1 + 8))(param_1);
      *param_5 = uVar4;
    }
  }
  else {
    cVar1 = FUN_000e4d70(7,4);
    cVar2 = '\0';
    if (cVar1 != '\0') {
      if (DAT_026ba530 == '\0') {
        iVar3 = thunk_FUN_012aa7d6(&DAT_026ba530);
        if (iVar3 != 0) {
          DAT_026ba528 = FUN_000e4a10(s_networking_investment_bap_client_016399dc);
          thunk_FUN_012aa7e6(&DAT_026ba530);
        }
      }
      uVar4 = (**(code **)(*param_1 + 8))(param_1);
      cVar2 = '\0';
      FUN_01008290(local_178,s_networking_investment_bap_client_016399dc,param_3,uVar4);
      FUN_000e4aa0(DAT_026ba528,local_178);
    }
  }
  if (*DAT_01a1f100 == local_38) {
    return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),cVar2);
  }
  uVar5 = thunk_FUN_012aa7f6();
  return uVar5;
}

