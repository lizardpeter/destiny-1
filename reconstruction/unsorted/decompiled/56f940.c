
void FUN_0056f940(undefined8 *param_1,undefined8 param_2,int param_3,undefined8 param_4,int param_5)

{
  undefined8 uVar1;
  
  if (param_3 == 4) {
    if (param_5 == 4) {
      FUN_0056f9d0(param_1,0);
      return;
    }
    if (param_5 == 1) {
      uVar1 = FUN_00557c40(&DAT_026bc508);
      uVar1 = FUN_00586750(uVar1,*param_1);
      FUN_002f1dc0(uVar1);
      return;
    }
    if (param_5 == 0) {
      FUN_0057e060();
      return;
    }
  }
  return;
}

