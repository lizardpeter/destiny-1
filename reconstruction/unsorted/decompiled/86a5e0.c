
/* WARNING: Type propagation algorithm not settling */
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8
FUN_0086a5e0(long *param_1,long param_2,undefined8 *param_3,undefined8 param_4,int *param_5)

{
  undefined8 *puVar1;
  long lVar2;
  long lVar3;
  long lVar4;
  undefined1 auVar5 [12];
  undefined1 auVar6 [16];
  undefined1 auVar7 [16];
  byte bVar8;
  char cVar9;
  char cVar10;
  char cVar11;
  undefined8 uVar12;
  long lVar13;
  float *pfVar14;
  ulong uVar15;
  long lVar16;
  undefined8 uVar17;
  undefined8 uVar18;
  int iVar19;
  long lVar20;
  ulong uVar21;
  uint uVar22;
  uint uVar23;
  ulong uVar25;
  undefined4 uVar26;
  undefined1 auVar27 [16];
  undefined1 auVar28 [16];
  undefined1 auVar29 [16];
  undefined1 auVar30 [16];
  float fVar31;
  float fVar35;
  float fVar36;
  undefined1 auVar32 [16];
  undefined1 auVar33 [16];
  undefined1 auVar34 [16];
  float fVar37;
  undefined1 auVar38 [16];
  undefined1 auVar39 [16];
  undefined1 auVar40 [16];
  undefined1 auVar41 [16];
  undefined1 auVar42 [16];
  undefined1 auVar43 [16];
  undefined1 auVar44 [16];
  undefined1 auVar45 [16];
  undefined1 auVar46 [16];
  undefined1 auVar47 [16];
  undefined1 auVar48 [16];
  undefined1 auVar49 [16];
  int local_9c;
  undefined8 local_68;
  undefined8 uStack_60;
  uint local_54 [3];
  undefined4 local_48 [2];
  undefined4 local_40 [2];
  long local_38;
  ulong uVar24;
  
  local_38 = *DAT_01a1f100;
  puVar1 = *(undefined8 **)(param_2 + 0x10);
  uVar12 = 0;
  if ((puVar1 != (undefined8 *)0x0) && ((byte *)param_3[3] != (byte *)0x0)) {
    bVar8 = *(byte *)param_3[3];
    if (((bVar8 & 2) != 0) && (uVar12 = 0, param_5[1] != -1)) {
      lVar2 = *(long *)(param_1[8] + 0x1b340);
      lVar3 = *param_1;
      local_40[0] = 0xffffffff;
      local_48[0] = 0xffffffff;
      local_54[1] = 0xffffffff;
      local_54[0] = 0;
      local_9c = *(int *)(puVar1 + 6);
      uVar21 = 0;
      if ((bVar8 & 1) != 0) {
        uVar21 = (ulong)(*(byte *)((long)puVar1 + 0x3c) >> 1);
      }
      bVar8 = *(byte *)((long)puVar1 + 0x3d);
      uVar12 = 1;
      if (bVar8 != 0) {
        uVar25 = uVar21 << 4 | 8;
        uVar24 = uVar21;
        while( true ) {
          lVar4 = puVar1[3];
          iVar19 = 0;
          if (*(int *)(lVar4 + -8 + uVar25) != 0) {
            uVar12 = FUN_0082b940(lVar3,0x18,0x80);
            lVar13 = FUN_0082b940(lVar3,0x1a,0x40);
            pfVar14 = (float *)FUN_0082b940(lVar3,8,0x80);
            uVar26 = FUN_0087aca0(*(undefined4 *)(lVar2 + 0x30),*(undefined4 *)((long)puVar1 + 0x34)
                                  ,*(undefined8 *)(lVar2 + 0x48));
            *(undefined4 *)(lVar13 + 0x2c) = uVar26;
            fVar31 = _DAT_016653d0;
            *(float *)(lVar13 + 0x30) = (float)(int)*(short *)((long)param_5 + 0xe) * _DAT_016653d0;
            *(float *)(lVar13 + 0x34) = (float)(int)(short)param_5[5] * fVar31;
            if (param_5[7] == 1) {
              FUN_00869ae0(param_5,local_40,local_48,local_54 + 1,pfVar14,local_54);
            }
            uVar15 = (ulong)local_54[0];
            thunk_FUN_012aa7c6(uVar12,puVar1[2],*(undefined1 *)((long)puVar1 + 0x3b));
            *(float *)(lVar13 + 0x20) = (float)uVar15;
            auVar7 = _DAT_01665390;
            auVar6 = _DAT_01665380;
            auVar28 = *(undefined1 (*) [16])(puVar1[4] + -0x10 + uVar25 * 2);
            fVar31 = auVar28._0_4_;
            auVar32._0_4_ = fVar31 * fVar31;
            fVar35 = auVar28._4_4_;
            auVar32._4_4_ = fVar35 * fVar35;
            fVar36 = auVar28._8_4_;
            auVar32._8_4_ = fVar36 * fVar36;
            fVar37 = auVar28._12_4_;
            auVar32._12_4_ = fVar37 * fVar37;
            auVar30 = vpshufd_avx(auVar32,0x4e);
            auVar33._0_4_ = auVar32._0_4_ + auVar30._0_4_;
            auVar33._4_4_ = auVar32._4_4_ + auVar30._4_4_;
            auVar33._8_4_ = auVar32._8_4_ + auVar30._8_4_;
            auVar33._12_4_ = auVar32._12_4_ + auVar30._12_4_;
            auVar30 = vpshufd_avx(auVar33,0x93);
            auVar38._0_4_ = auVar33._0_4_ + auVar30._0_4_;
            auVar38._4_4_ = auVar33._4_4_ + auVar30._4_4_;
            auVar38._8_4_ = auVar33._8_4_ + auVar30._8_4_;
            auVar38._12_4_ = auVar33._12_4_ + auVar30._12_4_;
            auVar30 = vcmpps_avx(_DAT_01ac6320,auVar38,1);
            auVar32 = vdivps_avx(_DAT_01665370,auVar38);
            auVar41._0_4_ = auVar32._0_4_ * DAT_01ac63d0;
            auVar41._4_4_ = auVar32._4_4_ * fRam0000000001ac63d4;
            auVar41._8_4_ = auVar32._8_4_ * fRam0000000001ac63d8;
            auVar41._12_4_ = auVar32._12_4_ * fRam0000000001ac63dc;
            auVar32 = vpshufd_avx(auVar28,0xff);
            auVar29 = vpshufd_avx(auVar28,0);
            auVar27 = vpshufd_avx(auVar28,0x25);
            auVar28 = vandps_avx(auVar30,auVar41);
            auVar30 = vpand_avx(auVar27,_DAT_01665360);
            auVar27._0_4_ = fVar31 * auVar28._0_4_;
            auVar27._4_4_ = fVar35 * auVar28._4_4_;
            auVar27._8_4_ = fVar36 * auVar28._8_4_;
            auVar27._12_4_ = fVar37 * auVar28._12_4_;
            auVar28 = vpshufd_avx(auVar27,0x29);
            auVar28 = vpand_avx(auVar28,_DAT_01665360);
            auVar34._0_4_ = auVar30._0_4_ * auVar28._0_4_;
            auVar34._4_4_ = auVar30._4_4_ * auVar28._4_4_;
            auVar34._8_4_ = auVar30._8_4_ * auVar28._8_4_;
            auVar34._12_4_ = auVar30._12_4_ * auVar28._12_4_;
            auVar28 = vpshufd_avx(auVar34,8);
            auVar43._0_4_ = auVar29._0_4_ * auVar27._0_4_;
            auVar43._4_4_ = auVar29._4_4_ * auVar27._4_4_;
            auVar43._8_4_ = auVar29._8_4_ * auVar27._8_4_;
            auVar43._12_4_ = auVar29._12_4_ * auVar27._12_4_;
            auVar30 = vpshufd_avx(auVar43,0);
            auVar5 = ZEXT812(0) << 0x20;
            auVar38 = ZEXT816(0) << 0x40;
            auVar29 = vshufps_avx(auVar30,auVar38,4);
            auVar28 = vpand_avx(auVar28,_DAT_01665360);
            auVar46._0_4_ = auVar32._0_4_ * auVar27._0_4_;
            auVar46._4_4_ = auVar32._4_4_ * auVar27._4_4_;
            auVar46._8_4_ = auVar32._8_4_ * auVar27._8_4_;
            auVar46._12_4_ = auVar32._12_4_ * auVar27._12_4_;
            auVar30 = vpshufd_avx(auVar46,6);
            auVar27 = vshufps_avx(auVar30,auVar38,4);
            auVar30 = vpshufd_avx(auVar43,9);
            auVar33 = vshufps_avx(auVar30,auVar38,4);
            auVar48._0_4_ = auVar33._0_4_ + auVar27._0_4_;
            auVar48._4_4_ = auVar33._4_4_ + auVar27._4_4_;
            auVar48._8_4_ = auVar33._8_4_ + auVar27._8_4_;
            auVar48._12_4_ = auVar33._12_4_ + auVar27._12_4_;
            auVar30 = vpshufd_avx(auVar48,0);
            auVar30 = vpand_avx(auVar30,_DAT_01665380);
            auVar32 = vpor_avx(auVar30,ZEXT416(0x3f800000));
            auVar27 = vsubps_avx(auVar33,auVar27);
            auVar30 = vpshufd_avx(auVar27,0x10);
            auVar30 = vpand_avx(auVar30,_DAT_01665390);
            auVar49._0_4_ = auVar30._0_4_ + auVar32._0_4_;
            auVar49._4_4_ = auVar30._4_4_ + auVar32._4_4_;
            auVar49._8_4_ = auVar30._8_4_ + auVar32._8_4_;
            auVar49._12_4_ = auVar30._12_4_ + auVar32._12_4_;
            auVar30 = vpand_avx(auVar34,_DAT_01665390);
            auVar47._0_4_ = auVar30._0_4_ + auVar29._0_4_ + auVar28._0_4_;
            auVar47._4_4_ = auVar30._4_4_ + auVar29._4_4_ + auVar28._4_4_;
            auVar47._8_4_ = auVar30._8_4_ + auVar29._8_4_ + auVar28._8_4_;
            auVar47._12_4_ = auVar30._12_4_ + auVar29._12_4_ + auVar28._12_4_;
            auVar28 = vpshufd_avx(auVar46,0);
            auVar30 = vpandn_avx(_DAT_01ac6290,auVar28);
            auVar28 = vsubps_avx(auVar38,auVar28);
            auVar28 = vpand_avx(_DAT_01ac6290,auVar28);
            auVar32 = vpshufd_avx(auVar47,2);
            auVar44._0_4_ = auVar32._0_4_;
            auVar44._4_12_ = auVar5;
            auVar29 = vsubps_avx(auVar49,auVar44);
            auVar28 = vpor_avx(auVar30,auVar28);
            auVar30 = vpshufd_avx(auVar34,0x55);
            auVar42._0_4_ = auVar30._0_4_ + auVar28._0_4_;
            auVar42._4_4_ = auVar30._4_4_ + auVar28._4_4_;
            auVar42._8_4_ = auVar30._8_4_ + auVar28._8_4_;
            auVar42._12_4_ = auVar30._12_4_ + auVar28._12_4_;
            auVar28 = *(undefined1 (*) [16])(puVar1[4] + uVar25 * 2);
            auVar30 = vpand_avx(auVar28,_DAT_01665360);
            auVar28 = vpshufd_avx(auVar28,0xff);
            auVar32 = vpor_avx(auVar30,_DAT_016653a0);
            fVar31 = auVar28._0_4_;
            fVar35 = auVar28._4_4_;
            fVar36 = auVar28._8_4_;
            fVar37 = auVar28._12_4_;
            *pfVar14 = fVar31 * auVar29._0_4_;
            pfVar14[1] = fVar35 * auVar29._4_4_;
            pfVar14[2] = fVar36 * auVar29._8_4_;
            pfVar14[3] = fVar37 * auVar29._12_4_;
            auVar28 = vpshufd_avx(auVar42,0);
            auVar30 = vpand_avx(auVar28,auVar7);
            auVar39._4_12_ = auVar5;
            auVar39._0_4_ = auVar27._0_4_;
            auVar28 = vorps_avx(auVar39,_DAT_016653b0);
            auVar40._0_4_ = auVar28._0_4_ + auVar30._0_4_;
            auVar40._4_4_ = auVar28._4_4_ + auVar30._4_4_;
            auVar40._8_4_ = auVar28._8_4_ + auVar30._8_4_;
            auVar40._12_4_ = auVar28._12_4_ + auVar30._12_4_;
            auVar28 = vpand_avx(auVar47,auVar6);
            auVar28 = vsubps_avx(auVar40,auVar28);
            auVar45._0_4_ = fVar31 * auVar28._0_4_;
            auVar45._4_4_ = fVar35 * auVar28._4_4_;
            auVar45._8_4_ = fVar36 * auVar28._8_4_;
            auVar45._12_4_ = fVar37 * auVar28._12_4_;
            auVar30 = vpand_avx(auVar42,auVar6);
            auVar28 = vpshufd_avx(auVar48,1);
            auVar28._4_12_ = auVar5;
            *(undefined1 (*) [16])(pfVar14 + 4) = auVar45;
            auVar28 = vorps_avx(auVar28,_DAT_016653c0);
            auVar29._0_4_ = auVar28._0_4_ + auVar30._0_4_;
            auVar29._4_4_ = auVar28._4_4_ + auVar30._4_4_;
            auVar29._8_4_ = auVar28._8_4_ + auVar30._8_4_;
            auVar29._12_4_ = auVar28._12_4_ + auVar30._12_4_;
            auVar28 = vpshufd_avx(auVar47,0);
            auVar28 = vpand_avx(auVar28,auVar7);
            auVar28 = vsubps_avx(auVar29,auVar28);
            auVar30._0_4_ = fVar31 * auVar28._0_4_;
            auVar30._4_4_ = fVar35 * auVar28._4_4_;
            auVar30._8_4_ = fVar36 * auVar28._8_4_;
            auVar30._12_4_ = fVar37 * auVar28._12_4_;
            *(undefined1 (*) [16])(pfVar14 + 8) = auVar30;
            *(undefined1 (*) [16])(pfVar14 + 0xc) = auVar32;
            FUN_00869be0(puVar1,lVar3,lVar13 + 0x10);
            lVar13 = 0;
            uVar23 = param_5[1];
            if (uVar23 != 0xffffffff) {
              lVar20 = (ulong)(((uint)((int)uVar23 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar23 >> 0xd) *
                       0x40;
              lVar13 = *DAT_01a238a0;
              lVar16 = *(long *)(lVar13 + 0x10 + lVar20);
              uVar15 = (ulong)((uVar23 & 0x1fff) * *(int *)(lVar13 + 0x30 + lVar20));
              lVar13 = (lVar16 + uVar15) -
                       ((long)*(int *)(lVar13 + 0x34 + lVar20) & *(ulong *)(lVar16 + 8 + uVar15));
            }
            local_68 = *param_3;
            uStack_60 = param_3[1];
            cVar9 = FUN_00890210(0,0,lVar13,&local_68,*(undefined2 *)(puVar1 + 7),
                                 param_1[6] + 0x2800,(int)param_1[0xe],*param_1);
            lVar16 = FUN_0082cb90(2);
            if (lVar16 != 0) {
              cVar10 = FUN_0081fd20(lVar3,lVar16,*(undefined8 *)(lVar3 + 0x15c0));
              if (cVar10 == '\0') {
                cVar11 = FUN_0082bd10(lVar3,1,lVar16 + 0x20);
                cVar10 = '\0';
                if (cVar11 != '\0') {
                  cVar10 = FUN_0082bd10(lVar3,2,lVar16 + 0xb0);
                }
              }
              if (cVar10 != '\0') {
                *(byte *)(lVar3 + 0x15ac) = *(byte *)(lVar3 + 0x15ac) | 4;
                lVar16 = *param_1;
                uVar12 = *(undefined8 *)(lVar16 + 0x15c0);
                FUN_007dec00(uVar12,0,(ulong)*(byte *)((long)param_5 + 0x16) << 4);
                uVar18 = *(undefined8 *)(*param_1 + 0x15c0);
                uVar17 = FUN_0082e430((char)param_5[6]);
                FUN_007deb70(uVar18,uVar17,0);
                uVar26 = FUN_0087f3f0();
                FUN_007dec20(uVar18,uVar26,0,*(undefined4 *)(lVar4 + -4 + uVar25),0);
                if (*param_5 != -1) {
                  cVar10 = FUN_00876200(param_5[7]);
                  if (cVar10 == '\0') {
                    uVar26 = FUN_0087f430();
                    FUN_007dec00(uVar12,0,(ulong)*(byte *)((long)param_5 + 0x17) << 4);
                    uVar18 = FUN_0082e430(*(undefined1 *)((long)param_5 + 0x19));
                    FUN_007deb70(uVar12,uVar18,0);
                    FUN_007dec20(uVar12,uVar26,0,local_9c,0);
                    FUN_007dec10(uVar12);
                  }
                }
                uVar26 = local_48[0];
                uVar23 = local_54[0];
                uVar18 = *puVar1;
                *(undefined8 *)(&DAT_000013e0 + lVar16) = puVar1[1];
                *(undefined8 *)(&DAT_000013d8 + lVar16) = uVar18;
                uVar18 = *(undefined8 *)(*param_1 + 0x15c0);
                iVar19 = param_5[7];
                if ((iVar19 == 0) || (iVar19 == 5)) {
                  uVar26 = FUN_0087f440();
                  FUN_007dee30(uVar18,uVar26);
                  uVar22 = 6;
                }
                else {
                  uVar22 = 0xffffffff;
                  if (iVar19 == 1) {
                    FUN_007dec20(uVar18,local_40[0],1,0,0);
                    FUN_007dee30(uVar18,uVar26);
                    uVar22 = uVar23;
                  }
                }
                cVar10 = FUN_0082b490(*param_1,lVar13);
                if (cVar10 != '\0') {
                  FUN_00879f00(param_5,lVar13,lVar16,*(undefined2 *)(lVar4 + -8 + uVar25),uVar22,
                               *(undefined2 *)(lVar4 + uVar25),*(undefined4 *)(lVar4 + -4 + uVar25))
                  ;
                }
                *(undefined4 *)(&DAT_000013d8 + lVar16) = 0;
                *(undefined8 *)(&DAT_000013e0 + lVar16) = 0;
                FUN_007dec10(uVar12);
              }
            }
            *(byte *)(lVar3 + 0x15ac) = *(byte *)(lVar3 + 0x15ac) & 0xfb;
            FUN_0082ba20(lVar3,8,0x80);
            if (cVar9 != '\0') {
              *(byte *)(lVar3 + 0x15ad) = *(byte *)(lVar3 + 0x15ad) & 0x7f;
            }
            FUN_0082ba20(lVar3,0x1a,0x40);
            FUN_0082ba20(lVar3,0x18,0x80);
            iVar19 = *(int *)(lVar4 + -8 + uVar25) << 4;
            bVar8 = *(byte *)((long)puVar1 + 0x3d);
          }
          uVar23 = (int)uVar24 + 1;
          uVar24 = (ulong)uVar23;
          if ((int)((uint)bVar8 + (int)uVar21) <= (int)uVar23) break;
          uVar25 = uVar25 + 0x10;
          local_9c = local_9c + iVar19 * (uint)*(byte *)((long)puVar1 + 0x3a);
        }
        uVar12 = 1;
      }
    }
  }
  if (*DAT_01a1f100 == local_38) {
    return uVar12;
  }
  uVar12 = thunk_FUN_012aa7f6();
  return uVar12;
}

