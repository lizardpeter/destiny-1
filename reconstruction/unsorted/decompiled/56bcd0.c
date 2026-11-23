
void FUN_0056bcd0(long param_1,undefined4 param_2,undefined8 *param_3,int param_4)

{
  long lVar1;
  long lVar2;
  
  lVar1 = 0x60;
  while ((*(char *)(param_1 + lVar1) != (char)param_2 || (*(long *)(param_1 + 0x20 + lVar1) != 0)))
  {
    lVar1 = lVar1 + 0x40;
    lVar2 = 0;
    if ((int)lVar1 == 0x40a0) {
LAB_0056bd06:
      *(undefined8 *)(lVar2 + 0x20) = *param_3;
      if (param_4 != 2) {
        if (param_4 == 1) {
          *(undefined1 *)(lVar2 + 0x28) = 1;
          return;
        }
        if (param_4 != 0) {
          return;
        }
        FUN_005523b0(param_2,param_3);
      }
      *(undefined1 *)(lVar2 + 0x28) = 2;
      return;
    }
  }
  lVar2 = param_1 + lVar1;
  goto LAB_0056bd06;
}

