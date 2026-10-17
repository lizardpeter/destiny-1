
undefined4 FUN_002a5490(long param_1,uint param_2)

{
  return CONCAT31((int3)(*(uint *)(param_1 + 0x5030) >> 8),
                  (*(uint *)(param_1 + 0x5030) >> (param_2 & 0x1f) & 1) != 0);
}

