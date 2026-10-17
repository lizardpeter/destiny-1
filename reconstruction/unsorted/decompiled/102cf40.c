
void FUN_0102cf40(undefined8 *param_1)

{
  long *plVar1;
  undefined8 uVar2;
  ulong local_38;
  undefined8 uStack_30;
  undefined8 local_28;
  long local_20;
  
  plVar1 = DAT_01a1f100;
  local_20 = *DAT_01a1f100;
  local_38 = 0;
  uStack_30 = 0;
  local_28 = 0;
  FUN_0102c320(&local_38);
  uVar2 = FUN_00071fe0(local_38 & 0xffffffff);
  *param_1 = uVar2;
  param_1[1] = uStack_30;
  *(undefined4 *)(param_1 + 2) = (undefined4)local_28;
  if (*plVar1 == local_20) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

