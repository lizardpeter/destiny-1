
long FUN_002b1270(int param_1)

{
  int *piVar1;
  uint uVar2;
  long lVar3;
  long lVar4;
  uint uVar5;
  
  uVar2 = FUN_002b0600();
  if (DAT_0265b4e0 == 0) {
    lVar4 = DAT_0265b4e8 + -0xf8;
    uVar5 = 0xffffffff;
    do {
      uVar5 = uVar5 + 1;
      if (uVar2 <= uVar5) {
        return 0;
      }
      piVar1 = (int *)(lVar4 + 0xf8);
      lVar4 = lVar4 + 0xf8;
    } while (*piVar1 != param_1);
  }
  else {
    uVar5 = 0xffffffff;
    lVar3 = DAT_0265b4e0 + 0x4318;
    do {
      uVar5 = uVar5 + 1;
      if (uVar2 <= uVar5) {
        return 0;
      }
      lVar4 = lVar3 + 0xf8;
      piVar1 = (int *)(lVar3 + 0xf8);
      lVar3 = lVar4;
    } while (*piVar1 != param_1);
  }
  return lVar4;
}

