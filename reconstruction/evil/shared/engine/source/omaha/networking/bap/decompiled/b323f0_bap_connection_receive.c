
undefined8
FUN_00b323f0(long param_1,undefined4 param_2,undefined8 param_3,int *param_4,undefined4 *param_5)

{
  int iVar1;
  int iVar2;
  undefined8 uVar3;
  undefined1 uVar4;
  undefined4 uVar5;
  int iVar6;
  undefined1 local_178 [320];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  iVar1 = FUN_002e5360(*(undefined8 *)(param_1 + 0x1218),param_3,param_2);
  if (iVar1 < 1) {
    uVar4 = 1;
    iVar6 = 0;
    if (iVar1 == -2) {
      uVar5 = 0;
      iVar1 = iVar6;
    }
    else if (iVar1 == 0) {
      if ((DAT_0282d860 == '\0') && (iVar1 = thunk_FUN_012aa7d6(&DAT_0282d860), iVar1 != 0)) {
        DAT_0282d858 = FUN_000e4a10(s_networking_server_bap____s____s__01689f09);
        thunk_FUN_012aa7e6(&DAT_0282d860);
      }
      uVar4 = 0;
      FUN_01008290(local_178,s_networking_server_bap____s____s__01689f09,param_1 + 0x1148,
                   (&PTR_s__none_0196bc80)[*(uint *)(param_1 + 0x1144)],param_1 + 0x1680);
      FUN_000e4aa0(DAT_0282d858,local_178);
      uVar5 = 0x1b;
      iVar1 = iVar6;
    }
    else {
      if ((DAT_0282d870 == '\0') && (iVar2 = thunk_FUN_012aa7d6(&DAT_0282d870), iVar2 != 0)) {
        DAT_0282d868 = FUN_000e4a10(s_networking_server_bap____s____s__01689f60);
        thunk_FUN_012aa7e6(&DAT_0282d870);
      }
      uVar4 = 0;
      FUN_01008290(local_178,s_networking_server_bap____s____s__01689f60,param_1 + 0x1148,
                   (&PTR_s__none_0196bc80)[*(uint *)(param_1 + 0x1144)],iVar1,param_1 + 0x1680);
      FUN_000e4aa0(DAT_0282d868,local_178);
      uVar5 = 0x1c;
      iVar1 = iVar6;
    }
  }
  else {
    uVar3 = DAT_026553b0;
    if (DAT_026553a8 == '\0') {
      uVar3 = FUN_000694d0();
    }
    *(undefined8 *)(&DAT_00001ef8 + param_1) = uVar3;
    FUN_00297fe0(param_1 + 0x1fe8,iVar1);
    uVar4 = 1;
    uVar5 = 0;
    if ((*(byte *)(param_1 + 0x10) & 0x20) == 0) {
      FUN_00b2cbf0(param_1 + 0x1220);
      uVar5 = 0;
    }
  }
  *param_5 = uVar5;
  *param_4 = iVar1;
  if (*DAT_01a1f100 != local_38) {
    uVar3 = thunk_FUN_012aa7f6();
    return uVar3;
  }
  return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),uVar4);
}

