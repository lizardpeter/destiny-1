
int FUN_009236f0(ushort param_1)

{
  byte bVar1;
  int iVar2;
  
  bVar1 = *(byte *)(DAT_0273eb80 + 200 + (ulong)param_1);
  iVar2 = -1;
  if (bVar1 != 0) {
    iVar2 = (int)(char)((bVar1 & 1) - 1);
  }
  return iVar2;
}

