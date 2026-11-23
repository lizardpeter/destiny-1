
void FUN_0094bdb0(long param_1,undefined8 param_2)

{
  long *plVar1;
  int local_40 [2];
  undefined4 local_38 [2];
  undefined8 local_30;
  long local_28;
  
  plVar1 = DAT_01a1f100;
  local_28 = *DAT_01a1f100;
  local_38[0] = 0x811c9dc5;
  local_30 = 0;
  if (((*(byte *)(param_1 + 0x1b) & 3) == 2) && (*(int *)(param_1 + 0x10) != -0x7ee3623b)) {
    local_40[0] = *(int *)(param_1 + 0x10);
    FUN_0094b0f0(local_40,local_38);
  }
  FUN_008da9d0(param_1,param_2,local_38,1);
  if (*plVar1 == local_28) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

