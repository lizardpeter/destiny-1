
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

long FUN_007e38c0(long param_1,int param_2)

{
  long lVar1;
  long *in_FS_OFFSET;
  
  lVar1 = 0;
  if ((param_2 == 0) && (*(long *)(param_1 + 0x28) == DAT_015b6068)) {
    lVar1 = param_1 + 0x10;
    FUN_007dc9e0(lVar1);
    *(long *)(*in_FS_OFFSET + _DAT_01a1f4c8) = lVar1;
  }
  return lVar1;
}

