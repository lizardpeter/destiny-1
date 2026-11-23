
undefined1 FUN_00545280(undefined4 param_1)

{
  char cVar1;
  long *plVar2;
  long lVar3;
  undefined1 uVar4;
  
  uVar4 = 0xff;
  if ((short)param_1 != -1) {
    cVar1 = FUN_0025cc10();
    if (cVar1 != '\0') {
      plVar2 = (long *)FUN_0025cbd0();
      lVar3 = (**(code **)(*plVar2 + 800))(plVar2,param_1);
      if (lVar3 != 0) {
        uVar4 = *(undefined1 *)(lVar3 + 0xa9);
      }
    }
  }
  return uVar4;
}

