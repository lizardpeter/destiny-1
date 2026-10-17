
uint FUN_002a5520(long param_1,long *param_2)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = 0xffffffff;
  do {
    uVar2 = uVar2 + 1;
    if (0x12 < (int)uVar2) {
      return 0xffffffff;
    }
  } while ((*(uint *)(param_1 + 0x502c) >> (uVar2 & 0x1f) & 1) == 0);
  uVar1 = 0xffffffff;
  if (uVar2 != 0xffffffff) {
    while (uVar1 = uVar2, *(long *)(param_1 + 8 + (long)(int)uVar2 * 0x250) != *param_2) {
      uVar1 = uVar2 + 1;
      do {
        uVar2 = uVar1;
        if (0x12 < (int)uVar2) {
          return 0xffffffff;
        }
        uVar1 = uVar2 + 1;
      } while ((*(uint *)(param_1 + 0x502c) >> (uVar2 & 0x1f) & 1) == 0);
      if (uVar2 + 1 == 0) {
        return 0xffffffff;
      }
    }
  }
  return uVar1;
}

