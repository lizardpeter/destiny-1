
void FUN_00586920(long param_1,long param_2)

{
  long lVar1;
  int iVar2;
  long lVar3;
  
  iVar2 = -1;
  lVar1 = param_1 + -0x30;
  do {
    lVar3 = lVar1;
    iVar2 = iVar2 + 1;
    if (0 < iVar2) {
      return;
    }
    lVar1 = lVar3 + 0x30;
  } while (*(char *)(lVar3 + 0x30) == '\0');
  if ((lVar1 != 0) && (*(long *)(lVar3 + 0x40) == param_2)) {
    *(undefined1 *)(lVar3 + 0x58) = 1;
    FUN_00586970(lVar1,lVar1);
    return;
  }
  return;
}

