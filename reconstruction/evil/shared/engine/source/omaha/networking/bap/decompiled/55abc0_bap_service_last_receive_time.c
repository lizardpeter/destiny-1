
undefined8 FUN_0055abc0(int param_1)

{
  long lVar1;
  undefined8 uVar2;
  
  if (*(int *)(DAT_026b9968 + 8 + (long)param_1 * 0x18) != -1) {
    lVar1 = FUN_00b333a0();
    if (lVar1 != 0) {
      uVar2 = FUN_00b2e860(lVar1);
      return uVar2;
    }
  }
  return 0xffffffffffffffff;
}

