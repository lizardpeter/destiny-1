
void FUN_007deb70(long param_1,long param_2)

{
  long lVar1;
  
  if ((param_2 != 0) && (*(long *)(param_1 + 0x1d60) != param_2)) {
    *(long *)(param_1 + 0x1d60) = param_2;
    lVar1 = 0;
    do {
      *(undefined4 *)(param_1 + 0x1d78 + lVar1 * 4) = 0xffffffff;
      *(undefined4 *)(&DAT_00001df8 + lVar1 * 4 + param_1) = 0xffffffff;
      lVar1 = lVar1 + 1;
    } while ((int)lVar1 != 0x20);
  }
  return;
}

