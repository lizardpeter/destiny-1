
void FUN_0029bde0(long param_1,long param_2)

{
  long lVar1;
  
  lVar1 = 0;
  do {
    *(uint *)(&DAT_00005ea8 + lVar1 * 4 + param_1) =
         *(uint *)(&DAT_00005ea8 + lVar1 * 4 + param_1) | *(uint *)(param_2 + lVar1 * 4);
    lVar1 = lVar1 + 1;
  } while ((int)lVar1 != 0x180);
  *(undefined1 *)(param_1 + 0x64a8) = 1;
  return;
}

