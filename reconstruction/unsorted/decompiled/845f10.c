
undefined8
FUN_00845f10(long param_1,long param_2,undefined8 param_3,undefined8 param_4,uint param_5,
            undefined8 param_6,undefined8 param_7,long param_8,uint param_9,char param_10)

{
  long *plVar1;
  undefined8 *puVar2;
  undefined8 *puVar3;
  byte bVar4;
  ushort uVar5;
  ushort uVar6;
  ushort uVar7;
  ushort uVar8;
  undefined4 uVar9;
  undefined4 uVar10;
  int iVar11;
  int iVar12;
  long lVar13;
  int iVar14;
  undefined8 uVar15;
  undefined8 uVar16;
  undefined8 uVar17;
  undefined8 uVar18;
  undefined8 uVar19;
  undefined8 uVar20;
  bool bVar21;
  char *pcVar22;
  byte bVar23;
  uint uVar24;
  ulong uVar25;
  undefined8 *puVar26;
  long lVar27;
  long lVar28;
  undefined8 uVar29;
  int iVar30;
  uint uVar31;
  long lVar32;
  ulong uVar33;
  long lVar34;
  byte bVar35;
  uint uVar36;
  uint uVar37;
  long lVar38;
  char *pcVar39;
  byte bVar40;
  long *plVar41;
  byte bVar42;
  uint uVar43;
  ushort *puVar44;
  long lVar45;
  bool bVar46;
  char *local_900;
  long local_8c0;
  uint local_898;
  uint local_894;
  uint local_874;
  uint *local_870;
  undefined4 local_868;
  undefined4 local_83c;
  byte local_838 [2048];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  iVar30 = -1;
  pcVar22 = (char *)(param_1 + 0x30);
  do {
    pcVar39 = pcVar22;
    iVar30 = iVar30 + 1;
    if (4 < iVar30) goto LAB_0084677e;
    pcVar22 = pcVar39 + 0x18;
  } while (*pcVar39 != (char)param_5);
  bVar46 = false;
  local_8c0 = 0;
  if ((param_5 == 0) && (*(long *)(param_1 + 0xa8) != 0)) {
    uVar25 = (ulong)((param_9 & 0x1fff) * DAT_02709940);
    bVar46 = *(int *)(DAT_02709938 + 8 + uVar25) != -1;
    local_8c0 = 0;
    if (bVar46) {
      local_8c0 = DAT_02709938 + uVar25;
    }
  }
  lVar13 = *(long *)(param_2 + 0x15c0);
  uVar9 = *(undefined4 *)(lVar13 + 0x25b8);
  uVar10 = *(undefined4 *)(&DAT_000025e8 + lVar13);
  puVar26 = (undefined8 *)FUN_0082b940(param_2,0x2e,0x40);
  local_83c = 0;
  FUN_0082b900(param_2,&local_83c);
  uVar36 = (int)*(uint *)(param_1 + 0x24) >> 0xd;
  lVar27 = (ulong)((uVar36 >> 0x12 | 0x3ff) & uVar36) * 0x40;
  bVar35 = *(byte *)(param_2 + 0x15d1);
  lVar45 = *DAT_01a238a0;
  lVar34 = *(long *)(lVar45 + 0x10 + lVar27);
  iVar30 = *(int *)(lVar45 + 0x34 + lVar27);
  uVar33 = (ulong)((*(uint *)(param_1 + 0x24) & 0x1fff) * *(int *)(lVar45 + 0x30 + lVar27));
  uVar25 = *(ulong *)(lVar34 + 8 + uVar33);
  thunk_FUN_012aa7c6(local_838,param_4,(long)*(int *)(param_1 + 8));
  bVar40 = 2;
  if ((bVar35 & 0x80) != 0) {
    bVar40 = bVar35 & 0x7f;
  }
  lVar45 = (lVar34 + uVar33) - ((long)iVar30 & uVar25);
  uVar36 = 0x9f;
  if (param_5 == 0xc) {
    uVar36 = 0xdf;
  }
  if ((0xc < param_5) || ((0x1041U >> (param_5 & 0x1f) & 1) == 0)) {
    FUN_00844d00(param_1,param_6,param_7,0xffffff7f,local_838);
  }
  if ((param_10 != '\0') &&
     (((param_5 == 0 || (param_5 == 0xc)) && (*(long *)(param_8 + 0x1fba8) != 0)))) {
    FUN_00844e40(param_1,param_6,*(long *)(param_8 + 0x1fba8),uVar36,local_838);
  }
  iVar30 = *(int *)(pcVar39 + 8);
  local_900 = (char *)0x0;
  if (*(long *)(pcVar39 + 0x10) != 0) {
    local_900 = pcVar39 + *(long *)(pcVar39 + 0x10) + 0x20;
  }
  if (0 < iVar30) {
    lVar34 = 0;
    do {
      uVar37 = (int)*(uint *)(local_900 + lVar34 * 4) >> 0xd;
      lVar32 = (ulong)((uVar37 >> 0x12 | 0x3ff) & uVar37) * 0x40;
      lVar27 = *DAT_01a238a0;
      lVar28 = *(long *)(lVar27 + 0x10 + lVar32);
      uVar25 = (ulong)((*(uint *)(local_900 + lVar34 * 4) & 0x1fff) *
                      *(int *)(lVar27 + 0x30 + lVar32));
      lVar27 = (lVar28 + uVar25) -
               ((long)*(int *)(lVar27 + 0x34 + lVar32) & *(ulong *)(lVar28 + 8 + uVar25));
      iVar11 = *(int *)(lVar27 + 0x28);
      puVar44 = (ushort *)0x0;
      if (*(long *)(lVar27 + 0x30) != 0) {
        puVar44 = (ushort *)(lVar27 + 0x40 + *(long *)(lVar27 + 0x30));
      }
      if (0 < iVar11) {
        uVar43 = 0;
        bVar21 = true;
        local_868 = 3;
        bVar23 = 0;
        plVar1 = (long *)(lVar27 + 0x10);
        plVar41 = (long *)(lVar27 + 0x20);
        local_870 = (uint *)0x0;
        bVar35 = 0x10;
        local_898 = 0xffffffff;
        local_894 = 0xffffffff;
        local_874 = 0xffffffff;
        uVar37 = uVar43;
        do {
          uVar5 = *puVar44;
          if ((local_838[(int)(puVar44[1] + uVar43)] & uVar36) < 0xc) {
            uVar6 = puVar44[4];
            uVar25 = (ulong)uVar6;
            bVar4 = (&DAT_01662980)
                    [(ulong)*(byte *)((long)plVar41 + uVar25 * 0x18 + *plVar41 + 0x1e) +
                     (ulong)(local_838[(int)(puVar44[1] + uVar43)] & uVar36) * 10 +
                     (ulong)(param_5 == 0) * 0xaa];
            if (bVar4 != 0) {
              uVar7 = puVar44[2];
              uVar31 = (uint)uVar7;
              if (uVar31 == local_898) {
                lVar27 = 0;
                uVar31 = local_898;
              }
              else {
                uVar24 = *(uint *)((long)plVar1 + (ulong)uVar7 * 8 + *plVar1 + 0x14);
                bVar23 = 0;
                if (uVar24 != 0xffffffff) {
                  lVar32 = (ulong)(((uint)((int)uVar24 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar24 >> 0xd
                                  ) * 0x40;
                  lVar27 = *DAT_01a238a0;
                  lVar28 = *(long *)(lVar27 + 0x10 + lVar32);
                  uVar33 = (ulong)((uVar24 & 0x1fff) * *(int *)(lVar27 + 0x30 + lVar32));
                  lVar27 = (lVar28 + uVar33) -
                           ((long)*(int *)(lVar27 + 0x34 + lVar32) & *(ulong *)(lVar28 + 8 + uVar33)
                           );
                  if (lVar27 != 0) {
                    uVar8 = puVar44[3];
                    if (uVar8 == local_894) {
                      bVar23 = FUN_0082b8a0(param_2,lVar27);
                    }
                    else {
                      uVar29 = FUN_0082e420((int)*(char *)((long)plVar1 +
                                                          (ulong)uVar7 * 8 + *plVar1 + 0x10));
                      FUN_007deb70(lVar13,uVar29,0);
                      bVar23 = FUN_0082b850(param_2,lVar27);
                      bVar35 = 0x10;
                      local_894 = (uint)uVar8;
                    }
                    goto LAB_00846417;
                  }
                }
                lVar27 = 0;
              }
LAB_00846417:
              uVar24 = (uint)uVar6;
              if (uVar24 != local_874) {
                lVar28 = *plVar41;
                FUN_007dee30(lVar13,*(undefined4 *)((long)plVar41 + uVar25 * 0x18 + lVar28 + 0x18));
                FUN_007dec20(lVar13,*(undefined4 *)((long)plVar41 + uVar25 * 0x18 + lVar28 + 0x10),0
                             ,0,0);
                local_870 = (uint *)((long)plVar41 + uVar25 * 0x18 + lVar28 + 0x10);
                iVar12 = *(int *)((long)plVar41 + uVar25 * 0x18 + lVar28 + 0x14);
                local_874 = uVar24;
                if (iVar12 != -1) {
                  FUN_007dec20(lVar13,iVar12,1,0,0);
                }
              }
              if (bVar4 != bVar35) {
                if (bVar4 == 0x10) {
                  bVar42 = 0;
                  uVar29 = 0xa8;
                  bVar35 = bVar40;
                }
                else {
                  bVar42 = bVar4 & 3;
                  bVar35 = 0xb - ((char)bVar4 >> 7);
                  uVar29 = 0xab;
                }
                FUN_007e0f70(lVar13,bVar35);
                FUN_007e10e0(lVar13,bVar42,uVar29);
              }
              bVar35 = bVar4;
              local_898 = uVar31;
              if ((bVar23 & 1) != 0) {
                lVar28 = (long)(int)(puVar44[5] + uVar43) * 0x40;
                uVar29 = *(undefined8 *)(lVar45 + lVar28);
                uVar15 = ((undefined8 *)(lVar45 + lVar28))[1];
                puVar2 = (undefined8 *)(lVar45 + 0x10 + lVar28);
                uVar18 = puVar2[1];
                puVar3 = (undefined8 *)(lVar45 + 0x20 + lVar28);
                uVar16 = *puVar3;
                uVar17 = puVar3[1];
                puVar3 = (undefined8 *)(lVar45 + 0x30 + lVar28);
                uVar19 = *puVar3;
                uVar20 = puVar3[1];
                puVar26[2] = *puVar2;
                puVar26[3] = uVar18;
                *puVar26 = uVar29;
                puVar26[1] = uVar15;
                puVar26[6] = uVar19;
                puVar26[7] = uVar20;
                puVar26[4] = uVar16;
                puVar26[5] = uVar17;
                lVar28 = FUN_0082cb90(9);
                if (lVar28 != 0) {
                  FUN_0081fe10(param_2,lVar28,*(undefined8 *)(param_2 + 0x15c0));
                }
                iVar12 = *(int *)(puVar44 + 8);
                if (iVar12 != -0x80000000) {
                  if (!bVar46) goto LAB_008466e0;
                  iVar14 = -iVar12;
                  if (0 < iVar12) {
                    iVar14 = iVar12;
                  }
                  uVar31 = (int)*local_870 >> 0xd;
                  lVar28 = *DAT_01a238a0;
                  lVar38 = (ulong)((uVar31 >> 0x12 | 0x3ff) & uVar31) * 0x40;
                  lVar32 = *(long *)(lVar28 + 0x10 + lVar38);
                  uVar25 = (ulong)((*local_870 & 0x1fff) * *(int *)(lVar28 + 0x30 + lVar38));
                  FUN_007dec20(lVar13,*(undefined4 *)(local_8c0 + 8),3,
                               *(int *)(puVar44 + 10) * uVar43 + iVar14 + *(int *)(local_8c0 + 0xc),
                               *(undefined4 *)
                                (((lVar32 + uVar25) -
                                 ((long)*(int *)(lVar28 + 0x34 + lVar38) &
                                 *(ulong *)(lVar32 + 8 + uVar25))) + 0x30));
                }
                if (lVar27 == 0) {
LAB_00846648:
                  if (!bVar21) goto LAB_008466e0;
                }
                else {
                  if ((*(byte *)(lVar27 + 8) & 0xfe) == 4) {
                    if (*(char *)(param_8 + 0x191f4) == '\0') {
                      bVar21 = false;
                    }
                    local_868 = 0x12;
                    goto LAB_00846648;
                  }
                  local_868 = 3;
                  bVar21 = true;
                }
                FUN_007e15d0(lVar13,local_868,0,local_870[4],local_870[5],puVar44[6],puVar44[7],0);
              }
            }
          }
LAB_008466e0:
          uVar31 = (int)((uVar43 + 1) - (uint)uVar5) >> 0x1f;
          uVar43 = uVar43 + 1 & uVar31;
          uVar31 = uVar31 & 1 ^ 1;
          puVar44 = puVar44 + (ulong)uVar31 * 0xc;
          uVar37 = uVar31 + uVar37;
        } while ((int)uVar37 < iVar11);
      }
      lVar34 = lVar34 + 1;
    } while ((int)lVar34 != iVar30);
  }
  if (param_5 == 0xc) {
    *(undefined1 *)(param_2 + 0x15d4) = 0;
  }
  FUN_007de460(lVar13,uVar9,uVar10);
  FUN_0082b930(param_2);
  FUN_0082ba20(param_2,0x2e,0x40);
LAB_0084677e:
  if (*DAT_01a1f100 != local_38) {
    uVar29 = thunk_FUN_012aa7f6();
    return uVar29;
  }
  return 0;
}

