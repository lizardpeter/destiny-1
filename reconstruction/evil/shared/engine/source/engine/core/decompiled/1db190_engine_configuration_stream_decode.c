
undefined8 FUN_001db190(long *param_1)

{
  char cVar1;
  undefined8 uVar2;
  int iVar3;
  int local_2c;
  long local_28;
  
  local_28 = *DAT_01a1f100;
  cVar1 = FUN_000a2180(*param_1,&local_2c);
  if ((cVar1 != '\0') && (local_2c == 0x123456)) {
    do {
      cVar1 = FUN_000a2180(*param_1,&local_2c);
      iVar3 = local_2c;
      if (cVar1 == '\0') {
        iVar3 = 0;
      }
      uVar2 = 1;
      if (iVar3 == 0) goto LAB_001db202;
      if (*(long *)(*param_1 + 0x18) != 0) break;
      cVar1 = FUN_00352860(iVar3,param_1);
    } while (cVar1 != '\0');
  }
  uVar2 = 0;
LAB_001db202:
  if (*DAT_01a1f100 == local_28) {
    return uVar2;
  }
  uVar2 = thunk_FUN_012aa7f6();
  return uVar2;
}

