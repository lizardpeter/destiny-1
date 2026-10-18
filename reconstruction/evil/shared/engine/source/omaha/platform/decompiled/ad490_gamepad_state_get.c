
undefined * FUN_000ad490(int param_1)

{
  undefined1 *puVar1;
  
  puVar1 = (undefined1 *)0x0;
  if ((&DAT_01ad40d0)[(long)param_1 + 0x10 + (long)DAT_01ad4840 * 0x3b0] != '\0') {
    if (DAT_01ad40d1 != '\0') {
      return &DAT_01ad4e00;
    }
    puVar1 = &DAT_01ad40d0 + (long)param_1 * 0xc0 + 0x20 + (long)DAT_01ad4840 * 0x3b0;
  }
  return puVar1;
}

