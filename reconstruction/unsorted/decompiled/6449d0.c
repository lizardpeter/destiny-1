
bool FUN_006449d0(long param_1,int param_2)

{
  int *piVar1;
  bool bVar2;
  
  piVar1 = (int *)FUN_0063db40(param_1 + 0xa0);
  bVar2 = false;
  if ((piVar1 != (int *)0x0) && (*piVar1 == 6)) {
    bVar2 = piVar1[0x33] == param_2;
  }
  return bVar2;
}

