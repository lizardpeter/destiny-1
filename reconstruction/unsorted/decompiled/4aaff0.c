
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_004aaff0(float param_1,undefined8 param_2,long param_3,undefined1 (*param_4) [16],
                 undefined1 (*param_5) [16],undefined1 (*param_6) [16],float *param_7,float *param_8
                 )

{
  undefined1 auVar1 [16];
  undefined1 auVar2 [16];
  undefined1 auVar3 [16];
  long *plVar4;
  float fVar5;
  float fVar10;
  undefined1 auVar6 [16];
  float fVar8;
  float fVar9;
  undefined1 auVar7 [64];
  undefined1 auVar11 [16];
  undefined1 auVar12 [16];
  float fVar14;
  undefined1 auVar13 [16];
  undefined1 auVar15 [16];
  float local_58;
  float fStack_54;
  float fStack_50;
  float fStack_4c;
  undefined1 local_48 [16];
  long local_30;
  undefined1 extraout_var [56];
  
  plVar4 = DAT_01a1f100;
  local_30 = *DAT_01a1f100;
  auVar6 = *param_4;
  auVar1 = *param_5;
  fVar5 = auVar1._0_4_;
  *param_7 = fVar5;
  auVar1 = vpshufd_avx(auVar1,1);
  *param_8 = auVar1._0_4_;
  if (param_1 < DAT_01634484) {
    fVar8 = DAT_01634488 - param_1;
    *param_7 = fVar8 * auVar6._0_4_ + fVar5 * param_1;
    auVar6 = vpshufd_avx(auVar6,1);
    *param_8 = fVar8 * auVar6._0_4_ + auVar1._0_4_ * param_1;
  }
  auVar1 = vandnps_avx(_DAT_01ac62b0,*param_6);
  auVar6 = vsubps_avx(ZEXT816(0) << 0x20,*param_6);
  auVar6 = vandps_avx(_DAT_01ac62b0,auVar6);
  auVar6 = vorps_avx(auVar1,auVar6);
  auVar1 = vpshufd_avx(auVar6,0xd2);
  auVar7._0_8_ = FUN_00097c30(*param_7);
  auVar7._8_56_ = extraout_var;
  auVar11._0_4_ = (float)auVar7._0_8_ * auVar6._0_4_;
  fVar8 = (float)((ulong)auVar7._0_8_ >> 0x20);
  auVar11._4_4_ = fVar8 * auVar6._4_4_;
  auVar11._8_4_ = extraout_var._0_4_ * auVar6._8_4_;
  auVar11._12_4_ = extraout_var._4_4_ * auVar6._12_4_;
  auVar2 = vpshufd_avx(auVar11,0x55);
  auVar3 = vpshufd_avx(auVar11,0);
  auVar13 = vpshufd_avx(auVar7._0_16_,0xc9);
  local_58 = auVar1._0_4_;
  fStack_54 = auVar1._4_4_;
  fStack_50 = auVar1._8_4_;
  fStack_4c = auVar1._12_4_;
  auVar12._0_4_ = auVar13._0_4_ * local_58;
  auVar12._4_4_ = auVar13._4_4_ * fStack_54;
  auVar12._8_4_ = auVar13._8_4_ * fStack_50;
  auVar12._12_4_ = auVar13._12_4_ * fStack_4c;
  auVar1 = vpshufd_avx(auVar6,0xc9);
  auVar13 = vpshufd_avx(auVar7._0_16_,0xd2);
  auVar15._0_4_ = auVar13._0_4_ * auVar1._0_4_;
  auVar15._4_4_ = auVar13._4_4_ * auVar1._4_4_;
  auVar15._8_4_ = auVar13._8_4_ * auVar1._8_4_;
  auVar15._12_4_ = auVar13._12_4_ * auVar1._12_4_;
  auVar12 = vsubps_avx(auVar15,auVar12);
  auVar1 = vpshufd_avx(auVar11,0xaa);
  auVar13 = vpshufd_avx(auVar6,0xff);
  fVar5 = auVar13._0_4_;
  fVar9 = auVar13._4_4_;
  fVar10 = auVar13._8_4_;
  fVar14 = auVar13._12_4_;
  auVar13._0_4_ = fVar5 * fVar5;
  auVar13._4_4_ = fVar9 * fVar9;
  auVar13._8_4_ = fVar10 * fVar10;
  auVar13._12_4_ = fVar14 * fVar14;
  auVar13 = vsubps_avx(auVar13,_DAT_01ac63c0);
  fVar5 = fVar5 * auVar12._0_4_ +
          (float)auVar7._0_8_ * auVar13._0_4_ +
          auVar6._0_4_ * (auVar1._0_4_ + auVar3._0_4_ + auVar2._0_4_);
  fVar8 = fVar9 * auVar12._4_4_ +
          fVar8 * auVar13._4_4_ + auVar6._4_4_ * (auVar1._4_4_ + auVar3._4_4_ + auVar2._4_4_);
  fVar9 = fVar10 * auVar12._8_4_ +
          extraout_var._0_4_ * auVar13._8_4_ +
          auVar6._8_4_ * (auVar1._8_4_ + auVar3._8_4_ + auVar2._8_4_);
  fVar10 = fVar14 * auVar12._12_4_ +
           extraout_var._4_4_ * auVar13._12_4_ +
           auVar6._12_4_ * (auVar1._12_4_ + auVar3._12_4_ + auVar2._12_4_);
  auVar6._0_4_ = fVar5 + fVar5;
  auVar6._4_4_ = fVar8 + fVar8;
  auVar6._8_4_ = fVar9 + fVar9;
  auVar6._12_4_ = fVar10 + fVar10;
  local_48 = vandps_avx(auVar6,_DAT_01634410);
  FUN_00097a90(local_48,param_7,param_8);
  fVar5 = *param_7;
  if (*param_7 - *(float *)(param_3 + 4) < 0.0) {
    fVar5 = *(float *)(param_3 + 4);
  }
  fVar8 = *(float *)(param_3 + 8);
  if (fVar5 - *(float *)(param_3 + 8) < 0.0) {
    fVar8 = fVar5;
  }
  *param_7 = fVar8;
  fVar5 = *param_8;
  if (*param_8 - *(float *)(param_3 + 0xc) < 0.0) {
    fVar5 = *(float *)(param_3 + 0xc);
  }
  fVar8 = *(float *)(param_3 + 0x10);
  if (fVar5 - *(float *)(param_3 + 0x10) < 0.0) {
    fVar8 = fVar5;
  }
  *param_8 = fVar8;
  if (*plVar4 == local_30) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

