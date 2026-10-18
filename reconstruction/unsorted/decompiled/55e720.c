
char FUN_0055e720(long *param_1,undefined8 param_2,undefined8 *param_3,undefined8 *param_4,
                 undefined4 param_5,undefined4 *param_6)

{
  ushort *puVar1;
  char cVar2;
  undefined4 uVar3;
  
  *param_4 = *param_3;
  cVar2 = FUN_00b34810(param_3,param_4,param_5,param_6);
  if (cVar2 != '\0') {
    puVar1 = (ushort *)((long)param_4 + 6);
    *puVar1 = *puVar1 << 8 | *puVar1 >> 8;
  }
  uVar3 = (**(code **)(*param_1 + 8))(param_1);
  *param_6 = uVar3;
  return cVar2;
}

