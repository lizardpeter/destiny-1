
long FUN_008d5220(long param_1,uint *param_2,int param_3)

{
  uint *puVar1;
  uint uVar2;
  long lVar3;
  long lVar4;
  int iVar5;
  undefined8 uVar6;
  uint *puVar7;
  long lVar8;
  long lVar9;
  long lVar10;
  uint *puVar11;
  uint *puVar12;
  uint *puVar13;
  ulong uVar14;
  
  uVar2 = *(uint *)(param_1 + *(long *)(&DAT_015d2b60 + (long)param_3 * 8));
  lVar9 = 0;
  if (uVar2 != 0xffffffff) {
    uVar6 = FUN_00346d20();
    iVar5 = FUN_00349c10(uVar6,uVar2);
    if (iVar5 == 2) {
      lVar8 = (ulong)(((uint)((int)uVar2 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar2 >> 0xd) * 0x40;
      lVar3 = *DAT_01a238a0;
      lVar4 = *(long *)(lVar3 + 0x10 + lVar8);
      uVar14 = (ulong)((uVar2 & 0x1fff) * *(int *)(lVar3 + 0x30 + lVar8));
      if (*(long *)(param_1 + 0x10) == 0) {
        puVar13 = (uint *)0x0;
      }
      else {
        puVar13 = (uint *)(*(long *)(param_1 + 0x10) + param_1 + 0x20);
      }
      puVar1 = puVar13 + *(long *)(param_1 + 8);
      puVar12 = puVar13;
      if (*(long *)(param_1 + 8) != 0) {
        puVar7 = puVar1;
        puVar11 = puVar13;
        do {
          while( true ) {
            lVar10 = (long)puVar7 - (long)puVar11 >> 2;
            lVar9 = lVar10 - ((long)puVar7 - (long)puVar11 >> 0x3f) >> 1;
            if (puVar11[lVar9] < *param_2) break;
            puVar7 = puVar11 + lVar9;
            puVar12 = puVar11;
            if (lVar10 + 1U < 3) goto LAB_008d531c;
          }
          puVar11 = puVar11 + lVar9 + 1;
          puVar12 = puVar7;
        } while (puVar11 != puVar7);
      }
LAB_008d531c:
      lVar9 = 0;
      if (puVar12 != puVar1) {
        puVar7 = puVar1;
        if (*puVar12 <= *param_2) {
          puVar7 = puVar12;
        }
        lVar9 = 0;
        if (puVar7 != puVar1) {
          lVar9 = (lVar4 + uVar14) -
                  ((long)*(int *)(lVar3 + 0x34 + lVar8) & *(ulong *)(lVar4 + 8 + uVar14));
          lVar9 = lVar9 + *(long *)(lVar9 + 0x50) + 0x60 +
                  ((long)puVar7 - (long)puVar13 & 0x3ffffffffffffffcU) * 4;
        }
      }
    }
  }
  return lVar9;
}

