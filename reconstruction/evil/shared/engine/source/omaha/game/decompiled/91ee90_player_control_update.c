
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0091ee90(undefined4 *param_1,undefined4 *param_2)

{
  undefined4 uVar1;
  float fVar2;
  undefined4 uVar3;
  undefined1 auVar4 [16];
  undefined8 uVar5;
  undefined8 uVar6;
  undefined8 uVar7;
  undefined8 uVar8;
  undefined8 uVar9;
  undefined8 uVar10;
  undefined8 uVar11;
  undefined8 uVar12;
  undefined8 uVar13;
  undefined8 uVar14;
  undefined8 uVar15;
  byte *pbVar16;
  undefined8 uVar17;
  undefined8 uVar18;
  undefined8 uVar19;
  undefined8 uVar20;
  byte *pbVar21;
  byte *pbVar22;
  char cVar23;
  byte bVar24;
  byte bVar25;
  char cVar26;
  short sVar27;
  undefined2 uVar28;
  uint uVar29;
  int iVar30;
  int iVar31;
  int iVar32;
  uint uVar33;
  undefined4 uVar34;
  undefined8 uVar35;
  long lVar36;
  undefined8 *puVar37;
  uint *puVar38;
  long lVar39;
  ulong uVar40;
  long lVar41;
  ulong uVar42;
  long lVar43;
  byte bVar44;
  long lVar45;
  byte bVar46;
  ulong uVar47;
  float fVar48;
  float fVar49;
  undefined8 extraout_XMM0_Qb;
  float fVar50;
  float local_26c;
  float local_264;
  uint local_250 [2];
  uint local_248;
  undefined4 uStack_244;
  long local_240;
  undefined4 local_20c;
  float local_1e8 [3];
  float local_1dc;
  float local_1d8;
  float local_1d4;
  undefined1 local_1d0 [4];
  int local_1cc;
  undefined1 local_1c0;
  undefined1 local_1bf;
  undefined4 local_1bc;
  uint local_1b8;
  uint local_1b4;
  undefined4 local_1b0;
  undefined8 local_1a0 [2];
  undefined4 local_190;
  byte local_180;
  undefined8 local_170 [2];
  byte local_160;
  undefined4 local_150;
  undefined4 local_14c;
  undefined4 local_148;
  undefined8 local_144;
  int local_13c;
  undefined8 local_130;
  undefined8 uStack_128;
  undefined8 local_120;
  undefined8 uStack_118;
  undefined8 local_110;
  undefined8 uStack_108;
  undefined8 local_100;
  undefined8 uStack_f8;
  undefined1 local_f0 [8];
  undefined4 local_e8;
  undefined8 local_e0;
  undefined8 uStack_d8;
  undefined8 uStack_d0;
  ulong uStack_c8;
  undefined8 local_c0;
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
  uVar34 = *param_2;
  uVar1 = *param_1;
  uVar35 = 0;
  uVar29 = FUN_009230f0(0);
  FUN_009013b0(0);
  if ((uVar29 == 0xffffffff) || (cVar23 = FUN_00906f70(), cVar23 != '\0')) goto LAB_009200d6;
  iVar30 = FUN_009231e0(uVar29);
  pbVar22 = DAT_0273eb28;
  cVar23 = FUN_000014d0();
  bVar24 = 0;
  if (cVar23 != '\0') {
    bVar24 = FUN_000014d0();
    bVar24 = bVar24 ^ 1;
  }
  lVar36 = *(long *)(DAT_0273ea80 + 8);
  lVar45 = ((ulong)uVar29 & 0xffff) * 0x2af0;
  FUN_004cbcc0(*(undefined4 *)(lVar36 + 0x644 + lVar45),local_250);
  uVar29 = FUN_00071f60(pbVar22 + 0x1a8);
  if (((uVar29 != local_250[0]) || (*(uint *)(pbVar22 + 0x1b0) != local_248)) ||
     (*(long *)(pbVar22 + 0x1b8) != local_240)) {
    iVar31 = FUN_00071f60(pbVar22 + 0x1a8);
    bVar46 = 0;
    bVar44 = 0;
    if (iVar31 != -1) {
      uVar29 = (int)*(uint *)(pbVar22 + 0x1b0) >> 0xd;
      lVar39 = (ulong)((uVar29 >> 0x12 | 0x3ff) & uVar29) * 0x40;
      lVar43 = *DAT_01a238a0;
      lVar41 = *(long *)(lVar43 + 0x10 + lVar39);
      uVar40 = (ulong)((*(uint *)(pbVar22 + 0x1b0) & 0x1fff) * *(int *)(lVar43 + 0x30 + lVar39));
      lVar43 = (lVar41 + uVar40) -
               ((long)*(int *)(lVar43 + 0x34 + lVar39) & *(ulong *)(lVar41 + 8 + uVar40));
      bVar44 = *(byte *)(*(long *)(pbVar22 + 0x1b8) + 0x24 + lVar43);
      bVar46 = *(byte *)(*(long *)(pbVar22 + 0x1b8) + 0x25 + lVar43);
    }
    local_26c = 0.0;
    if (local_248 == 0xffffffff) {
LAB_0091f084:
      local_264 = 0.0;
    }
    else {
      lVar39 = (ulong)(((uint)((int)local_248 >> 0xd) >> 0x12 | 0x3ff) & (int)local_248 >> 0xd) *
               0x40;
      lVar43 = *DAT_01a238a0;
      lVar41 = *(long *)(lVar43 + 0x10 + lVar39);
      uVar40 = (ulong)((local_248 & 0x1fff) * *(int *)(lVar43 + 0x30 + lVar39));
      lVar43 = (lVar41 + uVar40) -
               ((long)*(int *)(lVar43 + 0x34 + lVar39) & *(ulong *)(lVar41 + 8 + uVar40));
      bVar46 = bVar46 | *(byte *)(local_240 + 0x68 + lVar43);
      bVar44 = bVar44 | *(byte *)(local_240 + 0x26 + lVar43);
      if (local_250[0] == 0xffffffff) goto LAB_0091f084;
      lVar43 = local_240 + 0x20 + lVar43;
      uVar40 = (ulong)((local_250[0] & 0x1fff) * DAT_02689800);
      lVar41 = (DAT_026897f8 + uVar40) -
               ((long)DAT_02689818 & *(ulong *)(DAT_026897f8 + 8 + uVar40));
      local_264 = (float)FUN_004ccec0(lVar43,lVar41);
      local_26c = (float)FUN_004ccef0(lVar43,lVar41);
    }
    if (((bVar44 != 0) || (bVar46 != 0)) && (iVar31 = FUN_006ed9f0(local_20c), iVar31 != -1)) {
      uVar3 = *(undefined4 *)(pbVar22 + 0x20);
      uVar35 = FUN_00090a10(&local_e0);
      FUN_00bd4d50(uVar3,uVar35);
      FUN_00097a90(&local_e0,&local_1d4,local_1e8);
      uVar35 = FUN_00090a10(local_1d0);
      FUN_00bd4dc0(iVar31,uVar35);
      FUN_00097a90(local_1d0,&local_1dc,&local_1d8);
      if (bVar44 != 0) {
        local_1e8[0] = local_264 + local_1d8;
      }
      if (bVar46 != 0) {
        local_1d4 = local_26c + local_1dc;
      }
      local_e0 = FUN_00097c30(local_1d4,local_1e8[0]);
      uStack_d8 = extraout_XMM0_Qb;
      uVar35 = FUN_00057f80(&local_e0);
      FUN_009205f0(0,uVar35);
    }
  }
  pbVar21 = DAT_0273eb28;
  if (lVar36 + lVar45 == 0 || bVar24 != 0) {
    lVar36 = FUN_00928560(iVar30);
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
    FUN_0091e000(uVar1,uVar34,0,iVar30,lVar36,&local_e0);
    cVar23 = FUN_009828d0(iVar30);
    if (cVar23 != '\0') {
      uStack_c8 = 0;
      uStack_d0 = 0;
      uStack_d8 = 0;
      local_c0 = (ulong)((uint)local_c0 & 0x81);
      uStack_b8 = 0;
      FUN_0062a590(&uStack_b0);
      uStack_70 = CONCAT44(uStack_70._4_4_,0xffffffff);
    }
    bVar24 = FUN_008e3b10(0);
    uVar35 = FUN_00958d30();
    bVar44 = FUN_00959fc0(uVar35,iVar30);
    bVar46 = FUN_009299b0();
    bVar25 = FUN_003f6ff0();
    bVar25 = bVar25 | bVar46 | bVar44 | bVar24;
    if (bVar25 == 0) {
      if (pbVar21[0x12] != 0) {
        fVar49 = *(float *)(pbVar21 + 0x18);
        fVar50 = *(float *)(pbVar21 + 0x14);
        fVar48 = (float)FUN_00591b80();
        if (fVar48 <= DAT_0166b704) {
          fVar49 = *(float *)(pbVar21 + 0x14);
        }
        else {
          fVar2 = *(float *)(pbVar21 + 0x1c);
          if (fVar2 <= fVar48) {
            fVar49 = *(float *)(pbVar21 + 0x18);
            *(float *)(pbVar21 + 0x14) = fVar49;
            pbVar21[0x1c] = 0;
            pbVar21[0x1d] = 0;
            pbVar21[0x1e] = 0;
            pbVar21[0x1f] = 0;
          }
          else {
            fVar49 = (fVar49 - fVar50) * (fVar48 / fVar2) + *(float *)(pbVar21 + 0x14);
            *(float *)(pbVar21 + 0x14) = fVar49;
            *(float *)(pbVar21 + 0x1c) = fVar2 - fVar48;
          }
        }
        auVar4 = vandps_avx(ZEXT416((uint)(fVar49 + DAT_0166b708)),_DAT_0166b620);
        if ((auVar4._0_4_ < DAT_0166b704) &&
           (auVar4 = vandps_avx(ZEXT416((uint)(*(float *)(pbVar21 + 0x18) + DAT_0166b708)),
                                _DAT_0166b620), auVar4._0_4_ < DAT_0166b704)) {
          pbVar21[0x12] = 0;
        }
        if (((fVar49 <= 0.0) || (fVar50 = DAT_0166b70c, fVar49 < DAT_0166b70c)) &&
           (fVar50 = 0.0, 0.0 < fVar49)) {
          fVar50 = fVar49;
        }
        *(float *)(pbVar21 + 0x14) = fVar50;
        local_e0 = CONCAT44(fVar50 * local_e0._4_4_,fVar50 * (float)local_e0);
        uStack_d0 = CONCAT44(fVar50 * uStack_d0._4_4_,fVar50 * (float)uStack_d0);
        uStack_c8 = CONCAT44(uStack_c8._4_4_,fVar50 * (float)uStack_c8);
        fVar49 = fVar50 * uStack_b8._4_4_;
        uStack_b8 = CONCAT44(fVar49,(undefined4)uStack_b8);
        if (fVar50 < DAT_0166b704) {
          uStack_d8 = 0;
          local_c0 = 0;
          uStack_b8 = CONCAT44(fVar49,(undefined4)uStack_b8) & 0xffffffff00001000;
        }
      }
    }
    else {
      uVar29 = (uint)local_c0 & 0x781;
      uVar34 = (undefined4)uStack_b8;
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
      uStack_b8 = CONCAT44(uStack_b8._4_4_,uVar34) & 0xffffffff00001000;
      local_c0 = CONCAT44(local_c0._4_4_,(uint)local_c0 | uVar29);
    }
    pbVar16 = DAT_0273eb28;
    if ((uStack_b8 & 4) != 0) {
      *DAT_0273eb28 = *DAT_0273eb28 | 1;
    }
    if ((local_c0 & 0x800000) != 0) {
      *pbVar16 = *pbVar16 | 8;
    }
    uVar40 = local_c0 >> 0x20;
    if ((local_c0 & 0x10) != 0) {
      pbVar16[1] = pbVar16[1] | 1;
      uVar40 = (ulong)local_c0._4_4_;
    }
    if ((uVar40 & 0x10) != 0) {
      *pbVar16 = *pbVar16 | 2;
      uVar40 = (ulong)local_c0._4_4_;
    }
    if ((uVar40 & 0x20) != 0) {
      *pbVar16 = *pbVar16 | 4;
      uVar40 = (ulong)local_c0._4_4_;
    }
    if ((uVar40 & 1) != 0) {
      *pbVar16 = *pbVar16 | 0x40;
      uVar40 = (ulong)local_c0._4_4_;
    }
    if ((uVar40 & 2) != 0) {
      *pbVar16 = *pbVar16 | 0x80;
    }
    if ((uStack_b8 & 0x1000) != 0) {
      pbVar16[3] = pbVar16[3] | 2;
    }
    uVar40 = (ulong)*(uint *)(lVar36 + 0x1b0);
    if ((((*(byte *)(lVar36 + 4 + uVar40 * 0x14) & 1) == 0) &&
        ((iVar31 = *(int *)(lVar36 + 0x10 + uVar40 * 0x14), iVar31 == 0x25 ||
         (iVar31 == *(int *)(lVar36 + 0xc + uVar40 * 0x14))))) &&
       (*(char *)(lVar36 + 2 + uVar40 * 0x14) != '\0')) {
      pbVar16[1] = pbVar16[1] | 2;
    }
    uVar40 = (ulong)*(uint *)(lVar36 + 0x1dc);
    if ((((*(byte *)(lVar36 + 4 + uVar40 * 0x14) & 1) == 0) &&
        ((iVar31 = *(int *)(lVar36 + 0x10 + uVar40 * 0x14), iVar31 == 0x25 ||
         (iVar31 == *(int *)(lVar36 + 0xc + uVar40 * 0x14))))) &&
       (*(char *)(lVar36 + 2 + uVar40 * 0x14) != '\0')) {
      pbVar16[2] = pbVar16[2] | 0x10;
    }
    uVar40 = (ulong)*(uint *)(lVar36 + 0x1e0);
    if (((*(byte *)(lVar36 + 4 + uVar40 * 0x14) & 1) == 0) &&
       (((iVar31 = *(int *)(lVar36 + 0x10 + uVar40 * 0x14), iVar31 == 0x25 ||
         (iVar31 == *(int *)(lVar36 + 0xc + uVar40 * 0x14))) &&
        (*(char *)(lVar36 + 2 + uVar40 * 0x14) != '\0')))) {
      pbVar16[2] = pbVar16[2] | 0x20;
    }
    if ((((*(byte *)(lVar36 + 0x2c) & 1) == 0) &&
        ((*(int *)(lVar36 + 0x38) == 0x25 || (*(int *)(lVar36 + 0x38) == *(int *)(lVar36 + 0x34)))))
       && (*(char *)(lVar36 + 0x2a) != '\0')) {
      pbVar16[3] = pbVar16[3] | 4;
    }
    if ((((*(byte *)(lVar36 + 0x40) & 1) == 0) &&
        ((*(int *)(lVar36 + 0x4c) == 0x25 || (*(int *)(lVar36 + 0x4c) == *(int *)(lVar36 + 0x48)))))
       && (*(char *)(lVar36 + 0x3e) != '\0')) {
      pbVar16[3] = pbVar16[3] | 8;
    }
    if (((*(byte *)(lVar36 + 0x54) & 1) == 0) &&
       (((*(int *)(lVar36 + 0x60) == 0x25 || (*(int *)(lVar36 + 0x60) == *(int *)(lVar36 + 0x5c)))
        && (*(char *)(lVar36 + 0x52) != '\0')))) {
      pbVar16[3] = pbVar16[3] | 0x10;
    }
    if ((((*(byte *)(lVar36 + 0x68) & 1) == 0) &&
        ((*(int *)(lVar36 + 0x74) == 0x25 || (*(int *)(lVar36 + 0x74) == *(int *)(lVar36 + 0x70)))))
       && (*(char *)(lVar36 + 0x66) != '\0')) {
      pbVar16[3] = pbVar16[3] | 0x20;
    }
    if ((float)uStack_c8 <= 0.0) {
      if ((float)uStack_c8 < 0.0) {
        pbVar16[1] = pbVar16[1] | 0x20;
      }
    }
    else {
      pbVar16[1] = pbVar16[1] | 0x10;
    }
    if (uStack_d0._4_4_ <= 0.0) {
      if (uStack_d0._4_4_ < 0.0) {
        pbVar16[1] = pbVar16[1] | 0x80;
      }
    }
    else {
      pbVar16[1] = pbVar16[1] | 0x40;
    }
    if ((float)local_e0 <= 0.0) {
      if ((float)local_e0 < 0.0) {
        pbVar16[2] = pbVar16[2] | 2;
      }
    }
    else {
      pbVar16[2] = pbVar16[2] | 1;
    }
    if (local_e0._4_4_ <= 0.0) {
      if (local_e0._4_4_ < 0.0) {
        pbVar16[2] = pbVar16[2] | 8;
      }
    }
    else {
      pbVar16[2] = pbVar16[2] | 4;
    }
    if (uStack_b8._4_4_ <= 0.0) {
      if (uStack_b8._4_4_ < 0.0) {
        pbVar16[3] = pbVar16[3] | 1;
      }
    }
    else {
      pbVar16[2] = pbVar16[2] | 0x80;
    }
    if ((pbVar16[4] & 1) == 0) {
      uVar29 = *(uint *)(pbVar16 + 8);
      if ((uVar29 & 1) != 0) {
        uVar33 = uVar29 | 1;
        if ((uStack_b8 & 4) == 0) {
          uVar33 = uVar29 & 0xfffffffe;
        }
        *(uint *)(pbVar16 + 8) = uVar33;
        goto LAB_0091f8f5;
      }
    }
    else {
LAB_0091f8f5:
      uStack_b8 = uStack_b8 & 0xfffffffffffffff1 | 8;
    }
    if ((pbVar16[4] & 2) == 0) {
      uVar29 = *(uint *)(pbVar16 + 8);
      if ((uVar29 & 2) != 0) {
        uVar33 = uVar29 | 2;
        if ((local_c0 & 0x1000000000) == 0) {
          uVar33 = uVar29 & 0xfffffffd;
        }
        *(uint *)(pbVar16 + 8) = uVar33;
        goto LAB_0091f930;
      }
    }
    else {
LAB_0091f930:
      local_c0 = local_c0 & 0xffffffefffffffff;
    }
    if ((pbVar16[4] & 4) == 0) {
      uVar29 = *(uint *)(pbVar16 + 8);
      if ((uVar29 & 4) != 0) {
        uVar33 = uVar29 | 4;
        if ((local_c0 & 0x2000000000) == 0) {
          uVar33 = uVar29 & 0xfffffffb;
        }
        *(uint *)(pbVar16 + 8) = uVar33;
        local_c0 = local_c0 & 0xffffffdfffffffff;
      }
    }
    else {
      local_c0 = local_c0 & 0xffffffdfffffffff;
    }
    puVar38 = (uint *)(pbVar16 + 8);
    uVar29 = *puVar38;
    if ((uVar29 & 0x4000) != 0) {
      auVar4 = vminss_avx(ZEXT416((uint)uStack_d0._4_4_),ZEXT816(0));
      uStack_d0 = CONCAT44(auVar4._0_4_,(float)uStack_d0);
      uVar29 = *puVar38;
    }
    if ((uVar29 & 0x8000) != 0) {
      auVar4 = vmaxss_avx(ZEXT416((uint)uStack_d0._4_4_),ZEXT816(0) << 0x40);
      uStack_d0 = CONCAT44(auVar4._0_4_,(float)uStack_d0);
      uVar29 = *puVar38;
    }
    if ((uVar29 & 0x1000) != 0) {
      auVar4 = vminss_avx(ZEXT416((uint)(float)uStack_c8),ZEXT816(0) << 0x40);
      uStack_c8 = CONCAT44(uStack_c8._4_4_,auVar4._0_4_);
      uVar29 = *puVar38;
    }
    if ((uVar29 & 0x2000) != 0) {
      auVar4 = vmaxss_avx(ZEXT416((uint)(float)uStack_c8),ZEXT816(0) << 0x40);
      uStack_c8 = CONCAT44(uStack_c8._4_4_,auVar4._0_4_);
    }
    if ((pbVar21[0x10] != 0) && ((local_c0 & 0x1000000000) != 0)) {
      pbVar21[0x10] = 0;
      pbVar21[0x11] = 0;
    }
    if ((pbVar21[0x11] != 0) && ((local_c0 & 0x2000000000) != 0)) {
      pbVar21[0x10] = 0;
      pbVar21[0x11] = 0;
    }
    lVar36 = DAT_026897f8;
    if (*(uint *)(pbVar21 + 0x20) == 0xffffffff) {
      bVar24 = FUN_008e3ae0(0);
      if (((bVar24 | bVar25) & 1) == 0) {
        FUN_00920b90(uStack_d0._4_4_,uStack_c8 & 0xffffffff,uVar1,0);
      }
    }
    else {
      uVar40 = (ulong)((*(uint *)(pbVar21 + 0x20) & 0x1fff) * DAT_02689800);
      uVar47 = (ulong)DAT_02689818;
      uVar42 = (ulong)((*(uint *)(((uVar40 + DAT_026897f8) -
                                  (*(ulong *)(DAT_026897f8 + 8 + uVar40) & uVar47)) + 0x68) & 0x1fff
                       ) * DAT_02689800);
      iVar31 = *(int *)(pbVar21 + 100);
      uVar40 = *(ulong *)(DAT_026897f8 + 8 + uVar42);
      iVar32 = FUN_00bd5bf0();
      if (iVar31 != iVar32) {
        FUN_00bd5b80(*(undefined4 *)(pbVar21 + 0x20),pbVar21 + 100);
      }
      lVar36 = (lVar36 + uVar42) - (uVar47 & uVar40);
      sVar27 = -1;
      if (*(int *)(pbVar21 + 0x68) == -1) {
LAB_0091fafa:
        sVar27 = FUN_00bd7310(*(undefined4 *)(pbVar21 + 0x20),(int)sVar27,0);
        iVar31 = (int)sVar27;
        *(int *)(pbVar21 + 0x68) = iVar31;
      }
      else {
        sVar27 = (short)*(int *)(pbVar21 + 0x68);
        iVar31 = FUN_00bd5340(*(undefined4 *)(pbVar21 + 0x20),(int)sVar27);
        if (iVar31 == -1) goto LAB_0091fafa;
        iVar31 = *(int *)(pbVar21 + 0x68);
      }
      uVar29 = *(uint *)(lVar36 + 0x7a0);
      bVar24 = local_c0._4_1_;
      uVar33 = FUN_006ed8f0(*(undefined4 *)(pbVar21 + 0x20));
      if ((*(int *)((ulong)((uVar33 & 0x1fff) * DAT_02692230) + 0x44 + DAT_02692228) == -1) ||
         (uVar29 == 0xffffffff)) {
LAB_0091fb91:
        bVar44 = bVar24 & 1;
      }
      else {
        uVar40 = (ulong)((uVar29 & 0x1fff) * DAT_02689800);
        lVar45 = FUN_00102980((DAT_026897f8 + uVar40) -
                              ((long)DAT_02689818 & *(ulong *)(DAT_026897f8 + 8 + uVar40)));
        bVar46 = *(byte *)(lVar45 + 0xb8) & 0x10;
        bVar44 = bVar46 >> 4;
        if (bVar46 != 0) goto LAB_0091fb91;
      }
      if (iVar31 == -1) {
        FUN_00bd5b10(*(undefined4 *)(pbVar21 + 0x20),local_1d0);
        iVar31 = local_1cc;
      }
      if (bVar44 != 0) {
        sVar27 = FUN_00bd7310(*(undefined4 *)(pbVar21 + 0x20),(int)(short)iVar31,bVar44);
        *(int *)(pbVar21 + 0x68) = (int)sVar27;
        pbVar21[0x6e] = 0xff;
        pbVar21[0x6f] = 0xff;
        pbVar21[0x178] = 0;
      }
      sVar27 = FUN_00bd8040(*(undefined4 *)(pbVar21 + 0x20));
      if (sVar27 != -1) {
        iVar31 = FUN_00bd5aa0(*(undefined4 *)(pbVar21 + 0x20));
        if (iVar31 != sVar27) {
          *(int *)(pbVar21 + 0x68) = (int)sVar27;
        }
      }
      pbVar21[0x6c] = 0xff;
      pbVar21[0x6d] = 0xff;
      uVar35 = FUN_00945950(iVar30);
      uVar35 = FUN_009461c0(uVar35);
      cVar23 = FUN_00947f30(uVar35);
      cVar26 = FUN_001dad30();
      if (((cVar26 == '\0') && (*(int *)(pbVar21 + 0x20) != -1)) &&
         (cVar26 = FUN_00bd1b80(lVar36), cVar26 != '\0')) {
        if ((local_c0 & 0x400000000) == 0) {
          if ((local_c0 & 0x800000000) == 0) goto LAB_0091fc8e;
          if ((pbVar21[0x178] != 0) && (*(short *)(pbVar21 + 0x17c) < 0x7f)) {
            *(short *)(pbVar21 + 0x17c) = *(short *)(pbVar21 + 0x17c) + 1;
          }
        }
        else {
          if (cVar23 == '\0') {
            *(undefined2 *)(pbVar21 + 0x17a) = *(undefined2 *)(pbVar21 + 0x6e);
            sVar27 = FUN_00bd3b50(*(undefined4 *)(pbVar21 + 0x20));
            *(short *)(pbVar21 + 0x6e) = sVar27;
            if (sVar27 == -1) goto LAB_0091fc97;
          }
          else {
            uVar28 = FUN_00bd3b50(*(undefined4 *)(pbVar21 + 0x20),(int)*(short *)(pbVar21 + 0x6e));
            *(undefined2 *)(pbVar21 + 0x17a) = uVar28;
          }
          pbVar21[0x178] = 1;
          pbVar21[0x17c] = 0;
          pbVar21[0x17d] = 0;
        }
      }
      else {
        pbVar21[0x6e] = 0xff;
        pbVar21[0x6f] = 0xff;
LAB_0091fc8e:
        pbVar21[0x178] = 0;
      }
LAB_0091fc97:
      if ((local_c0 & 0x40000000000) != 0) {
        uVar34 = FUN_009230f0(0);
        FUN_00923310(local_1e8,uVar34);
        do {
          cVar23 = FUN_00923320(local_1e8);
        } while (cVar23 != '\0');
      }
      bVar24 = FUN_008e3ae0(0);
      if (((bVar24 | bVar25) & 1) == 0) {
        FUN_00920b90(uStack_d0._4_4_,uStack_c8 & 0xffffffff,uVar1,0);
      }
      uVar29 = FUN_006ed8f0(*(undefined4 *)(pbVar21 + 0x20));
      if (*(int *)((ulong)((uVar29 & 0x1fff) * DAT_02692230) + 0x44 + DAT_02692228) == -1) {
        if ((iVar30 != -1) && (cVar23 = FUN_0094fa50(iVar30), cVar23 != '\0')) {
          auVar4 = vandps_avx(ZEXT416((uint)(float)local_e0),_DAT_0166b620);
          if ((DAT_0166b710 < auVar4._0_4_) &&
             ((((lVar36 = FUN_00928560(iVar30), *(float *)(lVar36 + 0x2d0) == 0.0 &&
                (*(float *)(lVar36 + 0x2d4) == 0.0)) && (!NAN(*(float *)(lVar36 + 0x2d4)))) &&
              (pbVar21[0x160] == 0)))) {
            lVar36 = FUN_00526f80();
            iVar30 = *(int *)(pbVar21 + 0xec) + 1;
            if (*(int *)(pbVar21 + 0xec) < 0) {
              iVar30 = 0;
            }
            iVar31 = *(int *)(lVar36 + 0x1d8);
            if (iVar31 < iVar30) {
              iVar30 = iVar31;
            }
            *(int *)(pbVar21 + 0xec) = iVar30;
            pbVar21[0xe8] = iVar30 == iVar31;
            goto LAB_0091fda6;
          }
        }
        pbVar21[0xec] = 0;
        pbVar21[0xed] = 0;
        pbVar21[0xee] = 0;
        pbVar21[0xef] = 0;
      }
      pbVar21[0xe8] = 0;
    }
LAB_0091fda6:
    *(undefined8 *)(pbVar21 + 0x90) = local_a0;
    *(undefined8 *)(pbVar21 + 0x98) = uStack_98;
    *(undefined8 *)(pbVar21 + 0x80) = uStack_b0;
    *(undefined8 *)(pbVar21 + 0x88) = uStack_a8;
    *(undefined8 *)(pbVar21 + 0xb0) = local_80;
    *(undefined8 *)(pbVar21 + 0xb8) = uStack_78;
    *(undefined8 *)(pbVar21 + 0xa0) = uStack_90;
    *(undefined8 *)(pbVar21 + 0xa8) = uStack_88;
    *(undefined4 *)(pbVar21 + 0xc0) = (undefined4)uStack_70;
    *(uint *)(pbVar21 + 0x30) = (uint)local_c0;
    *(undefined4 *)(pbVar21 + 0x34) = (undefined4)uStack_b8;
    *(undefined8 *)(pbVar21 + 0x50) = local_e0;
    *(undefined4 *)(pbVar21 + 0x58) = (undefined4)uStack_d8;
    *(undefined4 *)(pbVar21 + 0x5c) = uStack_d8._4_4_;
    *(float *)(pbVar21 + 0x60) = (float)uStack_d0;
    pbVar21 = DAT_0273eb28;
    thunk_FUN_0073d590(&local_1c0);
    local_1b8 = *(uint *)(pbVar21 + 0x38);
    local_1b4 = *(uint *)(pbVar21 + 0x3c);
    local_1b0 = *(undefined4 *)(pbVar21 + 0x40);
    local_1a0[0] = FUN_00090ad0(pbVar21 + 0x50);
    local_190 = *(undefined4 *)(pbVar21 + 0x60);
    local_148 = *(undefined4 *)(pbVar21 + 0x34);
    local_1bc = *(undefined4 *)(pbVar21 + 0x30);
    local_144 = *(undefined8 *)(pbVar21 + 100);
    local_13c = (int)*(short *)(pbVar21 + 0x6e);
    local_150 = *(undefined4 *)(pbVar21 + 0x58);
    local_14c = *(undefined4 *)(pbVar21 + 0x5c);
    local_180 = pbVar21[0xc4];
    local_170[0] = FUN_00090ad0(pbVar21 + 200);
    local_160 = pbVar21[0xd0];
    local_130 = *(undefined8 *)(pbVar21 + 0x80);
    uStack_128 = *(undefined8 *)(pbVar21 + 0x88);
    local_120 = *(undefined8 *)(pbVar21 + 0x90);
    uStack_118 = *(undefined8 *)(pbVar21 + 0x98);
    local_110 = *(undefined8 *)(pbVar21 + 0xa0);
    uStack_108 = *(undefined8 *)(pbVar21 + 0xa8);
    local_100 = *(undefined8 *)(pbVar21 + 0xb0);
    uStack_f8 = *(undefined8 *)(pbVar21 + 0xb8);
    local_e8 = *(undefined4 *)DAT_0273eb28;
  }
  else {
    FUN_00744990(uVar1,uVar34,0,iVar30,&local_1c0);
    *(undefined4 *)(pbVar22 + 0x30) = local_1bc;
    *(undefined4 *)(pbVar22 + 0x34) = local_148;
    auVar4 = vinsertps_avx(ZEXT416(local_1b8),ZEXT416(local_1b4),0x10);
    *(long *)(pbVar22 + 0x38) = auVar4._0_8_;
    *(undefined4 *)(pbVar22 + 0x40) = local_1b0;
    puVar37 = (undefined8 *)FUN_00057f80(local_1a0);
    *(undefined8 *)(pbVar22 + 0x50) = *puVar37;
    *(undefined4 *)(pbVar22 + 0x58) = local_150;
    *(undefined4 *)(pbVar22 + 0x5c) = local_14c;
    *(undefined4 *)(pbVar22 + 0x60) = local_190;
    *(undefined8 *)(pbVar22 + 100) = local_144;
    *(undefined8 *)(pbVar22 + 0x90) = local_120;
    *(undefined8 *)(pbVar22 + 0x98) = uStack_118;
    *(undefined8 *)(pbVar22 + 0x80) = local_130;
    *(undefined8 *)(pbVar22 + 0x88) = uStack_128;
    *(undefined8 *)(pbVar22 + 0xb0) = local_100;
    *(undefined8 *)(pbVar22 + 0xb8) = uStack_f8;
    *(undefined8 *)(pbVar22 + 0xa0) = local_110;
    *(undefined8 *)(pbVar22 + 0xa8) = uStack_108;
    uVar34 = FUN_00071f60(local_f0);
    *(undefined4 *)(pbVar22 + 0xc0) = uVar34;
    pbVar22[0xc4] = local_180;
    puVar37 = (undefined8 *)FUN_00057f80(local_170);
    *(undefined8 *)(pbVar22 + 200) = *puVar37;
    pbVar22[0xd0] = local_160;
  }
  pbVar21 = DAT_0273eb28;
  if (*(uint *)(DAT_0273eb28 + 0x20) != 0xffffffff) {
    uVar40 = (ulong)((*(uint *)(DAT_0273eb28 + 0x20) & 0x1fff) * DAT_02689800);
    uVar40 = (ulong)((*(uint *)(((uVar40 + DAT_026897f8) -
                                (*(ulong *)(DAT_026897f8 + 8 + uVar40) & (long)DAT_02689818)) + 0x68
                               ) & 0x1fff) * DAT_02689800);
    local_1c0 = 1;
    local_1bf = *(undefined1 *)
                 (((DAT_026897f8 + uVar40) -
                  ((long)DAT_02689818 & *(ulong *)(DAT_026897f8 + 8 + uVar40))) + 0xa58);
    if ((*(int *)(DAT_0273eb28 + 0x20) != -1) &&
       (*(int *)(DAT_0273eb28 + 0x1c0) == *(int *)(DAT_0273eb28 + 0x20))) {
      uVar6 = *(undefined8 *)(DAT_0273eb28 + 0xc0);
      uVar7 = *(undefined8 *)(DAT_0273eb28 + 200);
      uVar35 = *(undefined8 *)(DAT_0273eb28 + 0x90);
      uVar5 = *(undefined8 *)(DAT_0273eb28 + 0x98);
      uVar8 = *(undefined8 *)(DAT_0273eb28 + 0xa0);
      uVar9 = *(undefined8 *)(DAT_0273eb28 + 0xa8);
      uVar10 = *(undefined8 *)(DAT_0273eb28 + 0x70);
      uVar11 = *(undefined8 *)(DAT_0273eb28 + 0x78);
      uVar12 = *(undefined8 *)(DAT_0273eb28 + 0x80);
      uVar13 = *(undefined8 *)(DAT_0273eb28 + 0x88);
      uVar14 = *(undefined8 *)(DAT_0273eb28 + 0x30);
      uVar15 = *(undefined8 *)(DAT_0273eb28 + 0x38);
      pbVar16 = DAT_0273eb28 + 0x48;
      uVar17 = *(undefined8 *)(DAT_0273eb28 + 0x50);
      uVar18 = *(undefined8 *)(DAT_0273eb28 + 0x58);
      uVar19 = *(undefined8 *)(DAT_0273eb28 + 0x60);
      uVar20 = *(undefined8 *)(DAT_0273eb28 + 0x68);
      *(undefined8 *)(DAT_0273eb28 + 0x1e0) = *(undefined8 *)(DAT_0273eb28 + 0x40);
      *(undefined8 *)(pbVar21 + 0x1e8) = *(undefined8 *)pbVar16;
      *(undefined8 *)(pbVar21 + 0x1d0) = uVar14;
      *(undefined8 *)(pbVar21 + 0x1d8) = uVar15;
      *(undefined8 *)(pbVar21 + 0x200) = uVar19;
      *(undefined8 *)(pbVar21 + 0x208) = uVar20;
      *(undefined8 *)(pbVar21 + 0x1f0) = uVar17;
      *(undefined8 *)(pbVar21 + 0x1f8) = uVar18;
      *(undefined8 *)(pbVar21 + 0x220) = uVar12;
      *(undefined8 *)(pbVar21 + 0x228) = uVar13;
      *(undefined8 *)(pbVar21 + 0x210) = uVar10;
      *(undefined8 *)(pbVar21 + 0x218) = uVar11;
      *(undefined8 *)(pbVar21 + 0x240) = uVar8;
      *(undefined8 *)(pbVar21 + 0x248) = uVar9;
      *(undefined8 *)(pbVar21 + 0x230) = uVar35;
      *(undefined8 *)(pbVar21 + 0x238) = uVar5;
      *(undefined8 *)(pbVar21 + 0x260) = uVar6;
      *(undefined8 *)(pbVar21 + 0x268) = uVar7;
      *(undefined8 *)(pbVar21 + 0x250) = *(undefined8 *)(pbVar21 + 0xb0);
      *(undefined8 *)(pbVar21 + 600) = *(undefined8 *)(pbVar21 + 0xb8);
      *(undefined8 *)(pbVar21 + 0x278) = *(undefined8 *)(pbVar21 + 0xd8);
      *(undefined8 *)(pbVar21 + 0x270) = *(undefined8 *)(pbVar21 + 0xd0);
    }
  }
  FUN_00072050(&local_e0,local_250[0]);
  *(undefined8 *)(pbVar22 + 0x1a8) = local_e0;
  uVar35 = 1;
  *(long *)(pbVar22 + 0x1b8) = local_240;
  *(ulong *)(pbVar22 + 0x1b0) = CONCAT44(uStack_244,local_248);
LAB_009200d6:
  FUN_009014c0(0);
  FUN_00b9ffc0(uVar35,&local_1c0);
  FUN_0092cf20();
  if (*DAT_01a1f100 == local_60) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

