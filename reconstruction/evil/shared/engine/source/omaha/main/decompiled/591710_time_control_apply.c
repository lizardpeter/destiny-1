
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00591710(float param_1,float *param_2,int *param_3,float *param_4,int *param_5)

{
  byte *pbVar1;
  char *pcVar2;
  byte *pbVar3;
  char cVar4;
  char cVar5;
  int iVar6;
  int iVar7;
  int *piVar8;
  int iVar9;
  bool bVar10;
  undefined4 uVar11;
  float fVar12;
  undefined8 extraout_XMM0_Qa;
  undefined1 auVar13 [16];
  undefined8 extraout_XMM0_Qa_00;
  undefined1 auVar14 [16];
  undefined1 extraout_var [56];
  undefined1 extraout_var_00 [56];
  float fVar17;
  int local_3c;
  long local_38;
  undefined1 auVar15 [64];
  undefined1 auVar16 [64];
  
  local_38 = *DAT_01a1f100;
  cVar4 = FUN_00906f70();
  if (cVar4 != '\0') {
    uVar11 = FUN_0093d580();
    *(undefined4 *)(DAT_026bc888 + 4) = uVar11;
  }
  pbVar1 = DAT_026bc888;
  cVar4 = FUN_00906e00();
  if ((cVar4 != '\0') && (fVar17 = *(float *)(pbVar1 + 0x10), 0.0 < fVar17)) {
    fVar12 = param_1 + *(float *)(pbVar1 + 0xc);
    *(float *)(pbVar1 + 0xc) = fVar12;
    if (fVar17 <= fVar12) {
      fVar17 = *(float *)(pbVar1 + 0x18);
      if (*(float *)(pbVar1 + 0x18) + DAT_0163e248 < 0.0) {
        fVar17 = DAT_0163e24c;
      }
      piVar8 = (int *)FUN_009067e0();
      auVar16._8_56_ = extraout_var_00;
      auVar16._0_8_ = extraout_XMM0_Qa_00;
      auVar14._4_12_ = auVar16._4_12_;
      auVar14._0_4_ = (float)*piVar8 / fVar17;
      iVar6 = thunk_FUN_012ab486(auVar14._0_8_);
      pbVar3 = DAT_026bc888;
      pcVar2 = DAT_026bc880;
      fVar17 = DAT_0163e250 / (float)iVar6;
      *(int *)(DAT_026bc880 + 4) = iVar6;
      *(float *)(pcVar2 + 8) = fVar17;
      *(float *)(pbVar3 + 4) = (float)*piVar8 / (float)iVar6;
      pbVar1[0x10] = 0;
      pbVar1[0x11] = 0;
      pbVar1[0x12] = 0;
      pbVar1[0x13] = 0;
    }
    else {
      fVar17 = (DAT_0163e250 - fVar12 / fVar17) * *(float *)(pbVar1 + 0x14) +
               (fVar12 / fVar17) * *(float *)(pbVar1 + 0x18);
      if (fVar17 + DAT_0163e248 < 0.0) {
        fVar17 = DAT_0163e24c;
      }
      piVar8 = (int *)FUN_009067e0();
      auVar15._8_56_ = extraout_var;
      auVar15._0_8_ = extraout_XMM0_Qa;
      auVar13._4_12_ = auVar15._4_12_;
      auVar13._0_4_ = (float)*piVar8 / fVar17;
      iVar6 = thunk_FUN_012ab486(auVar13._0_8_);
      pbVar3 = DAT_026bc888;
      pcVar2 = DAT_026bc880;
      fVar17 = DAT_0163e250 / (float)iVar6;
      *(int *)(DAT_026bc880 + 4) = iVar6;
      *(float *)(pcVar2 + 8) = fVar17;
      *(float *)(pbVar3 + 4) = (float)*piVar8 / (float)iVar6;
    }
  }
  cVar4 = FUN_00906e00();
  iVar6 = 0;
  fVar17 = 0.0;
  if (cVar4 == '\0') {
    fVar12 = 0.0;
  }
  else if ((*DAT_026bc880 == '\0') || ((*DAT_026bc888 & 2) == 0)) {
    fVar17 = 0.0;
    fVar12 = 0.0;
    if (0.0 < *(float *)(DAT_026bc888 + 4)) {
      cVar4 = FUN_001dad30();
      iVar6 = FUN_00b9f400();
      local_3c = 0;
      cVar5 = FUN_0093e0a0(&local_3c);
      if ((cVar5 != '\0') && (local_3c < iVar6)) {
        iVar6 = local_3c;
      }
      fVar12 = *(float *)(DAT_026bc888 + 4);
      if (cVar4 == '\0') {
        fVar17 = fVar12 + fVar12;
        if (fVar12 + fVar12 + DAT_0163e254 < 0.0) {
          fVar17 = DAT_0163e258;
        }
        if (0.0 <= fVar17 + DAT_0163e25c) {
          fVar17 = DAT_0163e260;
        }
        iVar7 = thunk_FUN_012ab486(fVar17);
        if (iVar7 < iVar6) {
          iVar6 = iVar7;
        }
        fVar12 = *(float *)(DAT_026bc888 + 4);
        iVar7 = iVar6;
      }
      else if (((((uint)(fVar12 + DAT_0163e264) & 0x7f800000) == 0x7f800000) ||
               (auVar14 = vandps_avx(ZEXT416((uint)(fVar12 + DAT_0163e264)),_DAT_0163e290),
               iVar7 = iVar6, DAT_0163e268 <= auVar14._0_4_)) && (iVar7 = 10, iVar6 < 0xb)) {
        iVar7 = iVar6;
      }
      fVar12 = fVar12 * param_1;
      fVar17 = (float)FUN_005938b0();
      fVar17 = fVar12 * fVar17 + *(float *)(pbVar1 + 8);
      iVar9 = (int)fVar17;
      iVar6 = iVar9;
      if (iVar7 < iVar9) {
        iVar6 = iVar7;
      }
      if (iVar7 < iVar9) {
        fVar12 = (float)FUN_00593890();
        fVar12 = (float)iVar6 * fVar12;
        fVar17 = *(float *)(pbVar1 + 8);
      }
      else {
        fVar17 = fVar17 - (float)iVar6;
      }
    }
  }
  else {
    fVar12 = 0.0;
  }
  *(float *)(pbVar1 + 8) = fVar17;
  iVar7 = iVar6;
  fVar17 = fVar12;
  if (((DAT_018dcaa4 != '\0') &&
      (((uint)(*(float *)(DAT_026bc888 + 4) + DAT_0163e264) & 0x7f800000) != 0x7f800000)) &&
     (auVar14 = vandps_avx(ZEXT416((uint)(*(float *)(DAT_026bc888 + 4) + DAT_0163e264)),
                           _DAT_0163e290), auVar14._0_4_ < DAT_0163e268)) {
    bVar10 = true;
    if (*DAT_026bc880 != '\0') {
      bVar10 = (*DAT_026bc888 & 2) == 0;
    }
    if ((bVar10) && (0.0 < param_1)) {
      fVar17 = *(float *)(DAT_026bc880 + 8);
      iVar7 = 1;
    }
  }
  if (DAT_026bc890 != '\0') {
    fVar12 = (float)FUN_00593890();
    iVar6 = 1;
  }
  *param_2 = fVar17;
  *param_3 = iVar7;
  *param_4 = fVar12;
  *param_5 = iVar6;
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

