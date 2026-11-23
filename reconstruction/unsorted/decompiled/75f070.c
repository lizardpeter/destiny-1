
undefined8 FUN_0075f070(void)

{
  char cVar1;
  long lVar2;
  long lVar3;
  undefined8 uVar4;
  int iVar5;
  
  lVar2 = FUN_00768080();
  lVar3 = FUN_00768080();
  if (lVar3 == 0) {
LAB_0075f0a9:
    cVar1 = FUN_00752150(4);
    uVar4 = 0;
    if (cVar1 == '\0') goto LAB_0075f0eb;
    iVar5 = *DAT_026c96f8;
  }
  else {
    iVar5 = *DAT_026c96f8;
    if (*(int *)(lVar3 + 0x4f0 + (long)iVar5 * 0x1f0) == -1) goto LAB_0075f0a9;
  }
  uVar4 = 0;
  if ((iVar5 != -1) && (*(int *)(lVar2 + 0x5b8 + (long)iVar5 * 0x1f0) != -1)) {
    uVar4 = FUN_002a0010();
  }
LAB_0075f0eb:
  lVar2 = FUN_00768080();
  if ((lVar2 != 0) && (*(int *)(lVar2 + 0x4f0 + (long)*DAT_026c96f8 * 0x1f0) == 6)) {
    uVar4 = FUN_0029a5e0(uVar4);
    return uVar4;
  }
  return 0;
}

