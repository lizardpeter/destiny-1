
void FUN_00bb5990(long param_1)

{
  undefined4 uVar1;
  int *piVar2;
  int *piVar3;
  undefined8 uVar4;
  
  if (*(int *)(param_1 + 8) == 1) {
    *(undefined4 *)(param_1 + 0x54) = 0;
  }
  else {
    uVar4 = FUN_00ba2b80(param_1 + 0x12a78 + (long)*(int *)(param_1 + 0x5b180) * 0x18258);
    FUN_00b56c90(uVar4);
    *(undefined4 *)(param_1 + 0x54) = 0;
    if (*(int *)(param_1 + 8) != 1) goto LAB_00bb5a60;
  }
  uVar1 = *(undefined4 *)(param_1 + 0x3c);
  piVar3 = *(int **)(param_1 + 0x12a68);
  while (piVar3 != (int *)0x0) {
    piVar2 = *(int **)(piVar3 + 0xe);
    if (*piVar3 == 0) {
      FUN_00aeaf90(*(undefined8 *)(piVar3 + 2));
    }
    FUN_00aeaf90(piVar3);
    piVar3 = piVar2;
  }
  *(undefined8 *)(param_1 + 0x12a5c) = 0;
  *(undefined8 *)(param_1 + 0x12a70) = 0;
  *(undefined8 *)(param_1 + 0x12a68) = 0;
  *(undefined4 *)(param_1 + 0x12a54) = 0xffffffff;
  *(undefined4 *)(param_1 + 0x12a58) = 0xffffffff;
  *(undefined4 *)(param_1 + 0x12a50) = uVar1;
LAB_00bb5a60:
  *(undefined1 *)(param_1 + 0x38) = 1;
  *(undefined1 *)(param_1 + 0x80) = 0;
  if (*(int *)(param_1 + 0x2c) == 4) {
    uVar4 = DAT_026553b0;
    if (DAT_026553a8 == '\0') {
      uVar4 = FUN_000694d0();
    }
    *(undefined8 *)(param_1 + 0x68) = uVar4;
  }
  *(undefined4 *)(param_1 + 0x2c) = 4;
  FUN_00ba0860(1);
  return;
}

