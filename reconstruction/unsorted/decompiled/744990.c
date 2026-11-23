
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00744990(undefined4 param_1,undefined4 param_2,int param_3,uint param_4,undefined1 *param_5
                 )

{
  int *piVar1;
  undefined1 auVar2 [16];
  undefined8 uVar3;
  undefined8 uVar4;
  undefined8 uVar5;
  undefined8 uVar6;
  undefined8 uVar7;
  undefined8 uVar8;
  bool bVar9;
  int *piVar10;
  char cVar11;
  char cVar12;
  char cVar13;
  char cVar14;
  undefined1 uVar15;
  short sVar16;
  uint uVar17;
  int iVar18;
  undefined4 uVar19;
  int iVar20;
  int iVar21;
  undefined8 uVar22;
  ulong uVar23;
  long lVar24;
  int *piVar25;
  long lVar26;
  ulong uVar27;
  long lVar28;
  long lVar29;
  long lVar30;
  uint uVar31;
  ulong uVar32;
  uint local_360;
  undefined1 local_350 [224];
  undefined1 local_270 [40];
  undefined1 local_248;
  undefined8 local_240;
  undefined8 uStack_238;
  undefined8 uStack_230;
  undefined8 uStack_228;
  undefined1 local_220 [16];
  undefined1 auStack_210 [16];
  int local_200 [30];
  undefined8 local_188 [19];
  char local_ee;
  undefined8 local_e0;
  undefined8 uStack_d8;
  undefined8 uStack_d0;
  ulong uStack_c8;
  ulong local_c0;
  undefined8 uStack_b8;
  undefined8 uStack_b0;
  undefined8 uStack_a8;
  undefined8 local_a0;
  undefined8 uStack_98;
  undefined8 uStack_90;
  undefined8 uStack_88;
  undefined8 local_80;
  undefined8 uStack_78;
  undefined8 uStack_70;
  undefined8 uStack_68;
  long local_60;
  
  local_60 = *DAT_01a1f100;
  uVar17 = FUN_00923110();
  thunk_FUN_0073d590(param_5);
  FUN_00928560(param_4);
  FUN_00928560(param_4);
  iVar18 = FUN_0010c430();
  cVar11 = FUN_008e3b10(param_3);
  cVar12 = FUN_001dad30();
  cVar13 = FUN_000014d0();
  uVar22 = FUN_00958d30();
  uVar19 = FUN_009230f0(param_3);
  uVar19 = FUN_009231e0(uVar19);
  cVar14 = FUN_00959fc0(uVar22,uVar19);
  if ((((((cVar11 == '\0') && (cVar12 == '\0')) && (cVar13 == '\0')) &&
       ((iVar18 != 7 && (iVar18 != 9)))) && (cVar14 == '\0')) &&
     ((*DAT_026c6ee0 != -1 &&
      ((lVar28 = (long)param_3, DAT_026c6ee0[lVar28 * 0x20 + 4] != -1 ||
       (piVar1 = DAT_026c6ee0 + lVar28 * 0x20 + 4, FUN_00744850(param_3), *piVar1 != -1)))))) {
    local_200[0x10] = 0;
    local_200[0x11] = 0;
    local_200[0x12] = 0;
    local_200[0x13] = 0;
    local_200[0x14] = 0;
    local_200[0x15] = 0;
    local_200[0x16] = 0;
    local_200[0x17] = 0;
    local_200[8] = 0;
    local_200[9] = 0;
    local_200[10] = 0;
    local_200[0xb] = 0;
    local_200[0xc] = 0;
    local_200[0xd] = 0;
    local_200[0xe] = 0;
    local_200[0xf] = 0;
    local_200[0] = 0;
    local_200[1] = 0;
    local_200[2] = 0;
    local_200[3] = 0;
    local_200[4] = 0;
    local_200[5] = 0;
    local_200[6] = 0;
    local_200[7] = 0;
    local_220 = ZEXT816(0);
    auStack_210 = ZEXT816(0);
    local_240 = 0;
    uStack_238 = 0;
    uStack_230 = 0;
    uStack_228 = 0;
    FUN_0073d590(local_350);
    piVar10 = DAT_026c6ee0;
    lVar24 = *DAT_01a238a0;
    lVar30 = *(long *)(DAT_026c6ee0 + lVar28 * 0x20 + 6);
    piVar1 = DAT_026c6ee0 + lVar28 * 0x20 + 0xc;
    uVar31 = DAT_026c6ee0[lVar28 * 0x20 + 4] >> 0xd;
    lVar26 = (ulong)((uVar31 >> 0x12 | 0x3ff) & uVar31) * 0x40;
    lVar29 = *(long *)(lVar24 + 0x10 + lVar26);
    uVar23 = (ulong)((DAT_026c6ee0[lVar28 * 0x20 + 4] & 0x1fffU) * *(int *)(lVar24 + 0x30 + lVar26))
    ;
    lVar29 = (lVar29 + uVar23) -
             ((long)*(int *)(lVar24 + 0x34 + lVar26) & *(ulong *)(lVar29 + 8 + uVar23));
    uVar31 = FUN_00923110(param_3);
    local_c0 = (ulong)(uint)local_c0;
    lVar24 = FUN_0091ab30(param_3);
    *(undefined4 *)(lVar30 + 0x88 + lVar29) = param_1;
    *(undefined4 *)(lVar30 + 0x8c + lVar29) = param_2;
    *(undefined4 *)(lVar30 + 0x84 + lVar29) = 0;
    piVar25 = (int *)(lVar30 + 0x80 + lVar29);
    *piVar25 = *piVar25 + 1;
    FUN_0062a590(piVar1);
    cVar11 = '\0';
    if (uVar31 != 0xffffffff) {
      uVar23 = (ulong)((uVar31 & 0x1fff) * DAT_02689800);
      uVar32 = (ulong)DAT_02689818;
      uVar27 = (ulong)((*(uint *)(((uVar23 + DAT_026897f8) -
                                  (*(ulong *)(DAT_026897f8 + 8 + uVar23) & uVar32)) + 0x68) & 0x1fff
                       ) * DAT_02689800);
      iVar18 = piVar10[lVar28 * 0x20 + 0x21];
      uVar23 = *(ulong *)(DAT_026897f8 + 8 + uVar27);
      lVar30 = DAT_026897f8 + uVar27;
      iVar20 = FUN_00bd5bf0(uVar31);
      if (iVar18 != iVar20) {
        FUN_00bd5b80(uVar31,piVar10 + lVar28 * 0x20 + 0x21);
      }
      cVar11 = FUN_00bd1c50((lVar30 - (uVar32 & uVar23)) + 0x9d0);
      local_248 = 0;
      cVar12 = FUN_00bd51e0(uVar31,local_270);
      if (((cVar12 != '\0') && (piVar10[lVar28 * 0x20 + 0x22] == 3)) &&
         (iVar18 = FUN_00354cf0(local_270), iVar18 != 3)) {
        iVar18 = FUN_003554c0(local_270);
        piVar10[lVar28 * 0x20 + 0x22] = iVar18;
      }
    }
    if (param_4 < 4) {
      lVar30 = FUN_00928560(param_4);
      FUN_00928520(local_188,param_4);
      local_80 = 0;
      uStack_78 = 0;
      uStack_70 = 0;
      uStack_68 = 0;
      local_a0 = 0;
      uStack_98 = 0;
      uStack_90 = 0;
      uStack_88 = 0;
      local_c0 = 0;
      uStack_b8 = 0;
      uStack_b0 = 0;
      uStack_a8 = 0;
      local_e0 = 0;
      uStack_d8 = 0;
      uStack_d0 = 0;
      uStack_c8 = 0;
      FUN_0062a590(&uStack_b0);
      uStack_70 = CONCAT44(uStack_70._4_4_,0xffffffff);
      uVar31 = FUN_00923110(param_3);
      if (uVar31 != 0xffffffff) {
        lVar29 = FUN_00bcf4a0(uVar31,3);
        lVar26 = 0;
        if (lVar29 != 0) {
          uVar23 = (ulong)((*(uint *)(lVar29 + 0x18) & 0x1fff) * DAT_02689800);
          lVar26 = ((DAT_026897f8 + uVar23) -
                   ((long)DAT_02689818 & *(ulong *)(DAT_026897f8 + 8 + uVar23))) + 0x9d0;
        }
        iVar18 = FUN_00bd3540(uVar31);
        *(undefined2 *)(lVar24 + 0x4e) = 0xffff;
        if (((*(char *)(lVar26 + 1) != -1) &&
            (uVar23 = (ulong)((uVar31 & 0x1fff) * DAT_02689800),
            uVar23 = (ulong)((*(uint *)(((uVar23 + DAT_026897f8) -
                                        (*(ulong *)(DAT_026897f8 + 8 + uVar23) & (long)DAT_02689818)
                                        ) + 0x68) & 0x1fff) * DAT_02689800),
            cVar12 = FUN_00bd1b80((DAT_026897f8 + uVar23) -
                                  ((long)DAT_02689818 & *(ulong *)(DAT_026897f8 + 8 + uVar23))),
            cVar12 != '\0')) && ((iVar18 == -1 || (cVar12 = FUN_00bc9790(iVar18), cVar12 != '\0'))))
        {
          *(short *)(lVar24 + 0x4e) = (short)*(char *)(lVar26 + 1);
        }
      }
      FUN_0091b500(param_1,param_2,param_3,param_4,lVar30,lVar24,&local_e0);
      cVar12 = FUN_008e3ae0(param_3);
      if (cVar12 == '\0') {
        FUN_00920b90(uStack_d0._4_4_,uStack_c8 & 0xffffffff,param_1,param_2,param_3,&local_e0);
      }
      if ((local_ee == '\0' || cVar11 != '\0') || (*(char *)(lVar24 + 0x140) != '\0')) {
LAB_00744ef8:
        *(undefined4 *)(lVar24 + 0xcc) = 0;
        *(undefined1 *)(lVar24 + 200) = 0;
      }
      else {
        auVar2 = vandps_avx(ZEXT416((uint)local_e0),_DAT_01649c10);
        if ((auVar2._0_4_ <= _DAT_01649c30) ||
           (((*(float *)(lVar30 + 0x2d0) != 0.0 || (*(float *)(lVar30 + 0x2d4) != 0.0)) ||
            (NAN(*(float *)(lVar30 + 0x2d4)))))) goto LAB_00744ef8;
        lVar29 = FUN_00526f80();
        iVar18 = *(int *)(lVar24 + 0xcc) + 1;
        if (*(int *)(lVar24 + 0xcc) < 0) {
          iVar18 = 0;
        }
        iVar20 = *(int *)(lVar29 + 0x1d8);
        if (iVar20 < iVar18) {
          iVar18 = iVar20;
        }
        *(int *)(lVar24 + 0xcc) = iVar18;
        *(bool *)(lVar24 + 200) = iVar18 == iVar20;
      }
      auVar2 = vunpcklps_avx(ZEXT416(*(uint *)(lVar30 + 0x2c0)),ZEXT416(*(uint *)(lVar30 + 0x2c4)));
      local_240 = auVar2._0_8_;
      uStack_238 = 0;
      piVar25 = (int *)(lVar30 + 0x10);
      lVar29 = 0;
      auVar2 = vunpcklps_avx(ZEXT416(*(uint *)(lVar30 + 0x2cc)),ZEXT416(*(uint *)(lVar30 + 0x2d4)));
      uStack_230 = auVar2._0_8_;
      uStack_228 = 0;
      auVar2 = vunpcklps_avx(ZEXT416(*(uint *)(lVar24 + 0x18)),ZEXT416(*(uint *)(lVar24 + 0x1c)));
      local_220 = vmovlhps_avx(auVar2,ZEXT416(*(uint *)(lVar24 + 0x20)));
      auVar2 = vunpcklps_avx(ZEXT416(*(uint *)(lVar24 + 0x24)),ZEXT416(*(uint *)(lVar24 + 0x28)));
      auStack_210 = vmovlhps_avx(auVar2,ZEXT416(*(uint *)(lVar24 + 0x2c)));
      do {
        iVar18 = 0;
        if (((*(byte *)(piVar25 + -3) & 1) == 0) &&
           ((*piVar25 == 0x25 || (*piVar25 == piVar25[-1])))) {
          iVar18 = piVar25[-2];
        }
        local_200[lVar29] = iVar18;
        piVar25 = piVar25 + 5;
        lVar29 = lVar29 + 1;
      } while ((int)lVar29 != 0x15);
      *(undefined8 *)(piVar1 + 4) = local_a0;
      *(undefined8 *)(piVar1 + 6) = uStack_98;
      *(undefined8 *)piVar1 = uStack_b0;
      *(undefined8 *)(piVar1 + 2) = uStack_a8;
      *(undefined8 *)(piVar1 + 0xc) = local_80;
      *(undefined8 *)(piVar1 + 0xe) = uStack_78;
      *(undefined8 *)(piVar1 + 8) = uStack_90;
      *(undefined8 *)(piVar1 + 10) = uStack_88;
      piVar10[lVar28 * 0x20 + 0x1c] = (int)uStack_70;
    }
    uVar31 = DAT_026c6ee0[lVar28 * 0x20 + 4] >> 0xd;
    lVar26 = (ulong)((uVar31 >> 0x12 | 0x3ff) & uVar31) * 0x40;
    lVar24 = *(long *)(DAT_026c6ee0 + lVar28 * 0x20 + 6);
    lVar30 = *DAT_01a238a0;
    bVar9 = false;
    lVar29 = *(long *)(lVar30 + 0x10 + lVar26);
    uVar23 = (ulong)((DAT_026c6ee0[lVar28 * 0x20 + 4] & 0x1fffU) * *(int *)(lVar30 + 0x30 + lVar26))
    ;
    lVar30 = (lVar29 + uVar23) -
             ((long)*(int *)(lVar30 + 0x34 + lVar26) & *(ulong *)(lVar29 + 8 + uVar23));
    iVar18 = *(int *)(lVar24 + 0x20 + lVar30);
    if (((iVar18 != 0) && (iVar18 != -1)) && (*(int *)(lVar24 + 0x28 + lVar30) != -1)) {
      FUN_00353510(lVar24 + 0x20 + lVar30,&local_240,local_350);
      bVar9 = true;
    }
    piVar1 = DAT_026c6ee0;
    iVar18 = FUN_00923110(param_3);
    thunk_FUN_012aa7c6(param_5,local_350,0xdc);
    uVar22 = *(undefined8 *)(piVar1 + lVar28 * 0x20 + 0xc);
    uVar3 = *(undefined8 *)(piVar1 + lVar28 * 0x20 + 0xc + 2);
    uVar4 = *(undefined8 *)(piVar1 + lVar28 * 0x20 + 0x10 + 2);
    uVar5 = *(undefined8 *)(piVar1 + lVar28 * 0x20 + 0x14);
    uVar6 = *(undefined8 *)(piVar1 + lVar28 * 0x20 + 0x14 + 2);
    uVar7 = *(undefined8 *)(piVar1 + lVar28 * 0x20 + 0x18);
    uVar8 = *(undefined8 *)(piVar1 + lVar28 * 0x20 + 0x18 + 2);
    *(undefined8 *)(param_5 + 0xa0) = *(undefined8 *)(piVar1 + lVar28 * 0x20 + 0x10);
    *(undefined8 *)(param_5 + 0xa8) = uVar4;
    *(undefined8 *)(param_5 + 0x90) = uVar22;
    *(undefined8 *)(param_5 + 0x98) = uVar3;
    *(undefined8 *)(param_5 + 0xc0) = uVar7;
    *(undefined8 *)(param_5 + 200) = uVar8;
    *(undefined8 *)(param_5 + 0xb0) = uVar5;
    *(undefined8 *)(param_5 + 0xb8) = uVar6;
    FUN_00072050(local_188,piVar1[lVar28 * 0x20 + 0x1c]);
    *(undefined8 *)(param_5 + 0xd0) = local_188[0];
    *(undefined8 *)(param_5 + 0x7c) = *(undefined8 *)(piVar1 + lVar28 * 0x20 + 0x21);
    if ((iVar18 != -1) && (cVar11 = FUN_005c4590(), cVar11 == '\0')) {
      iVar20 = *(int *)(param_5 + 0x80);
      if ((iVar20 == -1) || (iVar21 = FUN_00bd5340(iVar18,(int)(short)iVar20), iVar21 == -1)) {
        sVar16 = FUN_00bd7310(iVar18,(int)(short)iVar20,0);
        iVar18 = -1;
        if (sVar16 != 3 || iVar20 != -1) {
          iVar18 = (int)sVar16;
        }
        *(int *)(param_5 + 0x80) = iVar18;
      }
    }
    uVar15 = FUN_009828d0(param_4);
    param_5[0x3a] = uVar15;
    if (bVar9) {
      cVar11 = FUN_003f6ff0();
      if (cVar11 != '\0') {
        local_360 = *(uint *)(param_5 + 4) & 0x1000000;
        uVar19 = *(undefined4 *)(param_5 + 0x3c);
        thunk_FUN_0073d590(param_5);
        if (uVar17 != 0xffffffff) {
          uVar23 = (ulong)((uVar17 & 0x1fff) * DAT_02689800);
          uVar32 = (ulong)DAT_02689818;
          uVar27 = (ulong)((*(uint *)(((uVar23 + DAT_026897f8) -
                                      (*(ulong *)(DAT_026897f8 + 8 + uVar23) & uVar32)) + 0x68) &
                           0x1fff) * DAT_02689800);
          uVar23 = *(ulong *)(DAT_026897f8 + 8 + uVar27);
          lVar30 = DAT_026897f8 + uVar27;
          uVar17 = FUN_00913f50(uVar17);
          lVar28 = *(long *)(DAT_0273ea80 + 8);
          lVar24 = FUN_0091ab30(param_3);
          *(undefined4 *)(param_5 + 8) = *(undefined4 *)(lVar24 + 0x18);
          *(undefined4 *)(param_5 + 0xc) = *(undefined4 *)(lVar24 + 0x1c);
          *(undefined4 *)(param_5 + 0x10) = *(undefined4 *)(lVar24 + 0x20);
          lVar24 = ((ulong)uVar17 & 0xffff) * 0x2af0;
          uVar17 = *(uint *)(param_5 + 4) | 1;
          if ((*(uint *)((lVar30 - (uVar32 & uVar23)) + 0x9e4) & 1) == 0) {
            uVar17 = *(uint *)(param_5 + 4) & 0xfffffffe;
          }
          *(uint *)(param_5 + 4) = uVar17;
          *param_5 = *(undefined1 *)(lVar28 + 0x2930 + lVar24);
          param_5[1] = *(undefined1 *)(lVar28 + 0x2931 + lVar24);
          *(undefined8 *)(param_5 + 0x7c) = *(undefined8 *)(lVar28 + 0x29ac + lVar24);
          param_5[0x3a] = *(undefined1 *)(lVar28 + 0x296a + lVar24);
        }
        cVar11 = FUN_003f7050();
        if (cVar11 != '\0') {
          *(uint *)(param_5 + 4) = local_360;
          *(undefined4 *)(param_5 + 0x3c) = uVar19;
        }
      }
      goto LAB_007453b6;
    }
  }
  if (uVar17 != 0xffffffff) {
    uVar23 = (ulong)((uVar17 & 0x1fff) * DAT_02689800);
    uVar32 = (ulong)DAT_02689818;
    uVar27 = (ulong)((*(uint *)(((uVar23 + DAT_026897f8) -
                                (*(ulong *)(DAT_026897f8 + 8 + uVar23) & uVar32)) + 0x68) & 0x1fff)
                    * DAT_02689800);
    uVar23 = *(ulong *)(DAT_026897f8 + 8 + uVar27);
    lVar30 = DAT_026897f8 + uVar27;
    uVar17 = FUN_00913f50();
    lVar28 = *(long *)(DAT_0273ea80 + 8);
    lVar24 = FUN_0091ab30(param_3);
    *(undefined4 *)(param_5 + 8) = *(undefined4 *)(lVar24 + 0x18);
    *(undefined4 *)(param_5 + 0xc) = *(undefined4 *)(lVar24 + 0x1c);
    *(undefined4 *)(param_5 + 0x10) = *(undefined4 *)(lVar24 + 0x20);
    lVar24 = ((ulong)uVar17 & 0xffff) * 0x2af0;
    uVar17 = *(uint *)(param_5 + 4) | 1;
    if ((*(uint *)((lVar30 - (uVar32 & uVar23)) + 0x9e4) & 1) == 0) {
      uVar17 = *(uint *)(param_5 + 4) & 0xfffffffe;
    }
    *(uint *)(param_5 + 4) = uVar17;
    *param_5 = *(undefined1 *)(lVar28 + 0x2930 + lVar24);
    param_5[1] = *(undefined1 *)(lVar28 + 0x2931 + lVar24);
    *(undefined8 *)(param_5 + 0x7c) = *(undefined8 *)(lVar28 + 0x29ac + lVar24);
    param_5[0x3a] = *(undefined1 *)(lVar28 + 0x296a + lVar24);
  }
LAB_007453b6:
  if (*DAT_01a1f100 != local_60) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

