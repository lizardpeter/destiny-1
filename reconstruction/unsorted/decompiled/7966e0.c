
ulong FUN_007966e0(long param_1)

{
  char cVar1;
  int iVar2;
  undefined4 uVar3;
  undefined8 uVar4;
  undefined8 uVar5;
  undefined8 uVar6;
  uint uVar7;
  ulong uVar8;
  undefined4 local_188 [2];
  undefined4 local_180 [2];
  undefined1 local_178 [320];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  uVar4 = FUN_00765ee0();
  uVar7 = 2;
  if (((*(byte *)(param_1 + 0x1a9) & 4) == 0) && (uVar7 = 1, (*(byte *)(param_1 + 0x1a1) & 4) == 0))
  {
    uVar7 = (*(uint *)(param_1 + 0x198) >> 10 & 1) - 1;
  }
  cVar1 = FUN_00766750();
  if (cVar1 == '\0') {
    local_180[0] = DAT_026cfbbc;
    FUN_00758320(uVar4,local_180);
    if (uVar7 == 0) {
      FUN_00765fb0(0xb);
      uVar3 = FUN_00758d10();
      FUN_000f8520(uVar4,uVar3);
      local_188[0] = DAT_026cfbb0;
      FUN_007660d0(local_188);
      uVar3 = FUN_00758d10();
      uVar7 = 1;
      *(undefined4 *)(param_1 + 0x1b4) = uVar3;
    }
    uVar5 = FUN_003409a0();
    uVar6 = FUN_00078970(uVar5);
    iVar2 = FUN_00765d70();
    uVar8 = 2;
    if (iVar2 != -1) {
      uVar8 = 2;
      cVar1 = FUN_00340e50(uVar5,uVar6,iVar2,2);
      if (cVar1 != '\0') {
        if (0 < *(int *)(param_1 + 0x1b4)) {
          cVar1 = FUN_00756b80(uVar4);
          if (cVar1 != '\0') {
            cVar1 = FUN_00758c40(uVar4);
            if (cVar1 == '\0') {
              *(int *)(param_1 + 0x1b4) = *(int *)(param_1 + 0x1b4) + -1;
              uVar8 = (ulong)uVar7;
              goto LAB_007968c4;
            }
          }
        }
        FUN_000f8520(uVar4,0xffffffff);
        uVar8 = 2;
        FUN_00765d90(2);
        FUN_00765fb0(0xc);
      }
    }
  }
  else {
    cVar1 = FUN_000e4d70(5,1);
    uVar8 = 2;
    if (cVar1 != '\0') {
      if (DAT_026cfc18 == '\0') {
        iVar2 = thunk_FUN_012aa7d6(&DAT_026cfc18);
        if (iVar2 != 0) {
          DAT_026cfc10 = FUN_000e4a10(s_world_controller_state_activity__0165abc9);
          thunk_FUN_012aa7e6(&DAT_026cfc18);
        }
      }
      FUN_01008290(local_178,s_world_controller_state_activity__0165abc9);
      FUN_000e4aa0(DAT_026cfc10,local_178);
    }
  }
LAB_007968c4:
  if (*DAT_01a1f100 == local_38) {
    return uVar8;
  }
  uVar8 = thunk_FUN_012aa7f6();
  return uVar8;
}

