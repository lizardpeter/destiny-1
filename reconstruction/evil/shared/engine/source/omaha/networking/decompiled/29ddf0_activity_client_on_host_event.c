
undefined8 FUN_0029ddf0(long *param_1,undefined8 param_2,undefined4 param_3)

{
  char cVar1;
  undefined8 uVar2;
  
  if ((*(byte *)((long)param_1 + 0x131) & 2) == 0) {
    (**(code **)(*param_1 + 0x38))(param_1);
    uVar2 = (**(code **)(*param_1 + 0x10))(param_1);
    cVar1 = FUN_002408e0(uVar2,param_2,param_3);
    if (cVar1 == '\0') {
      *(byte *)((long)param_1 + 0x131) = *(byte *)((long)param_1 + 0x131) | 2;
    }
  }
  return 1;
}

