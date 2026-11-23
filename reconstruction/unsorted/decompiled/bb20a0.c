
void FUN_00bb20a0(undefined8 param_1,undefined8 param_2)

{
  long *plVar1;
  undefined8 local_6d0;
  undefined1 local_6c8 [1712];
  long local_18;
  
  plVar1 = DAT_01a1f100;
  local_18 = *DAT_01a1f100;
  local_6d0 = param_1;
  thunk_FUN_012aa7c6(local_6c8,param_2,0x6b0);
  FUN_00300230(0x17,*(undefined4 *)PTR_DAT_019b46f8,&local_6d0);
  if (*plVar1 == local_18) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

