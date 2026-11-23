
int FUN_00923720(ushort param_1,int param_2)

{
  byte bVar1;
  
  bVar1 = *(byte *)(DAT_0273eb80 + 200 + (ulong)param_1);
  if ((bVar1 != 0) && (param_2 == -1)) {
    return (int)(char)((bVar1 & 1) - 1);
  }
  return -1;
}

