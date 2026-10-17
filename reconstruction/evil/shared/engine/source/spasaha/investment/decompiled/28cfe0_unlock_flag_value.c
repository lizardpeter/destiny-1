
ulong FUN_0028cfe0(long param_1,ushort param_2)

{
  ulong in_RAX;
  ulong uVar1;
  
  uVar1 = in_RAX & 0xffffffffffffff00;
  if (param_2 < 0x2000) {
    uVar1 = CONCAT71((int7)(char)(param_2 >> 8),*(char *)(param_1 + (short)param_2) == '\x02');
  }
  return uVar1;
}

