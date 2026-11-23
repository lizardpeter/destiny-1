
bool FUN_00b21070(int param_1)

{
  char cVar1;
  long lVar2;
  long lVar3;
  bool bVar4;
  
  bVar4 = true;
  if (*(long *)(DAT_0281d300 + 0x20 + (long)param_1 * 0x500) == 0) {
    lVar2 = FUN_00775180();
    cVar1 = FUN_00b8f690(lVar2 + 0x7b00);
    bVar4 = false;
    if (cVar1 != '\0') {
      cVar1 = FUN_00b8f690(lVar2 + 0x7b00);
      lVar3 = 0;
      if (cVar1 != '\0') {
        lVar3 = lVar2 + 0x7be8;
      }
      bVar4 = *(long *)(lVar3 + 0x18) != 0;
    }
  }
  return bVar4;
}

