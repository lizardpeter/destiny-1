
long FUN_00273fc0(undefined8 *param_1)

{
  undefined8 uVar1;
  undefined8 uVar2;
  long lVar3;
  
  uVar1 = param_1[4];
  uVar2 = (**(code **)*param_1)();
  lVar3 = FUN_002601c0(uVar1,uVar2);
  return lVar3 + 0x38;
}

