
void FUN_00bad260(long param_1)

{
  char cVar1;
  int iVar2;
  undefined1 local_340 [320];
  undefined1 local_200 [20];
  undefined4 local_1ec;
  undefined8 local_128;
  undefined8 uStack_120;
  undefined8 local_118;
  undefined1 local_110;
  undefined4 local_10c;
  undefined4 local_108;
  undefined8 local_100;
  undefined8 local_f8;
  undefined2 local_f0;
  undefined1 local_e8 [90];
  undefined1 local_8e;
  undefined8 local_58;
  undefined8 local_50;
  undefined8 local_48;
  undefined8 local_40;
  undefined8 local_38;
  undefined4 local_30;
  undefined8 local_2c;
  long local_20;
  
  local_20 = *DAT_01a1f100;
  local_10c = 0;
  local_108 = 0;
  local_128 = 0;
  uStack_120 = 0;
  local_110 = 0;
  local_118 = 0;
  local_f0 = 0;
  local_f8 = 0;
  local_100 = 0;
  thunk_FUN_012aa986(local_e8,0,0x90);
  local_8e = 0xff;
  local_38 = 0;
  local_40 = 0;
  local_48 = 0;
  local_50 = 0;
  local_58 = 0xffffffff;
  local_30 = 0;
  local_2c = 0;
  local_1ec = 1;
  FUN_00072240(local_200,*(undefined8 *)(param_1 + 8),*(undefined4 *)(param_1 + 4));
  FUN_00072400(local_200);
  FUN_00ba4190(local_200,&local_128);
  cVar1 = FUN_00072210(local_200);
  if (cVar1 == '\0') {
    cVar1 = FUN_00ba9330(&local_128);
    if (cVar1 == '\0') {
      cVar1 = FUN_000e4d70(0x10,4);
      if (cVar1 != '\0') {
        if (DAT_028a6428 == '\0') {
          iVar2 = thunk_FUN_012aa7d6(&DAT_028a6428);
          if (iVar2 != 0) {
            DAT_028a6424 = FUN_000e4a10(s_networking_simulation_player_upd_01697d20);
            thunk_FUN_012aa7e6(&DAT_028a6428);
          }
        }
        FUN_01008290(local_340,s_networking_simulation_player_upd_01697d20);
        FUN_000e4aa0(DAT_028a6424,local_340);
      }
    }
  }
  FUN_00072650(local_200);
  if (*DAT_01a1f100 == local_20) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

