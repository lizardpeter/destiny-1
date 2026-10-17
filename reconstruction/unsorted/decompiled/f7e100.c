
void FUN_00f7e100(uint *param_1,uint param_2)

{
  *param_1 = *param_1 & 0xfffffffc | param_2 & 3;
  return;
}

