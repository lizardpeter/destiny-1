
long FUN_00906e00(void)

{
  uint7 uVar1;
  
  uVar1 = (uint7)((ulong)DAT_0273dcd0 >> 8);
  if (((DAT_0273dcd0 != (char *)0x0) && (DAT_0273dcd0[0x2b48] != '\0')) && (*DAT_0273dcd0 == '\0'))
  {
    return CONCAT71(uVar1,DAT_0273dcd0[1]);
  }
  return (ulong)uVar1 << 8;
}

