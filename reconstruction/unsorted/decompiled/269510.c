
long FUN_00269510(long param_1)

{
  long lVar1;
  uint uVar2;
  
  uVar2 = (uint)*(char *)(param_1 + 0x10);
  lVar1 = 0;
  if ((*(uint *)(*(long *)(param_1 + 0x18) + (long)((int)uVar2 >> 5) * 4) >> (uVar2 & 0x1f) & 1) !=
      0) {
    if (*(long *)(*(long *)(param_1 + 8) + (long)(int)uVar2 * 8) != 0) {
      lVar1 = *(long *)(param_1 + 8) + (long)(int)uVar2 * 8;
    }
  }
  return lVar1;
}

