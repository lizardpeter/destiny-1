
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0088bc30(long param_1,long param_2,int param_3,undefined4 param_4,long param_5,long param_6
                 ,char param_7)

{
  int iVar1;
  undefined8 uVar2;
  char cVar3;
  undefined8 uVar4;
  undefined8 *puVar5;
  ushort *puVar6;
  long lVar7;
  float fVar8;
  undefined8 extraout_XMM0_Qa;
  undefined1 auVar9 [16];
  undefined1 auVar10 [16];
  undefined1 extraout_var [56];
  float fVar12;
  undefined1 auVar13 [16];
  undefined1 auVar11 [64];
  
  if ((((DAT_018def0c == param_7) && (*(int *)(param_6 + 0x1b334) != 0)) &&
      (*(int *)(param_1 + 0x10) != -1)) && (*(int *)(param_1 + 0x14) != -1)) {
    *(undefined1 *)(param_2 + 0x15d4) = 0x81;
    *(char *)(param_2 + 0x15d5) = (param_3 != 0) + -0x7f;
    *(undefined1 *)(param_2 + 0x15d6) = 0x81;
    *(undefined1 *)(param_2 + 0x15d7) = 0x81;
    FUN_00818a30(param_3,param_4,0,0,0);
    uVar2 = *(undefined8 *)(param_2 + 0x15c0);
    uVar4 = FUN_0082e420(1);
    FUN_007deb70(uVar2,uVar4,0);
    FUN_007dec20(*(undefined8 *)(param_2 + 0x15c0),*(undefined4 *)(param_1 + 0x14),0,0,0);
    FUN_007dee30(*(undefined8 *)(param_2 + 0x15c0),*(undefined4 *)(param_1 + 0x10));
    puVar5 = (undefined8 *)FUN_0082b940(param_2,0x36,0x10);
    iVar1 = *(int *)(param_6 + 0x1b334);
    puVar6 = (ushort *)FUN_00818ec0(6);
    auVar11._8_56_ = extraout_var;
    auVar11._0_8_ = extraout_XMM0_Qa;
    auVar9._0_4_ = (float)puVar6[1];
    auVar9._4_12_ = auVar11._4_12_;
    auVar10 = vandps_avx(auVar9,_DAT_01666760);
    fVar8 = DAT_01666708;
    if (0.0 <= auVar10._0_4_ + DAT_0166670c) {
      fVar8 = (float)*puVar6 / auVar9._0_4_;
    }
    fVar12 = DAT_01666714;
    if (iVar1 == 2) {
      fVar12 = DAT_01666710;
    }
    fVar8 = (DAT_01666708 - fVar12 * fVar8) * DAT_01666718;
    if (param_3 != 0) {
      fVar8 = fVar8 - DAT_018def08;
    }
    auVar10._0_12_ = ZEXT812(0);
    auVar10._12_4_ = 0;
    if (0.0 <= fVar8) {
      auVar13 = ZEXT416((uint)(fVar8 + fVar8));
    }
    else {
      auVar13._0_12_ = ZEXT812(0);
      auVar13._12_4_ = 0;
    }
    if ((param_5 != 0) && (auVar10 = ZEXT416((uint)DAT_01666708), *(char *)(param_5 + 0xe5) == '\0')
       ) {
      auVar10._0_12_ = ZEXT812(0);
      auVar10._12_4_ = 0;
    }
    auVar10 = vunpcklps_avx(auVar13,auVar10);
    *puVar5 = auVar10._0_8_;
    puVar5[1] = 0;
    lVar7 = FUN_0082cc20(0xfa);
    if ((lVar7 != 0) && (cVar3 = FUN_0082b490(param_2,lVar7), cVar3 != '\0')) {
      FUN_007e15d0(*(undefined8 *)(param_2 + 0x15c0),3,0,0,0xc,0,0,0);
    }
    FUN_0082ba20(param_2,0x36,0x10);
    *(undefined4 *)(param_2 + 0x15d4) = 0;
  }
  return;
}

