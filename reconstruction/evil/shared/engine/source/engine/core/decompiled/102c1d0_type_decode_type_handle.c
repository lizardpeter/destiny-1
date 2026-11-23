
void FUN_0102c1d0(undefined4 *param_1,undefined8 param_2,undefined8 param_3,undefined8 param_4)

{
  char cVar1;
  undefined4 uVar2;
  
  cVar1 = FUN_00073430(param_4);
  if (cVar1 == '\0') {
    *param_1 = 0xffffffff;
  }
  else {
    uVar2 = FUN_00072c70(param_4,0x20);
    *param_1 = uVar2;
  }
  return;
}

