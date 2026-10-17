
long FUN_002b08c0(uint param_1)

{
  if (DAT_0265b4e0 != 0) {
    return DAT_0265b4e0 + 0x8218 + (ulong)param_1 * 0x118;
  }
  return (ulong)param_1 * 0x118 + DAT_0265b4f8;
}

