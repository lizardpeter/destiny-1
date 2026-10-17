
void FUN_0079dd90(long param_1)

{
  char cVar1;
  int iVar2;
  undefined4 uVar3;
  undefined8 uVar4;
  undefined8 uVar5;
  long lVar6;
  long lVar7;
  long lVar8;
  
  uVar4 = FUN_00557c40(&DAT_026bc508);
  iVar2 = *(int *)(param_1 + 0x34);
  if (iVar2 != 2) {
    if (iVar2 != 1) {
      if (iVar2 != 0) {
        return;
      }
      *(undefined4 *)(param_1 + 0x34) = 1;
    }
    FUN_0078c310(1);
    FUN_00542830();
    lVar6 = DAT_026553b0;
    if (DAT_026553a8 == '\0') {
      lVar6 = FUN_000694d0();
    }
    *(long *)(param_1 + 0x38) = lVar6;
    *(undefined4 *)(param_1 + 0x34) = 2;
    return;
  }
  uVar5 = FUN_00021860(&DAT_026bc270);
  iVar2 = FUN_00575970(uVar5);
  if (iVar2 != 0) {
    uVar3 = FUN_00575970(uVar5);
    iVar2 = FUN_0078e2d0(uVar3);
    if (iVar2 != -1) goto LAB_0079de8b;
  }
  lVar6 = *(long *)(param_1 + 0x38);
  lVar7 = DAT_026553b0;
  if (DAT_026553a8 == '\0') {
    lVar7 = FUN_000694d0();
  }
  lVar8 = FUN_0034e3a0();
  if (lVar7 - lVar6 < (long)*(int *)(lVar8 + 0x20)) {
    cVar1 = FUN_005862d0(uVar4);
    if (cVar1 == '\0') {
      cVar1 = FUN_005862e0(uVar4);
      if (cVar1 == '\0') {
        return;
      }
      cVar1 = FUN_0057f520();
      if (cVar1 == '\0') {
        return;
      }
      lVar6 = FUN_00587580();
      if (lVar6 == 0) {
        return;
      }
      cVar1 = FUN_0057db90(lVar6);
      if (cVar1 == '\0') {
        return;
      }
      *(undefined4 *)(param_1 + 0x34) = 3;
      return;
    }
    iVar2 = 0xb5;
  }
  else {
    iVar2 = 0xaf;
  }
LAB_0079de8b:
  FUN_00784e50(0x19,iVar2);
  return;
}

