
void FUN_007db4b0(int *param_1)

{
  long lVar1;
  
  lVar1 = FUN_007e3a00(DAT_026e2be8);
  FUN_00f80c90(*(undefined8 *)(lVar1 + 0x50),4,0,DAT_026df288,1,(long)*param_1,0,0);
  if (param_1[2] == 0) {
    FUN_007dcec0(lVar1,0,0);
    FUN_007dd060(lVar1);
    FUN_007dcaa0(lVar1);
    *(undefined1 *)(param_1 + 3) = 1;
    *(undefined1 *)((long)param_1 + 0xe) = 0;
    *(undefined1 *)((long)param_1 + 0xd) = 0;
    param_1[1] = 0;
  }
  return;
}

