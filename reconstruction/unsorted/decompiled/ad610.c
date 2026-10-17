
void FUN_000ad610(int param_1,undefined8 *param_2)

{
  long lVar1;
  
  lVar1 = (long)DAT_01ad4840;
  *(undefined4 *)(lVar1 * 0x3b0 + 0x1ad4438 + (long)param_1 * 0xc) = *(undefined4 *)(param_2 + 1);
  *(undefined8 *)(lVar1 * 0x3b0 + 0x1ad4430 + (long)param_1 * 0xc) = *param_2;
  return;
}

