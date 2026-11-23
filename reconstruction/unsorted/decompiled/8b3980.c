
void FUN_008b3980(uint *param_1,long *param_2,long param_3)

{
  int iVar1;
  undefined4 uVar2;
  long lVar3;
  undefined8 uVar4;
  undefined1 auVar5 [16];
  char cVar6;
  byte bVar7;
  uint uVar8;
  uint uVar9;
  long lVar10;
  undefined8 uVar11;
  undefined8 *puVar12;
  ulong uVar13;
  ulong uVar14;
  uint *puVar15;
  long lVar16;
  long lVar17;
  long lVar18;
  uint uVar19;
  uint uVar20;
  long lVar21;
  bool bVar22;
  long lVar23;
  long lVar24;
  char *pcVar25;
  undefined4 *puVar26;
  uint *puVar27;
  long lVar28;
  int iVar29;
  byte *pbVar30;
  undefined8 local_1e8;
  undefined8 uStack_1e0;
  long local_1d0;
  uint local_1a8;
  long local_190;
  char local_188 [16];
  undefined1 local_178 [144];
  undefined1 local_e8 [144];
  undefined8 local_58;
  undefined8 uStack_50;
  undefined8 local_48;
  undefined8 uStack_40;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  uVar8 = (int)*param_1 >> 0xd;
  lVar23 = (ulong)((uVar8 >> 0x12 | 0x3ff) & uVar8) * 0x40;
  lVar3 = param_2[7];
  iVar1 = (int)param_2[0xe];
  puVar27 = *(uint **)(param_3 + 0x10);
  lVar24 = *DAT_01a238a0;
  uVar13 = (ulong)((*param_1 & 0x1fff) * *(int *)(lVar24 + 0x30 + lVar23));
  lVar10 = *(long *)(lVar24 + 0x10 + lVar23);
  if (param_1[2] == 0xffffffff) {
    puVar15 = (uint *)0x0;
  }
  else {
    puVar15 = param_1 + 4;
  }
  uVar8 = *(uint *)(lVar3 + 0x440) & 1;
  lVar24 = (lVar10 + uVar13) -
           ((long)*(int *)(lVar24 + 0x34 + lVar23) & *(ulong *)(lVar10 + 8 + uVar13));
  if ((iVar1 != 0xc) && (iVar1 != 3)) {
    if (iVar1 == 0) {
      uVar20 = param_1[1];
      lVar3 = param_2[8];
      lVar10 = *param_2;
      if (uVar8 != 0) {
        *(undefined1 *)(lVar10 + 0x15d6) = 0x84;
      }
      lVar23 = FUN_0082cb90(0x11);
      *(byte *)(lVar10 + 0x15ae) = *(byte *)(lVar10 + 0x15ae) | 2;
      uVar4 = *(undefined8 *)(lVar10 + 0x15c0);
      uVar11 = FUN_0082e420(0x3d);
      FUN_007deb70(uVar4,uVar11,0);
      uVar13 = *(ulong *)(lVar24 + 0x58);
      if (*(long *)(lVar24 + 0x60) == 0) {
        local_1d0 = 0;
      }
      else {
        local_1d0 = *(long *)(lVar24 + 0x60) + lVar24 + 0x70;
      }
      if (*(char *)((long)puVar27 + 0x41) == '\0') {
        FUN_01075dd0(local_e8,*(long *)(lVar10 + 0x1018) + 0x120,*(long *)(lVar10 + 0x1018) + 0x20);
        if (puVar15 == (uint *)0x0) {
          if (0 < (int)uVar13) {
            pcVar25 = local_188;
            lVar16 = local_1d0;
            do {
              cVar6 = FUN_00832a00(local_e8,lVar16);
              *pcVar25 = cVar6;
              lVar16 = lVar16 + 0x60;
              pcVar25 = pcVar25 + 1;
              uVar19 = (int)uVar13 - 1;
              uVar13 = (ulong)uVar19;
            } while (uVar19 != 0);
          }
        }
        else {
          uVar19 = (int)*puVar15 >> 0xd;
          lVar16 = *DAT_01a238a0;
          lVar17 = (ulong)((uVar19 >> 0x12 | 0x3ff) & uVar19) * 0x40;
          uVar14 = (ulong)((*puVar15 & 0x1fff) * *(int *)(lVar16 + 0x30 + lVar17));
          if (0 < (int)uVar13) {
            lVar21 = *(long *)(param_2[7] + 0x7c8);
            lVar18 = *(long *)(lVar16 + 0x10 + lVar17);
            pbVar30 = (byte *)(((lVar18 + uVar14) -
                               ((long)*(int *)(lVar16 + 0x34 + lVar17) &
                               *(ulong *)(lVar18 + 8 + uVar14))) + 2);
            pcVar25 = local_188;
            lVar16 = local_1d0;
            do {
              cVar6 = '\0';
              if ((*pbVar30 & ~*(byte *)(lVar21 + (ulong)*(ushort *)(pbVar30 + -2))) == 0) {
                cVar6 = FUN_00832a00(local_e8,lVar16);
              }
              *pcVar25 = cVar6;
              pbVar30 = pbVar30 + 4;
              pcVar25 = pcVar25 + 1;
              lVar16 = lVar16 + 0x60;
              uVar19 = (int)uVar13 - 1;
              uVar13 = (ulong)uVar19;
            } while (uVar19 != 0);
          }
        }
      }
      uVar19 = (int)uVar20 >> 0xd;
      if ((char)puVar27[0x10] != '\0') {
        lVar16 = *param_2;
        FUN_007dec20(*(undefined8 *)(lVar16 + 0x15c0),*(undefined4 *)(lVar24 + 0x90),0,0,0);
        FUN_007dec20(*(undefined8 *)(lVar16 + 0x15c0),*(undefined4 *)(lVar24 + 0x94),1,0,0);
        FUN_007dee30(*(undefined8 *)(lVar16 + 0x15c0),*(undefined4 *)(lVar24 + 0x98));
        lVar18 = (ulong)((uVar19 >> 0x12 | 0x3ff) & uVar19) * 0x40;
        lVar17 = *DAT_01a238a0;
        lVar21 = *(long *)(lVar17 + 0x10 + lVar18);
        uVar13 = (ulong)((uVar20 & 0x1fff) * *(int *)(lVar17 + 0x30 + lVar18));
        lVar28 = (lVar21 + uVar13) -
                 ((long)*(int *)(lVar17 + 0x34 + lVar18) & *(ulong *)(lVar21 + 8 + uVar13));
        uVar9 = (int)*(uint *)(lVar24 + 0x90) >> 0xd;
        lVar18 = (ulong)((uVar9 >> 0x12 | 0x3ff) & uVar9) * 0x40;
        lVar21 = *(long *)(lVar17 + 0x10 + lVar18);
        uVar13 = (ulong)((*(uint *)(lVar24 + 0x90) & 0x1fff) * *(int *)(lVar17 + 0x30 + lVar18));
        FUN_007dec20(*(undefined8 *)(lVar16 + 0x15c0),*(undefined4 *)(lVar28 + 8),2,
                     *(int *)(lVar24 + 0xac) + *(int *)(lVar28 + 0xc),
                     *(undefined4 *)
                      (((lVar21 + uVar13) -
                       ((long)*(int *)(lVar17 + 0x34 + lVar18) & *(ulong *)(lVar21 + 8 + uVar13))) +
                      0x30));
        lVar17 = 0;
        uVar9 = *(uint *)(lVar24 + 0xa4);
        if (uVar9 != 0xffffffff) {
          lVar18 = (ulong)(((uint)((int)uVar9 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar9 >> 0xd) * 0x40;
          lVar17 = *DAT_01a238a0;
          lVar21 = *(long *)(lVar17 + 0x10 + lVar18);
          uVar13 = (ulong)((uVar9 & 0x1fff) * *(int *)(lVar17 + 0x30 + lVar18));
          lVar17 = (lVar21 + uVar13) -
                   ((long)*(int *)(lVar17 + 0x34 + lVar18) & *(ulong *)(lVar21 + 8 + uVar13));
        }
        uVar2 = *(undefined4 *)(lVar24 + 0xa8);
        uVar4 = *(undefined8 *)(lVar24 + 0x30);
        uVar11 = *(undefined8 *)(lVar24 + 0x38);
        puVar12 = (undefined8 *)
                  FUN_007df630(*(undefined8 *)(lVar16 + 0x15c0),2,*(undefined4 *)(lVar23 + 0x120),
                               0x20);
        *puVar12 = uVar4;
        puVar12[1] = uVar11;
        *(undefined1 (*) [16])(puVar12 + 2) = ZEXT816(0) << 0x20;
        FUN_007df250(*(undefined8 *)(lVar16 + 0x15c0),0xd,uVar2);
        if ((lVar17 != 0) && (cVar6 = FUN_0082b850(lVar16,lVar17), cVar6 != '\0')) {
          if (*(char *)((long)puVar27 + 0x41) == '\0') {
            uVar13 = *(ulong *)(lVar24 + 0x58);
            if (0 < (int)uVar13) {
              puVar26 = (undefined4 *)(local_1d0 + 0x4c);
              pcVar25 = local_188;
              puVar15 = puVar27;
              do {
                if ((*puVar15 == 5) && (*pcVar25 != '\0')) {
                  FUN_007da370(*(undefined8 *)(lVar16 + 0x15c0),5,0,puVar26[-1],*puVar26,0);
                }
                puVar15 = puVar15 + 1;
                pcVar25 = pcVar25 + 1;
                puVar26 = puVar26 + 0x18;
                uVar9 = (int)uVar13 - 1;
                uVar13 = (ulong)uVar9;
              } while (uVar9 != 0);
            }
          }
          else {
            FUN_007da370(*(undefined8 *)(lVar16 + 0x15c0),5,0,*(undefined4 *)(lVar24 + 0x9c),
                         *(undefined4 *)(lVar24 + 0xa0),0);
          }
        }
      }
      if (*(char *)((long)puVar27 + 0x41) == '\0') {
        if ((char)puVar27[0x10] == '\0') {
          FUN_007dec20(*(undefined8 *)(lVar10 + 0x15c0),*(undefined4 *)(lVar24 + 0x68),0,0,0);
          FUN_007dec20(*(undefined8 *)(lVar10 + 0x15c0),*(undefined4 *)(lVar24 + 0x6c),1,0,0);
          FUN_007dee30(*(undefined8 *)(lVar10 + 0x15c0),*(undefined4 *)(lVar24 + 0x70));
          lVar21 = (ulong)((uVar19 >> 0x12 | 0x3ff) & uVar19) * 0x40;
          lVar16 = *DAT_01a238a0;
          lVar17 = *(long *)(lVar16 + 0x10 + lVar21);
          uVar13 = (ulong)((uVar20 & 0x1fff) * *(int *)(lVar16 + 0x30 + lVar21));
          lVar21 = (lVar17 + uVar13) -
                   ((long)*(int *)(lVar16 + 0x34 + lVar21) & *(ulong *)(lVar17 + 8 + uVar13));
          uVar20 = (int)*(uint *)(lVar24 + 0x68) >> 0xd;
          lVar18 = (ulong)((uVar20 >> 0x12 | 0x3ff) & uVar20) * 0x40;
          lVar17 = *(long *)(lVar16 + 0x10 + lVar18);
          uVar13 = (ulong)((*(uint *)(lVar24 + 0x68) & 0x1fff) * *(int *)(lVar16 + 0x30 + lVar18));
          FUN_007dec20(*(undefined8 *)(lVar10 + 0x15c0),*(undefined4 *)(lVar21 + 8),2,
                       *(undefined4 *)(lVar21 + 0xc),
                       *(undefined4 *)
                        (((lVar17 + uVar13) -
                         ((long)*(int *)(lVar16 + 0x34 + lVar18) & *(ulong *)(lVar17 + 8 + uVar13)))
                        + 0x30));
        }
        uVar13 = *(ulong *)(lVar24 + 0x80);
        lVar16 = 0;
        if (*(long *)(lVar24 + 0x88) != 0) {
          lVar16 = *(long *)(lVar24 + 0x88) + lVar24 + 0x98;
        }
        if (0 < (int)uVar13) {
          auVar5 = vshufps_avx(*(undefined1 (*) [16])(lVar3 + 0x1fbe0),ZEXT816(0) << 0x40,4);
          pcVar25 = (char *)(lVar16 + 0xb);
          bVar22 = false;
          local_190._0_4_ = 0xffffffff;
          local_1a8 = 0xffffffff;
          do {
            uVar14 = (ulong)(byte)pcVar25[-1];
            if ((local_188[uVar14] != '\0') && ((char)puVar27[uVar14] == *pcVar25)) {
              if (local_1a8 != (byte)pcVar25[-1]) {
                local_58 = *(undefined8 *)(lVar24 + 0x30);
                uStack_50 = *(undefined8 *)(lVar24 + 0x38);
                puVar12 = (undefined8 *)(local_1d0 + 0x20 + uVar14 * 0x60);
                local_48 = *puVar12;
                uStack_40 = puVar12[1];
                puVar12 = (undefined8 *)
                          FUN_007df630(*(undefined8 *)(lVar10 + 0x15c0),2,
                                       *(undefined4 *)(lVar23 + 0x120),0x30);
                puVar12[3] = uStack_40;
                puVar12[2] = local_48;
                puVar12[1] = uStack_50;
                *puVar12 = local_58;
                local_1e8 = auVar5._0_8_;
                uStack_1e0 = auVar5._8_8_;
                puVar12[4] = local_1e8;
                puVar12[5] = uStack_1e0;
                if (*(int *)(local_1d0 + 0x58 + uVar14 * 0x60) == -1) {
                  FUN_007df310(*(undefined8 *)(lVar10 + 0x15c0),0xe,0);
                }
                else {
                  FUN_007df250(*(undefined8 *)(lVar10 + 0x15c0),0xe);
                }
                local_1a8 = (uint)(byte)pcVar25[-1];
              }
              uVar20 = *(uint *)(pcVar25 + -0xb);
              if (uVar20 != (uint)local_190) {
                if (uVar20 == 0xffffffff) {
LAB_008b4587:
                  bVar22 = false;
                }
                else {
                  lVar17 = (ulong)(((uint)((int)uVar20 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar20 >> 0xd
                                  ) * 0x40;
                  lVar3 = *DAT_01a238a0;
                  lVar16 = *(long *)(lVar3 + 0x10 + lVar17);
                  uVar14 = (ulong)((uVar20 & 0x1fff) * *(int *)(lVar3 + 0x30 + lVar17));
                  if (lVar16 + uVar14 ==
                      ((long)*(int *)(lVar3 + 0x34 + lVar17) & *(ulong *)(lVar16 + 8 + uVar14)))
                  goto LAB_008b4587;
                  cVar6 = FUN_0082b850(lVar10);
                  bVar22 = true;
                  if (cVar6 == '\0') goto LAB_008b4587;
                }
                local_190._0_4_ = *(uint *)(pcVar25 + -0xb);
              }
              if (bVar22) {
                FUN_007da370(*(undefined8 *)(lVar10 + 0x15c0),5,0,*(undefined4 *)(pcVar25 + -7),
                             *(undefined2 *)(pcVar25 + -3),0);
              }
            }
            pcVar25 = pcVar25 + 0xc;
            uVar20 = (int)uVar13 - 1;
            uVar13 = (ulong)uVar20;
          } while (uVar20 != 0);
        }
      }
      *(byte *)(lVar10 + 0x15ae) = *(byte *)(lVar10 + 0x15ae) & 0xfd;
      if (uVar8 != 0) {
        *(undefined1 *)(lVar10 + 0x15d6) = 0;
      }
    }
    goto LAB_008b45e6;
  }
  local_190 = 0;
  if (((*(int *)(lVar3 + 0x4e0) == 6) && ((ulong)*(uint *)(lVar3 + 0x450) != 0xffffffff)) &&
     (DAT_018deebc != '\0')) {
    local_190 = *(long *)(param_2[8] + 0x18930) + 0xc0 + (ulong)*(uint *)(lVar3 + 0x450) * 0x1c0;
  }
  lVar3 = *param_2;
  if (uVar8 != 0) {
    *(undefined1 *)(lVar3 + 0x15d6) = 0x84;
  }
  lVar10 = FUN_0082cb90(0x11);
  *(byte *)(lVar3 + 0x15ae) = *(byte *)(lVar3 + 0x15ae) | 2;
  uVar4 = *(undefined8 *)(lVar3 + 0x15c0);
  uVar11 = FUN_0082e420(0x3e);
  FUN_007deb70(uVar4,uVar11,0);
  uVar4 = *(undefined8 *)(lVar24 + 0x30);
  uVar11 = *(undefined8 *)(lVar24 + 0x38);
  puVar12 = (undefined8 *)
            FUN_007df630(*(undefined8 *)(lVar3 + 0x15c0),2,*(undefined4 *)(lVar10 + 0x120),0x20);
  lVar10 = 0;
  *puVar12 = uVar4;
  puVar12[1] = uVar11;
  puVar12[2] = 0;
  puVar12[3] = 0;
  uVar20 = *(uint *)(lVar24 + 0x74);
  if (uVar20 != 0xffffffff) {
    lVar16 = (ulong)(((uint)((int)uVar20 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar20 >> 0xd) * 0x40;
    lVar10 = *DAT_01a238a0;
    lVar23 = *(long *)(lVar10 + 0x10 + lVar16);
    uVar13 = (ulong)((uVar20 & 0x1fff) * *(int *)(lVar10 + 0x30 + lVar16));
    lVar10 = (lVar23 + uVar13) -
             ((long)*(int *)(lVar10 + 0x34 + lVar16) & *(ulong *)(lVar23 + 8 + uVar13));
  }
  if (iVar1 == 3) {
LAB_008b3c8c:
    if ((lVar10 != 0) && (cVar6 = FUN_0082b730(lVar3), cVar6 != '\0')) {
      if ((char)puVar27[0x10] == '\0') {
        FUN_007dec20(*(undefined8 *)(lVar3 + 0x15c0),*(undefined4 *)(lVar24 + 0x68),0,0,0);
        FUN_007dee30(*(undefined8 *)(lVar3 + 0x15c0),*(undefined4 *)(lVar24 + 0x70));
        FUN_01075dd0(local_178,*(long *)(lVar3 + 0x1018) + 0x120,*(long *)(lVar3 + 0x1018) + 0x20);
        lVar10 = 0;
        uVar13 = *(ulong *)(lVar24 + 0x58);
        if (*(long *)(lVar24 + 0x60) != 0) {
          lVar10 = *(long *)(lVar24 + 0x60) + lVar24 + 0x70;
        }
        iVar29 = (int)uVar13;
        if (puVar15 == (uint *)0x0) {
          if (0 < iVar29) {
            if (local_190 == 0) {
              pcVar25 = local_188;
              uVar14 = uVar13 & 0xffffffff;
              lVar24 = lVar10;
              do {
                cVar6 = FUN_00832a00(local_178,lVar24);
                *pcVar25 = cVar6;
                lVar24 = lVar24 + 0x60;
                pcVar25 = pcVar25 + 1;
                uVar20 = (int)uVar14 - 1;
                uVar14 = (ulong)uVar20;
              } while (uVar20 != 0);
            }
            else {
              pcVar25 = local_188;
              uVar14 = uVar13 & 0xffffffff;
              lVar24 = lVar10;
              do {
                cVar6 = FUN_00832c10(local_190,lVar24);
                *pcVar25 = cVar6;
                lVar24 = lVar24 + 0x60;
                pcVar25 = pcVar25 + 1;
                uVar20 = (int)uVar14 - 1;
                uVar14 = (ulong)uVar20;
              } while (uVar20 != 0);
            }
            goto LAB_008b46a5;
          }
        }
        else {
          uVar20 = (int)*puVar15 >> 0xd;
          lVar24 = *DAT_01a238a0;
          lVar23 = (ulong)((uVar20 >> 0x12 | 0x3ff) & uVar20) * 0x40;
          uVar14 = (ulong)((*puVar15 & 0x1fff) * *(int *)(lVar24 + 0x30 + lVar23));
          if (0 < iVar29) {
            lVar16 = *(long *)(param_2[7] + 0x7c8);
            lVar17 = *(long *)(lVar24 + 0x10 + lVar23);
            lVar24 = (lVar17 + uVar14) -
                     ((long)*(int *)(lVar24 + 0x34 + lVar23) & *(ulong *)(lVar17 + 8 + uVar14));
            if (local_190 == 0) {
              pbVar30 = (byte *)(lVar24 + 2);
              pcVar25 = local_188;
              uVar14 = uVar13 & 0xffffffff;
              lVar24 = lVar10;
              do {
                bVar7 = ~*(byte *)(lVar16 + (ulong)*(ushort *)(pbVar30 + -2)) & *pbVar30;
                *pcVar25 = bVar7 == 0;
                if (bVar7 == 0) {
                  cVar6 = FUN_00832a00(local_178,lVar24);
                  *pcVar25 = cVar6;
                }
                pbVar30 = pbVar30 + 4;
                pcVar25 = pcVar25 + 1;
                lVar24 = lVar24 + 0x60;
                uVar20 = (int)uVar14 - 1;
                uVar14 = (ulong)uVar20;
              } while (uVar20 != 0);
            }
            else {
              pbVar30 = (byte *)(lVar24 + 2);
              pcVar25 = local_188;
              uVar14 = uVar13 & 0xffffffff;
              lVar24 = lVar10;
              do {
                bVar7 = ~*(byte *)(lVar16 + (ulong)*(ushort *)(pbVar30 + -2)) & *pbVar30;
                *pcVar25 = bVar7 == 0;
                if (bVar7 == 0) {
                  cVar6 = FUN_00832c10(local_190,lVar24);
                  *pcVar25 = cVar6;
                }
                pbVar30 = pbVar30 + 4;
                pcVar25 = pcVar25 + 1;
                lVar24 = lVar24 + 0x60;
                uVar20 = (int)uVar14 - 1;
                uVar14 = (ulong)uVar20;
              } while (uVar20 != 0);
            }
LAB_008b46a5:
            if (0 < iVar29) {
              lVar10 = lVar10 + 0x34;
              pcVar25 = local_188;
              if (iVar1 == 0xc) {
                do {
                  uVar20 = *puVar27;
                  if (((int)uVar20 <= DAT_018defe0) && (*pcVar25 != '\0')) {
                    FUN_007da370(*(undefined8 *)(lVar3 + 0x15c0),5,0,
                                 *(undefined4 *)(lVar10 + -4 + (ulong)uVar20 * 8),
                                 *(undefined4 *)(lVar10 + (ulong)uVar20 * 8),0);
                  }
                  puVar27 = puVar27 + 1;
                  pcVar25 = pcVar25 + 1;
                  lVar10 = lVar10 + 0x60;
                  uVar20 = (int)uVar13 - 1;
                  uVar13 = (ulong)uVar20;
                } while (uVar20 != 0);
              }
              else {
                do {
                  if (*pcVar25 != '\0') {
                    FUN_007da370(*(undefined8 *)(lVar3 + 0x15c0),5,0,
                                 *(undefined4 *)(lVar10 + -4 + (ulong)*puVar27 * 8),
                                 *(undefined4 *)(lVar10 + (ulong)*puVar27 * 8),0);
                  }
                  pcVar25 = pcVar25 + 1;
                  puVar27 = puVar27 + 1;
                  lVar10 = lVar10 + 0x60;
                  uVar20 = (int)uVar13 - 1;
                  uVar13 = (ulong)uVar20;
                } while (uVar20 != 0);
              }
            }
          }
        }
      }
      else if ((iVar1 != 0xc) || (2 < DAT_018defe0)) {
        FUN_007dec20(*(undefined8 *)(lVar3 + 0x15c0),*(undefined4 *)(lVar24 + 0x90),0,0,0);
        FUN_007dee30(*(undefined8 *)(lVar3 + 0x15c0),*(undefined4 *)(lVar24 + 0x98));
        FUN_007da370(*(undefined8 *)(lVar3 + 0x15c0),5,0,*(undefined4 *)(lVar24 + 0x9c),
                     *(undefined4 *)(lVar24 + 0xa0),0);
      }
    }
  }
  else {
    uVar20 = *(uint *)(lVar24 + 0x78);
    if (uVar20 != 0xffffffff) {
      lVar16 = (ulong)(((uint)((int)uVar20 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar20 >> 0xd) * 0x40;
      lVar10 = *DAT_01a238a0;
      lVar23 = *(long *)(lVar10 + 0x10 + lVar16);
      uVar13 = (ulong)((uVar20 & 0x1fff) * *(int *)(lVar10 + 0x30 + lVar16));
      lVar10 = (lVar23 + uVar13) -
               ((long)*(int *)(lVar10 + 0x34 + lVar16) & *(ulong *)(lVar23 + 8 + uVar13));
      goto LAB_008b3c8c;
    }
  }
  *(byte *)(lVar3 + 0x15ae) = *(byte *)(lVar3 + 0x15ae) & 0xfd;
  if (uVar8 != 0) {
    *(undefined1 *)(lVar3 + 0x15d6) = 0;
  }
LAB_008b45e6:
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

