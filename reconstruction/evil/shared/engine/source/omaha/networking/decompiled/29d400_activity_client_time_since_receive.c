
long FUN_0029d400(long param_1)

{
  long lVar1;
  long lVar2;
  
  lVar1 = (**(code **)(**(long **)(param_1 + 0xe50) + 0x28))();
  lVar2 = 0;
  if (lVar1 != -1) {
    lVar2 = DAT_026553b0;
    if (DAT_026553a8 == '\0') {
      lVar2 = FUN_000694d0();
    }
    lVar2 = lVar2 - lVar1;
  }
  return lVar2;
}

