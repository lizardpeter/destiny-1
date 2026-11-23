
ulong FUN_00b2cab0(long param_1,undefined8 param_2,undefined8 param_3,int param_4)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  ulong uVar4;
  int local_f8 [16];
  long local_b8 [16];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  iVar1 = *(int *)(param_1 + 0x20);
  uVar4 = 0;
  if (iVar1 != 0) {
    local_b8[0] = param_1 + 0x24 + (long)*(int *)(param_1 + 0x1c);
    iVar3 = *(int *)(param_1 + 0x18) - *(int *)(param_1 + 0x1c);
    uVar4 = 1;
    local_f8[0] = iVar1;
    if (iVar3 < iVar1) {
      local_b8[1] = param_1 + 0x24;
      local_f8[1] = iVar1 - iVar3;
      uVar4 = 2;
      local_f8[0] = iVar3;
    }
  }
  if (0 < param_4) {
    thunk_FUN_012aa7c6(local_b8 + uVar4,param_2,(ulong)(param_4 - 1) * 8 + 8);
    thunk_FUN_012aa7c6(local_f8 + uVar4,param_3,(ulong)(param_4 - 1) * 4 + 4);
    uVar4 = (ulong)(uint)((int)uVar4 + param_4);
  }
  uVar2 = thunk_FUN_002e7600(*(undefined8 *)(param_1 + 8),local_b8,local_f8,uVar4);
  if ((int)uVar2 < 1) {
    uVar4 = 0xfffffffe;
    if (uVar2 != 0xfffffffe) {
      *(uint *)(param_1 + 0x10) = uVar2;
      uVar4 = (ulong)uVar2;
    }
  }
  else {
    iVar1 = *(int *)(param_1 + 0x20);
    uVar4 = (ulong)(uVar2 - iVar1);
    if (uVar2 - iVar1 == 0 || (int)uVar2 < iVar1) {
      *(int *)(param_1 + 0x1c) = (int)(*(int *)(param_1 + 0x1c) + uVar2) % *(int *)(param_1 + 0x18);
      *(uint *)(param_1 + 0x20) = iVar1 - uVar2;
      uVar4 = 0xfffffffe;
    }
    else {
      *(undefined4 *)(param_1 + 0x1c) = 0;
      *(undefined4 *)(param_1 + 0x20) = 0;
    }
  }
  if (*DAT_01a1f100 == local_38) {
    return uVar4;
  }
  uVar4 = thunk_FUN_012aa7f6();
  return uVar4;
}

