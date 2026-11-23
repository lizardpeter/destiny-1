
void FUN_009cd7e0(void)

{
  long *plVar1;
  
  plVar1 = (long *)FUN_0078e990();
  if (plVar1 != (long *)0x0) {
                    /* WARNING: Could not recover jumptable at 0x009cd7f5. Too many branches */
                    /* WARNING: Treating indirect jump as call */
    (**(code **)(*plVar1 + 8))(plVar1);
    return;
  }
  return;
}

