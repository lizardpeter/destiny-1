
long FUN_0025a690(long *param_1,short param_2)

{
  long lVar1;
  long lVar2;
  long lVar3;
  long lVar4;
  
  lVar2 = (**(code **)(*param_1 + 0x38))();
  lVar2 = lVar2 + 0x18 + *(long *)(lVar2 + 8);
  lVar3 = (long)param_2 * 0x10;
  lVar4 = 0;
  if ((lVar2 + lVar3 != 0) && (lVar1 = *(long *)(lVar2 + 8 + lVar3), lVar1 != 0)) {
    lVar4 = lVar1 + lVar2 + 8 + lVar3;
  }
  return lVar4;
}

