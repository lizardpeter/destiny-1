
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_007927b0(void)

{
  char cVar1;
  int iVar2;
  long lVar3;
  undefined8 uVar4;
  undefined1 local_160 [320];
  long local_20;
  
  local_20 = *DAT_01a1f100;
  cVar1 = FUN_002e80d0();
  if (cVar1 == '\0') {
    iVar2 = FUN_000697a0();
    uVar4 = 2;
    if (30000 < (uint)(iVar2 - _DAT_026cf968)) {
      if (DAT_026cf970 == '\0') {
        iVar2 = thunk_FUN_012aa7d6(&DAT_026cf970);
        if (iVar2 != 0) {
          DAT_026cf96c = FUN_000e4a10(s_world_controller_state_manager__N_01659a2f);
          thunk_FUN_012aa7e6(&DAT_026cf970);
        }
      }
      FUN_01008290(local_160,s_world_controller_state_manager__N_01659a2f);
      FUN_000e4aa0(DAT_026cf96c,local_160);
      _DAT_026cf968 = FUN_000697a0();
    }
  }
  else {
    lVar3 = FUN_00aea0b0();
    if (lVar3 == 0) {
      iVar2 = FUN_000697a0();
      uVar4 = 2;
      if (30000 < (uint)(iVar2 - _DAT_026cf978)) {
        if (DAT_026cf980 == '\0') {
          iVar2 = thunk_FUN_012aa7d6(&DAT_026cf980);
          if (iVar2 != 0) {
            DAT_026cf97c = FUN_000e4a10(s_world_controller_state_manager__A_01659a6d);
            thunk_FUN_012aa7e6(&DAT_026cf980);
          }
        }
        FUN_01008290(local_160,s_world_controller_state_manager__A_01659a6d);
        FUN_000e4aa0(DAT_026cf97c,local_160);
        _DAT_026cf978 = FUN_000697a0();
      }
    }
    else {
      uVar4 = FUN_00aea0b0();
      cVar1 = FUN_00b01930(uVar4);
      uVar4 = 0;
      if (cVar1 == '\0') {
        iVar2 = FUN_000697a0();
        uVar4 = 2;
        if (30000 < (uint)(iVar2 - _DAT_026cf988)) {
          if (DAT_026cf990 == '\0') {
            iVar2 = thunk_FUN_012aa7d6(&DAT_026cf990);
            if (iVar2 != 0) {
              DAT_026cf98c = FUN_000e4a10(s_world_controller_state_manager__A_01659ad0);
              thunk_FUN_012aa7e6(&DAT_026cf990);
            }
          }
          FUN_01008290(local_160,s_world_controller_state_manager__A_01659ad0);
          FUN_000e4aa0(DAT_026cf98c,local_160);
          _DAT_026cf988 = FUN_000697a0();
        }
      }
    }
  }
  if (*DAT_01a1f100 == local_20) {
    return uVar4;
  }
  uVar4 = thunk_FUN_012aa7f6();
  return uVar4;
}

