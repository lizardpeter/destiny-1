
void FUN_0102ce40(undefined8 param_1,undefined4 param_2,undefined8 param_3,undefined8 param_4,
                 undefined8 param_5)

{
  uint uVar1;
  
  uVar1 = FUN_00072c70(param_4,6);
                    /* WARNING: Could not recover jumptable at 0x0102ce98. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*(code *)(&PTR_FUN_019131b0)[uVar1])(param_1,param_2,param_3,param_4,param_5);
  return;
}

