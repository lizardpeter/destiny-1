
bool FUN_003455e0(long param_1)

{
  bool bVar1;
  
  bVar1 = false;
  if (*(long *)(param_1 + 8) != 0) {
    bVar1 = *(int *)(&DAT_00002114 + *(long *)(param_1 + 8)) != -1;
  }
  return bVar1;
}

