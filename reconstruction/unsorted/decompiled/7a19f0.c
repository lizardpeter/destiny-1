
void FUN_007a19f0(long param_1)

{
  long *plVar1;
  undefined1 local_28 [8];
  long local_20;
  
  plVar1 = DAT_01a1f100;
  local_20 = *DAT_01a1f100;
  *(undefined4 *)(param_1 + 0x38) = 0xffffffff;
  *(undefined1 *)(param_1 + 0x3c) = 0;
  *(undefined8 *)(param_1 + 0x40) = 0x3ffffffff;
  FUN_009828f0(0);
  FUN_007539b0(param_1 + 0x48,0);
  FUN_0078e950(param_1 + 0x30);
  local_28[0] = 1;
  FUN_00300230(0x32,*(undefined4 *)PTR_DAT_019e4cf8,local_28);
  thunk_FUN_0103f400();
  if (*plVar1 == local_20) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

