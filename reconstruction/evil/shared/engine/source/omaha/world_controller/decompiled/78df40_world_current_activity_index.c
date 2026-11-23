
undefined2 FUN_0078df40(void)

{
  char cVar1;
  undefined2 uVar2;
  int iVar3;
  long lVar4;
  
  iVar3 = FUN_0078b270();
  if (iVar3 != 3) {
    cVar1 = FUN_0075c600();
    if (cVar1 == '\0') {
      lVar4 = FUN_007642e0();
      uVar2 = 0xffff;
      if (lVar4 != 0) {
        lVar4 = FUN_002a2980(lVar4);
        uVar2 = *(undefined2 *)(lVar4 + 0x680);
      }
      return uVar2;
    }
  }
  uVar2 = FUN_010167d0();
  return uVar2;
}

