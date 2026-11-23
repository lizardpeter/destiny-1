
undefined8 FUN_007da740(void)

{
  long *plVar1;
  undefined8 uVar2;
  
  plVar1 = (long *)FUN_0025a3b0();
  if (plVar1 != (long *)0x0) {
                    /* WARNING: Could not recover jumptable at 0x007da755. Too many branches */
                    /* WARNING: Treating indirect jump as call */
    uVar2 = (**(code **)(*plVar1 + 0x18))(plVar1);
    return uVar2;
  }
  return 3;
}

