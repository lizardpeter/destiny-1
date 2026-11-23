
undefined8 FUN_00580840(undefined8 param_1,long *param_2)

{
  undefined4 uVar1;
  undefined8 uVar2;
  long lVar3;
  undefined8 uVar4;
  
  uVar2 = FUN_0056b260();
  uVar4 = 0;
  if (*param_2 != 0) {
    uVar1 = FUN_00001df0(uVar2);
    lVar3 = FUN_0056dc00(uVar2,2,uVar1,param_2);
    if (lVar3 != 0) {
      uVar2 = FUN_0056b260();
      if (*(long *)(lVar3 + 8) != 0) {
        uVar1 = FUN_01009850(uVar2);
        uVar4 = FUN_0056dc00(uVar2,2,uVar1,lVar3 + 8);
      }
    }
  }
  return uVar4;
}

