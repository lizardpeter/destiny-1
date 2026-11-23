
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

ulong FUN_007fc800(long *param_1,long param_2,long param_3,undefined8 param_4,undefined8 param_5,
                  long param_6)

{
  undefined1 (*pauVar1) [16];
  undefined4 uVar2;
  undefined4 uVar3;
  int iVar4;
  uint uVar5;
  float *pfVar6;
  long lVar7;
  float fVar8;
  float fVar9;
  float fVar10;
  float fVar11;
  float fVar12;
  float fVar13;
  float fVar14;
  float fVar15;
  undefined1 auVar16 [16];
  undefined8 uVar17;
  undefined8 uVar18;
  undefined8 uVar19;
  undefined8 uVar20;
  undefined8 uVar21;
  undefined8 uVar22;
  undefined8 uVar23;
  undefined1 auVar24 [16];
  char cVar25;
  uint uVar26;
  undefined8 *puVar27;
  undefined8 uVar28;
  ushort *puVar29;
  undefined8 uVar30;
  ulong uVar31;
  undefined *puVar32;
  long *plVar33;
  long lVar34;
  long lVar35;
  long lVar36;
  long lVar37;
  long lVar38;
  long lVar39;
  bool bVar40;
  float fVar41;
  float fVar51;
  ulong uVar52;
  undefined1 auVar53 [16];
  undefined1 auVar54 [16];
  undefined1 auVar55 [16];
  undefined1 auVar56 [16];
  undefined1 auVar57 [16];
  undefined1 auVar58 [16];
  undefined1 auVar59 [16];
  float fVar42;
  undefined1 auVar60 [16];
  undefined1 auVar61 [16];
  float fVar43;
  float fVar44;
  undefined4 uVar45;
  undefined1 auVar62 [16];
  float fVar46;
  float fVar47;
  undefined1 auVar63 [16];
  undefined1 auVar64 [16];
  undefined1 auVar65 [16];
  undefined1 auVar66 [16];
  float fVar48;
  float fVar49;
  float fVar50;
  undefined1 auVar67 [16];
  undefined1 auVar68 [16];
  undefined1 auVar69 [16];
  undefined1 auVar70 [16];
  undefined1 auVar71 [16];
  undefined1 auVar72 [64];
  undefined1 auVar73 [64];
  float fVar74;
  float fVar83;
  undefined1 auVar75 [16];
  undefined1 auVar76 [16];
  undefined1 auVar77 [16];
  undefined1 auVar78 [16];
  undefined1 auVar79 [16];
  undefined1 auVar80 [16];
  undefined1 auVar81 [16];
  undefined1 auVar82 [16];
  ulong uVar84;
  undefined1 auVar85 [16];
  undefined1 auVar86 [16];
  undefined1 auVar87 [16];
  undefined1 auVar88 [16];
  undefined1 auVar89 [16];
  undefined1 auVar90 [16];
  undefined1 auVar91 [16];
  undefined1 auVar92 [16];
  undefined1 auVar93 [16];
  undefined1 auVar94 [16];
  undefined1 auVar95 [16];
  undefined1 auVar96 [16];
  undefined1 auVar97 [16];
  undefined1 auVar98 [16];
  float fVar99;
  undefined1 auVar100 [16];
  undefined1 auVar101 [16];
  undefined1 auVar102 [16];
  undefined1 auVar103 [16];
  undefined1 auVar104 [16];
  float local_2c8;
  float fStack_2c4;
  float fStack_2c0;
  float fStack_2bc;
  undefined1 local_29d;
  float local_268;
  float local_1a8;
  float fStack_1a4;
  float fStack_1a0;
  float fStack_19c;
  float local_128;
  undefined8 local_108;
  undefined8 local_f8;
  undefined8 uStack_f0;
  undefined1 local_e8 [16];
  undefined8 local_d8;
  undefined8 uStack_d0;
  undefined8 local_c8;
  undefined8 uStack_c0;
  undefined1 local_b8 [16];
  undefined1 local_a8 [16];
  undefined8 local_98 [2];
  undefined1 local_88 [16];
  undefined8 local_78 [2];
  undefined1 local_68 [16];
  undefined8 local_58;
  undefined8 uStack_50;
  undefined8 local_48;
  undefined8 local_40;
  long local_38;
  undefined1 extraout_var [56];
  undefined1 extraout_var_00 [56];
  
  local_38 = *DAT_01a1f100;
  uVar26 = (int)*(uint *)(param_6 + 0x40) >> 0xd;
  lVar34 = (ulong)((uVar26 >> 0x12 | 0x3ff) & uVar26) * 0x40;
  pfVar6 = *(float **)(param_2 + 0x10);
  lVar7 = *param_1;
  lVar36 = param_1[8];
  lVar39 = *DAT_01a238a0;
  lVar38 = *(long *)(lVar39 + 0x10 + lVar34);
  uVar31 = (ulong)((*(uint *)(param_6 + 0x40) & 0x1fff) * *(int *)(lVar39 + 0x30 + lVar34));
  uVar26 = *(uint *)(lVar36 + 0x1fb84);
  lVar35 = 0;
  if (uVar26 != 0xffffffff) {
    lVar37 = (ulong)(((uint)((int)uVar26 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar26 >> 0xd) * 0x40;
    lVar35 = *(long *)(lVar39 + 0x10 + lVar37);
    uVar52 = (ulong)((uVar26 & 0x1fff) * *(int *)(lVar39 + 0x30 + lVar37));
    lVar35 = (lVar35 + uVar52) -
             ((long)*(int *)(lVar39 + 0x34 + lVar37) & *(ulong *)(lVar35 + 8 + uVar52));
  }
  lVar38 = (lVar38 + uVar31) -
           ((long)*(int *)(lVar39 + 0x34 + lVar34) & *(ulong *)(lVar38 + 8 + uVar31));
  lVar39 = *(long *)(lVar36 + 0x1fc50);
  iVar4 = *(int *)(param_6 + 0x48);
  local_128 = DAT_01660874;
  if (1 < iVar4 - 1U) {
    auVar103 = vsubps_avx(*(undefined1 (*) [16])(pfVar6 + 0xc),*(undefined1 (*) [16])(lVar39 + 0xd0)
                         );
    auVar53._0_4_ = auVar103._0_4_ * auVar103._0_4_;
    auVar53._4_4_ = auVar103._4_4_ * auVar103._4_4_;
    auVar53._8_4_ = auVar103._8_4_ * auVar103._8_4_;
    auVar53._12_4_ = auVar103._12_4_ * auVar103._12_4_;
    auVar103 = vpshufd_avx(auVar53,0x55);
    auVar104 = vpshufd_avx(auVar53,0);
    auVar53 = vpshufd_avx(auVar53,0xaa);
    auVar100._0_4_ = auVar53._0_4_ + auVar104._0_4_ + auVar103._0_4_;
    auVar100._4_4_ = auVar53._4_4_ + auVar104._4_4_ + auVar103._4_4_;
    auVar100._8_4_ = auVar53._8_4_ + auVar104._8_4_ + auVar103._8_4_;
    auVar100._12_4_ = auVar53._12_4_ + auVar104._12_4_ + auVar103._12_4_;
    fVar44 = *(float *)(lVar38 + 0x54) - *(float *)(lVar38 + 0x50);
    auVar103 = vrsqrtps_avx(auVar100);
    fVar41 = auVar103._0_4_;
    fVar42 = auVar103._4_4_;
    fVar83 = auVar103._8_4_;
    fVar43 = auVar103._12_4_;
    auVar104._0_4_ = fVar41 * fVar41 * auVar100._0_4_ * (float)DAT_01660eb0;
    auVar104._4_4_ = fVar42 * fVar42 * auVar100._4_4_ * DAT_01660eb0._4_4_;
    auVar104._8_4_ = fVar83 * fVar83 * auVar100._8_4_ * DAT_01660eb0._8_4_;
    auVar104._12_4_ = fVar43 * fVar43 * auVar100._12_4_ * DAT_01660eb0._12_4_;
    fVar51 = *(float *)(lVar38 + 0x4c) - *(float *)(lVar38 + 0x48);
    auVar104 = vsubps_avx(_DAT_01660eb0,auVar104);
    fVar74 = DAT_01660878;
    if (DAT_01660878 - fVar44 < 0.0) {
      fVar74 = fVar44;
    }
    fVar44 = DAT_01660878;
    if (DAT_01660878 - fVar51 < 0.0) {
      fVar44 = fVar51;
    }
    auVar70._0_4_ = fVar41 + fVar41 * auVar104._0_4_;
    auVar70._4_4_ = fVar42 + fVar42 * auVar104._4_4_;
    auVar70._8_4_ = fVar83 + fVar83 * auVar104._8_4_;
    auVar70._12_4_ = fVar43 + fVar43 * auVar104._12_4_;
    auVar53 = vcmpps_avx(auVar70,auVar70,0);
    auVar104 = vandps_avx(auVar53,auVar70);
    auVar103 = vandnps_avx(auVar53,auVar103);
    auVar103 = vorps_avx(auVar103,auVar104);
    auVar75._0_4_ = auVar100._0_4_ * auVar103._0_4_;
    auVar75._4_4_ = auVar100._4_4_ * auVar103._4_4_;
    auVar75._8_4_ = auVar100._8_4_ * auVar103._8_4_;
    auVar75._12_4_ = auVar100._12_4_ * auVar103._12_4_;
    auVar103 = vcmpps_avx(auVar103,_DAT_01660ec0,0);
    auVar103 = vandnps_avx(auVar103,auVar75);
    fVar44 = (auVar103._0_4_ - *(float *)(lVar38 + 0x48)) / fVar44;
    if (fVar44 < 0.0) {
      fVar44 = 0.0;
    }
    fVar41 = DAT_01660874;
    if (fVar44 + DAT_0166087c < 0.0) {
      fVar41 = fVar44;
    }
    fVar42 = DAT_01660874 - (auVar103._0_4_ - *(float *)(lVar38 + 0x50)) / fVar74;
    if (fVar42 < 0.0) {
      fVar42 = 0.0;
    }
    if (fVar42 + DAT_0166087c < 0.0) {
      local_128 = fVar42;
    }
    local_128 = local_128 * fVar41;
  }
  uVar31 = (ulong)(*(uint *)(*(long *)(lVar36 + 0x40) + (long)*(short *)(param_3 + 0x20) * 0x18) &
                  0x1fff);
  if (*(char *)(lVar36 + 0x18924) == '\0') {
    puVar32 = (undefined *)0x0;
    if (iVar4 == 2) goto LAB_007fd3f1;
  }
  else {
    puVar32 = (undefined *)0x0;
    if (iVar4 == 1) goto LAB_007fd3f1;
  }
  if ((*(uint *)(lVar39 + 0x110) & 0xfffffffd) == 0) {
    cVar25 = *(char *)(lVar38 + 8);
  }
  else {
    cVar25 = *(char *)(lVar38 + 9);
  }
  puVar32 = (undefined *)0x0;
  if ((cVar25 != '\0') && (puVar32 = (undefined *)0x0, 0.0 < local_128)) {
    if (*(int *)(lVar38 + 0x44) == 2) {
      local_29d = 0x8c;
    }
    else {
      local_29d = 0x82;
      if (*(int *)(lVar38 + 0x44) == 1) {
        local_29d = 0x83;
      }
    }
    auVar72._0_8_ = thunk_FUN_012ab9a6(*(float *)(lVar39 + 0x114) * DAT_01660880);
    auVar72._8_56_ = extraout_var;
    auVar76._0_4_ = (float)auVar72._0_8_ / DAT_026e6000;
    auVar76._4_12_ = auVar72._4_12_;
    auVar103 = vunpcklps_avx(auVar72._0_16_,auVar76);
    local_58 = auVar103._0_8_;
    uStack_50 = 0;
    if (iVar4 - 1U < 2) {
      fVar44 = *(float *)(lVar36 + 0x188f0);
      fVar51 = *(float *)(lVar36 + 0x188f4);
      fVar74 = *(float *)(lVar36 + 0x188f8);
      fVar47 = *(float *)(lVar36 + 0x188fc);
      auVar77._0_4_ = fVar44 * fVar44;
      auVar77._4_4_ = fVar51 * fVar51;
      auVar77._8_4_ = fVar74 * fVar74;
      auVar77._12_4_ = fVar47 * fVar47;
      auVar103 = vpshufd_avx(auVar77,0x55);
      auVar104 = vpshufd_avx(auVar77,0);
      auVar53 = vpshufd_avx(auVar77,0xaa);
      auVar78._0_4_ = auVar53._0_4_ + auVar104._0_4_ + auVar103._0_4_;
      auVar78._4_4_ = auVar53._4_4_ + auVar104._4_4_ + auVar103._4_4_;
      auVar78._8_4_ = auVar53._8_4_ + auVar104._8_4_ + auVar103._8_4_;
      auVar78._12_4_ = auVar53._12_4_ + auVar104._12_4_ + auVar103._12_4_;
      auVar100 = vrsqrtps_avx(auVar78);
      fVar41 = auVar100._0_4_;
      fVar42 = auVar100._4_4_;
      fVar83 = auVar100._8_4_;
      fVar43 = auVar100._12_4_;
      auVar103 = *(undefined1 (*) [16])(lVar39 + 0xd0);
      auVar95._0_4_ = fVar41 * fVar41 * auVar78._0_4_ * (float)DAT_01660eb0;
      auVar95._4_4_ = fVar42 * fVar42 * auVar78._4_4_ * DAT_01660eb0._4_4_;
      auVar95._8_4_ = fVar83 * fVar83 * auVar78._8_4_ * DAT_01660eb0._8_4_;
      auVar95._12_4_ = fVar43 * fVar43 * auVar78._12_4_ * DAT_01660eb0._12_4_;
      auVar104 = vsubps_avx(_DAT_01660eb0,auVar95);
      auVar85._0_4_ = fVar41 + fVar41 * auVar104._0_4_;
      auVar85._4_4_ = fVar42 + fVar42 * auVar104._4_4_;
      auVar85._8_4_ = fVar83 + fVar83 * auVar104._8_4_;
      auVar85._12_4_ = fVar43 + fVar43 * auVar104._12_4_;
      auVar53 = vcmpps_avx(auVar85,auVar85,0);
      auVar104 = vandps_avx(auVar53,auVar85);
      auVar53 = vandnps_avx(auVar53,auVar100);
      auVar104 = vorps_avx(auVar53,auVar104);
      auVar54._0_4_ = fVar44 * auVar104._0_4_;
      auVar54._4_4_ = fVar51 * auVar104._4_4_;
      auVar54._8_4_ = fVar74 * auVar104._8_4_;
      auVar54._12_4_ = fVar47 * auVar104._12_4_;
      auVar104 = vcmpps_avx(auVar104,_DAT_01660ec0,0);
      auVar104 = vandnps_avx(auVar104,auVar54);
      local_68._0_4_ = auVar103._0_4_ + auVar104._0_4_ * _DAT_01660ed0;
      local_68._4_4_ = auVar103._4_4_ + auVar104._4_4_ * fRam0000000001660ed4;
      local_68._8_4_ = auVar103._8_4_ + auVar104._8_4_ * fRam0000000001660ed8;
      local_68._12_4_ = auVar103._12_4_ + auVar104._12_4_ * fRam0000000001660edc;
      auVar55._0_4_ = auVar104._0_4_ * _DAT_01660ee0;
      auVar55._4_4_ = auVar104._4_4_ * fRam0000000001660ee4;
      auVar55._8_4_ = auVar104._8_4_ * fRam0000000001660ee8;
      auVar55._12_4_ = auVar104._12_4_ * fRam0000000001660eec;
    }
    else {
      local_68 = *(undefined1 (*) [16])(pfVar6 + 0xc);
      auVar103 = *(undefined1 (*) [16])(lVar39 + 0xd0);
      auVar104 = vsubps_avx(auVar103,local_68);
      fVar41 = auVar104._0_4_;
      auVar86._0_4_ = fVar41 * fVar41;
      fVar83 = auVar104._4_4_;
      auVar86._4_4_ = fVar83 * fVar83;
      fVar44 = auVar104._8_4_;
      auVar86._8_4_ = fVar44 * fVar44;
      fVar74 = auVar104._12_4_;
      auVar86._12_4_ = fVar74 * fVar74;
      auVar104 = vpshufd_avx(auVar86,0xaa);
      auVar53 = vpshufd_avx(auVar86,0x55);
      auVar100 = vpshufd_avx(auVar86,0);
      auVar79._0_4_ = auVar104._0_4_ + auVar100._0_4_ + auVar53._0_4_;
      auVar79._4_4_ = auVar104._4_4_ + auVar100._4_4_ + auVar53._4_4_;
      auVar79._8_4_ = auVar104._8_4_ + auVar100._8_4_ + auVar53._8_4_;
      auVar79._12_4_ = auVar104._12_4_ + auVar100._12_4_ + auVar53._12_4_;
      auVar100 = vrsqrtps_avx(auVar79);
      fVar42 = auVar100._0_4_;
      fVar43 = auVar100._4_4_;
      fVar51 = auVar100._8_4_;
      fVar47 = auVar100._12_4_;
      auVar96._0_4_ = fVar42 * fVar42 * auVar79._0_4_ * (float)DAT_01660eb0;
      auVar96._4_4_ = fVar43 * fVar43 * auVar79._4_4_ * DAT_01660eb0._4_4_;
      auVar96._8_4_ = fVar51 * fVar51 * auVar79._8_4_ * DAT_01660eb0._8_4_;
      auVar96._12_4_ = fVar47 * fVar47 * auVar79._12_4_ * DAT_01660eb0._12_4_;
      auVar104 = vsubps_avx(_DAT_01660eb0,auVar96);
      auVar87._0_4_ = fVar42 + fVar42 * auVar104._0_4_;
      auVar87._4_4_ = fVar43 + fVar43 * auVar104._4_4_;
      auVar87._8_4_ = fVar51 + fVar51 * auVar104._8_4_;
      auVar87._12_4_ = fVar47 + fVar47 * auVar104._12_4_;
      auVar53 = vcmpps_avx(auVar87,auVar87,0);
      auVar104 = vandps_avx(auVar53,auVar87);
      auVar53 = vandnps_avx(auVar53,auVar100);
      auVar104 = vorps_avx(auVar53,auVar104);
      auVar56._0_4_ = fVar41 * auVar104._0_4_;
      auVar56._4_4_ = fVar83 * auVar104._4_4_;
      auVar56._8_4_ = fVar44 * auVar104._8_4_;
      auVar56._12_4_ = fVar74 * auVar104._12_4_;
      auVar104 = vcmpps_avx(auVar104,_DAT_01660ec0,0);
      auVar55 = vandnps_avx(auVar104,auVar56);
    }
    auVar104 = local_68;
    if (*(char *)(lVar38 + 10) != '\0') {
      fVar41 = *(float *)(lVar38 + 0xc);
      local_88._0_4_ = fVar41 * _DAT_01ac6360;
      local_88._4_4_ = fVar41 * fRam0000000001ac6364;
      local_88._8_4_ = fVar41 * fRam0000000001ac6368;
      local_88._12_4_ = fVar41 * fRam0000000001ac636c;
      local_78[0] = FUN_0009aec0(local_88);
      fVar41 = *(float *)(lVar38 + 0x10);
      local_a8._0_4_ = fVar41 * _DAT_01ac6360;
      local_a8._4_4_ = fVar41 * fRam0000000001ac6364;
      local_a8._8_4_ = fVar41 * fRam0000000001ac6368;
      local_a8._12_4_ = fVar41 * fRam0000000001ac636c;
      local_98[0] = FUN_0009aec0(local_a8);
      fVar44 = *pfVar6;
      fVar51 = pfVar6[1];
      fVar74 = pfVar6[2];
      fVar47 = pfVar6[3];
      auVar101._0_4_ = fVar44 * fVar44;
      auVar101._4_4_ = fVar51 * fVar51;
      auVar101._8_4_ = fVar74 * fVar74;
      auVar101._12_4_ = fVar47 * fVar47;
      auVar103 = vpshufd_avx(auVar101,0x55);
      auVar53 = vpshufd_avx(auVar101,0);
      auVar100 = vpshufd_avx(auVar101,0xaa);
      auVar102._0_4_ = auVar100._0_4_ + auVar53._0_4_ + auVar103._0_4_;
      auVar102._4_4_ = auVar100._4_4_ + auVar53._4_4_ + auVar103._4_4_;
      auVar102._8_4_ = auVar100._8_4_ + auVar53._8_4_ + auVar103._8_4_;
      auVar102._12_4_ = auVar100._12_4_ + auVar53._12_4_ + auVar103._12_4_;
      auVar100 = vrsqrtps_avx(auVar102);
      fVar41 = auVar100._0_4_;
      fVar42 = auVar100._4_4_;
      fVar83 = auVar100._8_4_;
      fVar43 = auVar100._12_4_;
      auVar103._0_4_ = fVar41 * fVar41 * auVar102._0_4_ * (float)DAT_01660eb0;
      auVar103._4_4_ = fVar42 * fVar42 * auVar102._4_4_ * DAT_01660eb0._4_4_;
      auVar103._8_4_ = fVar83 * fVar83 * auVar102._8_4_ * DAT_01660eb0._8_4_;
      auVar103._12_4_ = fVar43 * fVar43 * auVar102._12_4_ * DAT_01660eb0._12_4_;
      auVar103 = vsubps_avx(_DAT_01660eb0,auVar103);
      auVar97._0_4_ = fVar41 + fVar41 * auVar103._0_4_;
      auVar97._4_4_ = fVar42 + fVar42 * auVar103._4_4_;
      auVar97._8_4_ = fVar83 + fVar83 * auVar103._8_4_;
      auVar97._12_4_ = fVar43 + fVar43 * auVar103._12_4_;
      auVar53 = vcmpps_avx(auVar97,auVar97,0);
      auVar103 = vandps_avx(auVar53,auVar97);
      auVar53 = vandnps_avx(auVar53,auVar100);
      auVar103 = vorps_avx(auVar53,auVar103);
      auVar57._0_4_ = fVar44 * auVar103._0_4_;
      auVar57._4_4_ = fVar51 * auVar103._4_4_;
      auVar57._8_4_ = fVar74 * auVar103._8_4_;
      auVar57._12_4_ = fVar47 * auVar103._12_4_;
      auVar103 = vcmpps_avx(auVar103,_DAT_01660ec0,0);
      auVar103 = vandnps_avx(auVar103,auVar57);
      local_f8._0_4_ = auVar55._0_4_;
      local_f8._4_4_ = auVar55._4_4_;
      uStack_f0._0_4_ = auVar55._8_4_;
      uStack_f0._4_4_ = auVar55._12_4_;
      auVar58._0_4_ = (float)local_f8 * auVar103._0_4_;
      auVar58._4_4_ = local_f8._4_4_ * auVar103._4_4_;
      auVar58._8_4_ = (float)uStack_f0 * auVar103._8_4_;
      auVar58._12_4_ = uStack_f0._4_4_ * auVar103._12_4_;
      auVar103 = vpshufd_avx(auVar58,0x55);
      auVar53 = vpshufd_avx(auVar58,0);
      auVar100 = vpshufd_avx(auVar58,0xaa);
      local_b8._0_4_ = auVar100._0_4_ + auVar53._0_4_ + auVar103._0_4_;
      local_b8._4_4_ = auVar100._4_4_ + auVar53._4_4_ + auVar103._4_4_;
      local_b8._8_4_ = auVar100._8_4_ + auVar53._8_4_ + auVar103._8_4_;
      local_b8._12_4_ = auVar100._12_4_ + auVar53._12_4_ + auVar103._12_4_;
      local_c8 = _DAT_01660ef0;
      uStack_c0 = uRam0000000001660ef8;
      local_d8 = 0;
      uStack_d0 = 0;
      fVar41 = (float)FUN_0009afa0(local_b8,local_78,local_98,&local_c8,&local_d8);
      local_128 = local_128 * fVar41;
      auVar103 = *(undefined1 (*) [16])(lVar39 + 0xd0);
    }
    auVar53 = vpshufd_avx(auVar55,0xff);
    auVar100 = vpshufd_avx(auVar55,0xaa);
    auVar70 = vpshufd_avx(auVar55,0x55);
    auVar75 = vpshufd_avx(auVar55,0);
    auVar59._0_4_ =
         auVar75._0_4_ * *(float *)(lVar39 + 0x10) + auVar70._0_4_ * *(float *)(lVar39 + 0x20) +
         auVar100._0_4_ * *(float *)(lVar39 + 0x30) + auVar53._0_4_ * *(float *)(lVar39 + 0x40);
    auVar59._4_4_ =
         auVar75._4_4_ * *(float *)(lVar39 + 0x14) + auVar70._4_4_ * *(float *)(lVar39 + 0x24) +
         auVar100._4_4_ * *(float *)(lVar39 + 0x34) + auVar53._4_4_ * *(float *)(lVar39 + 0x44);
    auVar59._8_4_ =
         auVar75._8_4_ * *(float *)(lVar39 + 0x18) + auVar70._8_4_ * *(float *)(lVar39 + 0x28) +
         auVar100._8_4_ * *(float *)(lVar39 + 0x38) + auVar53._8_4_ * *(float *)(lVar39 + 0x48);
    auVar59._12_4_ =
         auVar75._12_4_ * *(float *)(lVar39 + 0x1c) + auVar70._12_4_ * *(float *)(lVar39 + 0x2c) +
         auVar100._12_4_ * *(float *)(lVar39 + 0x3c) + auVar53._12_4_ * *(float *)(lVar39 + 0x4c);
    auVar53 = vmovhlps_avx(auVar59,auVar59);
    fVar41 = auVar53._0_4_;
    fVar42 = fVar41;
    if (fVar41 + DAT_01660874 < 0.0) {
      fVar42 = DAT_0166087c;
    }
    fVar83 = DAT_01660874;
    if (fVar42 + DAT_0166087c < 0.0) {
      fVar83 = fVar42;
    }
    fVar42 = (float)thunk_FUN_012aaf66();
    puVar32 = (undefined *)0x0;
    if (DAT_01660884 < fVar41) {
      auVar103 = vsubps_avx(auVar104,auVar103);
      auVar60._0_4_ = auVar103._0_4_ * auVar103._0_4_;
      auVar60._4_4_ = auVar103._4_4_ * auVar103._4_4_;
      auVar60._8_4_ = auVar103._8_4_ * auVar103._8_4_;
      auVar60._12_4_ = auVar103._12_4_ * auVar103._12_4_;
      auVar103 = vpshufd_avx(auVar60,0x55);
      auVar104 = vpshufd_avx(auVar60,0);
      auVar53 = vpshufd_avx(auVar60,0xaa);
      auVar61._0_4_ = auVar53._0_4_ + auVar104._0_4_ + auVar103._0_4_;
      auVar61._4_4_ = auVar53._4_4_ + auVar104._4_4_ + auVar103._4_4_;
      auVar61._8_4_ = auVar53._8_4_ + auVar104._8_4_ + auVar103._8_4_;
      auVar61._12_4_ = auVar53._12_4_ + auVar104._12_4_ + auVar103._12_4_;
      auVar53 = vrsqrtps_avx(auVar61);
      fVar43 = auVar53._0_4_;
      fVar44 = auVar53._4_4_;
      fVar51 = auVar53._8_4_;
      fVar74 = auVar53._12_4_;
      auVar88._0_4_ = fVar43 * fVar43 * auVar61._0_4_ * (float)DAT_01660eb0;
      auVar88._4_4_ = fVar44 * fVar44 * auVar61._4_4_ * DAT_01660eb0._4_4_;
      auVar88._8_4_ = fVar51 * fVar51 * auVar61._8_4_ * DAT_01660eb0._8_4_;
      auVar88._12_4_ = fVar74 * fVar74 * auVar61._12_4_ * DAT_01660eb0._12_4_;
      auVar103 = vsubps_avx(_DAT_01660eb0,auVar88);
      auVar80._0_4_ = fVar43 + fVar43 * auVar103._0_4_;
      auVar80._4_4_ = fVar44 + fVar44 * auVar103._4_4_;
      auVar80._8_4_ = fVar51 + fVar51 * auVar103._8_4_;
      auVar80._12_4_ = fVar74 + fVar74 * auVar103._12_4_;
      auVar104 = vcmpps_avx(auVar80,auVar80,0);
      auVar103 = vandps_avx(auVar104,auVar80);
      auVar104 = vandnps_avx(auVar104,auVar53);
      auVar104 = vorps_avx(auVar104,auVar103);
      auVar103 = vcmpps_avx(auVar104,_DAT_01660ec0,0);
      uVar28 = *(undefined8 *)(pfVar6 + 0x10);
      *(undefined8 *)(&DAT_000013e0 + lVar7) = *(undefined8 *)(pfVar6 + 0x12);
      *(undefined8 *)(&DAT_000013d8 + lVar7) = uVar28;
      fVar43 = pfVar6[0x14];
      uVar26 = *(uint *)(lVar38 + 0x68);
      local_e8 = (undefined1  [16])0x0;
      if (uVar26 != 0xffffffff) {
        lVar37 = (ulong)(((uint)((int)uVar26 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar26 >> 0xd) * 0x40;
        lVar36 = *DAT_01a238a0;
        lVar34 = *(long *)(lVar36 + 0x10 + lVar37);
        uVar52 = (ulong)((uVar26 & 0x1fff) * *(int *)(lVar36 + 0x30 + lVar37));
        lVar36 = (lVar34 + uVar52) -
                 ((long)*(int *)(lVar36 + 0x34 + lVar37) & *(ulong *)(lVar34 + 8 + uVar52));
        if (lVar36 != 0) {
          lVar34 = FUN_0082b940(lVar7,0x47,0xd0);
          thunk_FUN_012aa986(lVar34,0,0xd0);
          *(float *)(lVar34 + 0x54) = fVar43;
          FUN_0082b830(lVar7,lVar36,local_e8,1);
          FUN_0082ba20(lVar7,0x47,0xd0);
        }
      }
      auVar53 = vpshufd_avx(local_e8,3);
      fVar43 = auVar53._0_4_ * *(float *)(lVar38 + 0x14);
      if (0.0 < *(float *)(lVar38 + 0x3c)) {
        local_1a8 = auVar104._0_4_;
        fStack_1a4 = auVar104._4_4_;
        fStack_1a0 = auVar104._8_4_;
        fStack_19c = auVar104._12_4_;
        auVar89._0_4_ = auVar61._0_4_ * local_1a8;
        auVar89._4_4_ = auVar61._4_4_ * fStack_1a4;
        auVar89._8_4_ = auVar61._8_4_ * fStack_1a0;
        auVar89._12_4_ = auVar61._12_4_ * fStack_19c;
        vandnps_avx(auVar103,auVar89);
        fVar43 = (float)FUN_000915e0(fVar43 * *(float *)(lVar38 + 0x40));
      }
      uVar45 = *(undefined4 *)(param_6 + 0x48);
      uVar28 = *(undefined8 *)(param_1[8] + 0x1fc50);
      fVar44 = (float)FUN_007faf90(uVar28,lVar38,local_68,uVar45);
      if ((DAT_0271b830 != 0) ||
         (fVar83 = fVar83 * fVar83 * *(float *)(&DAT_026e4d08 + uVar31 * 4), fVar83 <= 0.0)) {
        puVar32 = (undefined *)0x0;
        if (DAT_0271b830 == 1) {
          uVar45 = FUN_007fb1d0(uVar28,lVar38,lVar39 + 0x10,local_68,&local_58,uVar45);
          iVar4 = *(int *)(param_6 + 0x48);
          lVar36 = *param_1;
          puVar27 = (undefined8 *)FUN_0082b940(lVar36,0x47,0xd0);
          uVar28 = FUN_00818d90(0xc);
          *puVar27 = uVar28;
          puVar29 = (ushort *)FUN_00818dd0(0xc);
          auVar62._0_4_ = DAT_01660874 / (float)*puVar29;
          auVar62._4_12_ = SUB6012((undefined1  [60])0x0,0);
          auVar103 = vinsertps_avx(ZEXT416((uint)(float)*puVar29),ZEXT416((uint)(float)puVar29[1]),
                                   0x10);
          auVar103 = vinsertps_avx(auVar103,auVar62,0x20);
          auVar103 = vinsertps_avx(auVar103,ZEXT416((uint)(DAT_01660874 / (float)puVar29[1])),0x30);
          *(undefined1 (*) [16])(puVar27 + 2) = auVar103;
          *(undefined4 *)(puVar27 + 8) = uVar45;
          *(undefined4 *)((long)puVar27 + 0x44) = uVar45;
          puVar27[4] = local_68._0_8_;
          puVar27[5] = local_68._8_8_;
          uVar28 = *(undefined8 *)(lVar36 + 0x15c0);
          uVar30 = FUN_0082e420(1);
          FUN_007deb70(uVar28,uVar30,0);
          FUN_007dec20(*(undefined8 *)(lVar36 + 0x15c0),DAT_026e5fdc,0,0,0);
          FUN_007dee30(*(undefined8 *)(lVar36 + 0x15c0),DAT_026e5fe0);
          if (*(char *)(param_1[8] + 0x19330) == '\0') {
            *(undefined4 *)(lVar36 + 0x15d0) = 0x81818fa6;
          }
          else {
            *(undefined4 *)(lVar36 + 0x15d0) = 0x81818f81;
          }
          lVar39 = FUN_0082cc20(0x163);
          if (iVar4 - 1U < 2) {
            lVar39 = FUN_0082cc20(0x164);
          }
          if ((((lVar39 != 0) && (cVar25 = FUN_0082b490(lVar36,lVar39), cVar25 != '\0')) &&
              (uVar26 = *(uint *)(&DAT_026e5bb0 + uVar31 * 4), uVar26 != 0xffffffff)) &&
             ((*(uint *)(&DAT_026e5390 + (ulong)(uVar26 >> 5 & 0xff) * 4) >> (uVar26 & 0x1f) & 1) !=
              0)) {
            fVar41 = pfVar6[0x15];
            local_48 = *(undefined8 *)(&DAT_026e53b0 + (ulong)(uVar26 & 0x1fff) * 8);
            FUN_007e12c0(param_1[1],&local_48,fVar41);
            FUN_007d2410(param_1,3,0,0,0x30);
            FUN_007e1390(param_1[1],&local_48,fVar41);
          }
          FUN_0082ba20(lVar36,0x47,0xd0);
          puVar32 = (undefined *)0x0;
        }
      }
      else {
        auVar103 = vpshufd_avx(auVar59,1);
        auVar90._0_4_ = auVar103._0_4_ / fVar41;
        auVar90._4_12_ = auVar103._4_12_;
        auVar98._0_4_ = auVar59._0_4_ / fVar41;
        auVar98._4_12_ = auVar59._4_12_;
        fVar43 = fVar43 * fVar44;
        local_128 = local_128 * fVar83;
        if ((*(uint *)(param_1 + 0x12) & 8) == 0) {
          lVar36 = *(long *)(lVar38 + 0x70);
          puVar32 = &DAT_026e0001;
          if (0 < lVar36) {
            auVar104 = vunpcklps_avx(auVar98,auVar90);
            auVar81._4_12_ = SUB1612(ZEXT416(0),0);
            auVar81._0_4_ = local_128;
            auVar103 = vpshufd_avx(ZEXT416((uint)local_128),0x50);
            auVar103 = vmovlhps_avx(auVar103,auVar81);
            plVar33 = (long *)(lVar38 + 0x78);
            bVar40 = (*(uint *)(param_1 + 0x12) & 0x10) == 0;
            fVar41 = auVar90._0_4_ + DAT_01660894;
            fVar83 = auVar98._0_4_ + DAT_01660894;
            uVar26 = *(uint *)(&DAT_01661308 + (ulong)!bVar40 * 4);
            lVar39 = 0xf1;
            do {
              fVar44 = DAT_01660874;
              lVar38 = *plVar33;
              if ((*(char *)((long)plVar33 + lVar39 + lVar38) != '\0' || bVar40) &&
                 (fVar51 = *(float *)((long)plVar33 + lVar39 + -0x9d + lVar38), fVar42 < fVar51)) {
                cVar25 = *(char *)((long)plVar33 + lVar39 + -1 + lVar38);
                pauVar1 = (undefined1 (*) [16])((long)plVar33 + lVar39 + -0x11 + lVar38);
                uVar30 = *(undefined8 *)*pauVar1;
                auVar100 = *pauVar1;
                pauVar1 = (undefined1 (*) [16])((long)plVar33 + lVar39 + -0x31 + lVar38);
                uVar17 = *(undefined8 *)*pauVar1;
                auVar70 = *pauVar1;
                pauVar1 = (undefined1 (*) [16])((long)plVar33 + lVar39 + -0x41 + lVar38);
                uVar18 = *(undefined8 *)*pauVar1;
                auVar75 = *pauVar1;
                pauVar1 = (undefined1 (*) [16])((long)plVar33 + lVar39 + -0x51 + lVar38);
                uVar19 = *(undefined8 *)*pauVar1;
                auVar56 = *pauVar1;
                uVar45 = *(undefined4 *)((long)plVar33 + lVar39 + -0x61 + lVar38);
                pauVar1 = (undefined1 (*) [16])((long)plVar33 + lVar39 + -0x71 + lVar38);
                uVar20 = *(undefined8 *)*pauVar1;
                auVar79 = *pauVar1;
                uVar2 = *(undefined4 *)((long)plVar33 + lVar39 + -0x81 + lVar38);
                pauVar1 = (undefined1 (*) [16])((long)plVar33 + lVar39 + -0x91 + lVar38);
                uVar21 = *(undefined8 *)*pauVar1;
                auVar76 = *pauVar1;
                uVar3 = *(undefined4 *)((long)plVar33 + lVar39 + -0x99 + lVar38);
                uVar5 = *(uint *)((long)plVar33 + lVar39 + -0xe1 + lVar38);
                fVar74 = *(float *)((long)plVar33 + lVar39 + -0xa1 + lVar38);
                pauVar1 = (undefined1 (*) [16])((long)plVar33 + lVar39 + -0xb1 + lVar38);
                uVar22 = *(undefined8 *)*pauVar1;
                auVar55 = *pauVar1;
                pauVar1 = (undefined1 (*) [16])((long)plVar33 + lVar39 + -0xc1 + lVar38);
                uVar28 = *(undefined8 *)*pauVar1;
                auVar53 = *pauVar1;
                pauVar1 = (undefined1 (*) [16])((long)plVar33 + lVar39 + -0xd1 + lVar38);
                uVar23 = *(undefined8 *)*pauVar1;
                auVar86 = *pauVar1;
                fVar47 = *(float *)((long)plVar33 + lVar39 + lVar38 + -0x21);
                fVar46 = (float)FUN_000915e0(DAT_01660874,uVar28,fVar43);
                auVar53 = vpshufd_avx(auVar53,1);
                fVar44 = (float)FUN_000915e0(fVar44,auVar53._0_8_,fVar43);
                fVar99 = (float)uVar19;
                auVar100 = vpshufd_avx(auVar100,1);
                local_128 = fVar41 * auVar100._0_4_ +
                            fVar83 * (float)uVar30 + fVar47 * DAT_026e5ffc * DAT_01660898 + 0.0;
                if (0.0 < fVar99) {
                  auVar100 = vpshufd_avx(auVar56,1);
                  if (0.0 < auVar100._0_4_) {
                    local_f8._0_4_ = (float)uVar28;
                    local_268 = auVar53._0_4_;
                    fVar47 = (float)thunk_FUN_012aaf86(auVar98._0_4_ * (float)local_f8 * fVar99,
                                                       auVar90._0_4_ * local_268 * auVar100._0_4_);
                    local_128 = local_128 + fVar47 / DAT_0166089c;
                  }
                }
                auVar96 = _DAT_01660ec0;
                auVar87 = _DAT_01660eb0;
                auVar53 = vunpcklps_avx(ZEXT416((uint)(auVar98._0_4_ * fVar46)),
                                        ZEXT416((uint)(auVar90._0_4_ * fVar44)));
                auVar63._0_8_ = auVar53._0_8_;
                auVar63._8_8_ = 0;
                auVar24._8_8_ = 0;
                auVar24._0_8_ = auVar104._0_8_;
                auVar53 = vsubps_avx(auVar63,auVar24);
                auVar53 = vshufps_avx(auVar53,_DAT_01660f10,4);
                auVar64._0_4_ = auVar53._0_4_ * auVar53._0_4_;
                auVar64._4_4_ = auVar53._4_4_ * auVar53._4_4_;
                auVar64._8_4_ = auVar53._8_4_ * auVar53._8_4_;
                auVar64._12_4_ = auVar53._12_4_ * auVar53._12_4_;
                auVar53 = vpshufd_avx(auVar64,0x55);
                auVar100 = vpshufd_avx(auVar64,0);
                auVar56 = vpshufd_avx(auVar64,0xaa);
                auVar65._0_4_ = auVar56._0_4_ + auVar100._0_4_ + auVar53._0_4_;
                auVar65._4_4_ = auVar56._4_4_ + auVar100._4_4_ + auVar53._4_4_;
                auVar65._8_4_ = auVar56._8_4_ + auVar100._8_4_ + auVar53._8_4_;
                auVar65._12_4_ = auVar56._12_4_ + auVar100._12_4_ + auVar53._12_4_;
                fVar47 = (float)DAT_01660eb0;
                fVar9 = DAT_01660eb0._4_4_;
                fVar12 = DAT_01660eb0._8_4_;
                fVar14 = DAT_01660eb0._12_4_;
                auVar56 = vrsqrtps_avx(auVar65);
                fVar99 = auVar56._0_4_;
                fVar10 = auVar56._4_4_;
                fVar48 = auVar56._8_4_;
                fVar49 = auVar56._12_4_;
                auVar91._0_4_ = auVar65._0_4_ * fVar47 * fVar99 * fVar99;
                auVar91._4_4_ = auVar65._4_4_ * fVar9 * fVar10 * fVar10;
                auVar91._8_4_ = auVar65._8_4_ * fVar12 * fVar48 * fVar48;
                auVar91._12_4_ = auVar65._12_4_ * fVar14 * fVar49 * fVar49;
                auVar53 = vsubps_avx(_DAT_01660eb0,auVar91);
                auVar92._0_4_ = fVar99 + fVar99 * auVar53._0_4_;
                auVar92._4_4_ = fVar10 + fVar10 * auVar53._4_4_;
                auVar92._8_4_ = fVar48 + fVar48 * auVar53._8_4_;
                auVar92._12_4_ = fVar49 + fVar49 * auVar53._12_4_;
                auVar100 = vcmpps_avx(auVar92,auVar92,0);
                auVar53 = vandps_avx(auVar100,auVar92);
                auVar100 = vandnps_avx(auVar100,auVar56);
                auVar53 = vorps_avx(auVar100,auVar53);
                auVar66._0_4_ = auVar65._0_4_ * auVar53._0_4_;
                auVar66._4_4_ = auVar65._4_4_ * auVar53._4_4_;
                auVar66._8_4_ = auVar65._8_4_ * auVar53._8_4_;
                auVar66._12_4_ = auVar65._12_4_ * auVar53._12_4_;
                auVar53 = vcmpps_avx(auVar53,_DAT_01660ec0,0);
                auVar53 = vandnps_avx(auVar53,auVar66);
                thunk_FUN_012aaf46(auVar53._0_8_,uVar2);
                fVar10 = DAT_0166087c;
                fVar99 = DAT_01660874;
                auVar100 = vmovhlps_avx(auVar76,auVar76);
                local_f8._0_4_ = DAT_01660874;
                fVar48 = (float)FUN_000915e0(uVar21,auVar100._0_8_);
                auVar100 = vpshufd_avx(auVar76,1);
                auVar76 = vpshufd_avx(auVar76,3);
                fVar49 = (float)FUN_000915e0(auVar100._0_8_,auVar76._0_8_);
                uVar52 = thunk_FUN_012aaf46(auVar53._0_8_,uVar45);
                if ((float)uVar52 < 0.0) {
                  uVar52 = 0;
                }
                auVar53 = vpshufd_avx(auVar79,1);
                uVar84 = (ulong)(uint)fVar99;
                if ((float)uVar52 + fVar10 < 0.0) {
                  uVar84 = uVar52;
                }
                fVar50 = (float)FUN_000915e0(uVar20,auVar53._0_8_,uVar84);
                auVar53 = vshufps_avx(auVar63,_DAT_01660f10,4);
                auVar67._0_4_ = auVar53._0_4_ * auVar53._0_4_;
                auVar67._4_4_ = auVar53._4_4_ * auVar53._4_4_;
                auVar67._8_4_ = auVar53._8_4_ * auVar53._8_4_;
                auVar67._12_4_ = auVar53._12_4_ * auVar53._12_4_;
                auVar53 = vpshufd_avx(auVar67,0x55);
                auVar100 = vpshufd_avx(auVar67,0);
                auVar76 = vpshufd_avx(auVar67,0xaa);
                auVar68._0_4_ = auVar76._0_4_ + auVar100._0_4_ + auVar53._0_4_;
                auVar68._4_4_ = auVar76._4_4_ + auVar100._4_4_ + auVar53._4_4_;
                auVar68._8_4_ = auVar76._8_4_ + auVar100._8_4_ + auVar53._8_4_;
                auVar68._12_4_ = auVar76._12_4_ + auVar100._12_4_ + auVar53._12_4_;
                auVar76 = vrsqrtps_avx(auVar68);
                fVar8 = auVar76._0_4_;
                fVar11 = auVar76._4_4_;
                fVar13 = auVar76._8_4_;
                fVar15 = auVar76._12_4_;
                auVar93._0_4_ = auVar68._0_4_ * fVar47 * fVar8 * fVar8;
                auVar93._4_4_ = auVar68._4_4_ * fVar9 * fVar11 * fVar11;
                auVar93._8_4_ = auVar68._8_4_ * fVar12 * fVar13 * fVar13;
                auVar93._12_4_ = auVar68._12_4_ * fVar14 * fVar15 * fVar15;
                auVar53 = vsubps_avx(auVar87,auVar93);
                auVar94._0_4_ = fVar8 + fVar8 * auVar53._0_4_;
                auVar94._4_4_ = fVar11 + fVar11 * auVar53._4_4_;
                auVar94._8_4_ = fVar13 + fVar13 * auVar53._8_4_;
                auVar94._12_4_ = fVar15 + fVar15 * auVar53._12_4_;
                auVar100 = vcmpps_avx(auVar94,auVar94,0);
                auVar53 = vandps_avx(auVar100,auVar94);
                auVar100 = vandnps_avx(auVar100,auVar76);
                auVar53 = vorps_avx(auVar100,auVar53);
                auVar69._0_4_ = auVar68._0_4_ * auVar53._0_4_;
                auVar69._4_4_ = auVar68._4_4_ * auVar53._4_4_;
                auVar69._8_4_ = auVar68._8_4_ * auVar53._8_4_;
                auVar69._12_4_ = auVar68._12_4_ * auVar53._12_4_;
                auVar53 = vcmpps_avx(auVar53,auVar96,0);
                auVar100 = vpshufd_avx(auVar70,1);
                auVar53 = vandnps_avx(auVar53,auVar69);
                thunk_FUN_012aaf46(auVar53._0_8_,auVar100._0_8_);
                fVar47 = (float)FUN_000915e0(uVar17,fVar99);
                auVar100 = vpshufd_avx(auVar75,1);
                uVar52 = thunk_FUN_012aaf46(auVar53._0_8_,auVar100._0_8_);
                if ((float)uVar52 < 0.0) {
                  uVar52 = 0;
                }
                uVar84 = (ulong)(uint)fVar99;
                if ((float)uVar52 + fVar10 < 0.0) {
                  uVar84 = uVar52;
                }
                fVar9 = local_58._4_4_;
                auVar73._0_8_ = FUN_000915e0(uVar18,fVar99,uVar84);
                auVar73._8_56_ = extraout_var_00;
                fVar74 = fVar74 * DAT_01660888;
                fVar51 = fVar51 * DAT_01660888;
                if (fVar51 - fVar74 < fVar42) {
                  fVar74 = (fVar51 - fVar42) / fVar74;
                  local_f8._0_4_ = DAT_01660874;
                  if (fVar74 < 0.0) {
                    fVar74 = 0.0;
                  }
                  if (fVar74 + DAT_0166087c < 0.0) {
                    local_f8._0_4_ = fVar74;
                  }
                }
                if (*(char *)(param_1[8] + 0x19330) == '\0') {
                  fVar50 = fVar50 * (float)local_f8;
                  auVar53 = vinsertps_avx(ZEXT416((uint)fVar50),ZEXT416((uint)fVar50),0x10);
                  auVar53 = vinsertps_avx(auVar53,ZEXT416((uint)fVar50),0x20);
                  auVar53 = vinsertps_avx(auVar53,ZEXT416((uint)DAT_01660874),0x30);
                  local_2c8 = auVar103._0_4_;
                  fStack_2c4 = auVar103._4_4_;
                  fStack_2c0 = auVar103._8_4_;
                  fStack_2bc = auVar103._12_4_;
                  auVar70 = auVar73._0_16_;
                  auVar100 = vinsertps_avx(auVar70,auVar70,0x10);
                  auVar100 = vinsertps_avx(auVar100,auVar70,0x20);
                  auVar100 = vinsertps_avx(auVar100,ZEXT416((uint)DAT_01660874),0x30);
                  fVar51 = auVar100._0_4_ * local_2c8 * auVar53._0_4_;
                  fVar74 = auVar100._4_4_ * fStack_2c4 * auVar53._4_4_;
                  uStack_f0._0_4_ = auVar100._8_4_ * fStack_2c0 * auVar53._8_4_;
                  uStack_f0._4_4_ = auVar100._12_4_ * fStack_2bc * auVar53._12_4_;
                  local_f8 = CONCAT44(fVar74,fVar51);
                  auVar71._0_4_ = fVar51 * _DAT_01660f00;
                  auVar71._4_4_ = fVar74 * fRam0000000001660f04;
                  auVar71._8_4_ = (float)uStack_f0 * fRam0000000001660f08;
                  auVar71._12_4_ = uStack_f0._4_4_ * fRam0000000001660f0c;
                  auVar53 = vpshufd_avx(auVar71,0x55);
                  auVar100 = vpshufd_avx(auVar71,0);
                  auVar70 = vpshufd_avx(auVar71,0xaa);
                  if (DAT_016608a0 < auVar70._0_4_ + auVar100._0_4_ + auVar53._0_4_) {
                    auVar100 = vpshufd_avx(auVar55,1);
                    auVar53 = vinsertps_avx(ZEXT416((uint)(auVar98._0_4_ * fVar46)),
                                            ZEXT416((uint)(auVar90._0_4_ * fVar44)),0x10);
                    auVar70 = vpshufd_avx(auVar86,1);
                    lVar38 = *(long *)(param_1[8] + 0x1fc50);
                    lVar34 = *param_1;
                    lVar35 = FUN_0082b940(lVar34,0x47,0xd0);
                    auVar75 = vunpcklps_avx(ZEXT416((uint)(fVar43 * (float)uVar22)),
                                            ZEXT416((uint)(fVar43 * auVar100._0_4_)));
                    auVar100 = vinsertps_avx(*(undefined1 (*) [16])
                                              (*(long *)(lVar34 + 0x15c8) + 0x1b320),ZEXT416(uVar26)
                                             ,0x30);
                    *(undefined1 (*) [16])(lVar35 + 0x70) = auVar100;
                    auVar53 = vinsertps_avx(auVar53,ZEXT416((uint)DAT_01660874),0x20);
                    auVar53 = vinsertps_avx(auVar53,ZEXT816(0) << 0x20,0x30);
                    lVar37 = 0;
                    *(float *)(lVar35 + 0x40) = fVar43 * (float)uVar23 * fVar48 * fVar47 * fVar9;
                    *(float *)(lVar35 + 0x44) = fVar43 * auVar70._0_4_ * fVar49 * fVar47 * fVar9;
                    *(undefined1 (*) [16])(lVar35 + 0x20) = auVar53;
                    *(long *)(lVar35 + 0x60) = auVar75._0_8_;
                    *(undefined8 *)(lVar35 + 0x68) = 0;
                    *(undefined8 *)(lVar35 + 0x30) = local_f8;
                    *(undefined8 *)(lVar35 + 0x38) = uStack_f0;
                    *(float *)(lVar35 + 0x48) = local_128;
                    *(undefined4 *)(lVar35 + 0x4c) = 0;
                    *(undefined4 *)(lVar35 + 0x50) = uVar3;
                    *(float *)(lVar35 + 0x54) = pfVar6[0x14];
                    uVar28 = *(undefined8 *)(lVar38 + 0x50);
                    uVar30 = *(undefined8 *)(lVar38 + 0x58);
                    uVar17 = *(undefined8 *)(lVar38 + 0x68);
                    uVar18 = *(undefined8 *)(lVar38 + 0x70);
                    uVar19 = *(undefined8 *)(lVar38 + 0x78);
                    auVar53 = *(undefined1 (*) [16])(lVar38 + 0x80);
                    *(undefined8 *)(lVar35 + 0x90) = *(undefined8 *)(lVar38 + 0x60);
                    *(undefined8 *)(lVar35 + 0x98) = uVar17;
                    *(undefined8 *)(lVar35 + 0x80) = uVar28;
                    *(undefined8 *)(lVar35 + 0x88) = uVar30;
                    *(undefined1 (*) [16])(lVar35 + 0xb0) = auVar53;
                    *(undefined8 *)(lVar35 + 0xa0) = uVar18;
                    *(undefined8 *)(lVar35 + 0xa8) = uVar19;
                    *(undefined1 *)(lVar34 + 0x15d0) = local_29d;
                    *(undefined2 *)(lVar34 + 0x15d1) = 0x8181;
                    *(undefined1 *)(lVar34 + 0x15d3) = 0x81;
                    if (uVar5 != 0xffffffff) {
                      lVar37 = (ulong)(((uint)((int)uVar5 >> 0xd) >> 0x12 | 0x3ff) &
                                      (int)uVar5 >> 0xd) * 0x40;
                      lVar38 = *DAT_01a238a0;
                      lVar35 = *(long *)(lVar38 + 0x10 + lVar37);
                      uVar52 = (ulong)((uVar5 & 0x1fff) * *(int *)(lVar38 + 0x30 + lVar37));
                      lVar37 = (lVar35 + uVar52) -
                               ((long)*(int *)(lVar38 + 0x34 + lVar37) &
                               *(ulong *)(lVar35 + 8 + uVar52));
                    }
                    if (*(uint *)(&DAT_026e5bb0 + uVar31 * 4) != 0xffffffff) {
                      local_40 = *(undefined8 *)
                                  (&DAT_026e53b0 +
                                  (ulong)(*(uint *)(&DAT_026e5bb0 + uVar31 * 4) & 0x1fff) * 8);
                      FUN_007e14b0(param_1[1],&local_40,pfVar6[0x15]);
                    }
                    uVar28 = *(undefined8 *)(lVar34 + 0x15c0);
                    uVar30 = FUN_0082e420(5);
                    FUN_007deb70(uVar28,uVar30,0);
                    if (cVar25 == '\0') {
                      FUN_007dec20(*(undefined8 *)(lVar34 + 0x15c0),DAT_026e5fe4,0,0,0);
                      FUN_007dee30(*(undefined8 *)(lVar34 + 0x15c0),DAT_026e5fe8);
                      if ((lVar37 != 0) && (cVar25 = FUN_0082b490(lVar34,lVar37), cVar25 != '\0')) {
                        uVar28 = *(undefined8 *)(lVar34 + 0x15c0);
                        uVar30 = 6;
LAB_007fde58:
                        FUN_007e15d0(uVar28,3,0,0,uVar30,0,0,0);
                      }
                    }
                    else {
                      FUN_007dec20(*(undefined8 *)(lVar34 + 0x15c0),DAT_026e5fec,0,0,0);
                      FUN_007dee30(*(undefined8 *)(lVar34 + 0x15c0),DAT_026e5ff0);
                      if ((lVar37 != 0) && (cVar25 = FUN_0082b490(lVar34,lVar37), cVar25 != '\0')) {
                        uVar28 = *(undefined8 *)(lVar34 + 0x15c0);
                        uVar30 = 0xc;
                        goto LAB_007fde58;
                      }
                    }
                    if (*(uint *)(&DAT_026e5bb0 + uVar31 * 4) != 0xffffffff) {
                      local_40 = *(undefined8 *)
                                  (&DAT_026e53b0 +
                                  (ulong)(*(uint *)(&DAT_026e5bb0 + uVar31 * 4) & 0x1fff) * 8);
                      FUN_007e14d0(param_1[1],&local_40,pfVar6[0x15]);
                    }
                    FUN_0082ba20(lVar34,0x47,0xd0);
                  }
                }
              }
              lVar39 = lVar39 + 0xf0;
              lVar36 = lVar36 + -1;
            } while (lVar36 != 0);
            puVar32 = (undefined *)0x1;
          }
        }
        else {
          puVar32 = &DAT_026e0001;
          if (((lVar35 != 0) && (*(char *)(lVar38 + 100) != '\0')) &&
             (fVar42 < *(float *)(lVar38 + 0x5c))) {
            auVar103 = vinsertps_avx(auVar98,auVar90,0x10);
            fVar41 = DAT_01660888 * *(float *)(lVar38 + 0x60);
            fVar83 = *(float *)(lVar38 + 0x5c) * DAT_01660888;
            fVar44 = DAT_01660874;
            if (fVar83 - fVar41 < fVar42) {
              fVar41 = (fVar83 - fVar42) / fVar41;
              if (fVar41 < 0.0) {
                fVar41 = 0.0;
              }
              if (fVar41 + DAT_0166087c < 0.0) {
                fVar44 = fVar41;
              }
            }
            auVar104 = vpshufd_avx(local_e8,0x24);
            auVar16._12_4_ = 0;
            auVar16._0_12_ = auVar104._4_12_;
            fVar41 = (fVar43 + DAT_0166088c) / DAT_01660890;
            auVar104 = vpshufd_avx(auVar16 << 0x20,0x27);
            if (0.0 <= fVar41 + DAT_0166087c) {
              fVar41 = DAT_01660874;
            }
            auVar53 = vpshufd_avx(ZEXT416((uint)(local_128 * fVar44 * fVar41)),0);
            fVar41 = auVar104._0_4_ * auVar53._0_4_;
            fVar42 = auVar104._4_4_ * auVar53._4_4_;
            fVar83 = auVar104._8_4_ * auVar53._8_4_;
            fVar44 = auVar104._12_4_ * auVar53._12_4_;
            local_108 = CONCAT44(fVar42,fVar41);
            auVar82._0_4_ = fVar41 * _DAT_01660f00;
            auVar82._4_4_ = fVar42 * fRam0000000001660f04;
            auVar82._8_4_ = fVar83 * fRam0000000001660f08;
            auVar82._12_4_ = fVar44 * fRam0000000001660f0c;
            auVar104 = vpshufd_avx(auVar82,0x55);
            auVar53 = vpshufd_avx(auVar82,0);
            auVar100 = vpshufd_avx(auVar82,0xaa);
            if (auVar100._0_4_ + auVar53._0_4_ + auVar104._0_4_ <= 0.0) {
              puVar32 = &DAT_026e0001;
            }
            else {
              fVar41 = *(float *)(lVar38 + 0x58);
              lVar36 = FUN_0082b940(lVar7,0x47,0xd0);
              fVar41 = fVar43 * fVar41 * auVar76._0_4_;
              *(float *)(lVar36 + 0x40) = fVar41;
              *(float *)(lVar36 + 0x44) = fVar41;
              auVar103 = vinsertps_avx(auVar103,ZEXT416((uint)DAT_01660874),0x20);
              auVar103 = vinsertps_avx(auVar103,ZEXT816(0),0x30);
              *(undefined1 (*) [16])(lVar36 + 0x20) = auVar103;
              uVar20 = *(undefined8 *)(lVar39 + 0x50);
              uVar21 = *(undefined8 *)(lVar39 + 0x58);
              uVar28 = *(undefined8 *)(lVar39 + 0x68);
              uVar30 = *(undefined8 *)(lVar39 + 0x70);
              uVar17 = *(undefined8 *)(lVar39 + 0x78);
              uVar18 = *(undefined8 *)(lVar39 + 0x80);
              uVar19 = *(undefined8 *)(lVar39 + 0x88);
              *(undefined8 *)(lVar36 + 0x90) = *(undefined8 *)(lVar39 + 0x60);
              *(undefined8 *)(lVar36 + 0x98) = uVar28;
              *(undefined8 *)(lVar36 + 0x80) = uVar20;
              *(undefined8 *)(lVar36 + 0x88) = uVar21;
              *(undefined8 *)(lVar36 + 0xb0) = uVar18;
              *(undefined8 *)(lVar36 + 0xb8) = uVar19;
              *(undefined8 *)(lVar36 + 0xa0) = uVar30;
              *(undefined8 *)(lVar36 + 0xa8) = uVar17;
              *(undefined8 *)(lVar36 + 0x30) = local_108;
              *(ulong *)(lVar36 + 0x38) = CONCAT44(fVar44,fVar83);
              uVar28 = *(undefined8 *)(lVar7 + 0x15c0);
              uVar30 = FUN_0082e420(1);
              FUN_007deb70(uVar28,uVar30,0);
              FUN_007dec20(*(undefined8 *)(lVar7 + 0x15c0),DAT_026e5ff4,0,0,0);
              FUN_007dee30(*(undefined8 *)(lVar7 + 0x15c0),DAT_026e5ff8);
              *(undefined1 *)(lVar7 + 0x15d0) = 0x82;
              *(undefined2 *)(lVar7 + 0x15d1) = 0x8181;
              *(undefined1 *)(lVar7 + 0x15d3) = 0x81;
              lVar36 = FUN_0082cc20(0x169);
              if ((lVar36 != 0) && (cVar25 = FUN_0082b490(lVar7,lVar36), cVar25 != '\0')) {
                FUN_007e15d0(*(undefined8 *)(lVar7 + 0x15c0),3,0,0,6,0,0,0);
              }
              FUN_0082ba20(lVar7,0x47,0xd0);
              puVar32 = (undefined *)0x1;
            }
          }
        }
      }
      *(undefined4 *)(&DAT_000013d8 + lVar7) = 0;
      *(undefined8 *)(&DAT_000013e0 + lVar7) = 0;
    }
  }
LAB_007fd3f1:
  if (*DAT_01a1f100 == local_38) {
    return (ulong)puVar32 & 0xffff;
  }
  uVar31 = thunk_FUN_012aa7f6();
  return uVar31;
}

