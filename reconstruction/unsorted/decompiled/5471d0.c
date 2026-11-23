
undefined8 FUN_005471d0(char param_1)

{
  char cVar1;
  undefined8 uVar2;
  
  uVar2 = 10;
  if (param_1 != '\0') {
    cVar1 = FUN_005428c0();
    if (cVar1 != '\0') {
      uVar2 = FUN_0057d940();
      cVar1 = FUN_0057ce50(uVar2);
      if (cVar1 == '\0') {
        return 1;
      }
    }
    cVar1 = FUN_005a1430();
    uVar2 = 5;
    if (((cVar1 == '\0') && (cVar1 = FUN_0059e1e0(), cVar1 == '\0')) &&
       (cVar1 = FUN_0059ea70(), cVar1 == '\0')) {
      cVar1 = FUN_00b210e0(0);
      uVar2 = 0xc;
      if (cVar1 == '\0') {
        uVar2 = 0;
      }
    }
  }
  return uVar2;
}

