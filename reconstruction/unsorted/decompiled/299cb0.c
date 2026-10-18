
void FUN_00299cb0(undefined8 param_1,undefined8 param_2,undefined8 param_3,undefined4 param_4)

{
  long *plVar1;
  undefined4 local_20 [2];
  long local_18;
  
  plVar1 = DAT_01a1f100;
  local_18 = *DAT_01a1f100;
  local_20[0] = 1;
  FUN_00299d10(param_1,param_2,6,0xffffffff,param_3,param_4,local_20);
  if (*plVar1 == local_18) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

