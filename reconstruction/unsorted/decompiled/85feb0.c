
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int FUN_0085feb0(uint *param_1,long param_2,long param_3,undefined8 param_4,char param_5)

{
  long *plVar1;
  undefined8 *puVar2;
  int iVar3;
  long lVar4;
  undefined8 uVar5;
  long lVar6;
  long lVar7;
  undefined1 auVar8 [12];
  short sVar9;
  undefined1 auVar10 [16];
  char cVar11;
  char cVar12;
  long lVar13;
  float *pfVar14;
  undefined8 uVar15;
  ulong uVar16;
  long lVar17;
  uint uVar18;
  long lVar19;
  long lVar20;
  long lVar21;
  ulong uVar22;
  long lVar23;
  undefined1 auVar24 [16];
  undefined1 auVar25 [16];
  undefined1 auVar26 [16];
  undefined1 auVar27 [16];
  undefined1 auVar28 [16];
  undefined1 auVar29 [16];
  undefined1 auVar30 [16];
  undefined1 auVar31 [16];
  undefined1 auVar32 [16];
  undefined1 auVar33 [16];
  undefined1 auVar34 [16];
  undefined1 auVar35 [16];
  undefined1 auVar36 [16];
  undefined1 auVar37 [16];
  undefined1 auVar38 [16];
  float fVar39;
  float fVar40;
  float fVar41;
  float fVar42;
  undefined1 auVar43 [16];
  undefined1 auVar44 [16];
  
  if (param_5 != '\0') {
    *(undefined2 *)(param_2 + 0x15d5) = 0x8482;
  }
  uVar18 = (int)param_1[10] >> 0xd;
  lVar4 = *(long *)(param_3 + 0x7c8);
  lVar21 = *DAT_01a238a0;
  lVar13 = (ulong)((uVar18 >> 0x12 | 0x3ff) & uVar18) * 0x40;
  lVar20 = *(long *)(lVar21 + 0x10 + lVar13);
  iVar3 = *(int *)(lVar21 + 0x34 + lVar13);
  uVar22 = (ulong)((param_1[10] & 0x1fff) * *(int *)(lVar21 + 0x30 + lVar13));
  uVar16 = *(ulong *)(lVar20 + 8 + uVar22);
  pfVar14 = (float *)FUN_0082b940(param_2,8,0x80);
  uVar5 = *(undefined8 *)(param_2 + 0x15c0);
  uVar15 = FUN_0082e420(0x10);
  FUN_007deb70(uVar5,uVar15,0);
  lVar13 = (lVar20 + uVar22) - ((long)iVar3 & uVar16);
  lVar21 = *DAT_01a238a0;
  uVar18 = (int)*param_1 >> 0xd;
  lVar20 = (ulong)((uVar18 >> 0x12 | 0x3ff) & uVar18) * 0x40;
  uVar16 = (ulong)((*param_1 & 0x1fff) * *(int *)(lVar21 + 0x30 + lVar20));
  if (*(long *)(lVar13 + 8) < 1) {
    sVar9 = 0;
  }
  else {
    lVar23 = *(long *)(lVar21 + 0x10 + lVar20);
    lVar21 = (lVar23 + uVar16) -
             ((long)*(int *)(lVar21 + 0x34 + lVar20) & *(ulong *)(lVar23 + 8 + uVar16));
    plVar1 = (long *)(lVar13 + 0x10);
    sVar9 = 0;
    lVar20 = 0;
    lVar23 = 0x60;
    do {
      auVar10 = _DAT_01664cd0;
      auVar31 = _DAT_01664cc0;
      if ((*(byte *)(lVar21 + 2 + lVar20 * 4) &
          ~*(byte *)(lVar4 + (ulong)*(ushort *)(lVar21 + lVar20 * 4))) == 0) {
        lVar6 = *plVar1;
        auVar35 = *(undefined1 (*) [16])((long)plVar1 + lVar23 + -0x40 + lVar6);
        auVar29 = *(undefined1 (*) [16])((long)plVar1 + lVar23 + -0x30 + lVar6);
        fVar39 = auVar35._0_4_;
        auVar24._0_4_ = fVar39 * fVar39;
        fVar40 = auVar35._4_4_;
        auVar24._4_4_ = fVar40 * fVar40;
        fVar41 = auVar35._8_4_;
        auVar24._8_4_ = fVar41 * fVar41;
        fVar42 = auVar35._12_4_;
        auVar24._12_4_ = fVar42 * fVar42;
        auVar27 = vpshufd_avx(auVar24,0x4e);
        auVar25._0_4_ = auVar24._0_4_ + auVar27._0_4_;
        auVar25._4_4_ = auVar24._4_4_ + auVar27._4_4_;
        auVar25._8_4_ = auVar24._8_4_ + auVar27._8_4_;
        auVar25._12_4_ = auVar24._12_4_ + auVar27._12_4_;
        auVar27 = vpshufd_avx(auVar25,0x93);
        auVar26._0_4_ = auVar25._0_4_ + auVar27._0_4_;
        auVar26._4_4_ = auVar25._4_4_ + auVar27._4_4_;
        auVar26._8_4_ = auVar25._8_4_ + auVar27._8_4_;
        auVar26._12_4_ = auVar25._12_4_ + auVar27._12_4_;
        auVar24 = vdivps_avx(_DAT_01664ca0,auVar26);
        auVar27 = vcmpps_avx(_DAT_01ac6320,auVar26,1);
        auVar36._0_4_ = auVar24._0_4_ * DAT_01ac63d0;
        auVar36._4_4_ = auVar24._4_4_ * fRam0000000001ac63d4;
        auVar36._8_4_ = auVar24._8_4_ * fRam0000000001ac63d8;
        auVar36._12_4_ = auVar24._12_4_ * fRam0000000001ac63dc;
        auVar24 = vpshufd_avx(auVar35,0x25);
        auVar25 = vpshufd_avx(auVar35,0xff);
        auVar26 = vpshufd_avx(auVar35,0);
        auVar24 = vpand_avx(auVar24,_DAT_01664cb0);
        auVar28 = vpshufd_avx(auVar29,0xff);
        auVar29 = vpand_avx(auVar29,_DAT_01664cb0);
        auVar35 = vandps_avx(auVar27,auVar36);
        auVar30._0_4_ = fVar39 * auVar35._0_4_;
        auVar30._4_4_ = fVar40 * auVar35._4_4_;
        auVar30._8_4_ = fVar41 * auVar35._8_4_;
        auVar30._12_4_ = fVar42 * auVar35._12_4_;
        auVar27._0_4_ = auVar26._0_4_ * auVar30._0_4_;
        auVar27._4_4_ = auVar26._4_4_ * auVar30._4_4_;
        auVar27._8_4_ = auVar26._8_4_ * auVar30._8_4_;
        auVar27._12_4_ = auVar26._12_4_ * auVar30._12_4_;
        auVar35 = vpshufd_avx(auVar27,0);
        auVar27 = vpshufd_avx(auVar27,9);
        auVar37._0_4_ = auVar25._0_4_ * auVar30._0_4_;
        auVar37._4_4_ = auVar25._4_4_ * auVar30._4_4_;
        auVar37._8_4_ = auVar25._8_4_ * auVar30._8_4_;
        auVar37._12_4_ = auVar25._12_4_ * auVar30._12_4_;
        auVar25 = vpshufd_avx(auVar37,6);
        auVar8 = ZEXT812(0) << 0x20;
        auVar36 = ZEXT816(0) << 0x40;
        auVar25 = vshufps_avx(auVar25,auVar36,4);
        auVar26 = vshufps_avx(auVar27,auVar36,4);
        auVar34 = vshufps_avx(auVar35,auVar36,4);
        auVar35 = vpshufd_avx(auVar30,0x29);
        auVar35 = vpand_avx(auVar35,_DAT_01664cb0);
        auVar33._0_4_ = auVar24._0_4_ * auVar35._0_4_;
        auVar33._4_4_ = auVar24._4_4_ * auVar35._4_4_;
        auVar33._8_4_ = auVar24._8_4_ * auVar35._8_4_;
        auVar33._12_4_ = auVar24._12_4_ * auVar35._12_4_;
        auVar35 = vpshufd_avx(auVar33,8);
        auVar35 = vpand_avx(auVar35,_DAT_01664cb0);
        auVar43._0_4_ = auVar26._0_4_ + auVar25._0_4_;
        auVar43._4_4_ = auVar26._4_4_ + auVar25._4_4_;
        auVar43._8_4_ = auVar26._8_4_ + auVar25._8_4_;
        auVar43._12_4_ = auVar26._12_4_ + auVar25._12_4_;
        auVar27 = vpshufd_avx(auVar43,0);
        auVar27 = vpand_avx(auVar27,_DAT_01664cc0);
        auVar24 = vpor_avx(auVar27,ZEXT416(0x3f800000));
        auVar25 = vsubps_avx(auVar26,auVar25);
        auVar27 = vpshufd_avx(auVar25,0x10);
        auVar27 = vpand_avx(auVar27,_DAT_01664cd0);
        auVar44._0_4_ = auVar27._0_4_ + auVar24._0_4_;
        auVar44._4_4_ = auVar27._4_4_ + auVar24._4_4_;
        auVar44._8_4_ = auVar27._8_4_ + auVar24._8_4_;
        auVar44._12_4_ = auVar27._12_4_ + auVar24._12_4_;
        auVar27 = vpand_avx(auVar33,_DAT_01664cd0);
        auVar32._0_4_ = auVar27._0_4_ + auVar34._0_4_ + auVar35._0_4_;
        auVar32._4_4_ = auVar27._4_4_ + auVar34._4_4_ + auVar35._4_4_;
        auVar32._8_4_ = auVar27._8_4_ + auVar34._8_4_ + auVar35._8_4_;
        auVar32._12_4_ = auVar27._12_4_ + auVar34._12_4_ + auVar35._12_4_;
        auVar35 = vpshufd_avx(auVar37,0);
        auVar27 = vpandn_avx(_DAT_01ac6290,auVar35);
        auVar35 = vsubps_avx(auVar36,auVar35);
        auVar35 = vpand_avx(_DAT_01ac6290,auVar35);
        auVar24 = vpshufd_avx(auVar32,2);
        auVar38._0_4_ = auVar24._0_4_;
        auVar38._4_12_ = auVar8;
        auVar24 = vsubps_avx(auVar44,auVar38);
        auVar35 = vpor_avx(auVar27,auVar35);
        auVar27 = vpshufd_avx(auVar33,0x55);
        auVar34._0_4_ = auVar27._0_4_ + auVar35._0_4_;
        auVar34._4_4_ = auVar27._4_4_ + auVar35._4_4_;
        auVar34._8_4_ = auVar27._8_4_ + auVar35._8_4_;
        auVar34._12_4_ = auVar27._12_4_ + auVar35._12_4_;
        auVar27 = vpor_avx(auVar29,_DAT_01664ce0);
        fVar39 = auVar28._0_4_;
        fVar40 = auVar28._4_4_;
        fVar41 = auVar28._8_4_;
        fVar42 = auVar28._12_4_;
        *pfVar14 = fVar39 * auVar24._0_4_;
        pfVar14[1] = fVar40 * auVar24._4_4_;
        pfVar14[2] = fVar41 * auVar24._8_4_;
        pfVar14[3] = fVar42 * auVar24._12_4_;
        auVar35 = vpshufd_avx(auVar34,0);
        auVar29 = vpand_avx(auVar35,auVar10);
        auVar35._0_4_ = auVar25._0_4_;
        auVar35._4_12_ = auVar8;
        auVar35 = vorps_avx(auVar35,_DAT_01664cf0);
        auVar28._0_4_ = auVar35._0_4_ + auVar29._0_4_;
        auVar28._4_4_ = auVar35._4_4_ + auVar29._4_4_;
        auVar28._8_4_ = auVar35._8_4_ + auVar29._8_4_;
        auVar28._12_4_ = auVar35._12_4_ + auVar29._12_4_;
        auVar35 = vpand_avx(auVar32,auVar31);
        auVar29 = vsubps_avx(auVar28,auVar35);
        auVar35 = vpand_avx(auVar34,auVar31);
        auVar31 = vpshufd_avx(auVar43,1);
        auVar31._4_12_ = auVar8;
        pfVar14[4] = fVar39 * auVar29._0_4_;
        pfVar14[5] = fVar40 * auVar29._4_4_;
        pfVar14[6] = fVar41 * auVar29._8_4_;
        pfVar14[7] = fVar42 * auVar29._12_4_;
        auVar31 = vorps_avx(auVar31,_DAT_01664d00);
        auVar29._0_4_ = auVar31._0_4_ + auVar35._0_4_;
        auVar29._4_4_ = auVar31._4_4_ + auVar35._4_4_;
        auVar29._8_4_ = auVar31._8_4_ + auVar35._8_4_;
        auVar29._12_4_ = auVar31._12_4_ + auVar35._12_4_;
        auVar31 = vpshufd_avx(auVar32,0);
        auVar31 = vpand_avx(auVar31,auVar10);
        auVar31 = vsubps_avx(auVar29,auVar31);
        pfVar14[8] = fVar39 * auVar31._0_4_;
        pfVar14[9] = fVar40 * auVar31._4_4_;
        pfVar14[10] = fVar41 * auVar31._8_4_;
        pfVar14[0xb] = fVar42 * auVar31._12_4_;
        *(undefined1 (*) [16])(pfVar14 + 0xc) = auVar27;
        puVar2 = (undefined8 *)((long)plVar1 + lVar23 + -0x20 + lVar6);
        uVar5 = puVar2[1];
        *(undefined8 *)(pfVar14 + 0x10) = *puVar2;
        *(undefined8 *)(pfVar14 + 0x12) = uVar5;
        puVar2 = (undefined8 *)((long)plVar1 + lVar23 + -0x10 + lVar6);
        uVar5 = puVar2[1];
        *(undefined8 *)(pfVar14 + 0x14) = *puVar2;
        *(undefined8 *)(pfVar14 + 0x16) = uVar5;
        puVar2 = (undefined8 *)((long)plVar1 + lVar23 + lVar6);
        uVar5 = puVar2[1];
        *(undefined8 *)(pfVar14 + 0x18) = *puVar2;
        *(undefined8 *)(pfVar14 + 0x1a) = uVar5;
        lVar17 = FUN_0082cb90(2);
        if (lVar17 != 0) {
          cVar11 = FUN_0081fd20(param_2,lVar17,*(undefined8 *)(param_2 + 0x15c0));
          if (cVar11 == '\0') {
            cVar12 = FUN_0082bd10(param_2,1,lVar17 + 0x20);
            cVar11 = '\0';
            if (cVar12 != '\0') {
              cVar11 = FUN_0082bd10(param_2,2,lVar17 + 0xb0);
            }
          }
          if (cVar11 != '\0') {
            *(byte *)(param_2 + 0x15ac) = *(byte *)(param_2 + 0x15ac) | 4;
            FUN_007dec20(*(undefined8 *)(param_2 + 0x15c0),
                         *(undefined4 *)((long)plVar1 + lVar23 + lVar6 + -0x48),0,0,0);
            FUN_007dee30(*(undefined8 *)(param_2 + 0x15c0),
                         *(undefined4 *)((long)plVar1 + lVar23 + lVar6 + -0x4c));
            lVar17 = 0;
            uVar18 = *(uint *)((long)plVar1 + lVar23 + lVar6 + -0x50);
            if (uVar18 != 0xffffffff) {
              lVar19 = (ulong)(((uint)((int)uVar18 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar18 >> 0xd) *
                       0x40;
              lVar17 = *DAT_01a238a0;
              lVar7 = *(long *)(lVar17 + 0x10 + lVar19);
              uVar16 = (ulong)((uVar18 & 0x1fff) * *(int *)(lVar17 + 0x30 + lVar19));
              lVar17 = (lVar7 + uVar16) -
                       ((long)*(int *)(lVar17 + 0x34 + lVar19) & *(ulong *)(lVar7 + 8 + uVar16));
            }
            cVar11 = FUN_0082b490(param_2,lVar17);
            if (cVar11 != '\0') {
              FUN_007e15d0(*(undefined8 *)(param_2 + 0x15c0),3,0,0,
                           *(int *)((long)plVar1 + lVar23 + lVar6 + -0x44) * 3,0,0,0);
              sVar9 = sVar9 + 1;
            }
          }
        }
      }
      lVar23 = lVar23 + 0x60;
      lVar20 = lVar20 + 1;
    } while (lVar20 < *(long *)(lVar13 + 8));
  }
  *(byte *)(param_2 + 0x15ac) = *(byte *)(param_2 + 0x15ac) & 0xfb;
  FUN_0082ba20(param_2,8,0x80);
  if (param_5 != '\0') {
    *(undefined2 *)(param_2 + 0x15d5) = 0;
  }
  return (int)sVar9;
}

