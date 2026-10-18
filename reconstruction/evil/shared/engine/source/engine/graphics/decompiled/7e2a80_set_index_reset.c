
void FUN_007e2a80(long param_1,char param_2)

{
  if ((*(long *)(param_1 + 0x50) != 0) && (param_2 != *(char *)(param_1 + 0x27c0))) {
    FUN_00f806d0(*(long *)(param_1 + 0x50),param_2);
    *(char *)(param_1 + 0x27c0) = param_2;
  }
  return;
}

