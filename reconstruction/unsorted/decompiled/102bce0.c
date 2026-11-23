
void FUN_0102bce0(undefined4 *param_1,undefined8 param_2,undefined4 *param_3,undefined8 param_4)

{
  uint uVar1;
  undefined4 uVar2;
  
  uVar1 = param_3[2];
  if ((uVar1 < 0x20) && (0 < (int)uVar1)) {
    uVar2 = FUN_00072c20(*param_3,param_3[1],param_4,s_real32_016271ef,uVar1,0,1);
    *param_1 = uVar2;
  }
  else {
    uVar2 = FUN_00072c70(param_4,0x20);
    *param_1 = uVar2;
  }
  return;
}

