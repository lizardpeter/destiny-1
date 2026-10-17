
ulong FUN_00591b30(void)

{
  ulong uVar1;
  
  if (*DAT_026bc880 != '\0') {
    uVar1 = CONCAT71((int7)((ulong)DAT_026bc888 >> 8),*DAT_026bc888) & 0xffffffffffffff02;
    return CONCAT71((int7)(uVar1 >> 8),(byte)uVar1 >> 1);
  }
  return (ulong)DAT_026bc880 & 0xffffffffffffff00;
}

