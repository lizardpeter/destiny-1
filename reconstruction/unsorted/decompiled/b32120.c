
undefined8
FUN_00b32120(long param_1,int param_2,int param_3,long param_4,int param_5,long param_6,int param_7,
            int *param_8,undefined4 *param_9)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  undefined8 uVar4;
  int iVar5;
  undefined1 uVar6;
  undefined1 local_190 [320];
  int local_50;
  int local_4c;
  long local_48;
  long local_40;
  long local_38;
  
  iVar5 = param_5 - param_3;
  local_38 = *DAT_01a1f100;
  if ((param_6 == 0) || (param_7 == 0)) {
    if (iVar5 <= param_2) {
      param_2 = iVar5;
    }
  }
  else {
    if (param_3 < param_5) {
      local_50 = iVar5;
      if (param_2 < iVar5) {
        local_50 = param_2;
      }
      local_4c = param_2 - local_50;
      if (param_7 < param_2 - local_50) {
        local_4c = param_7;
      }
      local_48 = param_4;
      local_40 = param_6;
      iVar1 = FUN_00b2cd30(param_1 + 0x1220,&local_48,&local_50,2);
      goto LAB_00b32178;
    }
    iVar1 = param_7 - (param_3 - param_5);
    if (param_2 < iVar1) {
      iVar1 = param_2;
    }
    param_4 = param_6 + (param_3 - param_5);
    param_2 = iVar1;
  }
  iVar1 = FUN_00b2ccd0(param_1 + 0x1220,param_4,param_2);
LAB_00b32178:
  if (iVar1 < 1) {
    if (iVar1 == 0) {
      if ((DAT_0282d830 == '\0') && (iVar1 = thunk_FUN_012aa7d6(&DAT_0282d830), iVar1 != 0)) {
        DAT_0282d828 = FUN_000e4a10(s_networking_server_bap____s____s__01689df0);
        thunk_FUN_012aa7e6(&DAT_0282d830);
      }
      uVar6 = 0;
      FUN_01008290(local_190,s_networking_server_bap____s____s__01689df0,param_1 + 0x1148,
                   (&PTR_s__none_0196bc80)[*(uint *)(param_1 + 0x1144)],iVar5 + param_7,
                   param_1 + 0x1680);
      FUN_000e4aa0(DAT_0282d828,local_190);
      iVar1 = 0;
      uVar2 = 0x1d;
    }
    else if (iVar1 == -2) {
      if (*(char *)(param_1 + 0x2288) == '\0') {
        uVar4 = DAT_026553b0;
        if (DAT_026553a8 == '\0') {
          uVar4 = FUN_000694d0();
        }
        *(undefined8 *)(param_1 + 0x2290) = uVar4;
      }
      FUN_00297fe0(&DAT_00002298 + param_1,1);
      uVar6 = 1;
      uVar2 = 0;
      iVar1 = 0;
    }
    else {
      if ((DAT_0282d840 == '\0') && (iVar3 = thunk_FUN_012aa7d6(&DAT_0282d840), iVar3 != 0)) {
        DAT_0282d838 = FUN_000e4a10(s_networking_server_bap____s____s__01689e53);
        thunk_FUN_012aa7e6(&DAT_0282d840);
      }
      uVar6 = 0;
      FUN_01008290(local_190,s_networking_server_bap____s____s__01689e53,param_1 + 0x1148,
                   (&PTR_s__none_0196bc80)[*(uint *)(param_1 + 0x1144)],iVar1,iVar5 + param_7,
                   param_1 + 0x1680);
      FUN_000e4aa0(DAT_0282d838,local_190);
      iVar1 = 0;
      uVar2 = 0x1e;
    }
  }
  else {
    uVar4 = DAT_026553b0;
    if (DAT_026553a8 == '\0') {
      uVar4 = FUN_000694d0();
    }
    *(undefined8 *)(&DAT_00001ef0 + param_1) = uVar4;
    FUN_00297fe0(param_1 + 0x21a8,iVar1);
    uVar6 = 1;
    uVar2 = 0;
  }
  *param_9 = uVar2;
  *param_8 = iVar1;
  if (*DAT_01a1f100 != local_38) {
    uVar4 = thunk_FUN_012aa7f6();
    return uVar4;
  }
  return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),uVar6);
}

