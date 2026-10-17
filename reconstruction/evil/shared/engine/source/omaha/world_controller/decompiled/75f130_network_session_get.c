
undefined8 FUN_0075f130(long param_1)

{
  char cVar1;
  long lVar2;
  long lVar3;
  undefined8 uVar4;
  int iVar5;
  int *piVar6;
  
  lVar2 = FUN_00768080();
  lVar3 = FUN_00768080();
  if (((lVar3 == 0) || (*(int *)(lVar3 + 0x4f0 + (long)*DAT_026c96f8 * 0x1f0) == -1)) &&
     (cVar1 = FUN_00752150(4), cVar1 == '\0')) {
    return 0;
  }
  piVar6 = (int *)(lVar2 + 0x5b8);
  iVar5 = 0;
  while ((*piVar6 == -1 || (lVar3 = FUN_002a0010(), lVar3 != param_1))) {
    piVar6 = piVar6 + 0x7c;
    iVar5 = iVar5 + 1;
    if (2 < iVar5) {
      return 0;
    }
  }
  uVar4 = FUN_0075bdb0(lVar2,iVar5);
  return uVar4;
}

