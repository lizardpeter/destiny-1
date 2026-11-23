
long FUN_0025a6e0(long *param_1,short param_2)

{
  long lVar1;
  long lVar2;
  int *piVar3;
  long lVar4;
  long lVar5;
  
  piVar3 = (int *)(**(code **)(*param_1 + 0x38))();
  lVar5 = 0;
  if ((ulong)(long)param_2 < (ulong)(long)*piVar3) {
    lVar1 = *(long *)(piVar3 + 2);
    lVar4 = (long)param_2 * 0x10;
    if (((long)piVar3 + lVar4 + lVar1 + 0x18 != 0) &&
       (lVar2 = *(long *)((long)piVar3 + lVar4 + lVar1 + 0x20), lVar2 != 0)) {
      lVar5 = (long)piVar3 + lVar2 + lVar4 + lVar1 + 0x20;
    }
  }
  return lVar5;
}

