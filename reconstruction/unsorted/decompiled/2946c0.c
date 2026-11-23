
void FUN_002946c0(undefined8 param_1,undefined8 param_2,undefined8 param_3)

{
  ulong uVar1;
  
  uVar1 = (ulong)DAT_026534e0;
  (&DAT_026532a0)[uVar1 * 3] = param_1;
  (&DAT_026532b0)[uVar1 * 3] = param_2;
  (&DAT_026532a8)[uVar1 * 3] = param_3;
  DAT_026534e0 = DAT_026534e0 + 1;
  return;
}

