
char FUN_0055dc40(long *param_1,undefined8 param_2,undefined8 *param_3,undefined8 *param_4,
                 undefined4 param_5,undefined4 *param_6)

{
  char cVar1;
  undefined4 uVar2;
  
  *(undefined2 *)((long)param_4 + 0xc) = *(undefined2 *)((long)param_3 + 0xc);
  *(undefined4 *)(param_4 + 1) = *(undefined4 *)(param_3 + 1);
  *param_4 = *param_3;
  cVar1 = FUN_00b34810(param_3,param_4,param_5,param_6);
  if (cVar1 != '\0') {
    FUN_002a3620((long)param_4 + 6);
  }
  uVar2 = (**(code **)(*param_1 + 8))(param_1);
  *param_6 = uVar2;
  return cVar1;
}

