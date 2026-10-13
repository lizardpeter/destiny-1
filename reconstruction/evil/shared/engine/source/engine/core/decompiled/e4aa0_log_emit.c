
void FUN_000e4aa0(int param_1,undefined8 param_2)

{
  ulong *puVar1;
  int *piVar2;
  int iVar3;
  long lVar4;
  ulong uVar5;
  int iVar6;
  ulong uVar7;
  uint uVar8;
  ulong uVar9;
  long lVar10;
  bool bVar11;
  
  lVar4 = DAT_02587bb0;
  if ((param_1 != -1) && (DAT_02587bb0 != 0)) {
    puVar1 = (ulong *)(DAT_02587bb0 + 0x75ba0);
    uVar9 = *(ulong *)(DAT_02587bb0 + 0x75ba0);
    do {
      uVar7 = uVar9 >> 0x20;
      iVar6 = (int)(uVar9 >> 0x20);
      uVar8 = iVar6 + 1;
      if (iVar6 == 0x463) {
        uVar8 = 0;
      }
      if (uVar8 == (uint)uVar9) {
        return;
      }
      LOCK();
      uVar5 = *puVar1;
      if (uVar9 == uVar5) {
        *puVar1 = (ulong)uVar8 << 0x20 | uVar9 & 0xffffffff;
        uVar5 = uVar9;
      }
      UNLOCK();
      bVar11 = uVar5 != uVar9;
      uVar9 = uVar5;
    } while (bVar11);
    lVar10 = uVar7 * 0x150;
    *(int *)(lVar4 + 0x19868 + lVar10) = param_1;
    FUN_00065030(lVar4 + 0x1986c + lVar10,param_2,0x140);
    FUN_00089bf0(lVar4 + 0x19860 + lVar10);
    piVar2 = (int *)(lVar4 + 0x199ac + lVar10);
    do {
      iVar3 = *piVar2;
      LOCK();
      iVar6 = *piVar2;
      if (iVar3 == iVar6) {
        *piVar2 = 1;
        iVar6 = iVar3;
      }
      UNLOCK();
    } while (iVar3 != iVar6);
  }
  return;
}

