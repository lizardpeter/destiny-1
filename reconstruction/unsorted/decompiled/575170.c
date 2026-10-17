
undefined8 FUN_00575170(long param_1,long *param_2)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined8 uVar3;
  
  uVar3 = FUN_0056b260();
  if (*param_2 == 0) {
    uVar3 = 0;
  }
  else {
    uVar1 = *(undefined4 *)(param_1 + 8);
    uVar2 = FUN_00011e50(uVar3);
    uVar3 = FUN_0056dc00(uVar3,uVar1,uVar2,param_2);
  }
  return uVar3;
}

