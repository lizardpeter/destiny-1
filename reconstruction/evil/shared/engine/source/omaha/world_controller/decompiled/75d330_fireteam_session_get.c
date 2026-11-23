
undefined8 FUN_0075d330(void)

{
  char cVar1;
  int iVar2;
  long lVar3;
  long lVar4;
  undefined8 uVar5;
  
  lVar3 = FUN_00768080();
  iVar2 = FUN_0075d200();
  if (((iVar2 != -1) &&
      (((lVar4 = FUN_00768080(), lVar4 != 0 &&
        (*(int *)(lVar4 + 0x4f0 + (long)*DAT_026c96f8 * 0x1f0) != -1)) ||
       (cVar1 = FUN_00752150(4), cVar1 != '\0')))) &&
     (((long)DAT_026c96f8[iVar2] != -1 &&
      (*(int *)(lVar3 + 0x5b8 + (long)DAT_026c96f8[iVar2] * 0x1f0) != -1)))) {
    uVar5 = FUN_002a0010();
    return uVar5;
  }
  return 0;
}

