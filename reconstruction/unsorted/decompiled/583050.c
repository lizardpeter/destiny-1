
void FUN_00583050(undefined8 param_1,long *param_2)

{
  long *plVar1;
  undefined2 uVar2;
  undefined *puVar3;
  undefined1 uVar4;
  int iVar5;
  undefined4 uVar6;
  int iVar7;
  long lVar8;
  undefined8 uVar9;
  long lVar10;
  long lVar11;
  uint uVar12;
  long lVar13;
  ushort uVar14;
  long lVar15;
  long *plVar16;
  ulong uVar17;
  long *plVar18;
  long *plVar19;
  bool bVar20;
  float fVar21;
  undefined4 local_1368 [2];
  uint local_1360 [2];
  long local_1358;
  int local_1350;
  uint uStack_134c;
  undefined8 *local_1348;
  long *local_1340;
  undefined4 local_1338 [2];
  uint local_1330 [2];
  long local_1328;
  int local_1320;
  uint uStack_131c;
  undefined8 *local_1318;
  long *local_1310;
  long local_1308 [122];
  long local_f38 [120];
  long local_b78 [120];
  long local_7b8 [120];
  undefined1 local_3f8 [960];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  local_1308[1] = 0;
  if (*param_2 != 0) {
    lVar8 = FUN_0057de80(*param_2);
    puVar3 = PTR_DAT_0197e2f0;
    lVar13 = *(long *)(PTR_DAT_0197e2f0 + 8);
    uVar9 = FUN_000e8680(lVar13,0,0xffffffff);
    thunk_FUN_012aa986(local_7b8,0,uVar9);
    uVar14 = *(ushort *)(lVar13 + 0x1c) & 0x78;
    bVar20 = uVar14 != 0;
    if (uVar14 == 0) {
      uVar12 = *(uint *)(lVar13 + 0x20);
      if ((*(ushort *)(lVar13 + 0x1c) & 0x40) != 0) {
        lVar10 = FUN_000e8a90(lVar13,local_7b8);
        if (lVar10 == 0) {
          uVar12 = uVar12 | 0x5488bf;
        }
        else {
          uVar12 = *(uint *)(lVar10 + 0x20) & 0x5488bf | uVar12;
        }
      }
      bVar20 = (uVar12 & 0xc08070) != 0;
    }
    if (bVar20) {
      FUN_000e6730(lVar13,local_7b8,0,0xffffffff,0);
    }
    lVar13 = *(long *)(puVar3 + 8);
    uVar9 = FUN_000e8680(lVar13,0,0xffffffff);
    plVar19 = local_f38;
    thunk_FUN_012aa986(plVar19,0,uVar9);
    uVar14 = *(ushort *)(lVar13 + 0x1c) & 0x78;
    bVar20 = uVar14 != 0;
    if (uVar14 == 0) {
      uVar12 = *(uint *)(lVar13 + 0x20);
      if ((*(ushort *)(lVar13 + 0x1c) & 0x40) != 0) {
        lVar10 = FUN_000e8a90(lVar13,local_f38);
        if (lVar10 == 0) {
          uVar12 = uVar12 | 0x5488bf;
        }
        else {
          uVar12 = *(uint *)(lVar10 + 0x20) & 0x5488bf | uVar12;
        }
      }
      bVar20 = (uVar12 & 0xc08070) != 0;
    }
    if (bVar20) {
      FUN_000e6730(lVar13,local_f38,0,0xffffffff,0);
    }
    lVar13 = *(long *)(puVar3 + 8);
    uVar9 = FUN_000e8680(lVar13,0,0xffffffff);
    thunk_FUN_012aa986(local_b78,0,uVar9);
    uVar14 = *(ushort *)(lVar13 + 0x1c) & 0x78;
    bVar20 = uVar14 != 0;
    if (uVar14 == 0) {
      uVar12 = *(uint *)(lVar13 + 0x20);
      if ((*(ushort *)(lVar13 + 0x1c) & 0x40) != 0) {
        lVar10 = FUN_000e8a90(lVar13,local_b78);
        if (lVar10 == 0) {
          uVar12 = uVar12 | 0x5488bf;
        }
        else {
          uVar12 = *(uint *)(lVar10 + 0x20) & 0x5488bf | uVar12;
        }
      }
      bVar20 = (uVar12 & 0xc08070) != 0;
    }
    if (bVar20) {
      FUN_000e6730(lVar13,local_b78,0,0xffffffff,0);
    }
    lVar13 = *(long *)(puVar3 + 8);
    uVar9 = FUN_000e8680(lVar13,0,0xffffffff);
    thunk_FUN_012aa986(local_1308 + 2,0,uVar9);
    uVar14 = *(ushort *)(lVar13 + 0x1c) & 0x78;
    bVar20 = uVar14 != 0;
    if (uVar14 == 0) {
      uVar12 = *(uint *)(lVar13 + 0x20);
      if ((*(ushort *)(lVar13 + 0x1c) & 0x40) != 0) {
        lVar10 = FUN_000e8a90(lVar13,local_1308 + 2);
        if (lVar10 == 0) {
          uVar12 = uVar12 | 0x5488bf;
        }
        else {
          uVar12 = *(uint *)(lVar10 + 0x20) & 0x5488bf | uVar12;
        }
      }
      bVar20 = (uVar12 & 0xc08070) != 0;
    }
    if (bVar20) {
      FUN_000e6730(lVar13,local_1308 + 2,0,0xffffffff,0);
    }
    thunk_FUN_012aa7c6(local_3f8,lVar8 + 0x10,0x3c0);
    FUN_00583d10();
    plVar18 = local_b78;
    plVar16 = local_1308 + 2;
    FUN_00584040();
    do {
      lVar13 = -0x3c0;
      if (*plVar19 == 0) break;
      do {
        if (lVar13 == 0) goto LAB_005833bb;
        plVar1 = (long *)(lVar8 + 0x3d0 + lVar13);
        lVar13 = lVar13 + 0x30;
      } while (*plVar19 != *plVar1);
      *(undefined8 *)(lVar8 + 0x3c8 + lVar13) = 0;
      *(undefined8 *)(lVar8 + 0x3c0 + lVar13) = 0;
      *(undefined8 *)(lVar8 + 0x3b8 + lVar13) = 0;
      *(undefined8 *)(lVar8 + 0x3b0 + lVar13) = 0;
      *(undefined8 *)(lVar8 + 0x3a8 + lVar13) = 0;
      *(undefined8 *)(lVar8 + 0x3a0 + lVar13) = 0;
LAB_005833bb:
      plVar19 = plVar19 + 6;
    } while (plVar19 != local_b78);
    do {
      lVar10 = *plVar16;
      lVar13 = 0;
      if (lVar10 == 0) break;
      do {
        if (lVar13 == 0x3c0) goto LAB_00583439;
        plVar19 = (long *)(lVar8 + 0x10 + lVar13);
        lVar13 = lVar13 + 0x30;
      } while (*plVar19 != lVar10);
      *(long *)(lVar8 + -0x20 + lVar13) = lVar10;
      *(short *)(lVar8 + -0x18 + lVar13) = (short)plVar16[1];
      uVar2 = *(undefined2 *)((long)plVar16 + 0x2a);
      *(undefined1 *)(lVar8 + 0xc + lVar13) = *(undefined1 *)((long)plVar16 + 0x2c);
      *(undefined2 *)(lVar8 + 10 + lVar13) = uVar2;
      *(undefined8 *)(lVar8 + 2 + lVar13) = *(undefined8 *)((long)plVar16 + 0x22);
      *(undefined8 *)(lVar8 + -6 + lVar13) = *(undefined8 *)((long)plVar16 + 0x1a);
      uVar9 = *(undefined8 *)((long)plVar16 + 10);
      *(undefined8 *)(lVar8 + -0xe + lVar13) = *(undefined8 *)((long)plVar16 + 0x12);
      *(undefined8 *)(lVar8 + -0x16 + lVar13) = uVar9;
LAB_00583439:
      plVar16 = plVar16 + 6;
    } while (plVar16 != local_f38);
    do {
      lVar13 = 0;
      if (*plVar18 == 0) break;
      do {
        if (lVar13 == 0x3c0) goto LAB_005834c4;
        plVar19 = (long *)(lVar8 + 0x10 + lVar13);
        lVar13 = lVar13 + 0x30;
      } while (*plVar19 != 0);
      *(long *)(lVar8 + -0x20 + lVar13) = *plVar18;
      *(short *)(lVar8 + -0x18 + lVar13) = (short)plVar18[1];
      uVar2 = *(undefined2 *)((long)plVar18 + 0x2a);
      *(undefined1 *)(lVar8 + 0xc + lVar13) = *(undefined1 *)((long)plVar18 + 0x2c);
      *(undefined2 *)(lVar8 + 10 + lVar13) = uVar2;
      *(undefined8 *)(lVar8 + 2 + lVar13) = *(undefined8 *)((long)plVar18 + 0x22);
      *(undefined8 *)(lVar8 + -6 + lVar13) = *(undefined8 *)((long)plVar18 + 0x1a);
      uVar9 = *(undefined8 *)((long)plVar18 + 10);
      *(undefined8 *)(lVar8 + -0xe + lVar13) = *(undefined8 *)((long)plVar18 + 0x12);
      *(undefined8 *)(lVar8 + -0x16 + lVar13) = uVar9;
LAB_005834c4:
      plVar18 = plVar18 + 6;
    } while (plVar18 != local_7b8);
    lVar13 = *(long *)(lVar8 + 0x3d8);
    *(undefined2 *)(lVar8 + 1000) = 0;
    *(undefined8 *)(lVar8 + 0x3e0) = 0;
    *(undefined8 *)(lVar8 + 0x3d8) = 0;
    *(undefined8 *)(lVar8 + 0x3d0) = 0;
    uVar9 = FUN_00557c40(&DAT_026bc508);
    local_1308[0] = FUN_00586510(uVar9,param_2);
    if (((local_1308[0] != 0) &&
        (lVar10 = FUN_00584560(local_1308), *(short *)(lVar10 + 0x2c20) != -1)) &&
       (*(char *)((long)&PTR_DAT_00002c38 + lVar10) == '\0')) {
      iVar5 = FUN_005452d0();
      *(undefined8 *)(lVar8 + 0x3d0) = *(undefined8 *)(lVar10 + 0x6fc0);
      lVar10 = 0;
      if (iVar5 == 3) {
        lVar10 = FUN_00587920();
        iVar5 = FUN_0010ca50();
        lVar10 = (long)iVar5 + *(long *)(lVar10 + 8);
      }
      lVar11 = lVar13 - lVar10;
      lVar15 = -lVar11;
      if (0 < lVar11) {
        lVar15 = lVar11;
      }
      if (0x22 < lVar15) {
        lVar13 = lVar10;
      }
      *(long *)(lVar8 + 0x3d8) = lVar13;
      uVar4 = FUN_00775840(1);
      *(undefined1 *)(lVar8 + 0x3e9) = uVar4;
      lVar13 = FUN_0011c5f0();
      if (lVar13 != 0) {
        uVar9 = *(undefined8 *)(DAT_02689580[1] + 0x10);
        uVar6 = FUN_0006f140(&DAT_02689580);
        FUN_0008f550(local_1330,uVar9,uVar6);
        local_1318 = &DAT_02689580;
        local_1310 = DAT_02689580;
        if ((int)local_1330[0] < local_1320) {
LAB_00583622:
          uVar17 = (ulong)((local_1330[0] & 0xffff) * (int)DAT_02689580[2]);
          if (*param_2 != *(long *)(*DAT_02689580 + 0x10 + uVar17)) {
            uVar17 = (ulong)uStack_131c;
            uVar12 = local_1330[0];
LAB_00583650:
            do {
              local_1330[0] = uVar12 + 1;
              if ((int)local_1330[0] < local_1320) {
                uVar17 = uVar17 >> 1;
                uStack_131c = (uint)uVar17;
                if (uStack_131c == 0) {
                  local_1330[0] = uVar12 + 0x20 & 0xffffffe0;
                  if (local_1320 <= (int)local_1330[0]) {
LAB_005836e3:
                    uVar17 = 0;
                    goto LAB_005836f0;
                  }
                  uStack_131c = *(uint *)(local_1328 + (long)((int)(uVar12 + 0x20) >> 5) * 4);
                  while (uVar17 = (ulong)uStack_131c, uStack_131c == 0) {
                    local_1330[0] = local_1330[0] + 0x20;
                    if (local_1320 <= (int)local_1330[0]) goto LAB_005836e3;
                    uStack_131c = *(uint *)(local_1328 + (long)((int)local_1330[0] >> 5) * 4);
                  }
                }
                uVar12 = local_1330[0];
                if ((uVar17 & 1) == 0) goto LAB_00583650;
              }
LAB_005836f0:
              if ((local_1320 <= (int)local_1330[0]) ||
                 (uVar12 = local_1330[0],
                 (*(uint *)(*(long *)(DAT_02689580[1] + 0x10) +
                           (ulong)(local_1330[0] >> 5 & 0x7ff) * 4) >> (local_1330[0] & 0x1f) & 1)
                 != 0)) goto LAB_0058370f;
            } while( true );
          }
          if (*DAT_02689580 + uVar17 != 0) {
            iVar5 = FUN_00301cb0();
            local_1338[0] = DAT_025d7450;
            uVar6 = FUN_0011d0d0(lVar13,iVar5,local_1338);
            *(undefined4 *)(lVar8 + 0x3e0) = uVar6;
            uVar9 = *(undefined8 *)(DAT_02689580[1] + 0x10);
            uVar6 = FUN_0006f140(&DAT_02689580);
            FUN_0008f550(local_1360,uVar9,uVar6);
            local_1348 = &DAT_02689580;
            local_1340 = DAT_02689580;
            if ((int)local_1360[0] < local_1350) {
              do {
                iVar7 = FUN_00301cb0((ulong)((local_1360[0] & 0xffff) * (int)local_1340[2]) +
                                     *local_1340);
                if (iVar7 != iVar5) {
                  *(char *)(lVar8 + 1000) = *(char *)(lVar8 + 1000) + '\x01';
                  local_1368[0] = DAT_025d7450;
                  fVar21 = (float)FUN_0011d0d0(lVar13,iVar7,local_1368);
                  if (*(float *)(lVar8 + 0x3e4) < fVar21) {
                    *(float *)(lVar8 + 0x3e4) = fVar21;
                  }
                }
                uVar17 = (ulong)uStack_134c;
LAB_00583822:
                do {
                  uVar12 = local_1360[0] + 1;
                  if ((int)uVar12 < local_1350) {
                    uVar17 = uVar17 >> 1;
                    uStack_134c = (uint)uVar17;
                    if (uStack_134c == 0) {
                      uVar12 = local_1360[0] + 0x20;
                      local_1360[0] = uVar12 & 0xffffffe0;
                      if (local_1350 <= (int)local_1360[0]) {
LAB_0058389d:
                        uVar17 = 0;
                        uVar12 = local_1360[0];
                        goto LAB_0058389f;
                      }
                      uStack_134c = *(uint *)(local_1358 + (long)((int)uVar12 >> 5) * 4);
                      while (uVar17 = (ulong)uStack_134c, uVar12 = local_1360[0], uStack_134c == 0)
                      {
                        local_1360[0] = local_1360[0] + 0x20;
                        if (local_1350 <= (int)local_1360[0]) goto LAB_0058389d;
                        uStack_134c = *(uint *)(local_1358 + (long)((int)local_1360[0] >> 5) * 4);
                      }
                    }
                    local_1360[0] = uVar12;
                    uVar12 = local_1360[0];
                    if ((uVar17 & 1) == 0) goto LAB_00583822;
                  }
LAB_0058389f:
                  local_1360[0] = uVar12;
                  if (local_1350 <= (int)local_1360[0]) goto LAB_005838ca;
                } while ((*(uint *)(*(long *)(local_1340[1] + 0x10) +
                                   (ulong)(local_1360[0] >> 5 & 0x7ff) * 4) >>
                          (local_1360[0] & 0x1f) & 1) == 0);
              } while( true );
            }
          }
        }
      }
    }
  }
LAB_005838ca:
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
LAB_0058370f:
  if (local_1320 <= (int)local_1330[0]) goto LAB_005838ca;
  goto LAB_00583622;
}

