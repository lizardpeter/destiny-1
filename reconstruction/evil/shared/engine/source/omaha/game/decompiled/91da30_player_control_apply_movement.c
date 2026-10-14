
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0091da30(uint param_1,char param_2,float *param_3,float *param_4,long param_5,int *param_6,
                 float *param_7)

{
  int *piVar1;
  float fVar2;
  undefined1 auVar3 [16];
  uint uVar4;
  undefined4 uVar5;
  int iVar6;
  uint uVar7;
  ulong uVar8;
  ulong uVar9;
  long lVar10;
  long lVar11;
  long lVar12;
  long lVar13;
  long lVar14;
  float fVar15;
  float fVar16;
  float fVar17;
  undefined1 auVar18 [16];
  undefined1 auVar19 [16];
  undefined1 auVar20 [16];
  undefined1 auVar21 [16];
  undefined1 auVar22 [16];
  undefined1 auVar23 [16];
  undefined1 auVar24 [16];
  undefined1 local_d8 [16];
  float local_c8;
  float fStack_c4;
  float fStack_c0;
  float fStack_bc;
  undefined1 local_b8 [16];
  long local_a8;
  long local_a0;
  uint local_98;
  undefined4 uStack_94;
  long local_90;
  undefined4 local_88;
  undefined1 local_80;
  undefined1 local_48 [8];
  undefined1 local_40 [8];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  *param_7 = *(float *)(param_5 + 0x2c0);
  param_7[1] = *(float *)(param_5 + 0x2c4);
  fVar17 = DAT_0166b6f0;
  if ((param_1 != 0xffffffff) &&
     (uVar4 = *(uint *)(*(long *)(DAT_0273ea80 + 8) + 0x2708 + (ulong)(param_1 & 0xffff) * 0x2af0),
     uVar4 != 0xffffffff)) {
    lVar10 = (ulong)(((uint)((int)uVar4 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar4 >> 0xd) * 0x40;
    lVar11 = *DAT_01a238a0;
    lVar14 = *(long *)(lVar11 + 0x10 + lVar10);
    uVar8 = (ulong)((uVar4 & 0x1fff) * *(int *)(lVar11 + 0x30 + lVar10));
    fVar17 = (float)FUN_00740990((lVar14 + uVar8) -
                                 ((long)*(int *)(lVar11 + 0x34 + lVar10) &
                                 *(ulong *)(lVar14 + 8 + uVar8)));
  }
  piVar1 = param_6 + 0x30;
  FUN_000ab210(piVar1,local_48);
  FUN_000ab260(local_48,param_7,local_40);
  FUN_000ab1b0(fVar17,local_40,local_40);
  FUN_000ab260(piVar1,local_40,param_7);
  FUN_000aa760(*param_7,param_7[1],piVar1);
  if (param_2 != '\0') {
    fVar17 = *param_7 - *param_3;
    if (((fVar17 <= DAT_0166b6f4) || (fVar15 = DAT_0166b6f0, fVar17 < DAT_0166b6f0)) &&
       (fVar15 = DAT_0166b6f4, DAT_0166b6f4 < fVar17)) {
      fVar15 = fVar17;
    }
    *param_7 = fVar15;
    fVar17 = param_7[1] + param_3[1];
    if (((fVar17 <= DAT_0166b6f4) || (fVar15 = DAT_0166b6f0, fVar17 < DAT_0166b6f0)) &&
       (fVar15 = DAT_0166b6f4, DAT_0166b6f4 < fVar17)) {
      fVar15 = fVar17;
    }
    param_7[1] = fVar15;
  }
  if (*param_6 != -1) {
    FUN_004cbcc0(*param_6,&local_a8);
    if ((uint)local_a0 != 0xffffffff) {
      uVar8 = (ulong)(((uint)local_a8 & 0x1fff) * DAT_02689800);
      lVar13 = (ulong)(((uint)((int)(uint)local_a0 >> 0xd) >> 0x12 | 0x3ff) &
                      (int)(uint)local_a0 >> 0xd) * 0x40;
      lVar11 = *DAT_01a238a0;
      lVar10 = CONCAT44(uStack_94,local_98);
      lVar14 = *(long *)(lVar11 + 0x10 + lVar13);
      uVar9 = (ulong)(((uint)local_a0 & 0x1fff) * *(int *)(lVar11 + 0x30 + lVar13));
      lVar11 = (lVar14 + uVar9) -
               ((long)*(int *)(lVar11 + 0x34 + lVar13) & *(ulong *)(lVar14 + 8 + uVar9));
      fVar17 = *(float *)(lVar10 + 0x188 + lVar11);
      if (0.0 < fVar17) {
        lVar14 = (DAT_026897f8 + uVar8) -
                 ((long)DAT_02689818 & *(ulong *)(DAT_026897f8 + 8 + uVar8));
        auVar3 = vpshufd_avx(ZEXT416((uint)fVar17),0);
        uVar4 = FUN_006ed8f0(*param_6);
        uVar5 = FUN_00337e80((ulong)((uVar4 & 0x1fff) * DAT_02692230) + DAT_02692228);
        FUN_00328ad0(uVar5,&local_c8,local_d8);
        auVar22 = vsubps_avx((undefined1  [16])0x0,auVar3);
        auVar19 = vcmpps_avx((undefined1  [16])0x0,(undefined1  [16])0x0,0);
        auVar24._0_4_ = auVar22._0_4_ * DAT_01ac6380;
        auVar24._4_4_ = auVar22._4_4_ * fRam0000000001ac6384;
        auVar24._8_4_ = auVar22._8_4_ * fRam0000000001ac6388;
        auVar24._12_4_ = auVar22._12_4_ * fRam0000000001ac638c;
        auVar22 = vmaxps_avx(auVar22,auVar24);
        auVar22 = vcmpps_avx(auVar22,_DAT_01ac6320,2);
        auVar18._0_4_ = auVar22._0_4_ ^ auVar19._0_4_;
        auVar18._4_4_ = auVar22._4_4_ ^ auVar19._4_4_;
        auVar18._8_4_ = auVar22._8_4_ ^ auVar19._8_4_;
        auVar18._12_4_ = auVar22._12_4_ ^ auVar19._12_4_;
        auVar19 = vcmpps_avx(auVar18,(undefined1  [16])0x0,0);
        iVar6 = vmovmskps_avx(auVar19);
        auVar19 = ZEXT816(0) << 0x20;
        if (iVar6 != 0xf) {
          auVar20._0_4_ = local_c8 * local_c8;
          auVar20._4_4_ = fStack_c4 * fStack_c4;
          auVar20._8_4_ = fStack_c0 * fStack_c0;
          auVar20._12_4_ = fStack_bc * fStack_bc;
          auVar19 = vpshufd_avx(auVar20,0x55);
          auVar22 = vpshufd_avx(auVar20,0);
          auVar18 = vpshufd_avx(auVar20,0xaa);
          auVar21._0_4_ = auVar18._0_4_ + auVar22._0_4_ + auVar19._0_4_;
          auVar21._4_4_ = auVar18._4_4_ + auVar22._4_4_ + auVar19._4_4_;
          auVar21._8_4_ = auVar18._8_4_ + auVar22._8_4_ + auVar19._8_4_;
          auVar21._12_4_ = auVar18._12_4_ + auVar22._12_4_ + auVar19._12_4_;
          auVar18 = vrsqrtps_avx(auVar21);
          fVar17 = auVar18._0_4_;
          fVar15 = auVar18._4_4_;
          fVar16 = auVar18._8_4_;
          fVar2 = auVar18._12_4_;
          auVar19._0_4_ = fVar17 * fVar17 * auVar21._0_4_ * (float)DAT_0166b5f0;
          auVar19._4_4_ = fVar15 * fVar15 * auVar21._4_4_ * DAT_0166b5f0._4_4_;
          auVar19._8_4_ = fVar16 * fVar16 * auVar21._8_4_ * DAT_0166b5f0._8_4_;
          auVar19._12_4_ = fVar2 * fVar2 * auVar21._12_4_ * DAT_0166b5f0._12_4_;
          auVar19 = vsubps_avx(_DAT_0166b5f0,auVar19);
          auVar23._0_4_ = fVar17 + fVar17 * auVar19._0_4_;
          auVar23._4_4_ = fVar15 + fVar15 * auVar19._4_4_;
          auVar23._8_4_ = fVar16 + fVar16 * auVar19._8_4_;
          auVar23._12_4_ = fVar2 + fVar2 * auVar19._12_4_;
          auVar22 = vcmpps_avx(auVar23,auVar23,0);
          auVar19 = vandps_avx(auVar22,auVar23);
          auVar22 = vandnps_avx(auVar22,auVar18);
          auVar19 = vorps_avx(auVar22,auVar19);
          auVar22._0_4_ = auVar21._0_4_ * auVar19._0_4_;
          auVar22._4_4_ = auVar21._4_4_ * auVar19._4_4_;
          auVar22._8_4_ = auVar21._8_4_ * auVar19._8_4_;
          auVar22._12_4_ = auVar21._12_4_ * auVar19._12_4_;
          auVar19 = vcmpps_avx(auVar19,_DAT_0166b600,0);
          auVar19 = vandnps_avx(auVar19,auVar22);
          auVar19 = vdivps_avx(auVar19,auVar3);
        }
        auVar19 = vmaxps_avx(auVar19,(undefined1  [16])0x0);
        local_b8 = vminps_avx(auVar19,_DAT_0166b610);
        fVar15 = (float)FUN_002fb3b0(lVar14,lVar10 + 400 + lVar11,local_b8);
        fVar16 = (float)FUN_002fb3b0(lVar14,lVar10 + 0x1d0 + lVar11,local_b8);
        fVar17 = DAT_0166b6f8;
        if ((*(byte *)(lVar10 + 5 + lVar11) & 8) == 0) {
          *param_4 = fVar15 * *param_4;
          fVar17 = param_4[1];
        }
        else {
          *param_4 = fVar15 * DAT_0166b6f8;
        }
        param_4[1] = fVar16 * fVar17;
      }
    }
    uVar4 = *(uint *)(*(long *)(DAT_0273ea80 + 8) + 0x2708 + (ulong)(param_1 & 0xffff) * 0x2af0);
    fVar17 = DAT_0166b6f0;
    if (uVar4 != 0xffffffff) {
      lVar10 = (ulong)(((uint)((int)uVar4 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar4 >> 0xd) * 0x40;
      lVar11 = *DAT_01a238a0;
      lVar14 = *(long *)(lVar11 + 0x10 + lVar10);
      uVar8 = (ulong)((uVar4 & 0x1fff) * *(int *)(lVar11 + 0x30 + lVar10));
      lVar11 = (lVar14 + uVar8) -
               ((long)*(int *)(lVar11 + 0x34 + lVar10) & *(ulong *)(lVar14 + 8 + uVar8));
      uVar4 = (uint)*(undefined8 *)(lVar11 + 0x100);
      if (uVar4 != 0xffffffff) {
        local_90 = *(long *)(lVar11 + 0x108);
        uVar7 = (int)*(uint *)(lVar11 + 0xf8) >> 0xd;
        local_88 = *(undefined4 *)(lVar11 + 0x110);
        local_80 = 0;
        lVar13 = (ulong)((uVar7 >> 0x12 | 0x3ff) & uVar7) * 0x40;
        lVar14 = *DAT_01a238a0;
        lVar12 = (ulong)(((uint)((int)uVar4 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar4 >> 0xd) * 0x40;
        lVar10 = *(long *)(lVar14 + 0x10 + lVar13);
        uVar8 = (ulong)((*(uint *)(lVar11 + 0xf8) & 0x1fff) * *(int *)(lVar14 + 0x30 + lVar13));
        local_a8 = (lVar10 + uVar8) -
                   ((long)*(int *)(lVar14 + 0x34 + lVar13) & *(ulong *)(lVar10 + 8 + uVar8));
        lVar10 = *(long *)(lVar14 + 0x10 + lVar12);
        uVar8 = (ulong)((uVar4 & 0x1fff) * *(int *)(lVar14 + 0x30 + lVar12));
        local_a0 = ((lVar10 + uVar8) -
                   ((long)*(int *)(lVar14 + 0x34 + lVar12) & *(ulong *)(lVar10 + 8 + uVar8))) +
                   local_90;
        uStack_94 = (undefined4)((ulong)*(undefined8 *)(lVar11 + 0x100) >> 0x20);
        local_98 = uVar4;
        fVar17 = (float)FUN_00353e40(&local_a8);
      }
    }
    param_4[1] = fVar17 * param_4[1];
    *param_4 = fVar17 * *param_4;
  }
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

