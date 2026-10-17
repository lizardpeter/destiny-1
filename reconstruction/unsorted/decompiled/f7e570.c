
void FUN_00f7e570(long param_1,undefined4 param_2)

{
  *(undefined4 *)(param_1 + 0x24) = param_2;
  *(uint *)(param_1 + 0x28) = *(uint *)(param_1 + 0x28) & 0xfffe0001 | 8;
  return;
}

