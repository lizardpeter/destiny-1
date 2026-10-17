
undefined1 FUN_0097df40(long param_1,short param_2,short *param_3)

{
  long lVar1;
  undefined1 uVar2;
  
  if (param_2 < 2) {
    *param_3 = param_2 + 1;
    return 1;
  }
  lVar1 = *(long *)(param_1 + 0x90);
  uVar2 = 0;
  if (param_2 == 2) {
    if (lVar1 != 0) {
      *param_3 = 0x200;
      return 1;
    }
  }
  else if (lVar1 != 0) {
    uVar2 = FUN_0097e390(lVar1,(int)param_2);
  }
  return uVar2;
}

