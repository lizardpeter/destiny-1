
void FUN_00b2ccd0(long param_1,undefined8 param_2,undefined4 param_3)

{
  long *plVar1;
  undefined4 local_24;
  undefined8 local_20;
  long local_18;
  
  plVar1 = DAT_01a1f100;
  local_18 = *DAT_01a1f100;
  local_24 = param_3;
  local_20 = param_2;
  if (*(int *)(param_1 + 0x10) == 1) {
    if (*(int *)(param_1 + 0x14) < 0) {
      FUN_002e5370(*(undefined8 *)(param_1 + 8));
    }
    else {
      FUN_00b2cd30(param_1,&local_20,&local_24,1);
    }
  }
  if (*plVar1 == local_18) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

