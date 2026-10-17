
void FUN_007e2a00(long param_1,uint param_2)

{
  float fVar1;
  
  if ((param_2 & 0x3c) != 0) {
    FUN_007e2480(*(undefined8 *)(param_1 + 0x40),param_1,param_2);
  }
  if ((param_2 & 0xc0) != 0) {
    fVar1 = *(float *)(param_1 + 0x20);
    if (*(char *)(param_1 + 0x24) == '\0') {
      fVar1 = DAT_0165feb4 - fVar1;
    }
    FUN_007e2760(fVar1,param_1,param_2,*(undefined1 *)(param_1 + 0x25));
    return;
  }
  return;
}

