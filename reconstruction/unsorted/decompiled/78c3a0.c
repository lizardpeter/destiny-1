
bool FUN_0078c3a0(void)

{
  long lVar1;
  char cVar2;
  bool bVar3;
  
  cVar2 = FUN_00752150(3);
  bVar3 = false;
  if (cVar2 != '\0') {
    lVar1 = thunk_FUN_0078f6f0();
    bVar3 = *(char *)(lVar1 + 0x2e39) != '\0';
  }
  return bVar3;
}

