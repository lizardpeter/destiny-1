
bool FUN_005845a0(long *param_1)

{
  undefined4 uVar1;
  undefined8 uVar2;
  long lVar3;
  bool bVar4;
  
  uVar2 = FUN_0056b260();
  bVar4 = false;
  if (*param_1 != 0) {
    uVar1 = FUN_00001df0(uVar2);
    lVar3 = FUN_0056dc00(uVar2,4,uVar1,param_1);
    bVar4 = lVar3 != 0;
  }
  return bVar4;
}

