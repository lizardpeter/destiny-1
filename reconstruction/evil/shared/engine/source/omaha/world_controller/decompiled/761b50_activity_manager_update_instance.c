
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00761b50(long param_1,int param_2)

{
  undefined4 *puVar1;
  uint uVar2;
  int iVar3;
  bool bVar4;
  char cVar5;
  undefined4 uVar6;
  long lVar7;
  long lVar8;
  long lVar9;
  long lVar10;
  long *plVar11;
  undefined8 uVar12;
  undefined8 *puVar13;
  undefined8 uVar14;
  undefined8 uVar15;
  long lVar16;
  int *piVar17;
  int iVar18;
  int iVar19;
  int iVar20;
  long lVar21;
  char *pcVar22;
  undefined8 local_2d0;
  undefined8 local_2c8;
  undefined8 local_2c0;
  undefined8 local_2b8;
  uint local_2b0 [2];
  undefined8 local_2a8;
  undefined8 local_2a0;
  undefined8 uStack_298;
  undefined8 uStack_290;
  undefined8 uStack_288;
  undefined8 local_280;
  undefined8 uStack_278;
  undefined8 uStack_270;
  undefined8 uStack_268;
  undefined8 local_260;
  undefined8 uStack_258;
  undefined8 uStack_250;
  undefined8 uStack_248;
  undefined8 local_240;
  undefined8 uStack_238;
  undefined8 uStack_230;
  undefined8 uStack_228;
  undefined8 local_220;
  undefined8 uStack_218;
  undefined8 uStack_210;
  undefined8 uStack_208;
  undefined8 local_200;
  undefined8 uStack_1f8;
  undefined8 uStack_1f0;
  undefined8 uStack_1e8;
  undefined8 local_1e0;
  undefined8 uStack_1d8;
  undefined8 uStack_1d0;
  undefined8 uStack_1c8;
  undefined8 local_1c0;
  undefined8 uStack_1b8;
  undefined8 uStack_1b0;
  undefined8 uStack_1a8;
  undefined1 local_1a0 [320];
  long local_60;
  
  local_60 = *DAT_01a1f100;
  lVar7 = FUN_0075bdb0();
  lVar8 = FUN_00b74340(lVar7);
  cVar5 = FUN_00b8f690();
  lVar16 = (long)param_2 * 0x1f0;
  puVar1 = (undefined4 *)(param_1 + 0x4f0 + lVar16);
  if (cVar5 == '\0') {
    iVar18 = FUN_000697a0();
    if (1000 < (uint)(iVar18 - _DAT_026c9af8)) {
      cVar5 = FUN_000e4d70(2,1);
      if (cVar5 != '\0') {
        if ((DAT_026c9b00 == '\0') && (iVar18 = thunk_FUN_012aa7d6(&DAT_026c9b00), iVar18 != 0)) {
          DAT_026c9afc = FUN_000e4a10(s_world_controller_activity_manage_0164bb4b);
          thunk_FUN_012aa7e6(&DAT_026c9b00);
        }
        uVar15 = FUN_00b6db70(lVar7);
        pcVar22 = s_<SESSION_NOT_ESTABLISHED>_0164c92f;
        if ((*(uint *)(lVar7 + 0x8c48) < 0xb) &&
           ((0x7f0U >> (*(uint *)(lVar7 + 0x8c48) & 0x1f) & 1) != 0)) {
          cVar5 = FUN_00b742d0(lVar7);
          if (cVar5 == '\0') {
            pcVar22 = s_<NO_MEMBERSHIP>_0164c949;
          }
          else {
            pcVar22 = s_<HOST_INDEX_INVALID>_0164c959;
            if (((*(uint *)(lVar7 + 0x64c) >> (*(uint *)(lVar7 + 0x630) & 0x1f) & 1) != 0) &&
               (lVar8 = (long)(int)*(uint *)(lVar7 + 0x630) * 0x168,
               *(int *)(lVar7 + 0x67c + lVar8) != 3)) {
              pcVar22 = (char *)(lVar7 + 0x690 + lVar8);
            }
          }
        }
        FUN_01008290(local_1a0,s_world_controller_activity_manage_0164bb4b,param_1 + 0x6c8 + lVar16,
                     uVar15,pcVar22);
        FUN_000e4aa0(DAT_026c9afc,local_1a0);
      }
      _DAT_026c9af8 = FUN_000697a0();
    }
  }
  else {
    lVar21 = lVar7 + 0x6eb8;
    cVar5 = FUN_00b8f690(lVar21);
    if (cVar5 == '\0') {
      iVar18 = FUN_000697a0();
      if (1000 < (uint)(iVar18 - _DAT_026c9b08)) {
        cVar5 = FUN_000e4d70(2,1);
        if (cVar5 != '\0') {
          if ((DAT_026c9b10 == '\0') && (iVar18 = thunk_FUN_012aa7d6(&DAT_026c9b10), iVar18 != 0)) {
            DAT_026c9b0c = FUN_000e4a10(s_world_controller_activity_manage_0164bbb8);
            thunk_FUN_012aa7e6(&DAT_026c9b10);
          }
          uVar15 = FUN_00b6db70(lVar7);
          pcVar22 = s_<SESSION_NOT_ESTABLISHED>_0164c92f;
          if ((*(uint *)(lVar7 + 0x8c48) < 0xb) &&
             ((0x7f0U >> (*(uint *)(lVar7 + 0x8c48) & 0x1f) & 1) != 0)) {
            cVar5 = FUN_00b742d0(lVar7);
            if (cVar5 == '\0') {
              pcVar22 = s_<NO_MEMBERSHIP>_0164c949;
            }
            else {
              pcVar22 = s_<HOST_INDEX_INVALID>_0164c959;
              if (((*(uint *)(lVar7 + 0x64c) >> (*(uint *)(lVar7 + 0x630) & 0x1f) & 1) != 0) &&
                 (lVar8 = (long)(int)*(uint *)(lVar7 + 0x630) * 0x168,
                 *(int *)(lVar7 + 0x67c + lVar8) != 3)) {
                pcVar22 = (char *)(lVar7 + 0x690 + lVar8);
              }
            }
          }
          FUN_01008290(local_1a0,s_world_controller_activity_manage_0164bbb8,
                       param_1 + 0x6c8 + lVar16,uVar15,pcVar22);
          FUN_000e4aa0(DAT_026c9b0c,local_1a0);
        }
        _DAT_026c9b08 = FUN_000697a0();
      }
    }
    else {
      local_2a8 = FUN_00b8f0f0(lVar21);
      cVar5 = FUN_000b4f80(&local_2a8);
      if (cVar5 == '\0') {
        iVar18 = FUN_000697a0();
        if (1000 < (uint)(iVar18 - _DAT_026c9b18)) {
          cVar5 = FUN_000e4d70(2,1);
          if (cVar5 != '\0') {
            if ((DAT_026c9b20 == '\0') && (iVar18 = thunk_FUN_012aa7d6(&DAT_026c9b20), iVar18 != 0))
            {
              DAT_026c9b1c = FUN_000e4a10(s_world_controller_activity_manage_0164bc3a);
              thunk_FUN_012aa7e6(&DAT_026c9b20);
            }
            uVar15 = FUN_00b6db70(lVar7);
            pcVar22 = s_<SESSION_NOT_ESTABLISHED>_0164c92f;
            if ((*(uint *)(lVar7 + 0x8c48) < 0xb) &&
               ((0x7f0U >> (*(uint *)(lVar7 + 0x8c48) & 0x1f) & 1) != 0)) {
              cVar5 = FUN_00b742d0(lVar7);
              if (cVar5 == '\0') {
                pcVar22 = s_<NO_MEMBERSHIP>_0164c949;
              }
              else {
                pcVar22 = s_<HOST_INDEX_INVALID>_0164c959;
                if (((*(uint *)(lVar7 + 0x64c) >> (*(uint *)(lVar7 + 0x630) & 0x1f) & 1) != 0) &&
                   (lVar8 = (long)(int)*(uint *)(lVar7 + 0x630) * 0x168,
                   *(int *)(lVar7 + 0x67c + lVar8) != 3)) {
                  pcVar22 = (char *)(lVar7 + 0x690 + lVar8);
                }
              }
            }
            FUN_01008290(local_1a0,s_world_controller_activity_manage_0164bc3a,
                         param_1 + 0x6c8 + lVar16,uVar15,pcVar22);
            FUN_000e4aa0(DAT_026c9b1c,local_1a0);
          }
          _DAT_026c9b18 = FUN_000697a0();
        }
      }
      else {
        lVar9 = FUN_00b8f0c0(lVar21);
        lVar10 = FUN_00b8e190(lVar7 + 0x74e0);
        if (lVar9 == lVar10) {
          plVar11 = (long *)FUN_002a0010(*(undefined4 *)(param_1 + 0x5b8 + lVar16));
          local_2b0[0] = 0;
          FUN_00b8f120(lVar21,local_2b0);
          if (((((local_2b0[0] >> (*(uint *)(lVar8 + 0x5d0c) & 0x1f) & 1) == 0) &&
               (uVar2 = *(uint *)(lVar7 + 0x8c48), (uVar2 & 0xfffffffe) != 6)) && (uVar2 != 8)) &&
             (uVar2 != 9)) {
            lVar8 = FUN_0034e340();
            cVar5 = FUN_0075f890(puVar1,0x18,(long)*(int *)(lVar8 + 0x18));
            if (cVar5 == '\0') {
              iVar18 = FUN_000697a0();
              if (1000 < (uint)(iVar18 - _DAT_026c9b48)) {
                cVar5 = FUN_000e4d70(2,2);
                if (cVar5 != '\0') {
                  if ((DAT_026c9b50 == '\0') &&
                     (iVar18 = thunk_FUN_012aa7d6(&DAT_026c9b50), iVar18 != 0)) {
                    DAT_026c9b4c = FUN_000e4a10(s_world_controller_activity_manage_0164bd87);
                    thunk_FUN_012aa7e6(&DAT_026c9b50);
                  }
                  lVar8 = 0;
                  if (*(int *)(param_1 + 0x5a8 + lVar16) == 0x18) {
                    lVar21 = *(long *)(param_1 + 0x5b0 + lVar16);
                    lVar8 = DAT_026553b0;
                    if (DAT_026553a8 == '\0') {
                      lVar8 = FUN_000694d0();
                    }
                    lVar8 = lVar8 - lVar21;
                  }
                  pcVar22 = s_<SESSION_NOT_ESTABLISHED>_0164c92f;
                  if ((*(uint *)(lVar7 + 0x8c48) < 0xb) &&
                     ((0x7f0U >> (*(uint *)(lVar7 + 0x8c48) & 0x1f) & 1) != 0)) {
                    cVar5 = FUN_00b742d0(lVar7);
                    if (cVar5 == '\0') {
                      pcVar22 = s_<NO_MEMBERSHIP>_0164c949;
                    }
                    else {
                      pcVar22 = s_<HOST_INDEX_INVALID>_0164c959;
                      if (((*(uint *)(lVar7 + 0x64c) >> (*(uint *)(lVar7 + 0x630) & 0x1f) & 1) != 0)
                         && (lVar21 = (long)(int)*(uint *)(lVar7 + 0x630) * 0x168,
                            *(int *)(lVar7 + 0x67c + lVar21) != 3)) {
                        pcVar22 = (char *)(lVar7 + 0x690 + lVar21);
                      }
                    }
                  }
                  FUN_01008290(local_1a0,s_world_controller_activity_manage_0164bd87,
                               param_1 + 0x6c8 + lVar16,lVar8,pcVar22);
                  FUN_000e4aa0(DAT_026c9b4c,local_1a0);
                }
                _DAT_026c9b48 = FUN_000697a0();
              }
            }
            else {
              *puVar1 = 0x18;
            }
            goto LAB_00762874;
          }
          if ((*(ushort *)(plVar11 + 0x26) & 8) == 0) {
            local_1c0 = 0;
            uStack_1b8 = 0;
            uStack_1b0 = 0;
            uStack_1a8 = 0;
            local_1e0 = 0;
            uStack_1d8 = 0;
            uStack_1d0 = 0;
            uStack_1c8 = 0;
            local_200 = 0;
            uStack_1f8 = 0;
            uStack_1f0 = 0;
            uStack_1e8 = 0;
            local_220 = 0;
            uStack_218 = 0;
            uStack_210 = 0;
            uStack_208 = 0;
            local_240 = 0;
            uStack_238 = 0;
            uStack_230 = 0;
            uStack_228 = 0;
            local_260 = 0;
            uStack_258 = 0;
            uStack_250 = 0;
            uStack_248 = 0;
            local_280 = 0;
            uStack_278 = 0;
            uStack_270 = 0;
            uStack_268 = 0;
            local_2a0 = 0;
            uStack_298 = 0;
            uStack_290 = 0;
            uStack_288 = 0;
            FUN_002e9160(4,&local_2a0);
            uStack_298 = FUN_00b8f0f0(lVar21);
            iVar18 = *(int *)(lVar8 + 0x5d0c);
            puVar13 = (undefined8 *)FUN_00b81740(lVar8,iVar18);
            uStack_290 = *puVar13;
            lVar9 = (long)iVar18 * 0x168;
            uStack_270 = *(undefined8 *)(lVar8 + 0x130 + lVar9);
            lVar9 = (long)*(int *)(lVar8 + 0x18c + lVar9);
            if (lVar9 == -1) {
              uStack_278 = 0;
              local_280 = 0;
              uStack_288 = 0;
            }
            else {
              lVar9 = lVar9 * 0xe8;
              uStack_288 = *(undefined8 *)(&DAT_00001c5c + lVar9 + lVar8);
              local_280 = *(undefined8 *)(lVar8 + 0x1ce0 + lVar9);
              uStack_278 = *(undefined8 *)(lVar8 + 0x1ce8 + lVar9);
            }
            FUN_00762e70(lVar7,&uStack_268);
            uVar6 = FUN_000e94a0();
            uStack_1b0 = CONCAT44(uVar6,(undefined4)uStack_1b0);
            uStack_1b0 = uStack_1b0 & 0xffffffffffffff00;
            cVar5 = FUN_0029ab70(plVar11,&local_2a0);
            if (cVar5 == '\0') {
              if ((DAT_026c9b60 == '\0') &&
                 (iVar18 = thunk_FUN_012aa7d6(&DAT_026c9b60), iVar18 != 0)) {
                DAT_026c9b58 = FUN_000e4a10(s_world_controller_activity_manage_0164be14);
                thunk_FUN_012aa7e6(&DAT_026c9b60);
              }
              uVar15 = (**(code **)(*plVar11 + 0x30))(plVar11);
              local_2b8 = FUN_00b8f0f0(lVar21);
              uVar14 = FUN_002a35d0(&local_2b8);
              FUN_01008290(local_1a0,s_world_controller_activity_manage_0164be14,
                           param_1 + 0x6c8 + lVar16,uVar15,uVar14);
              FUN_000e4aa0(DAT_026c9b58,local_1a0);
              *puVar1 = 0x19;
            }
            else {
              cVar5 = FUN_000e4d70(2,3);
              if (cVar5 != '\0') {
                if ((DAT_026c9b70 == '\0') &&
                   (iVar18 = thunk_FUN_012aa7d6(&DAT_026c9b70), iVar18 != 0)) {
                  DAT_026c9b68 = FUN_000e4a10(s_world_controller_activity_manage_0164be76);
                  thunk_FUN_012aa7e6(&DAT_026c9b70);
                }
                local_2c0 = FUN_00b8f0f0(lVar21);
                uVar15 = FUN_002a35d0(&local_2c0);
                pcVar22 = s_<SESSION_NOT_ESTABLISHED>_0164c92f;
                if ((*(uint *)(lVar7 + 0x8c48) < 0xb) &&
                   ((0x7f0U >> (*(uint *)(lVar7 + 0x8c48) & 0x1f) & 1) != 0)) {
                  cVar5 = FUN_00b742d0(lVar7);
                  if (cVar5 == '\0') {
                    pcVar22 = s_<NO_MEMBERSHIP>_0164c949;
                  }
                  else {
                    pcVar22 = s_<HOST_INDEX_INVALID>_0164c959;
                    if (((*(uint *)(lVar7 + 0x64c) >> (*(uint *)(lVar7 + 0x630) & 0x1f) & 1) != 0)
                       && (lVar8 = (long)(int)*(uint *)(lVar7 + 0x630) * 0x168,
                          *(int *)(lVar7 + 0x67c + lVar8) != 3)) {
                      pcVar22 = (char *)(lVar7 + 0x690 + lVar8);
                    }
                  }
                }
                FUN_01008290(local_1a0,s_world_controller_activity_manage_0164be76,
                             param_1 + 0x6c8 + lVar16,uVar15,pcVar22);
                FUN_000e4aa0(DAT_026c9b68,local_1a0);
              }
            }
            goto LAB_00762874;
          }
          if ((*(ushort *)(plVar11 + 0x26) & 0x10) == 0) {
            lVar7 = FUN_0034e340();
            cVar5 = FUN_0075f890(puVar1,0x1a,(long)*(int *)(lVar7 + 0x1c));
            if (cVar5 == '\0') {
              iVar18 = FUN_000697a0();
              if (1000 < (uint)(iVar18 - _DAT_026c9b78)) {
                cVar5 = FUN_000e4d70(2,1);
                if (cVar5 != '\0') {
                  if ((DAT_026c9b80 == '\0') &&
                     (iVar18 = thunk_FUN_012aa7d6(&DAT_026c9b80), iVar18 != 0)) {
                    DAT_026c9b7c = FUN_000e4a10(s_world_controller_activity_manage_0164bed2);
                    thunk_FUN_012aa7e6(&DAT_026c9b80);
                  }
                  local_2c8 = FUN_00b8f0f0(lVar21);
                  uVar15 = FUN_002a35d0(&local_2c8);
                  FUN_01008290(local_1a0,s_world_controller_activity_manage_0164bed2,
                               param_1 + 0x6c8 + lVar16,uVar15);
                  FUN_000e4aa0(DAT_026c9b7c,local_1a0);
                }
                _DAT_026c9b78 = FUN_000697a0();
              }
            }
            else {
              *puVar1 = 0x1a;
            }
            goto LAB_00762874;
          }
          cVar5 = (**(code **)(*plVar11 + 0x18))();
          iVar18 = -1;
          piVar17 = DAT_026c96f8;
          do {
            if (iVar18 == 1) {
              iVar18 = -1;
              break;
            }
            iVar18 = iVar18 + 1;
            iVar19 = *piVar17;
            piVar17 = piVar17 + 1;
          } while (iVar19 != param_2);
          piVar17 = DAT_026c96f8 + 2;
          iVar19 = -1;
          do {
            iVar20 = iVar18;
            if (iVar19 == 1) break;
            iVar19 = iVar19 + 1;
            iVar3 = *piVar17;
            piVar17 = piVar17 + 1;
            iVar20 = iVar19;
          } while (iVar3 != param_2);
          if (cVar5 == '\0') {
            bVar4 = false;
            if (iVar20 != 1) {
              iVar18 = FUN_007850a0();
              bVar4 = 0x1e < iVar18;
            }
            if ((DAT_026c9b90 == '\0') && (iVar18 = thunk_FUN_012aa7d6(&DAT_026c9b90), iVar18 != 0))
            {
              DAT_026c9b88 = FUN_000e4a10(s_world_controller_activity_manage_0164bf2f);
              thunk_FUN_012aa7e6(&DAT_026c9b90);
            }
            local_2d0 = FUN_00b8f0f0(lVar21);
            uVar15 = FUN_002a35d0(&local_2d0);
            pcVar22 = s_<SESSION_NOT_ESTABLISHED>_0164c92f;
            if ((*(uint *)(lVar7 + 0x8c48) < 0xb) &&
               ((0x7f0U >> (*(uint *)(lVar7 + 0x8c48) & 0x1f) & 1) != 0)) {
              cVar5 = FUN_00b742d0(lVar7);
              if (cVar5 == '\0') {
                pcVar22 = s_<NO_MEMBERSHIP>_0164c949;
              }
              else {
                pcVar22 = s_<HOST_INDEX_INVALID>_0164c959;
                if (((*(uint *)(lVar7 + 0x64c) >> (*(uint *)(lVar7 + 0x630) & 0x1f) & 1) != 0) &&
                   (lVar8 = (long)(int)*(uint *)(lVar7 + 0x630) * 0x168,
                   *(int *)(lVar7 + 0x67c + lVar8) != 3)) {
                  pcVar22 = (char *)(lVar7 + 0x690 + lVar8);
                }
              }
            }
            lVar7 = param_1 + 0x6c8 + lVar16;
            FUN_01008290(local_1a0,s_world_controller_activity_manage_0164bf2f,lVar7,uVar15,pcVar22)
            ;
            FUN_000e4aa0(DAT_026c9b88,local_1a0);
            if (*(char *)(param_1 + 0x5bd + lVar16) == '\0' || bVar4) {
              *puVar1 = 0x1d;
            }
            else {
              if ((DAT_026c9ba0 == '\0') &&
                 (iVar18 = thunk_FUN_012aa7d6(&DAT_026c9ba0), iVar18 != 0)) {
                DAT_026c9b98 = FUN_000e4a10(s_world_controller_activity_manage_0164bf8d);
                thunk_FUN_012aa7e6(&DAT_026c9ba0);
              }
              FUN_01008290(local_1a0,s_world_controller_activity_manage_0164bf8d,lVar7);
              FUN_000e4aa0(DAT_026c9b98,local_1a0);
              FUN_00b8efe0(lVar21);
              *puVar1 = 0x1e;
            }
            goto LAB_00762874;
          }
          FUN_00768080();
          cVar5 = FUN_007528d0();
          if (cVar5 == '\0') {
            lVar7 = FUN_00775180(2 - (uint)(iVar20 == 0));
            uVar2 = *(uint *)(lVar7 + 0x8c48);
            if (((((uVar2 & 0xfffffffe) == 6) || (uVar2 == 8)) || (uVar2 == 9)) &&
               (((cVar5 = FUN_00752150(3), cVar5 == '\0' || (iVar18 = FUN_0078b270(), iVar18 == 3))
                || (iVar18 = FUN_0078b250(), iVar18 == 3)))) goto LAB_007623fe;
            cVar5 = FUN_002999a0(plVar11);
            if (cVar5 == '\0') {
              lVar7 = FUN_0034e340();
              cVar5 = FUN_0075f890(puVar1,0x1b,(long)*(int *)(lVar7 + 0x20));
              if (cVar5 == '\0') {
                iVar18 = FUN_000697a0();
                if (1000 < (uint)(iVar18 - _DAT_026c9ba8)) {
                  cVar5 = FUN_000e4d70(2,1);
                  if (cVar5 != '\0') {
                    if ((DAT_026c9bb0 == '\0') &&
                       (iVar18 = thunk_FUN_012aa7d6(&DAT_026c9bb0), iVar18 != 0)) {
                      DAT_026c9bac = FUN_000e4a10(s_world_controller_activity_manage_0164c023);
                      thunk_FUN_012aa7e6(&DAT_026c9bb0);
                    }
                    uVar15 = (**(code **)(*plVar11 + 0x30))(plVar11);
                    FUN_01008290(local_1a0,s_world_controller_activity_manage_0164c023,
                                 param_1 + 0x6c8 + lVar16,uVar15);
                    FUN_000e4aa0(DAT_026c9bac,local_1a0);
                  }
                  _DAT_026c9ba8 = FUN_000697a0();
                }
              }
              else {
                *puVar1 = 0x1b;
              }
              goto LAB_00762874;
            }
            cVar5 = FUN_002998f0(plVar11);
            if (cVar5 == '\0') {
              lVar7 = FUN_0034e340();
              cVar5 = FUN_0075f890(puVar1,0x1c,(long)*(int *)(lVar7 + 0x24));
              if (cVar5 == '\0') {
                iVar18 = FUN_000697a0();
                if (1000 < (uint)(iVar18 - _DAT_026c9bb8)) {
                  cVar5 = FUN_000e4d70(2,1);
                  if (cVar5 != '\0') {
                    if ((DAT_026c9bc0 == '\0') &&
                       (iVar18 = thunk_FUN_012aa7d6(&DAT_026c9bc0), iVar18 != 0)) {
                      DAT_026c9bbc = FUN_000e4a10(s_world_controller_activity_manage_0164c07c);
                      thunk_FUN_012aa7e6(&DAT_026c9bc0);
                    }
                    FUN_01008290(local_1a0,s_world_controller_activity_manage_0164c07c,
                                 param_1 + 0x6c8 + lVar16);
                    FUN_000e4aa0(DAT_026c9bbc,local_1a0);
                  }
                  _DAT_026c9bb8 = FUN_000697a0();
                }
              }
              else {
                *puVar1 = 0x1c;
              }
              goto LAB_00762874;
            }
            cVar5 = FUN_000e4d70(2,2);
            if (cVar5 != '\0') {
              if ((DAT_026c9bd0 == '\0') &&
                 (iVar18 = thunk_FUN_012aa7d6(&DAT_026c9bd0), iVar18 != 0)) {
                DAT_026c9bc8 = FUN_000e4a10(s_world_controller_activity_manage_0164c0cf);
                thunk_FUN_012aa7e6(&DAT_026c9bd0);
              }
              uVar15 = (**(code **)(*plVar11 + 0x30))(plVar11);
              FUN_01008290(local_1a0,s_world_controller_activity_manage_0164c0cf,
                           param_1 + 0x6c8 + lVar16,uVar15);
              FUN_000e4aa0(DAT_026c9bc8,local_1a0);
            }
          }
          else {
LAB_007623fe:
            cVar5 = FUN_002999b0(plVar11);
            if (cVar5 == '\0') goto LAB_00762874;
          }
          *puVar1 = 6;
          goto LAB_00762874;
        }
        iVar18 = FUN_000697a0();
        if (1000 < (uint)(iVar18 - _DAT_026c9b28)) {
          cVar5 = FUN_000e4d70(2,1);
          if (cVar5 != '\0') {
            if ((DAT_026c9b30 == '\0') && (iVar18 = thunk_FUN_012aa7d6(&DAT_026c9b30), iVar18 != 0))
            {
              DAT_026c9b2c = FUN_000e4a10(s_world_controller_activity_manage_0164bca5);
              thunk_FUN_012aa7e6(&DAT_026c9b30);
            }
            uVar15 = FUN_00b6db70(lVar7);
            uVar14 = FUN_00b8f0c0(lVar21);
            uVar14 = FUN_002ea6a0(uVar14);
            uVar12 = FUN_00b8e190(lVar7 + 0x74e0);
            uVar12 = FUN_002ea6a0(uVar12);
            FUN_01008290(local_1a0,s_world_controller_activity_manage_0164bca5,
                         param_1 + 0x6c8 + lVar16,uVar15,uVar14,uVar12);
            FUN_000e4aa0(DAT_026c9b2c,local_1a0);
          }
          _DAT_026c9b28 = FUN_000697a0();
        }
      }
    }
  }
  lVar8 = FUN_0034e340();
  cVar5 = FUN_0075f890(puVar1,0x17,(long)*(int *)(lVar8 + 0x14));
  if (cVar5 == '\0') {
    iVar18 = FUN_000697a0();
    if (1000 < (uint)(iVar18 - _DAT_026c9b38)) {
      cVar5 = FUN_000e4d70(2,1);
      if (cVar5 != '\0') {
        if ((DAT_026c9b40 == '\0') && (iVar18 = thunk_FUN_012aa7d6(&DAT_026c9b40), iVar18 != 0)) {
          DAT_026c9b3c = FUN_000e4a10(s_world_controller_activity_manage_0164bd10);
          thunk_FUN_012aa7e6(&DAT_026c9b40);
        }
        lVar8 = 0;
        if (*(int *)(param_1 + 0x5a8 + lVar16) == 0x17) {
          lVar21 = *(long *)(param_1 + 0x5b0 + lVar16);
          lVar8 = DAT_026553b0;
          if (DAT_026553a8 == '\0') {
            lVar8 = FUN_000694d0();
          }
          lVar8 = lVar8 - lVar21;
        }
        pcVar22 = s_<SESSION_NOT_ESTABLISHED>_0164c92f;
        if ((*(uint *)(lVar7 + 0x8c48) < 0xb) &&
           ((0x7f0U >> (*(uint *)(lVar7 + 0x8c48) & 0x1f) & 1) != 0)) {
          cVar5 = FUN_00b742d0(lVar7);
          if (cVar5 == '\0') {
            pcVar22 = s_<NO_MEMBERSHIP>_0164c949;
          }
          else {
            pcVar22 = s_<HOST_INDEX_INVALID>_0164c959;
            if (((*(uint *)(lVar7 + 0x64c) >> (*(uint *)(lVar7 + 0x630) & 0x1f) & 1) != 0) &&
               (lVar21 = (long)(int)*(uint *)(lVar7 + 0x630) * 0x168,
               *(int *)(lVar7 + 0x67c + lVar21) != 3)) {
              pcVar22 = (char *)(lVar7 + 0x690 + lVar21);
            }
          }
        }
        FUN_01008290(local_1a0,s_world_controller_activity_manage_0164bd10,param_1 + 0x6c8 + lVar16,
                     lVar8,pcVar22);
        FUN_000e4aa0(DAT_026c9b3c,local_1a0);
      }
      _DAT_026c9b38 = FUN_000697a0();
    }
  }
  else {
    *puVar1 = 0x17;
  }
LAB_00762874:
  if (*DAT_01a1f100 != local_60) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

