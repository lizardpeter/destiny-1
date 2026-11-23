
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

ulong FUN_007420f0(long param_1,undefined1 (*param_2) [16],float *param_3)

{
  uint uVar1;
  long lVar2;
  undefined1 auVar3 [16];
  long lVar4;
  undefined1 auVar5 [16];
  char cVar6;
  undefined4 uVar7;
  uint uVar8;
  uint uVar9;
  int iVar10;
  long lVar11;
  long lVar12;
  long lVar13;
  ulong uVar14;
  char *pcVar15;
  long *plVar16;
  long lVar17;
  ulong uVar18;
  undefined8 uVar19;
  undefined1 auVar20 [16];
  undefined8 extraout_XMM0_Qb;
  float fVar21;
  float fVar22;
  float fVar28;
  float fVar30;
  undefined1 auVar23 [16];
  float fVar29;
  float fVar31;
  float fVar32;
  float fVar33;
  undefined1 auVar24 [16];
  undefined1 auVar25 [16];
  undefined1 auVar26 [16];
  undefined1 auVar27 [16];
  undefined1 auVar34 [16];
  float fVar35;
  undefined1 auVar36 [16];
  long local_a40;
  long local_a38;
  long local_a28;
  undefined4 local_a20;
  undefined1 local_a18;
  undefined1 local_a10 [16];
  uint local_a00;
  uint local_9f8;
  long local_9f0;
  undefined4 local_9e8;
  undefined4 local_9e0 [2];
  undefined1 local_9d8 [24];
  uint local_9c0;
  long local_9b8;
  uint local_9a8 [64];
  undefined8 local_8a8;
  undefined8 local_8a0;
  undefined4 local_898;
  undefined8 local_890;
  undefined8 local_888;
  undefined8 local_880;
  undefined1 local_78 [16];
  undefined1 local_68 [16];
  undefined1 local_58 [16];
  undefined8 local_48;
  undefined8 uStack_40;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  uVar1 = *(uint *)(param_1 + 0x2c);
  uVar18 = 0xffffffff;
  if ((*(uint *)(&DAT_0267fe58 + (ulong)(uVar1 >> 5 & 0xff) * 4) >> (uVar1 & 0x1f) & 1) == 0)
  goto LAB_0074276d;
  FUN_0073e660(param_1);
  *(undefined4 *)(param_1 + 0x1310) = 0;
  *(undefined4 *)(param_1 + 0x1314) = 0xffffffff;
  *(undefined4 *)(param_1 + 0x1220) = 0xffffffff;
  if (param_3 != (float *)0x0) {
    if (0.0 <= *param_3) {
      uVar7 = FUN_00591c80();
      *(undefined4 *)(param_1 + 0x1314) = uVar7;
    }
    if (param_3[4] == -NAN) {
      lVar11 = *(long *)(param_3 + 2);
      if (((lVar11 == 0) ||
          (pcVar15 = (char *)(lVar11 + (long)(param_3 + 2)), pcVar15 == (char *)0x0)) ||
         (*pcVar15 == '\0')) goto LAB_007421b5;
    }
    *(float *)(param_1 + 0x1220) = param_3[4];
  }
LAB_007421b5:
  local_888 = 0x10;
  local_890 = 0x800;
  local_880 = 0;
  local_8a0 = 0;
  local_898 = 0xffffffff;
  local_8a8 = 0;
  cVar6 = FUN_00308eb0(&local_8a8,*(undefined4 *)(param_1 + 0x1208));
  uVar18 = 0xffffffff;
  if (cVar6 != '\0') {
    lVar11 = FUN_0100fd30(&local_8a8);
    lVar12 = FUN_003090d0(&local_8a8,*(undefined4 *)PTR_DAT_019b4018,*(undefined4 *)PTR_DAT_019b3fe8
                         );
    auVar5 = _DAT_01649b20;
    auVar26 = vpshufd_avx(*param_2,0xff);
    auVar3 = vpand_avx(*param_2,_DAT_01649b20);
    fVar22 = auVar26._0_4_;
    auVar23._0_4_ = fVar22 * fVar22;
    fVar29 = auVar26._4_4_;
    auVar23._4_4_ = fVar29 * fVar29;
    fVar31 = auVar26._8_4_;
    auVar23._8_4_ = fVar31 * fVar31;
    fVar33 = auVar26._12_4_;
    auVar23._12_4_ = fVar33 * fVar33;
    auVar25 = vsubps_avx(auVar23,_DAT_01ac63c0);
    auVar26 = vpshufd_avx(auVar3,0x2a);
    auVar20 = vpand_avx(auVar26,_DAT_01649b20);
    fVar35 = auVar3._0_4_;
    auVar26 = vandps_avx(auVar25,_DAT_01649b40);
    auVar24 = vpshufd_avx(auVar3,1);
    auVar23 = vinsertps_avx(auVar24,ZEXT416((uint)(0.0 - fVar35)),0x10);
    auVar23 = vshufps_avx(auVar23,auVar3,0xf4);
    fVar21 = auVar26._0_4_ + fVar35 * auVar20._0_4_ + fVar22 * auVar23._0_4_;
    fVar28 = auVar26._4_4_ + auVar3._4_4_ * auVar20._4_4_ + fVar29 * auVar23._4_4_;
    fVar30 = auVar26._8_4_ + auVar3._8_4_ * auVar20._8_4_ + fVar31 * auVar23._8_4_;
    fVar32 = auVar26._12_4_ + auVar3._12_4_ * auVar20._12_4_ + fVar33 * auVar23._12_4_;
    auVar23 = vpshufd_avx(auVar3,0);
    local_58._0_4_ = fVar21 + fVar21;
    local_58._4_4_ = fVar28 + fVar28;
    local_58._8_4_ = fVar30 + fVar30;
    local_58._12_4_ = fVar32 + fVar32;
    auVar26 = vpshufd_avx(auVar3,0xb);
    auVar20 = vpshufd_avx(local_58,0xd2);
    auVar26 = vinsertps_avx(auVar26,ZEXT416((uint)(0.0 - auVar24._0_4_)),0x20);
    auVar26 = vblendps_avx(auVar26,auVar3,8);
    fVar22 = fVar35 * auVar23._0_4_ + auVar25._0_4_ + fVar22 * auVar26._0_4_;
    fVar29 = auVar3._4_4_ * auVar23._4_4_ + 0.0 + fVar29 * auVar26._4_4_;
    fVar31 = auVar3._8_4_ * auVar23._8_4_ + 0.0 + fVar31 * auVar26._8_4_;
    fVar33 = auVar3._12_4_ * auVar23._12_4_ + 0.0 + fVar33 * auVar26._12_4_;
    local_78._0_4_ = fVar22 + fVar22;
    local_78._4_4_ = fVar29 + fVar29;
    local_78._8_4_ = fVar31 + fVar31;
    local_78._12_4_ = fVar33 + fVar33;
    auVar26 = vpshufd_avx(local_78,0xc9);
    auVar34._0_4_ = auVar20._0_4_ * auVar26._0_4_;
    auVar34._4_4_ = auVar20._4_4_ * auVar26._4_4_;
    auVar34._8_4_ = auVar20._8_4_ * auVar26._8_4_;
    auVar34._12_4_ = auVar20._12_4_ * auVar26._12_4_;
    auVar26 = vpshufd_avx(local_58,0xc9);
    auVar23 = vpshufd_avx(local_78,0xd2);
    auVar24._0_4_ = auVar26._0_4_ * auVar23._0_4_;
    auVar24._4_4_ = auVar26._4_4_ * auVar23._4_4_;
    auVar24._8_4_ = auVar26._8_4_ * auVar23._8_4_;
    auVar24._12_4_ = auVar26._12_4_ * auVar23._12_4_;
    auVar26 = vsubps_avx(auVar24,auVar34);
    fVar22 = auVar26._0_4_;
    auVar36._0_4_ = fVar22 * fVar22;
    fVar31 = auVar26._4_4_;
    auVar36._4_4_ = fVar31 * fVar31;
    fVar21 = auVar26._8_4_;
    auVar36._8_4_ = fVar21 * fVar21;
    fVar30 = auVar26._12_4_;
    auVar36._12_4_ = fVar30 * fVar30;
    auVar26 = vpshufd_avx(auVar36,0x55);
    auVar23 = vpshufd_avx(auVar36,0);
    auVar3 = vpshufd_avx(auVar36,0xaa);
    auVar25._0_4_ = auVar3._0_4_ + auVar23._0_4_ + auVar26._0_4_;
    auVar25._4_4_ = auVar3._4_4_ + auVar23._4_4_ + auVar26._4_4_;
    auVar25._8_4_ = auVar3._8_4_ + auVar23._8_4_ + auVar26._8_4_;
    auVar25._12_4_ = auVar3._12_4_ + auVar23._12_4_ + auVar26._12_4_;
    auVar3 = vrsqrtps_avx(auVar25);
    fVar29 = auVar3._0_4_;
    fVar33 = auVar3._4_4_;
    fVar28 = auVar3._8_4_;
    fVar32 = auVar3._12_4_;
    auVar26._0_4_ = fVar29 * fVar29 * auVar25._0_4_ * (float)DAT_01649b30;
    auVar26._4_4_ = fVar33 * fVar33 * auVar25._4_4_ * DAT_01649b30._4_4_;
    auVar26._8_4_ = fVar28 * fVar28 * auVar25._8_4_ * DAT_01649b30._8_4_;
    auVar26._12_4_ = fVar32 * fVar32 * auVar25._12_4_ * DAT_01649b30._12_4_;
    auVar26 = vsubps_avx(_DAT_01649b30,auVar26);
    auVar20._0_4_ = fVar29 + fVar29 * auVar26._0_4_;
    auVar20._4_4_ = fVar33 + fVar33 * auVar26._4_4_;
    auVar20._8_4_ = fVar28 + fVar28 * auVar26._8_4_;
    auVar20._12_4_ = fVar32 + fVar32 * auVar26._12_4_;
    auVar23 = vcmpps_avx(auVar20,auVar20,0);
    auVar26 = vandps_avx(auVar23,auVar20);
    auVar23 = vandnps_avx(auVar23,auVar3);
    auVar26 = vorps_avx(auVar23,auVar26);
    auVar27._0_4_ = fVar22 * auVar26._0_4_;
    auVar27._4_4_ = fVar31 * auVar26._4_4_;
    auVar27._8_4_ = fVar21 * auVar26._8_4_;
    auVar27._12_4_ = fVar30 * auVar26._12_4_;
    auVar26 = vcmpps_avx(auVar26,_DAT_01649b60,0);
    local_68 = vandnps_avx(auVar26,auVar27);
    local_48 = _DAT_01649b50;
    uStack_40 = uRam0000000001649b58;
    uVar19 = FUN_00095770(local_78);
    *(undefined8 *)(lVar11 + 0x20) = uVar19;
    *(undefined8 *)(lVar11 + 0x28) = extraout_XMM0_Qb;
    auVar23 = vandnps_avx(_DAT_01ac62f0,*(undefined1 (*) [16])(lVar11 + 0x30));
    auVar26 = vandps_avx(auVar5,param_2[1]);
    auVar3._8_8_ = uRam0000000001649b58;
    auVar3._0_8_ = _DAT_01649b50;
    auVar26 = vorps_avx(auVar26,auVar3);
    auVar26 = vandps_avx(_DAT_01ac62f0,auVar26);
    auVar26 = vorps_avx(auVar23,auVar26);
    *(undefined1 (*) [16])(lVar11 + 0x30) = auVar26;
    *(undefined1 *)(lVar12 + 0xc) = 1;
    local_9e0[0] = *(undefined4 *)(param_1 + 0x4bc);
    lVar12 = FUN_0052b680(local_9e0);
    if (lVar12 != 0) {
      lVar13 = FUN_003090d0(&local_8a8,*(undefined4 *)PTR_DAT_019b1be8,
                            *(undefined4 *)PTR_DAT_019b1be0);
      if (lVar13 != 0) {
        lVar2 = *(long *)(lVar13 + 0x10);
        FUN_00309360(&local_8a8,lVar13 + 0x10,*(undefined4 *)PTR_DAT_019b1bf0,
                     *(long *)(lVar12 + 8) + lVar2);
        if (0 < *(long *)(lVar12 + 8)) {
          plVar16 = (long *)(lVar13 + 0x18);
          lVar13 = 0;
          do {
            lVar17 = *(long *)(lVar12 + 0x10) + lVar12 + 0x10;
            lVar4 = lVar2 * 8 + 0x14 + *plVar16;
            *(undefined4 *)((long)plVar16 + lVar13 * 8 + lVar4 + -4) =
                 *(undefined4 *)(lVar17 + 0x10 + lVar13 * 8);
            *(undefined4 *)((long)plVar16 + lVar13 * 8 + lVar4) =
                 *(undefined4 *)(lVar17 + 0x14 + lVar13 * 8);
            lVar13 = lVar13 + 1;
          } while (lVar13 < *(long *)(lVar12 + 8));
        }
      }
    }
    uVar8 = FUN_0032dbf0(lVar11);
    uVar18 = (ulong)uVar8;
    if (uVar8 != 0xffffffff) {
      FUN_0073e060(uVar8,*(undefined4 *)(param_1 + 0x120c));
      uVar9 = FUN_006ed9f0(uVar1);
      if ((uVar9 != 0xffffffff) &&
         (uVar14 = (ulong)((uVar9 & 0x1fff) * DAT_02689800),
         uVar14 = (ulong)((*(uint *)(((uVar14 + DAT_026897f8) -
                                     (*(ulong *)(DAT_026897f8 + 8 + uVar14) & (long)DAT_02689818)) +
                                    0x68) & 0x1fff) * DAT_02689800),
         *(int *)(((DAT_026897f8 + uVar14) -
                  ((long)DAT_02689818 & *(ulong *)(DAT_026897f8 + 8 + uVar14))) + 0x9d8) != -1)) {
        lVar11 = (ulong)((uVar8 & 0x1fff) * DAT_02692230) + DAT_02692228;
        if (lVar11 != 0) {
          cVar6 = FUN_00337fe0(lVar11,*(undefined4 *)PTR_DAT_019b4000,local_9d8,0);
          if (cVar6 != '\0') {
            lVar13 = (ulong)(((uint)((int)local_9c0 >> 0xd) >> 0x12 | 0x3ff) & (int)local_9c0 >> 0xd
                            ) * 0x40;
            lVar11 = *DAT_01a238a0;
            lVar12 = *(long *)(lVar11 + 0x10 + lVar13);
            uVar14 = (ulong)((local_9c0 & 0x1fff) * *(int *)(lVar11 + 0x30 + lVar13));
            uVar9 = *(uint *)(local_9b8 + 0x24 +
                             ((lVar12 + uVar14) -
                             ((long)*(int *)(lVar11 + 0x34 + lVar13) &
                             *(ulong *)(lVar12 + 8 + uVar14))));
            if (uVar9 != 0xffffffff) {
              uVar14 = (ulong)((uVar9 & 0x1fff) * DAT_02689800);
              iVar10 = FUN_00737da0((DAT_026897f8 + uVar14) -
                                    ((long)DAT_02689818 & *(ulong *)(DAT_026897f8 + 8 + uVar14)),
                                    0x40,local_9a8);
              if (0 < iVar10) {
                uVar14 = (ulong)((local_9a8[0] & 0x1fff) * DAT_02689800);
                FUN_006c1c50((DAT_026897f8 + uVar14) -
                             ((long)DAT_02689818 & *(ulong *)(DAT_026897f8 + 8 + uVar14)),uVar1);
              }
            }
          }
        }
      }
      cVar6 = FUN_00337fe0((ulong)((uVar8 & 0x1fff) * DAT_02692230) + DAT_02692228,
                           *(undefined4 *)PTR_DAT_019b3360,local_a10,0);
      if (cVar6 != '\0') {
        local_a18 = 0;
        lVar11 = *DAT_01a238a0;
        lVar13 = (ulong)(((uint)((int)local_a00 >> 0xd) >> 0x12 | 0x3ff) & (int)local_a00 >> 0xd) *
                 0x40;
        lVar12 = *(long *)(lVar11 + 0x10 + lVar13);
        uVar14 = (ulong)((local_a00 & 0x1fff) * *(int *)(lVar11 + 0x30 + lVar13));
        local_a40 = (lVar12 + uVar14) -
                    ((long)*(int *)(lVar11 + 0x34 + lVar13) & *(ulong *)(lVar12 + 8 + uVar14));
        lVar13 = (ulong)(((uint)((int)local_9f8 >> 0xd) >> 0x12 | 0x3ff) & (int)local_9f8 >> 0xd) *
                 0x40;
        lVar12 = *(long *)(lVar11 + 0x10 + lVar13);
        uVar14 = (ulong)((local_9f8 & 0x1fff) * *(int *)(lVar11 + 0x30 + lVar13));
        local_a38 = ((lVar12 + uVar14) -
                    ((long)*(int *)(lVar11 + 0x34 + lVar13) & *(ulong *)(lVar12 + 8 + uVar14))) +
                    local_9f0;
        local_a20 = local_9e8;
        local_a28 = local_9f0;
        FUN_00353640(&local_a40,uVar1);
      }
    }
    FUN_00072050(local_78,uVar18);
    *(undefined8 *)(param_1 + 0x1218) = local_78._0_8_;
  }
  if (*(int *)(param_1 + 0x2c) != -1) {
    FUN_002d94f0(*(undefined4 *)(param_1 + 0x24));
  }
LAB_0074276d:
  if (*DAT_01a1f100 == local_38) {
    return uVar18;
  }
  uVar18 = thunk_FUN_012aa7f6();
  return uVar18;
}

