
void FUN_002ca900(undefined8 param_1,undefined4 *param_2)

{
  char cVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  
  if ((DAT_0267fb28 != '\0') && (cVar1 = FUN_00073430(param_1), cVar1 != '\0')) {
    uVar4 = FUN_00072c20(DAT_0267fb30,DAT_0267fb40,param_1,&DAT_01626e24,DAT_0267fb50,0,0);
    *param_2 = uVar4;
    uVar4 = FUN_00072c20(DAT_0267fb34,DAT_0267fb44,param_1,&DAT_01626e26,DAT_0267fb54,0,0);
    param_2[1] = uVar4;
    uVar4 = FUN_00072c20(DAT_0267fb38,DAT_0267fb48,param_1,&DAT_01626e28,DAT_0267fb58,0,0);
    param_2[2] = uVar4;
    return;
  }
  uVar4 = FUN_00072c70(param_1,0x20);
  uVar2 = FUN_00072c70(param_1,0x20);
  uVar3 = FUN_00072c70(param_1,0x20);
  *param_2 = uVar4;
  param_2[1] = uVar2;
  param_2[2] = uVar3;
  return;
}

