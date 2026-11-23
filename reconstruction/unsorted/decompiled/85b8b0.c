
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int FUN_0085b8b0(undefined8 param_1,long param_2,undefined8 *param_3,undefined1 (*param_4) [16],
                int param_5,undefined8 param_6,long param_7)

{
  undefined4 uVar1;
  undefined4 uVar2;
  int iVar3;
  long lVar4;
  undefined1 auVar5 [16];
  char cVar6;
  int iVar7;
  int iVar8;
  long lVar9;
  undefined1 (*pauVar10) [16];
  long lVar11;
  ulong uVar12;
  long lVar13;
  long lVar14;
  uint uVar15;
  long lVar16;
  undefined8 uVar17;
  float *pfVar18;
  int iVar19;
  undefined8 uVar20;
  undefined8 in_XMM0_Qb;
  undefined8 extraout_XMM0_Qb;
  undefined1 auVar21 [16];
  undefined1 auVar22 [16];
  undefined1 auVar23 [16];
  float fVar24;
  float fVar27;
  float fVar28;
  undefined1 auVar25 [16];
  float fVar29;
  undefined1 auVar26 [16];
  undefined1 auVar30 [16];
  undefined1 auVar31 [16];
  int local_74;
  float local_68;
  float fStack_64;
  float fStack_60;
  float fStack_5c;
  float local_48;
  
  local_48 = (float)param_1;
  lVar16 = (long)*(int *)(param_2 + 0x18);
  local_74 = 0;
  if (0 < (int)(&DAT_0270e0d4)[lVar16 * 2]) {
    uVar1 = *(undefined4 *)(*(long *)(param_7 + 0x15c0) + 0x25b8);
    uVar2 = *(undefined4 *)(&DAT_000025e8 + *(long *)(param_7 + 0x15c0));
    *(undefined2 *)(param_7 + 0x15d5) = 0x82bd;
    lVar9 = FUN_0082cb90(10);
    local_74 = 0;
    if (lVar9 != 0) {
      cVar6 = FUN_0082bd10(param_7,1,lVar9 + 0x20);
      if (cVar6 != '\0') {
        cVar6 = FUN_0082bd10(param_7,2,lVar9 + 0xb0);
        if (cVar6 != '\0') {
          *(byte *)(param_7 + 0x15ad) = *(byte *)(param_7 + 0x15ad) | 4;
          pauVar10 = (undefined1 (*) [16])FUN_0082b940(param_7,0x30,0x20);
          uVar20 = FUN_00095760();
          auVar25 = ZEXT816(0) << 0x40;
          uVar17 = extraout_XMM0_Qb;
          if ((*(byte *)((long)param_3 + 0x5e) & 1) != 0) {
            uVar20 = *param_3;
            uVar17 = param_3[1];
            auVar25 = vandps_avx(*(undefined1 (*) [16])(param_3 + 2),_DAT_01664a70);
            auVar25 = vorps_avx(auVar25,_DAT_01664a80);
          }
          *pauVar10 = auVar25;
          *(undefined8 *)pauVar10[1] = uVar20;
          *(undefined8 *)(pauVar10[1] + 8) = uVar17;
          FUN_007e10e0(*(undefined8 *)(param_7 + 0x15c0),0x20,0x20);
          lVar11 = FUN_0082e420(0x20);
          local_74 = 0;
          FUN_007deb70(*(undefined8 *)(param_7 + 0x15c0),lVar11,0);
          uVar15 = (int)*(uint *)(param_3 + 7) >> 0xd;
          lVar13 = (ulong)((uVar15 >> 0x12 | 0x3ff) & uVar15) * 0x40;
          lVar9 = *DAT_01a238a0;
          lVar4 = *(long *)(lVar9 + 0x10 + lVar13);
          uVar12 = (ulong)((*(uint *)(param_3 + 7) & 0x1fff) * *(int *)(lVar9 + 0x30 + lVar13));
          FUN_007dec20(*(undefined8 *)(param_7 + 0x15c0),
                       *(undefined4 *)
                        (((lVar4 + uVar12) -
                         ((long)*(int *)(lVar9 + 0x34 + lVar13) & *(ulong *)(lVar4 + 8 + uVar12))) +
                        0x18),0,0,0);
          iVar3 = (&DAT_0270e0d0)[lVar16 * 2];
          FUN_007dec20(*(undefined8 *)(param_7 + 0x15c0),(&DAT_0270e5d0)[DAT_0270e5ec],1,
                       iVar3 * 0x38,0);
          auVar5._8_8_ = in_XMM0_Qb;
          auVar5._0_8_ = param_1;
          auVar22 = vpshufd_avx(auVar5,0);
          lVar9 = 0;
          auVar23 = ZEXT816(0) << 0x40;
          auVar5 = vcmpps_avx(auVar23,auVar23,0);
          auVar21 = vpshufd_avx(*(undefined1 (*) [16])(param_3 + 8),0xff);
          fVar24 = auVar22._0_4_ + auVar21._0_4_;
          fVar27 = auVar22._4_4_ + auVar21._4_4_;
          fVar28 = auVar22._8_4_ + auVar21._8_4_;
          fVar29 = auVar22._12_4_ + auVar21._12_4_;
          auVar22 = vpand_avx(*(undefined1 (*) [16])(param_3 + 8),_DAT_01664a70);
          auVar22 = vpor_avx(auVar22,_DAT_01664a80);
          auVar26._0_4_ = fVar24 * fVar24;
          auVar26._4_4_ = fVar27 * fVar27;
          auVar26._8_4_ = fVar28 * fVar28;
          auVar26._12_4_ = fVar29 * fVar29;
          auVar22 = vsubps_avx(*param_4,auVar22);
          auVar30._0_4_ = auVar22._0_4_ * auVar22._0_4_;
          auVar30._4_4_ = auVar22._4_4_ * auVar22._4_4_;
          auVar30._8_4_ = auVar22._8_4_ * auVar22._8_4_;
          auVar30._12_4_ = auVar22._12_4_ * auVar22._12_4_;
          auVar22 = vpshufd_avx(auVar30,0x55);
          auVar21 = vpshufd_avx(auVar30,0);
          auVar30 = vpshufd_avx(auVar30,0xaa);
          auVar31._0_4_ = auVar30._0_4_ + auVar21._0_4_ + auVar22._0_4_;
          auVar31._4_4_ = auVar30._4_4_ + auVar21._4_4_ + auVar22._4_4_;
          auVar31._8_4_ = auVar30._8_4_ + auVar21._8_4_ + auVar22._8_4_;
          auVar31._12_4_ = auVar30._12_4_ + auVar21._12_4_ + auVar22._12_4_;
          auVar22 = vcmpps_avx(auVar26,auVar31,1);
          auVar21._0_4_ = auVar22._0_4_ ^ auVar5._0_4_;
          auVar21._4_4_ = auVar22._4_4_ ^ auVar5._4_4_;
          auVar21._8_4_ = auVar22._8_4_ ^ auVar5._8_4_;
          auVar21._12_4_ = auVar22._12_4_ ^ auVar5._12_4_;
          auVar5 = vcmpps_avx(auVar21,auVar23,0);
          iVar7 = vmovmskps_avx(auVar5);
          do {
            if ((*(int *)(param_3 + lVar9 + 4) == param_5) &&
               (uVar15 = *(uint *)((long)param_3 + lVar9 * 8 + 0x24), uVar15 != 0xffffffff)) {
              lVar14 = (ulong)(((uint)((int)uVar15 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar15 >> 0xd) *
                       0x40;
              lVar4 = *DAT_01a238a0;
              lVar13 = *(long *)(lVar4 + 0x10 + lVar14);
              uVar12 = (ulong)((uVar15 & 0x1fff) * *(int *)(lVar4 + 0x30 + lVar14));
              if (lVar13 + uVar12 !=
                  ((long)*(int *)(lVar4 + 0x34 + lVar14) & *(ulong *)(lVar13 + 8 + uVar12))) {
                cVar6 = FUN_0082b490(param_7);
                if (cVar6 != '\0') {
                  if (iVar7 == 0xf) {
                    FUN_007e1710(*(undefined8 *)(param_7 + 0x15c0),3,0x24,0,
                                 (&DAT_0270e0d4)[lVar16 * 2],0,0);
                    iVar8 = (&DAT_0270e0d4)[lVar16 * 2];
                  }
                  else {
                    iVar8 = (&DAT_0270e0d4)[lVar16 * 2];
                    if (0 < iVar8) {
                      pfVar18 = (float *)((long)(int)(&DAT_0270e0d0)[lVar16 * 2] * 0x38 +
                                         *(long *)(&DAT_0270e5d8 + (long)DAT_0270e5ec * 8));
                      iVar19 = 0;
                      do {
                        local_68 = auVar25._0_4_;
                        fStack_64 = auVar25._4_4_;
                        fStack_60 = auVar25._8_4_;
                        fStack_5c = auVar25._12_4_;
                        auVar22._0_4_ = local_68 + *pfVar18;
                        auVar22._4_4_ = fStack_64 + pfVar18[1];
                        auVar22._8_4_ = fStack_60 + pfVar18[2];
                        auVar22._12_4_ = fStack_5c + pfVar18[3];
                        auVar5 = vsubps_avx(*param_4,auVar22);
                        auVar23._0_4_ = auVar5._0_4_ * auVar5._0_4_;
                        auVar23._4_4_ = auVar5._4_4_ * auVar5._4_4_;
                        auVar23._8_4_ = auVar5._8_4_ * auVar5._8_4_;
                        auVar23._12_4_ = auVar5._12_4_ * auVar5._12_4_;
                        auVar5 = vpshufd_avx(auVar23,0x55);
                        auVar22 = vpshufd_avx(auVar23,0);
                        auVar21 = vpshufd_avx(auVar23,0xaa);
                        if (auVar21._0_4_ + auVar22._0_4_ + auVar5._0_4_ <=
                            (local_48 + pfVar18[10]) * (local_48 + pfVar18[10])) {
                          FUN_007e0f70(*(undefined8 *)(param_7 + 0x15c0),0x1a);
                          uVar20 = *(undefined8 *)(param_7 + 0x15c0);
                          uVar17 = 3;
                        }
                        else {
                          FUN_007e0f70(*(undefined8 *)(param_7 + 0x15c0),0x3d);
                          uVar20 = *(undefined8 *)(param_7 + 0x15c0);
                          uVar17 = 2;
                        }
                        FUN_007de590(uVar20,uVar17);
                        FUN_007dec20(*(undefined8 *)(param_7 + 0x15c0),(&DAT_0270e5d0)[DAT_0270e5ec]
                                     ,1,*(int *)(lVar11 + 8) * iVar19 + iVar3 * 0x38,0x24);
                        FUN_007e1710(*(undefined8 *)(param_7 + 0x15c0),3,0x24,0,1,0,0);
                        pfVar18 = pfVar18 + 0xe;
                        iVar19 = iVar19 + 1;
                        iVar8 = (&DAT_0270e0d4)[lVar16 * 2];
                      } while (iVar19 < iVar8);
                    }
                  }
                  local_74 = local_74 + iVar8;
                }
              }
            }
            lVar9 = lVar9 + 1;
          } while ((int)lVar9 != 3);
          FUN_0082ba20(param_7,0x30,0x20);
          *(byte *)(param_7 + 0x15ad) = *(byte *)(param_7 + 0x15ad) & 0xfb;
        }
      }
    }
    FUN_007de460(*(undefined8 *)(param_7 + 0x15c0),uVar1,uVar2);
    *(undefined4 *)(param_7 + 0x15d4) = 0;
  }
  return local_74;
}

