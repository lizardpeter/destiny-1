
void FUN_00923010(int param_1,int param_2)

{
  long lVar1;
  
  lVar1 = (long)param_1;
  if (*(int *)(DAT_0273eb80 + 8 + lVar1 * 4) != param_2) {
    if (param_2 != -1) {
      FUN_00923010(param_1,0xffffffff);
      *(int *)(DAT_0273eb80 + 8 + lVar1 * 4) = param_2;
      FUN_0091b2a0(param_1,param_2);
      return;
    }
    FUN_0091b2a0();
    *(undefined4 *)(DAT_0273eb80 + 8 + lVar1 * 4) = 0xffffffff;
  }
  return;
}

