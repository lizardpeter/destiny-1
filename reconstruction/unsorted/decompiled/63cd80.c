
void FUN_0063cd80(long param_1)

{
  undefined8 *puVar1;
  long lVar2;
  
  if ((*(int *)(param_1 + 0xd0) != -1) && (*(int *)(param_1 + 0xb4) != -1)) {
    puVar1 = (undefined8 *)FUN_0023dfa0(param_1 + 0xac);
    lVar2 = FUN_0063bef0(*puVar1,*(undefined4 *)(param_1 + 0xb4));
    if (*(int *)(param_1 + 0xc) != -1) {
      FUN_0063ae20(lVar2 + 8);
    }
    if (*(int *)(param_1 + 0x14) != -1) {
      FUN_0063ae20(lVar2 + 0x20);
    }
    if (*(int *)(param_1 + 0x1c) != -1) {
      FUN_0063ae20(lVar2 + 0x38);
    }
    if (*(int *)(param_1 + 0x24) != -1) {
      FUN_0063ae20(lVar2 + 0x50);
    }
    if (*(int *)(param_1 + 0x2c) != -1) {
      FUN_0063ae20(lVar2 + 0x68);
    }
    if (*(int *)(param_1 + 0x34) != -1) {
      FUN_0063ae20(lVar2 + 0x80);
    }
    if (*(int *)(param_1 + 0x3c) != -1) {
      FUN_0063ae20(lVar2 + 0x98);
    }
    if (*(int *)(param_1 + 0x44) != -1) {
      FUN_0063ae20(lVar2 + 0xb0);
    }
  }
  return;
}

