
bool FUN_0075eba0(undefined8 param_1,int param_2,int param_3)

{
  char cVar1;
  long lVar2;
  undefined8 uVar3;
  bool bVar4;
  
  lVar2 = FUN_00768080();
  if (((lVar2 == 0) || (*(int *)(lVar2 + 0x4f0 + (long)*DAT_026c96f8 * 0x1f0) == -1)) &&
     (cVar1 = FUN_00752150(4), cVar1 == '\0')) {
    return false;
  }
  bVar4 = false;
  if ((((long)DAT_026c96f8[(long)param_3 * 2 + (long)param_2] != -1) &&
      (DAT_026c96f8[(long)DAT_026c96f8[(long)param_3 * 2 + (long)param_2] * 2 + 5] != -1)) &&
     (lVar2 = FUN_002a00a0(), lVar2 != 0)) {
    uVar3 = FUN_00021860(lVar2);
    lVar2 = FUN_002a2980(uVar3);
    bVar4 = *(char *)(lVar2 + 2) != '\0';
  }
  return bVar4;
}

