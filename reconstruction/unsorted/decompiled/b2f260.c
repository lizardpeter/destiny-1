
undefined8 FUN_00b2f260(long param_1,undefined8 param_2)

{
  char cVar1;
  int iVar2;
  undefined8 uVar3;
  undefined4 uVar4;
  undefined1 uVar5;
  undefined1 local_168 [320];
  long local_28;
  
  local_28 = *DAT_01a1f100;
  cVar1 = FUN_00b2f3d0();
  if (cVar1 == '\0') {
    if (DAT_0282d660 == '\0') {
      iVar2 = thunk_FUN_012aa7d6(&DAT_0282d660);
      if (iVar2 != 0) {
        DAT_0282d658 = FUN_000e4a10(s_networking_server_bap____s____s__0168936d);
        thunk_FUN_012aa7e6(&DAT_0282d660);
      }
    }
    FUN_01008290(local_168,s_networking_server_bap____s____s__0168936d,param_1 + 0x1148,
                 (&PTR_s__none_0196bc80)[*(uint *)(param_1 + 0x1144)]);
    uVar4 = DAT_0282d658;
  }
  else {
    cVar1 = FUN_00b2f520(param_1,param_2);
    uVar5 = 1;
    if (cVar1 != '\0') goto LAB_00b2f399;
    if (DAT_0282d670 == '\0') {
      iVar2 = thunk_FUN_012aa7d6(&DAT_0282d670);
      if (iVar2 != 0) {
        DAT_0282d668 = FUN_000e4a10(s_networking_server_bap____s____s__016893af);
        thunk_FUN_012aa7e6(&DAT_0282d670);
      }
    }
    FUN_01008290(local_168,s_networking_server_bap____s____s__016893af,param_1 + 0x1148,
                 (&PTR_s__none_0196bc80)[*(uint *)(param_1 + 0x1144)]);
    uVar4 = DAT_0282d668;
  }
  uVar5 = 0;
  FUN_000e4aa0(uVar4,local_168);
LAB_00b2f399:
  if (*DAT_01a1f100 == local_28) {
    return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),uVar5);
  }
  uVar3 = thunk_FUN_012aa7f6();
  return uVar3;
}

