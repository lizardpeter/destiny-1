
void FUN_007df310(long param_1,ulong param_2,undefined *param_3)

{
  char cVar1;
  
  if (param_3 == (undefined *)0x0) {
    param_3 = PTR_DAT_01a1f4b8;
  }
  param_2 = param_2 & 0xffffffff;
  if (param_3 != *(undefined **)(&DAT_00001ef8 + param_2 * 8 + param_1)) {
    cVar1 = FUN_00f84710(param_3);
    if (cVar1 == '\0') {
      param_3 = PTR_DAT_01a1f4b8;
    }
    FUN_00f8afd0(*(long *)(param_1 + 0x50) + 0xc0,1,param_2,1,param_3);
    *(undefined **)(&DAT_00001ef8 + param_2 * 8 + param_1) = param_3;
  }
  return;
}

