
void FUN_007a0390(long param_1,int param_2)

{
  if (param_2 == 0x24) {
    if (*(int *)(param_1 + 8) == 5) {
      *(undefined4 *)(param_1 + 8) = 2;
    }
  }
  else if ((param_2 == 0x22) && (*(int *)(param_1 + 8) == 3)) {
    *(undefined4 *)(param_1 + 8) = 0;
    return;
  }
  return;
}

