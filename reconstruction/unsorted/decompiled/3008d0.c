
bool FUN_003008d0(void)

{
  long lVar1;
  int iVar2;
  bool bVar3;
  
  lVar1 = DAT_02689540;
  iVar2 = FUN_002ff6c0(DAT_02689540);
  bVar3 = false;
  if (iVar2 == 0) {
    iVar2 = FUN_002ff6c0(lVar1 + 0x28);
    bVar3 = iVar2 == 0;
  }
  return bVar3;
}

