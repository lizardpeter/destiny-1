
bool FUN_00b34c80(long param_1,int param_2,long *param_3)

{
  long lVar1;
  
  lVar1 = FUN_000b0aa0((long)&DAT_01ad5000 +
                       (ulong)*(ushort *)(param_1 + 0x30) * DAT_01ad5010 + DAT_01ad5000,
                       (long)param_2);
  *param_3 = lVar1;
  return lVar1 != 0;
}

