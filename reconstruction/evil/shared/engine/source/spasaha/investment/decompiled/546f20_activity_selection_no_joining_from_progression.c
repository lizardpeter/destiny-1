
undefined1 FUN_00546f20(undefined8 param_1)

{
  long lVar1;
  char cVar2;
  undefined1 uVar3;
  long *plVar4;
  
  cVar2 = FUN_0025cc10();
  uVar3 = 0;
  if (cVar2 != '\0') {
    plVar4 = (long *)FUN_0025a550();
    lVar1 = (**(code **)(*plVar4 + 0x68))(plVar4);
    if (*(short *)(lVar1 + 0x192) != -1) {
      uVar3 = FUN_0028cfb0(param_1);
    }
  }
  return uVar3;
}

