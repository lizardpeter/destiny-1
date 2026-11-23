
void FUN_00923370(int param_1,int param_2,undefined1 param_3)

{
  long lVar1;
  
  lVar1 = (long)param_1;
  if (*(int *)(DAT_0273eb80 + 0xc4 + lVar1 * 4) != param_2) {
    if (param_2 != -1) {
      FUN_00923370(param_1,0xffffffff,param_3);
      *(int *)(DAT_0273eb80 + 0xc4 + lVar1 * 4) = param_2;
      FUN_0091b490(param_1,param_2);
      FUN_0090a340(param_1,param_2,param_3);
      return;
    }
    FUN_0091b490(param_1,0xffffffff);
    FUN_0090a340(param_1,0xffffffff,param_3);
    *(undefined4 *)(DAT_0273eb80 + 0xc4 + lVar1 * 4) = 0xffffffff;
  }
  return;
}

