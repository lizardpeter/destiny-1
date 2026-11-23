
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_007a50e0(long param_1)

{
  byte bVar1;
  int iVar2;
  undefined8 uVar3;
  undefined1 local_158 [320];
  long local_18;
  
  local_18 = *DAT_01a1f100;
  bVar1 = *(byte *)(param_1 + 0x6b8);
  if ((bVar1 & 7) != 0) {
    FUN_007a5250(param_1);
    *(undefined4 *)(param_1 + 0x6bc) = 1;
    bVar1 = *(byte *)(param_1 + 0x6b8);
  }
  if ((bVar1 & 7) == 0) {
    if (*(char *)(param_1 + 0x6b9) == '\0') {
      FUN_007a52d0(param_1);
    }
    FUN_010535d0(param_1 + 0x38,param_1);
    if (*(long *)(param_1 + 0x6b0) == *(long *)(param_1 + 0x6a0)) {
      FUN_00784e50(*(undefined4 *)(param_1 + 0x6c8),*(undefined4 *)(param_1 + 0x6cc));
      *(undefined4 *)(param_1 + 0x6bc) = 3;
    }
    else {
      *(undefined4 *)(param_1 + 0x6bc) = 2;
    }
  }
  iVar2 = FUN_000697a0();
  if (15000 < (uint)(iVar2 - _DAT_026d0120)) {
    if (DAT_026d0128 == '\0') {
      iVar2 = thunk_FUN_012aa7d6(&DAT_026d0128);
      if (iVar2 != 0) {
        DAT_026d0124 = FUN_000e4a10(s_world_controller_state_cleanup__A_0165bca4);
        thunk_FUN_012aa7e6(&DAT_026d0128);
      }
    }
    uVar3 = FUN_007850c0();
    FUN_01008290(local_158,s_world_controller_state_cleanup__A_0165bca4,uVar3,
                 *(undefined4 *)(param_1 + 0x6bc),
                 *(ulong *)(param_1 + 0x6a8) ^ *(ulong *)(param_1 + 0x6b0),
                 *(ulong *)(param_1 + 0x6a0) ^ *(ulong *)(param_1 + 0x6a8),
                 *(ulong *)(param_1 + 0x6a0));
    FUN_000e4aa0(DAT_026d0124,local_158);
    _DAT_026d0120 = FUN_000697a0();
  }
  if (*DAT_01a1f100 == local_18) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

