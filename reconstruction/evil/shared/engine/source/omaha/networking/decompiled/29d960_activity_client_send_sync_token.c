
void FUN_0029d960(long *param_1)

{
  long *plVar1;
  undefined8 uVar2;
  undefined4 local_30 [2];
  undefined4 local_28 [2];
  long local_20;
  
  plVar1 = DAT_01a1f100;
  local_20 = *DAT_01a1f100;
  local_30[0] = *(undefined4 *)((long)param_1 + 0x64ac);
  uVar2 = (**(code **)(*param_1 + 0x10))();
  local_28[0] = 0;
  FUN_00299d10(param_1,uVar2,0x1c,*(undefined4 *)PTR_DAT_0191a3e8,local_30,4,local_28);
  if (*plVar1 == local_20) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

