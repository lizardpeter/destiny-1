
byte FUN_0029bda0(long param_1)

{
  byte bVar1;
  
  bVar1 = 1;
  if (*(char *)(param_1 + 0x64a9) == '\0') {
    bVar1 = FUN_0008f800(&DAT_00005ea8 + param_1,0x3000);
    bVar1 = bVar1 ^ 1;
  }
  return bVar1;
}

