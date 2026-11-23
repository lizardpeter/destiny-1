
ulong FUN_0094c160(ulong *param_1,undefined8 param_2)

{
  ulong uVar1;
  ulong uVar2;
  ulong uVar3;
  int *piVar4;
  long lVar5;
  int local_50 [2];
  undefined4 local_48 [2];
  undefined8 local_40;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  uVar1 = *param_1;
  uVar3 = 0;
  if (uVar1 != 0) {
    uVar1 = uVar1 + (long)param_1;
    uVar3 = uVar1;
  }
  piVar4 = (int *)(uVar3 + 0x10);
  lVar5 = (ulong)(uint)param_1[1] << 5;
  do {
    uVar1 = CONCAT71((int7)(uVar1 >> 8),1);
    if (lVar5 == 0) break;
    local_48[0] = 0x811c9dc5;
    local_40 = 0;
    if (((*(byte *)(uVar3 + 0x1b) & 3) == 2) && (*piVar4 != -0x7ee3623b)) {
      local_50[0] = *piVar4;
      FUN_0094b0f0(local_50,local_48);
    }
    uVar2 = FUN_008da9d0(uVar3,param_2,local_48,1);
    lVar5 = lVar5 + -0x20;
    piVar4 = piVar4 + 8;
    uVar3 = uVar3 + 0x20;
    uVar1 = uVar2 & 0xffffffffffffff00;
  } while ((char)uVar2 != '\0');
  if (*DAT_01a1f100 == local_38) {
    return uVar1;
  }
  uVar1 = thunk_FUN_012aa7f6();
  return uVar1;
}

