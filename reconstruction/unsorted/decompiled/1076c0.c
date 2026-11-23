
bool FUN_001076c0(long param_1)

{
  bool bVar1;
  
  bVar1 = false;
  if (*(short *)(param_1 + 6) != -1) {
    bVar1 = *(char *)(param_1 + 4) != -1;
  }
  return bVar1;
}

