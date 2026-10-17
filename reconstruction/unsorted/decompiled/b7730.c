
void FUN_000b7730(long *param_1)

{
  undefined1 uVar1;
  
  param_1 = (long *)*param_1;
  uVar1 = (**(code **)(*param_1 + 0x28))(param_1);
  *(undefined1 *)(param_1 + 6) = uVar1;
  return;
}

