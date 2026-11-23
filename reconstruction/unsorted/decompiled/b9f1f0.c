
void FUN_00b9f1f0(undefined4 param_1)

{
  long lVar1;
  long lVar2;
  undefined8 uVar3;
  
  lVar1 = FUN_00aeacd0();
  lVar2 = FUN_00aeacd0();
  if (*(int *)(lVar1 + 8) == 1) {
    uVar3 = 1;
  }
  else {
    if (*(int *)(lVar1 + 8) != 2) goto LAB_00b9f230;
    uVar3 = 0;
  }
  FUN_00906fb0(uVar3);
LAB_00b9f230:
  FUN_00bb53b0(lVar1);
  FUN_00ba6170(lVar2 + 0x5b190,param_1);
  FUN_00bb71f0(lVar1);
  FUN_0090fbe0();
  DAT_028a5426 = 0;
  return;
}

