
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_004aae60(undefined8 param_1,long param_2,float *param_3,undefined1 (*param_4) [16],
                 float *param_5,float *param_6)

{
  undefined1 auVar1 [16];
  long *plVar2;
  float fVar3;
  float fVar9;
  undefined1 auVar5 [16];
  float fVar7;
  float fVar8;
  undefined1 auVar4 [16];
  undefined1 auVar6 [64];
  undefined1 auVar10 [16];
  undefined1 auVar11 [16];
  undefined1 auVar12 [16];
  float fVar14;
  undefined1 auVar13 [16];
  float local_58;
  float fStack_54;
  float fStack_50;
  float fStack_4c;
  undefined1 local_48 [16];
  long local_38;
  undefined1 extraout_var [56];
  
  plVar2 = DAT_01a1f100;
  local_38 = *DAT_01a1f100;
  *param_5 = *param_3;
  *param_6 = param_3[1];
  auVar4._0_12_ = ZEXT812(0);
  auVar4._12_4_ = 0;
  auVar5 = vandnps_avx(_DAT_01ac62b0,*param_4);
  auVar4 = vsubps_avx(auVar4,*param_4);
  auVar4 = vandps_avx(_DAT_01ac62b0,auVar4);
  auVar4 = vorps_avx(auVar5,auVar4);
  auVar5 = vpshufd_avx(auVar4,0xd2);
  auVar6._0_8_ = FUN_00097c30(*param_5);
  auVar6._8_56_ = extraout_var;
  auVar1 = vpshufd_avx(auVar6._0_16_,0xc9);
  local_58 = auVar5._0_4_;
  fStack_54 = auVar5._4_4_;
  fStack_50 = auVar5._8_4_;
  fStack_4c = auVar5._12_4_;
  auVar10._0_4_ = auVar1._0_4_ * local_58;
  auVar10._4_4_ = auVar1._4_4_ * fStack_54;
  auVar10._8_4_ = auVar1._8_4_ * fStack_50;
  auVar10._12_4_ = auVar1._12_4_ * fStack_4c;
  auVar5 = vpshufd_avx(auVar4,0xc9);
  auVar1 = vpshufd_avx(auVar6._0_16_,0xd2);
  auVar11._0_4_ = auVar1._0_4_ * auVar5._0_4_;
  auVar11._4_4_ = auVar1._4_4_ * auVar5._4_4_;
  auVar11._8_4_ = auVar1._8_4_ * auVar5._8_4_;
  auVar11._12_4_ = auVar1._12_4_ * auVar5._12_4_;
  auVar11 = vsubps_avx(auVar11,auVar10);
  auVar12._0_4_ = (float)auVar6._0_8_ * auVar4._0_4_;
  fVar7 = (float)((ulong)auVar6._0_8_ >> 0x20);
  auVar12._4_4_ = fVar7 * auVar4._4_4_;
  auVar12._8_4_ = extraout_var._0_4_ * auVar4._8_4_;
  auVar12._12_4_ = extraout_var._4_4_ * auVar4._12_4_;
  auVar5 = vpshufd_avx(auVar12,0x55);
  auVar1 = vpshufd_avx(auVar12,0);
  auVar10 = vpshufd_avx(auVar4,0xff);
  fVar3 = auVar10._0_4_;
  fVar8 = auVar10._4_4_;
  fVar9 = auVar10._8_4_;
  fVar14 = auVar10._12_4_;
  auVar10 = vpshufd_avx(auVar12,0xaa);
  auVar13._0_4_ = fVar3 * fVar3;
  auVar13._4_4_ = fVar8 * fVar8;
  auVar13._8_4_ = fVar9 * fVar9;
  auVar13._12_4_ = fVar14 * fVar14;
  auVar12 = vsubps_avx(auVar13,_DAT_01ac63c0);
  fVar3 = fVar3 * auVar11._0_4_ +
          (float)auVar6._0_8_ * auVar12._0_4_ +
          auVar4._0_4_ * (auVar10._0_4_ + auVar1._0_4_ + auVar5._0_4_);
  fVar7 = fVar8 * auVar11._4_4_ +
          fVar7 * auVar12._4_4_ + auVar4._4_4_ * (auVar10._4_4_ + auVar1._4_4_ + auVar5._4_4_);
  fVar8 = fVar9 * auVar11._8_4_ +
          extraout_var._0_4_ * auVar12._8_4_ +
          auVar4._8_4_ * (auVar10._8_4_ + auVar1._8_4_ + auVar5._8_4_);
  fVar9 = fVar14 * auVar11._12_4_ +
          extraout_var._4_4_ * auVar12._12_4_ +
          auVar4._12_4_ * (auVar10._12_4_ + auVar1._12_4_ + auVar5._12_4_);
  auVar5._0_4_ = fVar3 + fVar3;
  auVar5._4_4_ = fVar7 + fVar7;
  auVar5._8_4_ = fVar8 + fVar8;
  auVar5._12_4_ = fVar9 + fVar9;
  local_48 = vandps_avx(auVar5,_DAT_01634400);
  FUN_00097a90(local_48,param_5,param_6);
  fVar3 = *param_5;
  if (*param_5 - *(float *)(param_2 + 4) < 0.0) {
    fVar3 = *(float *)(param_2 + 4);
  }
  fVar7 = *(float *)(param_2 + 8);
  if (fVar3 - *(float *)(param_2 + 8) < 0.0) {
    fVar7 = fVar3;
  }
  *param_5 = fVar7;
  fVar3 = *param_6;
  if (*param_6 - *(float *)(param_2 + 0xc) < 0.0) {
    fVar3 = *(float *)(param_2 + 0xc);
  }
  fVar7 = *(float *)(param_2 + 0x10);
  if (fVar3 - *(float *)(param_2 + 0x10) < 0.0) {
    fVar7 = fVar3;
  }
  *param_6 = fVar7;
  if (*plVar2 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

