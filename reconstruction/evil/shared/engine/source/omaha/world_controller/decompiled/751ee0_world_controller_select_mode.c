
void FUN_00751ee0(int param_1)

{
  int iVar1;
  
  FUN_007672d0();
  if (DAT_026c92a0 != 0) {
    FUN_0075e9b0();
    FUN_0075e9d0(DAT_026c92a0);
  }
  FUN_0078f570();
  FUN_0078f660(param_1);
  if (param_1 == 3) {
    return;
  }
  FUN_000d3100();
  if (DAT_0295c100 == '\0') {
    iVar1 = thunk_FUN_012aa7d6(&DAT_0295c100);
    if (iVar1 != 0) {
      DAT_0295c0a0 = &PTR_FUN_01914b60;
      thunk_FUN_012aa7e6(&DAT_0295c100);
    }
  }
  FUN_0033e210(&DAT_0295c0a0,FUN_00752aa0,FUN_00752b20,FUN_000d30d0);
  return;
}

