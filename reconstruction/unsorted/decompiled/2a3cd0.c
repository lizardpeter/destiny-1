
bool FUN_002a3cd0(long *param_1)

{
  int iVar1;
  
  iVar1 = (int)param_1[1];
  if (*param_1 != 0) {
    if (iVar1 == -1) {
      iVar1 = FUN_002a54d0();
    }
    else {
      iVar1 = FUN_002a5500(*param_1,iVar1);
    }
    *(int *)(param_1 + 1) = iVar1;
  }
  return iVar1 != -1;
}

