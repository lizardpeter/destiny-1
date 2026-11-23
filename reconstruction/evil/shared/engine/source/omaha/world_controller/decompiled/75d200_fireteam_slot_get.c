
int FUN_0075d200(void)

{
  char cVar1;
  long lVar2;
  uint uVar3;
  int iVar4;
  
  FUN_00768080();
  lVar2 = FUN_00768080();
  if (((lVar2 == 0) || (*(int *)(lVar2 + 0x4f0 + (long)*DAT_026c96f8 * 0x1f0) == -1)) &&
     (cVar1 = FUN_00752150(4), cVar1 == '\0')) {
    return -1;
  }
  lVar2 = FUN_00768080();
  if (((((lVar2 != 0) && (*(int *)(lVar2 + 0x4f0 + (long)*DAT_026c96f8 * 0x1f0) != -1)) ||
       (cVar1 = FUN_00752150(4), cVar1 != '\0')) &&
      (((long)DAT_026c96f8[1] != -1 && (DAT_026c96f8[(long)DAT_026c96f8[1] * 2 + 5] != -1)))) &&
     (lVar2 = FUN_002a00a0(), lVar2 != 0)) {
    return 1;
  }
  lVar2 = FUN_00768080();
  if ((lVar2 == 0) || (iVar4 = *DAT_026c96f8, *(int *)(lVar2 + 0x4f0 + (long)iVar4 * 0x1f0) == -1))
  {
    cVar1 = FUN_00752150(4);
    uVar3 = 1;
    if (cVar1 == '\0') goto LAB_0075d317;
    iVar4 = *DAT_026c96f8;
  }
  uVar3 = 1;
  if ((iVar4 != -1) && (DAT_026c96f8[(long)iVar4 * 2 + 5] != -1)) {
    lVar2 = FUN_002a00a0();
    uVar3 = (uint)(lVar2 == 0);
  }
LAB_0075d317:
  return (int)(uVar3 << 0x1f) >> 0x1f;
}

