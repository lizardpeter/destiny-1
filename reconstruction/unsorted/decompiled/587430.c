
void FUN_00587430(long param_1)

{
  char cVar1;
  int iVar2;
  long lVar3;
  long lVar4;
  
  lVar3 = 0;
  if (*(long *)(param_1 + 8) != 0) {
    lVar3 = *(long *)(param_1 + 8);
  }
  FUN_00585e00(lVar3);
  FUN_00585f10(lVar3);
  lVar4 = lVar3 + -0x30;
  iVar2 = -1;
  do {
    iVar2 = iVar2 + 1;
    if (0 < iVar2) goto LAB_0058749d;
    cVar1 = *(char *)(lVar4 + 0x30);
    lVar4 = lVar4 + 0x30;
  } while (cVar1 == '\0');
  if (lVar4 != 0) {
    if (cVar1 == '\x03') {
      FUN_00586970();
    }
    else if (cVar1 == '\x01') {
      FUN_00587150();
    }
  }
LAB_0058749d:
  FUN_00586000(lVar3);
  lVar3 = 0;
  if (*(long *)(param_1 + 0x10) != 0) {
    lVar3 = *(long *)(param_1 + 0x10);
  }
  FUN_00585a80(lVar3);
  return;
}

