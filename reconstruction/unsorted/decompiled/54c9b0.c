
long FUN_0054c9b0(undefined8 param_1,short param_2)

{
  int *piVar1;
  long lVar2;
  
  piVar1 = (int *)FUN_0054c9f0();
  if ((ulong)(long)param_2 < (ulong)(long)*piVar1) {
    lVar2 = (long)piVar1 + (long)param_2 * 0x10 + *(long *)(piVar1 + 2) + 0x18;
  }
  else {
    lVar2 = 0;
  }
  return lVar2;
}

