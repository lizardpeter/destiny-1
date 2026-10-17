
ulong FUN_000ad140(void)

{
  ulong uVar1;
  
  uVar1 = FUN_000f7c30();
  LOCK();
  if ((uint)uVar1 == DAT_01ad4844) {
    DAT_01ad4844 = 0;
  }
  else {
    uVar1 = (ulong)DAT_01ad4844;
  }
  UNLOCK();
  return uVar1;
}

