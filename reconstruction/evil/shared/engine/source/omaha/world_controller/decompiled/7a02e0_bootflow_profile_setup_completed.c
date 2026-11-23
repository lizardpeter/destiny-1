
void FUN_007a02e0(long param_1,int param_2)

{
  if (param_2 == 0x22) {
    if (*(int *)(param_1 + 0x38) == 3) {
      *(undefined4 *)(param_1 + 0x38) = 4;
      return;
    }
  }
  else if (param_2 == 0x24) {
    if (*(int *)(param_1 + 0x38) == 5) {
      *(undefined4 *)(param_1 + 0x38) = 6;
    }
  }
  else if ((param_2 == 0x23) && (*(int *)(param_1 + 0x38) == 1)) {
    *(undefined4 *)(param_1 + 0x38) = 2;
    return;
  }
  return;
}

