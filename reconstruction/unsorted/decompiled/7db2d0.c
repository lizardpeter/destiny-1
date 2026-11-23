
void FUN_007db2d0(int *param_1)

{
  int iVar1;
  undefined8 uVar2;
  
  LOCK();
  UNLOCK();
  iVar1 = DAT_026df280 + 1;
  *param_1 = DAT_026df280;
  DAT_026df280 = iVar1;
  param_1[1] = 0;
  if (param_1[2] == 0) {
    uVar2 = FUN_007e3a00(DAT_026e2be8);
    FUN_007dcaa0(uVar2);
    FUN_007dcce0(uVar2);
    FUN_007dcaf0(uVar2);
    *(undefined2 *)(param_1 + 3) = 0;
    *(undefined1 *)((long)param_1 + 0xe) = 1;
  }
  return;
}

