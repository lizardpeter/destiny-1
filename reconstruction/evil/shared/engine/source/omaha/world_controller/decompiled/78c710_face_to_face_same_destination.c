
bool FUN_0078c710(void)

{
  long lVar1;
  char cVar2;
  int *piVar3;
  
  lVar1 = FUN_00775770(0);
  if (lVar1 != 0) {
    cVar2 = FUN_00b8f690(lVar1 + 0x4b8);
    if (cVar2 != '\0') {
      cVar2 = FUN_00b8f690(lVar1 + 0x9b8);
      if (cVar2 != '\0') {
        cVar2 = FUN_00b8f690(lVar1 + 0x4b8);
        piVar3 = (int *)0x0;
        if (cVar2 != '\0') {
          piVar3 = (int *)(lVar1 + 0x59c);
        }
        lVar1 = FUN_011c3f80(lVar1 + 0x9b8);
        if (*piVar3 == DAT_026cf2b0) {
          return *(short *)(lVar1 + 2) != -1;
        }
      }
    }
  }
  return false;
}

