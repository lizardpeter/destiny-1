
undefined4 FUN_0006c530(undefined1 *param_1,undefined8 param_2,undefined8 param_3)

{
  undefined4 uVar1;
  
  *(undefined8 *)(param_1 + 8) = param_3;
  thunk_FUN_012aa7c6(param_1 + 0x10);
  uVar1 = FUN_00f6c200(&PTR_DAT_01a111b8);
  *(undefined4 *)(param_1 + 4) = uVar1;
  *param_1 = 1;
  return 1;
}

