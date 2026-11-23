
void FUN_007a0360(long param_1,int param_2)

{
  if (param_2 == 0x24) {
    if (*(int *)(param_1 + 0x38) == 5) {
      *(undefined4 *)(param_1 + 0x38) = 2;
    }
  }
  else if ((param_2 == 0x22) && (*(int *)(param_1 + 0x38) == 3)) {
    *(undefined4 *)(param_1 + 0x38) = 0;
    return;
  }
  return;
}

