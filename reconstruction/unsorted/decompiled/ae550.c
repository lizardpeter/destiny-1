
long FUN_000ae550(int param_1)

{
  long lVar1;
  uint7 uVar2;
  
  uVar2 = (uint7)(int3)((uint)param_1 >> 8);
  lVar1 = (ulong)uVar2 << 8;
  if ((&DAT_01ad4eec)[(long)param_1 * 0x18] != '\0') {
    lVar1 = CONCAT71(uVar2,(&DAT_01ad4ef1)[(long)param_1 * 0x18] != '\0');
  }
  return lVar1;
}

