
undefined8 FUN_00644970(long param_1)

{
  int *piVar1;
  undefined8 uVar2;
  
  piVar1 = (int *)FUN_0063db40(param_1 + 0xa0);
  if ((piVar1 != (int *)0x0) && (*piVar1 == 6)) {
    uVar2 = FUN_0104eb30(piVar1[0x32]);
    return uVar2;
  }
  return 0xffffffff;
}

