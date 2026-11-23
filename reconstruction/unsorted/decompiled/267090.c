
undefined8 FUN_00267090(undefined4 param_1,undefined4 param_2)

{
  long *plVar1;
  undefined8 uVar2;
  undefined1 auVar3 [16];
  
  auVar3 = FUN_0025a3b0();
  plVar1 = auVar3._0_8_;
  if (plVar1 != (long *)0x0) {
                    /* WARNING: Could not recover jumptable at 0x002670be. Too many branches */
                    /* WARNING: Treating indirect jump as call */
    uVar2 = (**(code **)(*plVar1 + 0x40))
                      (param_1,plVar1,param_2,auVar3._8_8_,*(code **)(*plVar1 + 0x40));
    return uVar2;
  }
  return 2;
}

