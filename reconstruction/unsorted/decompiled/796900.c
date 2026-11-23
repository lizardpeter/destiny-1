
void FUN_00796900(long param_1)

{
  long *plVar1;
  undefined8 uVar2;
  undefined4 local_28 [2];
  long local_20;
  
  plVar1 = DAT_01a1f100;
  local_20 = *DAT_01a1f100;
  *(undefined8 *)(param_1 + 0x1a8) = 0;
  *(undefined8 *)(param_1 + 0x1a0) = 0;
  *(undefined8 *)(param_1 + 0x198) = 0;
  *(undefined8 *)(param_1 + 0x198) = 0x7ff;
  uVar2 = FUN_00765ee0();
  FUN_00758d20(uVar2);
  FUN_00765fb0(10);
  local_28[0] = DAT_026cfbb4;
  FUN_007660d0(local_28);
  FUN_00766080();
  *(undefined8 *)(param_1 + 0x1b0) = 0;
  if (*plVar1 == local_20) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

