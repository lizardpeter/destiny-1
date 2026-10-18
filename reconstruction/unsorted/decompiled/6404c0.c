
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_006404c0(void)

{
  long *plVar1;
  undefined1 auVar2 [16];
  uint uVar3;
  long lVar4;
  long lVar5;
  undefined1 auVar6 [16];
  undefined *puVar7;
  undefined *puVar8;
  undefined *puVar9;
  uint *puVar10;
  uint *puVar11;
  char cVar12;
  int iVar13;
  uint uVar14;
  uint uVar15;
  ulong uVar16;
  undefined8 uVar17;
  long lVar18;
  long lVar19;
  ulong uVar20;
  long lVar21;
  long lVar22;
  int iVar23;
  float fVar24;
  float fVar25;
  undefined1 auVar26 [16];
  long local_300;
  long local_2f8;
  long local_2e8;
  undefined4 local_2e0;
  undefined1 local_2d8;
  undefined1 local_2d0 [16];
  uint local_2c0;
  uint local_2b8;
  long local_2b0;
  undefined4 local_2a8;
  long local_2a0;
  undefined1 local_298 [8];
  uint local_290;
  undefined1 local_288 [16];
  undefined1 local_278 [24];
  uint local_260;
  long local_258;
  undefined1 local_248 [48];
  undefined1 local_218 [24];
  uint local_200;
  long local_1f8;
  long local_1e8;
  uint auStack_1e0 [2];
  float afStack_1d8 [104];
  long local_38;
  
  puVar10 = DAT_026bea70;
  local_38 = *DAT_01a1f100;
  FUN_0063f640();
  FUN_0063b880(DAT_026bea78);
  FUN_0063b880(DAT_026bea80);
  FUN_0063b880(DAT_026bea88);
  FUN_0063b880(DAT_026bea90);
  FUN_0063b880(DAT_026bea98);
  FUN_006412c0(DAT_026beaa0);
  puVar11 = DAT_026bea70;
  uVar15 = *DAT_026bea70;
  if (uVar15 != 0xffffffff) {
    lVar19 = (ulong)(((uint)((int)uVar15 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar15 >> 0xd) * 0x40;
    lVar22 = *DAT_01a238a0;
    lVar18 = *(long *)(lVar22 + 0x10 + lVar19);
    uVar16 = (ulong)((uVar15 & 0x1fff) * *(int *)(lVar22 + 0x30 + lVar19));
    iVar13 = FUN_00346c90((lVar18 + uVar16) -
                          ((long)*(int *)(lVar22 + 0x34 + lVar19) & *(ulong *)(lVar18 + 8 + uVar16))
                         );
    if (iVar13 < 1) {
      uVar17 = FUN_00346d20();
      FUN_0034a1d0(uVar17,*puVar11);
    }
  }
  fVar25 = (float)puVar10[0xb];
  fVar24 = (float)FUN_00591b80();
  fVar25 = fVar25 - fVar24;
  if (fVar25 < 0.0) {
    fVar25 = 0.0;
  }
  puVar10[0xb] = (uint)fVar25;
  uVar15 = puVar10[9];
  if ((int)puVar10[8] < 1) {
    uVar14 = puVar10[10];
    if ((int)uVar15 < 0x12) {
      if (2 < (int)uVar14) {
        puVar10[9] = uVar15 + 1;
        puVar10[10] = 0;
        goto LAB_00640657;
      }
    }
    else if (2 < (int)uVar14) goto LAB_00640657;
    puVar10[10] = uVar14 + 1;
  }
  else if ((0 < (int)uVar15) && (fVar25 <= 0.0)) {
    if ((int)puVar10[10] < 1) {
      puVar10[9] = uVar15 - 1;
      puVar10[10] = 3;
    }
    else {
      puVar10[10] = puVar10[10] - 1;
    }
  }
LAB_00640657:
  puVar10[8] = 0;
  cVar12 = FUN_00305010(local_288);
  if (cVar12 != '\0') {
    FUN_00074a80(local_298,DAT_0273ea80);
    lVar22 = 0;
    while (lVar18 = FUN_00074a90(local_298), uVar15 = local_290, local_2a0 = lVar18, lVar18 != 0) {
      uVar14 = FUN_006ed930(local_290);
      if (uVar14 != 0xffffffff) {
        auVar2 = *(undefined1 (*) [16])
                  ((ulong)((uVar14 & 0x1fff) * DAT_02692230) + 0xe0 + DAT_02692228);
        auStack_1e0[lVar22 * 6] = uVar15;
        (&local_1e8)[lVar22 * 3] = lVar18;
        auVar2 = vandps_avx(auVar2,_DAT_01643c10);
        auVar2 = vorps_avx(auVar2,_DAT_01643c20);
        auVar2 = vsubps_avx(auVar2,local_288);
        auStack_1e0[lVar22 * 6 + 1] = uVar14;
        auVar26._0_4_ = auVar2._0_4_ * auVar2._0_4_;
        auVar26._4_4_ = auVar2._4_4_ * auVar2._4_4_;
        auVar26._8_4_ = auVar2._8_4_ * auVar2._8_4_;
        auVar26._12_4_ = auVar2._12_4_ * auVar2._12_4_;
        auVar2 = vpshufd_avx(auVar26,0x55);
        auVar6 = vpshufd_avx(auVar26,0);
        auVar26 = vpshufd_avx(auVar26,0xaa);
        afStack_1d8[lVar22 * 6] = auVar26._0_4_ + auVar6._0_4_ + auVar2._0_4_;
        lVar22 = lVar22 + 1;
      }
    }
    iVar13 = (int)lVar22;
    lVar22 = 0;
    FUN_0006a350(&local_1e8,(long)iVar13,0x18,FUN_00640bc0,0);
    puVar9 = PTR_DAT_019b2430;
    puVar8 = PTR_DAT_019b1b60;
    puVar7 = PTR_DAT_019b1b40;
    if (0 < iVar13) {
      do {
        uVar15 = puVar10[9];
        uVar14 = 0;
        iVar23 = (int)lVar22;
        if ((iVar23 < (int)uVar15) && (uVar14 = 3, iVar23 == uVar15 - 1)) {
          uVar14 = puVar10[10];
        }
        lVar18 = (&local_1e8)[lVar22 * 3];
        if (((bool)*(char *)(lVar18 + 0x2868) != iVar23 < (int)uVar15) ||
           (*(uint *)(lVar18 + 0x286c) != uVar14)) {
          plVar1 = &local_1e8 + lVar22 * 3;
          if (((int)uVar15 <= iVar23) || ((int)uVar14 < *(int *)(lVar18 + 0x286c))) {
            puVar10[0xb] = 0x3f800000;
            lVar18 = *plVar1;
          }
          *(bool *)(lVar18 + 0x2868) = iVar23 < (int)uVar15;
          *(uint *)(*plVar1 + 0x286c) = uVar14;
          *(undefined1 *)(*plVar1 + 0x2840) = 1;
          lVar19 = DAT_02692228;
          uVar16 = (ulong)((auStack_1e0[lVar22 * 6 + 1] & 0x1fff) * DAT_02692230);
          lVar18 = DAT_02692228 + uVar16;
          cVar12 = FUN_003381f0(lVar18,*(undefined4 *)puVar8,
                                *(undefined4 *)(DAT_02692228 + 0x54 + uVar16),local_218);
          if (cVar12 != '\0') {
            lVar21 = (ulong)(((uint)((int)local_200 >> 0xd) >> 0x12 | 0x3ff) & (int)local_200 >> 0xd
                            ) * 0x40;
            lVar4 = *DAT_01a238a0;
            lVar5 = *(long *)(lVar4 + 0x10 + lVar21);
            uVar20 = (ulong)((local_200 & 0x1fff) * *(int *)(lVar4 + 0x30 + lVar21));
            uVar3 = *(uint *)(local_1f8 + 0x24 +
                             ((lVar5 + uVar20) -
                             ((long)*(int *)(lVar4 + 0x34 + lVar21) & *(ulong *)(lVar5 + 8 + uVar20)
                             )));
            if (uVar3 != 0xffffffff) {
              lVar21 = (ulong)(((uint)((int)uVar3 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar3 >> 0xd) *
                       0x40;
              lVar4 = *DAT_01a238a0;
              lVar5 = *(long *)(lVar4 + 0x10 + lVar21);
              uVar20 = (ulong)((uVar3 & 0x1fff) * *(int *)(lVar4 + 0x30 + lVar21));
              FUN_00642630((lVar5 + uVar20) -
                           ((long)*(int *)(lVar4 + 0x34 + lVar21) & *(ulong *)(lVar5 + 8 + uVar20)),
                           iVar23 < (int)uVar15);
            }
          }
          cVar12 = FUN_003381f0(lVar18,*(undefined4 *)puVar9,*(undefined4 *)(lVar19 + 0x54 + uVar16)
                                ,local_2d0);
          if (cVar12 != '\0') {
            local_2d8 = 0;
            lVar4 = *DAT_01a238a0;
            iVar23 = 0;
            lVar21 = (ulong)(((uint)((int)local_2c0 >> 0xd) >> 0x12 | 0x3ff) & (int)local_2c0 >> 0xd
                            ) * 0x40;
            lVar5 = *(long *)(lVar4 + 0x10 + lVar21);
            uVar20 = (ulong)((local_2c0 & 0x1fff) * *(int *)(lVar4 + 0x30 + lVar21));
            local_300 = (lVar5 + uVar20) -
                        ((long)*(int *)(lVar4 + 0x34 + lVar21) & *(ulong *)(lVar5 + 8 + uVar20));
            lVar21 = (ulong)(((uint)((int)local_2b8 >> 0xd) >> 0x12 | 0x3ff) & (int)local_2b8 >> 0xd
                            ) * 0x40;
            lVar5 = *(long *)(lVar4 + 0x10 + lVar21);
            uVar20 = (ulong)((local_2b8 & 0x1fff) * *(int *)(lVar4 + 0x30 + lVar21));
            local_2f8 = ((lVar5 + uVar20) -
                        ((long)*(int *)(lVar4 + 0x34 + lVar21) & *(ulong *)(lVar5 + 8 + uVar20))) +
                        local_2b0;
            local_2e0 = local_2a8;
            local_2e8 = local_2b0;
            do {
              uVar15 = FUN_00353640(&local_300,iVar23);
              FUN_003381f0(lVar18,*(undefined4 *)puVar8,*(undefined4 *)(lVar19 + 0x54 + uVar16),
                           local_248);
              if ((uVar15 != 0xffffffff) &&
                 (uVar20 = (ulong)((uVar15 & 0x1fff) * DAT_02692230),
                 cVar12 = FUN_003381f0(DAT_02692228 + uVar20,*(undefined4 *)puVar7,
                                       *(undefined4 *)(DAT_02692228 + 0x54 + uVar20),local_278),
                 cVar12 != '\0')) {
                lVar21 = (ulong)(((uint)((int)local_260 >> 0xd) >> 0x12 | 0x3ff) &
                                (int)local_260 >> 0xd) * 0x40;
                lVar4 = *DAT_01a238a0;
                lVar5 = *(long *)(lVar4 + 0x10 + lVar21);
                uVar20 = (ulong)((local_260 & 0x1fff) * *(int *)(lVar4 + 0x30 + lVar21));
                uVar15 = *(uint *)(local_258 + 0x24 +
                                  ((lVar5 + uVar20) -
                                  ((long)*(int *)(lVar4 + 0x34 + lVar21) &
                                  *(ulong *)(lVar5 + 8 + uVar20))));
                if (uVar15 != 0xffffffff) {
                  lVar21 = (ulong)(((uint)((int)uVar15 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar15 >> 0xd
                                  ) * 0x40;
                  lVar4 = *DAT_01a238a0;
                  lVar5 = *(long *)(lVar4 + 0x10 + lVar21);
                  uVar20 = (ulong)((uVar15 & 0x1fff) * *(int *)(lVar4 + 0x30 + lVar21));
                  FUN_00644810((lVar5 + uVar20) -
                               ((long)*(int *)(lVar4 + 0x34 + lVar21) &
                               *(ulong *)(lVar5 + 8 + uVar20)),iVar23 < (int)uVar14);
                }
              }
              iVar23 = iVar23 + 1;
            } while (iVar23 != 3);
          }
        }
        lVar22 = lVar22 + 1;
      } while ((int)lVar22 != iVar13);
    }
  }
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

