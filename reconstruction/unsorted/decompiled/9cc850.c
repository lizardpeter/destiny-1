
void FUN_009cc850(long param_1)

{
  undefined *puVar1;
  long lVar2;
  bool bVar3;
  ulong uVar4;
  char cVar5;
  uint uVar6;
  long lVar7;
  long lVar8;
  undefined8 uVar9;
  long lVar10;
  long *plVar11;
  ulong *puVar12;
  undefined8 *puVar13;
  undefined4 *puVar14;
  long lVar15;
  int iVar16;
  long *plVar17;
  int *piVar18;
  float fVar19;
  float fVar20;
  float local_330 [6];
  undefined4 local_318 [2];
  undefined8 local_310;
  long local_308;
  undefined4 local_300 [2];
  undefined8 local_2f8;
  long local_2f0;
  undefined8 local_2e8;
  long local_2e0;
  undefined4 local_2d8 [2];
  undefined **local_2d0;
  char local_2c8;
  undefined1 uStack_2c7;
  char cStack_2c6;
  undefined1 uStack_2c5;
  float fStack_2c4;
  float fStack_2c0;
  undefined4 uStack_2bc;
  float local_2b8;
  undefined1 local_2b0 [8];
  undefined4 local_2a8 [2];
  undefined4 local_2a0 [6];
  undefined4 local_288 [6];
  undefined4 local_270 [6];
  undefined4 local_258 [6];
  undefined8 local_240 [3];
  float afStack_228 [122];
  long local_40;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  FUN_009438f0();
  lVar7 = FUN_0078eeb0();
  if (lVar7 != 0) {
    local_40 = 0;
    local_330[2] = 0.0;
    local_330[3] = 0.0;
    lVar10 = 0;
    piVar18 = &DAT_015de0e0;
    local_330[0] = 0.0;
    local_330[1] = 0.0;
    puVar12 = (ulong *)(lVar7 + 0x10);
    iVar16 = 1;
    do {
      if ((int)puVar12[-2] != 0) {
        local_2d0 = &PTR_thunk_FUN_00a8e8d0_01957d70;
        local_2c8 = (char)iVar16 + -1;
        uVar4 = puVar12[-2];
        uStack_2c7 = (char)uVar4;
        uStack_2bc = CONCAT31((int3)((uint)uStack_2bc >> 8),*(undefined1 *)((long)puVar12 + -0xc));
        local_2b8 = *(float *)(puVar12 + -1);
        if (*(float *)(puVar12 + -1) + DAT_016717c8 < DAT_016717f4) {
          local_2b8 = DAT_016717c4;
        }
        cStack_2c6 = *(char *)((long)puVar12 + -4);
        fStack_2c4 = -1.0;
        fStack_2c0 = -1.0;
        fVar19 = (float)*puVar12;
        if (cStack_2c6 != '\0') {
          if (fVar19 <= DAT_016717cc) {
            if (fVar19 <= DAT_016717d0) {
              if (fVar19 <= DAT_016717d4) {
                uStack_2c5 = 0;
              }
              else {
                uStack_2c5 = 1;
                fVar19 = fVar19 * DAT_016717d8;
              }
            }
            else {
              uStack_2c5 = 2;
              fVar19 = fVar19 * DAT_016717dc;
            }
          }
          else {
            uStack_2c5 = 3;
            fVar19 = fVar19 * DAT_016717e0;
          }
          fStack_2c4 = fVar19;
          if (*(char *)((long)puVar12 + -0xc) != '\0') {
            fStack_2c0 = fVar19 * *(float *)(puVar12 + -1);
          }
        }
        local_40 = lVar10 + 1;
        if (local_240 + lVar10 * 4 != (undefined8 *)0x0) {
          local_240[lVar10 * 4] = &PTR_thunk_FUN_00a8e8d0_01957d70;
          afStack_228[lVar10 * 8] = local_2b8;
          *(ulong *)(afStack_228 + lVar10 * 8 + -2) = CONCAT44(uStack_2bc,fStack_2c0);
          local_240[lVar10 * 4 + 1] =
               CONCAT44(fStack_2c4,
                        CONCAT13(uStack_2c5,CONCAT12(cStack_2c6,CONCAT11((char)uVar4,local_2c8))));
        }
        if (iVar16 != 4) {
          lVar7 = (long)*piVar18;
          local_330[lVar7] = local_330[lVar7] + DAT_016717e4;
          if (((int)puVar12[-2] == 3) || (fVar19 = *(float *)(puVar12 + -1), DAT_016717e4 <= fVar19)
             ) {
            fVar19 = local_330[lVar7 + 2] + DAT_016717e4;
          }
          else {
            if (fVar19 < DAT_016717f4) goto LAB_009ccada;
            fVar19 = fVar19 + local_330[lVar7 + 2];
          }
          local_330[lVar7 + 2] = fVar19;
        }
LAB_009ccada:
        FUN_00a8e8d0(&local_2d0);
        lVar10 = local_40;
      }
      if (lVar10 == 0x10) break;
      puVar12 = puVar12 + 3;
      piVar18 = piVar18 + 1;
      bVar3 = iVar16 < 5;
      iVar16 = iVar16 + 1;
    } while (bVar3);
    fVar19 = DAT_016717e8;
    if (DAT_016717ec < local_330[0]) {
      fVar19 = (local_330[2] / local_330[0]) * DAT_016717e8 + 0.0;
    }
    fVar20 = DAT_016717f0;
    if (DAT_016717ec < local_330[1]) {
      fVar20 = (local_330[3] / local_330[1]) * DAT_016717f0;
    }
    if (*(float *)(param_1 + 0x2a8) < fVar19 + fVar20) {
      *(float *)(param_1 + 0x2a8) = fVar19 + fVar20;
    }
    puVar13 = local_240;
    FUN_010dcfa0(puVar13,local_2a8,param_1 + 0x90,param_1 + 0x198,local_2b0);
    if (local_40 != 0) {
      lVar7 = local_40 << 5;
      do {
        (**(code **)*puVar13)(puVar13);
        puVar13 = puVar13 + 4;
        lVar7 = lVar7 + -0x20;
      } while (lVar7 != 0);
    }
  }
  uVar6 = FUN_00752a40();
  if (*(long *)(param_1 + 0x2a0) != 0) {
    plVar11 = (long *)(param_1 + 0x1a7U & 0xfffffffffffffff8);
    lVar7 = *(long *)(param_1 + 0x2a0) << 4;
    plVar17 = plVar11;
    do {
      if ((*plVar17 != 0) && (*(char *)(*plVar17 + 8) == '\x02')) {
        iVar16 = (int)((ulong)((long)plVar17 - (long)plVar11) >> 4);
        goto LAB_009ccc35;
      }
      plVar17 = plVar17 + 2;
      lVar7 = lVar7 + -0x10;
    } while (lVar7 != 0);
  }
  iVar16 = -1;
LAB_009ccc35:
  local_2a8[0] = DAT_027667b8;
  lVar7 = FUN_00977c40(*(undefined8 *)(param_1 + 0x28),local_2a8);
  if ((lVar7 != 0) &&
     (cVar5 = FUN_00978170(*(undefined8 *)(lVar7 + 0x10),DAT_0278b4f8), cVar5 != '\0')) {
    plVar17 = *(long **)(lVar7 + 0x248);
    if (plVar17 != (long *)(lVar7 + 0x248)) {
      do {
        lVar10 = plVar17[-0x3d];
        if (lVar10 != 0) {
          local_2d8[0] = DAT_027667bc;
          lVar8 = FUN_0108dc90(lVar10,local_2d8);
          if ((lVar8 != 0) &&
             (cVar5 = FUN_00978170(*(undefined8 *)(lVar8 + 0x10),DAT_02753618), cVar5 != '\0')) {
            if (*(int *)((long)plVar17 + 0x14) == iVar16) {
              if (*(char *)(lVar8 + 0x184) != '\0') {
                *(undefined1 *)(lVar8 + 0x184) = 0;
                FUN_009984d0(lVar8 + 0x78,0x40000000);
                FUN_0096dff0(lVar8);
              }
              if (*(long *)(param_1 + 0x2b0) == 0) {
                if ((uVar6 < 0xc) && ((0xba0UL >> ((byte)uVar6 & 0x3f) & 1) == 0)) {
                  puVar1 = (&PTR_DAT_01957e70)[(int)uVar6];
                  uVar9 = FUN_00065850(puVar1);
                  FUN_008dad00(&local_2e8,puVar1,uVar9);
                  if (local_2e0 != 0) {
                    *(int *)(local_2e0 + 8) = *(int *)(local_2e0 + 8) + 1;
                  }
                  *(undefined8 *)(param_1 + 0x2b0) = local_2e8;
                  lVar2 = *(long *)(param_1 + 0x2b8);
                  *(long *)(param_1 + 0x2b8) = local_2e0;
                  lVar15 = local_2e0;
                  if (lVar2 != 0) {
                    FUN_008dd4f0();
                    lVar15 = local_2e0;
                  }
                }
                else {
                  FUN_008da6c0(&local_2f8);
                  if (local_2f0 != 0) {
                    *(int *)(local_2f0 + 8) = *(int *)(local_2f0 + 8) + 1;
                  }
                  *(undefined8 *)(param_1 + 0x2b0) = local_2f8;
                  lVar2 = *(long *)(param_1 + 0x2b8);
                  *(long *)(param_1 + 0x2b8) = local_2f0;
                  lVar15 = local_2f0;
                  if (lVar2 != 0) {
                    FUN_008dd4f0();
                    lVar15 = local_2f0;
                  }
                }
                if (lVar15 != 0) {
                  FUN_008dd4f0();
                }
              }
              puVar14 = local_258;
              FUN_00a95af0(puVar14,(long *)(param_1 + 0x2b0));
            }
            else {
              if (*(char *)(lVar8 + 0x184) != '\x01') {
                *(undefined1 *)(lVar8 + 0x184) = 1;
                FUN_009984d0(lVar8 + 0x78,0x40000000);
                FUN_0096dff0(lVar8);
              }
              local_270[0] = 0xffffffff;
              puVar14 = local_270;
            }
            FUN_0096e090(lVar8,puVar14);
            FUN_00a95c80(puVar14);
          }
          local_300[0] = DAT_027667c0;
          lVar10 = FUN_0108dc90(lVar10,local_300);
          if ((lVar10 != 0) &&
             (cVar5 = FUN_00978170(*(undefined8 *)(lVar10 + 0x10),DAT_02753618), cVar5 != '\0')) {
            if (uVar6 == 3) {
              if (*(long *)(param_1 + 0x2c0) == 0) {
                uVar9 = FUN_00065850(u__peut_prendre_un_certain_temps__015de100);
                FUN_008dad00(&local_310,u__peut_prendre_un_certain_temps__015de100,uVar9);
                if (local_308 != 0) {
                  *(int *)(local_308 + 8) = *(int *)(local_308 + 8) + 1;
                }
                *(undefined8 *)(param_1 + 0x2c0) = local_310;
                lVar8 = *(long *)(param_1 + 0x2c8);
                *(long *)(param_1 + 0x2c8) = local_308;
                if (lVar8 != 0) {
                  FUN_008dd4f0();
                }
                if (local_308 != 0) {
                  FUN_008dd4f0();
                }
              }
              local_318[0] = 0x811c9dc5;
              FUN_0096dee0(lVar10,local_318);
              puVar14 = local_288;
              FUN_00a95af0(puVar14,(long *)(param_1 + 0x2c0));
            }
            else {
              local_330[4] = (float)DAT_027667c4;
              FUN_0096dee0(lVar10,local_330 + 4);
              local_2a0[0] = 0xffffffff;
              puVar14 = local_2a0;
            }
            FUN_0096e090(lVar10,puVar14);
            FUN_00a95c80(puVar14);
          }
        }
        plVar17 = (long *)*plVar17;
      } while (plVar17 != (long *)(lVar7 + 0x248));
    }
  }
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

