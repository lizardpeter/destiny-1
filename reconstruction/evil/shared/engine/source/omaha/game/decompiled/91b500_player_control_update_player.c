
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0091b500(float param_1,float param_2,int param_3,uint param_4,long param_5,int *param_6,
                 uint *param_7)

{
  uint *puVar1;
  short sVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  float fVar6;
  undefined1 auVar7 [16];
  undefined1 auVar8 [16];
  undefined1 auVar9 [16];
  undefined1 auVar10 [16];
  undefined1 auVar11 [16];
  undefined1 auVar12 [16];
  undefined1 auVar13 [16];
  undefined1 auVar14 [16];
  undefined1 auVar15 [16];
  undefined1 auVar16 [16];
  undefined1 auVar17 [16];
  undefined1 auVar18 [16];
  undefined1 auVar19 [16];
  undefined1 auVar20 [16];
  undefined1 auVar21 [16];
  undefined1 auVar22 [16];
  undefined1 auVar23 [16];
  undefined1 auVar24 [16];
  char cVar25;
  byte bVar26;
  char cVar27;
  byte bVar28;
  char cVar29;
  char cVar30;
  char cVar31;
  bool bVar32;
  undefined4 uVar33;
  int iVar34;
  ulong uVar35;
  long lVar36;
  long lVar37;
  undefined8 *puVar38;
  long lVar39;
  char *pcVar40;
  float *pfVar41;
  uint *puVar42;
  uint uVar43;
  ulong uVar44;
  byte bVar45;
  long lVar46;
  long lVar47;
  long lVar48;
  float fVar49;
  float fVar50;
  undefined4 uVar51;
  float fVar52;
  uint uVar53;
  float fVar54;
  float extraout_XMM0_Da;
  undefined8 uVar55;
  undefined1 auVar56 [16];
  undefined1 auVar57 [16];
  undefined1 auVar58 [16];
  undefined1 auVar59 [16];
  float fVar66;
  undefined8 extraout_XMM0_Qb_00;
  undefined1 auVar60 [16];
  undefined1 auVar61 [16];
  undefined1 auVar62 [64];
  undefined8 extraout_XMM0_Qb;
  undefined1 auVar63 [64];
  undefined1 auVar64 [64];
  undefined1 auVar65 [64];
  float extraout_XMM1_Da;
  float fVar75;
  undefined1 auVar67 [16];
  undefined1 auVar68 [16];
  float fVar76;
  undefined1 auVar69 [16];
  undefined1 auVar70 [16];
  undefined1 auVar71 [16];
  undefined1 auVar72 [16];
  undefined1 auVar73 [16];
  undefined1 auVar74 [16];
  undefined1 auVar77 [16];
  undefined1 auVar78 [16];
  undefined1 auVar79 [16];
  undefined1 auVar80 [16];
  undefined1 auVar81 [16];
  undefined1 auVar82 [16];
  double dVar83;
  undefined1 auVar84 [16];
  undefined1 auVar85 [16];
  undefined1 auVar86 [16];
  undefined1 auVar87 [16];
  undefined1 auVar88 [16];
  undefined1 auVar89 [16];
  undefined1 auVar90 [16];
  undefined1 auVar91 [16];
  float local_2f8;
  double local_2e0;
  undefined1 local_2c8 [16];
  undefined1 local_2b8 [16];
  ulong local_2a0;
  undefined1 local_298 [2] [16];
  undefined1 local_278 [16];
  float local_260;
  float local_25c;
  long local_258;
  long local_250;
  undefined4 local_248;
  long local_240;
  undefined1 local_238 [8];
  undefined1 local_230 [8];
  undefined1 local_228 [152];
  ushort local_190;
  char local_18d;
  char local_18c;
  char local_18b;
  float local_180;
  float local_17c;
  undefined8 local_178;
  undefined8 uStack_170;
  float local_160;
  float local_15c;
  float local_158;
  float local_154;
  undefined1 local_150 [16];
  double local_140;
  double local_138;
  undefined1 local_108 [16];
  undefined4 local_f8;
  char *local_f0;
  undefined1 local_c8 [12];
  undefined1 local_b8 [8];
  undefined8 local_b0;
  undefined8 local_a8;
  undefined8 local_a0;
  undefined8 local_98;
  undefined8 local_90;
  undefined8 local_88;
  undefined4 local_80;
  undefined1 local_78 [16];
  float local_68;
  float local_64;
  undefined8 local_60;
  float afStack_58 [6];
  float local_40;
  float local_3c;
  long local_38;
  undefined1 extraout_var [56];
  undefined1 extraout_var_00 [56];
  undefined1 extraout_var_01 [56];
  undefined1 extraout_var_02 [56];
  
  local_38 = *DAT_01a1f100;
  uVar33 = FUN_009230f0();
  local_178 = 0;
  if (*(char *)(param_5 + 0x2a0) == '\0') {
    FUN_00928520(local_228,param_4);
    pfVar41 = (float *)&local_178;
    FUN_00926320(param_4,param_5 + 0x2a2,pfVar41);
    uVar55 = local_178;
    if ((local_190 & 0xfffd) == 1) {
      local_178 = uStack_170;
      uStack_170 = uVar55;
      uVar51 = *(undefined4 *)(param_5 + 0x2ac);
      *(undefined4 *)(param_5 + 0x2ac) = *(undefined4 *)(param_5 + 0x2b0);
      *(undefined4 *)(param_5 + 0x2b0) = uVar51;
    }
    if ((local_190 & 0xfffe) == 2) {
      fVar52 = *(float *)(param_5 + 0x2ac);
      fVar54 = *(float *)(param_5 + 0x2b0);
      uVar35 = 2;
      uVar44 = 2;
      if (0.0 <= local_178._4_4_) {
        uVar44 = 0;
      }
      if (0.0 <= uStack_170._4_4_) {
        uVar35 = 0;
      }
      auVar56._4_12_ = auRam000000000166b594;
      auVar56._0_4_ = DAT_0166b590;
      auVar56 = vandps_avx(ZEXT416((uint)(fVar52 - *(float *)(&DAT_0166b6a0 +
                                                             (uVar44 | (float)local_178 < 0.0) * 4))
                                  ),auVar56);
      fVar66 = auVar56._0_4_;
      auVar59._0_4_ = *(float *)(&DAT_0166b6a0 + (uVar35 | (float)uStack_170 < 0.0) * 4);
      fVar49 = (float)FUN_000aa520(&local_178);
      fVar50 = (float)FUN_000aa520(&uStack_170);
      if (DAT_0166b6b0 <= fVar66) {
        auVar56 = vandps_avx(ZEXT416((uint)local_178._4_4_),ZEXT416(DAT_0166b590));
        auVar7 = vandps_avx(ZEXT416((uint)(float)local_178),ZEXT416(DAT_0166b590));
        if (auVar56._0_4_ < auVar7._0_4_) {
          fVar75 = 0.0;
          fVar52 = *(float *)(&DAT_0166b7c4 + (ulong)((float)local_178 < 0.0) * 4);
          goto LAB_0091b807;
        }
        fVar52 = 0.0;
        fVar75 = fVar49 * *(float *)(&DAT_0166b7c4 + (ulong)(local_178._4_4_ < 0.0) * 4);
LAB_0091b8a7:
        fVar66 = fVar52;
      }
      else {
        auVar7._4_12_ = auRam000000000166b594;
        auVar7._0_4_ = DAT_0166b590;
        auVar56 = vandps_avx(ZEXT416((uint)fVar52),auVar7);
        if ((auVar56._0_4_ < DAT_0166b6b4) || (DAT_0166b6b8 < auVar56._0_4_)) {
          fVar52 = DAT_0166b6c0;
          if ((float)local_178 < 0.0) {
            fVar52 = DAT_0166b6bc;
          }
          fVar75 = DAT_0166b6c0;
          if (local_178._4_4_ < 0.0) {
            fVar75 = DAT_0166b6bc;
          }
          fVar75 = (fVar66 / DAT_0166b6c4 + DAT_0166b6c0) * fVar49 * fVar75;
LAB_0091b807:
          fVar52 = fVar49 * fVar52;
        }
        else {
          fVar75 = DAT_0166b6c0;
          if (local_178._4_4_ < 0.0) {
            fVar75 = DAT_0166b6bc;
          }
          fVar75 = fVar49 * fVar75;
          fVar52 = DAT_0166b6c0;
          if ((float)local_178 < 0.0) {
            fVar52 = DAT_0166b6bc;
          }
          fVar52 = (fVar66 / DAT_0166b6c4 + DAT_0166b6c0) * fVar49 * fVar52;
        }
        if (((fVar52 <= DAT_0166b6bc) || (fVar66 = DAT_0166b6c0, fVar52 < DAT_0166b6c0)) &&
           (fVar66 = DAT_0166b6bc, DAT_0166b6bc < fVar52)) goto LAB_0091b8a7;
      }
      if (((fVar75 <= DAT_0166b6bc) || (fVar52 = DAT_0166b6c0, fVar75 < DAT_0166b6c0)) &&
         (fVar52 = DAT_0166b6bc, DAT_0166b6bc < fVar75)) {
        fVar52 = fVar75;
      }
      auVar8._4_12_ = auRam000000000166b594;
      auVar8._0_4_ = DAT_0166b590;
      auVar56 = vandps_avx(ZEXT416((uint)(fVar54 - auVar59._0_4_)),auVar8);
      auVar59._0_4_ = auVar56._0_4_;
      if (DAT_0166b6c8 <= auVar59._0_4_) {
        auVar56 = vandps_avx(ZEXT416((uint)uStack_170._4_4_),ZEXT416(DAT_0166b590));
        auVar59 = vandps_avx(ZEXT416((uint)(float)uStack_170),ZEXT416(DAT_0166b590));
        if (auVar56._0_4_ < auVar59._0_4_) {
          fVar49 = 0.0;
          fVar54 = *(float *)(&DAT_0166b7c4 + (ulong)((float)uStack_170 < 0.0) * 4);
          goto LAB_0091ba29;
        }
        fVar54 = 0.0;
        fVar49 = fVar50 * *(float *)(&DAT_0166b7c4 + (ulong)(uStack_170._4_4_ < 0.0) * 4);
LAB_0091bac7:
        auVar59._0_4_ = fVar54;
      }
      else {
        auVar9._4_12_ = auRam000000000166b594;
        auVar9._0_4_ = DAT_0166b590;
        auVar56 = vandps_avx(ZEXT416((uint)fVar54),auVar9);
        if ((auVar56._0_4_ < DAT_0166b6b4) || (DAT_0166b6b8 < auVar56._0_4_)) {
          fVar54 = DAT_0166b6c0;
          if ((float)uStack_170 < 0.0) {
            fVar54 = DAT_0166b6bc;
          }
          fVar49 = DAT_0166b6c0;
          if (uStack_170._4_4_ < 0.0) {
            fVar49 = DAT_0166b6bc;
          }
          fVar49 = (auVar59._0_4_ / DAT_0166b6c4 + DAT_0166b6c0) * fVar50 * fVar49;
LAB_0091ba29:
          fVar54 = fVar50 * fVar54;
        }
        else {
          fVar49 = DAT_0166b6c0;
          if (uStack_170._4_4_ < 0.0) {
            fVar49 = DAT_0166b6bc;
          }
          fVar49 = fVar50 * fVar49;
          fVar54 = DAT_0166b6c0;
          if ((float)uStack_170 < 0.0) {
            fVar54 = DAT_0166b6bc;
          }
          fVar54 = (auVar59._0_4_ / DAT_0166b6c4 + DAT_0166b6c0) * fVar50 * fVar54;
        }
        if (((fVar54 <= DAT_0166b6bc) || (auVar59._0_4_ = DAT_0166b6c0, fVar54 < DAT_0166b6c0)) &&
           (auVar59._0_4_ = DAT_0166b6bc, DAT_0166b6bc < fVar54)) goto LAB_0091bac7;
      }
      if (((fVar49 <= DAT_0166b6bc) || (fVar54 = DAT_0166b6c0, fVar49 < DAT_0166b6c0)) &&
         (fVar54 = DAT_0166b6bc, DAT_0166b6bc < fVar49)) {
        fVar54 = fVar49;
      }
      local_178 = CONCAT44(fVar52,auVar59._0_4_);
      uStack_170 = CONCAT44(fVar54,fVar66);
      uVar51 = thunk_FUN_012aaf86(fVar52);
      *(undefined4 *)(param_5 + 0x2ac) = uVar51;
      uVar51 = thunk_FUN_012aaf86(fVar54,fVar66);
      *(undefined4 *)(param_5 + 0x2b0) = uVar51;
    }
    uVar35 = 0;
    do {
      uVar51 = *(undefined4 *)(param_5 + 0x2ac + uVar35 * 4);
      FUN_000aa760(*pfVar41,pfVar41[1],pfVar41);
      local_f8 = 0xffffffff;
      local_f0 = (char *)0x0;
      local_108 = ZEXT816(0);
      cVar25 = FUN_00920990(param_3,param_4,uVar35 & 0xffffffff,local_108);
      if (cVar25 != '\0') {
        if (local_108._0_8_ == 0) {
          lVar36 = *(long *)((long)local_f0 + 0x130);
          if (lVar36 != 0) {
            lVar47 = (long)local_f0 + 0x130;
LAB_0091bc51:
            if (lVar47 + lVar36 != 0) {
              auVar56 = ZEXT416((uint)(*pfVar41 * *pfVar41 + pfVar41[1] * pfVar41[1]));
              auVar56 = vsqrtss_avx(auVar56,auVar56);
              fVar52 = (float)FUN_00239650(auVar56._0_8_,lVar47 + lVar36 + 8);
              if (fVar52 + DAT_0166b6c0 < DAT_0166b6ec) {
                fVar52 = DAT_0166b6bc;
              }
              fVar54 = DAT_0166b6c0;
              if (fVar52 + DAT_0166b6bc < DAT_0166b6ec) {
                fVar54 = fVar52;
              }
              fVar52 = (float)thunk_FUN_012aaa36(uVar51,1,0);
              *pfVar41 = fVar52 * fVar54;
              fVar52 = (float)thunk_FUN_012aaa36(uVar51,0,0);
              pfVar41[1] = fVar52 * fVar54;
            }
          }
        }
        else {
          lVar47 = *(long *)(local_108._0_8_ + 0x38);
          if (lVar47 != 0) {
            lVar36 = local_108._0_8_ + 0x38;
            goto LAB_0091bc51;
          }
        }
      }
      local_f8 = 0xffffffff;
      local_f0 = (char *)0x0;
      local_108 = ZEXT816(0);
      cVar25 = FUN_00920990(param_3,param_4,uVar35 & 0xffffffff,local_108);
      if (cVar25 == '\0') {
        fVar52 = *pfVar41;
LAB_0091bd95:
        auVar56 = vandps_avx(ZEXT416((uint)fVar52),ZEXT416(DAT_0166b590));
        auVar59._0_4_ = auVar56._0_4_;
        fVar54 = DAT_0166b6c0;
        if (DAT_0166b6cc < auVar59._0_4_) {
          auVar56 = vandps_avx(ZEXT416((uint)pfVar41[1]),ZEXT416(DAT_0166b590));
          fVar66 = auVar56._0_4_;
          if (DAT_0166b6cc < fVar66) {
            if (auVar59._0_4_ <= fVar66) {
              fVar54 = auVar59._0_4_ / fVar66;
              auVar59._0_4_ = DAT_0166b6c0;
            }
            else {
              auVar59._0_4_ = fVar66 / auVar59._0_4_;
            }
            auVar56 = vsqrtss_avx(ZEXT416((uint)fVar52),
                                  ZEXT416((uint)(auVar59._0_4_ * auVar59._0_4_ + fVar54 * fVar54)));
            fVar54 = auVar56._0_4_;
          }
        }
        fVar52 = fVar52 * fVar54;
        if (((fVar52 <= DAT_0166b6bc) || (auVar59._0_4_ = DAT_0166b6c0, fVar52 < DAT_0166b6c0)) &&
           (auVar59._0_4_ = DAT_0166b6bc, DAT_0166b6bc < fVar52)) {
          auVar59._0_4_ = fVar52;
        }
        *pfVar41 = auVar59._0_4_;
        fVar54 = fVar54 * pfVar41[1];
        if ((fVar54 <= DAT_0166b6bc) || (fVar54 < DAT_0166b6c0)) {
          fVar52 = DAT_0166b6bc;
          if (DAT_0166b6bc < fVar54) {
            fVar52 = fVar54;
          }
          pfVar41[1] = fVar52;
        }
        else {
          pfVar41[1] = DAT_0166b6c0;
        }
      }
      else {
        pcVar40 = (char *)local_108._0_8_;
        if ((char *)local_108._0_8_ == (char *)0x0) {
          pcVar40 = local_f0;
        }
        fVar52 = *pfVar41;
        if (*pcVar40 == '\x02') goto LAB_0091bd95;
        FUN_000aa760(fVar52,pfVar41[1],pfVar41);
      }
      uVar43 = DAT_0166b5a0;
      pfVar41 = pfVar41 + 2;
      uVar35 = uVar35 + 1;
    } while ((int)uVar35 != 2);
    *(uint *)(param_5 + 0x2c4) = DAT_0166b5a0 ^ (uint)(float)local_178;
    *(float *)(param_5 + 0x2c0) = local_178._4_4_;
    uVar53 = (uint)(float)uStack_170 ^ uVar43;
    *(uint *)(param_5 + 0x2cc) = uVar53;
    *(uint *)(param_5 + 0x2d4) = (uint)uStack_170._4_4_ ^ uVar43;
    uVar55 = *(undefined8 *)(param_5 + 0x2d0);
    *(undefined8 *)(param_5 + 0x2d8) = uVar55;
    if (local_18d != '\0') {
      uVar43 = (uint)uVar55 ^ 0x80000000;
      *(uint *)(param_5 + 0x2d0) = uVar43;
      *(float *)(param_5 + 0x2d4) = uStack_170._4_4_;
      *(uint *)(param_5 + 0x2d8) = uVar43;
      *(uint *)(param_5 + 0x2dc) = (uint)((ulong)uVar55 >> 0x20) ^ 0x80000000;
    }
    if (local_18c == '\0') {
      cVar25 = FUN_000014d0();
      if (cVar25 != '\0') {
        uVar53 = *(uint *)(param_5 + 0x2cc);
        goto LAB_0091bf70;
      }
    }
    else {
LAB_0091bf70:
      uVar43 = DAT_0166b5a0;
      *(uint *)(param_5 + 0x2c8) = *(uint *)(param_5 + 0x2c8) ^ DAT_0166b5a0;
      *(uint *)(param_5 + 0x2cc) = uVar53 ^ uVar43;
    }
    uVar43 = DAT_0166b5a0;
    if (local_18b != '\0') {
      *(uint *)(param_5 + 0x2d8) = *(uint *)(param_5 + 0x2d8) ^ DAT_0166b5a0;
      *(uint *)(param_5 + 0x2dc) = *(uint *)(param_5 + 0x2dc) ^ uVar43;
    }
  }
  bVar26 = FUN_00900ad0(param_2,param_3,&local_180,&local_2a0,local_238);
  bVar45 = 0;
  if (((*param_6 != -1) && (*(short *)((long)param_6 + 0x4e) != -1)) &&
     (uVar35 = FUN_00743be0(), (uVar35 & 1) != 0)) {
    fVar52 = *(float *)(param_5 + 0x2b4) * DAT_0166b6d0;
    if ((uVar35 & 0x100) != 0) {
      fVar52 = fVar52 + *(float *)(param_5 + 700);
    }
    auVar57 = ZEXT416((uint)fVar52);
    if ((uVar35 & 0x10000) != 0) {
      auVar57._0_4_ = (uint)fVar52 ^ DAT_0166b5a0;
      auVar57._4_4_ = uRam000000000166b5a4;
      auVar57._8_4_ = uRam000000000166b5a8;
      auVar57._12_4_ = uRam000000000166b5ac;
    }
    auVar10._4_12_ = auRam000000000166b594;
    auVar10._0_4_ = DAT_0166b590;
    auVar56 = vandps_avx(auVar57,auVar10);
    fVar52 = auVar56._0_4_ + DAT_0166b6d4;
    if (fVar52 < 0.0) {
      fVar52 = 0.0;
    }
    auVar59._0_4_ = (float)(uVar35 >> 0x20) * DAT_0166b6d8;
    fVar54 = *(float *)(param_5 + 0x2b8);
    fVar49 = auVar57._0_4_;
    fVar66 = DAT_0166b6c0;
    if (0.0 <= fVar49) {
      if (fVar49 <= DAT_0166b6dc) {
        fVar66 = (float)((uint)fVar49 ^ DAT_0166b5a0);
        goto LAB_0091c0e0;
      }
    }
    else {
LAB_0091c0e0:
      fVar66 = (float)((uint)fVar66 ^ DAT_0166b5a0);
    }
    auVar11._4_12_ = auRam000000000166b594;
    auVar11._0_4_ = DAT_0166b590;
    auVar56 = vandps_avx(ZEXT416((uint)fVar54),auVar11);
    fVar49 = auVar56._0_4_ + DAT_0166b6d4;
    if (fVar49 < 0.0) {
      fVar49 = 0.0;
    }
    fVar52 = fVar52 * fVar66;
    fVar66 = DAT_0166b6c0;
    if (0.0 <= fVar54) {
      if (fVar54 <= DAT_0166b6dc) {
        fVar66 = (float)((uint)fVar54 ^ DAT_0166b5a0);
        goto LAB_0091c14a;
      }
    }
    else {
LAB_0091c14a:
      fVar66 = (float)((uint)fVar66 ^ DAT_0166b5a0);
    }
    uVar55 = FUN_000aa520(&uStack_170);
    fVar54 = (float)FUN_00091690(DAT_0166b6e0,DAT_0166b6c0,DAT_0166b6c0,DAT_0166b6e0,uVar55);
    local_108._0_4_ = 0x3f800000;
    local_140 = (double)CONCAT44(local_140._4_4_,0x3f800000);
    FUN_00bd3a50(*param_6,local_108,&local_140);
    fVar50 = (float)FUN_00bd3740(*param_6,(int)*(short *)((long)param_6 + 0x4e));
    bVar45 = 1;
    local_180 = fVar54 * auVar59._0_4_ * fVar52 * ((float)local_108._0_4_ / fVar50) + local_180;
    local_17c = fVar54 * auVar59._0_4_ * fVar49 * fVar66 * (local_140._0_4_ / fVar50) + local_17c;
    if ((fVar52 == 0.0) && (!NAN(fVar52))) {
      auVar56 = vcmpss_avx(ZEXT416((uint)(fVar49 * fVar66)),ZEXT816(0) << 0x40,4);
      bVar45 = auVar56[0] & 1;
    }
  }
  iVar34 = -1;
  local_2c8._8_8_ = 0;
  local_2c8._0_8_ = local_2a0;
  if (*param_6 != -1) {
    iVar34 = FUN_00bd3540();
  }
  auVar56 = vpshufd_avx(local_2c8,1);
  local_2c8._0_4_ = (undefined4)local_2a0;
  if (((auVar56._0_4_ != 0.0) || ((float)local_2c8._0_4_ != 0.0)) ||
     ((NAN((float)local_2c8._0_4_) || (cVar25 = FUN_00bc9890(iVar34), cVar25 != '\0')))) {
    if (iVar34 == -1) {
      param_6[0x36] = 0;
      param_6[0x37] = 0;
LAB_0091c36a:
      param_6[0x34] = 0;
      param_6[0x35] = 0;
    }
    else {
      FUN_00bc9960(iVar34,param_6 + 0x36,param_6 + 0x37);
      if (((float)param_6[0x36] <= 0.0) || ((float)param_6[0x37] <= 0.0)) goto LAB_0091c36a;
      param_6[0x34] = (int)(auVar56._0_4_ + (float)param_6[0x34]);
      param_6[0x35] = (int)((float)local_2c8._0_4_ * DAT_0166b6e0 + (float)param_6[0x35]);
    }
    bVar28 = 0;
  }
  else {
    auVar56 = ZEXT416((uint)((float)param_6[0x34] * (float)param_6[0x34] +
                            (float)param_6[0x35] * (float)param_6[0x35]));
    auVar56 = vsqrtss_avx(auVar56,auVar56);
    fVar52 = auVar56._0_4_;
    if (*param_6 != -1) {
      FUN_00bd36a0();
    }
    auVar62._0_8_ = FUN_000915e0(param_6[0x36],param_6[0x37]);
    auVar62._8_56_ = extraout_var;
    if ((fVar52 <= DAT_0166b6cc) || (fVar54 = (float)auVar62._0_8_, fVar54 <= 0.0)) {
      param_6[0x34] = 0;
      param_6[0x35] = 0;
      bVar28 = 0;
    }
    else {
      if (fVar52 <= DAT_0166b6e4) {
        auVar77._0_4_ = fVar54 / DAT_0166b6e4;
        auVar77._4_12_ = auVar62._4_12_;
        fVar54 = (float)FUN_00091710(fVar52,0,auVar77._0_8_,param_2);
      }
      else {
        fVar54 = (float)FUN_000915f0(fVar52,0,fVar54 * param_2);
      }
      fVar54 = fVar54 / fVar52;
      bVar28 = 1;
      local_17c = local_17c - (float)param_6[0x34] * (DAT_0166b6c0 - fVar54);
      local_180 = local_180 - (DAT_0166b6c0 - fVar54) * (float)param_6[0x35];
      param_6[0x34] = (int)(fVar54 * (float)param_6[0x34]);
      param_6[0x35] = (int)(fVar54 * (float)param_6[0x35]);
    }
  }
  bVar28 = bVar26 | bVar45 | bVar28;
  uVar51 = 0xffffffff;
  if (*param_6 != -1) {
    uVar51 = FUN_00bd3540();
  }
  cVar25 = FUN_00bc99e0(uVar51,local_2b8);
  FUN_00928590(param_4,local_230);
  FUN_0091da30(uVar33,bVar28,local_238,local_230,param_5,param_6,param_7);
  lVar36 = FUN_00526f80();
  lVar47 = DAT_0273eb28;
  uVar33 = FUN_009230f0(param_3);
  if (param_4 < 4) {
    lVar46 = (long)param_3 * 0x1a0;
    puVar1 = (uint *)(lVar47 + 0x20 + lVar46);
    lVar37 = FUN_00928560();
    if (((*(byte *)(DAT_0273eb28 + 0xc) & 1) == 0) && (cVar27 = FUN_00591b30(), cVar27 == '\0')) {
      FUN_00928670(param_1,lVar37,local_230,0,&local_40);
      if (*(char *)(lVar37 + 0x2a0) == '\0') {
        lVar39 = FUN_00928560(param_4);
        fVar52 = extraout_XMM1_Da;
        fVar54 = extraout_XMM0_Da;
        if (lVar39 != 0) {
          lVar48 = 0;
          uVar35 = 0;
          do {
            *(undefined4 *)((long)afStack_58 + lVar48) = 0x3f800000;
            *(undefined4 *)((long)afStack_58 + lVar48 + 4) = 0x3f800000;
            local_f8 = 0xffffffff;
            local_f0 = (char *)0x0;
            local_108 = ZEXT816(0);
            cVar27 = FUN_00920990(param_3,param_4,uVar35 & 0xffffffff,local_108);
            if (cVar27 != '\0') {
              auVar65._0_8_ = FUN_0091acb0(local_108);
              auVar65._8_56_ = extraout_var_02;
              pcVar40 = (char *)local_108._0_8_;
              if ((char *)local_108._0_8_ == (char *)0x0) {
                pcVar40 = local_f0;
              }
              cVar27 = *pcVar40;
              fVar52 = (float)auVar65._0_8_;
              auVar56 = auVar65._0_16_;
              if (((fVar52 <= DAT_0166b6cc) &&
                  (auVar59 = vpshufd_avx(auVar56,1), auVar59._0_4_ <= DAT_0166b6cc)) ||
                 (cVar27 == '\0')) {
                *(undefined8 *)(lVar39 + 0x2e0 + lVar48) = 0;
                *(undefined4 *)(lVar39 + 0x2f0 + lVar48) = 0;
                *(undefined4 *)(lVar39 + 0x2f4 + lVar48) = 0;
              }
              else {
                uVar55 = FUN_0091abd0(local_108);
                pfVar41 = (float *)local_108._8_8_;
                if ((float *)local_108._8_8_ == (float *)0x0) {
                  pcVar40 = (char *)local_108._0_8_;
                  if ((char *)local_108._0_8_ == (char *)0x0) {
                    pcVar40 = local_f0;
                  }
                  pfVar41 = (float *)(pcVar40 + 4);
                }
                fVar54 = *pfVar41;
                auVar59._0_4_ = *(float *)((long)&local_178 + lVar48);
                local_2e0 = (double)auVar59._0_4_;
                local_140 = local_2e0;
                fVar66 = *(float *)((long)&local_178 + lVar48 + 4);
                dVar83 = (double)fVar66;
                local_138 = dVar83;
                if (fVar66 < 0.0) {
                  dVar83 = (double)((ulong)dVar83 ^ _DAT_0166b5b0);
                }
                local_2f8 = (float)uVar55;
                if (auVar59._0_4_ < 0.0) {
                  local_2e0 = (double)((ulong)local_2e0 ^ _DAT_0166b5b0);
                }
                if (cVar27 == '\x02') {
                  fVar66 = *(float *)(lVar39 + 0x2f0 + lVar48);
                  auVar23._8_8_ = extraout_XMM0_Qb;
                  auVar23._0_8_ = uVar55;
                  fVar49 = DAT_0166b6c0;
                  if (0.0 <= auVar59._0_4_) {
                    if (auVar59._0_4_ <= DAT_0166b6dc) {
                      fVar49 = (float)((uint)auVar59._0_4_ ^ DAT_0166b5a0);
                      goto LAB_0091c9e8;
                    }
                  }
                  else {
LAB_0091c9e8:
                    fVar49 = (float)((uint)fVar49 ^ DAT_0166b5a0);
                  }
                  if ((fVar66 != (float)((uint)fVar49 ^ DAT_0166b5a0)) ||
                     (NAN(fVar66) || NAN((float)((uint)fVar49 ^ DAT_0166b5a0)))) {
                    pfVar41 = (float *)(lVar39 + 0x2e0 + lVar48);
                    auVar20._4_12_ = auRam000000000166b594;
                    auVar20._0_4_ = DAT_0166b590;
                    auVar7 = vandps_avx(ZEXT416((uint)auVar59._0_4_),auVar20);
                    if (auVar7._0_4_ < fVar54) goto LAB_0091ca6b;
                    fVar66 = *(float *)(lVar39 + 0x2e0 + lVar48);
                    if (DAT_0166b6cc < local_2f8) {
                      auVar7 = vmaxss_avx(ZEXT416((uint)(fVar66 / local_2f8)),ZEXT816(0) << 0x40);
                      auVar7 = vminss_avx(auVar7,ZEXT416((uint)DAT_0166b6c0));
                      fVar52 = (fVar52 + DAT_0166b6bc) * auVar7._0_4_ + DAT_0166b6c0;
                    }
                    *(float *)((long)afStack_58 + lVar48) = fVar52;
                    *pfVar41 = fVar66 + param_1;
                    if (0.0 <= auVar59._0_4_) {
                      if (DAT_0166b6dc < auVar59._0_4_) {
                        auVar59._0_4_ = DAT_0166b6c0;
                      }
                    }
                    else {
                      auVar59._0_4_ = (float)((uint)DAT_0166b6c0 ^ DAT_0166b5a0);
                    }
                  }
                  else {
                    pfVar41 = (float *)(lVar39 + 0x2e0 + uVar35 * 8);
LAB_0091ca6b:
                    *pfVar41 = 0.0;
                    auVar59._0_4_ = 0.0;
                  }
                  *(float *)(lVar39 + 0x2f0 + lVar48) = auVar59._0_4_;
                  fVar52 = *(float *)(lVar39 + 0x2f4 + lVar48);
                  auVar59._0_4_ = *(float *)((long)&local_178 + lVar48 + 4);
                  fVar66 = DAT_0166b6c0;
                  if (0.0 <= auVar59._0_4_) {
                    if (auVar59._0_4_ <= DAT_0166b6dc) {
                      fVar66 = (float)((uint)auVar59._0_4_ ^ DAT_0166b5a0);
                      goto LAB_0091cd53;
                    }
                  }
                  else {
LAB_0091cd53:
                    fVar66 = (float)((uint)fVar66 ^ DAT_0166b5a0);
                  }
                  if ((fVar52 != (float)((uint)fVar66 ^ DAT_0166b5a0)) ||
                     (NAN(fVar52) || NAN((float)((uint)fVar66 ^ DAT_0166b5a0)))) {
                    pfVar41 = (float *)(lVar39 + 0x2e4 + lVar48);
                    auVar19._4_12_ = auRam000000000166b594;
                    auVar19._0_4_ = DAT_0166b590;
                    auVar7 = vandps_avx(ZEXT416((uint)auVar59._0_4_),auVar19);
                    if (fVar54 <= auVar7._0_4_) {
                      fVar52 = *(float *)(lVar39 + 0x2e4 + lVar48);
                      auVar56 = vpshufd_avx(auVar56,1);
                      fVar54 = auVar56._0_4_;
                      auVar56 = vpshufd_avx(auVar23,1);
                      if (DAT_0166b6cc < auVar56._0_4_) {
                        auVar56 = vmaxss_avx(ZEXT416((uint)(fVar52 / auVar56._0_4_)),
                                             ZEXT816(0) << 0x40);
                        auVar56 = vminss_avx(auVar56,ZEXT416((uint)DAT_0166b6c0));
                        fVar54 = (fVar54 + DAT_0166b6bc) * auVar56._0_4_ + DAT_0166b6c0;
                      }
                      *(float *)((long)afStack_58 + lVar48 + 4) = fVar54;
                      *pfVar41 = fVar52 + param_1;
                      fVar52 = DAT_0166b6c0;
                      if (0.0 <= auVar59._0_4_) {
                        if (DAT_0166b6dc < auVar59._0_4_) goto LAB_0091ce50;
LAB_0091ce40:
                        fVar52 = (float)((uint)auVar59._0_4_ ^ DAT_0166b5a0);
                      }
LAB_0091ce48:
                      fVar52 = (float)((uint)fVar52 ^ DAT_0166b5a0);
                      goto LAB_0091ce50;
                    }
                  }
                  else {
                    pfVar41 = (float *)(lVar39 + 0x2e4 + uVar35 * 8);
                  }
                  *pfVar41 = 0.0;
                  *(undefined4 *)(lVar39 + 0x2f4 + lVar48) = 0;
                }
                else {
                  auVar63._0_8_ = (double)FUN_000ab190(&local_140);
                  auVar63._8_56_ = extraout_var_00;
                  if (local_2e0 < dVar83) {
LAB_0091cab0:
                    *(undefined4 *)(lVar39 + 0x2e0 + lVar48) = 0;
                    fVar52 = 0.0;
                  }
                  else {
                    auVar59._0_4_ = *(float *)(lVar39 + 0x2f0 + lVar48);
                    auVar58._0_4_ = (float)auVar63._0_8_;
                    auVar58._4_12_ = auVar63._4_12_;
                    fVar66 = DAT_0166b6c0;
                    if (0.0 <= auVar58._0_4_) {
                      if (auVar58._0_4_ <= DAT_0166b6dc) {
                        fVar66 = (float)((uint)auVar58._0_4_ ^ DAT_0166b5a0);
                        goto LAB_0091ca82;
                      }
                    }
                    else {
LAB_0091ca82:
                      fVar66 = (float)((uint)fVar66 ^ DAT_0166b5a0);
                    }
                    if (((auVar59._0_4_ == (float)((uint)fVar66 ^ DAT_0166b5a0)) &&
                        (!NAN(auVar59._0_4_) && !NAN((float)((uint)fVar66 ^ DAT_0166b5a0)))) ||
                       (auVar21._4_12_ = auRam000000000166b594, auVar21._0_4_ = DAT_0166b590,
                       auVar59 = vandps_avx(auVar58,auVar21), auVar59._0_4_ < fVar54))
                    goto LAB_0091cab0;
                    auVar59._0_4_ = *(float *)(lVar39 + 0x2e0 + lVar48);
                    if (DAT_0166b6cc < local_2f8) {
                      auVar7 = vmaxss_avx(ZEXT416((uint)(auVar59._0_4_ / local_2f8)),ZEXT816(0));
                      auVar7 = vminss_avx(auVar7,ZEXT416((uint)DAT_0166b6c0));
                      fVar52 = (fVar52 + DAT_0166b6bc) * auVar7._0_4_ + DAT_0166b6c0;
                    }
                    *(float *)((long)afStack_58 + lVar48) = fVar52;
                    *(float *)(lVar39 + 0x2e0 + lVar48) = auVar59._0_4_ + param_1;
                    if (0.0 <= auVar58._0_4_) {
                      fVar52 = auVar58._0_4_;
                      if (DAT_0166b6dc < auVar58._0_4_) {
                        fVar52 = DAT_0166b6c0;
                      }
                    }
                    else {
                      fVar52 = (float)((uint)DAT_0166b6c0 ^ DAT_0166b5a0);
                    }
                  }
                  *(float *)(lVar39 + 0x2f0 + lVar48) = fVar52;
                  auVar64._0_8_ = (double)FUN_000ab190(&local_140);
                  auVar64._8_56_ = extraout_var_01;
                  if (dVar83 <= local_2e0) {
LAB_0091cbee:
                    *(undefined4 *)(lVar39 + 0x2e4 + lVar48) = 0;
                    *(undefined4 *)(lVar39 + 0x2f4 + lVar48) = 0;
                    goto LAB_0091cf5c;
                  }
                  fVar52 = *(float *)(lVar39 + 0x2f4 + lVar48);
                  auVar59._0_4_ = (float)auVar64._0_8_;
                  auVar59._4_12_ = auVar64._4_12_;
                  fVar66 = DAT_0166b6c0;
                  if (0.0 <= auVar59._0_4_) {
                    if (auVar59._0_4_ <= DAT_0166b6dc) {
                      fVar66 = (float)((uint)auVar59._0_4_ ^ DAT_0166b5a0);
                      goto LAB_0091cbc4;
                    }
                  }
                  else {
LAB_0091cbc4:
                    fVar66 = (float)((uint)fVar66 ^ DAT_0166b5a0);
                  }
                  if (((fVar52 == (float)((uint)fVar66 ^ DAT_0166b5a0)) &&
                      (!NAN(fVar52) && !NAN((float)((uint)fVar66 ^ DAT_0166b5a0)))) ||
                     (auVar22._4_12_ = auRam000000000166b594, auVar22._0_4_ = DAT_0166b590,
                     auVar7 = vandps_avx(auVar59,auVar22), auVar7._0_4_ < fVar54))
                  goto LAB_0091cbee;
                  fVar52 = *(float *)(lVar39 + 0x2e4 + lVar48);
                  auVar56 = vpshufd_avx(auVar56,1);
                  fVar54 = auVar56._0_4_;
                  auVar24._8_8_ = extraout_XMM0_Qb;
                  auVar24._0_8_ = uVar55;
                  auVar56 = vpshufd_avx(auVar24,1);
                  if (DAT_0166b6cc < auVar56._0_4_) {
                    auVar56 = vmaxss_avx(ZEXT416((uint)(fVar52 / auVar56._0_4_)),ZEXT816(0) << 0x40)
                    ;
                    auVar56 = vminss_avx(auVar56,ZEXT416((uint)DAT_0166b6c0));
                    fVar54 = (fVar54 + DAT_0166b6bc) * auVar56._0_4_ + DAT_0166b6c0;
                  }
                  *(float *)((long)afStack_58 + lVar48 + 4) = fVar54;
                  *(float *)(lVar39 + 0x2e4 + lVar48) = fVar52 + param_1;
                  fVar52 = DAT_0166b6c0;
                  if (auVar59._0_4_ < 0.0) goto LAB_0091ce48;
                  if (auVar59._0_4_ <= DAT_0166b6dc) goto LAB_0091ce40;
LAB_0091ce50:
                  *(float *)(lVar39 + 0x2f4 + lVar48) = fVar52;
                }
              }
            }
LAB_0091cf5c:
            uVar35 = uVar35 + 1;
            lVar48 = lVar48 + 8;
            fVar52 = afStack_58[2];
            fVar54 = afStack_58[3];
          } while ((int)lVar48 != 0x10);
        }
        local_40 = fVar52 * local_40;
        local_3c = fVar54 * local_3c;
        local_258 = 0;
        local_248 = 0xffffffff;
        local_240 = 0;
        local_250 = 0;
        cVar27 = FUN_00920990(param_3,param_4,1,&local_258);
        if (cVar27 != '\0') {
          if (local_250 == 0) {
            if (local_258 == 0) {
              puVar42 = (uint *)(local_240 + 0x128);
            }
            else {
              puVar42 = (uint *)(local_258 + 0x30);
            }
          }
          else {
            puVar42 = (uint *)(local_250 + 0x30);
          }
          uVar43 = *puVar42;
          auVar68._0_4_ = uVar43 ^ DAT_0166b5a0;
          auVar68._4_4_ = uRam000000000166b5a4;
          auVar68._8_4_ = uRam000000000166b5a8;
          auVar68._12_4_ = uRam000000000166b5ac;
          auVar56 = vmaxss_avx(ZEXT416((uint)local_40),auVar68);
          auVar56 = vminss_avx(auVar56,ZEXT416(uVar43));
          local_40 = auVar56._0_4_;
          auVar56 = vmaxss_avx(ZEXT416((uint)local_3c),auVar68);
          auVar56 = vminss_avx(auVar56,ZEXT416(uVar43));
          local_3c = auVar56._0_4_;
        }
      }
      cVar27 = FUN_008e3ae0(param_3);
      if (cVar27 == '\0') {
        cVar27 = FUN_008e3b10(param_3);
        uVar55 = FUN_00958d30();
        cVar29 = FUN_00959fc0(uVar55,param_4);
        cVar30 = FUN_009299b0();
        cVar31 = FUN_003f6ff0();
        if ((((cVar27 == '\0') && (cVar29 == '\0')) && (cVar30 == '\0')) &&
           ((cVar31 == '\0' && (bVar28 == 1)))) {
          FUN_00920b90(CONCAT44(uRam000000000166b5a4,(uint)local_180 ^ DAT_0166b5a0),local_17c,
                       param_1,param_3);
        }
      }
      if ((*puVar1 != 0xffffffff) && (sVar2 = *(short *)(lVar47 + 0x6e + lVar46), sVar2 != -1)) {
        fVar52 = (float)FUN_00bd3740(*puVar1,(int)sVar2);
        FUN_00bd3a50(*puVar1,&local_25c,&local_260);
        local_40 = (local_25c / fVar52) * local_40;
        local_3c = (local_260 / fVar52) * local_3c;
      }
      FUN_00914460(*(undefined4 *)(lVar47 + 0x3c + lVar46),*(undefined4 *)(lVar47 + 0x38 + lVar46),
                   uVar33,local_78);
      local_278._0_8_ = FUN_00090ae0(local_78);
      local_278._8_8_ = extraout_XMM0_Qb_00;
      if ((cVar25 != '\0') && (*puVar1 != 0xffffffff)) {
        FUN_008e7990(local_298,*puVar1,0);
        auVar59 = vandnps_avx(_DAT_01ac62b0,local_298[0]);
        auVar56 = vsubps_avx(ZEXT816(0) << 0x40,local_298[0]);
        auVar56 = vandps_avx(_DAT_01ac62b0,auVar56);
        auVar56 = vorps_avx(auVar59,auVar56);
        auVar84._0_4_ = local_278._0_4_ * auVar56._0_4_;
        auVar84._4_4_ = local_278._4_4_ * auVar56._4_4_;
        auVar84._8_4_ = local_278._8_4_ * auVar56._8_4_;
        auVar84._12_4_ = local_278._12_4_ * auVar56._12_4_;
        auVar7 = vpshufd_avx(auVar84,0x55);
        auVar8 = vpshufd_avx(auVar84,0);
        auVar59 = vpshufd_avx(auVar56,0xd2);
        auVar9 = vpshufd_avx(auVar84,0xaa);
        auVar57 = vpshufd_avx(local_278,0xc9);
        auVar88._0_4_ = auVar57._0_4_ * auVar59._0_4_;
        auVar88._4_4_ = auVar57._4_4_ * auVar59._4_4_;
        auVar88._8_4_ = auVar57._8_4_ * auVar59._8_4_;
        auVar88._12_4_ = auVar57._12_4_ * auVar59._12_4_;
        auVar59 = vpshufd_avx(auVar56,0xc9);
        auVar57 = vpshufd_avx(local_278,0xd2);
        auVar89._0_4_ = auVar57._0_4_ * auVar59._0_4_;
        auVar89._4_4_ = auVar57._4_4_ * auVar59._4_4_;
        auVar89._8_4_ = auVar57._8_4_ * auVar59._8_4_;
        auVar89._12_4_ = auVar57._12_4_ * auVar59._12_4_;
        auVar57 = vsubps_avx(auVar89,auVar88);
        auVar59 = vpshufd_avx(auVar56,0xff);
        fVar52 = auVar59._0_4_;
        auVar90._0_4_ = fVar52 * fVar52;
        fVar66 = auVar59._4_4_;
        auVar90._4_4_ = fVar66 * fVar66;
        fVar75 = auVar59._8_4_;
        auVar90._8_4_ = fVar75 * fVar75;
        fVar76 = auVar59._12_4_;
        auVar90._12_4_ = fVar76 * fVar76;
        auVar10 = vsubps_avx(auVar90,_DAT_01ac63c0);
        auVar59 = vpshufd_avx(local_298[0],0xff);
        fVar54 = auVar59._0_4_;
        auVar78._0_4_ = fVar54 * fVar54;
        fVar49 = auVar59._4_4_;
        auVar78._4_4_ = fVar49 * fVar49;
        fVar3 = auVar59._8_4_;
        auVar78._8_4_ = fVar3 * fVar3;
        fVar5 = auVar59._12_4_;
        auVar78._12_4_ = fVar5 * fVar5;
        auVar59 = vpshufd_avx(local_2b8,0xff);
        auVar91._0_4_ = auVar59._0_4_ * auVar59._0_4_;
        fVar50 = auVar59._4_4_;
        auVar91._4_4_ = fVar50 * fVar50;
        fVar4 = auVar59._8_4_;
        auVar91._8_4_ = fVar4 * fVar4;
        fVar6 = auVar59._12_4_;
        auVar91._12_4_ = fVar6 * fVar6;
        auVar11 = vsubps_avx(auVar91,_DAT_01ac63c0);
        auVar77 = vsubps_avx(auVar78,_DAT_01ac63c0);
        fVar52 = fVar52 * auVar57._0_4_ +
                 local_278._0_4_ * auVar10._0_4_ +
                 auVar56._0_4_ * (auVar9._0_4_ + auVar8._0_4_ + auVar7._0_4_);
        fVar66 = fVar66 * auVar57._4_4_ +
                 local_278._4_4_ * auVar10._4_4_ +
                 auVar56._4_4_ * (auVar9._4_4_ + auVar8._4_4_ + auVar7._4_4_);
        fVar75 = fVar75 * auVar57._8_4_ +
                 local_278._8_4_ * auVar10._8_4_ +
                 auVar56._8_4_ * (auVar9._8_4_ + auVar8._8_4_ + auVar7._8_4_);
        fVar76 = fVar76 * auVar57._12_4_ +
                 local_278._12_4_ * auVar10._12_4_ +
                 auVar56._12_4_ * (auVar9._12_4_ + auVar8._12_4_ + auVar7._12_4_);
        auVar69._0_4_ = fVar52 + fVar52;
        auVar69._4_4_ = fVar66 + fVar66;
        auVar69._8_4_ = fVar75 + fVar75;
        auVar69._12_4_ = fVar76 + fVar76;
        auVar56 = vandps_avx(auVar69,_DAT_0166b5c0);
        auVar85._0_4_ = local_2b8._0_4_ * auVar56._0_4_;
        auVar85._4_4_ = local_2b8._4_4_ * auVar56._4_4_;
        auVar85._8_4_ = local_2b8._8_4_ * auVar56._8_4_;
        auVar85._12_4_ = local_2b8._12_4_ * auVar56._12_4_;
        auVar7 = vpshufd_avx(auVar85,0x55);
        auVar8 = vpshufd_avx(auVar85,0);
        auVar9 = vpshufd_avx(local_2b8,0xd2);
        auVar57 = vpshufd_avx(auVar56,0xc9);
        auVar79._0_4_ = auVar9._0_4_ * auVar57._0_4_;
        auVar79._4_4_ = auVar9._4_4_ * auVar57._4_4_;
        auVar79._8_4_ = auVar9._8_4_ * auVar57._8_4_;
        auVar79._12_4_ = auVar9._12_4_ * auVar57._12_4_;
        auVar9 = vpshufd_avx(local_2b8,0xc9);
        auVar57 = vpshufd_avx(auVar56,0xd2);
        auVar70._0_4_ = auVar9._0_4_ * auVar57._0_4_;
        auVar70._4_4_ = auVar9._4_4_ * auVar57._4_4_;
        auVar70._8_4_ = auVar9._8_4_ * auVar57._8_4_;
        auVar70._12_4_ = auVar9._12_4_ * auVar57._12_4_;
        auVar58 = vsubps_avx(auVar70,auVar79);
        auVar9 = vpshufd_avx(auVar85,0xaa);
        auVar57 = vpshufd_avx(local_298[0],0xc9);
        auVar10 = vpshufd_avx(local_298[0],0xd2);
        fVar52 = auVar59._0_4_ * auVar58._0_4_ +
                 auVar11._0_4_ * auVar56._0_4_ +
                 local_2b8._0_4_ * (auVar9._0_4_ + auVar8._0_4_ + auVar7._0_4_);
        auVar59._0_4_ =
             fVar50 * auVar58._4_4_ +
             auVar11._4_4_ * auVar56._4_4_ +
             local_2b8._4_4_ * (auVar9._4_4_ + auVar8._4_4_ + auVar7._4_4_);
        fVar66 = fVar4 * auVar58._8_4_ +
                 auVar11._8_4_ * auVar56._8_4_ +
                 local_2b8._8_4_ * (auVar9._8_4_ + auVar8._8_4_ + auVar7._8_4_);
        fVar50 = fVar6 * auVar58._12_4_ +
                 auVar11._12_4_ * auVar56._12_4_ +
                 local_2b8._12_4_ * (auVar9._12_4_ + auVar8._12_4_ + auVar7._12_4_);
        auVar71._0_4_ = fVar52 + fVar52;
        auVar71._4_4_ = auVar59._0_4_ + auVar59._0_4_;
        auVar71._8_4_ = fVar66 + fVar66;
        auVar71._12_4_ = fVar50 + fVar50;
        auVar56 = vandps_avx(auVar71,_DAT_0166b5c0);
        auVar59 = vpshufd_avx(auVar56,0xc9);
        auVar80._0_4_ = auVar10._0_4_ * auVar59._0_4_;
        auVar80._4_4_ = auVar10._4_4_ * auVar59._4_4_;
        auVar80._8_4_ = auVar10._8_4_ * auVar59._8_4_;
        auVar80._12_4_ = auVar10._12_4_ * auVar59._12_4_;
        auVar59 = vpshufd_avx(auVar56,0xd2);
        auVar72._0_4_ = auVar57._0_4_ * auVar59._0_4_;
        auVar72._4_4_ = auVar57._4_4_ * auVar59._4_4_;
        auVar72._8_4_ = auVar57._8_4_ * auVar59._8_4_;
        auVar72._12_4_ = auVar57._12_4_ * auVar59._12_4_;
        auVar57 = vsubps_avx(auVar72,auVar80);
        auVar86._0_4_ = local_298[0]._0_4_ * auVar56._0_4_;
        auVar86._4_4_ = local_298[0]._4_4_ * auVar56._4_4_;
        auVar86._8_4_ = local_298[0]._8_4_ * auVar56._8_4_;
        auVar86._12_4_ = local_298[0]._12_4_ * auVar56._12_4_;
        auVar7 = vpshufd_avx(auVar86,0x55);
        auVar8 = vpshufd_avx(auVar86,0);
        auVar9 = vpshufd_avx(auVar86,0xaa);
        fVar52 = fVar54 * auVar57._0_4_ +
                 auVar77._0_4_ * auVar56._0_4_ +
                 local_298[0]._0_4_ * (auVar9._0_4_ + auVar8._0_4_ + auVar7._0_4_);
        fVar54 = fVar49 * auVar57._4_4_ +
                 auVar77._4_4_ * auVar56._4_4_ +
                 local_298[0]._4_4_ * (auVar9._4_4_ + auVar8._4_4_ + auVar7._4_4_);
        auVar59._0_4_ =
             fVar3 * auVar57._8_4_ +
             auVar77._8_4_ * auVar56._8_4_ +
             local_298[0]._8_4_ * (auVar9._8_4_ + auVar8._8_4_ + auVar7._8_4_);
        fVar66 = fVar5 * auVar57._12_4_ +
                 auVar77._12_4_ * auVar56._12_4_ +
                 local_298[0]._12_4_ * (auVar9._12_4_ + auVar8._12_4_ + auVar7._12_4_);
        auVar60._0_4_ = fVar52 + fVar52;
        auVar60._4_4_ = fVar54 + fVar54;
        auVar60._8_4_ = auVar59._0_4_ + auVar59._0_4_;
        auVar60._12_4_ = fVar66 + fVar66;
        auVar56 = vandps_avx(auVar60,_DAT_0166b5c0);
        fVar52 = auVar56._0_4_;
        auVar73._0_4_ = fVar52 * fVar52;
        auVar59._0_4_ = auVar56._4_4_;
        auVar73._4_4_ = auVar59._0_4_ * auVar59._0_4_;
        fVar49 = auVar56._8_4_;
        auVar73._8_4_ = fVar49 * fVar49;
        fVar75 = auVar56._12_4_;
        auVar73._12_4_ = fVar75 * fVar75;
        auVar56 = vpshufd_avx(auVar73,0x55);
        auVar7 = vpshufd_avx(auVar73,0);
        auVar8 = vpshufd_avx(auVar73,0xaa);
        auVar74._0_4_ = auVar8._0_4_ + auVar7._0_4_ + auVar56._0_4_;
        auVar74._4_4_ = auVar8._4_4_ + auVar7._4_4_ + auVar56._4_4_;
        auVar74._8_4_ = auVar8._8_4_ + auVar7._8_4_ + auVar56._8_4_;
        auVar74._12_4_ = auVar8._12_4_ + auVar7._12_4_ + auVar56._12_4_;
        auVar8 = vrsqrtps_avx(auVar74);
        fVar54 = auVar8._0_4_;
        fVar66 = auVar8._4_4_;
        fVar50 = auVar8._8_4_;
        fVar3 = auVar8._12_4_;
        auVar81._0_4_ = fVar54 * fVar54 * auVar74._0_4_ * (float)DAT_0166b5d0;
        auVar81._4_4_ = fVar66 * fVar66 * auVar74._4_4_ * DAT_0166b5d0._4_4_;
        auVar81._8_4_ = fVar50 * fVar50 * auVar74._8_4_ * DAT_0166b5d0._8_4_;
        auVar81._12_4_ = fVar3 * fVar3 * auVar74._12_4_ * DAT_0166b5d0._12_4_;
        auVar56 = vsubps_avx(_DAT_0166b5d0,auVar81);
        auVar82._0_4_ = fVar54 + fVar54 * auVar56._0_4_;
        auVar82._4_4_ = fVar66 + fVar66 * auVar56._4_4_;
        auVar82._8_4_ = fVar50 + fVar50 * auVar56._8_4_;
        auVar82._12_4_ = fVar3 + fVar3 * auVar56._12_4_;
        auVar7 = vcmpps_avx(auVar82,auVar82,0);
        auVar56 = vandps_avx(auVar7,auVar82);
        auVar7 = vandnps_avx(auVar7,auVar8);
        auVar56 = vorps_avx(auVar7,auVar56);
        auVar61._0_4_ = fVar52 * auVar56._0_4_;
        auVar61._4_4_ = auVar59._0_4_ * auVar56._4_4_;
        auVar61._8_4_ = fVar49 * auVar56._8_4_;
        auVar61._12_4_ = fVar75 * auVar56._12_4_;
        auVar56 = vcmpps_avx(auVar56,_DAT_0166b5e0,0);
        local_278 = vandnps_avx(auVar56,auVar61);
      }
      FUN_00901580(param_3,lVar47 + 0x30 + lVar46,1,local_278,&local_68,param_7 + 0xc,param_7 + 0x1c
                  );
      cVar25 = FUN_006167a0(*puVar1);
      if (cVar25 == '\0') {
        bVar32 = true;
        if ((float)local_60 <= 0.0) {
          bVar32 = 0.0 < local_60._4_4_;
        }
      }
      else {
        local_60 = 0;
        bVar32 = false;
      }
      *(bool *)(lVar47 + 0x160 + lVar46) = bVar32;
      if (((bVar32 != false) && (0.0 < param_1)) &&
         ((auVar15._4_12_ = auRam000000000166b594, auVar15._0_4_ = DAT_0166b590,
          auVar56 = vandps_avx(ZEXT416((uint)local_40),auVar15), DAT_0166b6cc < auVar56._0_4_ ||
          (((auVar16._4_12_ = auRam000000000166b594, auVar16._0_4_ = DAT_0166b590,
            auVar56 = vandps_avx(ZEXT416((uint)local_3c),auVar16), DAT_0166b6cc < auVar56._0_4_ ||
            (auVar17._4_12_ = auRam000000000166b594, auVar17._0_4_ = DAT_0166b590,
            auVar56 = vandps_avx(ZEXT416(*param_7),auVar17), DAT_0166b6cc < auVar56._0_4_)) ||
           (auVar18._4_12_ = auRam000000000166b594, auVar18._0_4_ = DAT_0166b590,
           auVar56 = vandps_avx(ZEXT416(param_7[1]),auVar18), DAT_0166b6cc < auVar56._0_4_)))))) {
        fVar52 = *(float *)(lVar36 + 0x1c0);
        fVar54 = *(float *)(lVar36 + 0x1c4);
        if (fVar54 < 0.0) {
          fVar54 = 0.0;
        }
        if (fVar52 < 0.0) {
          fVar52 = 0.0;
        }
        auVar59._0_4_ = DAT_0166b6c0;
        if (fVar52 + DAT_0166b6bc < 0.0) {
          auVar59._0_4_ = fVar52;
        }
        fVar52 = *(float *)(lVar36 + 0x1cc);
        fVar66 = (param_2 / param_1) * local_68;
        if (fVar52 + fVar66 < 0.0) {
          fVar66 = (float)((uint)fVar52 ^ DAT_0166b5a0);
        }
        fVar49 = DAT_0166b6c0;
        if (fVar54 + DAT_0166b6bc < 0.0) {
          fVar49 = fVar54;
        }
        fVar54 = *(float *)(lVar36 + 0x1d0);
        local_68 = fVar52;
        if (fVar66 - fVar52 < 0.0) {
          local_68 = fVar66;
        }
        auVar59._0_4_ = DAT_0166b6c0 - auVar59._0_4_ * (float)local_60;
        fVar52 = (param_2 / param_1) * local_64;
        if (fVar54 + fVar52 < 0.0) {
          fVar52 = (float)((uint)fVar54 ^ DAT_0166b5a0);
        }
        local_64 = fVar54;
        if (fVar52 - fVar54 < 0.0) {
          local_64 = fVar52;
        }
        local_40 = local_40 * auVar59._0_4_ + fVar49 * local_60._4_4_ * local_68;
        local_3c = local_3c * auVar59._0_4_ + fVar49 * local_60._4_4_ * local_64;
      }
      param_7[5] = (uint)(local_40 * param_1);
      param_7[6] = (uint)(local_3c * param_1);
      param_7[0xb] = *(uint *)(lVar37 + 0x2d4);
    }
    else {
      param_7[5] = 0;
      param_7[6] = 0;
      param_7[0xb] = 0;
    }
    if (*puVar1 != 0xffffffff) {
      cVar25 = FUN_00bcf9e0();
      if (cVar25 != '\0') {
        FUN_000ab3c0(param_7[6],param_7[5],local_b8);
        uVar43 = *puVar1;
        uVar53 = FUN_006ed8f0(uVar43);
        if (*(int *)((ulong)((uVar53 & 0x1fff) * DAT_02692230) + 0x44 + DAT_02692228) != -1) {
          uVar53 = FUN_006ed8f0(uVar43);
          uVar53 = FUN_006ed9f0(*(undefined4 *)
                                 ((ulong)((uVar53 & 0x1fff) * DAT_02692230) + 0x44 + DAT_02692228));
          uVar35 = (ulong)((uVar53 & 0x1fff) * DAT_02689800);
          uVar44 = (ulong)DAT_02689818;
          if ((((3U >> (*(byte *)(((uVar35 + DAT_026897f8) -
                                  (*(ulong *)(DAT_026897f8 + 8 + uVar35) & uVar44)) + 0x42) & 0x1f)
                & 1) != 0) &&
              (uVar35 = (ulong)((uVar43 & 0x1fff) * DAT_02689800),
              uVar35 = (ulong)((*(uint *)(((uVar35 + DAT_026897f8) -
                                          (*(ulong *)(DAT_026897f8 + 8 + uVar35) & uVar44)) + 0x68)
                               & 0x1fff) * DAT_02689800),
              uVar53 = *(uint *)(((uVar35 + DAT_026897f8) -
                                 (*(ulong *)(DAT_026897f8 + 8 + uVar35) & uVar44)) + 0x7a0),
              uVar53 != 0xffffffff)) &&
             ((uVar35 = (ulong)((uVar53 & 0x1fff) * DAT_02689800),
              lVar36 = FUN_00102980((DAT_026897f8 + uVar35) -
                                    (*(ulong *)(DAT_026897f8 + 8 + uVar35) & uVar44)),
              (*(byte *)(lVar36 + 0xba) & 8) != 0 &&
              (uVar53 = FUN_006ed8f0(uVar43),
              *(int *)((ulong)((uVar53 & 0x1fff) * DAT_02692230) + 0x40 + DAT_02692228) != -1)))) {
            uVar53 = FUN_006ed8f0(uVar43);
            uVar33 = FUN_006ed9f0(*(undefined4 *)
                                   ((ulong)((uVar53 & 0x1fff) * DAT_02692230) + 0x44 + DAT_02692228)
                                 );
            uVar53 = FUN_006ed8f0(uVar43);
            puVar38 = (undefined8 *)
                      FUN_00bcead0(uVar33,(int)*(short *)((ulong)((uVar53 & 0x1fff) * DAT_02692230)
                                                          + 0x40 + DAT_02692228));
            local_90 = puVar38[4];
            local_88 = puVar38[5];
            local_80 = *(undefined4 *)(puVar38 + 6);
            local_98 = puVar38[3];
            local_a0 = puVar38[2];
            local_b0 = *puVar38;
            local_a8 = puVar38[1];
            uVar43 = FUN_006ed8f0(uVar43);
            iVar34 = FUN_006ed9f0(*(undefined4 *)
                                   ((ulong)((uVar43 & 0x1fff) * DAT_02692230) + 0x44 + DAT_02692228)
                                 );
            if (iVar34 != -1) {
              if (iVar34 == *(int *)(lVar47 + 0x154 + lVar46)) {
                uVar43 = FUN_006ed8f0(*puVar1);
                auVar56 = *(undefined1 (*) [16])
                           ((ulong)((uVar43 & 0x1fff) * DAT_02692230) + 0xb0 + DAT_02692228);
                auVar7 = vpand_avx(auVar56,_DAT_0166b5c0);
                auVar8 = vpshufd_avx(auVar7,0);
                auVar56 = vpshufd_avx(auVar56,0xff);
                fVar52 = auVar56._0_4_;
                auVar87._0_4_ = fVar52 * fVar52;
                fVar54 = auVar56._4_4_;
                auVar87._4_4_ = fVar54 * fVar54;
                auVar59._0_4_ = auVar56._8_4_;
                auVar87._8_4_ = auVar59._0_4_ * auVar59._0_4_;
                fVar66 = auVar56._12_4_;
                auVar87._12_4_ = fVar66 * fVar66;
                auVar57 = vsubps_avx(auVar87,_DAT_01ac63c0);
                auVar56 = vpshufd_avx(auVar7,0xb);
                auVar9 = vpshufd_avx(auVar7,1);
                auVar56 = vinsertps_avx(auVar56,ZEXT416((uint)(0.0 - auVar9._0_4_)),0x20);
                auVar56 = vblendps_avx(auVar56,auVar7,8);
                fVar52 = auVar7._0_4_ * auVar8._0_4_ + auVar57._0_4_ + fVar52 * auVar56._0_4_;
                fVar54 = auVar7._4_4_ * auVar8._4_4_ + 0.0 + fVar54 * auVar56._4_4_;
                auVar59._0_4_ = auVar7._8_4_ * auVar8._8_4_ + 0.0 + auVar59._0_4_ * auVar56._8_4_;
                fVar66 = auVar7._12_4_ * auVar8._12_4_ + 0.0 + fVar66 * auVar56._12_4_;
                local_108._0_4_ = fVar52 + fVar52;
                local_108._4_4_ = fVar54 + fVar54;
                local_108._8_4_ = auVar59._0_4_ + auVar59._0_4_;
                local_108._12_4_ = fVar66 + fVar66;
                local_c8 = FUN_00090760(local_108);
                puVar38 = (undefined8 *)(lVar47 + 0x118 + lVar46);
                FUN_000a7520(puVar38,local_108);
                FUN_000a7d00(&local_b0,local_108,&local_140);
                FUN_000a8030(&local_140,local_c8,local_150);
                FUN_00090bc0(&local_158,local_150);
                FUN_00090bc0(&local_160,local_c8);
                fVar52 = DAT_0166b6e8;
                fVar54 = (float)thunk_FUN_012ab996(DAT_0166b6e8 + local_160);
                auVar59._0_4_ = (float)thunk_FUN_012ab996(fVar52 + local_158);
                auVar56 = vandps_avx(ZEXT416((uint)(auVar59._0_4_ - fVar54)),ZEXT416(DAT_0166b590));
                auVar7 = vandps_avx(ZEXT416((uint)(local_158 - local_160)),ZEXT416(DAT_0166b590));
                fVar52 = local_158 - local_160;
                if (auVar56._0_4_ <= auVar7._0_4_) {
                  fVar52 = auVar59._0_4_ - fVar54;
                }
                param_7[5] = (uint)(fVar52 + (float)param_7[5]);
                param_7[6] = (uint)((local_154 - local_15c) + (float)param_7[6]);
              }
              else {
                puVar38 = (undefined8 *)(lVar47 + 0x118 + lVar46);
              }
              *(undefined4 *)(puVar38 + 6) = local_80;
              puVar38[5] = local_88;
              puVar38[4] = local_90;
              puVar38[3] = local_98;
              puVar38[2] = local_a0;
              puVar38[1] = local_a8;
              *puVar38 = local_b0;
              *(int *)(lVar47 + 0x154 + lVar46) = iVar34;
              goto LAB_0091c6b7;
            }
          }
        }
        *(undefined4 *)(lVar47 + 0x154 + lVar46) = 0xffffffff;
      }
    }
  }
LAB_0091c6b7:
  fVar52 = (float)param_7[6];
  auVar12._4_12_ = auRam000000000166b594;
  auVar12._0_4_ = DAT_0166b590;
  auVar56 = vandps_avx(ZEXT416((uint)fVar52),auVar12);
  if (auVar56._0_4_ <= DAT_0166b6cc) goto LAB_0091d13d;
  fVar54 = (float)param_6[0x34];
  auVar13._4_12_ = auRam000000000166b594;
  auVar13._0_4_ = DAT_0166b590;
  auVar56 = vandps_avx(ZEXT416((uint)fVar54),auVar13);
  if (auVar56._0_4_ <= DAT_0166b6cc) goto LAB_0091d13d;
  auVar59._0_4_ = DAT_0166b6c0;
  if (0.0 <= fVar52) {
    if (fVar52 <= DAT_0166b6dc) {
      auVar59._0_4_ = (float)((uint)fVar52 ^ DAT_0166b5a0);
      goto LAB_0091d00e;
    }
  }
  else {
LAB_0091d00e:
    auVar59._0_4_ = (float)((uint)auVar59._0_4_ ^ DAT_0166b5a0);
  }
  fVar66 = DAT_0166b6c0;
  if (0.0 <= fVar54) {
    if (fVar54 <= DAT_0166b6dc) {
      fVar66 = (float)((uint)fVar54 ^ DAT_0166b5a0);
      goto LAB_0091d04a;
    }
  }
  else {
LAB_0091d04a:
    fVar66 = (float)((uint)fVar66 ^ DAT_0166b5a0);
  }
  if ((auVar59._0_4_ == fVar66) && (!NAN(auVar59._0_4_) && !NAN(fVar66))) {
    auVar59._0_4_ = (float)param_7[0xb];
    fVar66 = DAT_0166b6c0;
    if (0.0 <= auVar59._0_4_) {
      if (auVar59._0_4_ <= DAT_0166b6dc) {
        fVar66 = (float)((uint)auVar59._0_4_ ^ DAT_0166b5a0);
        goto LAB_0091d09c;
      }
    }
    else {
LAB_0091d09c:
      fVar66 = (float)((uint)fVar66 ^ DAT_0166b5a0);
    }
    auVar59._0_4_ = DAT_0166b6c0;
    if (0.0 <= fVar54) {
      if (fVar54 <= DAT_0166b6dc) {
        auVar59._0_4_ = (float)((uint)fVar54 ^ DAT_0166b5a0);
        goto LAB_0091d0d8;
      }
    }
    else {
LAB_0091d0d8:
      auVar59._0_4_ = (float)((uint)auVar59._0_4_ ^ DAT_0166b5a0);
    }
    if ((fVar66 == auVar59._0_4_) && (!NAN(fVar66) && !NAN(auVar59._0_4_))) {
      param_6[0x34] = 0;
      param_6[0x35] = 0;
      goto LAB_0091d13d;
    }
  }
  param_6[0x34] = (int)(fVar52 + fVar54);
  auVar14._4_12_ = auRam000000000166b594;
  auVar14._0_4_ = DAT_0166b590;
  auVar56 = vandps_avx(ZEXT416((uint)(fVar52 + fVar54)),auVar14);
  auVar67 = ZEXT416((uint)param_6[0x35]);
  fVar52 = auVar56._0_4_;
  if ((float)param_6[0x35] + fVar52 < 0.0) {
    auVar67._0_4_ = (uint)fVar52 ^ DAT_0166b5a0;
    auVar67._4_4_ = 0;
    auVar67._8_4_ = auVar56._8_4_ ^ uRam000000000166b5a8;
    auVar67._12_4_ = auVar56._12_4_ ^ uRam000000000166b5ac;
  }
  if (auVar67._0_4_ - fVar52 < 0.0) {
    auVar56 = auVar67;
  }
  param_6[0x35] = auVar56._0_4_;
LAB_0091d13d:
  *(uint *)(param_5 + 0x2c0) = *param_7;
  *(uint *)(param_5 + 0x2c4) = param_7[1];
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

