
void FUN_0028a2f0(long param_1,long param_2)

{
  long lVar1;
  long lVar2;
  
  thunk_FUN_012aa986(param_2,0,0x100);
  lVar1 = 0;
  do {
    lVar2 = (long)*(char *)(param_1 + lVar1 * 8);
    if (lVar2 != -1) {
      *(undefined4 *)(param_2 + lVar2 * 4) = *(undefined4 *)(param_1 + 4 + lVar1 * 8);
    }
    lVar1 = lVar1 + 1;
  } while ((int)lVar1 != 0x10);
  return;
}

