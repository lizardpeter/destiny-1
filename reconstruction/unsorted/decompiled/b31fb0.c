
undefined8
FUN_00b31fb0(long param_1,undefined8 param_2,int param_3,undefined8 param_4,int param_5,int *param_6
            ,undefined8 param_7)

{
  int iVar1;
  char cVar2;
  undefined8 uVar3;
  int iVar4;
  int iVar5;
  undefined1 uVar6;
  int local_17c;
  undefined1 local_178 [320];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  iVar1 = *param_6;
  iVar5 = (param_5 + param_3) - iVar1;
  uVar6 = 1;
  local_17c = 0;
  iVar4 = 0;
  if (0 < iVar5) {
    cVar2 = FUN_00b32120(param_1,iVar5,iVar1,param_2,param_3,param_4,param_5,&local_17c,param_7);
    if (cVar2 == '\0') {
      if (DAT_0282d820 == '\0') {
        iVar4 = thunk_FUN_012aa7d6(&DAT_0282d820);
        if (iVar4 != 0) {
          DAT_0282d818 = FUN_000e4a10(s_networking_server_bap____s____s__01689d9b);
          thunk_FUN_012aa7e6(&DAT_0282d820);
        }
      }
      uVar6 = 0;
      FUN_01008290(local_178,s_networking_server_bap____s____s__01689d9b,param_1 + 0x1148,
                   (&PTR_s__none_0196bc80)[*(uint *)(param_1 + 0x1144)],iVar5,iVar1);
      FUN_000e4aa0(DAT_0282d818,local_178);
      iVar4 = 0;
    }
    else {
      iVar4 = iVar1 + local_17c;
    }
  }
  *param_6 = iVar4;
  if (*DAT_01a1f100 == local_38) {
    return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),uVar6);
  }
  uVar3 = thunk_FUN_012aa7f6();
  return uVar3;
}

