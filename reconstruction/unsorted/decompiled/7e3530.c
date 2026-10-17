
void FUN_007e3530(void)

{
  long lVar1;
  
  if (DAT_026e2be0 != '\0') {
    FUN_007e3860(DAT_026e2be8);
    lVar1 = DAT_026e2be8;
    thunk_FUN_007dc780(DAT_026e2be8 + 0xf2f0);
    thunk_FUN_007dc780(lVar1 + 0xca90);
    thunk_FUN_007dc780(lVar1 + 0xa230);
    thunk_FUN_007dc780(lVar1 + 0x79d0);
    thunk_FUN_007dc780(lVar1 + 0x5170);
    thunk_FUN_007dc780(lVar1 + 0x2910);
    thunk_FUN_007dc780(lVar1 + 0x10);
    FUN_000af8f0(DAT_026e2bf0);
    DAT_026e2bf0 = 0xffff;
    DAT_026e2be8 = 0;
    DAT_026e2be0 = '\0';
  }
  return;
}

