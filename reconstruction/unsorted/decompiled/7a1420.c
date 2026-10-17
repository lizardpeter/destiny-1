
void FUN_007a1420(void)

{
  int iVar1;
  
  if (DAT_0295c100 == '\0') {
    iVar1 = thunk_FUN_012aa7d6(&DAT_0295c100);
    if (iVar1 != 0) {
      DAT_0295c0a0 = &PTR_FUN_01914b60;
      thunk_FUN_012aa7e6(&DAT_0295c100);
    }
  }
  FUN_0033e260(&DAT_0295c0a0);
  return;
}

