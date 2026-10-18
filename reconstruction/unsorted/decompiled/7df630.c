
undefined8 FUN_007df630(long param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined8 uVar1;
  undefined1 local_48 [16];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  uVar1 = FUN_00f7feb0(*(undefined8 *)(param_1 + 0x50),param_4,4);
  FUN_00f7d180(local_48,uVar1,param_4);
  FUN_00f7d010(local_48,0x10);
  FUN_00f8b500(*(long *)(param_1 + 0x50) + 0xc0,param_2,param_3,1,local_48);
  if (*DAT_01a1f100 == local_38) {
    return uVar1;
  }
  uVar1 = thunk_FUN_012aa7f6();
  return uVar1;
}

