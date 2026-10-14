
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00926320(undefined4 param_1,short *param_2,float *param_3)

{
  undefined1 auVar1 [16];
  long lVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  undefined1 auVar6 [16];
  float fVar7;
  
  fVar5 = DAT_0166b880;
  fVar4 = (float)(int)*param_2 * DAT_0166b880;
  *param_3 = fVar4;
  fVar3 = DAT_0166b884;
  fVar5 = (float)(int)param_2[1] * fVar5;
  param_3[1] = fVar5;
  if (((fVar4 <= DAT_0166b888) || (fVar7 = fVar3, fVar4 < DAT_0166b884)) &&
     (fVar7 = DAT_0166b888, DAT_0166b888 < fVar4)) {
    fVar7 = fVar4;
  }
  *param_3 = fVar7;
  if (((fVar5 <= DAT_0166b888) || (fVar5 < DAT_0166b884)) &&
     (fVar3 = DAT_0166b888, DAT_0166b888 < fVar5)) {
    fVar3 = fVar5;
  }
  param_3[1] = fVar3;
  if (((DAT_0273fbe9 != '\0') && (lVar2 = FUN_005287f0(param_1), lVar2 != 0)) &&
     ((*(long *)(lVar2 + 0x10) != 0 && (lVar2 = *(long *)(lVar2 + 0x10) + lVar2 + 0x10, lVar2 != 0))
     )) {
    auVar6 = ZEXT416((uint)(*param_3 * *param_3 + param_3[1] * param_3[1]));
    auVar6 = vsqrtss_avx(auVar6,auVar6);
    fVar4 = (float)FUN_00239650(lVar2 + 8);
    if (fVar4 < 0.0) {
      fVar4 = 0.0;
    }
    auVar1 = vandps_avx(ZEXT416((uint)auVar6._0_4_),_DAT_0166b8e0);
    fVar5 = DAT_0166b884;
    if (0.0 <= auVar1._0_4_ + DAT_0166b88c) {
      if (0.0 <= fVar4 + DAT_0166b888) {
        fVar4 = DAT_0166b884;
      }
      fVar5 = fVar4 / auVar6._0_4_;
    }
    *param_3 = fVar5 * *param_3;
    param_3[1] = fVar5 * param_3[1];
  }
  fVar5 = DAT_0166b880;
  fVar4 = (float)(int)param_2[2] * DAT_0166b880;
  param_3[2] = fVar4;
  fVar3 = DAT_0166b884;
  fVar5 = (float)(int)param_2[3] * fVar5;
  param_3[3] = fVar5;
  if (((fVar4 <= DAT_0166b888) || (fVar7 = fVar3, fVar4 < DAT_0166b884)) &&
     (fVar7 = DAT_0166b888, DAT_0166b888 < fVar4)) {
    fVar7 = fVar4;
  }
  param_3[2] = fVar7;
  if (((fVar5 <= DAT_0166b888) || (fVar5 < DAT_0166b884)) &&
     (fVar3 = DAT_0166b888, DAT_0166b888 < fVar5)) {
    fVar3 = fVar5;
  }
  param_3[3] = fVar3;
  if (((DAT_0273fbe9 != '\0') && (lVar2 = FUN_005287f0(param_1), lVar2 != 0)) &&
     ((*(long *)(lVar2 + 0x10) != 0 && (lVar2 = *(long *)(lVar2 + 0x10) + lVar2 + 0x10, lVar2 != 0))
     )) {
    auVar6 = ZEXT416((uint)(param_3[2] * param_3[2] + param_3[3] * param_3[3]));
    auVar6 = vsqrtss_avx(auVar6,auVar6);
    fVar4 = (float)FUN_00239650(lVar2 + 8);
    if (fVar4 < 0.0) {
      fVar4 = 0.0;
    }
    auVar1 = vandps_avx(ZEXT416((uint)auVar6._0_4_),_DAT_0166b8e0);
    fVar5 = DAT_0166b884;
    if (0.0 <= auVar1._0_4_ + DAT_0166b88c) {
      if (0.0 <= fVar4 + DAT_0166b888) {
        fVar4 = DAT_0166b884;
      }
      fVar5 = fVar4 / auVar6._0_4_;
    }
    param_3[2] = fVar5 * param_3[2];
    param_3[3] = fVar5 * param_3[3];
  }
  return;
}

