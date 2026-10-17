
undefined8 FUN_005845f0(long *param_1)

{
  undefined4 uVar1;
  undefined8 uVar2;
  
  uVar2 = FUN_0056b260();
  if (*param_1 == 0) {
    uVar2 = 0;
  }
  else {
    uVar1 = FUN_00001df0(uVar2);
    uVar2 = FUN_0056dc00(uVar2,4,uVar1,param_1);
  }
  return uVar2;
}

