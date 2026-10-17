
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

long FUN_007e3910(undefined8 param_1,int param_2)

{
  long lVar1;
  long lVar2;
  long *in_FS_OFFSET;
  
  lVar1 = DAT_026e2be8;
  if (param_2 == 0) {
    if (*(long *)(DAT_026e2be8 + 0x28) == DAT_015b6068) {
      lVar2 = DAT_026e2be8 + 0x10;
      FUN_007dc9e0(lVar2);
      *(long *)(*in_FS_OFFSET + _DAT_01a1f4c8) = lVar2;
    }
    else {
      do {
      } while (*(long *)(DAT_026e2be8 + 0x28) != DAT_015b6068);
      lVar2 = DAT_026e2be8 + 0x10;
      FUN_007dc9e0(lVar2);
      *(long *)(*in_FS_OFFSET + _DAT_01a1f4c8) = lVar2;
    }
    FUN_00818210(lVar1 + 0x10);
    return lVar1 + 0x10;
  }
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}

