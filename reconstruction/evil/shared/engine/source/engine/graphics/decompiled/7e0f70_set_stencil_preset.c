
void FUN_007e0f70(long param_1,int param_2)

{
  if ((*(int *)(param_1 + 0x25b8) != param_2) && (*(long *)(param_1 + 0x50) != 0)) {
    FUN_007e0de0(param_1,param_2,*(undefined4 *)(&DAT_000025e8 + param_1));
    return;
  }
  return;
}

