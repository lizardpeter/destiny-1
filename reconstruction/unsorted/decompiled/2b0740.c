
long FUN_002b0740(uint param_1)

{
  if (DAT_0265b4e0 != 0) {
    return DAT_0265b4e0 + 0x4410 + (ulong)param_1 * 0xf8;
  }
  return (ulong)param_1 * 0xf8 + DAT_0265b4e8;
}

