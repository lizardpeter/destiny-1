
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00914a80(long param_1)

{
  long *plVar1;
  uint *puVar2;
  byte *pbVar3;
  undefined8 *puVar4;
  long lVar5;
  float fVar6;
  float fVar7;
  float fVar8;
  float fVar9;
  float fVar10;
  undefined1 auVar11 [16];
  undefined1 auVar12 [16];
  undefined *puVar13;
  char *pcVar14;
  undefined2 uVar15;
  byte bVar16;
  char cVar17;
  char cVar18;
  char cVar19;
  char cVar20;
  undefined4 uVar21;
  uint uVar22;
  int iVar23;
  undefined4 uVar24;
  int iVar25;
  ulong uVar26;
  int *piVar27;
  long lVar28;
  long lVar29;
  long lVar30;
  uint uVar31;
  undefined8 uVar32;
  long lVar33;
  uint uVar34;
  uint uVar35;
  uint uVar36;
  uint uVar37;
  long lVar38;
  ulong uVar39;
  byte bVar40;
  uint uVar41;
  long lVar42;
  uint uVar43;
  long lVar44;
  ulong uVar45;
  ulong uVar46;
  long lVar47;
  bool bVar48;
  bool bVar49;
  float fVar50;
  float fVar51;
  undefined8 extraout_XMM0_Qa;
  float fVar56;
  undefined8 extraout_XMM0_Qb;
  undefined8 extraout_XMM0_Qb_00;
  undefined8 extraout_XMM0_Qb_01;
  undefined1 auVar52 [16];
  undefined8 extraout_XMM0_Qb_02;
  undefined8 extraout_XMM0_Qb_03;
  undefined1 auVar53 [16];
  undefined1 auVar54 [16];
  undefined1 extraout_var [56];
  undefined1 auVar57 [16];
  undefined1 auVar58 [16];
  undefined1 auVar59 [16];
  undefined1 auVar60 [16];
  undefined1 auVar61 [16];
  undefined1 auVar62 [16];
  undefined1 auVar63 [16];
  undefined1 auVar64 [16];
  undefined1 auVar65 [16];
  uint local_3e8;
  undefined1 local_388 [8];
  uint local_380;
  long local_378;
  undefined1 local_370 [8];
  uint local_368;
  long local_360;
  undefined1 local_358 [8];
  uint local_350;
  long local_348;
  undefined1 local_340 [16];
  undefined4 local_330;
  undefined4 local_32c;
  long local_328;
  undefined8 uStack_320;
  undefined4 local_318;
  undefined1 local_310 [24];
  uint local_2f8;
  long local_2f0;
  long local_2e0;
  uint local_2d8 [2];
  long local_2d0;
  int local_2c8;
  uint uStack_2c4;
  undefined8 *local_2c0;
  long *local_2b8;
  long local_2b0;
  long local_2a8;
  long local_2a0;
  ulong local_298;
  long local_290;
  ulong local_288;
  undefined8 local_280;
  undefined4 local_278;
  undefined4 uStack_274;
  undefined1 uStack_270;
  undefined7 uStack_26f;
  undefined1 local_268 [16];
  int local_258;
  undefined8 local_244;
  undefined8 local_238;
  undefined8 uStack_230;
  undefined8 local_228;
  undefined8 uStack_220;
  undefined8 local_218;
  undefined8 uStack_210;
  undefined8 local_208;
  undefined8 uStack_200;
  undefined4 local_1d8;
  undefined4 local_1cc;
  undefined4 local_1c8;
  undefined4 local_1c4;
  undefined4 local_1c0;
  undefined4 local_1bc;
  undefined4 local_1b8;
  undefined4 local_1b4;
  undefined4 local_1b0;
  undefined4 local_1ac;
  undefined1 local_1a8 [8];
  float fStack_1a0;
  float fStack_19c;
  undefined1 local_198 [16];
  undefined4 local_188;
  undefined4 local_184;
  undefined4 local_180;
  undefined4 local_17c;
  undefined4 local_178;
  undefined4 local_170;
  undefined8 local_168;
  undefined8 local_160;
  undefined4 local_158;
  undefined4 local_150;
  undefined4 local_148;
  undefined4 uStack_144;
  undefined4 uStack_140;
  undefined4 uStack_13c;
  undefined4 local_138;
  undefined4 local_130;
  undefined4 local_110;
  byte local_108;
  undefined4 local_f8;
  undefined4 local_f4;
  uint local_f0;
  ulong local_ec;
  int local_e4;
  undefined8 local_d8;
  undefined4 uStack_d0;
  undefined4 uStack_cc;
  undefined8 local_c8;
  undefined8 uStack_c0;
  undefined8 local_b8;
  undefined4 uStack_b0;
  undefined4 uStack_ac;
  undefined8 local_a8;
  undefined8 uStack_a0;
  undefined8 local_98;
  undefined4 local_90;
  undefined4 local_70;
  undefined4 local_68;
  undefined4 local_64;
  undefined4 local_60;
  undefined4 local_5c;
  undefined4 local_58;
  undefined4 local_54;
  undefined4 local_50;
  undefined4 local_4c;
  undefined4 local_48;
  long local_38;
  undefined1 auVar55 [64];
  
  local_38 = *DAT_01a1f100;
  FUN_00074a80(&local_290,DAT_0273ea80);
  uVar26 = FUN_00074a90(&local_290);
  local_298 = uVar26;
  if (uVar26 != 0) {
    do {
      uVar22 = *(uint *)(uVar26 + 0x610);
      local_298 = uVar26;
      if ((uVar22 & 2) == 0) {
        cVar17 = FUN_00906f70();
        if (cVar17 == '\0') {
          bVar40 = FUN_00ba0580(uVar26 + 0x620);
        }
        else {
          bVar40 = (byte)uVar22 & 1;
        }
        uVar22 = *(uint *)(uVar26 + 0x610);
        if ((uVar22 & 1) != (uint)bVar40) {
          if (cVar17 == '\0') {
            local_168 = (local_288 & 0xffff) << 0x20;
            local_160 = CONCAT71((int7)(local_160 >> 8),bVar40) & 0xffffffff000000ff;
            FUN_00bacda0(&local_168);
          }
          else if (bVar40 == 0) {
            *(uint *)(uVar26 + 0x610) = uVar22 & 0xfffffffe;
          }
          else {
            *(uint *)(uVar26 + 0x610) = uVar22 | 1;
          }
        }
      }
      uVar26 = FUN_00074a90(&local_290);
      local_298 = uVar26;
    } while (uVar26 != 0);
  }
  piVar27 = (int *)FUN_0077ba50();
  cVar17 = *(char *)((long)piVar27 + 0xd);
  if ((*piVar27 != -1) || (cVar17 = *(char *)((long)piVar27 + 0xad), piVar27[0x28] != -1)) {
    cVar18 = FUN_0075b6a0();
    FUN_00074a80(&uStack_320,DAT_0273ea80);
    lVar28 = FUN_00074a90(&uStack_320);
    puVar13 = PTR_DAT_019b1b60;
    local_328 = lVar28;
    if (lVar28 != 0) {
      do {
        uVar24 = local_318;
        cVar20 = *(char *)(lVar28 + 0x2841);
        local_328 = lVar28;
        if ((*(char *)(lVar28 + 0x2840) != '\0') || (cVar20 != cVar18)) {
          if (*(char *)(lVar28 + 0x2838) == '\0') {
            *(undefined1 *)(lVar28 + 0x2838) = 1;
            uVar21 = FUN_005916f0();
            *(undefined4 *)(lVar28 + 0x283c) = uVar21;
          }
          uVar22 = FUN_006ed8f0(*(undefined4 *)(lVar28 + 0x644));
          *(undefined1 *)(lVar28 + 0x2840) = 0;
          *(char *)(lVar28 + 0x2841) = cVar18;
          lVar29 = FUN_0066ae60(uVar24);
          iVar23 = FUN_00919ee0(uVar24,cVar18,&local_32c);
          FUN_0063b390(&local_298);
          local_1d8 = *(undefined4 *)(lVar29 + 0x328);
          cVar19 = FUN_0063b470(&local_298);
          uVar24 = 0xffffffff;
          bVar48 = iVar23 == 3;
          if (cVar19 == '\0') {
            uVar24 = FUN_0063fb80(bVar48,&local_298);
          }
          if (*(int *)(lVar28 + 0x284c) != -1) {
            FUN_0063fc70();
          }
          *(undefined4 *)(lVar28 + 0x284c) = uVar24;
          FUN_0063b390(&local_298);
          local_1d8 = *(undefined4 *)(lVar29 + 0x360);
          cVar19 = FUN_0063b470(&local_298);
          uVar24 = 0xffffffff;
          if (cVar19 == '\0') {
            uVar24 = FUN_0063fbb0(bVar48,&local_298);
          }
          if (*(int *)(lVar28 + 0x2850) != -1) {
            FUN_0063fca0();
          }
          *(undefined4 *)(lVar28 + 0x2850) = uVar24;
          uVar32 = 1;
          if ((cVar17 == '\x01') && (uVar32 = 1, *(char *)(lVar29 + 0xb) != '\x01')) {
            uVar32 = 2;
          }
          local_150 = 0x811c9dc5;
          local_130 = 0x811c9dc5;
          local_110 = 0x811c9dc5;
          local_f0 = 0x811c9dc5;
          uStack_d0 = 0x811c9dc5;
          uStack_b0 = 0x811c9dc5;
          local_90 = 0x811c9dc5;
          local_70 = 0x811c9dc5;
          local_68 = 0;
          local_64 = 0x811c9dc5;
          local_60 = 0x811c9dc5;
          local_5c = 0x811c9dc5;
          local_58 = 0x811c9dc5;
          local_54 = 0x811c9dc5;
          local_50 = 0x811c9dc5;
          local_4c = 0x811c9dc5;
          local_48 = 0x811c9dc5;
          if (*(char *)(lVar28 + 0x2868) == '\0') {
            FUN_00641990(&local_168);
          }
          else {
            FUN_0066b220(lVar29 + 0x180,*(undefined1 *)(lVar29 + 9),*(undefined1 *)(lVar29 + 8),
                         uVar32,iVar23,local_32c,&local_168);
          }
          auVar54 = local_198;
          auVar52 = _local_1a8;
          local_1cc = 0;
          local_1c8 = 0x811c9dc5;
          local_1c4 = 0x811c9dc5;
          local_1c0 = 0x811c9dc5;
          local_1bc = 0x811c9dc5;
          local_1b8 = 0x811c9dc5;
          local_1b4 = 0x811c9dc5;
          local_1b0 = 0x811c9dc5;
          local_1ac = 0x811c9dc5;
          local_1a8._0_4_ = 0x811c9dc5;
          auVar11 = _local_1a8;
          fStack_19c = auVar52._12_4_;
          local_1a8 = auVar11._0_8_;
          fStack_1a0 = -2.876587e-38;
          local_198._0_4_ = 0x811c9dc5;
          auVar52 = local_198;
          local_198._12_4_ = auVar54._12_4_;
          local_198._0_8_ = auVar52._0_8_;
          local_198._8_4_ = 0x811c9dc5;
          local_188 = 0x811c9dc5;
          local_180 = 0x811c9dc5;
          local_178 = 0x811c9dc5;
          local_170 = 0x811c9dc5;
          FUN_00641ad0(&local_168,&local_298);
          cVar19 = FUN_0063b470(&local_298);
          iVar25 = -1;
          if (cVar19 == '\0') {
            iVar25 = FUN_0063fb00(bVar48,&local_298);
          }
          if (*(int *)(lVar28 + 0x2854) != -1) {
            FUN_0063fbe0();
          }
          *(int *)(lVar28 + 0x2854) = iVar25;
          if (iVar25 == -1) {
            *(undefined1 *)(lVar28 + 0x2840) = 1;
          }
          if (((cVar20 != cVar18) && (uVar22 != 0xffffffff)) &&
             (cVar20 = FUN_00337fe0((ulong)((uVar22 & 0x1fff) * DAT_02692230) + DAT_02692228,
                                    *(undefined4 *)puVar13,local_310,0), cVar20 != '\0')) {
            lVar38 = (ulong)(((uint)((int)local_2f8 >> 0xd) >> 0x12 | 0x3ff) & (int)local_2f8 >> 0xd
                            ) * 0x40;
            lVar44 = *DAT_01a238a0;
            lVar47 = *(long *)(lVar44 + 0x10 + lVar38);
            uVar26 = (ulong)((local_2f8 & 0x1fff) * *(int *)(lVar44 + 0x30 + lVar38));
            uVar22 = *(uint *)(local_2f0 + 0x24 +
                              ((lVar47 + uVar26) -
                              ((long)*(int *)(lVar44 + 0x34 + lVar38) &
                              *(ulong *)(lVar47 + 8 + uVar26))));
            if (uVar22 != 0xffffffff) {
              lVar38 = (ulong)(((uint)((int)uVar22 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar22 >> 0xd) *
                       0x40;
              lVar44 = *DAT_01a238a0;
              lVar47 = *(long *)(lVar44 + 0x10 + lVar38);
              uVar26 = (ulong)((uVar22 & 0x1fff) * *(int *)(lVar44 + 0x30 + lVar38));
              FUN_006422a0((lVar47 + uVar26) -
                           ((long)*(int *)(lVar44 + 0x34 + lVar38) & *(ulong *)(lVar47 + 8 + uVar26)
                           ),&local_168);
            }
          }
          cVar20 = FUN_005c4590();
          bVar49 = false;
          if (cVar20 != '\0') {
            bVar49 = *(int *)(lVar28 + 0x628) != *(int *)(DAT_0273ea90 + 0xb4);
          }
          lVar29 = lVar29 + 0x38c;
          lVar44 = 0;
          do {
            local_168 = CONCAT44(local_168._4_4_,0x811c9dc5);
            local_160 = CONCAT44(local_160._4_4_,0x811c9dc5);
            local_158 = 0x811c9dc5;
            local_150 = 0x811c9dc5;
            local_148 = 0x811c9dc5;
            uStack_140 = 0x811c9dc5;
            local_138 = 0x811c9dc5;
            if ((bVar49) || (*(int *)(lVar28 + 0x286c) <= (int)lVar44)) {
              FUN_00643fa0(&local_168);
            }
            else {
              local_330 = *(undefined4 *)(lVar29 + -0x18);
              FUN_00672b60(lVar29,*(undefined4 *)(lVar29 + -0x24),&local_330,iVar23,&local_168);
            }
            auVar54 = local_198;
            auVar52 = _local_1a8;
            local_1cc = 0;
            local_1c8 = 0x811c9dc5;
            local_1c4 = 0x811c9dc5;
            local_1c0 = 0x811c9dc5;
            local_1bc = 0x811c9dc5;
            local_1b8 = 0x811c9dc5;
            local_1b4 = 0x811c9dc5;
            local_1b0 = 0x811c9dc5;
            local_1ac = 0x811c9dc5;
            local_1a8._0_4_ = 0x811c9dc5;
            auVar11 = _local_1a8;
            fStack_19c = auVar52._12_4_;
            local_1a8 = auVar11._0_8_;
            fStack_1a0 = -2.876587e-38;
            local_198._0_4_ = 0x811c9dc5;
            auVar52 = local_198;
            local_198._12_4_ = auVar54._12_4_;
            local_198._0_8_ = auVar52._0_8_;
            local_198._8_4_ = 0x811c9dc5;
            local_188 = 0x811c9dc5;
            local_180 = 0x811c9dc5;
            local_178 = 0x811c9dc5;
            local_170 = 0x811c9dc5;
            FUN_00644040(&local_168,&local_298);
            cVar20 = FUN_0063b470(&local_298);
            iVar25 = -1;
            if (cVar20 == '\0') {
              iVar25 = FUN_0063fb20(bVar48,&local_298);
            }
            if (*(int *)(lVar28 + 0x285c + lVar44 * 4) != -1) {
              FUN_0063fc10();
            }
            *(int *)(lVar28 + 0x285c + lVar44 * 4) = iVar25;
            if ((*(int *)(lVar29 + -0x24) != -1) && (iVar25 == -1)) {
              *(undefined1 *)(lVar28 + 0x2840) = 1;
            }
            lVar29 = lVar29 + 800;
            lVar44 = lVar44 + 1;
          } while ((int)lVar44 != 3);
        }
        lVar28 = FUN_00074a90(&uStack_320);
        local_328 = lVar28;
      } while (lVar28 != 0);
    }
  }
  FUN_00074a80(local_340,DAT_0273ea80);
  while (lVar28 = FUN_00074a90(local_340), local_348 = lVar28, lVar28 != 0) {
    if (*(char *)(lVar28 + 0x2838) != '\0') {
      cVar18 = '\0';
      cVar17 = '\0';
      if (*(int *)(lVar28 + 0x2854) != -1) {
        cVar17 = FUN_0063fed0();
      }
      if (*(int *)(lVar28 + 0x285c) != -1) {
        cVar18 = FUN_0063ff50();
      }
      cVar19 = '\0';
      cVar20 = '\0';
      if (*(int *)(lVar28 + 0x2860) != -1) {
        cVar20 = FUN_0063ff50();
      }
      if (*(int *)(lVar28 + 0x2864) != -1) {
        cVar19 = FUN_0063ff50();
      }
      if (cVar19 == '\0' && (cVar20 == '\0' && (cVar18 == '\0' && cVar17 == '\0'))) {
        *(undefined1 *)(lVar28 + 0x2838) = 0;
        *(undefined4 *)(lVar28 + 0x283c) = 0;
      }
    }
  }
  FUN_00649910();
  FUN_00074a80(local_358,DAT_0273ea80);
  while (lVar28 = FUN_00074a90(local_358), local_360 = lVar28, lVar28 != 0) {
    if ((*(char *)(DAT_0273ea90 + 0xa8) != '\0') &&
       (local_2e0 = *(long *)(DAT_0273ea90 + 0xa9),
       *(long *)(*(long *)(DAT_0273ea80 + 8) + 0x620 + (ulong)(local_350 & 0xffff) * 0x2af0) ==
       local_2e0)) {
      if ((*(int *)(lVar28 + 8) == -1) && (iVar23 = FUN_00ba7bf0(2), iVar23 != -1)) {
        *(int *)(lVar28 + 8) = iVar23;
        FUN_00ba8010(iVar23,local_350);
      }
      cVar17 = FUN_00906f70();
      if (((cVar17 == '\0') && (*(int *)(lVar28 + 8) != -1)) &&
         (iVar23 = FUN_00ba8150(), iVar23 == -1)) {
        FUN_00bb9490(2,*(undefined4 *)(lVar28 + 8),0xffffffff);
      }
    }
  }
  FUN_00074a80(local_370,DAT_0273ea80);
  local_378 = FUN_00074a90(local_370);
  while (local_378 != 0) {
    FUN_009205a0(local_368 & 0xffff,
                 *(undefined4 *)(param_1 + 0xf8 + (ulong)(local_368 & 0xffff) * 0xe0));
    local_378 = FUN_00074a90(local_370);
  }
  cVar17 = FUN_00906f70();
  if (((cVar17 != '\0') && (iVar23 = FUN_009236b0(0), iVar23 != -1)) &&
     ((*(uint *)(param_1 + 0x10) >> ((int)(short)iVar23 & 0x1fU) & 1) != 0)) {
    FUN_00920430(0,param_1 + 0x20 + (long)(int)(short)iVar23 * 0xe0);
  }
  bVar40 = DAT_0273ea88;
  cVar17 = FUN_005428c0();
  if (cVar17 != '\0') {
    uVar32 = FUN_00078970(&DAT_026bc820);
    cVar17 = FUN_0058e540(uVar32);
    uVar32 = *(undefined8 *)(DAT_02689580[1] + 0x10);
    uVar24 = FUN_0006f140(&DAT_02689580);
    FUN_0008f550(local_2d8,uVar32,uVar24);
    local_2c0 = &DAT_02689580;
    local_2b8 = DAT_02689580;
    if ((int)local_2d8[0] < local_2c8) {
      do {
        uVar26 = (ulong)((local_2d8[0] & 0xffff) * (int)local_2b8[2]);
        lVar28 = *local_2b8;
        FUN_0058bf90(*(undefined4 *)(uVar26 + 0x4c + lVar28));
        if (cVar17 != '\0') {
          if (*(long *)(uVar26 + 0x20 + lVar28) != 0) {
            plVar1 = (long *)(uVar26 + 0x20 + lVar28);
            uVar32 = FUN_0056b260();
            if (*plVar1 != 0) {
              uVar24 = FUN_00001df0(uVar32);
              lVar29 = FUN_0056dc00(uVar32,2,uVar24,plVar1);
              if (lVar29 != 0) {
                lVar47 = (ulong)(*(uint *)(lVar28 + 0x4c + uVar26) & 0xffff) * 0x2af0;
                lVar44 = *(long *)(DAT_0273ea80 + 8);
                FUN_00065a00(lVar44 + 0x2ab0 + lVar47,lVar29 + 0x10,0x1b);
                FUN_00065a00(lVar44 + 0x2ae6 + lVar47,lVar29 + 0x46,5);
              }
            }
          }
          uVar32 = FUN_00078970(&DAT_026bc820);
          FUN_0058e550(uVar32,0);
        }
        if ((((*(byte *)(uVar26 + 0x40 + lVar28) & 1) == 0) || ((bVar40 & 1) != 0)) ||
           ((lVar28 = FUN_0057ddd0(*(undefined8 *)(uVar26 + 0x10 + lVar28)), lVar28 == 0 ||
            (bVar16 = 1, *(char *)(lVar28 + 0x22) != '\0')))) {
          bVar16 = bVar40;
        }
        do {
          bVar40 = bVar16;
          uVar26 = (ulong)uStack_2c4;
          do {
            uVar22 = local_2d8[0] + 1;
            if (local_2c8 <= (int)uVar22) break;
            uVar26 = uVar26 >> 1;
            uStack_2c4 = (uint)uVar26;
            if (uStack_2c4 == 0) {
              uVar22 = local_2d8[0] + 0x20 & 0xffffffe0;
              if (local_2c8 <= (int)uVar22) break;
              uStack_2c4 = *(uint *)(local_2d0 + (long)((int)(local_2d8[0] + 0x20) >> 5) * 4);
              while (uVar26 = (ulong)uStack_2c4, uStack_2c4 == 0) {
                uVar22 = uVar22 + 0x20;
                if (local_2c8 <= (int)uVar22) goto LAB_00915795;
                uStack_2c4 = *(uint *)(local_2d0 + (long)((int)uVar22 >> 5) * 4);
              }
            }
            local_2d8[0] = uVar22;
            uVar22 = local_2d8[0];
          } while ((uVar26 & 1) == 0);
LAB_00915795:
          local_2d8[0] = uVar22;
          if (local_2c8 <= (int)local_2d8[0]) goto LAB_009157d0;
          bVar16 = bVar40;
        } while ((*(uint *)(*(long *)(local_2b8[1] + 0x10) + (ulong)(local_2d8[0] >> 5 & 0x7ff) * 4)
                  >> (local_2d8[0] & 0x1f) & 1) == 0);
      } while( true );
    }
  }
LAB_009157d0:
  FUN_000ad2f0(bVar40 & 1);
  FUN_00412800(param_1);
  FUN_00074a80(local_388,DAT_0273ea80);
  lVar28 = FUN_00074a90(local_388);
  uVar22 = local_380;
  do {
    if (lVar28 == 0) {
      if (*DAT_01a1f100 != local_38) {
        thunk_FUN_012aa7f6();
        return;
      }
      return;
    }
    local_380 = uVar22;
    if ((*(uint *)(param_1 + 0x10) >> (uVar22 & 0x1f) & 1) != 0) {
      lVar29 = param_1 + 0x20 + (ulong)(uVar22 & 0xffff) * 0xe0;
      cVar17 = FUN_00914550(lVar29,1);
      if (((cVar17 != '\0') && (*(int *)(lVar28 + 0x644) != -1)) &&
         (cVar17 = FUN_00bd5c50(), pcVar14 = DAT_0273ea98, cVar17 != '\0')) {
        uVar26 = (ulong)((*(uint *)(lVar28 + 0x644) & 0x1fff) * DAT_02689800);
        uVar26 = (ulong)((*(uint *)(((uVar26 + DAT_026897f8) -
                                    (*(ulong *)(DAT_026897f8 + 8 + uVar26) & (long)DAT_02689818)) +
                                   0x68) & 0x1fff) * DAT_02689800);
        lVar44 = (DAT_026897f8 + uVar26) -
                 ((long)DAT_02689818 & *(ulong *)(DAT_026897f8 + 8 + uVar26));
        if (*DAT_0273ea98 == '\0') {
          thunk_FUN_012aa7c6(&local_168,lVar29,0xdc);
          if (pcVar14[1] != '\0') {
            uVar15 = (undefined2)local_168;
            local_290 = CONCAT44(local_290._4_4_,local_158);
            local_298 = local_160;
            FUN_0073d590(&local_168);
            local_168 = CONCAT62(local_168._2_6_,uVar15);
            local_158 = (undefined4)local_290;
            local_160 = local_298;
          }
          lVar47 = (ulong)(uVar22 & 0xffff) * 0x2af0;
          lVar29 = *(long *)(DAT_0273ea80 + 8);
          uVar31 = local_168._4_4_;
          uVar34 = ~*(uint *)(lVar29 + 0x654 + lVar47) & local_168._4_4_;
          local_168 = CONCAT44(uVar34,(undefined4)local_168);
          uVar35 = (*(uint *)(lVar29 + 0x658 + lVar47) & 0xf001000 ^ 0x3fffffff) & local_f0;
          uVar37 = *(uint *)(lVar29 + 0x658 + lVar47);
          *(uint *)(lVar29 + 0x654 + lVar47) =
               (*(uint *)(lVar29 + 0x654 + lVar47) | 0x10000000) & uVar31;
          *(uint *)(lVar29 + 0x658 + lVar47) = uVar37 & 0x30ffefff | local_f0 & 0xf001000;
          uVar36 = uVar35 & 0x10;
          uVar31 = uVar35 | 4;
          if (((uVar37 & 1) == 0 & (byte)uVar35 & 1) == 0) {
            uVar31 = uVar35 & 0xfffffffb;
          }
          uVar43 = uVar35 & 0x100;
          puVar2 = (uint *)(lVar29 + 0x658 + lVar47);
          if ((uVar35 & 1) == 0) {
            local_f0 = uVar31 & 0xfffffff7;
            if ((uVar37 & 8) == 0 && (uVar37 & 1) != 0) {
              local_f0 = uVar31 | 8;
            }
            uVar31 = *puVar2 & 0xfffffffe;
            *puVar2 = uVar31;
LAB_00915b9b:
            uVar41 = uVar31 & 0xfffffff7;
          }
          else {
            local_f0 = uVar31 & 0xfffffff7;
            uVar41 = *puVar2;
            uVar31 = uVar41 | 1;
            *puVar2 = uVar31;
            if ((uVar37 & 8) == 0) goto LAB_00915b9b;
            uVar41 = uVar41 | 9;
          }
          *puVar2 = uVar41;
          bVar48 = (uVar37 & 0x10) == 0;
          uVar31 = local_f0 & 0xffffffbf;
          if (bVar48 && uVar36 != 0) {
            uVar31 = local_f0 | 0x40;
          }
          uVar41 = uVar31 | 0x80;
          if (uVar36 != 0 || bVar48) {
            uVar41 = uVar31 & 0xffffff7f;
          }
          uVar31 = *puVar2 | 0x10;
          if (uVar36 == 0) {
            uVar31 = *puVar2 & 0xffffffef;
          }
          bVar48 = (uVar37 & 0x100) != 0;
          *puVar2 = uVar31;
          uVar31 = uVar41 | 0x400;
          if (bVar48 || uVar43 == 0) {
            uVar31 = uVar41 & 0xfffffbff;
          }
          uVar41 = uVar31 | 0x800;
          if (uVar43 != 0 || !bVar48) {
            uVar41 = uVar31 & 0xfffff7ff;
          }
          uVar31 = *puVar2 | 0x100;
          if (uVar43 == 0) {
            uVar31 = *puVar2 & 0xfffffeff;
          }
          uVar43 = uVar31 & 0xfffbffff;
          if ((uVar35 & 0x40000) != 0) {
            uVar43 = uVar31 | 0x40000;
          }
          uVar31 = uVar43 | 0x80000;
          if ((uVar35 & 0x80000) == 0) {
            uVar31 = uVar43 & 0xfff7ffff;
          }
          uVar43 = uVar31 | 0x100000;
          if ((uVar35 & 0x100000) == 0) {
            uVar43 = uVar31 & 0xffefffff;
          }
          uVar31 = uVar43 | 0x200000;
          if ((uVar35 & 0x200000) == 0) {
            uVar31 = uVar43 & 0xffdfffff;
          }
          uVar43 = uVar31 | 0x400000;
          if ((uVar35 & 0x400000) == 0) {
            uVar43 = uVar31 & 0xffbfffff;
          }
          uVar31 = uVar43 | 0x800000;
          if ((uVar35 & 0x800000) == 0) {
            uVar31 = uVar43 & 0xff7fffff;
          }
          *puVar2 = uVar31;
          local_f0 = uVar41 | 0x4000;
          if ((uVar37 & 0x2000) != 0 || (uVar35 & 0x2000) == 0) {
            local_f0 = uVar41 & 0xffffbfff;
          }
          uVar31 = *puVar2 | 0x2000;
          if ((uVar35 & 0x2000) == 0) {
            uVar31 = *puVar2 & 0xffffdfff;
          }
          *puVar2 = uVar31;
          if (((uVar35 & 0x8000) == 0) && ((uVar37 & 0x28000) == 0x8000)) {
            local_f0 = local_f0 | 0x10000;
          }
          else {
            local_f0 = local_f0 & 0xfffeffff;
          }
          uVar37 = *puVar2 | 0x20000;
          if ((uVar35 & 0x20000) == 0) {
            uVar37 = *puVar2 & 0xfffdffff;
          }
          uVar31 = uVar37 & 0xffff7fff;
          if ((uVar35 & 0x8000) != 0) {
            uVar31 = uVar37 | 0x8000;
          }
          *puVar2 = uVar31;
          puVar2 = (uint *)(lVar29 + 0x610 + lVar47);
          uVar37 = *(uint *)(lVar29 + 0x610 + lVar47);
          if ((uVar37 & 8) != 0) {
            local_f0 = local_f0 & 0x3ffffff0;
            if ((uVar35 & 1) == 0) {
              uVar37 = *puVar2 & 0xfffffff7;
            }
            else {
              uVar37 = *puVar2 | 8;
            }
            *puVar2 = uVar37;
          }
          if ((uVar37 & 0x10) != 0) {
            local_f0 = local_f0 & 0x3fffff0f;
            if (uVar36 == 0) {
              uVar37 = *puVar2 & 0xffffffef;
            }
            else {
              uVar37 = *puVar2 | 0x10;
            }
            *puVar2 = uVar37;
          }
          if ((uVar37 & 0x20) != 0) {
            local_f0 = local_f0 & 0x3ffff0ff;
            if (uVar36 == 0) {
              uVar37 = *puVar2 & 0xffffffdf;
            }
            else {
              uVar37 = *puVar2 | 0x20;
            }
            *puVar2 = uVar37;
          }
          if ((uVar37 & 0x400) != 0) {
            local_f0 = local_f0 & 0x3ffbffff;
            if ((uVar35 & 0x40000) == 0) {
              uVar37 = *puVar2 & 0xfffffbff;
            }
            else {
              uVar37 = *puVar2 | 0x400;
            }
            *puVar2 = uVar37;
          }
          if ((uVar37 & 0x800) != 0) {
            local_f0 = local_f0 & 0x3ff7ffff;
            if ((uVar35 & 0x80000) == 0) {
              uVar37 = *puVar2 & 0xfffff7ff;
            }
            else {
              uVar37 = *puVar2 | 0x800;
            }
            *puVar2 = uVar37;
          }
          if ((uVar37 & 0x1000) != 0) {
            local_f0 = local_f0 & 0x3fefffff;
            if ((uVar35 & 0x100000) == 0) {
              uVar37 = *puVar2 & 0xffffefff;
            }
            else {
              uVar37 = *puVar2 | 0x1000;
            }
            *puVar2 = uVar37;
          }
          if ((uVar37 & 0x2000) != 0) {
            local_f0 = local_f0 & 0x3fdfffff;
            if ((uVar35 & 0x200000) == 0) {
              uVar37 = *puVar2 & 0xffffdfff;
            }
            else {
              uVar37 = *puVar2 | 0x2000;
            }
            *puVar2 = uVar37;
          }
          if ((uVar37 & 0x4000) != 0) {
            local_f0 = local_f0 & 0x3fbfffff;
            if ((uVar35 & 0x400000) == 0) {
              uVar37 = *puVar2 & 0xffffbfff;
            }
            else {
              uVar37 = *puVar2 | 0x4000;
            }
            *puVar2 = uVar37;
          }
          if ((uVar37 & 0x8000) != 0) {
            local_f0 = local_f0 & 0x3f7fffff;
            if ((uVar35 & 0x800000) == 0) {
              uVar37 = *puVar2 & 0xffff7fff;
            }
            else {
              uVar37 = *puVar2 | 0x8000;
            }
            *puVar2 = uVar37;
          }
          if ((uVar37 & 0x40) != 0) {
            if (local_e4 == -1) {
              uVar37 = uVar37 & 0xffffffbf;
              *puVar2 = uVar37;
            }
            else {
              local_e4 = -1;
              uVar37 = *puVar2;
            }
          }
          if ((uVar37 & 0x80) != 0) {
            if ((uVar34 & 0x800000) == 0) {
              uVar37 = uVar37 & 0xffffff7f;
              *puVar2 = uVar37;
            }
            else {
              local_168 = CONCAT44(uVar34,(undefined4)local_168) & 0xff7fffffffffffff;
              uVar37 = *puVar2;
            }
          }
          if ((uVar37 & 0x100) != 0) {
            if ((local_168 & 0x1000000000000000) == 0) {
              uVar37 = uVar37 & 0xfffffeff;
              *puVar2 = uVar37;
            }
            else {
              local_168 = local_168 & 0xefffffffffffffff;
              uVar37 = *puVar2;
            }
          }
          uVar26 = local_168;
          if ((uVar37 & 0x200) != 0) {
            local_168 = local_168 | 0x200000000;
            if ((uVar26 & 0x100000000) == 0) {
              *(byte *)((long)puVar2 + 1) = *(byte *)((long)puVar2 + 1) & 0xfd;
            }
            else {
              local_168 = uVar26 & 0xfffffffeffffffff | 0x200000000;
            }
          }
          lVar38 = DAT_026897f8;
          uVar37 = *(uint *)(lVar28 + 0x644);
          uVar26 = (ulong)((uVar37 & 0x1fff) * DAT_02689800);
          uVar46 = (ulong)DAT_02689818;
          local_3e8 = (uint)(local_168 >> 0x20) & 0x700002;
          lVar29 = *(long *)(DAT_0273ea80 + 8);
          uVar45 = (ulong)((*(uint *)(((uVar26 + DAT_026897f8) -
                                      (*(ulong *)(DAT_026897f8 + 8 + uVar26) & uVar46)) + 0x68) &
                           0x1fff) * DAT_02689800);
          uVar26 = *(ulong *)(DAT_026897f8 + 8 + uVar45);
          FUN_00743660(uVar22,&local_168);
          lVar30 = FUN_005da040(uVar37);
          if ((lVar30 != 0) && (*(int *)(lVar30 + 0x18) != -1)) {
            uStack_270 = 0;
            uVar31 = (int)*(uint *)(lVar30 + 0x10) >> 0xd;
            lVar5 = *DAT_01a238a0;
            lVar42 = (ulong)((uVar31 >> 0x12 | 0x3ff) & uVar31) * 0x40;
            lVar33 = *(long *)(lVar5 + 0x10 + lVar42);
            uVar39 = (ulong)((*(uint *)(lVar30 + 0x10) & 0x1fff) * *(int *)(lVar5 + 0x30 + lVar42));
            local_298 = (lVar33 + uVar39) -
                        ((long)*(int *)(lVar5 + 0x34 + lVar42) & *(ulong *)(lVar33 + 8 + uVar39));
            uVar31 = (int)*(uint *)(lVar30 + 0x18) >> 0xd;
            lVar42 = (ulong)((uVar31 >> 0x12 | 0x3ff) & uVar31) * 0x40;
            lVar33 = *(long *)(lVar5 + 0x10 + lVar42);
            uVar39 = (ulong)((*(uint *)(lVar30 + 0x18) & 0x1fff) * *(int *)(lVar5 + 0x30 + lVar42));
            local_290 = ((lVar33 + uVar39) -
                        ((long)*(int *)(lVar5 + 0x34 + lVar42) & *(ulong *)(lVar33 + 8 + uVar39))) +
                        *(long *)(lVar30 + 0x20);
            local_278 = *(undefined4 *)(lVar30 + 0x28);
            local_288 = *(ulong *)(lVar30 + 0x18);
            local_280 = *(undefined8 *)(lVar30 + 0x20);
            FUN_00354c90(&local_298,&local_168,0x700002);
          }
          lVar30 = (lVar38 + uVar45) - (uVar46 & uVar26);
          lVar38 = lVar29 + 0x27e4 + lVar47;
          uVar31 = *(uint *)(lVar30 + 0x7c0);
          iVar23 = FUN_00071f60(lVar38);
          if ((iVar23 != -1) && (uVar31 != 0xffffffff)) {
            uVar34 = FUN_00071f60(lVar38);
            lVar33 = (ulong)(((uint)((int)uVar34 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar34 >> 0xd) *
                     0x40;
            lVar38 = *DAT_01a238a0;
            lVar5 = *(long *)(lVar38 + 0x10 + lVar33);
            iVar23 = *(int *)(lVar38 + 0x34 + lVar33);
            uVar46 = (ulong)((uVar34 & 0x1fff) * *(int *)(lVar38 + 0x30 + lVar33));
            uVar26 = *(ulong *)(lVar5 + 8 + uVar46);
            lVar42 = (ulong)(((uint)((int)uVar31 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar31 >> 0xd) *
                     0x40;
            lVar33 = *(long *)(lVar38 + 0x10 + lVar42);
            uVar45 = (ulong)((uVar31 & 0x1fff) * *(int *)(lVar38 + 0x30 + lVar42));
            cVar17 = FUN_006e3880((lVar33 + uVar45) -
                                  ((long)*(int *)(lVar38 + 0x34 + lVar42) &
                                  *(ulong *)(lVar33 + 8 + uVar45)));
            if (cVar17 != '\0') {
              lVar38 = (lVar5 + uVar46) - ((long)iVar23 & uVar26);
              cVar17 = FUN_00679dd0(lVar38);
              if ((cVar17 != '\0') || (cVar17 = FUN_006782a0(lVar38), cVar17 != '\0')) {
                local_168 = local_168 & 0xfffffffeffffffff;
              }
            }
          }
          if ((*(char *)(DAT_0273ea90 + 0xa8) != '\0') &&
             (local_2a8 = *(long *)(DAT_0273ea90 + 0xa9),
             *(long *)(*(long *)(DAT_0273ea80 + 8) + 0x620 + lVar47) == local_2a8)) {
            uVar31 = *(uint *)(lVar29 + 0x27dc + lVar47);
            if (uVar31 != 0xffffffff) {
              uVar26 = (ulong)((uVar31 & 0x1fff) * DAT_02689800);
              FUN_006b5550((DAT_026897f8 + uVar26) -
                           ((long)DAT_02689818 & *(ulong *)(DAT_026897f8 + 8 + uVar26)),&local_168);
            }
            uVar31 = *(uint *)(lVar29 + 0x27e0 + lVar47);
            if (uVar31 != 0xffffffff) {
              uVar26 = (ulong)((uVar31 & 0x1fff) * DAT_02689800);
              FUN_003d15f0((DAT_026897f8 + uVar26) -
                           ((long)DAT_02689818 & *(ulong *)(DAT_026897f8 + 8 + uVar26)),&local_168);
            }
          }
          if (((local_f0 & 0x880) != 0) && (iVar23 = FUN_00bd3540(uVar37), iVar23 != -1)) {
            lVar38 = FUN_006fc560(iVar23);
            cVar17 = FUN_00bca0a0(iVar23);
            if ((((cVar17 != '\0') || ((lVar38 != 0 && ((*(byte *)(lVar38 + 0x4c9) & 4) != 0)))) &&
                (*(int *)(*(long *)(DAT_0273ea80 + 8) + 0x644 + lVar47) != -1)) &&
               (cVar17 = FUN_00bd6910(), cVar17 != '\0')) {
              if (uVar22 != 0xffffffff) {
                lVar38 = *(long *)(DAT_0273ea80 + 8);
                FUN_00923130();
                pbVar3 = (byte *)(lVar38 + 0x610 + lVar47);
                *pbVar3 = *pbVar3 | 0x20;
              }
              local_f0 = local_f0 & 0xfffff7ff;
            }
          }
          if (((local_f0 & 8) != 0) && (iVar23 = FUN_00bd3540(uVar37), iVar23 != -1)) {
            local_168 = local_168 | 0x1000000000000000;
            local_f0 = local_f0 & 0xfffffff7;
            pbVar3 = (byte *)(lVar29 + 0x658 + lVar47);
            *pbVar3 = *pbVar3 | 8;
          }
          uVar31 = *(uint *)(lVar30 + 0x7a0);
          uVar34 = FUN_006ed8f0(uVar37);
          if ((*(int *)((ulong)((uVar34 & 0x1fff) * DAT_02692230) + 0x44 + DAT_02692228) != -1) &&
             (uVar31 != 0xffffffff)) {
            uVar26 = (ulong)((uVar31 & 0x1fff) * DAT_02689800);
            if ((((local_f0 & 2) != 0) || ((local_168 & 0x1000000000) != 0)) &&
               ((*(char *)(lVar30 + 0x7a4) != '\x01' &&
                ((*(byte *)(((DAT_026897f8 + uVar26) -
                            ((long)DAT_02689818 & *(ulong *)(DAT_026897f8 + 8 + uVar26))) + 0x120) &
                 2) != 0)))) {
              FUN_007373f0(lVar30,(local_168._4_4_ & 0x10) >> 4);
              if (uVar22 != 0xffffffff) {
                lVar38 = *(long *)(DAT_0273ea80 + 8);
                FUN_00923130(uVar22);
                pbVar3 = (byte *)(lVar38 + 0x610 + lVar47);
                *pbVar3 = *pbVar3 | 8;
              }
              local_f0 = local_f0 & 0xfffffffd;
              pbVar3 = (byte *)(lVar29 + 0x658 + lVar47);
              *pbVar3 = *pbVar3 | 8;
            }
          }
          FUN_00743720(uVar22,&local_168);
          iVar23 = FUN_00bd3540(uVar37);
          if ((iVar23 == -1) || (cVar17 = FUN_00bc9a60(iVar23), cVar17 == '\0')) {
            FUN_00629aa0(lVar29 + 0x828 + lVar47);
LAB_00916509:
            *(undefined4 *)(lVar29 + 0x838 + lVar47) = 0;
          }
          else {
            puVar4 = (undefined8 *)(lVar29 + 0x828 + lVar47);
            cVar17 = FUN_003f73b0(&uStack_b0);
            if (cVar17 != '\0') {
              puVar4[1] = local_a8;
              *puVar4 = CONCAT44(uStack_ac,uStack_b0);
              goto LAB_00916509;
            }
            cVar17 = FUN_003f73b0(puVar4);
            auVar55._8_56_ = extraout_var;
            auVar55._0_8_ = extraout_XMM0_Qa;
            if (cVar17 != '\0') {
              iVar23 = *(int *)(lVar29 + 0x838 + lVar47) + 1;
              *(int *)(lVar29 + 0x838 + lVar47) = iVar23;
              auVar52._0_4_ = (float)iVar23;
              auVar52._4_12_ = auVar55._4_12_;
              fVar50 = (float)FUN_005916e0(auVar52._0_8_);
              if (DAT_0166b528 < fVar50) {
                FUN_00629aa0(puVar4);
                *(undefined4 *)(lVar29 + 0x838 + lVar47) = 0;
              }
            }
          }
          if (*(char *)(DAT_0273ea90 + 0xa8) != '\0') {
            local_2b0 = *(long *)(DAT_0273ea90 + 0xa9);
            if ((*(long *)(*(long *)(DAT_0273ea80 + 8) + 0x620 + lVar47) == local_2b0) &&
               (local_328 = local_2b0,
               *(long *)(*(long *)(DAT_0273ea80 + 8) + 0x620 + lVar47) == local_2b0)) {
              plVar1 = (long *)(lVar29 + 0x81c + lVar47);
              cVar17 = FUN_003f73b0(&uStack_b0);
              if (cVar17 == '\0') {
                *(undefined4 *)plVar1 = 0xffffffff;
                *(undefined4 *)(lVar29 + 0x820 + lVar47) = 0xffffffff;
              }
              else {
                FUN_00072050(&local_328,uStack_ac);
                *plVar1 = local_328;
              }
            }
          }
          uVar26 = local_168;
          local_168 = CONCAT44(local_168._4_4_ & 0xff8ffffd | local_3e8,(undefined4)local_168);
          if (((char)uVar26 == '\x01') && ((char)(uVar26 >> 8) == *(char *)(lVar44 + 0xa58))) {
            local_17c = 0x811c9dc5;
            uVar26 = (ulong)((*(uint *)(lVar28 + 0x644) & 0x1fff) * DAT_02689800);
            uVar26 = (ulong)((*(uint *)(((uVar26 + DAT_026897f8) -
                                        (*(ulong *)(DAT_026897f8 + 8 + uVar26) & (long)DAT_02689818)
                                        ) + 0x68) & 0x1fff) * DAT_02689800);
            lVar28 = (DAT_026897f8 + uVar26) -
                     ((long)DAT_02689818 & *(ulong *)(DAT_026897f8 + 8 + uVar26));
            if (*(int *)(lVar28 + 0x7a0) != -1) {
              FUN_006ed8f0();
            }
            FUN_00730e60(&local_298);
            uVar26 = local_160;
            local_298 = CONCAT44(local_298._4_4_,local_168._4_4_);
            if ((local_168 & 0x20000000000000) == 0) {
              uVar24 = local_160._4_4_;
              uVar32 = FUN_00090a10(&local_328);
              lVar29 = *(long *)(DAT_0273ea80 + 8);
              FUN_000ab3c0(uVar24,uVar26 & 0xffffffff,&local_348);
              FUN_00090c20(uVar32,&local_348);
              iVar23 = *(int *)(lVar29 + 0x644 + lVar47);
              if (iVar23 != -1) {
                FUN_00bd4e70(iVar23,uVar32);
              }
              local_278 = (undefined4)local_328;
              uStack_274 = (undefined4)((ulong)local_328 >> 0x20);
              uStack_270 = (undefined1)uStack_320;
              uStack_26f = (undefined7)((ulong)uStack_320 >> 8);
              local_268._8_8_ = uStack_320;
              local_268._0_8_ = local_328;
              local_188 = local_158;
            }
            else {
              local_328 = FUN_00090ae0(lVar28 + 0x9f4);
              local_278 = (undefined4)local_328;
              uStack_274 = (undefined4)((ulong)local_328 >> 0x20);
              uStack_270 = (undefined1)extraout_XMM0_Qb_02;
              uStack_26f = (undefined7)((ulong)extraout_XMM0_Qb_02 >> 8);
              local_268._8_8_ = extraout_XMM0_Qb_02;
              local_268._0_8_ = local_328;
              local_188 = *(undefined4 *)(lVar28 + 0xa3c);
              local_298 = local_298 & 0xffffffffffdfffff;
              uStack_320 = extraout_XMM0_Qb_02;
            }
            if (*(char *)(DAT_0273ea90 + 0xa8) == '\0') {
LAB_0091691e:
              auVar11._8_8_ = uStack_320;
              auVar11._0_8_ = local_328;
              auVar52 = vandps_avx(auVar11,_DAT_0166b470);
              fVar50 = auVar52._0_4_;
              auVar59._0_4_ = fVar50 * fVar50;
              fVar56 = auVar52._4_4_;
              auVar59._4_4_ = fVar56 * fVar56;
              fVar7 = auVar52._8_4_;
              auVar59._8_4_ = fVar7 * fVar7;
              fVar9 = auVar52._12_4_;
              auVar59._12_4_ = fVar9 * fVar9;
              auVar52 = vpshufd_avx(auVar59,0x55);
              auVar11 = vpshufd_avx(auVar59,0);
              auVar54 = vpshufd_avx(auVar59,0xaa);
              auVar60._0_4_ = auVar54._0_4_ + auVar11._0_4_ + auVar52._0_4_;
              auVar60._4_4_ = auVar54._4_4_ + auVar11._4_4_ + auVar52._4_4_;
              auVar60._8_4_ = auVar54._8_4_ + auVar11._8_4_ + auVar52._8_4_;
              auVar60._12_4_ = auVar54._12_4_ + auVar11._12_4_ + auVar52._12_4_;
              auVar54 = vrsqrtps_avx(auVar60);
              auVar65._4_4_ = uStack_144;
              auVar65._0_4_ = local_148;
              auVar65._8_4_ = uStack_140;
              auVar65._12_4_ = uStack_13c;
              fVar51 = auVar54._0_4_;
              fVar6 = auVar54._4_4_;
              fVar8 = auVar54._8_4_;
              fVar10 = auVar54._12_4_;
              auVar64._0_4_ = fVar51 * fVar51 * auVar60._0_4_ * (float)DAT_0166b480;
              auVar64._4_4_ = fVar6 * fVar6 * auVar60._4_4_ * DAT_0166b480._4_4_;
              auVar64._8_4_ = fVar8 * fVar8 * auVar60._8_4_ * DAT_0166b480._8_4_;
              auVar64._12_4_ = fVar10 * fVar10 * auVar60._12_4_ * DAT_0166b480._12_4_;
              auVar52 = vsubps_avx(_DAT_0166b480,auVar64);
              auVar63._0_4_ = fVar51 + fVar51 * auVar52._0_4_;
              auVar63._4_4_ = fVar6 + fVar6 * auVar52._4_4_;
              auVar63._8_4_ = fVar8 + fVar8 * auVar52._8_4_;
              auVar63._12_4_ = fVar10 + fVar10 * auVar52._12_4_;
              auVar11 = vcmpps_avx(auVar63,auVar63,0);
              auVar52 = vandps_avx(auVar11,auVar63);
              auVar11 = vandnps_avx(auVar11,auVar54);
              auVar52 = vorps_avx(auVar11,auVar52);
              auVar54._0_4_ = fVar50 * auVar52._0_4_;
              auVar54._4_4_ = fVar56 * auVar52._4_4_;
              auVar54._8_4_ = fVar7 * auVar52._8_4_;
              auVar54._12_4_ = fVar9 * auVar52._12_4_;
              auVar52 = vcmpps_avx(auVar52,_DAT_0166b490,0);
              local_198 = vandnps_avx(auVar52,auVar54);
            }
            else {
              local_2a0 = *(long *)(DAT_0273ea90 + 0xa9);
              if (*(long *)(*(long *)(DAT_0273ea80 + 8) + 0x620 + lVar47) != local_2a0)
              goto LAB_0091691e;
              thunk_FUN_012aa7c6(*(long *)(DAT_0273ea80 + 8) + 0x2930 + lVar47,&local_168,0xdc);
              uVar21 = uStack_144;
              uVar24 = local_148;
              auVar65._12_4_ = uStack_13c;
              auVar65._8_4_ = uStack_140;
              auVar12._4_4_ = uStack_274;
              auVar12._0_4_ = local_278;
              auVar12[8] = uStack_270;
              auVar12._9_7_ = uStack_26f;
              auVar52 = vandps_avx(auVar12,_DAT_0166b470);
              fVar50 = auVar52._0_4_;
              auVar61._0_4_ = fVar50 * fVar50;
              fVar56 = auVar52._4_4_;
              auVar61._4_4_ = fVar56 * fVar56;
              fVar7 = auVar52._8_4_;
              fVar10 = auVar52._12_4_;
              auVar61._8_4_ = fVar7 * fVar7;
              auVar61._12_4_ = fVar10 * fVar10;
              uVar32 = FUN_00097c30(local_160 & 0xffffffff,local_160._4_4_);
              auVar65._4_4_ = uVar21;
              auVar65._0_4_ = uVar24;
              local_278 = (undefined4)uVar32;
              uStack_274 = (undefined4)((ulong)uVar32 >> 0x20);
              uStack_270 = (undefined1)extraout_XMM0_Qb_03;
              uStack_26f = (undefined7)((ulong)extraout_XMM0_Qb_03 >> 8);
              auVar52 = vpshufd_avx(auVar61,0x55);
              auVar11 = vpshufd_avx(auVar61,0);
              auVar54 = vpshufd_avx(auVar61,0xaa);
              auVar53._0_4_ = auVar54._0_4_ + auVar11._0_4_ + auVar52._0_4_;
              auVar53._4_4_ = auVar54._4_4_ + auVar11._4_4_ + auVar52._4_4_;
              auVar53._8_4_ = auVar54._8_4_ + auVar11._8_4_ + auVar52._8_4_;
              auVar53._12_4_ = auVar54._12_4_ + auVar11._12_4_ + auVar52._12_4_;
              auVar54 = vrsqrtps_avx(auVar53);
              fVar51 = auVar54._0_4_;
              fVar6 = auVar54._4_4_;
              fVar8 = auVar54._8_4_;
              fVar9 = auVar54._12_4_;
              local_268[8] = uStack_270;
              local_268._0_8_ = uVar32;
              local_268._9_7_ = uStack_26f;
              auVar62._0_4_ = fVar51 * fVar51 * auVar53._0_4_ * (float)DAT_0166b480;
              auVar62._4_4_ = fVar6 * fVar6 * auVar53._4_4_ * DAT_0166b480._4_4_;
              auVar62._8_4_ = fVar8 * fVar8 * auVar53._8_4_ * DAT_0166b480._8_4_;
              auVar62._12_4_ = fVar9 * fVar9 * auVar53._12_4_ * DAT_0166b480._12_4_;
              auVar52 = vsubps_avx(_DAT_0166b480,auVar62);
              auVar57._0_4_ = fVar51 + fVar51 * auVar52._0_4_;
              auVar57._4_4_ = fVar6 + fVar6 * auVar52._4_4_;
              auVar57._8_4_ = fVar8 + fVar8 * auVar52._8_4_;
              auVar57._12_4_ = fVar9 + fVar9 * auVar52._12_4_;
              auVar11 = vcmpps_avx(auVar57,auVar57,0);
              auVar52 = vandps_avx(auVar11,auVar57);
              auVar11 = vandnps_avx(auVar11,auVar54);
              auVar52 = vorps_avx(auVar11,auVar52);
              auVar58._0_4_ = fVar50 * auVar52._0_4_;
              auVar58._4_4_ = fVar56 * auVar52._4_4_;
              auVar58._8_4_ = fVar7 * auVar52._8_4_;
              auVar58._12_4_ = fVar10 * auVar52._12_4_;
              auVar52 = vcmpps_avx(auVar52,_DAT_0166b490,0);
              local_198 = vandnps_avx(auVar52,auVar58);
            }
            auVar52 = vandps_avx(auVar65,_DAT_0166b470);
            _local_1a8 = auVar52;
            if ((local_108 & 1) != 0) {
              local_1a8._0_4_ = auVar52._0_4_ + _DAT_0166b4a0;
              local_1a8._4_4_ = auVar52._4_4_ + fRam000000000166b4a4;
              fStack_1a0 = auVar52._8_4_ + fRam000000000166b4a8;
              fStack_19c = auVar52._12_4_ + fRam000000000166b4ac;
            }
            if ((local_108 & 2) != 0) {
              fVar51 = local_1a8._0_4_;
              fVar56 = local_1a8._8_4_;
              fVar50 = local_1a8._12_4_;
              local_1a8._4_4_ = local_1a8._4_4_ + fRam000000000166b4b4;
              local_1a8._0_4_ = fVar51 + _DAT_0166b4b0;
              fStack_1a0 = fVar56 + fRam000000000166b4b8;
              fStack_19c = fVar50 + fRam000000000166b4bc;
            }
            local_280 = CONCAT44(local_f4,local_f8);
            local_184 = local_138;
            local_288 = local_ec;
            local_258 = local_e4;
            uStack_230 = CONCAT44(uStack_cc,uStack_d0);
            uStack_210 = CONCAT44(uStack_ac,uStack_b0);
            local_228 = local_c8;
            uStack_220 = uStack_c0;
            local_238 = local_d8;
            local_208 = local_a8;
            uStack_200 = uStack_a0;
            local_218 = local_b8;
            local_244 = local_98;
            FUN_00734510(lVar28,&local_298,0);
          }
          FUN_00ba0010(uVar22,&local_168);
        }
        else if (*(int *)(lVar44 + 0x9d4) == -1) {
          local_17c = 0x811c9dc5;
          FUN_00730e60(&local_298);
          local_198._0_8_ = FUN_00090ae0(lVar44 + 0x9e8);
          local_198._8_8_ = extraout_XMM0_Qb;
          uVar32 = FUN_00090ae0(lVar44 + 0x9f4);
          local_278 = (undefined4)uVar32;
          uStack_274 = (undefined4)((ulong)uVar32 >> 0x20);
          uStack_270 = (undefined1)extraout_XMM0_Qb_00;
          uStack_26f = (undefined7)((ulong)extraout_XMM0_Qb_00 >> 8);
          local_268._0_8_ = FUN_00090ae0(lVar44 + 0xa18);
          local_268._8_8_ = extraout_XMM0_Qb_01;
          FUN_00734510(lVar44,&local_298,0);
        }
      }
    }
    lVar28 = FUN_00074a90(local_388);
    uVar22 = local_380;
  } while( true );
}

