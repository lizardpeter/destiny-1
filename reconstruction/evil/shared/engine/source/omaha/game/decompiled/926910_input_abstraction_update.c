
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00926910(void)

{
  long lVar1;
  undefined1 (*pauVar2) [16];
  uint *puVar3;
  long lVar4;
  undefined8 uVar5;
  undefined8 uVar6;
  undefined *puVar7;
  undefined *puVar8;
  char cVar9;
  byte bVar10;
  undefined1 uVar11;
  undefined2 uVar12;
  int iVar13;
  uint uVar14;
  uint uVar15;
  long lVar16;
  long lVar17;
  long lVar18;
  long *plVar19;
  float *pfVar20;
  char cVar21;
  undefined4 *puVar22;
  ulong uVar23;
  undefined4 *puVar24;
  undefined4 *puVar25;
  char *pcVar26;
  short *psVar27;
  byte bVar28;
  uint uVar29;
  int *piVar30;
  int iVar31;
  undefined4 *puVar32;
  undefined1 (*pauVar33) [16];
  byte *pbVar34;
  long lVar35;
  long *plVar36;
  float *pfVar37;
  long lVar38;
  char cVar39;
  short sVar40;
  long lVar41;
  bool bVar42;
  bool bVar43;
  float fVar44;
  float fVar45;
  undefined4 uVar46;
  undefined4 uVar47;
  uint uVar48;
  undefined8 extraout_XMM0_Qa;
  undefined8 extraout_XMM0_Qb;
  undefined1 auVar49 [16];
  undefined1 auVar50 [16];
  undefined1 auVar51 [16];
  undefined1 auVar52 [16];
  undefined8 extraout_XMM0_Qb_00;
  undefined8 uVar57;
  undefined1 auVar53 [16];
  undefined1 auVar54 [16];
  undefined8 extraout_XMM0_Qa_00;
  undefined1 extraout_var [56];
  undefined1 extraout_var_00 [56];
  undefined1 extraout_var_01 [56];
  undefined1 auVar55 [64];
  undefined1 extraout_var_02 [56];
  float fVar58;
  uint uVar59;
  double dVar60;
  undefined1 auVar61 [16];
  double dVar62;
  double dVar63;
  double dVar64;
  short *local_c0;
  char *local_78;
  double local_58;
  double local_50;
  uint local_48;
  uint uStack_44;
  uint uStack_40;
  uint uStack_3c;
  long local_38;
  undefined1 auVar56 [12];
  
  local_38 = *DAT_01a1f100;
  cVar9 = FUN_00001f70();
  if (cVar9 != '\0') {
    FUN_00926600(0);
    FUN_00926600(1);
    FUN_00926600(2);
    FUN_00926600(3);
  }
  FUN_000ad120();
  puVar8 = PTR_DAT_019b3308;
  puVar7 = PTR_DAT_019b3300;
  puVar24 = &DAT_0273f184;
  puVar32 = &DAT_0273ed48;
  local_c0 = &DAT_0273f282;
  pfVar37 = (float *)&DAT_0273efe8;
  local_78 = &DAT_0273f242;
  uVar29 = 0;
  do {
    lVar35 = (long)(int)uVar29;
    iVar13 = 0x24;
    puVar22 = puVar32;
    puVar25 = puVar24;
    do {
      *puVar25 = *puVar22;
      puVar22 = puVar22 + 1;
      puVar25 = puVar25 + 1;
      iVar13 = iVar13 + -1;
    } while (iVar13 != 0);
    lVar16 = FUN_000ad490(uVar29);
    bVar43 = false;
    if (lVar16 != 0) {
      lVar16 = lVar35 * 0x300;
      (&DAT_0273f280)[lVar16] = 0;
      if ((&DAT_0273fbe4)[lVar35] == '\0') {
        (&DAT_0273fbe4)[lVar35] = 1;
      }
      lVar17 = FUN_000ad490(uVar29);
      auVar55._8_56_ = extraout_var;
      auVar55._0_8_ = extraout_XMM0_Qa;
      lVar38 = 0;
      psVar27 = local_c0;
      do {
        uVar57 = auVar55._8_8_;
        *(undefined4 *)psVar27 = *(undefined4 *)(lVar17 + 0x44 + lVar38 * 2);
        if (((DAT_0273fbe9 != '\0') &&
            (lVar18 = FUN_005287f0(uVar29), uVar57 = extraout_XMM0_Qb, lVar18 != 0)) &&
           (*(char *)(lVar18 + 1) != '\x01')) {
          if (*(char *)(lVar18 + 1) == '\x02') {
            auVar52 = ZEXT416((uint)((float)(int)psVar27[1] * DAT_0166b898));
            if ((float)(int)psVar27[1] * DAT_0166b898 + DAT_0166b89c < DAT_0166b8cc) {
              auVar52 = ZEXT416((uint)DAT_0166b8a0);
            }
            sVar40 = *psVar27;
            auVar50 = ZEXT416((uint)DAT_0166b89c);
            if (auVar52._0_4_ + DAT_0166b8a0 < DAT_0166b8cc) {
              auVar50 = auVar52;
            }
            auVar52 = ZEXT416((uint)((float)(int)sVar40 * DAT_0166b898));
            if ((float)(int)sVar40 * DAT_0166b898 + DAT_0166b89c < DAT_0166b8cc) {
              auVar52 = ZEXT416((uint)DAT_0166b8a0);
            }
            auVar51 = ZEXT416((uint)DAT_0166b89c);
            if (auVar52._0_4_ + DAT_0166b8a0 < DAT_0166b8cc) {
              auVar51 = auVar52;
            }
            auVar52 = vandps_avx(auVar51,ZEXT416(DAT_0166b8f0));
            fVar45 = auVar52._0_4_;
            fVar44 = DAT_0166b89c;
            if (DAT_0166b8a4 < fVar45) {
              auVar50 = vandps_avx(auVar50,ZEXT416(DAT_0166b8f0));
              fVar58 = auVar50._0_4_;
              if (DAT_0166b8a4 < fVar58) {
                auVar52 = vunpcklps_avx(auVar52,auVar50);
                auVar52 = vshufps_avx(auVar52,ZEXT416((uint)DAT_0166b89c),0x14);
                if (fVar45 <= fVar58) {
                  auVar50._4_12_ = auVar52._4_12_;
                  auVar50._0_4_ = fVar45 / fVar58;
                  auVar52 = vpshufd_avx(auVar50,0xe0);
                  auVar51._4_12_ = auVar52._4_12_;
                  auVar51._0_4_ = DAT_0166b89c;
                  auVar52 = vpshufd_avx(auVar51,0xe1);
                }
                else {
                  auVar49._4_12_ = auVar52._4_12_;
                  auVar49._0_4_ = fVar58 / fVar45;
                  auVar52 = vpshufd_avx(auVar49,0xe0);
                  auVar52._4_12_ = auVar52._4_12_;
                  auVar52._0_4_ = DAT_0166b89c;
                }
                auVar50 = vpshufd_avx(auVar52,1);
                auVar52 = ZEXT416((uint)(auVar52._0_4_ * auVar52._0_4_ +
                                        auVar50._0_4_ * auVar50._0_4_));
                auVar52 = vsqrtss_avx(auVar52,auVar52);
                fVar44 = auVar52._0_4_;
              }
            }
            fVar44 = DAT_0166b89c / fVar44;
          }
          else {
            sVar40 = *psVar27;
            fVar44 = DAT_0166b89c;
          }
          fVar45 = fVar44 * (float)(int)sVar40;
          if (((fVar45 <= DAT_0166b8a8) || (sVar40 = 0x7fff, fVar45 < DAT_0166b8ac)) &&
             (sVar40 = -0x8000, DAT_0166b8a8 < fVar45)) {
            sVar40 = (short)(int)fVar45;
          }
          *psVar27 = sVar40;
          fVar44 = fVar44 * (float)(int)psVar27[1];
          uVar57 = 0;
          if (((fVar44 <= DAT_0166b8a8) || (sVar40 = 0x7fff, fVar44 < DAT_0166b8ac)) &&
             (sVar40 = -0x8000, DAT_0166b8a8 < fVar44)) {
            sVar40 = (short)(int)fVar44;
          }
          psVar27[1] = sVar40;
        }
        sVar40 = *(short *)((long)&DAT_0166b8dc + lVar38);
        if ((DAT_0273fbe9 != '\0') &&
           (lVar18 = FUN_005287f0(uVar29), uVar57 = extraout_XMM0_Qb_00, lVar18 != 0)) {
          fVar44 = *(float *)(lVar18 + 4);
          uVar57 = 0;
          if (((fVar44 <= DAT_0166b8cc) || (sVar40 = 0x7fff, fVar44 < DAT_0166b89c)) &&
             (sVar40 = 0, DAT_0166b8cc < fVar44)) {
            uVar57 = 0;
            sVar40 = (short)(int)(fVar44 * DAT_0166b8ac);
          }
        }
        auVar53._0_8_ = (double)(int)sVar40;
        auVar53._8_8_ = uVar57;
        auVar56 = auVar53._4_12_;
        dVar62 = (double)(int)*psVar27;
        dVar64 = 0.0;
        if (auVar53._0_8_ < dVar62) {
          dVar64 = ((dVar62 - auVar53._0_8_) * DAT_0166b930) / (DAT_0166b930 - auVar53._0_8_);
        }
        dVar60 = (double)((ulong)auVar53._0_8_ ^ _DAT_0166b900);
        if (dVar62 < dVar60) {
          dVar64 = ((auVar53._0_8_ + dVar62) * DAT_0166b938) / (auVar53._0_8_ + DAT_0166b938);
        }
        *psVar27 = (short)(int)dVar64;
        dVar63 = (double)(int)psVar27[1];
        dVar62 = 0.0;
        if (auVar53._0_8_ < dVar63) {
          dVar62 = ((dVar63 - auVar53._0_8_) * DAT_0166b930) / (DAT_0166b930 - auVar53._0_8_);
        }
        if (dVar63 < dVar60) {
          dVar62 = (auVar53._0_8_ + dVar63) * DAT_0166b938;
          auVar56._4_8_ = 0;
          auVar56._0_4_ = (uint)((ulong)dVar62 >> 0x20);
          dVar62 = dVar62 / (auVar53._0_8_ + DAT_0166b938);
        }
        psVar27[1] = (short)(int)dVar62;
        auVar61._0_4_ = (float)(int)(short)(int)dVar64;
        auVar61._4_12_ = auVar56;
        auVar54._0_4_ = (float)(int)(short)(int)dVar62;
        auVar54._4_12_ = auVar56;
        auVar55._0_8_ = thunk_FUN_012aaf86(auVar54._0_8_,auVar61._0_8_);
        auVar55._8_56_ = extraout_var_00;
        *(int *)(psVar27 + 5) = (int)auVar55._0_8_;
        if (DAT_0273fbe9 != '\0') {
          lVar18 = FUN_005287f0(uVar29);
          auVar55._8_56_ = extraout_var_01;
          auVar55._0_8_ = extraout_XMM0_Qa_00;
          if (lVar18 != 0) {
            fVar44 = *(float *)(lVar18 + 8);
            auVar55 = ZEXT464((uint)fVar44);
            if ((fVar44 <= DAT_0166b8cc) || (sVar40 = 0x7fff, fVar44 < DAT_0166b89c)) {
              if (DAT_0166b8cc < fVar44) {
                auVar55 = ZEXT464((uint)(fVar44 * DAT_0166b8ac));
                sVar40 = (short)(int)(fVar44 * DAT_0166b8ac);
                if (0 < sVar40) goto LAB_00926e04;
              }
            }
            else {
LAB_00926e04:
              local_58 = (double)(int)*psVar27;
              local_50 = (double)(int)psVar27[1];
              dVar62 = (double)FUN_000ab190(&local_58);
              if (((dVar62 <= DAT_0166b938) ||
                  (dVar64 = (double)FUN_000ab190(&local_58), dVar62 = DAT_0166b930,
                  dVar64 < DAT_0166b930)) &&
                 (dVar64 = (double)FUN_000ab190(&local_58), dVar62 = DAT_0166b938,
                 DAT_0166b938 < dVar64)) {
                dVar62 = (double)FUN_000ab190(&local_58);
              }
              dVar64 = (double)(int)sVar40;
              if (dVar62 <= dVar64) {
                iVar31 = 0;
                iVar13 = 0;
              }
              else {
                dVar62 = ((dVar62 - dVar64) * DAT_0166b930) / (DAT_0166b930 - dVar64);
                fVar44 = (float)thunk_FUN_012aaa36(*(undefined4 *)(psVar27 + 5),1,0);
                fVar45 = (float)thunk_FUN_012aaa36(*(undefined4 *)(psVar27 + 5),0,0);
                iVar31 = (int)(short)(int)(dVar62 * (double)fVar44);
                iVar13 = (int)(short)(int)(dVar62 * (double)fVar45);
              }
              auVar55._0_8_ = FUN_0092e580(psVar27,iVar31,iVar13);
              auVar55._8_56_ = extraout_var_02;
            }
          }
        }
        psVar27 = psVar27 + 2;
        lVar38 = lVar38 + 2;
      } while ((int)lVar38 != 4);
      lVar17 = FUN_000ad490(uVar29);
      uVar57 = *(undefined8 *)(lVar17 + 0x50);
      uVar5 = *(undefined8 *)(lVar17 + 0x58);
      uVar6 = *(undefined8 *)(lVar17 + 0x68);
      *(undefined8 *)(&DAT_0273f230 + lVar16) = *(undefined8 *)(lVar17 + 0x60);
      *(undefined8 *)(lVar16 + 0x273f238) = uVar6;
      *(undefined8 *)(&DAT_0273f220 + lVar16) = uVar57;
      *(undefined8 *)(lVar16 + 0x273f228) = uVar5;
      (&DAT_0273f242)[lVar16] = *(undefined1 *)(lVar17 + 0x72);
      *(undefined2 *)(&DAT_0273f240 + lVar16) = *(undefined2 *)(lVar17 + 0x70);
      uVar57 = *(undefined8 *)(lVar17 + 0x80);
      uVar5 = *(undefined8 *)(lVar17 + 0x88);
      uVar6 = *(undefined8 *)(lVar17 + 0x98);
      *(undefined8 *)(&DAT_0273f260 + lVar35 * 0xc0) = *(undefined8 *)(lVar17 + 0x90);
      *(undefined8 *)(lVar16 + 0x273f268) = uVar6;
      *(undefined8 *)(&DAT_0273f250 + lVar35 * 0xc0) = uVar57;
      *(undefined8 *)(lVar16 + 0x273f258) = uVar5;
      (&DAT_0273f272)[lVar16] = *(undefined1 *)(lVar17 + 0xa2);
      *(undefined2 *)(&DAT_0273f270 + lVar16) = *(undefined2 *)(lVar17 + 0xa0);
      lVar17 = FUN_000ad490(uVar29);
      uVar47 = DAT_0166b8b0;
      uVar46 = FUN_000915e0(*(undefined4 *)(&DAT_0273f298 + lVar16),*(undefined4 *)(lVar17 + 0xb4));
      *(undefined4 *)(&DAT_0273f298 + lVar16) = uVar46;
      uVar46 = FUN_000915e0(*(undefined4 *)(&DAT_0273f294 + lVar16),*(undefined4 *)(lVar17 + 0xb0),
                            uVar47);
      *(undefined4 *)(&DAT_0273f294 + lVar16) = uVar46;
      uVar47 = FUN_000915e0(*(undefined4 *)(&DAT_0273f29c + lVar16),*(undefined4 *)(lVar17 + 0xb8),
                            uVar47);
      *(undefined4 *)(&DAT_0273f29c + lVar16) = uVar47;
      lVar17 = FUN_000ad490(uVar29);
      plVar19 = (long *)FUN_005288b0(uVar29);
      bVar10 = FUN_00528780(uVar29);
      lVar38 = 0;
      pfVar20 = pfVar37;
      if (plVar19 == (long *)0x0) {
        do {
          cVar9 = *(char *)(lVar17 + 4 + lVar38);
          bVar10 = -(cVar9 != '\0');
          if ((uint)lVar38 < 2) {
            bVar10 = *(byte *)(lVar17 + lVar38);
          }
          uVar12 = *(undefined2 *)(lVar17 + 0x1a + lVar38 * 2);
          *(undefined1 *)((long)pfVar20 + -5) = *(undefined1 *)((long)pfVar20 + -6);
          fVar44 = (float)bVar10 / DAT_0166b8b4;
          *(undefined2 *)(pfVar20 + -2) = uVar12;
          *(char *)((long)pfVar20 + -6) = cVar9;
          *pfVar20 = fVar44;
          if ((cVar9 == '\0') && ((*(byte *)(pfVar20 + -1) & 1) != 0)) {
            *(byte *)(pfVar20 + -1) = *(byte *)(pfVar20 + -1) & 0xfe;
          }
          lVar38 = lVar38 + 1;
          pfVar20 = pfVar20 + 5;
        } while ((int)lVar38 != 0x11);
      }
      else {
        plVar36 = plVar19 + 1;
        do {
          lVar18 = 0x20;
          lVar41 = -1;
          do {
            lVar41 = lVar41 + 1;
            if (*plVar19 <= lVar41) {
              cVar9 = *(char *)(lVar17 + 4 + lVar38);
              bVar28 = -(cVar9 != '\0');
              if ((uint)lVar38 < 2) {
                bVar28 = *(byte *)(lVar17 + lVar38);
              }
              uVar12 = *(undefined2 *)(lVar17 + 0x1a + lVar38 * 2);
              (&DAT_0273efe3)[lVar38 * 0x14 + lVar16] = (&DAT_0273efe2)[lVar38 * 0x14 + lVar16];
              fVar44 = (float)bVar28 / DAT_0166b8b4;
              (&DAT_0273efe0)[lVar35 * 0x180 + lVar38 * 10] = uVar12;
              (&DAT_0273efe2)[lVar38 * 0x14 + lVar16] = cVar9;
              (&DAT_0273efe8)[lVar35 * 0xc0 + lVar38 * 5] = fVar44;
              if ((cVar9 == '\0') && (((&DAT_0273efe4)[lVar38 * 0x14 + lVar16] & 1) != 0)) {
                (&DAT_0273efe4)[lVar38 * 0x14 + lVar16] =
                     (&DAT_0273efe4)[lVar38 * 0x14 + lVar16] & 0xfe;
              }
              break;
            }
            lVar4 = *plVar36;
            uVar15 = FUN_00528a00(*(undefined1 *)((long)plVar36 + lVar18 + lVar4));
            lVar1 = lVar18 + -0x10;
            lVar18 = lVar18 + 0x18;
          } while (((*(byte *)((long)plVar36 + lVar1 + lVar4) & (byte)(1 << (bVar10 & 0x1f))) == 0)
                  || (uVar15 != (uint)lVar38));
          lVar38 = lVar38 + 1;
        } while ((int)lVar38 != 0x11);
      }
      local_58 = (double)((ulong)local_58 & 0xffffffff00000000);
      plVar19 = (long *)FUN_005288b0(uVar29);
      cVar9 = '\0';
      if (plVar19 == (long *)0x0) {
        cVar39 = '\0';
        cVar21 = '\0';
LAB_00927530:
        (&DAT_0273f137)[lVar16] = (&DAT_0273f136)[lVar16];
        *(undefined2 *)(&DAT_0273f134 + lVar16) = 0;
        (&DAT_0273f136)[lVar16] = 0;
        *(undefined4 *)(&DAT_0273f13c + lVar16) = 0;
        if (((&DAT_0273f138)[lVar16] & 1) != 0) {
          (&DAT_0273f138)[lVar16] = (&DAT_0273f138)[lVar16] & 0xfe;
        }
      }
      else {
        bVar10 = FUN_00528780(uVar29);
        cVar21 = '\0';
        cVar39 = '\0';
        if (*plVar19 < 1) goto LAB_00927530;
        plVar36 = plVar19 + 1;
        lVar17 = 0;
        do {
          lVar38 = *plVar36;
          if ((*(byte *)((long)plVar36 + lVar17 * 0x18 + lVar38 + 0x10) &
              (byte)(1 << (bVar10 & 0x1f))) != 0) {
            uVar15 = FUN_00528a00();
            lVar18 = *(long *)((long)plVar36 + lVar17 * 0x18 + lVar38 + 0x18);
            pauVar2 = (undefined1 (*) [16])((long)plVar36 + lVar18 + lVar17 * 0x18 + lVar38 + 0x18);
            iVar13 = 0;
            pcVar26 = local_78;
            do {
              if (lVar18 == 0) {
                iVar31 = -1;
                pauVar33 = (undefined1 (*) [16])0x0;
              }
              else {
                iVar31 = *(int *)(pauVar2[-1] + 0xc);
                pauVar33 = pauVar2;
              }
              if (*(int *)puVar7 == iVar31) {
                bVar43 = true;
                if (((pauVar33[2][0] != '\0') &&
                    (bVar43 = false, ((&DAT_0273f124)[lVar16] & 1) == 0)) &&
                   (((&DAT_0273f130)[lVar35 * 0xc0] == 0x25 ||
                    ((&DAT_0273f130)[lVar35 * 0xc0] == (&DAT_0273f12c)[lVar35 * 0xc0])))) {
                  bVar43 = (&DAT_0273f122)[lVar16] != '\0';
                }
                bVar42 = false;
                fVar44 = SUB164(*(undefined1 (*) [16])(pcVar26 + -0x22),0);
                if ((SUB164(*pauVar33,0) <= fVar44) && (fVar44 <= SUB164(pauVar33[1],0))) {
                  auVar52 = vpshufd_avx(*(undefined1 (*) [16])(pcVar26 + -0x22),1);
                  auVar50 = vpshufd_avx(*pauVar33,1);
                  if (auVar52._0_4_ <= auVar50._0_4_) {
                    auVar50 = vpshufd_avx(pauVar33[1],1);
                    bVar42 = auVar50._0_4_ <= auVar52._0_4_;
                  }
                }
                if (pcVar26[-1] != '\0') {
                  if (bVar43) {
                    bVar43 = bVar42;
                  }
                  bVar42 = false;
LAB_00927480:
                  if (bVar43) {
                    if (bVar42) {
                      *pcVar26 = '\x01';
                    }
                    uVar23 = (ulong)uVar15;
                    cVar9 = (&DAT_0273efe2)[uVar23 * 0x14 + lVar16];
                    pbVar34 = &DAT_0273efe2 + uVar23 * 0x14 + lVar16;
                    psVar27 = &DAT_0273efe0 + lVar35 * 0x180 + uVar23 * 10;
                    if (iVar13 == -1) goto LAB_009274c3;
                    if (cVar9 != -1) {
                      (&DAT_0273efe3)[uVar23 * 0x14 + lVar16] = cVar9;
                      bVar28 = cVar9 + 1;
                      *psVar27 = (ushort)bVar28 * 0x21;
                      *pbVar34 = bVar28;
                      (&DAT_0273efe8)[lVar35 * 0xc0 + uVar23 * 5] = 0x3f800000;
                      if ((bVar28 == 0) && (((&DAT_0273efe4)[uVar23 * 0x14 + lVar16] & 1) != 0)) {
                        (&DAT_0273efe4)[uVar23 * 0x14 + lVar16] =
                             (&DAT_0273efe4)[uVar23 * 0x14 + lVar16] & 0xfe;
                      }
                    }
                    goto LAB_009274e7;
                  }
                }
              }
              else if (((*(int *)puVar8 == iVar31) && (pcVar26[-1] != '\0')) && (*pcVar26 == '\0'))
              {
                if ((*pauVar33)[0] == '\x01') {
                  bVar43 = *(float *)(pcVar26 + -0x12) == *(float *)(pcVar26 + -0x22) + DAT_0166b8b8
                  ;
                  bVar42 = *(float *)(pcVar26 + -0x12) < *(float *)(pcVar26 + -0x22) + DAT_0166b8b8;
                }
                else {
                  bVar43 = false;
                  bVar42 = bVar43;
                  if ((*pauVar33)[0] != '\0') goto LAB_00927480;
                  bVar43 = *(float *)(pcVar26 + -0x22) + DAT_0166b8bc == *(float *)(pcVar26 + -0x12)
                  ;
                  bVar42 = *(float *)(pcVar26 + -0x22) + DAT_0166b8bc < *(float *)(pcVar26 + -0x12);
                }
                bVar43 = !bVar42 && !bVar43;
                bVar42 = bVar43;
                goto LAB_00927480;
              }
              pcVar26 = pcVar26 + 0x30;
              iVar13 = iVar13 + 1;
            } while (iVar13 < 2);
            uVar23 = (ulong)uVar15;
            cVar9 = (&DAT_0273efe2)[uVar23 * 0x14 + lVar16];
            pbVar34 = &DAT_0273efe2 + uVar23 * 0x14 + lVar16;
            psVar27 = &DAT_0273efe0 + lVar35 * 0x180 + uVar23 * 10;
LAB_009274c3:
            *(char *)((long)psVar27 + 3) = cVar9;
            *psVar27 = 0;
            *pbVar34 = 0;
            psVar27[4] = 0;
            psVar27[5] = 0;
            if ((*(byte *)(psVar27 + 2) & 1) != 0) {
              *(byte *)(psVar27 + 2) = *(byte *)(psVar27 + 2) & 0xfe;
            }
LAB_009274e7:
            if (uVar15 - 0x11 < 4) {
              *(undefined1 *)((long)&local_58 + (long)(int)(uVar15 - 0x11)) = 1;
            }
          }
          lVar17 = lVar17 + 1;
        } while (lVar17 < *plVar19);
        cVar9 = (char)((ulong)local_58 >> 0x18);
        cVar21 = (char)((ulong)local_58 >> 0x10);
        cVar39 = (char)((ulong)local_58 >> 8);
        if (SUB81(local_58,0) == '\0') goto LAB_00927530;
      }
      if (cVar39 == '\0') {
        (&DAT_0273f14b)[lVar16] = (&DAT_0273f14a)[lVar16];
        *(undefined2 *)(&DAT_0273f148 + lVar16) = 0;
        (&DAT_0273f14a)[lVar16] = 0;
        *(undefined4 *)(&DAT_0273f150 + lVar16) = 0;
        if (((&DAT_0273f14c)[lVar16] & 1) != 0) {
          (&DAT_0273f14c)[lVar16] = (&DAT_0273f14c)[lVar16] & 0xfe;
        }
      }
      if (cVar21 == '\0') {
        (&DAT_0273f15f)[lVar16] = (&DAT_0273f15e)[lVar16];
        *(undefined2 *)(&DAT_0273f15c + lVar16) = 0;
        (&DAT_0273f15e)[lVar16] = 0;
        *(undefined4 *)(&DAT_0273f164 + lVar16) = 0;
        if (((&DAT_0273f160)[lVar16] & 1) != 0) {
          (&DAT_0273f160)[lVar16] = (&DAT_0273f160)[lVar16] & 0xfe;
        }
      }
      if (cVar9 == '\0') {
        (&DAT_0273f173)[lVar16] = (&DAT_0273f172)[lVar16];
        *(undefined2 *)(&DAT_0273f170 + lVar16) = 0;
        (&DAT_0273f172)[lVar16] = 0;
        *(undefined4 *)(&DAT_0273f178 + lVar16) = 0;
        if (((&DAT_0273f174)[lVar16] & 1) != 0) {
          (&DAT_0273f174)[lVar16] = (&DAT_0273f174)[lVar16] & 0xfe;
        }
      }
      FUN_00926320(uVar29,&DAT_0273f282 + lVar35 * 0x180,&local_48);
      uVar15 = DAT_0166b910;
      lVar17 = lVar35 * 0xa8;
      sVar40 = *(short *)(&DAT_0273edd8 + lVar35 * 0x15);
      if (sVar40 == 3) {
        uVar48 = uStack_40 ^ DAT_0166b910;
        *(uint *)(&DAT_0273f2ac + lVar16) = uVar48;
        uVar59 = uStack_44 ^ uVar15;
        *(uint *)(&DAT_0273f2b4 + lVar16) = uVar59;
        *(uint *)(&DAT_0273f2a0 + lVar16) = uStack_3c;
        *(uint *)(&DAT_0273f2a4 + lVar16) = uVar15 ^ local_48;
      }
      else if (sVar40 == 2) {
        uVar48 = DAT_0166b910 ^ local_48;
        *(uint *)(&DAT_0273f2ac + lVar16) = uVar48;
        uVar59 = uStack_3c ^ uVar15;
        *(uint *)(&DAT_0273f2b4 + lVar16) = uVar59;
        *(uint *)(&DAT_0273f2a0 + lVar16) = uStack_44;
        *(uint *)(&DAT_0273f2a4 + lVar16) = uStack_40 ^ uVar15;
      }
      else if (sVar40 == 1) {
        uVar48 = DAT_0166b910 ^ local_48;
        *(uint *)(&DAT_0273f2ac + lVar16) = uVar48;
        uVar59 = uStack_44 ^ uVar15;
        *(uint *)(&DAT_0273f2b4 + lVar16) = uVar59;
        *(uint *)(&DAT_0273f2a4 + lVar16) = uStack_40 ^ uVar15;
        *(uint *)(&DAT_0273f2a0 + lVar16) = uStack_3c;
      }
      else {
        *(uint *)(&DAT_0273f2a4 + lVar16) = DAT_0166b910 ^ local_48;
        *(uint *)(&DAT_0273f2a0 + lVar16) = uStack_44;
        uVar48 = uStack_40 ^ uVar15;
        *(uint *)(&DAT_0273f2ac + lVar16) = uVar48;
        uVar59 = uStack_3c ^ uVar15;
        *(uint *)(&DAT_0273f2b4 + lVar16) = uVar59;
      }
      *(undefined8 *)(&DAT_0273f2b8 + lVar16) = *(undefined8 *)(&DAT_0273f2b0 + lVar16);
      puVar3 = (uint *)(&DAT_0273f2b8 + lVar16);
      if (*(char *)((long)&DAT_0273edd8 + lVar17 + 3) != '\0') {
        uVar14 = (uint)*(undefined8 *)(&DAT_0273f2b0 + lVar16) ^ 0x80000000;
        *(uint *)(&DAT_0273f2b0 + lVar16) = uVar14;
        uVar15 = DAT_0166b910;
        *(uint *)(&DAT_0273f2b4 + lVar16) = uVar59 ^ DAT_0166b910;
        *puVar3 = uVar14;
        *(uint *)(&DAT_0273f2bc + lVar16) = *(uint *)(&DAT_0273f2bc + lVar16) ^ uVar15;
      }
      if (*(char *)((long)&DAT_0273edd8 + lVar17 + 4) == '\0') {
        cVar9 = FUN_000014d0();
        if (cVar9 != '\0') {
          uVar48 = *(uint *)(&DAT_0273f2ac + lVar16);
          goto LAB_009278dc;
        }
      }
      else {
LAB_009278dc:
        uVar15 = DAT_0166b910;
        *(uint *)(&DAT_0273f2a8 + lVar16) = *(uint *)(&DAT_0273f2a8 + lVar16) ^ DAT_0166b910;
        *(uint *)(&DAT_0273f2ac + lVar16) = uVar48 ^ uVar15;
      }
      uVar15 = DAT_0166b910;
      bVar43 = true;
      if (*(char *)((long)&DAT_0273edd8 + lVar17 + 5) != '\0') {
        *puVar3 = *puVar3 ^ DAT_0166b910;
        *(uint *)(&DAT_0273f2bc + lVar16) = *(uint *)(&DAT_0273f2bc + lVar16) ^ uVar15;
      }
    }
    if (uVar29 == 0) {
      if (bVar43) {
        cVar9 = FUN_0005ce00(&DAT_0273f282,8);
        if (cVar9 == '\0') goto LAB_00927a50;
        cVar9 = FUN_0005ce00(&DAT_0273efe0,0x1a4);
        if (cVar9 == '\0') {
          uVar15 = 0;
          piVar30 = &DAT_0273eff0;
          do {
            if ((*(byte *)(piVar30 + -3) & 1) != 0) goto LAB_00927a50;
            iVar13 = *piVar30;
            if ((iVar13 == 0x25) || (iVar13 == piVar30[-1])) {
              if (*(char *)((long)piVar30 + -0xe) != '\0') goto LAB_00927a50;
              if (iVar13 != 0x25) goto LAB_009279e1;
LAB_009279e6:
              if (DAT_0166b8cc < (float)piVar30[-2]) goto LAB_00927a50;
            }
            else {
LAB_009279e1:
              if (iVar13 == piVar30[-1]) goto LAB_009279e6;
            }
            piVar30 = piVar30 + 5;
            uVar15 = uVar15 + 1;
          } while (uVar15 < 0x15);
        }
      }
      lVar16 = lVar35 * 0x300;
      piVar30 = (int *)FUN_000ad670();
      (&DAT_0273f280)[lVar16] = 1;
      fVar44 = DAT_0166b8c0;
      if (piVar30 == (int *)0x0) {
        *(undefined4 *)(&DAT_0273f2b0 + lVar16) = 0;
        *(undefined4 *)(&DAT_0273f2a8 + lVar16) = 0;
      }
      else {
        *(float *)(&DAT_0273f2a8 + lVar16) = ((float)*piVar30 * DAT_0166b8c0) / DAT_0166b8c4;
        *(float *)(&DAT_0273f2b0 + lVar16) = ((float)piVar30[1] * fVar44) / DAT_0166b8c8;
      }
      *(undefined8 *)(&DAT_0273f2d0 + lVar16) = 0;
      *(undefined8 *)(lVar16 + 0x273f2d8) = 0;
      *(undefined8 *)(&DAT_0273f2c0 + lVar16) = 0;
      *(undefined8 *)(lVar16 + 0x273f2c8) = 0;
      iVar13 = FUN_000ad300(0x69);
      if (((iVar13 < 1) && (iVar13 = FUN_000ad300(0x6a), iVar13 < 1)) &&
         (iVar13 = FUN_000ad300(0x6c), iVar13 < 1)) {
        iVar13 = FUN_000ad300(0x4f);
        iVar31 = FUN_000ad300(0x50);
        *(float *)(&DAT_0273f2ac + lVar16) = (float)(int)((uint)(0 < iVar13) - (uint)(0 < iVar31));
        iVar13 = FUN_000ad300(0x4e);
        iVar31 = FUN_000ad300(0x4d);
        *(float *)(&DAT_0273f2b4 + lVar16) = (float)(int)((uint)(0 < iVar13) - (uint)(0 < iVar31));
      }
      *(undefined8 *)(&DAT_0273f2b8 + lVar16) = *(undefined8 *)(&DAT_0273f2b0 + lVar16);
      iVar13 = FUN_000ad300(0x20);
      iVar31 = FUN_000ad300(0x2e);
      *(float *)(&DAT_0273f2a0 + lVar16) = (float)(int)((uint)(0 < iVar13) - (uint)(0 < iVar31));
      iVar13 = FUN_000ad300(0x2d);
      iVar31 = FUN_000ad300(0x2f);
      *(float *)(&DAT_0273f2a4 + lVar16) = (float)(int)((uint)(0 < iVar13) - (uint)(0 < iVar31));
      uVar12 = FUN_000ad3a0(0x48);
      uVar11 = FUN_000ad300(0x48);
      iVar13 = FUN_000ad300(0x48);
      fVar44 = DAT_0166b8b4;
      fVar45 = (float)(byte)-(iVar13 != 0) / DAT_0166b8b4;
      *(undefined2 *)(&DAT_0273f0a8 + lVar16) = uVar12;
      (&DAT_0273f0aa)[lVar16] = uVar11;
      *(float *)(&DAT_0273f0b0 + lVar16) = fVar45;
      uVar12 = FUN_000ad3a0(0x3d);
      uVar11 = FUN_000ad300(0x3d);
      iVar13 = FUN_000ad300(0x3d);
      *(undefined2 *)(&DAT_0273f10c + lVar16) = uVar12;
      (&DAT_0273f10e)[lVar16] = uVar11;
      *(float *)(&DAT_0273f114 + lVar16) = (float)(byte)-(iVar13 != 0) / fVar44;
      uVar12 = FUN_000ad3a0(0x30);
      uVar11 = FUN_000ad300(0x30);
      iVar13 = FUN_000ad300(0x30);
      *(undefined2 *)(&DAT_0273f0f8 + lVar16) = uVar12;
      (&DAT_0273f0fa)[lVar16] = uVar11;
      *(float *)(&DAT_0273f100 + lVar16) = (float)(byte)-(iVar13 != 0) / fVar44;
      uVar12 = FUN_000ad3a0(0x22);
      uVar11 = FUN_000ad300(0x22);
      iVar13 = FUN_000ad300(0x22);
      *(undefined2 *)(&DAT_0273f0e4 + lVar16) = uVar12;
      (&DAT_0273f0e6)[lVar16] = uVar11;
      *(float *)(&DAT_0273f0ec + lVar16) = (float)(byte)-(iVar13 != 0) / fVar44;
      uVar12 = FUN_000ad3a0(0x3b);
      uVar11 = FUN_000ad300(0x3b);
      iVar13 = FUN_000ad300(0x3b);
      *(undefined2 *)(&DAT_0273f030 + lVar16) = uVar12;
      (&DAT_0273f032)[lVar16] = uVar11;
      *(float *)(&DAT_0273f038 + lVar16) = (float)(byte)-(iVar13 != 0) / fVar44;
      uVar12 = FUN_000ad3a0(0x3c);
      uVar11 = FUN_000ad300(0x3c);
      iVar13 = FUN_000ad300(0x3c);
      *(undefined2 *)(&DAT_0273f044 + lVar16) = uVar12;
      (&DAT_0273f046)[lVar16] = uVar11;
      *(float *)(&DAT_0273f04c + lVar16) = (float)(byte)-(iVar13 != 0) / fVar44;
      uVar12 = FUN_000ad3a0(0x1f);
      uVar11 = FUN_000ad300(0x1f);
      iVar13 = FUN_000ad300(0x1f);
      *(undefined2 *)(&DAT_0273f0bc + lVar16) = uVar12;
      (&DAT_0273f0be)[lVar16] = uVar11;
      *(float *)(&DAT_0273f0c4 + lVar16) = (float)(byte)-(iVar13 != 0) / fVar44;
      uVar12 = FUN_000ad3a0(0x21);
      uVar11 = FUN_000ad300(0x21);
      iVar13 = FUN_000ad300(0x21);
      *(undefined2 *)(&DAT_0273f0d0 + lVar16) = uVar12;
      (&DAT_0273f0d2)[lVar16] = uVar11;
      *(float *)(&DAT_0273f0d8 + lVar16) = (float)(byte)-(iVar13 != 0) / fVar44;
      uVar12 = FUN_000ad3a0(0x3a);
      uVar11 = FUN_000ad300(0x3a);
      iVar13 = FUN_000ad300(0x3a);
      *(undefined2 *)(&DAT_0273f080 + lVar16) = uVar12;
      (&DAT_0273f082)[lVar16] = uVar11;
      *(float *)(&DAT_0273f088 + lVar16) = (float)(byte)-(iVar13 != 0) / fVar44;
      iVar13 = FUN_000ad6c0(1);
      iVar31 = FUN_000ad3a0(0x3e);
      if (iVar31 < iVar13) {
        uVar12 = FUN_000ad6c0(1);
      }
      else {
        uVar12 = FUN_000ad3a0(0x3e);
      }
      iVar13 = FUN_000ad6a0(1);
      iVar31 = FUN_000ad300(0x3e);
      if (iVar31 < iVar13) {
        uVar11 = FUN_000ad6a0(1);
      }
      else {
        uVar11 = FUN_000ad300(0x3e);
      }
      iVar13 = FUN_000ad6a0(1);
      iVar31 = FUN_000ad300(0x3e);
      if (iVar31 < iVar13) {
        iVar13 = FUN_000ad6a0(1);
      }
      else {
        iVar13 = FUN_000ad300(0x3e);
      }
      fVar44 = (float)(byte)-(iVar13 != 0) / DAT_0166b8b4;
      *(undefined2 *)(&DAT_0273f094 + lVar16) = uVar12;
      (&DAT_0273f096)[lVar16] = uVar11;
      *(float *)(&DAT_0273f09c + lVar16) = fVar44;
      iVar13 = FUN_000ad6c0(2);
      iVar31 = FUN_000ad3a0(0x55);
      if (iVar31 < iVar13) {
        uVar12 = FUN_000ad6c0(2);
      }
      else {
        uVar12 = FUN_000ad3a0(0x55);
      }
      iVar13 = FUN_000ad6a0(2);
      iVar31 = FUN_000ad300(0x55);
      if (iVar31 < iVar13) {
        uVar11 = FUN_000ad6a0(2);
      }
      else {
        uVar11 = FUN_000ad300(0x55);
      }
      iVar13 = FUN_000ad6c0(2);
      iVar31 = FUN_000ad300(0x55);
      if (iVar31 < iVar13) {
        iVar13 = FUN_000ad6c0(2);
      }
      else {
        iVar13 = FUN_000ad300(0x55);
      }
      fVar44 = (float)(byte)-(iVar13 != 0) / DAT_0166b8b4;
      (&DAT_0273efe0)[lVar35 * 0x180] = uVar12;
      (&DAT_0273efe2)[lVar16] = uVar11;
      (&DAT_0273efe8)[lVar35 * 0xc0] = fVar44;
      iVar13 = FUN_000ad6c0(0);
      iVar31 = FUN_000ad3a0(0x51);
      if (iVar31 < iVar13) {
        uVar12 = FUN_000ad6c0(0);
      }
      else {
        uVar12 = FUN_000ad3a0(0x51);
      }
      iVar13 = FUN_000ad6a0(0);
      iVar31 = FUN_000ad300(0x51);
      if (iVar31 < iVar13) {
        uVar11 = FUN_000ad6a0(0);
      }
      else {
        uVar11 = FUN_000ad300(0x51);
      }
      iVar13 = FUN_000ad6c0(0);
      iVar31 = FUN_000ad300(0x51);
      if (iVar31 < iVar13) {
        iVar13 = FUN_000ad6c0(0);
      }
      else {
        iVar13 = FUN_000ad300(0x51);
      }
      fVar44 = DAT_0166b8b4;
      fVar45 = (float)(byte)-(iVar13 != 0) / DAT_0166b8b4;
      (&DAT_0273eff4)[lVar35 * 0x180] = uVar12;
      (&DAT_0273eff6)[lVar16] = uVar11;
      (&DAT_0273effc)[lVar35 * 0xc0] = fVar45;
      uVar12 = FUN_000ad3a0(0x56);
      uVar11 = FUN_000ad300(0x56);
      iVar13 = FUN_000ad300(0x56);
      *(undefined2 *)(&DAT_0273f058 + lVar16) = uVar12;
      (&DAT_0273f05a)[lVar16] = uVar11;
      *(float *)(&DAT_0273f060 + lVar16) = (float)(byte)-(iVar13 != 0) / fVar44;
      uVar12 = FUN_000ad3a0(0x53);
      uVar11 = FUN_000ad300(0x53);
      iVar13 = FUN_000ad300(0x53);
      *(undefined2 *)(&DAT_0273f06c + lVar16) = uVar12;
      (&DAT_0273f06e)[lVar16] = uVar11;
      *(float *)(&DAT_0273f074 + lVar16) = (float)(byte)-(iVar13 != 0) / fVar44;
      uVar12 = FUN_000ad3a0(0x23);
      uVar11 = FUN_000ad300(0x23);
      iVar13 = FUN_000ad300(0x23);
      *(undefined2 *)(&DAT_0273f008 + lVar16) = uVar12;
      (&DAT_0273f00a)[lVar16] = uVar11;
      *(float *)(&DAT_0273f010 + lVar16) = (float)(byte)-(iVar13 != 0) / fVar44;
      uVar12 = FUN_000ad3a0(0x31);
      uVar11 = FUN_000ad300(0x31);
      iVar13 = FUN_000ad300(0x31);
      *(undefined2 *)(&DAT_0273f01c + lVar16) = uVar12;
      (&DAT_0273f01e)[lVar16] = uVar11;
      *(float *)(&DAT_0273f024 + lVar16) = (float)(byte)-(iVar13 != 0) / fVar44;
      uVar12 = FUN_000ad3a0(0x25);
      uVar11 = FUN_000ad300(0x25);
      iVar13 = FUN_000ad300(0x25);
      *(undefined2 *)(&DAT_0273f120 + lVar16) = uVar12;
      (&DAT_0273f122)[lVar16] = uVar11;
      *(float *)(&DAT_0273f128 + lVar16) = (float)(byte)-(iVar13 != 0) / fVar44;
      uVar12 = FUN_000ad3a0(0x33);
      uVar11 = FUN_000ad300(0x33);
      iVar13 = FUN_000ad300(0x33);
      *(undefined2 *)(&DAT_0273f134 + lVar16) = uVar12;
      (&DAT_0273f136)[lVar16] = uVar11;
      *(float *)(&DAT_0273f13c + lVar16) = (float)(byte)-(iVar13 != 0) / fVar44;
      uVar12 = FUN_000ad3a0(0x34);
      uVar11 = FUN_000ad300(0x34);
      iVar13 = FUN_000ad300(0x34);
      *(undefined2 *)(&DAT_0273f148 + lVar16) = uVar12;
      (&DAT_0273f14a)[lVar16] = uVar11;
      *(float *)(&DAT_0273f150 + lVar16) = (float)(byte)-(iVar13 != 0) / fVar44;
      uVar12 = FUN_000ad3a0(0x3f);
      uVar11 = FUN_000ad300(0x3f);
      iVar13 = FUN_000ad300(0x3f);
      *(undefined2 *)(&DAT_0273f15c + lVar16) = uVar12;
      (&DAT_0273f15e)[lVar16] = uVar11;
      *(float *)(&DAT_0273f164 + lVar16) = (float)(byte)-(iVar13 != 0) / fVar44;
      uVar12 = FUN_000ad3a0(0x40);
      uVar11 = FUN_000ad300(0x40);
      iVar13 = FUN_000ad300(0x40);
      *(undefined2 *)(&DAT_0273f170 + lVar16) = uVar12;
      (&DAT_0273f172)[lVar16] = uVar11;
      *(float *)(&DAT_0273f178 + lVar16) = (float)(byte)-(iVar13 != 0) / fVar44;
    }
    else {
LAB_00927a50:
      if (!bVar43) {
        lVar16 = 0;
        if ((&DAT_0273fbe4)[lVar35] != '\0') {
          do {
            *(undefined1 *)((long)pfVar37 + lVar16 + -5) =
                 *(undefined1 *)((long)pfVar37 + lVar16 + -6);
            *(undefined2 *)((long)pfVar37 + lVar16 + -8) = 0;
            *(undefined1 *)((long)pfVar37 + lVar16 + -6) = 0;
            *(undefined4 *)((long)pfVar37 + lVar16) = 0;
            bVar10 = *(byte *)((long)pfVar37 + lVar16 + -4);
            if ((bVar10 & 1) != 0) {
              *(byte *)((long)pfVar37 + lVar16 + -4) = bVar10 & 0xfe;
            }
            lVar16 = lVar16 + 0x14;
          } while ((int)lVar16 != 0x1a4);
          FUN_0092e580(&DAT_0273f282 + lVar35 * 0x180,0,0);
          FUN_0092e580(&DAT_0273f286 + lVar35 * 0x180,0,0);
          *(undefined1 (*) [16])(&DAT_0273f2b0 + lVar35 * 0x300) = ZEXT816(0) << 0x40;
          *(undefined1 (*) [16])(&DAT_0273f2a0 + lVar35 * 0x300) = ZEXT816(0) << 0x40;
        }
        (&DAT_0273fbe4)[lVar35] = 0;
      }
    }
    if (uVar29 + 1 == 0xffffffff) break;
    local_78 = local_78 + 0x300;
    pfVar37 = pfVar37 + 0xc0;
    local_c0 = local_c0 + 0x180;
    puVar32 = puVar32 + 0x2a;
    puVar24 = puVar24 + 0xc0;
    bVar43 = uVar29 < 3;
    uVar29 = uVar29 + 1;
  } while (bVar43);
  FUN_000ad140();
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

