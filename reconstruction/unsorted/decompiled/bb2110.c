
void FUN_00bb2110(undefined8 param_1,undefined8 *param_2)

{
  long *plVar1;
  undefined8 local_28;
  undefined8 local_20;
  long local_18;
  
  plVar1 = DAT_01a1f100;
  local_18 = *DAT_01a1f100;
  local_20 = *param_2;
  local_28 = param_1;
  FUN_00300230(0x18,*(undefined4 *)PTR_DAT_019b4700,&local_28);
  if (*plVar1 == local_18) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

