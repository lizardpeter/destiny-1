
void FUN_007e1110(long param_1,ulong param_2)

{
  param_2 = param_2 & 0xffffffff;
  if (*(undefined **)(&DAT_00001ef8 + param_2 * 8 + param_1) != PTR_DAT_01a1f4b8) {
    FUN_00f84710(&DAT_026df2b4);
    FUN_00f8afd0(*(long *)(param_1 + 0x50) + 0xc0,1,param_2,1,&DAT_026df2b4);
    *(undefined **)(&DAT_00001ef8 + param_2 * 8 + param_1) = &DAT_026df2b4;
  }
  return;
}

