
void FUN_007dfac0(float param_1,float param_2,long param_3,uint param_4,uint param_5,uint param_6,
                 uint param_7)

{
  float fVar1;
  long *plVar2;
  float fVar3;
  undefined1 auVar4 [16];
  undefined1 auVar5 [16];
  float fVar6;
  undefined1 auVar7 [16];
  float fVar8;
  float fVar9;
  float local_50;
  float local_4c;
  float local_48;
  float local_44;
  float local_40;
  float local_3c;
  long local_38;
  
  plVar2 = DAT_01a1f100;
  fVar8 = DAT_0165fe80;
  local_38 = *DAT_01a1f100;
  fVar3 = (float)param_6 * DAT_0165fe80;
  local_3c = DAT_0165fe84 / (param_2 - param_1);
  fVar6 = (float)param_7 * DAT_0165fe88;
  local_48 = param_1 / (param_2 - param_1);
  fVar1 = (float)param_5 + (float)param_7 * DAT_0165fe80;
  fVar9 = (float)param_4 + fVar3;
  *(uint *)(param_3 + 0x2578) = param_4;
  *(uint *)(param_3 + 0x257c) = param_5;
  *(uint *)(param_3 + 0x2580) = param_6;
  *(uint *)(&DAT_00002584 + param_3) = param_7;
  *(float *)(&DAT_00002588 + param_3) = param_1;
  *(float *)(&DAT_0000258c + param_3) = param_2;
  local_50 = fVar9;
  local_4c = fVar1;
  local_44 = fVar3;
  local_40 = fVar6;
  FUN_00f80340(*(undefined8 *)(param_3 + 0x50),0,&local_44,&local_50);
  FUN_00f80440(*(undefined8 *)(param_3 + 0x50),param_4,param_5,param_6,param_7);
  auVar5 = vroundss_avx(ZEXT416((uint)DAT_0165fe8c),ZEXT416((uint)(fVar9 * DAT_0165fe8c + fVar8)),1)
  ;
  auVar4 = ZEXT416((uint)(fVar1 * DAT_0165fe8c + fVar8));
  auVar7 = vroundss_avx(auVar4,auVar4,1);
  FUN_00f7ebb0(*(undefined8 *)(param_3 + 0x50),(int)auVar5._0_4_,(int)auVar7._0_4_);
  auVar4 = vandps_avx(ZEXT416((uint)fVar3),ZEXT416(DAT_0165fe20));
  fVar3 = auVar4._0_4_;
  fVar8 = (float)((int)auVar5._0_4_ << 4);
  auVar4 = vandps_avx(ZEXT416((uint)fVar6),ZEXT416(DAT_0165fe20));
  fVar6 = auVar4._0_4_;
  auVar4 = vminss_avx(ZEXT416((uint)(((fVar9 - fVar3) - fVar8) + DAT_0165fe94)),
                      ZEXT416((uint)(fVar8 + ((DAT_0165fe90 - fVar3) - fVar9))));
  auVar5._0_4_ = auVar4._0_4_ / fVar3;
  auVar5._4_12_ = auVar4._4_12_;
  fVar9 = (float)((int)auVar7._0_4_ << 4);
  auVar4 = vminss_avx(ZEXT416((uint)(((fVar1 - fVar6) - fVar9) + DAT_0165fe94)),
                      ZEXT416((uint)(fVar9 + ((DAT_0165fe90 - fVar6) - fVar1))));
  auVar7._0_4_ = auVar4._0_4_ / fVar6;
  auVar7._4_12_ = auVar4._4_12_;
  FUN_00f7ec30(auVar5._0_8_,auVar7._0_8_,*(undefined8 *)(param_3 + 0x50));
  *(uint *)(FUN_00002590 + param_3) = param_4;
  *(uint *)(param_3 + 0x2594) = param_5;
  *(uint *)(param_3 + 0x2598) = param_6;
  *(uint *)(param_3 + 0x259c) = param_7;
  if (*plVar2 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

