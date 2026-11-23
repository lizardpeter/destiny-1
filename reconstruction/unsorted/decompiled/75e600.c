
bool FUN_0075e600(void)

{
  float fVar1;
  char cVar2;
  char cVar3;
  undefined1 uVar4;
  undefined2 uVar5;
  undefined4 uVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  long lVar10;
  long lVar11;
  int iVar12;
  undefined8 unaff_RBX;
  float *pfVar13;
  float fVar14;
  float fVar15;
  undefined1 auVar16 [16];
  undefined1 auVar17 [64];
  undefined4 local_1a4;
  float local_1a0;
  undefined1 local_198 [32];
  undefined1 local_178 [320];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  uVar5 = FUN_0078df40();
  uVar6 = FUN_0078dfd0();
  FUN_00545b30(local_198,CONCAT62((int6)((ulong)unaff_RBX >> 0x10),uVar5) & 0xffffffff,uVar6);
  cVar2 = FUN_00545cb0(local_198);
  if (cVar2 == '\0') {
    cVar2 = '\0';
    goto LAB_0075e78e;
  }
  lVar10 = FUN_003db440();
  iVar7 = FUN_0010c810();
  cVar2 = '\x01';
  if (iVar7 == 4) goto LAB_0075e78e;
  if (lVar10 == 0) {
    cVar2 = '\0';
    goto LAB_0075e78e;
  }
  cVar3 = *(char *)(lVar10 + 0x47c4);
  cVar2 = '\0';
  if (cVar3 == -1) goto LAB_0075e78e;
  fVar15 = *(float *)(lVar10 + 0x47cc);
  fVar14 = (float)FUN_005461a0(local_198);
  fVar14 = fVar14 * *(float *)(lVar10 + 0x46b8);
  iVar8 = FUN_00546200(local_198);
  iVar7 = *(int *)(lVar10 + 0x4588);
  cVar2 = FUN_00b29220(0xd);
  fVar1 = fVar14;
  if (cVar2 != '\0') {
    lVar11 = FUN_0034e500();
    fVar1 = fVar14 * *(float *)(lVar11 + 0xa4);
    cVar2 = FUN_000e4d70(3,2);
    if (cVar2 != '\0') {
      if ((DAT_026c9900 == '\0') && (iVar9 = thunk_FUN_012aa7d6(&DAT_026c9900), iVar9 != 0)) {
        DAT_026c98f8 = FUN_000e4a10(s_world_controller_activity_manage_0164adb4);
        thunk_FUN_012aa7e6(&DAT_026c9900);
      }
      FUN_01008290((double)fVar14,(double)fVar1,local_178,
                   s_world_controller_activity_manage_0164adb4);
      FUN_000e4aa0(DAT_026c98f8,local_178);
    }
  }
  if (iVar7 < 1) {
    iVar9 = 0;
LAB_0075e8ac:
    local_1a4 = 0;
    local_1a0 = 0.0;
  }
  else {
    pfVar13 = (float *)(lVar10 + 0x4594);
    local_1a0 = 0.0;
    iVar9 = 0;
    iVar12 = iVar7;
    do {
      if (*(char *)(pfVar13 + -2) != cVar3) {
        fVar14 = fVar15 - *pfVar13;
        local_1a0 = local_1a0 + fVar14;
        iVar9 = iVar9 + (uint)(fVar1 < fVar14);
      }
      pfVar13 = pfVar13 + 5;
      iVar12 = iVar12 + -1;
    } while (iVar12 != 0);
    if (iVar7 < 2) goto LAB_0075e8ac;
    iVar12 = iVar7 + -1;
    local_1a0 = local_1a0 / (float)iVar12;
    pfVar13 = (float *)(lVar10 + 0x4594);
    auVar17 = ZEXT1664(ZEXT816(0) << 0x40);
    do {
      if (*(char *)(pfVar13 + -2) != cVar3) {
        fVar14 = local_1a0 - (fVar15 - *pfVar13);
        auVar17 = ZEXT464((uint)(auVar17._0_4_ + fVar14 * fVar14));
      }
      pfVar13 = pfVar13 + 5;
      iVar7 = iVar7 + -1;
    } while (iVar7 != 0);
    auVar16._0_4_ = auVar17._0_4_ / (float)iVar12;
    auVar16._4_12_ = auVar17._4_12_;
    auVar16 = vsqrtss_avx(auVar16,auVar16);
    local_1a4 = auVar16._0_4_;
  }
  fVar15 = (float)FUN_005461a0(local_198);
  cVar2 = '\0';
  if (((0 < iVar8) && (0.0 < fVar15)) && (iVar8 <= iVar9)) {
    cVar3 = FUN_000e4d70(3,3);
    cVar2 = '\x01';
    if (cVar3 != '\0') {
      if ((DAT_026c9910 == '\0') && (iVar7 = thunk_FUN_012aa7d6(&DAT_026c9910), iVar7 != 0)) {
        DAT_026c9908 = FUN_000e4a10(s_world_controller_activity_manage_0164ae36);
        thunk_FUN_012aa7e6(&DAT_026c9910);
      }
      cVar2 = '\x01';
      FUN_01008290((double)fVar1,local_178,s_world_controller_activity_manage_0164ae36,iVar9,iVar8);
      FUN_000e4aa0(DAT_026c9908,local_178);
    }
  }
  lVar10 = thunk_FUN_00768060();
  if (lVar10 != 0) {
    FUN_0076dbf0(local_1a0,local_1a4,lVar10,cVar2);
  }
LAB_0075e78e:
  if (*DAT_01a1f100 != local_38) {
    uVar4 = thunk_FUN_012aa7f6();
    return (bool)uVar4;
  }
  return cVar2 != '\0';
}

