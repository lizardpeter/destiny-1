
/* WARNING: Removing unreachable block (ram,0x000d65a3) */

ulong FUN_000d6300(undefined8 param_1,uint *param_2,short param_3,long param_4,long *param_5)

{
  long *plVar1;
  short *psVar2;
  short *psVar3;
  long lVar4;
  int iVar5;
  short sVar6;
  short sVar7;
  ushort uVar8;
  ushort uVar9;
  long *plVar10;
  long *plVar11;
  char cVar12;
  ushort uVar13;
  uint uVar14;
  int iVar15;
  int iVar16;
  long lVar17;
  undefined8 uVar18;
  long lVar19;
  long lVar20;
  undefined4 uVar21;
  uint uVar22;
  long lVar23;
  long lVar24;
  ushort uVar25;
  ulong uVar26;
  ulong uVar27;
  long lVar28;
  bool bVar29;
  bool bVar30;
  ushort local_382;
  int local_380 [2];
  undefined1 local_378 [24];
  undefined1 local_360 [256];
  undefined1 local_260 [4];
  undefined4 local_25c;
  undefined1 local_140 [264];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  FUN_0008a7e0(local_260);
  uVar13 = FUN_00077100(DAT_025820a8,1,&DAT_025838b0);
  plVar10 = DAT_025820a8;
  uVar26 = (ulong)uVar13;
  lVar28 = DAT_025820a8[2] * uVar26;
  lVar24 = *DAT_025820a8;
  psVar2 = (short *)((long)DAT_025820a8 + lVar28 + lVar24);
  thunk_FUN_012aa986(psVar2,0,0x288);
  lVar17 = FUN_00064f60(param_1,&DAT_01616479);
  lVar4 = (long)plVar10 + lVar28 + 0x140 + lVar24;
  if (lVar17 == 0) {
    FUN_010080a0(lVar4,s_packages__s_pkg_0161647e,param_1);
  }
  else {
    FUN_00065030(lVar4,param_1,0x100);
  }
  *(long *)((long)plVar10 + lVar28 + 0x268 + lVar24) = DAT_01ad4f48;
  *(long *)((long)plVar10 + lVar28 + 0x260 + lVar24) = DAT_01ad4f48;
  *(long *)((long)plVar10 + lVar28 + 0x248 + lVar24) = DAT_01ad4f48;
  *(undefined2 *)((long)plVar10 + lVar28 + 0x274 + lVar24) = 0xffff;
  *(undefined2 *)((long)plVar10 + lVar28 + 0x27c + lVar24) = 0xffff;
  *(undefined4 *)((long)plVar10 + lVar28 + 0x270 + lVar24) = 0xffffffff;
  uVar21 = 0xc;
  if ((*param_2 & 0x40) != 0) {
    uVar21 = 5;
  }
  *(undefined4 *)((long)plVar10 + lVar28 + 0x240 + lVar24) = uVar21;
  FUN_00087ad0(local_140);
  FUN_00087d20(local_140,*(undefined4 *)((long)plVar10 + lVar28 + 0x240 + lVar24),lVar4);
  FUN_0008ac00(local_260,local_140);
  cVar12 = FUN_0008ac30(local_260,3,local_25c);
  uVar14 = 0xffffffac;
  if (cVar12 == '\0') {
    bVar30 = false;
    bVar29 = false;
  }
  else {
    cVar12 = FUN_0008ba70(local_260,0,0x140,psVar2);
    uVar14 = 1;
    if (cVar12 == '\0') {
      uVar14 = 0xffffffa1;
    }
    cVar12 = FUN_0008b600(local_260,local_380);
    if (cVar12 == '\0') {
      uVar14 = 0xffffffa1;
    }
    bVar30 = false;
    bVar29 = false;
    if (uVar14 == 1) {
      uVar14 = FUN_0003b180();
      uVar25 = *(ushort *)((long)plVar10 + lVar28 + 2 + lVar24);
      if (uVar25 == uVar14) {
        bVar30 = false;
        uVar14 = 0xffffffbf;
        if (*psVar2 == 0x18) {
          sVar6 = *(short *)((long)plVar10 + lVar28 + 4 + lVar24);
          cVar12 = FUN_0008ba70(local_260,*(undefined4 *)((long)plVar10 + lVar28 + 0xb0 + lVar24),
                                0x100,local_360);
          if (cVar12 == '\0') {
            uVar14 = 0xffffffa1;
          }
          else {
            cVar12 = FUN_000d9340(psVar2,local_360);
            if (cVar12 != '\0') {
              uVar22 = *(uint *)((long)plVar10 + lVar28 + 0xb4 + lVar24);
              bVar30 = false;
              if (uVar22 == 0) {
                bVar29 = false;
              }
              else {
                if (uVar22 < 0x2001) {
                  if (*(int *)((long)plVar10 + lVar28 + 0x13c + lVar24) == local_380[0]) {
                    bVar30 = false;
                    if (0xff < *(ushort *)((long)plVar10 + lVar28 + 0x20 + lVar24)) {
                      bVar29 = false;
                      goto LAB_000d6d95;
                    }
                    uVar14 = *param_2;
                    if (((uVar14 & 8) == 0) ||
                       (*(short *)((long)plVar10 + lVar28 + lVar24 + 4) == param_3)) {
                      if (((uVar14 & 4) == 0) ||
                         (*(long *)((long)plVar10 + lVar28 + 8 + lVar24) == param_4)) {
                        uVar25 = sVar6 + 0x400;
                        uVar22 = uVar25 - 0x40a;
                        if ((uVar14 & 1) == 0) {
LAB_000d66bb:
                          bVar30 = false;
                          uVar14 = 0xffffffbf;
                          bVar29 = false;
                          if (uVar22 < 0xbf6) {
                            uVar18 = FUN_0006fb60();
                            *(undefined8 *)((long)plVar10 + lVar28 + 0x250 + lVar24) = uVar18;
                            uVar25 = *(ushort *)((long)plVar10 + lVar28 + 0x22 + lVar24);
                            bVar30 = true;
                            uVar14 = DAT_025838b8;
                            if (((uVar25 != 0) &&
                                (uVar22 = (uint)uVar25, uVar14 = uVar22, DAT_025838b8 != 0)) &&
                               (uVar14 = DAT_025838b8, uVar22 != DAT_025838b8)) {
                              if (DAT_01a231f0 == (code *)0x0) {
                                FUN_0005c750(s_Package_localization_mismatch__a_0161648e,uVar22,
                                             DAT_025838b8);
                                s__libexec_ld_elf_so_1_00000000[1] = '*';
                                s__libexec_ld_elf_so_1_00000000[2] = '\0';
                                s__libexec_ld_elf_so_1_00000000[3] = '\0';
                                s__libexec_ld_elf_so_1_00000000[4] = '\0';
                                uVar14 = DAT_025838b8;
                              }
                              else {
                                (*DAT_01a231f0)(0,s_Package_localization_mismatch__a_0161648e);
                                uVar14 = DAT_025838b8;
                              }
                            }
                            DAT_025838b8 = uVar14;
                            plVar11 = DAT_025820a8;
                            lVar17 = 0;
                            if ((ulong)*(ushort *)
                                        (&DAT_025820b0 +
                                        (long)*(short *)((long)plVar10 + lVar28 + 4 + lVar24) * 2)
                                != 0xffff) {
                              lVar19 = (ulong)*(ushort *)
                                               (&DAT_025820b0 +
                                               (long)*(short *)((long)plVar10 + lVar28 + 4 + lVar24)
                                               * 2) * DAT_025820a8[2];
                              lVar17 = *DAT_025820a8;
                              DAT_025820a0 = *(long *)((long)DAT_025820a8 + lVar19 + 0x248 + lVar17)
                              ;
                              *(long *)((long)DAT_025820a8 + lVar19 + 0x248 + lVar17) = DAT_01ad4f48
                              ;
                              lVar17 = (long)plVar11 + lVar19 + lVar17;
                            }
                            bVar29 = false;
                            if (*(long *)((long)plVar10 + lVar28 + 0x250 + lVar24) != 0) {
                              iVar15 = FUN_0006f130();
                              bVar29 = iVar15 != 0;
                            }
                            plVar11 = DAT_025820a8;
                            if (DAT_025838b0 != 0xffff) {
                              plVar1 = DAT_025820a8 + 1;
                              uVar25 = DAT_025838b0;
LAB_000d6800:
                              uVar27 = (ulong)uVar25;
                              lVar20 = DAT_025820a8[2] * uVar27;
                              lVar19 = *DAT_025820a8;
                              sVar6 = *(short *)((long)plVar10 + lVar28 + lVar24 + 4);
                              sVar7 = *(short *)((long)DAT_025820a8 + lVar20 + 4 + lVar19);
                              if (sVar7 == sVar6) {
                                uVar9 = *(ushort *)((long)DAT_025820a8 + lVar20 + 0x20 + lVar19);
                                uVar8 = *(ushort *)((long)plVar10 + lVar28 + lVar24 + 0x20);
                                if (!bVar29) {
                                  psVar3 = (short *)((long)DAT_025820a8 + lVar20 + lVar19);
                                  if ((uVar8 == uVar9) && (psVar2 != psVar3)) {
                                    uVar22 = 0xffffffc0;
                                    if (*(long *)((long)plVar10 + lVar28 + lVar24 + 8) ==
                                        *(long *)((long)DAT_025820a8 + lVar20 + 8 + lVar19))
                                    goto LAB_000d6ac9;
                                    FUN_000d6fc0();
                                    if (*(int *)((long)plVar11 + lVar20 + 0x270 + lVar19) != -1) {
                                      FUN_000839f0();
                                      *(undefined4 *)((long)plVar11 + lVar20 + lVar19 + 0x270) =
                                           0xffffffff;
                                      DAT_025838c4 = DAT_025838c4 + -1;
                                    }
                                    FUN_00077490(DAT_025820a8,&DAT_025838b0,&DAT_025838b0,uVar13,
                                                 uVar27);
                                    FUN_00077290(plVar11,&DAT_025838b0,uVar27);
                                    lVar19 = DAT_025820a8[2];
                                    lVar20 = lVar19 * uVar26;
                                    lVar23 = *DAT_025820a8 + (long)DAT_025820a8;
                                    if (uVar13 != 0xffff) goto LAB_000d69ef;
                                  }
                                  else {
                                    if (psVar2 != psVar3) {
                                      if (uVar8 <= uVar9) goto LAB_000d689b;
                                      FUN_00077490(DAT_025820a8,&DAT_025838b0,&DAT_025838b0,uVar13,
                                                   uVar27);
                                    }
                                    lVar19 = DAT_025820a8[2];
                                    lVar20 = lVar19 * uVar26;
                                    lVar23 = *DAT_025820a8 + (long)DAT_025820a8;
                                    if (uVar13 != 0xffff) {
                                      uVar25 = *(ushort *)
                                                ((long)DAT_025820a8 +
                                                uVar26 * 4 + DAT_025820a8[1] + 10);
                                      goto LAB_000d6a90;
                                    }
                                  }
LAB_000d6ab1:
                                  *(ushort *)
                                   (&DAT_025820b0 + (long)*(short *)(lVar20 + 4 + lVar23) * 2) =
                                       uVar13;
                                  goto LAB_000d6ac3;
                                }
                                uVar22 = 0xffffffa3;
                                if (uVar9 <= uVar8 && uVar8 != uVar9) goto LAB_000d6ac9;
                                if (uVar8 == uVar9) {
                                  uVar22 = 2;
                                  if (*(long *)((long)plVar10 + lVar28 + lVar24 + 8) !=
                                      *(long *)((long)DAT_025820a8 + lVar20 + 8 + lVar19)) {
                                    uVar22 = 0xffffffa3;
                                  }
                                  goto LAB_000d6ac9;
                                }
                                if (uVar25 == 0xffff) goto LAB_000d6ac3;
                                lVar19 = uVar27 * 4 + *plVar1;
                              }
                              else {
                                if (sVar6 < sVar7) {
                                  FUN_00077490(DAT_025820a8,&DAT_025838b0,&DAT_025838b0,uVar13,
                                               uVar27);
                                  lVar19 = DAT_025820a8[2];
                                  lVar20 = lVar19 * uVar26;
                                  lVar23 = *DAT_025820a8 + (long)DAT_025820a8;
                                  if (uVar13 == 0xffff) goto LAB_000d6ab1;
LAB_000d69ef:
                                  uVar25 = *(ushort *)
                                            ((long)DAT_025820a8 + uVar26 * 4 + DAT_025820a8[1] + 10)
                                  ;
LAB_000d6a90:
                                  bVar29 = (ulong)uVar25 == 0xffff;
                                  if (!bVar29) {
                                    bVar29 = *(short *)((ulong)uVar25 * lVar19 + 4 + lVar23) !=
                                             *(short *)(lVar20 + 4 + lVar23);
                                  }
                                  if (!bVar29) goto LAB_000d6ac3;
                                  goto LAB_000d6ab1;
                                }
LAB_000d689b:
                                if (uVar25 == 0xffff) goto LAB_000d6ac3;
                                lVar19 = uVar27 * 4 + *plVar1;
                              }
                              uVar25 = *(ushort *)((long)plVar1 + lVar19);
                              if (uVar25 == 0xffff) goto LAB_000d6ac3;
                              goto LAB_000d6800;
                            }
                            uVar22 = 1;
                            goto LAB_000d6ac9;
                          }
                        }
                        else {
                          bVar30 = false;
                          uVar14 = 0xffffffaa;
                          if (uVar22 < 0x9f6) {
                            bVar29 = false;
                          }
                          else {
                            bVar29 = false;
                            if (0x1ff < uVar25 - 0xe00) goto LAB_000d66bb;
                          }
                        }
                        goto LAB_000d6d95;
                      }
                      uVar14 = 0xffffffa6;
                    }
                    else {
                      uVar14 = 0xffffffa5;
                    }
                  }
                  else {
                    uVar14 = 0xffffffa8;
                  }
                  goto LAB_000d65f3;
                }
                bVar29 = false;
              }
              goto LAB_000d6d95;
            }
            uVar14 = 0xffffffa3;
          }
LAB_000d65f3:
          bVar30 = false;
          bVar29 = false;
        }
        else {
          bVar29 = false;
        }
      }
      else {
        bVar30 = false;
        uVar14 = 0xffffffbf;
        local_382 = uVar25;
        if (0xff < uVar25) {
          FUN_000c00f0(&local_382,1,0xfffffffe);
          goto LAB_000d65f3;
        }
        bVar29 = false;
      }
    }
  }
LAB_000d6d95:
  cVar12 = FUN_0008b0d0(local_260);
  if (cVar12 != '\0') {
    FUN_0008aa70(local_260);
  }
  if (uVar14 == 1) {
    uVar26 = 1;
    if (param_5 == (long *)0x0) goto LAB_000d6f58;
    *param_5 = (long)psVar2;
    uVar26 = 1;
  }
  else {
    if (*(int *)((long)plVar10 + lVar28 + lVar24 + 0x270) != -1) {
      FUN_000839f0();
      *(undefined4 *)((long)plVar10 + lVar28 + lVar24 + 0x270) = 0xffffffff;
      DAT_025838c4 = DAT_025838c4 + -1;
    }
    if (bVar30) {
      FUN_000d6fc0(psVar2);
    }
    uVar25 = 0xffff;
    if (uVar13 != 0xffff) {
      uVar9 = *(ushort *)((long)DAT_025820a8 + uVar26 * 4 + DAT_025820a8[1] + 8);
      if (((ulong)uVar9 != 0xffff) &&
         (uVar25 = uVar9,
         *(short *)((long)DAT_025820a8 + uVar26 * DAT_025820a8[2] + 4 + *DAT_025820a8) !=
         *(short *)((long)DAT_025820a8 + DAT_025820a8[2] * (ulong)uVar9 + 4 + *DAT_025820a8))) {
        uVar25 = 0xffff;
      }
    }
    sVar6 = *(short *)((long)plVar10 + lVar28 + 4 + lVar24);
    FUN_00077290(DAT_025820a8,&DAT_025838b0,uVar13);
    if (bVar29) {
      if (uVar25 == 0xffff) {
        *(undefined2 *)(&DAT_025820b0 + (long)sVar6 * 2) = 0xffff;
      }
      else {
        lVar24 = DAT_025820a8[2] * (ulong)uVar25;
        uVar26 = (ulong)*(ushort *)((long)DAT_025820a8 + (ulong)uVar25 * 4 + DAT_025820a8[1] + 10);
        lVar4 = *DAT_025820a8;
        bVar30 = uVar26 == 0xffff;
        if (!bVar30) {
          bVar30 = *(short *)((long)DAT_025820a8 + uVar26 * DAT_025820a8[2] + 4 + lVar4) !=
                   *(short *)((long)DAT_025820a8 + lVar24 + 4 + lVar4);
        }
        if (bVar30) {
          *(ushort *)(&DAT_025820b0 + (long)*(short *)((long)DAT_025820a8 + lVar24 + 4 + lVar4) * 2)
               = uVar25;
        }
      }
    }
    uVar26 = 1;
    if (uVar14 != 2) {
      uVar26 = (ulong)uVar14;
    }
    if (param_5 != (long *)0x0) {
      *param_5 = 0;
    }
  }
  if (((int)uVar26 == -0x40) && (uVar26 = 0xffffffc0, (*param_2 & 0x10) != 0)) {
    uVar26 = 1;
  }
LAB_000d6f58:
  thunk_FUN_0008aa70(local_260);
  if (*DAT_01a1f100 != local_38) {
    uVar26 = thunk_FUN_012aa7f6();
    return uVar26;
  }
  return uVar26;
LAB_000d6ac3:
  uVar22 = 1;
LAB_000d6ac9:
  uVar25 = *(ushort *)(&DAT_025820b0 + (long)*(short *)((long)plVar10 + lVar28 + lVar24 + 4) * 2);
  bVar29 = uVar13 == uVar25;
  if ((uVar22 == 1) && (bVar29)) {
    iVar15 = *(int *)((long)plVar10 + lVar28 + 0xec + lVar24) * 0x44;
    if (iVar15 == 0) {
      *(long *)((long)plVar10 + lVar28 + lVar24 + 0x248) = DAT_01ad4f48;
      goto LAB_000d6c1d;
    }
    lVar20 = FUN_000d7090(DAT_0257a072,iVar15,uVar13);
    lVar19 = *(long *)(&DAT_01ad5030 + (ulong)DAT_0257a072 * DAT_01ad5010 + DAT_01ad5000);
    cVar12 = FUN_0008ba70(local_260,*(undefined4 *)((long)plVar10 + lVar28 + 0xf0 + lVar24),iVar15,
                          lVar19 + lVar20);
    uVar14 = 0xffffffa1;
    if (cVar12 != '\0') {
      *(long *)((long)plVar10 + lVar28 + lVar24 + 0x248) = lVar20;
      cVar12 = FUN_000d9560(lVar19 + lVar20,iVar15,(long)plVar10 + lVar28 + lVar24 + 0xf4,local_378)
      ;
      if (cVar12 != '\0') goto LAB_000d6c1d;
      if (DAT_01a231f0 == (code *)0x0) {
        FUN_0005c750(s_resourcerer_contexts__Failed_to_v_0161654c,lVar4);
        s__libexec_ld_elf_so_1_00000000[1] = '*';
        s__libexec_ld_elf_so_1_00000000[2] = '\0';
        s__libexec_ld_elf_so_1_00000000[3] = '\0';
        s__libexec_ld_elf_so_1_00000000[4] = '\0';
      }
      else {
        (*DAT_01a231f0)(2,s_resourcerer_contexts__Failed_to_v_0161654c,lVar4);
      }
      uVar14 = 0xffffffa7;
    }
  }
  else {
LAB_000d6c1d:
    uVar14 = uVar22;
    if (uVar22 == 1) {
      if ((ushort)(*(short *)((long)plVar10 + lVar28 + lVar24 + 4) + 0x400) - 0x40a < 0x9f6) {
        iVar15 = FUN_00059260();
        iVar16 = FUN_00059280();
        if (((iVar15 == -1) ||
            (iVar5 = *(int *)((long)plVar10 + lVar28 + lVar24 + 0x18), iVar15 < iVar5)) ||
           ((iVar15 == iVar5 && (iVar16 < *(int *)((long)plVar10 + lVar28 + 0x1c + lVar24))))) {
          FUN_00059300(*(undefined4 *)((long)plVar10 + lVar28 + lVar24 + 0x18));
          FUN_00059310(*(undefined4 *)((long)plVar10 + lVar28 + lVar24 + 0x1c));
        }
      }
      else {
        FUN_00059320(1);
      }
      uVar14 = 1;
      if (uVar13 == uVar25) {
        uVar14 = 1;
        if (DAT_025820a0 == DAT_01ad4f48) {
          bVar29 = true;
        }
        else {
          FUN_000b1950((long)&DAT_01ad5000 + (ulong)DAT_0257a072 * DAT_01ad5010 + DAT_01ad5000);
          DAT_025820a0 = DAT_01ad4f48;
        }
        goto LAB_000d6d95;
      }
    }
  }
  if (lVar17 != 0) {
    *(long *)(lVar17 + 0x248) = DAT_025820a0;
    DAT_025820a0 = DAT_01ad4f48;
  }
  goto LAB_000d6d95;
}

