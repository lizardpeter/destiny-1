
void FUN_0056e580(undefined8 *param_1,undefined8 *param_2,undefined8 param_3,int param_4,
                 undefined8 param_5,int param_6)

{
  undefined1 auVar1 [16];
  undefined1 auVar2 [16];
  undefined1 auVar3 [16];
  undefined1 auVar4 [16];
  undefined1 auVar5 [16];
  undefined1 auVar6 [16];
  undefined1 auVar7 [16];
  undefined1 auVar8 [16];
  undefined1 auVar9 [16];
  undefined1 auVar10 [16];
  undefined1 auVar11 [16];
  undefined1 auVar12 [16];
  undefined1 auVar13 [16];
  byte bVar14;
  char cVar15;
  char cVar16;
  undefined1 uVar17;
  short sVar18;
  undefined4 uVar19;
  long lVar20;
  long *plVar21;
  int *piVar22;
  undefined8 uVar23;
  undefined8 uVar24;
  undefined8 uVar25;
  long *plVar26;
  long *plVar27;
  long lVar28;
  long lVar29;
  uint uVar30;
  long lVar31;
  ushort uVar32;
  char *pcVar33;
  undefined8 *puVar34;
  short *psVar35;
  ulong uVar36;
  undefined8 *puVar37;
  bool bVar38;
  short *psVar39;
  int iVar40;
  byte *pbVar41;
  int iVar42;
  int *piVar43;
  bool bVar44;
  undefined1 auVar45 [16];
  undefined1 local_240 [16];
  undefined1 local_230 [16];
  long local_220;
  undefined8 *local_218;
  long local_210;
  undefined8 local_208;
  ulong local_200;
  int local_1f8;
  undefined4 uStack_1f4;
  undefined8 local_1f0;
  undefined8 local_178;
  undefined8 local_170;
  int local_168;
  undefined4 uStack_164;
  undefined8 local_160;
  long local_38;
  
  auVar9._8_8_ = local_230._8_8_;
  auVar9._0_8_ = local_230._0_8_;
  auVar8._8_8_ = local_230._8_8_;
  auVar8._0_8_ = local_230._0_8_;
  auVar7._8_8_ = local_230._8_8_;
  auVar7._0_8_ = local_230._0_8_;
  auVar6._8_8_ = local_230._8_8_;
  auVar6._0_8_ = local_230._0_8_;
  auVar1._8_8_ = local_240._8_8_;
  auVar1._0_8_ = local_240._0_8_;
  auVar45._8_8_ = local_240._8_8_;
  auVar45._0_8_ = local_240._0_8_;
  local_38 = *DAT_01a1f100;
  local_240 = auVar1;
  if (param_4 != 4) {
    if (param_4 == 2) {
      if (param_6 == 1) {
        if ((*(short *)((long)param_1 + 10) != *(short *)((long)param_2 + 10)) ||
           (local_230 = auVar6, *(short *)(param_1 + 1) != *(short *)(param_2 + 1))) {
          lVar20 = FUN_00021860(&DAT_026bc820);
          if (lVar20 != 0) {
            FUN_00590960(lVar20);
          }
        }
      }
      else {
        local_230 = auVar7;
        if (param_6 == 0) {
          uVar23 = FUN_00078970(&DAT_026bc820);
          FUN_0058e550(uVar23,1);
        }
      }
    }
    else if ((param_4 == 0) && (local_230 = auVar8, param_6 == 1)) {
      lVar20 = FUN_00078970(&DAT_026bc2b8);
      if (lVar20 != 0) {
        FUN_00577b20(lVar20,*param_2);
      }
    }
    goto switchD_0056e632_caseD_2;
  }
  local_230 = auVar9;
  switch(param_6) {
  case 0:
    lVar20 = 0;
    local_240 = auVar45;
    if ((param_1[0xd] != 0) && (lVar20 = param_1[0xd], local_240 = auVar1, param_2[0xd] != 0)) {
      uVar24 = FUN_005494c0();
      puVar37 = (undefined8 *)FUN_0028bbd0();
      uVar23 = *puVar37;
      if (0 < (int)uVar23) {
        bVar44 = false;
        lVar20 = 0;
        do {
          if ((*(char *)((long)param_1 + lVar20 + 0x383c) != '\x02') &&
             (*(char *)((long)param_2 + lVar20 + 0x383c) == '\x02')) {
            auVar45 = FUN_0054cdb0(uVar24,*(undefined2 *)
                                           ((long)puVar37 + lVar20 * 8 + puVar37[1] + 0x1c));
            local_240 = auVar45;
            FUN_00ac1780(local_240);
            bVar44 = true;
            uVar23 = *puVar37;
          }
          lVar20 = lVar20 + 1;
        } while ((int)lVar20 < (int)uVar23);
        if (bVar44) {
          lVar20 = FUN_00557c40(&DAT_026bc390);
          *(undefined1 *)(lVar20 + 0x40c) = 1;
        }
      }
      lVar20 = 0;
      do {
        if ((*(short *)((long)param_2 + lVar20 + 0x3058) != -1) &&
           ((*(short *)((long)param_1 + lVar20 + 0x3058) == -1 ||
            (*(int *)((long)param_1 + lVar20 + 0x304c) < *(int *)((long)param_2 + lVar20 + 0x304c)))
           )) {
          FUN_0056fad0((long)param_1 + lVar20 + 0x304c,(long)param_2 + lVar20 + 0x304c,0);
          uVar23 = FUN_00557c40(&DAT_026bc038);
          FUN_005747b0(uVar23,*(undefined2 *)((long)param_2 + lVar20 + 0x3058),
                       *(undefined4 *)((long)param_2 + lVar20 + 0x304c));
        }
        lVar20 = lVar20 + 0x10;
      } while ((int)lVar20 != 0x7f0);
      bVar44 = false;
      psVar39 = (short *)(param_1 + 0x99);
      psVar35 = (short *)(param_2 + 0x99);
      iVar42 = 0;
      do {
        if ((*psVar39 == *psVar35) && (*(long *)(psVar39 + 4) == *(long *)(psVar35 + 4))) {
          if (*(int *)(psVar39 + 8) < *(int *)(psVar35 + 8)) {
            local_160 = *(undefined8 *)(psVar35 + 0xc);
            local_178 = *(undefined8 *)psVar35;
            local_170 = *(undefined8 *)(psVar35 + 4);
            uStack_164 = (undefined4)((ulong)*(undefined8 *)(psVar35 + 8) >> 0x20);
            _local_168 = CONCAT44(uStack_164,*(int *)(psVar35 + 8) - *(int *)(psVar39 + 8));
            FUN_00ac0e90(&local_178,1,iVar42);
            sVar18 = 0;
            pcVar33 = (char *)((long)param_2 + 0x2d94);
            do {
              if (((*(int *)(pcVar33 + -4) == *(int *)(psVar35 + 10)) && (*pcVar33 != '\0')) &&
                 (*pcVar33 != '\x06')) {
                uVar23 = FUN_00557c40(&DAT_026bc038);
                FUN_00574620(uVar23,&local_178,1);
                break;
              }
              sVar18 = sVar18 + 1;
              pcVar33 = pcVar33 + 0xc;
            } while (sVar18 < 0x10);
          }
          else if (*(int *)(psVar35 + 8) < *(int *)(psVar39 + 8)) {
            local_1f0 = *(undefined8 *)(psVar35 + 0xc);
            local_208 = *(undefined8 *)psVar35;
            local_200 = *(ulong *)(psVar35 + 4);
            uStack_1f4 = (undefined4)((ulong)*(undefined8 *)(psVar35 + 8) >> 0x20);
            _local_1f8 = CONCAT44(uStack_1f4,*(int *)(psVar39 + 8) - *(int *)(psVar35 + 8));
            FUN_00aa04e0(&local_208);
          }
        }
        else {
          if (*psVar39 != -1) {
            FUN_00aa04e0(psVar39);
            sVar18 = 0;
            pcVar33 = (char *)((long)param_2 + 0x2d94);
            do {
              if ((*(int *)(pcVar33 + -4) == *(int *)(psVar39 + 10)) && (*pcVar33 == '\n')) {
                FUN_00ac1800(psVar39,1);
                bVar44 = true;
                break;
              }
              sVar18 = sVar18 + 1;
              pcVar33 = pcVar33 + 0xc;
              bVar44 = true;
            } while (sVar18 < 0x10);
          }
          if (*psVar35 != -1) {
            FUN_00ac0e90(psVar35,1,iVar42);
            FUN_00ac0f50(psVar35,1,iVar42);
            sVar18 = 0;
            pbVar41 = (byte *)((long)param_2 + 0x2d95);
            do {
              if (((*(int *)(pbVar41 + -5) == *(int *)(psVar35 + 10)) && (pbVar41[-1] != 0)) &&
                 (pbVar41[-1] != 6)) {
                uVar23 = FUN_00557c40(&DAT_026bc038);
                FUN_00574620(uVar23,psVar35,1);
                bVar44 = true;
                if ((*pbVar41 & 1) != 0) {
                  FUN_00aa04e0(*psVar35);
                }
                break;
              }
              sVar18 = sVar18 + 1;
              pbVar41 = pbVar41 + 0xc;
              bVar44 = true;
            } while (sVar18 < 0x10);
          }
        }
        if (*(int *)(psVar39 + 0xc) != *(int *)(psVar35 + 0xc)) {
          FUN_00ac1080(psVar39,psVar35,iVar42);
        }
        psVar39 = psVar39 + 0x10;
        if (psVar39 == (short *)(param_1 + 0x5b1)) break;
        psVar35 = psVar35 + 0x10;
        iVar42 = iVar42 + 1;
      } while (psVar35 != (short *)(param_2 + 0x5b1));
      if (bVar44) {
        lVar20 = FUN_00557c40(&DAT_026bc390);
        *(undefined1 *)(lVar20 + 0x40c) = 1;
      }
      if (*(int *)(param_2 + 0xeb7) != *(int *)(param_1 + 0xeb7)) {
        cVar15 = FUN_0075c1d0();
        if (cVar15 != '\0') {
          lVar20 = FUN_0075d560(0,0);
          if (lVar20 != 0) {
            FUN_0029bba0(lVar20);
          }
        }
      }
      uVar23 = FUN_00021860(&DAT_026bc820);
      FUN_00590950(uVar23);
      lVar20 = param_1[0xd];
    }
    if (lVar20 != param_2[0xd]) {
      FUN_0057e060();
    }
    if (*(int *)((long)param_1 + 0x563c) != *(int *)((long)param_2 + 0x563c)) {
      FUN_0059deb0(0);
      if (*(char *)(param_2 + 0xac8) == '\x04') {
        FUN_0059dda0();
      }
      plVar21 = (long *)FUN_0025a550();
      piVar22 = (int *)(**(code **)(*plVar21 + 400))(plVar21);
      if (0 < *piVar22) {
        sVar18 = 0;
        do {
          uVar36 = (ulong)sVar18;
          if (*(uint *)((long)param_1 + uVar36 * 4 + 0x5644) <
              *(uint *)((long)param_2 + uVar36 * 4 + 0x5644)) {
            plVar21 = (long *)FUN_0025a550();
            lVar20 = (**(code **)(*plVar21 + 0x448))(plVar21,uVar36 & 0xffffffff);
            if (lVar20 != 0) {
              cVar15 = FUN_00272240(*(undefined2 *)(lVar20 + 0x18));
              if (cVar15 != '\0') {
                FUN_00ac1050(*(undefined2 *)(lVar20 + 0x18),
                             *(int *)(lVar20 + 0x14) *
                             (*(int *)((long)param_2 + uVar36 * 4 + 0x5644) -
                             *(int *)((long)param_1 + uVar36 * 4 + 0x5644)));
              }
            }
          }
          sVar18 = sVar18 + 1;
        } while ((int)sVar18 < *piVar22);
      }
    }
    break;
  case 1:
    uVar23 = FUN_00557c40(&DAT_026bc508);
    uVar23 = FUN_00586750(uVar23,*param_2);
    uVar24 = FUN_00557c40(&DAT_026bc038);
    uVar36 = 0;
    do {
      if (param_1[uVar36 + 0x570] != param_2[uVar36 + 0x570]) {
        if (param_2[uVar36 + 0x570] != 0) {
          FUN_005745f0(uVar24,uVar36 & 0xffffffff);
        }
        lVar20 = FUN_007af680();
        *(undefined1 *)(lVar20 + 0xb748) = 1;
        uVar25 = FUN_007af680();
        FUN_007b24b0(uVar25);
      }
      uVar36 = uVar36 + 1;
    } while ((char)uVar36 != '\x14');
    bVar44 = false;
    psVar39 = (short *)(param_1 + 7);
    psVar35 = (short *)(param_2 + 7);
    iVar42 = 0;
    do {
      if ((*psVar39 == *psVar35) && (*(long *)(psVar39 + 4) == *(long *)(psVar35 + 4))) {
        if (*(int *)(psVar39 + 8) < *(int *)(psVar35 + 8)) {
          local_160 = *(undefined8 *)(psVar35 + 0xc);
          local_178 = *(undefined8 *)psVar35;
          local_170 = *(undefined8 *)(psVar35 + 4);
          uStack_164 = (undefined4)((ulong)*(undefined8 *)(psVar35 + 8) >> 0x20);
          _local_168 = CONCAT44(uStack_164,*(int *)(psVar35 + 8) - *(int *)(psVar39 + 8));
          FUN_00ac0e90(&local_178,0,iVar42);
          sVar18 = 0;
          pcVar33 = (char *)((long)param_2 + 0x2ac4);
          do {
            if (((*(int *)(pcVar33 + -4) == *(int *)(psVar35 + 10)) && (*pcVar33 != '\0')) &&
               (*pcVar33 != '\x06')) {
              uVar24 = FUN_00557c40(&DAT_026bc038);
              FUN_00574620(uVar24,&local_178,0);
              break;
            }
            sVar18 = sVar18 + 1;
            pcVar33 = pcVar33 + 0xc;
          } while (sVar18 < 0x10);
        }
        else if (*(int *)(psVar35 + 8) < *(int *)(psVar39 + 8)) {
          local_1f0 = *(undefined8 *)(psVar35 + 0xc);
          local_208 = *(undefined8 *)psVar35;
          local_200 = *(ulong *)(psVar35 + 4);
          uStack_1f4 = (undefined4)((ulong)*(undefined8 *)(psVar35 + 8) >> 0x20);
          _local_1f8 = CONCAT44(uStack_1f4,*(int *)(psVar39 + 8) - *(int *)(psVar35 + 8));
          FUN_00aa04e0(&local_208);
        }
      }
      else {
        if (*psVar39 != -1) {
          FUN_00aa04e0(psVar39);
          sVar18 = 0;
          pcVar33 = (char *)((long)param_2 + 0x2ac4);
          do {
            if ((*(int *)(pcVar33 + -4) == *(int *)(psVar39 + 10)) && (*pcVar33 == '\n')) {
              FUN_00ac1800(psVar39,1);
              bVar44 = true;
              break;
            }
            sVar18 = sVar18 + 1;
            pcVar33 = pcVar33 + 0xc;
            bVar44 = true;
          } while (sVar18 < 0x10);
        }
        if (*psVar35 != -1) {
          FUN_00ac0e90(psVar35,0,iVar42);
          FUN_00ac0f50(psVar35,0,iVar42);
          sVar18 = 0;
          pbVar41 = (byte *)((long)param_2 + 0x2ac5);
          do {
            if (((*(int *)(pbVar41 + -5) == *(int *)(psVar35 + 10)) && (pbVar41[-1] != 0)) &&
               (pbVar41[-1] != 6)) {
              uVar24 = FUN_00557c40(&DAT_026bc038);
              FUN_00574620(uVar24,psVar35,0);
              bVar44 = true;
              if ((*pbVar41 & 1) != 0) {
                FUN_00aa04e0(*psVar35);
              }
              break;
            }
            sVar18 = sVar18 + 1;
            pbVar41 = pbVar41 + 0xc;
            bVar44 = true;
          } while (sVar18 < 0x10);
        }
      }
      if (*(int *)(psVar39 + 0xc) != *(int *)(psVar35 + 0xc)) {
        FUN_00ac1080(psVar39,psVar35,iVar42);
      }
      psVar39 = psVar39 + 0x10;
      if (psVar39 == (short *)(param_1 + 0x557)) break;
      psVar35 = psVar35 + 0x10;
      iVar42 = iVar42 + 1;
    } while (psVar35 != (short *)(param_2 + 0x557));
    if (bVar44) {
      lVar20 = FUN_00557c40(&DAT_026bc390);
      *(undefined1 *)(lVar20 + 0x40c) = 1;
    }
    psVar39 = (short *)((long)param_1 + 0x2abc);
    psVar35 = (short *)((long)param_2 + 0x2abc);
    do {
      if ((*psVar39 != *psVar35) && ((*(byte *)((long)psVar35 + 9) & 2) != 0)) {
        iVar42 = -1;
        plVar21 = param_2 + 4;
        do {
          iVar42 = iVar42 + 1;
          if (0x153 < iVar42) goto LAB_0056ef67;
          piVar22 = (int *)((long)plVar21 + 0x2c);
          plVar21 = plVar21 + 4;
        } while (*piVar22 != *(int *)(psVar35 + 2));
        if (*plVar21 != 0) {
          FUN_00ac1720(plVar21);
          lVar20 = *plVar21;
          uVar19 = FUN_0052bb90();
          FUN_0091a260(lVar20,uVar19);
        }
      }
LAB_0056ef67:
      psVar39 = psVar39 + 6;
    } while ((psVar39 != (short *)((long)param_1 + 0x2b7c)) &&
            (psVar35 = psVar35 + 6, psVar35 != (short *)((long)param_2 + 0x2b7c)));
    iVar42 = *(int *)(param_1 + 0x6cc);
    if ((iVar42 == *(int *)(param_2 + 0x6cc)) && (0 < iVar42)) {
      piVar43 = (int *)((long)param_1 + 0x3664);
      piVar22 = (int *)((long)param_2 + 0x3664);
      iVar40 = 0;
      do {
        if (*piVar43 < *piVar22) {
          FUN_0056fad0(piVar43,piVar22,0);
          uVar24 = FUN_00557c40(&DAT_026bc038);
          FUN_005747b0(uVar24,(short)piVar22[3],*piVar22);
          iVar42 = *(int *)(param_1 + 0x6cc);
        }
        piVar43 = piVar43 + 4;
        piVar22 = piVar22 + 4;
        iVar40 = iVar40 + 1;
      } while (iVar40 < iVar42);
    }
    uVar25 = FUN_005494c0();
    puVar37 = (undefined8 *)FUN_0028bc00();
    uVar24 = *puVar37;
    if (0 < (int)uVar24) {
      bVar44 = false;
      lVar20 = 0;
      do {
        if ((*(char *)((long)param_1 + lVar20 + 0x53c0) != '\x02') &&
           (*(char *)((long)param_2 + lVar20 + 0x53c0) == '\x02')) {
          auVar45 = FUN_0054cdb0(uVar25,*(undefined2 *)
                                         ((long)puVar37 + lVar20 * 8 + puVar37[1] + 0x1c));
          local_230 = auVar45;
          FUN_00ac1780(local_230);
          bVar44 = true;
          uVar24 = *puVar37;
        }
        lVar20 = lVar20 + 1;
      } while ((int)lVar20 < (int)uVar24);
      if (bVar44) {
        lVar20 = FUN_00557c40(&DAT_026bc390);
        *(undefined1 *)(lVar20 + 0x40c) = 1;
      }
    }
    lVar20 = 0;
    bVar44 = false;
    do {
      bVar38 = bVar44;
      lVar28 = (long)param_2 + lVar20 + 0x3ea8;
      bVar14 = FUN_00271080((long)param_1 + lVar20 + 0x3ea8,lVar28);
      if ((*(short *)((long)param_2 + lVar20 + 0x3e98) != -1) && (bVar14 == 0)) {
        uVar24 = FUN_00078970(&DAT_026bc380);
        FUN_0057be00(uVar24,lVar28);
      }
      lVar20 = lVar20 + 0x38;
      bVar44 = bVar38 || (bVar14 ^ 1) != 0;
    } while ((int)lVar20 != 0xe00);
    if (bVar38 || (bVar14 ^ 1) != 0) {
      FUN_0058a3a0();
    }
    cVar15 = FUN_00271080(param_1 + 0xa76,param_2 + 0xa76);
    if (cVar15 == '\0') {
      uVar24 = FUN_00078970(&DAT_026bc380);
      FUN_0057be00(uVar24,param_2 + 0xa76);
    }
    sVar18 = *(short *)(param_2 + 0x584);
    if (*(short *)(param_1 + 0x584) != sVar18) {
      uVar24 = FUN_00557c40(&DAT_026bc038);
      if (sVar18 == -1) {
        FUN_005745e0();
      }
      else {
        FUN_00574470(uVar24,param_2 + 0x584);
      }
    }
    if ((*(char *)(param_2 + 0x587) != '\0') && (*(char *)(param_1 + 0x587) == '\0')) {
      sVar18 = *(short *)(param_2 + 0x584);
      iVar42 = (int)sVar18;
      if (iVar42 != -1) {
        lVar20 = FUN_00775770(0);
        uVar24 = FUN_005494c0();
        auVar45 = FUN_005498e0(uVar24,iVar42);
        if (*(int *)(auVar45._8_8_ + 0x18) != -0x7ee3623b) goto LAB_0056f8c4;
        if (lVar20 == 0) {
LAB_0056f5dc:
          cVar15 = FUN_000e4d70(8,4);
          if (cVar15 != '\0') {
            if (DAT_026bada8 == '\0') {
              iVar40 = thunk_FUN_012aa7d6(&DAT_026bada8);
              if (iVar40 != 0) {
                DAT_026bada0 = FUN_000e4a10(s__world_controller_investment_act_0163cd3f + 1);
                thunk_FUN_012aa7e6(&DAT_026bada8);
              }
            }
            FUN_01008290(&local_178,s__world_controller_investment_act_0163cd3f + 1,iVar42);
            uVar19 = DAT_026bada0;
LAB_0056f7b4:
            FUN_000e4aa0(uVar19,&local_178);
          }
        }
        else {
          lVar20 = lVar20 + 0x9b8;
          cVar15 = FUN_00b8f690(lVar20);
          if (cVar15 == '\0') goto LAB_0056f5dc;
          lVar28 = FUN_011c3f80(lVar20);
          if (*(short *)(lVar28 + 2) != sVar18) {
            cVar15 = FUN_000e4d70(8,4);
            if (cVar15 == '\0') goto LAB_0056f8c4;
            if (DAT_026badb8 == '\0') {
              iVar40 = thunk_FUN_012aa7d6(&DAT_026badb8);
              if (iVar40 != 0) {
                DAT_026badb0 = FUN_000e4a10(s_world_controller_investment_acti_0163cdd7);
                thunk_FUN_012aa7e6(&DAT_026badb8);
              }
            }
            lVar20 = FUN_011c3f80(lVar20);
            FUN_01008290(&local_178,s_world_controller_investment_acti_0163cdd7,iVar42,
                         (int)*(short *)(lVar20 + 2));
            uVar19 = DAT_026badb0;
            goto LAB_0056f7b4;
          }
          lVar20 = *(long *)(auVar45._0_8_ + 0x98);
          if (lVar20 == 0) {
            cVar15 = FUN_000e4d70(8,2);
            if (cVar15 != '\0') {
              if (DAT_026bade8 == '\0') {
                iVar40 = thunk_FUN_012aa7d6(&DAT_026bade8);
                if (iVar40 != 0) {
                  DAT_026bade0 = FUN_000e4a10(s_world_controller_investment_acti_0163cf7f);
                  thunk_FUN_012aa7e6(&DAT_026bade8);
                }
              }
              FUN_01008290(&local_178,s_world_controller_investment_acti_0163cf7f,iVar42);
              uVar19 = DAT_026bade0;
              goto LAB_0056f7b4;
            }
          }
          else {
            lVar28 = FUN_005753c0(4);
            lVar20 = lVar20 + auVar45._0_8_ + 0x98;
            cVar15 = FUN_0028eba0(lVar20);
            if (cVar15 != '\0') {
              cVar15 = FUN_0028e530(lVar28,lVar20);
              if (cVar15 == '\0') {
                cVar15 = FUN_000e4d70(8,3);
                if (cVar15 != '\0') {
                  if (DAT_026badc8 == '\0') {
                    iVar40 = thunk_FUN_012aa7d6(&DAT_026badc8);
                    if (iVar40 != 0) {
                      DAT_026badc0 = FUN_000e4a10(s_world_controller_investment_acti_0163ce66);
                      thunk_FUN_012aa7e6(&DAT_026badc8);
                    }
                  }
                  FUN_01008290(&local_178,s_world_controller_investment_acti_0163ce66,iVar42);
                  uVar19 = DAT_026badc0;
                  goto LAB_0056f7b4;
                }
                goto LAB_0056f8c4;
              }
            }
            local_200 = local_200 & 0xffffffff00000000;
            lVar29 = *(long *)(PTR_DAT_0197e288 + 8);
            uVar24 = FUN_000e8680(lVar29,0,0xffffffff);
            thunk_FUN_012aa986(&local_208,0,uVar24);
            uVar32 = *(ushort *)(lVar29 + 0x1c) & 0x78;
            bVar44 = uVar32 != 0;
            if (uVar32 == 0) {
              uVar30 = *(uint *)(lVar29 + 0x20);
              if ((*(ushort *)(lVar29 + 0x1c) & 0x40) != 0) {
                lVar31 = FUN_000e8a90(lVar29,&local_208);
                if (lVar31 == 0) {
                  uVar30 = uVar30 | 0x5488bf;
                }
                else {
                  uVar30 = *(uint *)(lVar31 + 0x20) & 0x5488bf | uVar30;
                }
              }
              bVar44 = (uVar30 & 0xc08070) != 0;
            }
            if (bVar44) {
              FUN_000e6730(lVar29,&local_208,0,0xffffffff,0);
            }
            local_208._0_5_ = CONCAT14(0xff,(undefined4)local_208);
            uVar24 = local_208;
            local_208 = CONCAT71(local_208._1_7_,*(undefined1 *)(lVar20 + 0x10));
            uVar25 = local_208;
            local_208._4_4_ = SUB84(uVar24,4);
            local_208._0_4_ = CONCAT22(*(undefined2 *)(lVar20 + 0x12),(short)uVar25);
            if (lVar28 != 0) {
              cVar15 = FUN_0026b6d0(lVar28);
              if (cVar15 != '\0') {
                uVar17 = FUN_0026b7f0(lVar28,local_208._2_2_);
                local_208._0_5_ = CONCAT14(uVar17,(undefined4)local_208);
              }
            }
            cVar15 = FUN_000e4d70(8,3);
            if (cVar15 != '\0') {
              if (DAT_026badd8 == '\0') {
                iVar40 = thunk_FUN_012aa7d6(&DAT_026badd8);
                if (iVar40 != 0) {
                  DAT_026badd0 = FUN_000e4a10(s_world_controller_investment_acti_0163cf0f);
                  thunk_FUN_012aa7e6(&DAT_026badd8);
                }
              }
              FUN_01008290(&local_178,s_world_controller_investment_acti_0163cf0f,iVar42,
                           (int)local_208._2_2_);
              FUN_000e4aa0(DAT_026badd0,&local_178);
            }
            uVar24 = FUN_00574ef0();
            FUN_00574dc0(uVar24,&local_208);
          }
        }
LAB_0056f8c4:
        uVar24 = FUN_00557c40(&DAT_026bc038);
        FUN_005745e0(uVar24);
      }
    }
    lVar20 = FUN_00078970(&DAT_026bc2b8);
    if (lVar20 != 0) {
      FUN_00577ab0(lVar20,*param_2);
    }
    FUN_002f1dc0(uVar23);
    uVar23 = FUN_00021860(&DAT_026bc820);
    FUN_00590950(uVar23);
    break;
  case 3:
    FUN_0056fad0(param_1 + 7,param_2 + 7,param_2);
    if (param_2 != param_1) {
      lVar20 = FUN_00557c40(&DAT_026bc390);
      *(undefined1 *)(lVar20 + 0x40c) = 1;
      uVar23 = FUN_005494c0();
      auVar45 = FUN_0054b1b0(uVar23,*(undefined2 *)((long)param_1 + 0x24));
      auVar13._8_8_ = local_230._8_8_;
      auVar13._0_8_ = local_230._0_8_;
      auVar12._8_8_ = local_230._8_8_;
      auVar12._0_8_ = local_230._0_8_;
      auVar11._8_8_ = local_230._8_8_;
      auVar11._0_8_ = local_230._0_8_;
      auVar5._8_8_ = local_240._8_8_;
      auVar5._0_8_ = local_240._0_8_;
      auVar4._8_8_ = local_240._8_8_;
      auVar4._0_8_ = local_240._0_8_;
      auVar3._8_8_ = local_240._8_8_;
      auVar3._0_8_ = local_240._0_8_;
      lVar20 = auVar45._0_8_;
      if ((((lVar20 != 0) && (local_240 = auVar3, local_230 = auVar11, auVar45._8_8_ != 0)) &&
          (local_240 = auVar4, local_230 = auVar12, *(long *)(lVar20 + 0x20) != 0)) &&
         (plVar21 = (long *)(*(long *)(lVar20 + 0x20) + lVar20 + 0x20), local_240 = auVar5,
         local_230 = auVar13, plVar21 != (long *)0x0)) {
        plVar26 = (long *)FUN_005753c0(4);
        cVar15 = FUN_0026e1c0(plVar26,lVar20,param_2);
        if ((cVar15 == '\0') || (cVar15 = FUN_0026e1c0(plVar26,lVar20,param_1), cVar15 != '\0')) {
          if (0 < *plVar21) {
            lVar29 = 0;
            lVar28 = lVar20;
            do {
              uVar36 = CONCAT62((int6)((ulong)lVar28 >> 0x10),
                                *(undefined2 *)
                                 ((long)(plVar21 + 1) + lVar29 * 2 + plVar21[1] + 0x10));
              plVar27 = (long *)FUN_0025a550();
              lVar28 = (**(code **)(*plVar27 + 0x430))(plVar27,uVar36 & 0xffffffff);
              if (lVar28 != 0) {
                cVar15 = FUN_00270040(plVar26,lVar28,lVar20,param_1);
                cVar16 = FUN_00270040(plVar26,lVar28,lVar20,param_2);
                if ((cVar15 == '\0') && (cVar16 == '\x01')) {
                  FUN_00aa04e0(*(undefined2 *)((long)param_2 + 0x24),uVar36 & 0xffffffff);
                }
              }
              lVar29 = lVar29 + 1;
            } while (lVar29 < *plVar21);
          }
        }
        else {
          uVar23 = (**(code **)(*plVar26 + 0x10))(plVar26);
          uVar23 = FUN_0026de00(uVar23,param_2);
          FUN_00ac1800(uVar23,0);
        }
      }
    }
    break;
  case 4:
    uVar23 = FUN_00557c40(&DAT_026bc508);
    local_210 = FUN_005863c0(uVar23);
    lVar20 = FUN_00557c40(&DAT_026bc810);
    auVar10._8_8_ = local_230._8_8_;
    auVar10._0_8_ = local_230._0_8_;
    auVar2._8_8_ = local_240._8_8_;
    auVar2._0_8_ = local_240._0_8_;
    if ((lVar20 != 0) && (local_178 = 0, local_240 = auVar2, local_230 = auVar10, local_210 != 0)) {
      lVar28 = FUN_00266e70(param_1);
      lVar29 = FUN_00266e70(param_2);
      puVar34 = (undefined8 *)0x0;
      puVar37 = (undefined8 *)0x0;
      lVar31 = 0;
      if (lVar28 != 0) {
        lVar31 = (long)*(short *)(lVar28 + 0x12) - (long)*(short *)(lVar28 + 0x10);
        puVar37 = param_1 + (long)*(short *)(lVar28 + 0x10) * 2 + 1;
      }
      lVar28 = 0;
      if (lVar29 != 0) {
        lVar28 = (long)*(short *)(lVar29 + 0x12) - (long)*(short *)(lVar29 + 0x10);
        puVar34 = param_2 + (long)*(short *)(lVar29 + 0x10) * 2 + 1;
      }
      if (((int)lVar31 != 0) || ((int)lVar28 != 0)) {
        local_220 = lVar28;
        local_218 = puVar34;
        FUN_0058cb50(lVar20,&local_210,1,lVar31,puVar37);
      }
    }
  }
switchD_0056e632_caseD_2:
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

