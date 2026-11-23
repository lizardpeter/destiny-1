
long FUN_0066ae60(uint param_1)

{
  if (param_1 == 0xffffffff) {
    return 0;
  }
  return *(long *)(DAT_0273ea80 + 8) + 0x1660 + (ulong)(param_1 & 0xffff) * 0x2af0;
}

