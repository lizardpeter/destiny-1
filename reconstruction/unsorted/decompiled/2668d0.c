
undefined4 FUN_002668d0(undefined8 param_1)

{
  long lVar1;
  short sVar2;
  undefined4 uVar3;
  
  sVar2 = FUN_00276550();
  uVar3 = 0;
  if (sVar2 != -1) {
    lVar1 = FUN_002601f0(param_1);
    uVar3 = *(undefined4 *)(lVar1 + 0x4004 + (long)sVar2 * 4);
  }
  return uVar3;
}

