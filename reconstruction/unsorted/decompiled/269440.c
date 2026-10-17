
ulong FUN_00269440(long param_1)

{
  ulong uVar1;
  uint uVar2;
  
  uVar2 = (uint)*(char *)(param_1 + 0x10);
  uVar1 = *(ulong *)(param_1 + 0x18) & 0xffffffffffffff00;
  if ((*(uint *)(*(ulong *)(param_1 + 0x18) + (long)((int)uVar2 >> 5) * 4) >> (uVar2 & 0x1f) & 1) !=
      0) {
    uVar1 = CONCAT71((int7)(int3)(*(char *)(param_1 + 0x10) >> 7),
                     *(long *)(*(long *)(param_1 + 8) + (long)(int)uVar2 * 8) != 0);
  }
  return uVar1;
}

