
int FUN_000ad120(void)

{
  int iVar1;
  int iVar2;
  
  iVar1 = FUN_000f7c30();
  iVar2 = 0;
  LOCK();
  if (DAT_01ad4844 != 0) {
    iVar1 = DAT_01ad4844;
    iVar2 = DAT_01ad4844;
  }
  DAT_01ad4844 = iVar1;
  UNLOCK();
  return iVar2;
}

