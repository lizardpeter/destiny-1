
void FUN_002778b0(long *param_1,undefined8 *param_2,long param_3,undefined4 param_4)

{
  long *plVar1;
  long *plVar2;
  code *pcVar3;
  undefined *puVar4;
  char cVar5;
  char cVar6;
  long lVar7;
  long lVar8;
  undefined8 uVar9;
  long lVar10;
  long lVar11;
  undefined1 *puVar12;
  long *plVar13;
  long lVar14;
  long lVar15;
  undefined8 *puVar16;
  uint uVar17;
  ushort uVar18;
  long lVar19;
  long lVar20;
  ulong uVar21;
  long lVar22;
  bool bVar23;
  ulong local_100;
  undefined8 uStack_f8;
  long lStack_f0;
  long lStack_e8;
  long local_e0;
  undefined8 local_d8;
  long local_d0;
  ulong local_c8;
  undefined8 local_c0;
  undefined4 local_b8;
  undefined4 uStack_b4;
  undefined8 local_b0;
  undefined8 local_a8;
  undefined8 local_a0;
  undefined8 local_98;
  undefined8 local_90;
  int local_88;
  char acStack_84 [36];
  long local_60;
  
  local_60 = *DAT_01a1f100;
  lVar7 = (**(code **)(*param_1 + 0x90))();
  if (lVar7 == 0) goto LAB_00278206;
  if (*(char *)(param_3 + 0x19) != '\0') {
    FUN_00277700(param_1);
  }
  if (*(char *)(param_3 + 0x18) != '\0') {
    lVar8 = (**(code **)(*param_1 + 0x88))(param_1);
    lVar11 = *(long *)(PTR_DAT_0197e368 + 8);
    uVar9 = FUN_000e8680(lVar11,0,0xffffffff);
    lVar19 = lVar8 + 0x4c0;
    thunk_FUN_012aa986(lVar19,0,uVar9);
    uVar18 = *(ushort *)(lVar11 + 0x1c) & 0x78;
    bVar23 = uVar18 != 0;
    if (uVar18 == 0) {
      uVar17 = *(uint *)(lVar11 + 0x20);
      if ((*(ushort *)(lVar11 + 0x1c) & 0x40) != 0) {
        lVar10 = FUN_000e8a90(lVar11,lVar19);
        if (lVar10 == 0) {
          uVar17 = uVar17 | 0x5488bf;
        }
        else {
          uVar17 = *(uint *)(lVar10 + 0x20) & 0x5488bf | uVar17;
        }
      }
      bVar23 = (uVar17 & 0xc08070) != 0;
    }
    if (bVar23) {
      FUN_000e6730(lVar11,lVar19,0,0xffffffff);
    }
    lVar11 = *(long *)(PTR_DAT_0197e168 + 8);
    uVar9 = FUN_000e8680(lVar11,0,0xffffffff);
    lVar19 = lVar8 + 0x383c;
    thunk_FUN_012aa986(lVar19,0,uVar9);
    uVar18 = *(ushort *)(lVar11 + 0x1c) & 0x78;
    bVar23 = uVar18 != 0;
    if (uVar18 == 0) {
      uVar17 = *(uint *)(lVar11 + 0x20);
      if ((*(ushort *)(lVar11 + 0x1c) & 0x40) != 0) {
        lVar10 = FUN_000e8a90(lVar11,lVar19);
        if (lVar10 == 0) {
          uVar17 = uVar17 | 0x5488bf;
        }
        else {
          uVar17 = *(uint *)(lVar10 + 0x20) & 0x5488bf | uVar17;
        }
      }
      bVar23 = (uVar17 & 0xc08070) != 0;
    }
    if (bVar23) {
      FUN_000e6730(lVar11,lVar19,0,0xffffffff);
    }
    lVar11 = *(long *)(PTR_DAT_0197e170 + 8);
    uVar9 = FUN_000e8680(lVar11,0,0xffffffff);
    lVar19 = lVar8 + 0x4458;
    thunk_FUN_012aa986(lVar19,0,uVar9);
    uVar18 = *(ushort *)(lVar11 + 0x1c) & 0x78;
    bVar23 = uVar18 != 0;
    if (uVar18 == 0) {
      uVar17 = *(uint *)(lVar11 + 0x20);
      if ((*(ushort *)(lVar11 + 0x1c) & 0x40) != 0) {
        lVar10 = FUN_000e8a90(lVar11,lVar19);
        if (lVar10 == 0) {
          uVar17 = uVar17 | 0x5488bf;
        }
        else {
          uVar17 = *(uint *)(lVar10 + 0x20) & 0x5488bf | uVar17;
        }
      }
      bVar23 = (uVar17 & 0xc08070) != 0;
    }
    if (bVar23) {
      FUN_000e6730(lVar11,lVar19,0,0xffffffff);
    }
    lVar19 = *(long *)(PTR_DAT_0197e2d0 + 8);
    uVar9 = FUN_000e8680(lVar19,0,0xffffffff);
    lVar8 = lVar8 + 0x2e4c;
    thunk_FUN_012aa986(lVar8,0,uVar9);
    uVar18 = *(ushort *)(lVar19 + 0x1c) & 0x78;
    bVar23 = uVar18 != 0;
    if (uVar18 == 0) {
      uVar17 = *(uint *)(lVar19 + 0x20);
      if ((*(ushort *)(lVar19 + 0x1c) & 0x40) != 0) {
        lVar11 = FUN_000e8a90(lVar19,lVar8);
        if (lVar11 == 0) {
          uVar17 = uVar17 | 0x5488bf;
        }
        else {
          uVar17 = *(uint *)(lVar11 + 0x20) & 0x5488bf | uVar17;
        }
      }
      bVar23 = (uVar17 & 0xc08070) != 0;
    }
    if (bVar23) {
      FUN_000e6730(lVar19,lVar8,0,0xffffffff);
    }
  }
  if (*(char *)(param_3 + 4) != -1) {
    *(char *)(lVar7 + 10) = *(char *)(param_3 + 4);
  }
  if (*(char *)(param_3 + 5) != -1) {
    *(char *)(lVar7 + 8) = *(char *)(param_3 + 5);
  }
  if (*(char *)(param_3 + 6) != -1) {
    *(char *)(lVar7 + 9) = *(char *)(param_3 + 6);
  }
  puVar4 = PTR_DAT_0197e1c0;
  lVar19 = *(long *)(param_3 + 8);
  if (lVar19 < 1) {
LAB_002781ce:
    puVar12 = (undefined1 *)(**(code **)(*param_1 + 200))(param_1);
    *puVar12 = 0;
    FUN_00278790(param_1,param_2);
  }
  else {
    plVar1 = (long *)(param_3 + 0x10);
    bVar23 = false;
    lVar11 = 0;
    do {
      lVar8 = *plVar1;
      cVar5 = *(char *)((long)plVar1 + lVar11 * 0x48 + lVar8 + 0x10);
      if ((cVar5 == -1) || (cVar5 == *(char *)(lVar7 + 10))) {
        cVar5 = *(char *)((long)plVar1 + lVar11 * 0x48 + lVar8 + 0x11);
        if (((cVar5 == -1) || (cVar5 == *(char *)(lVar7 + 8))) &&
           ((cVar5 = *(char *)((long)plVar1 + lVar11 * 0x48 + lVar8 + 0x12), cVar5 == -1 ||
            (cVar5 == *(char *)(lVar7 + 9))))) {
          FUN_0027a330(param_1,(long)plVar1 + lVar11 * 0x48 + lVar8 + 0x28,
                       (long)plVar1 + lVar11 * 0x48 + lVar8 + 0x38);
          puVar12 = (undefined1 *)(**(code **)(*param_1 + 200))(param_1);
          *puVar12 = 0;
          if (0 < *(long *)((long)plVar1 + lVar11 * 0x48 + lVar8 + 0x18)) {
            plVar2 = (long *)((long)plVar1 + lVar11 * 0x48 + lVar8 + 0x20);
            lVar19 = 0;
            do {
              FUN_00274190(lVar7,*(undefined2 *)((long)plVar2 + lVar19 * 8 + *plVar2 + 0x10),
                           *(undefined4 *)((long)plVar2 + lVar19 * 8 + *plVar2 + 0x14));
              lVar19 = lVar19 + 1;
            } while (lVar19 < *(long *)((long)plVar1 + lVar11 * 0x48 + lVar8 + 0x18));
          }
          if (0 < *(long *)((long)plVar1 + lVar11 * 0x48 + lVar8 + 0x48)) {
            plVar2 = (long *)((long)plVar1 + lVar11 * 0x48 + lVar8 + 0x50);
            lVar19 = 0;
            do {
              lVar10 = *plVar2;
              lVar20 = lVar19 * 0x38;
              plVar13 = (long *)FUN_0025a550();
              lVar14 = (**(code **)(*plVar13 + 0x410))
                                 (plVar13,*(undefined2 *)((long)plVar2 + lVar20 + 0x10 + lVar10));
              if (DAT_0295b378 == '\0') {
                lVar22 = *(long *)(puVar4 + 8);
                uVar9 = FUN_000e8680(lVar22,0,0xffffffff);
                thunk_FUN_012aa986(&local_a8,0,uVar9);
                uVar18 = *(ushort *)(lVar22 + 0x1c) & 0x78;
                bVar23 = uVar18 != 0;
                if (uVar18 == 0) {
                  uVar17 = *(uint *)(lVar22 + 0x20);
                  if ((*(ushort *)(lVar22 + 0x1c) & 0x40) != 0) {
                    lVar15 = FUN_000e8a90(lVar22,&local_a8);
                    if (lVar15 == 0) {
                      uVar17 = uVar17 | 0x5488bf;
                    }
                    else {
                      uVar17 = *(uint *)(lVar15 + 0x20) & 0x5488bf | uVar17;
                    }
                  }
                  bVar23 = (uVar17 & 0xc08070) != 0;
                }
                if (bVar23) {
                  FUN_000e6730(lVar22,&local_a8,0,0xffffffff,0);
                }
                DAT_0295b368 = local_90;
                DAT_0295b360 = local_98;
                DAT_0295b358 = local_a0;
                DAT_0295b350 = local_a8;
                DAT_0295b378 = '\x01';
              }
              local_b0 = DAT_0295b368;
              local_c0 = DAT_0295b358;
              local_c8 = CONCAT62((int6)((ulong)DAT_0295b350 >> 0x10),
                                  *(undefined2 *)((long)plVar2 + lVar20 + 0x10 + lVar10));
              puVar16 = (undefined8 *)0x0;
              _local_b8 = CONCAT44((int)((ulong)DAT_0295b360 >> 0x20),
                                   *(undefined4 *)((long)plVar2 + lVar20 + lVar10 + 0x14));
              if (*(char *)(lVar14 + 0x8b) == '\0') {
LAB_00278160:
                FUN_0026cef0(param_1,param_2,&local_c8,puVar16,
                             *(undefined1 *)((long)plVar2 + lVar20 + lVar10 + 0x40),param_4);
              }
              else {
                pcVar3 = *(code **)*param_2;
                uVar9 = (**(code **)(*param_1 + 0xa8))(param_1);
                puVar16 = (undefined8 *)(*pcVar3)(param_2,uVar9);
                if (puVar16 != (undefined8 *)0x0) {
                  uStack_f8 = *puVar16;
                  local_d8 = 0;
                  local_100 = local_c8 & 0xffff;
                  local_e0 = (long)plVar2 + lVar20 + lVar10 + 0x1c;
                  local_d0 = (long)plVar2 + lVar20 + lVar10 + 0x20;
                  lStack_e8 = (long)plVar2 + lVar20 + lVar10 + 0x18;
                  lStack_f0 = lVar7 + 0x4c98;
                  local_c0 = uStack_f8;
                  cVar5 = FUN_0026e3d0(&local_100,param_1,puVar16);
                  if (cVar5 != '\0') {
                    FUN_0026f1e0(lVar14,param_1,puVar16);
                    *(undefined4 *)(puVar16 + 7) =
                         *(undefined4 *)((long)plVar2 + lVar20 + lVar10 + 0x24);
                    if (*(long *)(lVar14 + 0x58) != 0) {
                      plVar13 = (long *)FUN_0025a550();
                      lVar14 = (**(code **)(*plVar13 + 0x4d8))
                                         (plVar13,*(undefined2 *)(puVar16 + 0xb));
                      if ((*(char *)((long)plVar2 + lVar20 + lVar10 + 0x28) != '\0') &&
                         (0 < *(long *)(lVar14 + 0x10))) {
                        plVar13 = (long *)(lVar14 + 0x18);
                        cVar5 = '\0';
                        do {
                          lVar22 = *plVar13;
                          uVar21 = (ulong)cVar5;
                          lVar15 = uVar21 * 0x40;
                          if ((*(int *)((long)plVar13 + lVar15 + 0x48 + lVar22) == -0x7ee3623b) ||
                             (cVar6 = FUN_00284ca0(puVar16 + 7,
                                                   (long)plVar13 + lVar15 + lVar22 + 0x10,
                                                   uVar21 & 0xffffffff,0), cVar5 == cVar6)) {
                            *(undefined1 *)((long)puVar16 + uVar21 + 0x5a) =
                                 *(undefined1 *)((long)plVar13 + lVar15 + lVar22 + 0x28);
                          }
                          cVar5 = cVar5 + '\x01';
                        } while ((long)cVar5 < *(long *)(lVar14 + 0x10));
                      }
                      if (0 < *(long *)((long)plVar2 + lVar20 + lVar10 + 0x30)) {
                        plVar13 = (long *)((long)plVar2 + lVar20 + lVar10 + 0x38);
                        lVar22 = 0;
                        do {
                          lVar15 = *plVar13;
                          *(undefined1 *)
                           ((long)puVar16 +
                           (long)*(char *)((long)plVar13 + lVar22 * 2 + lVar15 + 0x10) + 0x5a) =
                               *(undefined1 *)((long)plVar13 + lVar22 * 2 + lVar15 + 0x11);
                          if (*(char *)((long)plVar13 + lVar22 * 2 + lVar15 + 0x11) != '\0') {
                            local_88 = 0;
                            FUN_002841c0(lVar14,(int)*(char *)((long)plVar13 +
                                                              lVar22 * 2 + lVar15 + 0x10),&local_88)
                            ;
                            lVar15 = 0;
                            if (0 < local_88) {
                              do {
                                *(undefined1 *)((long)puVar16 + (long)acStack_84[lVar15] + 0x5a) = 0
                                ;
                                lVar15 = lVar15 + 1;
                              } while ((int)lVar15 < local_88);
                            }
                          }
                          lVar22 = lVar22 + 1;
                        } while (lVar22 < *(long *)((long)plVar2 + lVar20 + lVar10 + 0x30));
                      }
                      FUN_00284290(puVar16 + 7);
                    }
                    goto LAB_00278160;
                  }
                }
              }
              lVar19 = lVar19 + 1;
            } while (lVar19 < *(long *)((long)plVar1 + lVar11 * 0x48 + lVar8 + 0x48));
          }
          lVar19 = *(long *)(param_3 + 8);
          bVar23 = true;
        }
      }
      lVar11 = lVar11 + 1;
    } while (lVar11 < lVar19);
    if (!bVar23) goto LAB_002781ce;
  }
  if (*(char *)(param_3 + 0x19) != '\0') {
    FUN_00265770(param_1,param_2);
  }
  FUN_00265c50(param_1,param_2);
LAB_00278206:
  if (*DAT_01a1f100 != local_60) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

