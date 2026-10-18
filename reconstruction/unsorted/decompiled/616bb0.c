
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00616bb0(uint *param_1)

{
  undefined8 *puVar1;
  long lVar2;
  long lVar3;
  long lVar4;
  ulong uVar5;
  undefined1 auVar6 [16];
  float fVar7;
  float fVar8;
  float fVar9;
  float fVar10;
  char cVar11;
  int iVar12;
  uint uVar13;
  uint uVar14;
  uint uVar15;
  ulong uVar16;
  long lVar17;
  long lVar18;
  long lVar19;
  ulong uVar20;
  float fVar21;
  float fVar26;
  float fVar27;
  float fVar28;
  undefined1 auVar22 [16];
  undefined1 auVar23 [16];
  undefined1 auVar24 [16];
  undefined8 extraout_XMM0_Qb;
  undefined1 auVar25 [64];
  undefined1 auVar29 [16];
  undefined1 auVar30 [16];
  undefined1 auVar31 [16];
  undefined1 auVar32 [16];
  undefined1 auVar33 [16];
  undefined1 auVar34 [16];
  undefined1 auVar35 [16];
  undefined1 auVar36 [16];
  undefined1 auVar37 [16];
  undefined1 local_e8 [16];
  undefined1 local_d8 [16];
  undefined8 local_b8;
  undefined8 uStack_b0;
  undefined1 local_a8 [16];
  undefined1 local_98 [16];
  undefined1 local_88 [16];
  undefined1 local_78 [16];
  undefined1 local_68 [16];
  undefined1 local_58 [16];
  undefined8 local_48;
  undefined8 uStack_40;
  long local_38;
  undefined1 extraout_var [56];
  
  local_38 = *DAT_01a1f100;
  uVar15 = param_1[0xb];
  if ((*(uint *)(&DAT_0267fe58 + (ulong)(uVar15 >> 5 & 0xff) * 4) >> (uVar15 & 0x1f) & 1) != 0) {
    iVar12 = FUN_00071f60();
    if (iVar12 != -1) {
      uVar13 = (int)*param_1 >> 0xd;
      uVar16 = (ulong)((uVar15 & 0x1fff) * DAT_02692230);
      lVar2 = *(long *)(param_1 + 2);
      lVar3 = *DAT_01a238a0;
      lVar17 = (ulong)((uVar13 >> 0x12 | 0x3ff) & uVar13) * 0x40;
      lVar4 = *(long *)(lVar3 + 0x10 + lVar17);
      iVar12 = *(int *)(lVar3 + 0x34 + lVar17);
      uVar20 = (ulong)((*param_1 & 0x1fff) * *(int *)(lVar3 + 0x30 + lVar17));
      uVar5 = *(ulong *)(lVar4 + 8 + uVar20);
      puVar1 = (undefined8 *)(uVar16 + 0xd0 + DAT_02692228);
      local_b8 = *puVar1;
      uStack_b0 = puVar1[1];
      auVar6 = vandps_avx(_DAT_01ac62f0,*(undefined1 (*) [16])(param_1 + 0x310));
      auVar24 = vandnps_avx(_DAT_01ac62f0,*(undefined1 (*) [16])(uVar16 + 0xe0 + DAT_02692228));
      local_a8 = vorps_avx(auVar24,auVar6);
      uVar13 = param_1[0x181];
      if (uVar13 != 0xffffffff) {
        lVar18 = (ulong)(((uint)((int)uVar13 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar13 >> 0xd) * 0x40;
        lVar3 = *DAT_01a238a0;
        lVar17 = *(long *)(lVar3 + 0x10 + lVar18);
        uVar16 = (ulong)((uVar13 & 0x1fff) * *(int *)(lVar3 + 0x30 + lVar18));
        FUN_004cf750((lVar17 + uVar16) -
                     ((long)*(int *)(lVar3 + 0x34 + lVar18) & *(ulong *)(lVar17 + 8 + uVar16)),
                     local_e8);
        auVar6._8_8_ = uStack_b0;
        auVar6._0_8_ = local_b8;
        auVar24 = vpand_avx(auVar6,_DAT_01643340);
        auVar22 = vpshufd_avx(auVar24,0);
        auVar6 = vpshufd_avx(auVar6,0xff);
        fVar21 = auVar6._0_4_;
        auVar37._0_4_ = fVar21 * fVar21;
        fVar26 = auVar6._4_4_;
        auVar37._4_4_ = fVar26 * fVar26;
        fVar27 = auVar6._8_4_;
        auVar37._8_4_ = fVar27 * fVar27;
        fVar28 = auVar6._12_4_;
        auVar37._12_4_ = fVar28 * fVar28;
        auVar29 = vsubps_avx(auVar37,_DAT_01ac63c0);
        auVar6 = vpshufd_avx(auVar24,1);
        auVar23 = vpshufd_avx(auVar24,0xb);
        auVar6 = vinsertps_avx(auVar23,ZEXT416((uint)(0.0 - auVar6._0_4_)),0x20);
        auVar6 = vblendps_avx(auVar6,auVar24,8);
        fVar21 = auVar24._0_4_ * auVar22._0_4_ + auVar29._0_4_ + fVar21 * auVar6._0_4_;
        fVar26 = auVar24._4_4_ * auVar22._4_4_ + 0.0 + fVar26 * auVar6._4_4_;
        fVar27 = auVar24._8_4_ * auVar22._8_4_ + 0.0 + fVar27 * auVar6._8_4_;
        fVar28 = auVar24._12_4_ * auVar22._12_4_ + 0.0 + fVar28 * auVar6._12_4_;
        local_88._0_4_ = fVar21 + fVar21;
        local_88._4_4_ = fVar26 + fVar26;
        local_88._8_4_ = fVar27 + fVar27;
        local_88._12_4_ = fVar28 + fVar28;
        auVar6 = vpshufd_avx(local_88,0xc9);
        auVar24 = vpshufd_avx(local_d8,0xd2);
        auVar32._0_4_ = auVar24._0_4_ * auVar6._0_4_;
        auVar32._4_4_ = auVar24._4_4_ * auVar6._4_4_;
        auVar32._8_4_ = auVar24._8_4_ * auVar6._8_4_;
        auVar32._12_4_ = auVar24._12_4_ * auVar6._12_4_;
        auVar6 = vpshufd_avx(local_88,0xd2);
        auVar22 = vpshufd_avx(local_d8,0xc9);
        auVar30._0_4_ = auVar22._0_4_ * auVar6._0_4_;
        auVar30._4_4_ = auVar22._4_4_ * auVar6._4_4_;
        auVar30._8_4_ = auVar22._8_4_ * auVar6._8_4_;
        auVar30._12_4_ = auVar22._12_4_ * auVar6._12_4_;
        auVar23 = vsubps_avx(auVar30,auVar32);
        auVar6 = vpshufd_avx(auVar23,0xd2);
        auVar29._0_4_ = auVar22._0_4_ * auVar6._0_4_;
        auVar29._4_4_ = auVar22._4_4_ * auVar6._4_4_;
        auVar29._8_4_ = auVar22._8_4_ * auVar6._8_4_;
        auVar29._12_4_ = auVar22._12_4_ * auVar6._12_4_;
        auVar6 = vpshufd_avx(auVar23,0xc9);
        auVar22._0_4_ = auVar24._0_4_ * auVar6._0_4_;
        auVar22._4_4_ = auVar24._4_4_ * auVar6._4_4_;
        auVar22._8_4_ = auVar24._8_4_ * auVar6._8_4_;
        auVar22._12_4_ = auVar24._12_4_ * auVar6._12_4_;
        local_98 = vsubps_avx(auVar22,auVar29);
        auVar25._0_8_ = FUN_00099f80(local_98,local_88);
        auVar25._8_56_ = extraout_var;
        local_88 = auVar25._0_16_;
        auVar6 = vpshufd_avx(local_88,0xc9);
        auVar24 = vpshufd_avx(local_d8,0xd2);
        auVar33._0_4_ = auVar6._0_4_ * auVar24._0_4_;
        auVar33._4_4_ = auVar6._4_4_ * auVar24._4_4_;
        auVar33._8_4_ = auVar6._8_4_ * auVar24._8_4_;
        auVar33._12_4_ = auVar6._12_4_ * auVar24._12_4_;
        auVar6 = vpshufd_avx(local_88,0xd2);
        auVar24 = vpshufd_avx(local_d8,0xc9);
        auVar23._0_4_ = auVar6._0_4_ * auVar24._0_4_;
        auVar23._4_4_ = auVar6._4_4_ * auVar24._4_4_;
        auVar23._8_4_ = auVar6._8_4_ * auVar24._8_4_;
        auVar23._12_4_ = auVar6._12_4_ * auVar24._12_4_;
        auVar6 = vsubps_avx(auVar23,auVar33);
        fVar21 = auVar6._0_4_;
        auVar34._0_4_ = fVar21 * fVar21;
        fVar27 = auVar6._4_4_;
        auVar34._4_4_ = fVar27 * fVar27;
        fVar7 = auVar6._8_4_;
        auVar34._8_4_ = fVar7 * fVar7;
        fVar9 = auVar6._12_4_;
        auVar34._12_4_ = fVar9 * fVar9;
        auVar6 = vpshufd_avx(auVar34,0x55);
        auVar24 = vpshufd_avx(auVar34,0);
        auVar22 = vpshufd_avx(auVar34,0xaa);
        auVar35._0_4_ = auVar22._0_4_ + auVar24._0_4_ + auVar6._0_4_;
        auVar35._4_4_ = auVar22._4_4_ + auVar24._4_4_ + auVar6._4_4_;
        auVar35._8_4_ = auVar22._8_4_ + auVar24._8_4_ + auVar6._8_4_;
        auVar35._12_4_ = auVar22._12_4_ + auVar24._12_4_ + auVar6._12_4_;
        local_58 = local_d8;
        auVar22 = vrsqrtps_avx(auVar35);
        fVar26 = auVar22._0_4_;
        fVar28 = auVar22._4_4_;
        fVar8 = auVar22._8_4_;
        fVar10 = auVar22._12_4_;
        auVar36._0_4_ = fVar26 * fVar26 * auVar35._0_4_ * (float)DAT_01643350;
        auVar36._4_4_ = fVar28 * fVar28 * auVar35._4_4_ * DAT_01643350._4_4_;
        auVar36._8_4_ = fVar8 * fVar8 * auVar35._8_4_ * DAT_01643350._8_4_;
        auVar36._12_4_ = fVar10 * fVar10 * auVar35._12_4_ * DAT_01643350._12_4_;
        auVar6 = vsubps_avx(_DAT_01643350,auVar36);
        auVar31._0_4_ = fVar26 + fVar26 * auVar6._0_4_;
        auVar31._4_4_ = fVar28 + fVar28 * auVar6._4_4_;
        auVar31._8_4_ = fVar8 + fVar8 * auVar6._8_4_;
        auVar31._12_4_ = fVar10 + fVar10 * auVar6._12_4_;
        auVar24 = vcmpps_avx(auVar31,auVar31,0);
        auVar6 = vandps_avx(auVar24,auVar31);
        auVar24 = vandnps_avx(auVar24,auVar22);
        auVar6 = vorps_avx(auVar24,auVar6);
        auVar24._0_4_ = fVar21 * auVar6._0_4_;
        auVar24._4_4_ = fVar27 * auVar6._4_4_;
        auVar24._8_4_ = fVar7 * auVar6._8_4_;
        auVar24._12_4_ = fVar9 * auVar6._12_4_;
        auVar6 = vcmpps_avx(auVar6,_DAT_01643370,0);
        local_68 = vandnps_avx(auVar6,auVar24);
        local_48 = _DAT_01643360;
        uStack_40 = uRam0000000001643368;
        local_78 = local_88;
        local_b8 = FUN_00095770(local_78);
        uStack_b0 = extraout_XMM0_Qb;
      }
      uVar13 = FUN_00071f60(param_1 + 0x2fd);
      uVar14 = 0xffffffff;
      if (uVar13 != 0xffffffff) {
        lVar18 = (ulong)(((uint)((int)uVar13 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar13 >> 0xd) * 0x40;
        lVar3 = *DAT_01a238a0;
        lVar17 = *(long *)(lVar3 + 0x10 + lVar18);
        uVar16 = (ulong)((uVar13 & 0x1fff) * *(int *)(lVar3 + 0x30 + lVar18));
        if (lVar17 + uVar16 !=
            ((long)*(int *)(lVar3 + 0x34 + lVar18) & *(ulong *)(lVar17 + 8 + uVar16))) {
          uVar14 = FUN_00742010();
        }
      }
      lVar19 = (ulong)(((uint)((int)uVar14 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar14 >> 0xd) * 0x40;
      lVar3 = *DAT_01a238a0;
      lVar18 = 0;
      lVar17 = *(long *)(lVar3 + 0x10 + lVar19);
      uVar16 = (ulong)((uVar14 & 0x1fff) * *(int *)(lVar3 + 0x30 + lVar19));
      lVar17 = (lVar17 + uVar16) -
               ((long)*(int *)(lVar3 + 0x34 + lVar19) & *(ulong *)(lVar17 + 8 + uVar16));
      lVar3 = *(long *)(lVar17 + 8);
      if (lVar3 != 0) {
        lVar18 = lVar17 + 8 + lVar3;
      }
      cVar11 = FUN_00233fb0(DAT_01643440,lVar18,&local_b8,uVar15,2,param_1 + 0x310);
      if (cVar11 == '\0') {
        *(undefined1 *)(param_1 + 0x30c) = 5;
      }
      else {
        auVar6 = vandps_avx(_DAT_01ac62f0,*(undefined1 (*) [16])(param_1 + 0x310));
        auVar24 = vandnps_avx(_DAT_01ac62f0,local_a8);
        local_a8 = vorps_avx(auVar24,auVar6);
        lVar3 = *DAT_01a238a0;
        uVar13 = (int)param_1[0x2fe] >> 0xd;
        lVar18 = (ulong)((uVar13 >> 0x12 | 0x3ff) & uVar13) * 0x40;
        lVar17 = *(long *)(lVar3 + 0x10 + lVar18);
        uVar16 = (ulong)((param_1[0x2fe] & 0x1fff) * *(int *)(lVar3 + 0x30 + lVar18));
        FUN_007420f0((lVar17 + uVar16) -
                     ((long)*(int *)(lVar3 + 0x34 + lVar18) & *(ulong *)(lVar17 + 8 + uVar16)),
                     &local_b8,lVar2 + 0x558 + ((lVar4 + uVar20) - ((long)iVar12 & uVar5)));
        uVar15 = FUN_00913fa0(uVar15);
        if (uVar15 != 0xffffffff) {
          FUN_00abac60(*(undefined4 *)
                        (*(long *)(DAT_0273ea80 + 8) + 0x630 + (ulong)(uVar15 & 0xffff) * 0x2af0));
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

