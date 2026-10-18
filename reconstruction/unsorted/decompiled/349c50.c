
undefined8
FUN_00349c50(long param_1,undefined8 param_2,int param_3,undefined8 param_4,undefined8 param_5)

{
  undefined8 uVar1;
  
  if (param_3 == 2) {
    uVar1 = FUN_00349cb0(param_1,param_2,2,param_4,&DAT_02693cd0,param_1 + 8,param_5);
  }
  else if (param_3 == 1) {
    uVar1 = FUN_00349cb0(param_1,param_2,1,param_4,&DAT_02693c50,param_1 + 4,param_5);
  }
  else {
    uVar1 = 0xffffffff;
  }
  return uVar1;
}

