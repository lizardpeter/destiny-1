
void FUN_00576410(undefined8 param_1,long *param_2)

{
  long *plVar1;
  undefined8 uVar2;
  undefined1 local_29;
  long local_28;
  
  plVar1 = DAT_01a1f100;
  local_28 = *DAT_01a1f100;
  uVar2 = (**(code **)(*param_2 + 0x18))(param_2);
  uVar2 = FUN_00584560(uVar2);
  local_29 = 0;
  (**(code **)(*param_2 + 0x40))(param_2);
  FUN_00554b90(uVar2,param_2,&local_29);
  if (*plVar1 == local_28) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

