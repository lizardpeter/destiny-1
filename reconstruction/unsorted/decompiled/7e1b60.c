
void FUN_007e1b60(long param_1,uint param_2,undefined4 param_3)

{
  undefined1 auVar1 [16];
  undefined1 auVar2 [16];
  long *plVar3;
  uint uVar4;
  uint uVar5;
  float fVar6;
  undefined1 in_ZMM0 [64];
  undefined8 local_20;
  long local_18;
  undefined1 auVar7 [16];
  
  plVar3 = DAT_01a1f100;
  local_18 = *DAT_01a1f100;
  local_20 = 0;
  fVar6 = in_ZMM0._0_4_;
  auVar7 = in_ZMM0._0_16_;
  if (param_2 < 0x40) {
    if (param_2 == 8) {
      auVar1 = vpshufd_avx(auVar7,1);
      auVar7 = vmovhlps_avx(auVar7,auVar7);
      local_20 = (ulong)((int)(long)(auVar7._0_4_ * DAT_0165feac) << 4 |
                        (int)(long)(auVar1._0_4_ * DAT_0165feac) << 2 |
                        (uint)(long)(fVar6 * DAT_0165feac));
    }
    else {
      if (param_2 == 0x10) {
        auVar2 = vpshufd_avx(auVar7,1);
        auVar1 = vmovhlps_avx(auVar7,auVar7);
        auVar7 = vpshufd_avx(auVar7,3);
        uVar5 = (int)(long)(auVar1._0_4_ * DAT_0165fea8) << 8 |
                (int)(long)(auVar2._0_4_ * DAT_0165fea8) << 4 | (uint)(long)(fVar6 * DAT_0165fea8);
        uVar4 = (int)(long)(auVar7._0_4_ * DAT_0165fea8) << 0xc;
      }
      else {
        if (param_2 != 0x20) goto LAB_007e1ce5;
        auVar2 = vpshufd_avx(auVar7,1);
        auVar1 = vmovhlps_avx(auVar7,auVar7);
        auVar7 = vpshufd_avx(auVar7,3);
        uVar5 = (int)(long)(auVar1._0_4_ * DAT_0165fea4) << 0x10 |
                (int)(long)(auVar2._0_4_ * DAT_0165fea4) << 8 | (uint)(long)(fVar6 * DAT_0165fea4);
        uVar4 = (int)(long)(auVar7._0_4_ * DAT_0165fea4) << 0x18;
      }
      local_20 = (ulong)(uVar4 | uVar5);
    }
  }
  else if (param_2 == 0x40) {
    auVar2 = vpshufd_avx(auVar7,1);
    auVar1 = vmovhlps_avx(auVar7,auVar7);
    auVar7 = vpshufd_avx(auVar7,3);
    uVar4 = (int)(long)(auVar7._0_4_ * DAT_0165fea4) << 0x18 |
            (int)(long)(auVar1._0_4_ * DAT_0165fea4) << 0x10 |
            (int)(long)(auVar2._0_4_ * DAT_0165fea4) << 8 | (uint)(long)(fVar6 * DAT_0165fea4);
    local_20 = CONCAT44(uVar4,uVar4);
  }
LAB_007e1ce5:
  FUN_00f7ed40(*(undefined8 *)(param_1 + 0x50),param_3,&local_20);
  if (*plVar3 != local_18) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

