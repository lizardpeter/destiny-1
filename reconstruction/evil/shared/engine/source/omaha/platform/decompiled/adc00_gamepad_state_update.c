
void FUN_000adc00(ulong param_1,uint *param_2,byte *param_3,undefined8 param_4,int param_5)

{
  float *pfVar1;
  float *pfVar2;
  byte bVar3;
  ushort uVar4;
  undefined1 auVar5 [16];
  undefined1 auVar6 [16];
  undefined1 auVar7 [16];
  undefined1 auVar8 [16];
  float fVar9;
  uint uVar10;
  int iVar11;
  uint uVar12;
  int iVar13;
  long lVar14;
  long lVar15;
  byte bVar16;
  int iVar17;
  byte *pbVar18;
  byte bVar19;
  int iVar20;
  byte bVar21;
  uint *puVar22;
  undefined1 auVar23 [16];
  undefined1 auVar24 [16];
  undefined1 auVar25 [12];
  undefined1 auVar26 [12];
  undefined1 auVar29 [16];
  undefined1 auVar27 [16];
  undefined1 auVar28 [16];
  
  bVar19 = (byte)param_2[2];
  bVar3 = *(byte *)((long)param_2 + 9);
  *param_3 = bVar19;
  bVar21 = param_3[2];
  if (bVar21 < bVar19) {
    bVar16 = 0xff;
    if (param_3[4] + 1 < 0x100) {
      bVar16 = (byte)(param_3[4] + 1);
    }
    param_3[4] = bVar16;
    iVar11 = (uint)*(ushort *)(param_3 + 0x1a) + param_5;
    iVar17 = iVar11;
    if ((-1 < iVar11) && (iVar17 = 0xffff, iVar11 < 0x10000)) {
      iVar17 = iVar11;
    }
    *(short *)(param_3 + 0x1a) = (short)iVar17;
    bVar16 = 0;
    if (0x1f < bVar19) {
      bVar16 = bVar19 - 0x20;
    }
    if (bVar21 < bVar16) {
LAB_000adc76:
      param_3[2] = bVar16;
    }
  }
  else {
    param_3[4] = 0;
    param_3[0x1a] = 0;
    param_3[0x1b] = 0;
    bVar16 = 0xff;
    if (bVar19 < 0xc0) {
      bVar16 = bVar19 + 0x40;
    }
    if (bVar16 < bVar21) goto LAB_000adc76;
  }
  param_3[1] = bVar3;
  bVar19 = param_3[3];
  if (bVar19 < bVar3) {
    bVar21 = 0xff;
    if (param_3[5] + 1 < 0x100) {
      bVar21 = (byte)(param_3[5] + 1);
    }
    param_3[5] = bVar21;
    iVar11 = (uint)*(ushort *)(param_3 + 0x1c) + param_5;
    iVar17 = iVar11;
    if ((-1 < iVar11) && (iVar17 = 0xffff, iVar11 < 0x10000)) {
      iVar17 = iVar11;
    }
    *(short *)(param_3 + 0x1c) = (short)iVar17;
    bVar21 = 0;
    if (0x1f < bVar3) {
      bVar21 = bVar3 - 0x20;
    }
    if (bVar21 <= bVar19) goto LAB_000adcec;
  }
  else {
    param_3[5] = 0;
    param_3[0x1c] = 0;
    param_3[0x1d] = 0;
    bVar21 = 0xff;
    if (bVar3 < 0xc0) {
      bVar21 = bVar3 + 0x40;
    }
    if (bVar19 <= bVar21) goto LAB_000adcec;
  }
  param_3[3] = bVar21;
LAB_000adcec:
  lVar14 = 0xf;
  puVar22 = &DAT_015b5ab0;
  do {
    if ((*param_2 & *puVar22) == 0) {
      param_3[lVar14 + -9] = 0;
      iVar17 = 0;
    }
    else {
      bVar19 = 0xff;
      if (param_3[lVar14 + -9] + 1 < 0x100) {
        bVar19 = (byte)(param_3[lVar14 + -9] + 1);
      }
      uVar4 = *(ushort *)(param_3 + lVar14 * 2);
      param_3[lVar14 + -9] = bVar19;
      iVar17 = (uint)uVar4 + param_5;
      if ((-1 < iVar17) && (0xffff < iVar17)) {
        iVar17 = 0xffff;
      }
    }
    *(short *)(param_3 + lVar14 * 2) = (short)iVar17;
    uVar12 = DAT_016136c0;
    puVar22 = puVar22 + 1;
    lVar14 = lVar14 + 1;
  } while ((short)lVar14 != 0x1e);
  pfVar1 = (float *)(&DAT_01ad4ee8 + (param_1 & 0xffffffff) * 0x18);
  pfVar2 = (float *)(&DAT_01ad4ee4 + (param_1 & 0xffffffff) * 0x18);
  lVar14 = 0;
  *(short *)(param_3 + 0x44) = (short)(((uint)(byte)param_2[1] * 0xffff) / 0xff) + -0x8000;
  *(short *)(param_3 + 0x46) =
       (short)(((*(byte *)((long)param_2 + 5) ^ 0xff) * 0xffff) / 0xff) + -0x8000;
  *(short *)(param_3 + 0x48) =
       (short)(((uint)*(byte *)((long)param_2 + 6) * 0xffff) / 0xff) + -0x8000;
  *(short *)(param_3 + 0x4a) =
       (short)(((*(byte *)((long)param_2 + 7) ^ 0xff) * 0xffff) / 0xff) + -0x8000;
  *(uint *)(param_3 + 0xb4) = param_2[10] ^ uVar12;
  *(uint *)(param_3 + 0xb0) = param_2[0xb] ^ uVar12;
  *(uint *)(param_3 + 0xb8) = param_2[0xc] ^ uVar12;
  bVar19 = (byte)param_2[0xd];
  do {
    if ((int)(uint)bVar19 <= (int)lVar14) goto LAB_000adec8;
    lVar15 = lVar14 * 2;
    lVar14 = lVar14 + 1;
  } while ((byte)param_2[lVar15 + 0x10] != param_3[0x70]);
  if ((int)lVar14 == 0) {
LAB_000adec8:
    param_3[0x71] = 0;
    uVar12 = 1;
  }
  else {
    param_3[0x71] = param_3[0x71] + 1;
    auVar5._4_12_ = auRam00000000016136d4;
    auVar5._0_4_ = DAT_016136d0;
    auVar5 = vandps_avx(ZEXT416((uint)*pfVar2),auVar5);
    auVar23._12_4_ = 0;
    auVar23._0_12_ = ZEXT812(0);
    auVar23 = auVar23 << 0x20;
    auVar25 = ZEXT812(0);
    if (0.0 <= auVar5._0_4_ + DAT_016136e0) {
      auVar25._4_8_ = 0;
      auVar25._0_4_ = (float)(ushort)param_2[lVar14 * 2 + 0xd] / *pfVar2;
    }
    auVar27._12_4_ = 0;
    auVar27._0_12_ = auVar25;
    auVar6._4_12_ = auRam00000000016136d4;
    auVar6._0_4_ = DAT_016136d0;
    auVar5 = vandps_avx(ZEXT416((uint)*pfVar1),auVar6);
    if (0.0 <= auVar5._0_4_ + DAT_016136e0) {
      auVar23 = ZEXT416((uint)((float)*(ushort *)((long)param_2 + lVar14 * 8 + 0x36) / *pfVar1));
    }
    auVar5 = vunpcklps_avx(auVar27,auVar23);
    auVar5 = vshufps_avx(auVar5,ZEXT416(DAT_016136e4),0x14);
    *(undefined1 (*) [16])(param_3 + 0x60) = auVar5;
    uVar12 = 2;
  }
  lVar14 = 0;
  do {
    if ((int)(uint)bVar19 <= (int)lVar14) goto LAB_000adf8c;
    lVar15 = lVar14 * 2;
    lVar14 = lVar14 + 1;
  } while ((byte)param_2[lVar15 + 0x10] != param_3[0xa0]);
  if ((int)lVar14 == 0) {
LAB_000adf8c:
    param_3[0xa1] = 0;
  }
  else {
    param_3[0xa1] = param_3[0xa1] + 1;
    auVar7._4_12_ = auRam00000000016136d4;
    auVar7._0_4_ = DAT_016136d0;
    auVar5 = vandps_avx(ZEXT416((uint)*pfVar2),auVar7);
    auVar24._12_4_ = 0;
    auVar24._0_12_ = ZEXT812(0);
    auVar24 = auVar24 << 0x20;
    auVar26 = ZEXT812(0);
    if (0.0 <= auVar5._0_4_ + DAT_016136e0) {
      auVar26._4_8_ = 0;
      auVar26._0_4_ = (float)(ushort)param_2[lVar14 * 2 + 0xd] / *pfVar2;
    }
    auVar28._12_4_ = 0;
    auVar28._0_12_ = auVar26;
    auVar8._4_12_ = auRam00000000016136d4;
    auVar8._0_4_ = DAT_016136d0;
    auVar5 = vandps_avx(ZEXT416((uint)*pfVar1),auVar8);
    if (0.0 <= auVar5._0_4_ + DAT_016136e0) {
      auVar24 = ZEXT416((uint)((float)*(ushort *)((long)param_2 + lVar14 * 8 + 0x36) / *pfVar1));
    }
    auVar5 = vunpcklps_avx(auVar28,auVar24);
    auVar5 = vshufps_avx(auVar5,ZEXT416(DAT_016136e4),0x14);
    *(undefined1 (*) [16])(param_3 + 0x90) = auVar5;
    if (1 < uVar12) {
      return;
    }
  }
  uVar10 = DAT_016136e4;
  fVar9 = DAT_016136e0;
  uVar12 = DAT_016136d0;
  if (bVar19 != 0) {
    lVar14 = 0;
    do {
      iVar17 = -1;
      iVar11 = 0;
      for (pbVar18 = param_3 + 0x71;
          (iVar20 = iVar11, *pbVar18 == 0 ||
          (iVar20 = iVar17, (byte)param_2[lVar14 * 2 + 0x10] != pbVar18[-1]));
          pbVar18 = pbVar18 + 0x30) {
        iVar13 = iVar11 + 1;
        iVar11 = -1;
        iVar17 = iVar20;
        if (1 < iVar13) break;
        iVar11 = iVar13;
      }
      if ((iVar11 == -1) && (iVar17 != -1)) {
        lVar15 = (long)iVar17 * 0x30;
        param_3[lVar15 + 0x70] = (byte)param_2[lVar14 * 2 + 0x10];
        param_3[lVar15 + 0x71] = 1;
        auVar23 = ZEXT816(0) << 0x40;
        auVar5 = vandps_avx(ZEXT416((uint)*pfVar2),ZEXT416(uVar12));
        auVar29._0_12_ = ZEXT812(0);
        auVar29._12_4_ = 0;
        if (0.0 <= auVar5._0_4_ + fVar9) {
          auVar29 = ZEXT416((uint)((float)(ushort)param_2[lVar14 * 2 + 0xf] / *pfVar2));
        }
        auVar5 = vandps_avx(ZEXT416((uint)*pfVar1),ZEXT416(uVar12));
        if (0.0 <= auVar5._0_4_ + fVar9) {
          auVar23 = ZEXT416((uint)((float)*(ushort *)((long)param_2 + lVar14 * 8 + 0x3e) / *pfVar1))
          ;
        }
        auVar5 = vunpcklps_avx(auVar29,auVar23);
        auVar5 = vshufps_avx(auVar5,ZEXT416(uVar10),0x14);
        *(undefined1 (*) [16])(param_3 + lVar15 + 0x50) = auVar5;
        *(undefined1 (*) [16])(param_3 + lVar15 + 0x60) =
             *(undefined1 (*) [16])(param_3 + lVar15 + 0x50);
      }
      lVar14 = lVar14 + 1;
    } while ((int)lVar14 < (int)(uint)bVar19);
  }
  return;
}

