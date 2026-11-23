
void FUN_0078f660(int param_1)

{
  undefined8 uVar1;
  
  if ((param_1 == 4) || (param_1 == 3)) {
    FUN_000596b0();
  }
  uVar1 = 0;
  DAT_026cf430 = param_1;
  if ((long *)(&DAT_026cf438)[param_1] != (long *)0x0) {
    (**(code **)(*(long *)(&DAT_026cf438)[param_1] + 0x40))();
    uVar1 = (&DAT_026cf438)[DAT_026cf430];
  }
  FUN_0033f3a0(uVar1);
  return;
}

