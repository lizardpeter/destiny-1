
ulong FUN_0056bf10(long param_1,char param_2,long *param_3)

{
  ulong uVar1;
  
  uVar1 = 0x88;
  while ((*(char *)(param_1 + -0x28 + uVar1) != param_2 ||
         (*(long *)(param_1 + -8 + uVar1) != *param_3))) {
    uVar1 = uVar1 + 0x40;
    if ((int)uVar1 == 0x40c8) {
      return uVar1 & 0xffffffffffffff00;
    }
  }
  return CONCAT71((int7)(uVar1 >> 8),*(char *)(param_1 + uVar1) == '\x03');
}

