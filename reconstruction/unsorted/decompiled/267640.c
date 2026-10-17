
void FUN_00267640(long param_1)

{
  code *UNRECOVERED_JUMPTABLE;
  undefined1 auVar1 [16];
  
  auVar1 = FUN_0025a550();
  UNRECOVERED_JUMPTABLE = *(code **)(*auVar1._0_8_ + 0x330);
                    /* WARNING: Could not recover jumptable at 0x00267669. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*UNRECOVERED_JUMPTABLE)
            (auVar1._0_8_,*(undefined1 *)(*(long *)(param_1 + 8) + 4),auVar1._8_8_,
             UNRECOVERED_JUMPTABLE);
  return;
}

