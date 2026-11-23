
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00917d70(uint param_1)

{
  undefined8 *puVar1;
  undefined8 *puVar2;
  uint *puVar3;
  uint uVar4;
  long lVar5;
  undefined1 auVar6 [16];
  undefined8 uVar7;
  undefined8 uVar8;
  undefined8 uVar9;
  char cVar10;
  uint uVar11;
  int iVar12;
  ulong uVar13;
  long lVar14;
  long lVar15;
  long lVar16;
  long lVar17;
  undefined4 uVar18;
  long local_8d0;
  long local_8c8;
  long local_8b8;
  undefined4 local_8b0;
  undefined1 local_8a8;
  undefined1 local_8a0 [16];
  uint local_890;
  uint local_888;
  long local_880;
  undefined4 local_878;
  long local_870;
  undefined8 local_868;
  undefined8 local_860;
  undefined4 local_858;
  undefined8 local_850;
  undefined8 local_848;
  undefined8 local_840;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  lVar17 = ((ulong)param_1 & 0xffff) * 0x2af0;
  lVar16 = *(long *)(DAT_0273ea80 + 8);
  uVar11 = FUN_006ed8f0(*(undefined4 *)(lVar16 + 0x644 + lVar17));
  if (*(char *)(DAT_0273ea90 + 0xa8) != '\0') {
    lVar14 = *(long *)(DAT_0273ea80 + 8);
    local_870 = *(long *)(DAT_0273ea90 + 0xa9);
    if (*(long *)(lVar14 + 0x620 + lVar17) == local_870) {
      uVar13 = (ulong)((uVar11 & 0x1fff) * DAT_02692230);
      puVar1 = (undefined8 *)(uVar13 + 0xd0 + DAT_02692228);
      uVar7 = *puVar1;
      uVar8 = puVar1[1];
      puVar2 = (undefined8 *)(uVar13 + 0xe0 + DAT_02692228);
      uVar9 = puVar2[1];
      puVar1 = (undefined8 *)(lVar14 + 0x70 + lVar17);
      *puVar1 = *puVar2;
      puVar1[1] = uVar9;
      puVar1 = (undefined8 *)(lVar14 + 0x60 + lVar17);
      *puVar1 = uVar7;
      puVar1[1] = uVar8;
    }
  }
  *(undefined4 *)(lVar16 + 0x2834 + lVar17) = 0;
  FUN_00072050(&local_8d0,uVar11);
  *(long *)(lVar16 + 0x64c + lVar17) = local_8d0;
  *(undefined4 *)(lVar16 + 0x818 + lVar17) = 0;
  uVar4 = *(uint *)(lVar16 + 0x270c + lVar17);
  if (uVar4 != 0xffffffff) {
    uVar13 = (ulong)((uVar4 & 0x1fff) * DAT_02689800);
    FUN_006597b0((DAT_026897f8 + uVar13) -
                 ((long)DAT_02689818 & *(ulong *)(DAT_026897f8 + 8 + uVar13)),lVar16 + lVar17);
  }
  auVar6 = vandps_avx(*(undefined1 (*) [16])
                       ((ulong)((uVar11 & 0x1fff) * DAT_02692230) + 0xe0 + DAT_02692228),
                      _DAT_0166b4f0);
  auVar6 = vorps_avx(auVar6,_DAT_0166b500);
  *(undefined1 (*) [16])(lVar16 + 0x660 + lVar17) = auVar6;
  uVar11 = *(uint *)(lVar16 + 4 + lVar17);
  if ((uVar11 != 0xffffffff) &&
     (uVar11 = *(uint *)((ulong)((uVar11 & 0x1fff) * DAT_02689590) + 0x54 + DAT_02689588),
     uVar11 != 0xffffffff)) {
    uVar13 = (ulong)((uVar11 & 0x1fff) * DAT_02692230);
    cVar10 = FUN_003381f0(DAT_02692228 + uVar13,*(undefined4 *)PTR_DAT_019b1e68,
                          *(undefined4 *)(DAT_02692228 + 0x54 + uVar13),local_8a0);
    if (cVar10 != '\0') {
      local_8a8 = 0;
      lVar14 = *DAT_01a238a0;
      lVar15 = (ulong)(((uint)((int)local_890 >> 0xd) >> 0x12 | 0x3ff) & (int)local_890 >> 0xd) *
               0x40;
      lVar5 = *(long *)(lVar14 + 0x10 + lVar15);
      uVar13 = (ulong)((local_890 & 0x1fff) * *(int *)(lVar14 + 0x30 + lVar15));
      local_8d0 = (lVar5 + uVar13) -
                  ((long)*(int *)(lVar14 + 0x34 + lVar15) & *(ulong *)(lVar5 + 8 + uVar13));
      lVar15 = (ulong)(((uint)((int)local_888 >> 0xd) >> 0x12 | 0x3ff) & (int)local_888 >> 0xd) *
               0x40;
      lVar5 = *(long *)(lVar14 + 0x10 + lVar15);
      uVar13 = (ulong)((local_888 & 0x1fff) * *(int *)(lVar14 + 0x30 + lVar15));
      local_8c8 = ((lVar5 + uVar13) -
                  ((long)*(int *)(lVar14 + 0x34 + lVar15) & *(ulong *)(lVar5 + 8 + uVar13))) +
                  local_880;
      local_8b0 = local_878;
      local_8b8 = local_880;
      uVar18 = FUN_00354c00(&local_8d0,6);
      *(undefined4 *)(lVar16 + 0x670 + lVar17) = uVar18;
    }
  }
  puVar3 = (uint *)(lVar16 + 0x644 + lVar17);
  if (*puVar3 != 0xffffffff) {
    cVar10 = FUN_00bcfad0();
    if (cVar10 == '\0') {
      uVar13 = (ulong)((*puVar3 & 0x1fff) * DAT_02689800);
      uVar13 = (ulong)((*(uint *)(((uVar13 + DAT_026897f8) -
                                  (*(ulong *)(DAT_026897f8 + 8 + uVar13) & (long)DAT_02689818)) +
                                 0x68) & 0x1fff) * DAT_02689800);
      *(undefined4 *)
       (((DAT_026897f8 + uVar13) - ((long)DAT_02689818 & *(ulong *)(DAT_026897f8 + 8 + uVar13))) +
       0x9e0) = 0xffffffff;
    }
  }
  FUN_00911c50((ulong)param_1,0xffffffff,0,0);
  if (*(char *)(DAT_0273ea90 + 0xa8) != '\0') {
    local_8d0 = *(long *)(DAT_0273ea90 + 0xa9);
    if (*(long *)(*(long *)(DAT_0273ea80 + 8) + 0x620 + lVar17) == local_8d0) {
      cVar10 = FUN_00752710();
      if (cVar10 == '\0') {
        iVar12 = FUN_0052b2b0();
        if (iVar12 != -1) {
          lVar16 = (ulong)((*(uint *)(*(long *)(DAT_0273ea80 + 8) + 4 + lVar17) & 0x1fff) *
                          DAT_02689590) + DAT_02689588;
          local_848 = 0x10;
          local_850 = 0x800;
          local_840 = 0;
          local_860 = 0;
          local_858 = 0xffffffff;
          local_868 = 0;
          cVar10 = FUN_00308ca0(&local_868,iVar12);
          if (cVar10 != '\0') {
            lVar14 = FUN_0100fd30(&local_868);
            puVar1 = (undefined8 *)(*(long *)(DAT_0273ea80 + 8) + 0x60 + lVar17);
            uVar7 = *puVar1;
            uVar8 = puVar1[1];
            puVar1 = (undefined8 *)(*(long *)(DAT_0273ea80 + 8) + 0x70 + lVar17);
            uVar9 = puVar1[1];
            *(undefined8 *)(lVar14 + 0x30) = *puVar1;
            *(undefined8 *)(lVar14 + 0x38) = uVar9;
            *(undefined8 *)(lVar14 + 0x20) = uVar7;
            *(undefined8 *)(lVar14 + 0x28) = uVar8;
            lVar17 = FUN_003090d0(&local_868,*(undefined4 *)PTR_DAT_01975088,
                                  *(undefined4 *)PTR_DAT_01975070);
            if (lVar17 != 0) {
              uVar18 = FUN_00301cb0(lVar16);
              *(undefined4 *)(lVar17 + 0xc) = uVar18;
              FUN_0032dbf0(lVar14);
            }
          }
        }
      }
    }
  }
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

