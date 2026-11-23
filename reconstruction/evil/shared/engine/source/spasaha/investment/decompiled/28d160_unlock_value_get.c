
undefined4 FUN_0028d160(long param_1,ushort param_2)

{
  if (param_2 < 0x800) {
    return *(undefined4 *)(param_1 + (long)(short)param_2 * 4);
  }
  return 0;
}

