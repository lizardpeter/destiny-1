
void FUN_007982a0(long param_1)

{
  int iVar1;
  undefined8 uVar2;
  
  FUN_00788e10(0x20);
  FUN_007539b0(param_1 + 0x40,0);
  *(undefined4 *)(param_1 + 0x30) = 0;
  if (DAT_0295c100 == '\0') {
    iVar1 = thunk_FUN_012aa7d6(&DAT_0295c100);
    if (iVar1 != 0) {
      DAT_0295c0a0 = &PTR_FUN_01914b60;
      thunk_FUN_012aa7e6(&DAT_0295c100);
    }
  }
  FUN_0033e240(&DAT_0295c0a0);
  uVar2 = FUN_00574ef0();
  thunk_FUN_01018280(uVar2);
  return;
}

