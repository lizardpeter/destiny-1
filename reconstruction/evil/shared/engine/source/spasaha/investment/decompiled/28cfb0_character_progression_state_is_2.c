
bool FUN_0028cfb0(undefined8 param_1,ushort param_2)

{
  long lVar1;
  bool bVar2;
  
  lVar1 = FUN_002601f0();
  bVar2 = false;
  if (param_2 < 0x2000) {
    bVar2 = *(char *)(lVar1 + 4 + (long)(short)param_2) == '\x02';
  }
  return bVar2;
}

