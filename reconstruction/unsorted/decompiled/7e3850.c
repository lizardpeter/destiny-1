
void thunk_FUN_007e5a70(undefined4 *param_1)

{
  uint uVar1;
  int iVar2;
  
  param_1[3] = 3;
  uVar1 = FUN_00057e60(DAT_026e2e88 + 0x50c);
  *(ulong *)(param_1 + 6) = (ulong)uVar1 << 8;
  uVar1 = FUN_00057e60((long)DAT_026e2e88 + 0x288c);
  *(ulong *)(param_1 + 8) = (ulong)uVar1 << 8;
  uVar1 = FUN_00057e60(DAT_026e2e88 + 0x517);
  *(ulong *)(param_1 + 10) = (ulong)uVar1 << 8;
  iVar2 = *(int *)(*DAT_026e2e88 + 0xb0) + -1;
  if (*(int *)(*DAT_026e2e88 + 0xb0) == 0) {
    iVar2 = 2;
  }
  param_1[4] = iVar2;
  *(undefined1 *)(param_1 + 0xe) = 1;
  FUN_00f89990(param_1 + 0x10,
               (long)DAT_026e2e88 + (ulong)*(uint *)(*DAT_026e2e88 + 0xb0) * 0x2c + 0x2860,0);
  *param_1 = param_1[0x12];
  param_1[1] = param_1[0x13];
  param_1[2] = 0;
  return;
}

