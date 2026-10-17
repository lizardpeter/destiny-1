
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

char FUN_007e39a0(void)

{
  char cVar1;
  undefined8 uVar2;
  long *in_FS_OFFSET;
  
  uVar2 = FUN_000f7c30();
  cVar1 = '\x01';
  if (*(long *)(*in_FS_OFFSET + _DAT_01a1f4c8) != 0) {
    cVar1 = FUN_007dca10(*(long *)(*in_FS_OFFSET + _DAT_01a1f4c8),uVar2);
    if (cVar1 != '\0') {
      *(undefined8 *)(*in_FS_OFFSET + _DAT_01a1f4c8) = 0;
    }
  }
  return cVar1;
}

