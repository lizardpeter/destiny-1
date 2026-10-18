
void FUN_007de8c0(long param_1,uint param_2,ulong param_3,undefined *param_4)

{
  char cVar1;
  long lVar2;
  
  lVar2 = (ulong)param_2 * 0x80 + param_1;
  param_3 = param_3 & 0xffffffff;
  if (param_4 == (undefined *)0x0) {
    param_4 = PTR_DAT_01a1f4b8;
  }
  if (param_4 != *(undefined **)(&DAT_00001e78 + param_3 * 8 + lVar2)) {
    cVar1 = FUN_00f84710(param_4);
    if (cVar1 == '\0') {
      param_4 = PTR_DAT_01a1f4b8;
    }
    FUN_00f8afd0(*(long *)(param_1 + 0x50) + 0xc0,param_2,param_3,1,param_4);
    *(undefined **)(&DAT_00001e78 + param_3 * 8 + lVar2) = param_4;
  }
  return;
}

