
void FUN_00b2cbf0(long param_1)

{
  int iVar1;
  undefined8 uVar2;
  int iVar3;
  int local_d8;
  int local_d4;
  long local_98;
  long local_90;
  long local_18;
  
  local_18 = *DAT_01a1f100;
  iVar1 = *(int *)(param_1 + 0x20);
  if (iVar1 != 0) {
    local_98 = param_1 + 0x24 + (long)*(int *)(param_1 + 0x1c);
    iVar3 = *(int *)(param_1 + 0x18) - *(int *)(param_1 + 0x1c);
    uVar2 = 1;
    local_d8 = iVar1;
    if (iVar3 < iVar1) {
      local_90 = param_1 + 0x24;
      local_d4 = iVar1 - iVar3;
      uVar2 = 2;
      local_d8 = iVar3;
    }
    iVar1 = thunk_FUN_002e7600(*(undefined8 *)(param_1 + 8),&local_98,&local_d8,uVar2);
    if (iVar1 < 1) {
      if (iVar1 != -2) {
        *(int *)(param_1 + 0x10) = iVar1;
      }
    }
    else if (*(int *)(param_1 + 0x20) < iVar1) {
      *(undefined8 *)(param_1 + 0x1c) = 0;
    }
    else {
      *(int *)(param_1 + 0x1c) = (*(int *)(param_1 + 0x1c) + iVar1) % *(int *)(param_1 + 0x18);
      *(int *)(param_1 + 0x20) = *(int *)(param_1 + 0x20) - iVar1;
    }
  }
  if (*DAT_01a1f100 == local_18) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

