
undefined8 * FUN_005753c0(undefined4 param_1)

{
  char cVar1;
  undefined4 uVar2;
  long lVar3;
  long lVar4;
  long lVar5;
  undefined8 uVar6;
  undefined8 uVar7;
  undefined8 uVar8;
  undefined8 *puVar9;
  
  cVar1 = FUN_005428c0();
  puVar9 = (undefined8 *)0x0;
  if (cVar1 != '\0') {
    cVar1 = FUN_0025cc10();
    if (cVar1 != '\0') {
      lVar3 = FUN_00587920();
      lVar4 = FUN_00587690();
      lVar5 = FUN_00587820();
      if (((lVar3 != 0) && (puVar9 = (undefined8 *)0x0, lVar4 != 0)) && (lVar5 != 0)) {
        uVar6 = FUN_0056b260();
        uVar7 = 0;
        if (DAT_02652bb0 != 0) {
          uVar2 = FUN_00084200(uVar6);
          uVar7 = FUN_0056dc00(uVar6,4,uVar2,&DAT_02652bb0);
        }
        uVar6 = FUN_0056b260();
        uVar2 = FUN_00059710(uVar6);
        uVar6 = FUN_0056dc80(uVar6,4,uVar2);
        uVar8 = FUN_005751e0(param_1);
        puVar9 = &DAT_026bc130;
        FUN_00260c50(&DAT_026bc130,lVar3,lVar4,lVar5,uVar6,uVar7,uVar8);
        FUN_00260cc0(&DAT_026bc130);
      }
    }
  }
  return puVar9;
}

