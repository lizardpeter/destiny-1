
float FUN_007da6f0(long param_1)

{
  float fVar1;
  
  fVar1 = DAT_0165fd88 / *(float *)(&DAT_018dcc10 + (ulong)*(uint *)(param_1 + 0xc) * 4);
  if (DAT_0165fd88 / *(float *)(&DAT_018dcc10 + (ulong)*(uint *)(param_1 + 0xc) * 4) + DAT_0165fd94
      < 0.0) {
    fVar1 = DAT_0165fd90;
  }
  if (0.0 <= fVar1 + DAT_0165fd98) {
    fVar1 = DAT_0165fd8c;
  }
  return fVar1;
}

