
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

ulong FUN_007fe460(long *param_1,long param_2,uint *param_3,undefined8 *param_4,long param_5,
                  long param_6,int param_7,int param_8,uint param_9,uint param_10)

{
  long *plVar1;
  undefined8 *puVar2;
  long *plVar3;
  long *plVar4;
  byte bVar5;
  ushort uVar6;
  int iVar7;
  long lVar8;
  long lVar9;
  undefined8 uVar10;
  undefined8 uVar11;
  undefined8 uVar12;
  undefined8 uVar13;
  undefined8 uVar14;
  byte bVar15;
  char cVar16;
  char cVar17;
  byte bVar18;
  ushort uVar19;
  int iVar20;
  long lVar21;
  undefined1 (*pauVar22) [16];
  long lVar23;
  undefined1 (*pauVar24) [16];
  long lVar25;
  long lVar26;
  long lVar27;
  ulong uVar28;
  long lVar29;
  ulong uVar30;
  byte bVar31;
  byte bVar32;
  uint uVar33;
  long lVar34;
  ulong uVar35;
  long lVar36;
  int iVar37;
  uint uVar38;
  undefined8 uVar39;
  long lVar40;
  bool bVar41;
  uint uVar42;
  undefined8 extraout_XMM0_Qa;
  undefined1 auVar43 [16];
  undefined1 auVar44 [16];
  undefined1 extraout_var [56];
  char *local_120;
  long local_b0;
  undefined1 local_88 [16];
  undefined8 local_48;
  undefined8 uStack_40;
  long local_38;
  undefined1 auVar45 [64];
  
  local_38 = *DAT_01a1f100;
  iVar7 = *(int *)(param_1[8] + 0x191dc);
  if ((char)param_3[1] == '\0') {
    bVar41 = false;
  }
  else {
    bVar41 = *(int *)(param_1[7] + 0x4e0) - 2U < 4;
  }
  uVar19 = 0;
  if ((((byte)param_3[0xc] < 4) && (uVar19 = 0, !bVar41)) &&
     (lVar8 = *(long *)(param_3 + 10), uVar19 = 0, 0 < *(long *)(lVar8 + 0x10))) {
    uVar33 = (int)*(uint *)(param_5 + 0xb8) >> 0xd;
    bVar31 = *(byte *)((long)param_3 + 6);
    uVar38 = *param_3;
    lVar40 = *(long *)(param_5 + 0xc0);
    lVar9 = *param_1;
    lVar23 = *DAT_01a238a0;
    lVar21 = (ulong)((uVar33 >> 0x12 | 0x3ff) & uVar33) * 0x40;
    lVar25 = *(long *)(lVar23 + 0x10 + lVar21);
    iVar37 = *(int *)(lVar23 + 0x34 + lVar21);
    uVar28 = (ulong)((*(uint *)(param_5 + 0xb8) & 0x1fff) * *(int *)(lVar23 + 0x30 + lVar21));
    uVar30 = *(ulong *)(lVar25 + 8 + uVar28);
    pauVar22 = (undefined1 (*) [16])FUN_0082b940(lVar9,8,0x80);
    uVar14 = uRam00000000016612e8;
    uVar13 = _DAT_016612e0;
    uVar12 = uRam00000000016612d8;
    uVar11 = _DAT_016612d0;
    uVar39 = uRam00000000016612c8;
    uVar10 = _DAT_016612c0;
    plVar1 = (long *)(lVar8 + 0x18);
    *pauVar22 = ZEXT416(DAT_01660974);
    *(undefined8 *)pauVar22[1] = uVar13;
    *(undefined8 *)(pauVar22[1] + 8) = uVar14;
    *(undefined8 *)pauVar22[2] = uVar11;
    *(undefined8 *)(pauVar22[2] + 8) = uVar12;
    *(undefined8 *)pauVar22[3] = uVar10;
    *(undefined8 *)(pauVar22[3] + 8) = uVar39;
    puVar2 = (undefined8 *)(*(long *)(lVar8 + 0x18) + 0x28 + lVar8);
    uVar10 = puVar2[1];
    *(undefined8 *)pauVar22[4] = *puVar2;
    *(undefined8 *)(pauVar22[4] + 8) = uVar10;
    puVar2 = (undefined8 *)(*(long *)(lVar8 + 0x18) + 0x38 + lVar8);
    uVar10 = puVar2[1];
    *(undefined8 *)pauVar22[5] = *puVar2;
    *(undefined8 *)(pauVar22[5] + 8) = uVar10;
    puVar2 = (undefined8 *)(*(long *)(lVar8 + 0x18) + 0x48 + lVar8);
    uVar10 = puVar2[1];
    *(undefined8 *)pauVar22[6] = *puVar2;
    *(undefined8 *)(pauVar22[6] + 8) = uVar10;
    if (*(uint *)(param_1 + 0xe) < 0x11) {
      uVar33 = 0x114cfU >> ((byte)*(uint *)(param_1 + 0xe) & 0x1f) & 1;
      bVar41 = uVar33 == 0;
      if ((*(char *)(param_5 + 0xb4) != '\0') && (uVar33 != 0)) {
        lVar23 = FUN_0082b940(lVar9,0x19,0x18);
        FUN_008213f0(lVar23,*(undefined4 *)(param_5 + 0xa0));
        FUN_008213f0(lVar23 + 8,*(undefined4 *)(param_5 + 0xa4));
        FUN_008213f0(lVar23 + 0x10,*(undefined4 *)(param_5 + 0xa8));
        lVar23 = FUN_0082b940(lVar9,0x1b,0x70);
        uVar10 = uRam00000000016612d8;
        uVar33 = *(uint *)(param_5 + 0x88);
        if (uVar33 == 0xffffffff) {
          *(undefined8 *)(lVar23 + 0x20) = _DAT_016612d0;
          *(undefined8 *)(lVar23 + 0x28) = uVar10;
        }
        else {
          lVar27 = (ulong)(((uint)((int)uVar33 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar33 >> 0xd) * 0x40
          ;
          lVar21 = *DAT_01a238a0;
          lVar26 = *(long *)(lVar21 + 0x10 + lVar27);
          uVar35 = (ulong)((uVar33 & 0x1fff) * *(int *)(lVar21 + 0x30 + lVar27));
          lVar21 = (lVar26 + uVar35) -
                   ((long)*(int *)(lVar21 + 0x34 + lVar27) & *(ulong *)(lVar26 + 8 + uVar35));
          FUN_008213f0(lVar23,*(undefined4 *)(lVar21 + 0x60));
          FUN_008213f0(lVar23 + 8,*(undefined4 *)(lVar21 + 100));
          uVar10 = *(undefined8 *)(lVar21 + 0x78);
          *(undefined8 *)(lVar23 + 0x10) = *(undefined8 *)(lVar21 + 0x70);
          *(undefined8 *)(lVar23 + 0x18) = uVar10;
          uVar10 = *(undefined8 *)(lVar21 + 0x58);
          *(undefined8 *)(lVar23 + 0x20) = *(undefined8 *)(lVar21 + 0x50);
          *(undefined8 *)(lVar23 + 0x28) = uVar10;
          uVar10 = *(undefined8 *)(lVar21 + 0x98);
          *(undefined8 *)(lVar23 + 0x40) = *(undefined8 *)(lVar21 + 0x90);
          *(undefined8 *)(lVar23 + 0x48) = uVar10;
          uVar10 = *(undefined8 *)(lVar21 + 0xa8);
          *(undefined8 *)(lVar23 + 0x50) = *(undefined8 *)(lVar21 + 0xa0);
          *(undefined8 *)(lVar23 + 0x58) = uVar10;
          uVar10 = *(undefined8 *)(lVar21 + 0x88);
          *(undefined8 *)(lVar23 + 0x30) = *(undefined8 *)(lVar21 + 0x80);
          *(undefined8 *)(lVar23 + 0x38) = uVar10;
        }
        local_88._12_4_ = 0;
        local_88._0_12_ = ZEXT812(0);
        local_88 = local_88 << 0x20;
        uVar42 = 0;
        if (uVar33 == 0xffffffff) {
          uVar42 = DAT_01660974;
        }
        auVar44 = vpshufd_avx(*(undefined1 (*) [16])(lVar23 + 0x30),0x24);
        auVar43._4_12_ = auVar44._4_12_;
        auVar43._0_4_ = uVar42;
        auVar43 = vpshufd_avx(auVar43,0x27);
        *(undefined1 (*) [16])(lVar23 + 0x30) = auVar43;
        pauVar24 = (undefined1 (*) [16])FUN_0082b940(auVar43._0_8_,auVar44._0_8_,lVar9,0x1f,0x10);
        iVar20 = FUN_00886ae0();
        if (iVar20 != 7) {
          local_88 = ZEXT416(DAT_01660974);
        }
        bVar41 = false;
        uVar33 = FUN_00886ae0();
        auVar45._8_56_ = extraout_var;
        auVar45._0_8_ = extraout_XMM0_Qa;
        auVar44._0_4_ = (float)uVar33;
        auVar44._4_12_ = auVar45._4_12_;
        auVar44 = vinsertps_avx(auVar44,local_88,0x10);
        auVar44 = vinsertps_avx(auVar44,ZEXT416(DAT_01660974),0x20);
        auVar44 = vinsertps_avx(auVar44,local_88,0x30);
        *pauVar24 = auVar44;
      }
    }
    else {
      bVar41 = true;
    }
    local_120 = (char *)(param_5 + 0xb4);
    lVar23 = *plVar1;
    lVar21 = *(long *)(lVar23 + 0x60 + (long)plVar1);
    uVar10 = *(undefined8 *)(lVar9 + 0x15c0);
    local_b0 = 0;
    if (lVar21 != 0) {
      local_b0 = (long)plVar1 + lVar21 + lVar23 + 0x70;
    }
    uVar19 = *(ushort *)((long)plVar1 + (long)param_7 * 2 + lVar23 + 0x68);
    lVar40 = ((lVar25 + uVar28) - ((long)iVar37 & uVar30)) + lVar40 + (ulong)uVar38 * 0x140;
    uVar30 = (ulong)(byte)param_7;
    plVar3 = (long *)(uVar30 * 0x10 + 0x338 + lVar40);
    uVar39 = 2;
    if (bVar31 == 0) {
      lVar25 = *plVar3;
      bVar31 = 1;
      uVar39 = 0;
      if ((lVar25 < 5) && (bVar31 = 0, 0 < lVar25)) {
        lVar21 = 0;
        bVar15 = 0;
        do {
          bVar31 = 1;
          if (param_3[(ulong)*param_3 * 4 + lVar21 + 0x14] != 0xffffffff) {
            bVar31 = bVar15;
          }
          lVar21 = lVar21 + 1;
          bVar15 = bVar31;
        } while (lVar21 < lVar25);
      }
    }
    lVar25 = FUN_007d9120((int)*(char *)((long)plVar1 + uVar30 + lVar23 + 0x90),uVar39,param_6);
    uVar39 = uRam0000000002709a48;
    if ((param_6 == 0) || (lVar25 != 0)) {
      *(undefined8 *)pauVar22[7] = _DAT_02709a40;
      *(undefined8 *)(pauVar22[7] + 8) = uVar39;
      lVar21 = *(long *)(param_1[8] + 0x658 + (long)*(int *)(param_5 + 0x68) * 8);
      uVar39 = *(undefined8 *)(lVar21 + 0x68);
      *(undefined8 *)pauVar22[7] = *(undefined8 *)(lVar21 + 0x60);
      *(undefined8 *)(pauVar22[7] + 8) = uVar39;
      bVar15 = 0;
      if ((lVar21 != 0) && ((bVar31 & 1) != 0)) {
        bVar15 = FUN_008980e0(*(undefined4 *)(param_5 + 100),*(undefined4 *)(param_5 + 0x60),lVar21,
                              lVar9);
      }
      uVar38 = 0x20;
      if (*(char *)((long)param_3 + 5) != '\0') {
        uVar38 = 0xa0;
      }
      lVar26 = param_1[7];
      if (*(int *)(lVar26 + 0x4e0) == 5) {
        lVar27 = *(long *)(lVar26 + 0x4e8);
        if (*(long *)(lVar26 + 0x4e8) == 0) {
          lVar27 = lVar26;
        }
        if (*(int *)(lVar27 + 0x110) == 2) {
          iVar37 = *(int *)(lVar21 + 0x7c);
          if (iVar37 == 2) {
            uVar33 = 0x88;
          }
          else if (iVar37 == 1) {
            uVar33 = 0x80;
          }
          else {
            uVar33 = 0;
            if (iVar37 == 0) {
              uVar33 = 8;
            }
          }
          uVar38 = uVar33 | uVar38;
        }
      }
      *(undefined4 *)(*param_1 + 0x15d4) = 0;
      FUN_007e10e0(*(undefined8 *)(*param_1 + 0x15c0),uVar38,0xa8);
      lVar21 = FUN_0082cb90(2);
      if (lVar21 != 0) {
        cVar16 = FUN_0081fd20(lVar9,lVar21,*(undefined8 *)(lVar9 + 0x15c0));
        if (cVar16 == '\0') {
          cVar17 = FUN_0082bd10(lVar9,1,lVar21 + 0x20);
          cVar16 = '\0';
          if (cVar17 != '\0') {
            cVar16 = FUN_0082bd10(lVar9,2,lVar21 + 0xb0);
          }
        }
        if (cVar16 != '\0') {
          *(byte *)(lVar9 + 0x15ac) = *(byte *)(lVar9 + 0x15ac) | 4;
          if (0 < *plVar3) {
            lVar21 = *(long *)(param_3 + 0xe);
            bVar5 = bVar31 & 1;
            bVar32 = bVar15;
            if (bVar5 == 0) {
              bVar32 = 1;
            }
            plVar4 = (long *)(uVar30 * 0x10 + 0x340 + lVar40);
            lVar40 = 0;
            do {
              lVar26 = (long)*(int *)((long)plVar4 + lVar40 * 4 + *plVar4 + 0x10) + (ulong)uVar19;
              if (((lVar21 == 0) ||
                  (uVar6 = *(ushort *)(local_b0 + 0x1a + lVar26 * 0x24),
                  (*(uint *)(lVar21 + (ulong)(uVar6 >> 5) * 4) >> (uVar6 & 0x1f) & 1) != 0)) &&
                 ((*(ushort *)(local_b0 + 0x1c + lVar26 * 0x24) & param_9) == param_10)) {
                lVar27 = lVar25;
                if (lVar25 == 0 || param_8 == 1) {
                  lVar27 = (long)*(short *)(local_b0 + 4 + lVar26 * 0x24);
                  if (lVar27 == -1) {
                    uVar38 = *(uint *)(local_b0 + lVar26 * 0x24);
                  }
                  else {
                    uVar38 = *(uint *)(*(long *)(param_3 + 8) + lVar27 * 4);
                  }
                  lVar27 = 0;
                  if (uVar38 != 0xffffffff) {
                    lVar34 = (ulong)(((uint)((int)uVar38 >> 0xd) >> 0x12 | 0x3ff) &
                                    (int)uVar38 >> 0xd) * 0x40;
                    lVar27 = *DAT_01a238a0;
                    lVar29 = *(long *)(lVar27 + 0x10 + lVar34);
                    uVar28 = (ulong)((uVar38 & 0x1fff) * *(int *)(lVar27 + 0x30 + lVar34));
                    lVar27 = (lVar29 + uVar28) -
                             ((long)*(int *)(lVar27 + 0x34 + lVar34) &
                             *(ulong *)(lVar29 + 8 + uVar28));
                  }
                }
                iVar37 = (int)param_1[0xe];
                cVar16 = '\0';
                if (((iVar37 == 7) || (iVar37 == 9)) &&
                   ((*(char *)(lVar8 + 0x38) != '\0' || (lVar25 != 0)))) {
                  local_48 = *param_4;
                  uStack_40 = param_4[1];
                  cVar16 = FUN_00890160(0,0,lVar27,&local_48,*(undefined4 *)(param_2 + 8),
                                        param_1[6] + 0x2800,iVar37,*param_1);
                }
                if (((lVar27 != 0 & (bVar5 == 0 | bVar15)) == 1) &&
                   (cVar17 = FUN_0082b850(lVar9,lVar27), cVar17 != '\0')) {
                  if ((int)param_1[0xe] == 0) {
                    if ((byte)param_3[0xc] == 0) {
                      lVar29 = *param_1;
                      bVar18 = *(byte *)(lVar29 + 0x15d1) & 0x7f;
                      if ((*(byte *)(lVar29 + 0x15d1) & 0x80) == 0) {
                        bVar18 = 2;
                      }
                      iVar37 = 0;
                      uVar39 = 0;
                    }
                    else {
                      iVar37 = 4 - (uint)(byte)param_3[0xc];
                      lVar29 = *param_1;
                      uVar39 = 3;
                      bVar18 = 0xc;
                    }
                    FUN_007e0f70(*(undefined8 *)(lVar29 + 0x15c0),bVar18);
                    FUN_007e10e0(*(undefined8 *)(*param_1 + 0x15c0),iVar37,uVar39);
                    if (param_8 == 1) {
                      FUN_007e0f70(*(undefined8 *)(*param_1 + 0x15c0),2);
                      FUN_007de4a0(*(undefined8 *)(*param_1 + 0x15c0),1);
                    }
                  }
                  uVar39 = FUN_0082e420((int)*(char *)((long)plVar1 + uVar30 + lVar23 + 0x90));
                  FUN_007deb70(uVar10,uVar39,0);
                  FUN_007dee30(uVar10,*(undefined4 *)((long)plVar1 + lVar23 + 0x50));
                  if (bVar5 == 0) {
                    uVar38 = *(uint *)((long)plVar1 + lVar23 + 0x44);
                    uVar33 = (int)uVar38 >> 0xd;
                    lVar29 = *DAT_01a238a0;
                    lVar36 = (ulong)((uVar33 >> 0x12 | 0x3ff) & uVar33) * 0x40;
                    lVar34 = *(long *)(lVar29 + 0x10 + lVar36);
                    uVar28 = (ulong)((uVar38 & 0x1fff) * *(int *)(lVar29 + 0x30 + lVar36));
                    FUN_007dec20(uVar10,(&DAT_0270a0d0)[iVar7],0,
                                 param_3[(ulong)*param_3 * 4 + lVar40 + 0x14],
                                 *(undefined4 *)
                                  (((lVar34 + uVar28) -
                                   ((long)*(int *)(lVar29 + 0x34 + lVar36) &
                                   *(ulong *)(lVar34 + 8 + uVar28))) + 0x30));
                    iVar37 = *(int *)((long)plVar1 + lVar23 + 0x44);
                    if (iVar37 != -1) {
                      FUN_007dec20(uVar10,iVar37,1,0,0);
                    }
                    iVar37 = *(int *)((long)plVar1 + lVar23 + 0x48);
                    if (iVar37 != -1) {
                      FUN_007dec20(uVar10,iVar37,2,0,0);
                    }
                    iVar37 = *(int *)((long)plVar1 + lVar23 + 0x4c);
joined_r0x007feef3:
                    if (iVar37 != -1) {
                      FUN_007dec20(uVar10,iVar37,3,0,0);
                    }
                  }
                  else if (bVar15 != 0) {
                    iVar37 = *(int *)((long)plVar1 + lVar23 + 0x40);
                    if (iVar37 != -1) {
                      FUN_007dec20(uVar10,iVar37,0,0,0);
                    }
                    iVar37 = *(int *)((long)plVar1 + lVar23 + 0x44);
                    if (iVar37 != -1) {
                      FUN_007dec20(uVar10,iVar37,1,0,0);
                    }
                    iVar37 = *(int *)((long)plVar1 + lVar23 + 0x48);
                    if (iVar37 != -1) {
                      FUN_007dec20(uVar10,iVar37,2,0,0);
                    }
                    iVar37 = *(int *)((long)plVar1 + lVar23 + 0x4c);
                    goto joined_r0x007feef3;
                  }
                  uVar39 = 3;
                  bVar18 = bVar32;
                  if ((*(byte *)(lVar27 + 8) & 0xfe) == 4) {
                    if (*(char *)(param_1[8] + 0x191f4) == '\0') {
                      bVar18 = 0;
                    }
                    uVar39 = 0x12;
                  }
                  if ((bVar18 & 1) != 0) {
                    FUN_007da370(uVar10,uVar39,0,*(undefined4 *)(local_b0 + 8 + lVar26 * 0x24),
                                 *(undefined4 *)(local_b0 + 0xc + lVar26 * 0x24),0);
                  }
                }
                if (cVar16 != '\0') {
                  *(byte *)(lVar9 + 0x15ad) = *(byte *)(lVar9 + 0x15ad) & 0x7f;
                }
              }
              lVar40 = lVar40 + 1;
            } while (lVar40 < *plVar3);
          }
          if (((bVar31 & 1) != 0) && (bVar15 == 1)) {
            *(byte *)(lVar9 + 0x15ac) = *(byte *)(lVar9 + 0x15ac) & 0x7f;
          }
        }
      }
      *(undefined4 *)(*param_1 + 0x15d4) = 0;
    }
    if (*local_120 != '\0' && !bVar41) {
      FUN_0082ba20(lVar9,0x1f,0x10);
      FUN_0082ba20(lVar9,0x1b,0x70);
      FUN_0082ba20(lVar9,0x19,0x18);
    }
    *(byte *)(lVar9 + 0x15ac) = *(byte *)(lVar9 + 0x15ac) & 0xfb;
    FUN_0082ba20(lVar9,8,0x80);
    uVar19 = 1;
  }
  if (*DAT_01a1f100 == local_38) {
    return (ulong)uVar19;
  }
  uVar30 = thunk_FUN_012aa7f6();
  return uVar30;
}

