
void FUN_00f7d2f0(long *param_1,long param_2,uint param_3,long param_4,long param_5)

{
  param_1[2] = param_2;
  *param_1 = param_2;
  param_1[1] = (ulong)(param_3 & 0xfffffffc) + param_2;
  param_1[3] = param_4;
  param_1[4] = param_5;
  return;
}

