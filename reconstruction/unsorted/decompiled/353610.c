
void FUN_00353610(long *param_1)

{
  long lVar1;
  code *UNRECOVERED_JUMPTABLE;
  
  lVar1 = *param_1;
  UNRECOVERED_JUMPTABLE = *(code **)(lVar1 + 0x30 + *(long *)(lVar1 + 0x18));
  if (((ulong)UNRECOVERED_JUMPTABLE & 1) != 0) {
    UNRECOVERED_JUMPTABLE =
         *(code **)(UNRECOVERED_JUMPTABLE +
                   *(long *)(param_1[1] + *(long *)(lVar1 + 0x38 + *(long *)(lVar1 + 0x18))) + -1);
  }
                    /* WARNING: Could not recover jumptable at 0x00353631. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*UNRECOVERED_JUMPTABLE)();
  return;
}

