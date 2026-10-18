
char FUN_0055e3d0(long *param_1,undefined8 param_2,undefined8 *param_3,undefined8 *param_4,
                 undefined4 param_5,undefined4 *param_6)

{
  undefined8 uVar1;
  char cVar2;
  undefined4 uVar3;
  
  param_4[3] = param_3[3];
  param_4[2] = param_3[2];
  uVar1 = *param_3;
  param_4[1] = param_3[1];
  *param_4 = uVar1;
  cVar2 = FUN_00b34810(param_3,param_4,param_5,param_6);
  if (cVar2 != '\0') {
    uVar1 = swap_bytes(*(undefined8 *)((long)param_4 + 6));
    *(undefined8 *)((long)param_4 + 6) = uVar1;
    uVar1 = swap_bytes(*(undefined8 *)((long)param_4 + 0xe));
    *(undefined8 *)((long)param_4 + 0xe) = uVar1;
    FUN_002a3620(param_4 + 3);
  }
  uVar3 = (**(code **)(*param_1 + 8))(param_1);
  *param_6 = uVar3;
  return cVar2;
}

