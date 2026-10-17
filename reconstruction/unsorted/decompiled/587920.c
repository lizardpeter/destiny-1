
long FUN_00587920(void)

{
  long lVar1;
  undefined4 uVar2;
  undefined8 uVar3;
  long lVar4;
  bool bVar5;
  
  lVar1 = DAT_026bc510;
  lVar4 = 0;
  if (DAT_026bc510 != 0) {
    uVar3 = FUN_0056b260();
    bVar5 = true;
    if (DAT_02652ba8 != 0) {
      uVar2 = FUN_0055c360(uVar3);
      lVar4 = FUN_0056dc00(uVar3,5,uVar2,&DAT_02652ba8);
      bVar5 = lVar4 == 0;
    }
    lVar4 = 0;
    if (!bVar5) {
      lVar4 = lVar1 + 0x50;
    }
  }
  return lVar4;
}

