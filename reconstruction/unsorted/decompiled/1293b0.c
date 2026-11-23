
uint FUN_001293b0(long param_1)

{
  uint uVar1;
  
  if (*(uint *)(param_1 + 0x1f0) == 0xffffffff) {
    return 0xffffff00;
  }
  uVar1 = (*(uint *)(param_1 + 0x1f0) & 0x1fff) * DAT_02689590;
  return CONCAT31((int3)(uVar1 >> 8),*(undefined1 *)((ulong)uVar1 + 0x40 + DAT_02689588)) &
         0xffffff01;
}

