
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0102ca90(undefined1 (*param_1) [16],undefined8 param_2,undefined8 param_3,
                 undefined8 param_4)

{
  float fVar1;
  float fVar2;
  float fVar3;
  char cVar4;
  float fVar5;
  float fVar6;
  undefined8 uVar7;
  undefined8 extraout_XMM0_Qb;
  undefined8 uVar9;
  undefined1 auVar8 [64];
  undefined1 auVar10 [16];
  undefined1 auVar11 [16];
  undefined1 auVar12 [16];
  undefined1 auVar13 [16];
  undefined1 auVar14 [16];
  float local_28;
  float fStack_24;
  float fStack_20;
  float fStack_1c;
  undefined1 extraout_var [56];
  
  cVar4 = FUN_00073430(param_4);
  if (cVar4 == '\0') {
    uVar7 = FUN_00072d70(param_4,&DAT_016271d4,0x13);
    uVar9 = extraout_XMM0_Qb;
  }
  else {
    cVar4 = FUN_00073430(param_4);
    uVar7 = _DAT_01626f90;
    uVar9 = uRam0000000001626f98;
    if (cVar4 == '\0') {
      uVar7 = _DAT_01626fa0;
      uVar9 = uRam0000000001626fa8;
    }
  }
  fVar5 = (float)FUN_00072c20(DAT_01627144,DAT_01627148,param_4,s_facing_angle_016271d9,7,0,0);
  fVar5 = fVar5 * DAT_0162714c;
  fVar6 = (float)thunk_FUN_012aaa36(0,0);
  auVar8._0_8_ = thunk_FUN_012aaa36(fVar5,1,0);
  auVar8._8_56_ = extraout_var;
  local_28 = (float)uVar7;
  fStack_24 = (float)((ulong)uVar7 >> 0x20);
  fStack_20 = (float)uVar9;
  fStack_1c = (float)((ulong)uVar9 >> 0x20);
  auVar10._0_4_ = local_28 * local_28;
  auVar10._4_4_ = fStack_24 * fStack_24;
  auVar10._8_4_ = fStack_20 * fStack_20;
  auVar10._12_4_ = fStack_1c * fStack_1c;
  auVar14 = vpshufd_avx(auVar10,0x55);
  auVar13 = vpshufd_avx(auVar10,0);
  auVar10 = vpshufd_avx(auVar10,0xaa);
  auVar11._0_4_ = auVar10._0_4_ + auVar13._0_4_ + auVar14._0_4_;
  auVar11._4_4_ = auVar10._4_4_ + auVar13._4_4_ + auVar14._4_4_;
  auVar11._8_4_ = auVar10._8_4_ + auVar13._8_4_ + auVar14._8_4_;
  auVar11._12_4_ = auVar10._12_4_ + auVar13._12_4_ + auVar14._12_4_;
  auVar10 = vrsqrtps_avx(auVar11);
  fVar5 = auVar10._0_4_;
  fVar1 = auVar10._4_4_;
  fVar2 = auVar10._8_4_;
  fVar3 = auVar10._12_4_;
  auVar14._0_4_ = fVar5 * fVar5 * auVar11._0_4_ * (float)DAT_01626fb0;
  auVar14._4_4_ = fVar1 * fVar1 * auVar11._4_4_ * DAT_01626fb0._4_4_;
  auVar14._8_4_ = fVar2 * fVar2 * auVar11._8_4_ * DAT_01626fb0._8_4_;
  auVar14._12_4_ = fVar3 * fVar3 * auVar11._12_4_ * DAT_01626fb0._12_4_;
  auVar14 = vsubps_avx(_DAT_01626fb0,auVar14);
  auVar12._0_4_ = fVar5 + fVar5 * auVar14._0_4_;
  auVar12._4_4_ = fVar1 + fVar1 * auVar14._4_4_;
  auVar12._8_4_ = fVar2 + fVar2 * auVar14._8_4_;
  auVar12._12_4_ = fVar3 + fVar3 * auVar14._12_4_;
  auVar13 = vcmpps_avx(auVar12,auVar12,0);
  auVar14 = vandps_avx(auVar13,auVar12);
  auVar13 = vandnps_avx(auVar13,auVar10);
  auVar14 = vorps_avx(auVar13,auVar14);
  auVar13._0_4_ = local_28 * auVar14._0_4_;
  auVar13._4_4_ = fStack_24 * auVar14._4_4_;
  auVar13._8_4_ = fStack_20 * auVar14._8_4_;
  auVar13._12_4_ = fStack_1c * auVar14._12_4_;
  auVar14 = vcmpps_avx(auVar14,_DAT_01626fc0,0);
  auVar14 = vandnps_avx(auVar14,auVar13);
  auVar13 = vpshufd_avx(auVar14,1);
  auVar13 = vinsertps_avx(ZEXT416((uint)(fVar6 * auVar14._0_4_)),
                          ZEXT416((uint)(fVar6 * auVar13._0_4_)),0x10);
  auVar14 = vmovhlps_avx(auVar14,auVar14);
  auVar14 = vinsertps_avx(auVar13,ZEXT416((uint)(fVar6 * auVar14._0_4_)),0x20);
  auVar14 = vinsertps_avx(auVar14,auVar8._0_16_,0x30);
  *param_1 = auVar14;
  return;
}

