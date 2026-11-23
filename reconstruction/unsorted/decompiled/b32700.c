
undefined8 FUN_00b32700(long param_1)

{
  char cVar1;
  int iVar2;
  undefined8 uVar3;
  undefined1 uVar4;
  undefined1 local_170 [320];
  long local_30;
  
  local_30 = *DAT_01a1f100;
  cVar1 = FUN_00b336f0(param_1 + 0x90);
  uVar4 = 1;
  if (cVar1 == '\0') {
    if (DAT_0282d960 == '\0') {
      iVar2 = thunk_FUN_012aa7d6(&DAT_0282d960);
      if (iVar2 != 0) {
        DAT_0282d958 = FUN_000e4a10(s_networking_server_bap____s____s__0168a414);
        thunk_FUN_012aa7e6(&DAT_0282d960);
      }
    }
    uVar4 = 0;
    FUN_01008290(local_170,s_networking_server_bap____s____s__0168a414,param_1 + 0x1148,
                 (&PTR_s__none_0196bc80)[*(uint *)(param_1 + 0x1144)]);
    FUN_000e4aa0(DAT_0282d958,local_170);
    if (DAT_0282d970 == '\0') {
      iVar2 = thunk_FUN_012aa7d6(&DAT_0282d970);
      if (iVar2 != 0) {
        DAT_0282d968 = FUN_000e4a10(s_networking_server_bap____s____s__0168a461);
        thunk_FUN_012aa7e6(&DAT_0282d970);
      }
    }
    FUN_01008290(local_170,s_networking_server_bap____s____s__0168a461,param_1 + 0x1148,
                 (&PTR_s__none_0196bc80)[*(uint *)(param_1 + 0x1144)]);
    FUN_000e4aa0(DAT_0282d968,local_170);
    FUN_00b2e400(param_1,0x2c);
  }
  if (*DAT_01a1f100 == local_30) {
    return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),uVar4);
  }
  uVar3 = thunk_FUN_012aa7f6();
  return uVar3;
}

