
undefined8
FUN_0055da10(long *param_1,undefined8 *param_2,int param_3,int param_4,undefined4 *param_5,
            undefined8 *param_6)

{
  ushort *puVar1;
  char cVar2;
  char cVar3;
  int iVar4;
  undefined4 uVar5;
  undefined8 uVar6;
  undefined1 local_178 [320];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  iVar4 = (**(code **)(*param_1 + 8))();
  if (iVar4 == param_3) {
    iVar4 = (**(code **)(*param_1 + 8))(param_1);
    if (param_4 < iVar4) {
      cVar2 = FUN_000e4d70(7,4);
      cVar3 = '\0';
      if (cVar2 != '\0') {
        if (DAT_026ba520 == '\0') {
          iVar4 = thunk_FUN_012aa7d6(&DAT_026ba520);
          if (iVar4 != 0) {
            DAT_026ba518 = FUN_000e4a10(s_networking_investment_bap_client_01639987);
            thunk_FUN_012aa7e6(&DAT_026ba520);
          }
        }
        uVar5 = (**(code **)(*param_1 + 8))(param_1);
        cVar3 = '\0';
        FUN_01008290(local_178,s_networking_investment_bap_client_01639987,param_4,uVar5);
        FUN_000e4aa0(DAT_026ba518,local_178);
      }
    }
    else {
      *param_6 = *param_2;
      cVar3 = FUN_00b34840(param_2,param_4,param_6);
      if (cVar3 != '\0') {
        puVar1 = (ushort *)((long)param_6 + 6);
        *puVar1 = *puVar1 << 8 | *puVar1 >> 8;
      }
      uVar5 = (**(code **)(*param_1 + 8))(param_1);
      *param_5 = uVar5;
    }
  }
  else {
    cVar2 = FUN_000e4d70(7,4);
    cVar3 = '\0';
    if (cVar2 != '\0') {
      if (DAT_026ba510 == '\0') {
        iVar4 = thunk_FUN_012aa7d6(&DAT_026ba510);
        if (iVar4 != 0) {
          DAT_026ba508 = FUN_000e4a10(s_networking_investment_bap_client_0163993a);
          thunk_FUN_012aa7e6(&DAT_026ba510);
        }
      }
      uVar5 = (**(code **)(*param_1 + 8))(param_1);
      cVar3 = '\0';
      FUN_01008290(local_178,s_networking_investment_bap_client_0163993a,param_3,uVar5);
      FUN_000e4aa0(DAT_026ba508,local_178);
    }
  }
  if (*DAT_01a1f100 == local_38) {
    return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),cVar3);
  }
  uVar6 = thunk_FUN_012aa7f6();
  return uVar6;
}

