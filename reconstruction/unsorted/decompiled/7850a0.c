
undefined4 FUN_007850a0(void)

{
  undefined4 uVar1;
  long lVar2;
  
  lVar2 = FUN_00768050();
  uVar1 = 0xffffffff;
  if (lVar2 != 0) {
    uVar1 = *(undefined4 *)(lVar2 + 0x1b0);
  }
  return uVar1;
}

