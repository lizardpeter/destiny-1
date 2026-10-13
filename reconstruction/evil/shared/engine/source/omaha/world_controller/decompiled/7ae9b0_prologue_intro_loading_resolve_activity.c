
undefined8 FUN_007ae9b0(void)

{
  char cVar1;
  int iVar2;
  undefined8 uVar3;
  char *pcVar4;
  undefined8 uVar5;
  undefined1 uVar6;
  undefined4 uVar7;
  undefined4 local_170 [2];
  undefined1 local_168 [320];
  long local_28;
  
  local_28 = *DAT_01a1f100;
  uVar3 = FUN_003409a0();
  pcVar4 = (char *)FUN_0075f040();
  if ((pcVar4 == (char *)0x0) || (*pcVar4 == '\0')) {
    cVar1 = FUN_000e4d70(5,4);
    uVar6 = 0;
    if (cVar1 == '\0') goto LAB_007aebc0;
    if (DAT_026d08d8 == '\0') {
      iVar2 = thunk_FUN_012aa7d6(&DAT_026d08d8);
      if (iVar2 != 0) {
        DAT_026d08d0 = FUN_000e4a10(s_world_controller_state_prologue__0165e77d);
        thunk_FUN_012aa7e6(&DAT_026d08d8);
      }
    }
    FUN_01008290(local_168,s_world_controller_state_prologue__0165e77d);
    uVar7 = DAT_026d08d0;
  }
  else {
    cVar1 = FUN_00340cf0(uVar3);
    if (cVar1 == '\0') {
      cVar1 = FUN_00340d10(uVar3,pcVar4);
      if (cVar1 == '\0') {
        cVar1 = FUN_000e4d70(5,4);
        uVar6 = 0;
        if (cVar1 != '\0') {
          if (DAT_026d08f8 == '\0') {
            iVar2 = thunk_FUN_012aa7d6(&DAT_026d08f8);
            if (iVar2 != 0) {
              DAT_026d08f0 = FUN_000e4a10(s_world_controller_state_prologue__0165e842);
              thunk_FUN_012aa7e6(&DAT_026d08f8);
            }
          }
          uVar6 = 0;
          FUN_01008290(local_168,s_world_controller_state_prologue__0165e842,pcVar4);
          FUN_000e4aa0(DAT_026d08f0,local_168);
        }
      }
      else {
        FUN_00340f30(uVar3,pcVar4);
        uVar5 = FUN_00078970(uVar3);
        iVar2 = FUN_00064e90(uVar5,pcVar4);
        if (iVar2 != 0) {
          local_170[0] = 1;
          FUN_00341050(uVar3,local_170);
        }
        FUN_00341960(uVar3);
        uVar6 = 1;
      }
      goto LAB_007aebc0;
    }
    cVar1 = FUN_000e4d70(5,4);
    uVar6 = 0;
    if (cVar1 == '\0') goto LAB_007aebc0;
    if (DAT_026d08e8 == '\0') {
      iVar2 = thunk_FUN_012aa7d6(&DAT_026d08e8);
      if (iVar2 != 0) {
        DAT_026d08e0 = FUN_000e4a10(s_world_controller_state_prologue__0165e7cc);
        thunk_FUN_012aa7e6(&DAT_026d08e8);
      }
    }
    FUN_01008290(local_168,s_world_controller_state_prologue__0165e7cc);
    uVar7 = DAT_026d08e0;
  }
  uVar6 = 0;
  FUN_000e4aa0(uVar7,local_168);
LAB_007aebc0:
  if (*DAT_01a1f100 == local_28) {
    return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),uVar6);
  }
  uVar3 = thunk_FUN_012aa7f6();
  return uVar3;
}

