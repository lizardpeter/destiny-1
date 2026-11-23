
void FUN_0006fa10(long param_1,ulong param_2,long param_3,long param_4)

{
  long *plVar1;
  long lVar2;
  bool bVar3;
  long lVar4;
  uint uVar5;
  long lVar6;
  uint uVar7;
  long lVar8;
  ulong uVar9;
  
  uVar9 = param_3 - param_4;
  lVar6 = (param_2 & 0xffffffff) * 0x40;
  lVar2 = *(long *)(param_1 + 0x10 + lVar6);
  lVar4 = 0;
  lVar8 = 0;
  if (lVar2 != 0) {
    lVar8 = lVar2 + uVar9;
  }
  *(long *)(param_1 + 0x10 + lVar6) = lVar8;
  lVar2 = *(long *)(param_1 + 0x20 + lVar6);
  if (lVar2 != 0) {
    lVar4 = lVar2 + uVar9;
  }
  *(long *)(param_1 + 0x20 + lVar6) = lVar4;
  lVar2 = *(long *)(param_1 + 0x28 + lVar6);
  lVar8 = 0;
  if (lVar2 != 0) {
    lVar8 = lVar2 + uVar9;
  }
  *(long *)(param_1 + 0x28 + lVar6) = lVar8;
  FUN_0006e070(*(undefined8 *)(param_1 + 0x18 + lVar6));
  if ((*(int *)(param_1 + 0x34 + lVar6) != 0) &&
     (lVar2 = *(long *)(param_1 + 0x18 + lVar6), 0 < *(int *)(lVar2 + 0x14))) {
    uVar7 = 0;
    uVar5 = 1;
    do {
      plVar1 = (long *)((ulong)(uVar7 * *(int *)(lVar2 + 0x10)) + 8 + *(long *)(lVar2 + 8));
      *plVar1 = *plVar1 + (uVar9 & 0xffffffff);
      bVar3 = (int)uVar5 < *(int *)(lVar2 + 0x14);
      uVar7 = uVar5;
      uVar5 = uVar5 + 1 & 0xffff;
    } while (bVar3);
  }
  return;
}

