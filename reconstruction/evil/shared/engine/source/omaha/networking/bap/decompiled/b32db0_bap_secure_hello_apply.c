
bool FUN_00b32db0(long param_1,long param_2)

{
  char cVar1;
  undefined1 uVar2;
  int iVar3;
  undefined4 uVar4;
  undefined *puVar5;
  undefined8 local_1d8;
  undefined4 local_1cc;
  undefined1 local_1c8 [320];
  undefined local_88 [88];
  long local_30;
  
  local_30 = *DAT_01a1f100;
  puVar5 = local_88;
  FUN_00b34f40(puVar5);
  if (*(int *)(param_1 + 8) == 0) {
    puVar5 = &DAT_0282da48;
  }
  local_1cc = 0;
  local_1d8 = 0;
  FUN_00b34f70(puVar5,param_1 + 0x2539,param_1 + 0x2549);
  cVar1 = FUN_00b34fe0(puVar5,param_2,*(undefined8 *)(param_2 + 0x5c),&local_1d8,&local_1cc);
  if (cVar1 == '\0') {
    if (DAT_0282d9b0 == '\0') {
      iVar3 = thunk_FUN_012aa7d6(&DAT_0282d9b0);
      if (iVar3 != 0) {
        DAT_0282d9a8 = FUN_000e4a10(s_networking_server_bap____s____s__0168a5d1);
        thunk_FUN_012aa7e6(&DAT_0282d9b0);
      }
    }
    cVar1 = '\0';
    FUN_01008290(local_1c8,s_networking_server_bap____s____s__0168a5d1,param_1 + 0x1148,
                 (&PTR_s__none_0196bc80)[*(uint *)(param_1 + 0x1144)]);
    FUN_000e4aa0(DAT_0282d9a8,local_1c8);
    FUN_00b2e400(param_1,0x25);
  }
  else {
    cVar1 = FUN_00b34d80((long)&PTR_DAT_00001eb8 + param_1,param_2 + 0xc,param_2);
    if (cVar1 == '\0') {
      if (DAT_0282d9a0 == '\0') {
        iVar3 = thunk_FUN_012aa7d6(&DAT_0282d9a0);
        if (iVar3 != 0) {
          DAT_0282d998 = FUN_000e4a10(s_networking_server_bap____s____s__0168a55a);
          thunk_FUN_012aa7e6(&DAT_0282d9a0);
        }
      }
      puVar5 = (&PTR_s__none_0196bc80)[*(uint *)(param_1 + 0x1144)];
      uVar4 = FUN_00b333d0();
      FUN_01008290(local_1c8,s_networking_server_bap____s____s__0168a55a,param_1 + 0x1148,puVar5,
                   uVar4);
      FUN_000e4aa0(DAT_0282d998,local_1c8);
    }
  }
  if (*DAT_01a1f100 == local_30) {
    return cVar1 != '\0';
  }
  uVar2 = thunk_FUN_012aa7f6();
  return (bool)uVar2;
}

