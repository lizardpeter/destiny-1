
void FUN_007dc140(long *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  FUN_007db810(param_1[1],*param_1,param_2,param_3,param_4);
  *(undefined8 *)*param_1 = ((undefined8 *)*param_1)[2];
  *(undefined8 *)(*param_1 + 0x80) = *(undefined8 *)(*param_1 + 0x90);
  return;
}

