
void FUN_007de590(long param_1,uint param_2)

{
  long lVar1;
  
  if (*(uint *)(param_1 + 0x25c0) != param_2) {
    lVar1 = (ulong)param_2 * 0x10;
    FUN_00f81a90(param_1 + 0x25d4,*(undefined4 *)(&DAT_015d2394 + lVar1),
                 *(undefined4 *)(&DAT_015d2394 + lVar1));
    FUN_00f7e100(param_1 + 0x25d4,*(undefined4 *)(&DAT_015d2398 + lVar1));
    FUN_00f81c50(FUN_000025d0 + param_1,(&DAT_015d239c)[lVar1] ^ 1,(&DAT_015d239c)[lVar1] ^ 1);
    FUN_00f80790(*(undefined8 *)(param_1 + 0x50),*(undefined4 *)(param_1 + 0x25d4));
    FUN_00f80640(*(undefined8 *)(param_1 + 0x50),*(undefined4 *)(FUN_000025d0 + param_1));
    *(uint *)(param_1 + 0x25c0) = param_2;
  }
  return;
}

