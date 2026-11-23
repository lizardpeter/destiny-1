
void FUN_007a1380(long param_1)

{
  short sVar1;
  int iVar2;
  long lVar3;
  
  if (DAT_0295c100 == '\0') {
    iVar2 = thunk_FUN_012aa7d6(&DAT_0295c100);
    if (iVar2 != 0) {
      DAT_0295c0a0 = &PTR_FUN_01914b60;
      thunk_FUN_012aa7e6(&DAT_0295c100);
    }
  }
  FUN_0033e240(&DAT_0295c0a0);
  *(undefined2 *)(param_1 + 0x34) = 0xffff;
  lVar3 = FUN_005753c0(4);
  if (lVar3 == 0) {
    sVar1 = *(short *)(param_1 + 0x34);
  }
  else {
    sVar1 = FUN_00264980(lVar3);
    *(short *)(param_1 + 0x34) = sVar1;
  }
  *(uint *)(param_1 + 0x30) = (uint)(sVar1 == -1) + (uint)(sVar1 == -1) * 4;
  return;
}

