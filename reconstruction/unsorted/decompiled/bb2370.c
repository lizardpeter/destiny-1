
void FUN_00bb2370(undefined8 param_1)

{
  long *plVar1;
  undefined8 local_20;
  long local_18;
  
  plVar1 = DAT_01a1f100;
  local_18 = *DAT_01a1f100;
  local_20 = param_1;
  FUN_00300230(0x1c,*(undefined4 *)PTR_DAT_019b4720,&local_20);
  if (*plVar1 == local_18) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

