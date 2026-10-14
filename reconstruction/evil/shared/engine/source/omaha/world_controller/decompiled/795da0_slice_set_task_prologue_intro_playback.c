
ulong FUN_00795da0(long param_1)

{
  char cVar1;
  int iVar2;
  ulong uVar3;
  uint uVar4;
  undefined1 local_160 [320];
  long local_20;
  
  local_20 = *DAT_01a1f100;
  uVar4 = 2;
  if (((*(byte *)(param_1 + 0x1a8) & 0x10) == 0) &&
     (uVar4 = 1, (*(byte *)(param_1 + 0x1a0) & 0x10) == 0)) {
    uVar4 = (*(uint *)(param_1 + 0x198) >> 4 & 1) - 1;
  }
  cVar1 = FUN_00766750();
  if (cVar1 == '\0') {
    if (uVar4 == 0) {
      FUN_00765d90(0);
      uVar4 = 1;
    }
    cVar1 = FUN_00765c40();
    if (cVar1 == '\0') {
      cVar1 = FUN_00765ea0();
      uVar3 = 2;
      if (cVar1 != '\0') {
        uVar3 = (ulong)uVar4;
      }
      if (*DAT_01a1f100 == local_20) {
        return uVar3;
      }
      goto LAB_00795ec3;
    }
  }
  else {
    cVar1 = FUN_000e4d70(5,1);
    uVar4 = 2;
    if (cVar1 != '\0') {
      if ((DAT_026cfbd8 == '\0') && (iVar2 = thunk_FUN_012aa7d6(&DAT_026cfbd8), iVar2 != 0)) {
        DAT_026cfbd0 = FUN_000e4a10(s_world_controller_state_activity__0165a984);
        thunk_FUN_012aa7e6(&DAT_026cfbd8);
      }
      FUN_01008290(local_160,s_world_controller_state_activity__0165a984);
      FUN_000e4aa0(DAT_026cfbd0,local_160);
    }
  }
  if (*DAT_01a1f100 == local_20) {
    return (ulong)uVar4;
  }
LAB_00795ec3:
  uVar3 = thunk_FUN_012aa7f6();
  return uVar3;
}

