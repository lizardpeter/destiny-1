
void FUN_0078af50(long param_1,undefined8 param_2,undefined4 *param_3,undefined4 param_4,
                 undefined8 param_5)

{
  long *plVar1;
  undefined4 local_30 [2];
  long local_28;
  
  plVar1 = DAT_01a1f100;
  local_28 = *DAT_01a1f100;
  local_30[0] = *param_3;
  FUN_000cdbd0(param_2,local_30,param_4,param_5);
  *(short *)(param_1 + 0x2262 + (ulong)*(uint *)(param_1 + 0x2e1c) * 2) = (short)param_4;
  *(int *)(param_1 + 0x2e1c) = *(int *)(param_1 + 0x2e1c) + 1;
  if (*plVar1 == local_28) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

