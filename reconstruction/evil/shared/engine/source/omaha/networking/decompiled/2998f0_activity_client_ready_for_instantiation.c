
undefined8 FUN_002998f0(long *param_1)

{
  char cVar1;
  byte extraout_AL;
  undefined8 uVar2;
  char *pcVar3;
  undefined7 extraout_var;
  byte bVar4;
  byte bVar5;
  bool bVar6;
  
  bVar6 = true;
  bVar4 = 0;
  if (param_1[0x1cb] == 0) {
    bVar5 = 0;
  }
  else {
    uVar2 = FUN_00021860();
    cVar1 = FUN_002a2c50(uVar2);
    bVar5 = 0;
    if (cVar1 != '\0') {
      uVar2 = FUN_00021860(param_1[0x1cb]);
      pcVar3 = (char *)FUN_002a2980(uVar2);
      bVar5 = 1;
      if (*pcVar3 == '\0') {
        bVar6 = true;
      }
      else if ((pcVar3[1] == '\0') || (bVar6 = false, *(int *)(pcVar3 + 0x10) < 1)) {
        bVar6 = pcVar3[1] != '\0';
      }
    }
  }
  (**(code **)(*param_1 + 0x18))(param_1);
  if (((!bVar6) && ((extraout_AL & bVar5) == 1)) && (*(char *)((long)param_1 + 0x64aa) != '\0')) {
    bVar4 = *(byte *)((long)param_1 + 0x131) & 1;
  }
  return CONCAT71(extraout_var,bVar4);
}

