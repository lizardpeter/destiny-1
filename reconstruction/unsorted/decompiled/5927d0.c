
void FUN_005927d0(void)

{
  int iVar1;
  
  FUN_007e9c40(1);
  FUN_0074ba10();
  FUN_00300c20();
  FUN_00937ec0(0xe000);
  FUN_00000380();
  FUN_00906500();
  if (DAT_0295c110 == '\0') {
    iVar1 = thunk_FUN_012aa7d6(&DAT_0295c110);
    if (iVar1 != 0) {
      DAT_0295c108 = &PTR_FUN_01909670;
      thunk_FUN_012aa7e6(&DAT_0295c110);
    }
  }
  (*(code *)DAT_0295c108[4])(&DAT_0295c108);
  if (DAT_0295c110 == '\0') {
    iVar1 = thunk_FUN_012aa7d6(&DAT_0295c110);
    if (iVar1 != 0) {
      DAT_0295c108 = &PTR_FUN_01909670;
      thunk_FUN_012aa7e6(&DAT_0295c110);
    }
  }
  (*(code *)DAT_0295c108[5])(&DAT_0295c108);
  FUN_000cbda0();
  FUN_00928ca0();
  FUN_00929370();
  FUN_0092cde0();
  FUN_0023a900();
  FUN_002c0ec0();
  FUN_002bb410();
  FUN_00594390();
  FUN_002ad760();
  FUN_00241bd0();
  FUN_0023b860();
  thunk_FUN_000eba70();
  FUN_000ecfc0();
  return;
}

