
void FUN_0033e0d0(long param_1,undefined4 param_2,undefined4 param_3)

{
  if (0 < *(int *)(param_1 + 0x48)) {
    if (*(char *)(param_1 + 0x50) != '\x02') {
      *(undefined4 *)(param_1 + 0x54) = param_2;
      *(undefined4 *)(param_1 + 0x58) = param_3;
      return;
    }
    if (*(long *)(param_1 + 0x10) != 0) {
      *(undefined4 *)(param_1 + 0x58) = param_3;
      FUN_0033d700(DAT_02692560);
      return;
    }
  }
  return;
}

