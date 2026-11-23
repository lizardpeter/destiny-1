
long FUN_0075f040(void)

{
  long lVar1;
  long lVar2;
  
  lVar1 = FUN_0075f070();
  if (lVar1 != 0) {
    lVar2 = 0;
    if (*(char *)(lVar1 + 0x628) != '\0') {
      lVar2 = lVar1 + 0x628;
    }
    return lVar2;
  }
  return 0;
}

