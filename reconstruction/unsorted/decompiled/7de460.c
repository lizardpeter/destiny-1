
void FUN_007de460(long param_1,int param_2,int param_3)

{
  if ((*(long *)(param_1 + 0x50) != 0) &&
     ((*(int *)(&DAT_000025e8 + param_1) != param_3 || (*(int *)(param_1 + 0x25b8) != param_2)))) {
    FUN_007e0de0(param_1,param_2,param_3);
    *(int *)(&DAT_000025e8 + param_1) = param_3;
  }
  return;
}

