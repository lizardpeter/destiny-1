
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

bool FUN_0078fef0(byte *param_1,int *param_2)

{
  long lVar1;
  byte *pbVar2;
  byte *pbVar3;
  byte bVar4;
  short sVar5;
  bool bVar6;
  bool bVar7;
  char cVar8;
  char cVar9;
  char cVar10;
  char cVar11;
  undefined1 uVar12;
  int iVar13;
  int iVar14;
  int iVar15;
  long lVar16;
  long lVar17;
  undefined8 uVar18;
  undefined8 uVar19;
  long lVar20;
  long lVar21;
  long lVar22;
  undefined *puVar23;
  undefined *puVar24;
  int *piVar25;
  undefined4 uVar26;
  uint uVar27;
  undefined *puVar28;
  uint uVar29;
  char *pcVar30;
  undefined1 auVar31 [16];
  undefined4 local_adc;
  undefined4 local_ad8 [2];
  undefined4 local_ad0 [2];
  uint local_ac8 [2];
  uint local_ac0 [2];
  undefined1 local_ab8 [64];
  undefined1 local_a78 [256];
  undefined1 local_978 [2];
  short local_976;
  char local_974;
  undefined4 local_970;
  undefined1 local_578 [1024];
  undefined1 local_178 [320];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  iVar13 = FUN_007850a0();
  lVar16 = FUN_0034e5c0();
  lVar16 = *(long *)(lVar16 + 0xb0);
  lVar17 = FUN_001db3c0();
  if (param_1[0x21] == 0) {
    lVar1 = lVar17 + lVar16;
    pbVar2 = param_1 + 0x18;
    pbVar3 = param_1 + 8;
LAB_0079011f:
    FUN_00788e10(0x13);
    bVar4 = *param_1;
    uVar29 = (uint)(char)bVar4;
    iVar15 = -1;
    if (uVar29 - 0xb < 6) {
      iVar15 = *(int *)(&DAT_015cf730 + (long)(int)(uVar29 - 0xb) * 4);
    }
    if (iVar13 <= iVar15) {
      cVar8 = FUN_000e4d70(5,3);
      bVar6 = false;
      bVar7 = true;
      if (cVar8 != '\0') {
        if ((DAT_026cf808 == '\0') && (iVar14 = thunk_FUN_012aa7d6(&DAT_026cf808), iVar14 != 0)) {
          DAT_026cf800 = FUN_000e4a10(s_world_controller_state_manager_p_01659762);
          thunk_FUN_012aa7e6(&DAT_026cf808);
        }
        uVar18 = FUN_00783940(iVar13);
        uVar19 = FUN_00783940(iVar15);
        pcVar30 = s_INVALID_0162318f;
        if (bVar4 < 0x13) {
          pcVar30 = (&PTR_DAT_01945910)[uVar29];
        }
        bVar6 = false;
        FUN_01008290(local_578,s_world_controller_state_manager_p_01659762,uVar18,uVar19,pcVar30);
        uVar26 = DAT_026cf800;
        bVar7 = true;
LAB_007902bb:
        FUN_000e4aa0(uVar26,local_578);
      }
      goto LAB_007916d5;
    }
    bVar6 = false;
    switch((ulong)uVar29) {
    case 0:
      cVar8 = FUN_000e4d70(5,3);
      bVar7 = true;
      if (cVar8 != '\0') {
        if ((DAT_026cf588 == '\0') && (iVar15 = thunk_FUN_012aa7d6(&DAT_026cf588), iVar15 != 0)) {
          DAT_026cf580 = FUN_000e4a10(s_world_controller_state_manager_p_016583fe);
          thunk_FUN_012aa7e6(&DAT_026cf588);
        }
        uVar18 = FUN_00783960((int)*(short *)(param_1 + 2));
        bVar6 = false;
        FUN_01008290(local_578,s_world_controller_state_manager_p_016583fe,uVar18);
        uVar26 = DAT_026cf580;
        bVar7 = true;
        goto LAB_007902bb;
      }
      bVar6 = false;
      break;
    case 1:
      cVar8 = FUN_0093d460();
      bVar7 = true;
      if (cVar8 == '\0') {
        bVar6 = false;
      }
      else {
        cVar8 = FUN_000e4d70(5,2);
        if (cVar8 != '\0') {
          if ((DAT_026cf598 == '\0') && (iVar15 = thunk_FUN_012aa7d6(&DAT_026cf598), iVar15 != 0)) {
            DAT_026cf590 = FUN_000e4a10(s_world_controller_state_manager_p_01658483);
            thunk_FUN_012aa7e6(&DAT_026cf598);
          }
          FUN_01008290(local_578,s_world_controller_state_manager_p_01658483);
          FUN_000e4aa0(DAT_026cf590,local_578);
        }
        FUN_0093c590(s_starting_soft_kto__private_activ_016584c6);
        bVar6 = false;
      }
      break;
    case 2:
      uVar18 = FUN_003ccc70();
      local_ad0[0] = DAT_026cf500;
      cVar8 = FUN_003cd7f0(uVar18,local_ad0);
      bVar7 = true;
      if (cVar8 == '\0') {
        lVar21 = FUN_0034e5c0();
        lVar21 = *(long *)(lVar21 + 0xc0);
        cVar8 = FUN_000e4d70(5,2);
        if (cVar8 != '\0') {
          if ((DAT_026cf5a8 == '\0') && (iVar15 = thunk_FUN_012aa7d6(&DAT_026cf5a8), iVar15 != 0)) {
            DAT_026cf5a0 = FUN_000e4a10(s_world_controller_state_manager_p_016584f2);
            thunk_FUN_012aa7e6(&DAT_026cf5a8);
          }
          FUN_01008290(local_578,s_world_controller_state_manager_p_016584f2,lVar21);
          FUN_000e4aa0(DAT_026cf5a0,local_578);
        }
        uVar18 = FUN_003ccc70();
        local_ad8[0] = DAT_026cf500;
        auVar31._0_4_ = (float)lVar21 / DAT_01658104;
        auVar31._4_12_ = SUB6012((undefined1  [60])0x0,0);
        FUN_003cd580(auVar31._0_8_,uVar18,local_ad8,&DAT_026cf510);
        bVar6 = false;
      }
      else {
        bVar6 = false;
      }
      break;
    case 3:
      uVar18 = 0;
LAB_00790a05:
      FUN_0077b710(uVar18);
      goto LAB_00790bb4;
    case 4:
      FUN_004e4610();
      goto LAB_00790bb4;
    case 5:
      uVar18 = FUN_003430b0();
      cVar8 = FUN_003455e0(uVar18);
      if (cVar8 != '\0') {
        cVar8 = FUN_007526f0(1);
        if ((cVar8 == '\0') && (cVar8 = FUN_0034d130(), cVar8 == '\0')) {
          cVar8 = FUN_000e4d70(5,3);
          if (cVar8 != '\0') {
            if ((DAT_026cf5b8 == '\0') && (iVar15 = thunk_FUN_012aa7d6(&DAT_026cf5b8), iVar15 != 0))
            {
              DAT_026cf5b0 = FUN_000e4a10(s_world_controller_state_manager_p_01658544);
              thunk_FUN_012aa7e6(&DAT_026cf5b8);
            }
            FUN_01008290(local_578,s_world_controller_state_manager_p_01658544);
            FUN_000e4aa0(DAT_026cf5b0,local_578);
          }
          FUN_00752480();
        }
        else {
          iVar15 = FUN_000697a0();
          if (15000 < (uint)(iVar15 - _DAT_026cf5c0)) {
            cVar8 = FUN_000e4d70(5,2);
            if (cVar8 != '\0') {
              if ((DAT_026cf5c8 == '\0') &&
                 (iVar15 = thunk_FUN_012aa7d6(&DAT_026cf5c8), iVar15 != 0)) {
                DAT_026cf5c4 = FUN_000e4a10(s_world_controller_state_manager_p_01658597);
                thunk_FUN_012aa7e6(&DAT_026cf5c8);
              }
              FUN_00752760(local_a78);
              FUN_01008290(local_578,s_world_controller_state_manager_p_01658597,local_a78);
              FUN_000e4aa0(DAT_026cf5c4,local_578);
            }
            _DAT_026cf5c0 = FUN_000697a0();
          }
        }
        goto switchD_00790173_default;
      }
      cVar8 = FUN_000e4d70(5,3);
      if (cVar8 != '\0') {
        if ((DAT_026cf5d8 == '\0') && (iVar15 = thunk_FUN_012aa7d6(&DAT_026cf5d8), iVar15 != 0)) {
          DAT_026cf5d0 = FUN_000e4a10(s_world_controller_state_manager_p_0165860f);
          thunk_FUN_012aa7e6(&DAT_026cf5d8);
        }
        FUN_01008290(local_578,s_world_controller_state_manager_p_0165860f);
        FUN_000e4aa0(DAT_026cf5d0,local_578);
      }
      FUN_00774700(2);
      FUN_00774780(2);
      goto LAB_00790bb4;
    case 6:
      FUN_0076a630(0);
      goto LAB_00790bb4;
    case 7:
      cVar8 = FUN_0075cb40(0,0,(int)*(short *)(param_1 + 2));
      cVar9 = FUN_0075cb40(1,0,(int)*(short *)(param_1 + 2));
      cVar10 = FUN_0075cb40(1,1,(int)*(short *)(param_1 + 2));
      if (((cVar8 == '\0') || (cVar9 == '\0')) || (bVar7 = true, cVar10 == '\0')) {
        iVar15 = FUN_000697a0();
        if (15000 < (uint)(iVar15 - _DAT_026cf5e0)) {
          cVar11 = FUN_000e4d70(5,2);
          if (cVar11 != '\0') {
            if ((DAT_026cf5e8 == '\0') && (iVar15 = thunk_FUN_012aa7d6(&DAT_026cf5e8), iVar15 != 0))
            {
              DAT_026cf5e4 = FUN_000e4a10(s_world_controller_state_manager_p_01658680);
              thunk_FUN_012aa7e6(&DAT_026cf5e8);
            }
            puVar24 = &DAT_0165796b;
            if (cVar8 != '\0') {
              puVar24 = &DAT_0165796e;
            }
            puVar23 = &DAT_0165796b;
            if (cVar9 != '\0') {
              puVar23 = &DAT_0165796e;
            }
            puVar28 = &DAT_0165796b;
            if (cVar10 != '\0') {
              puVar28 = &DAT_0165796e;
            }
            FUN_01008290(local_578,s_world_controller_state_manager_p_01658680,puVar24,puVar23,
                         puVar28);
            FUN_000e4aa0(DAT_026cf5e4,local_578);
          }
          _DAT_026cf5e0 = FUN_000697a0();
        }
        goto switchD_00790173_default;
      }
      break;
    case 8:
      lVar21 = FUN_00775180(1);
      uVar29 = *(uint *)(lVar21 + 0x8c48);
      if ((uVar29 < 0xb) && ((0x7f0U >> (uVar29 & 0x1f) & 1) != 0)) {
        if (((uVar29 & 0xfffffffe) == 6) || ((uVar29 == 8 || (uVar29 == 9)))) {
          if ((0x500U >> (uVar29 & 0x1f) & 1) == 0) {
            lVar22 = FUN_00775180(1);
            local_ac0[0] = 0;
            if ((*(uint *)(lVar22 + 0x8c48) < 0xb) &&
               ((0x7f0U >> (*(uint *)(lVar22 + 0x8c48) & 0x1f) & 1) != 0)) {
              cVar8 = FUN_00b8f120(lVar22 + 0x6eb8,local_ac0);
              if (cVar8 == '\0') {
                cVar8 = FUN_000e4d70(5,4);
                bVar6 = false;
                iVar15 = -1;
                if (cVar8 != '\0') {
                  if ((DAT_026cf828 == '\0') &&
                     (iVar15 = thunk_FUN_012aa7d6(&DAT_026cf828), iVar15 != 0)) {
                    DAT_026cf820 = FUN_000e4a10(s_world_controller_state_manager_p_01659841);
                    thunk_FUN_012aa7e6(&DAT_026cf828);
                  }
                  uVar18 = FUN_00b6db70(lVar22);
                  FUN_01008290(local_178,s_world_controller_state_manager_p_01659841,uVar18);
                  uVar26 = DAT_026cf820;
                  goto LAB_007906b0;
                }
              }
              else {
                lVar20 = FUN_00b74340(lVar22);
                uVar26 = *(undefined4 *)(lVar20 + 0x5d0c);
                piVar25 = (int *)(lVar20 + 0x5c);
                uVar29 = 0;
                local_ac8[0] = 0;
                do {
                  uVar27 = 1 << ((byte)uVar29 & 0x1f);
                  if (((*(uint *)(lVar20 + 0x2c) >> (uVar29 & 0x1f) & 1) == 0) || (*piVar25 == 3)) {
                    local_ac8[0] = ~uVar27 & local_ac8[0];
                  }
                  else {
                    local_ac8[0] = local_ac8[0] | uVar27;
                  }
                  piVar25 = piVar25 + 0x5a;
                  uVar29 = uVar29 + 1;
                } while (uVar29 != 0x14);
                iVar15 = -1;
                uVar29 = (1 << ((byte)uVar26 & 0x1f) & 0xfffffU ^ 0xfffff) & local_ac8[0] &
                         local_ac0[0];
                if (uVar29 != 0) {
                  do {
                    iVar15 = iVar15 + 1;
                    if (0x13 < iVar15) break;
                  } while ((1 << ((byte)iVar15 & 0x1f) & uVar29) == 0);
                  if (0x13 < iVar15) {
                    iVar15 = -1;
                  }
                }
                iVar14 = FUN_000697a0();
                bVar6 = true;
                if (15000 < (uint)(iVar14 - _DAT_026cf830)) {
                  cVar8 = FUN_000e4d70(5,2);
                  if (cVar8 != '\0') {
                    if ((DAT_026cf838 == '\0') &&
                       (iVar14 = thunk_FUN_012aa7d6(&DAT_026cf838), iVar14 != 0)) {
                      DAT_026cf834 = FUN_000e4a10(s_world_controller_state_manager_p_016598af);
                      thunk_FUN_012aa7e6(&DAT_026cf838);
                    }
                    uVar18 = FUN_00b6db70(lVar22);
                    FUN_01052b80(local_578,local_ac8);
                    FUN_01052b80(local_978,local_ac0);
                    FUN_01008290(local_178,s_world_controller_state_manager_p_016598af,uVar18,iVar15
                                 ,uVar26,local_578,local_978);
                    FUN_000e4aa0(DAT_026cf834,local_178);
                  }
                  bVar6 = true;
                  _DAT_026cf830 = FUN_000697a0();
                }
              }
            }
            else {
              cVar8 = FUN_000e4d70(5,4);
              bVar6 = false;
              iVar15 = -1;
              if (cVar8 != '\0') {
                if ((DAT_026cf818 == '\0') &&
                   (iVar15 = thunk_FUN_012aa7d6(&DAT_026cf818), iVar15 != 0)) {
                  DAT_026cf810 = FUN_000e4a10(s_world_controller_state_manager_p_016597ed);
                  thunk_FUN_012aa7e6(&DAT_026cf818);
                }
                uVar18 = FUN_00b6db70(lVar22);
                FUN_01008290(local_178,s_world_controller_state_manager_p_016597ed,uVar18);
                uVar26 = DAT_026cf810;
LAB_007906b0:
                bVar6 = false;
                iVar15 = -1;
                FUN_000e4aa0(uVar26,local_178);
              }
            }
            if (!bVar6) {
              cVar8 = FUN_000e4d70(5,4);
              if (cVar8 != '\0') {
                if ((DAT_026cf628 == '\0') &&
                   (iVar13 = thunk_FUN_012aa7d6(&DAT_026cf628), iVar13 != 0)) {
                  DAT_026cf620 = FUN_000e4a10(s_world_controller_state_manager_p_01658858);
                  thunk_FUN_012aa7e6(&DAT_026cf628);
                }
                uVar18 = FUN_00b6db70(lVar21);
                FUN_01008290(local_578,s_world_controller_state_manager_p_01658858,uVar18);
                uVar26 = DAT_026cf620;
                goto LAB_00791f38;
              }
              goto LAB_00791f40;
            }
            cVar8 = FUN_000e4d70(5,3);
            if (iVar15 == -1) {
              bVar7 = true;
              if (cVar8 != '\0') {
                if ((DAT_026cf638 == '\0') &&
                   (iVar15 = thunk_FUN_012aa7d6(&DAT_026cf638), iVar15 != 0)) {
                  DAT_026cf630 = FUN_000e4a10(s_world_controller_state_manager_p_016588cb);
                  thunk_FUN_012aa7e6(&DAT_026cf638);
                }
                uVar18 = FUN_00b6db70(lVar21);
                bVar6 = false;
                FUN_01008290(local_578,s_world_controller_state_manager_p_016588cb,uVar18);
                uVar26 = DAT_026cf630;
                bVar7 = true;
                goto LAB_007902bb;
              }
              bVar6 = false;
              break;
            }
            if (cVar8 != '\0') {
              if ((DAT_026cf648 == '\0') &&
                 (iVar14 = thunk_FUN_012aa7d6(&DAT_026cf648), iVar14 != 0)) {
                DAT_026cf640 = FUN_000e4a10(s_world_controller_state_manager_p_01658930);
                thunk_FUN_012aa7e6(&DAT_026cf648);
              }
              uVar18 = FUN_00b6db70(lVar21);
              FUN_01008290(local_578,s_world_controller_state_manager_p_01658930,uVar18,iVar15);
              FUN_000e4aa0(DAT_026cf640,local_578);
            }
            FUN_00b75c30(lVar21,iVar15,2,0);
          }
          else {
            iVar15 = FUN_000697a0();
            if (15000 < (uint)(iVar15 - _DAT_026cf610)) {
              cVar8 = FUN_000e4d70(5,3);
              if (cVar8 != '\0') {
                if ((DAT_026cf618 == '\0') &&
                   (iVar15 = thunk_FUN_012aa7d6(&DAT_026cf618), iVar15 != 0)) {
                  DAT_026cf614 = FUN_000e4a10(s_world_controller_state_manager_p_016587c7);
                  thunk_FUN_012aa7e6(&DAT_026cf618);
                }
                uVar18 = FUN_00b6db70(lVar21);
                uVar19 = FUN_00b79b80(*(undefined4 *)(lVar21 + 0x8c48));
                FUN_01008290(local_578,s_world_controller_state_manager_p_016587c7,uVar18,uVar19);
                FUN_000e4aa0(DAT_026cf614,local_578);
              }
              _DAT_026cf610 = FUN_000697a0();
            }
          }
          goto switchD_00790173_default;
        }
        cVar8 = FUN_000e4d70(5,3);
        bVar7 = true;
        if (cVar8 != '\0') {
          if ((DAT_026cf608 == '\0') && (iVar15 = thunk_FUN_012aa7d6(&DAT_026cf608), iVar15 != 0)) {
            DAT_026cf600 = FUN_000e4a10(s_world_controller_state_manager_p_01658762);
            thunk_FUN_012aa7e6(&DAT_026cf608);
          }
          uVar18 = FUN_00b6db70(lVar21);
          bVar6 = false;
          FUN_01008290(local_578,s_world_controller_state_manager_p_01658762,uVar18);
          uVar26 = DAT_026cf600;
          bVar7 = true;
          goto LAB_007902bb;
        }
        bVar6 = false;
        break;
      }
      cVar8 = FUN_000e4d70(5,4);
      if (cVar8 != '\0') {
        if ((DAT_026cf5f8 == '\0') && (iVar13 = thunk_FUN_012aa7d6(&DAT_026cf5f8), iVar13 != 0)) {
          DAT_026cf5f0 = FUN_000e4a10(s_world_controller_state_manager_p_016586fd);
          thunk_FUN_012aa7e6(&DAT_026cf5f8);
        }
        uVar18 = FUN_00b6db70(lVar21);
        FUN_01008290(local_578,s_world_controller_state_manager_p_016586fd,uVar18);
        uVar26 = DAT_026cf5f0;
LAB_00791f38:
        FUN_000e4aa0(uVar26,local_578);
      }
LAB_00791f40:
      *param_2 = -1;
      cVar8 = FUN_000e4d70(5,3);
      if (cVar8 != '\0') {
        if ((DAT_026cf768 == '\0') && (iVar13 = thunk_FUN_012aa7d6(&DAT_026cf768), iVar13 != 0)) {
          DAT_026cf760 = FUN_000e4a10(s_world_controller_state_manager_p_016590f8);
          thunk_FUN_012aa7e6(&DAT_026cf768);
        }
        if (*param_1 < 0x13) {
          pcVar30 = (&PTR_DAT_01945910)[(uint)(int)(char)*param_1];
        }
        else {
          pcVar30 = s_INVALID_0162318f;
        }
        FUN_01008290(local_578,s_world_controller_state_manager_p_016590f8,pcVar30);
        FUN_000e4aa0(DAT_026cf760,local_578);
      }
      lVar16 = *(long *)(param_1 + 8);
      bVar4 = param_1[0x20];
      uVar26 = *(undefined4 *)(param_1 + 0x18);
      sVar5 = *(short *)(param_1 + 2);
      lVar17 = DAT_026553b0;
      if (DAT_026553a8 == '\0') {
        lVar17 = FUN_000694d0();
      }
      FUN_00771c10(1,(int)sVar5,uVar26,bVar4,lVar17 - lVar16);
      goto LAB_00791a77;
    case 9:
      iVar15 = FUN_0075c850((int)*(short *)(param_1 + 2));
      if (iVar15 == 0) goto switchD_00790173_default;
      if (iVar15 == 2) {
        cVar8 = FUN_000e4d70(5,4);
        if (cVar8 != '\0') {
          if ((DAT_026cf658 == '\0') && (iVar13 = thunk_FUN_012aa7d6(&DAT_026cf658), iVar13 != 0)) {
            DAT_026cf650 = FUN_000e4a10(s_world_controller_state_manager_p_0165898e);
            thunk_FUN_012aa7e6(&DAT_026cf658);
          }
          FUN_01008290(local_578,s_world_controller_state_manager_p_0165898e);
          uVar26 = DAT_026cf650;
          goto LAB_00791f38;
        }
        goto LAB_00791f40;
      }
      cVar8 = FUN_000e4d70(5,3);
      bVar7 = true;
      if (cVar8 != '\0') {
        if ((DAT_026cf668 == '\0') && (iVar15 = thunk_FUN_012aa7d6(&DAT_026cf668), iVar15 != 0)) {
          DAT_026cf660 = FUN_000e4a10(s_world_controller_state_manager_p_01658a12);
          thunk_FUN_012aa7e6(&DAT_026cf668);
        }
        bVar6 = false;
        FUN_01008290(local_578,s_world_controller_state_manager_p_01658a12);
        uVar26 = DAT_026cf660;
        bVar7 = true;
        goto LAB_007902bb;
      }
      bVar6 = false;
      break;
    case 10:
      iVar15 = FUN_0075cbe0(0,0);
      cVar8 = FUN_0075cd90(iVar15);
      if (cVar8 != '\0') {
        *(int *)(param_1 + 0x1c) = *(int *)(param_1 + 0x1c) + 1;
      }
      if (iVar15 == -1) {
        lVar21 = FUN_00775770(1);
        uVar18 = 0;
        if (lVar21 != 0) {
          uVar18 = FUN_011c3f80(lVar21 + 0x9b8);
        }
        local_970 = 0;
        uVar19 = FUN_005753c0(4);
        thunk_FUN_012aa7c6(local_978,uVar18,0x8c);
        local_974 = FUN_0026b7f0(uVar19,local_976);
        cVar8 = FUN_000e4d70(5,2);
        if (cVar8 != '\0') {
          if ((DAT_026cf678 == '\0') && (iVar15 = thunk_FUN_012aa7d6(&DAT_026cf678), iVar15 != 0)) {
            DAT_026cf670 = FUN_000e4a10(s_world_controller_state_manager_p_01658a8c);
            thunk_FUN_012aa7e6(&DAT_026cf678);
          }
          local_ab8[0] = 0;
          FUN_0100a3d0(local_ab8,s_activity_index__d__insertion_poi_0164c903,(int)local_976,
                       (int)local_974);
          FUN_01008290(local_578,s_world_controller_state_manager_p_01658a8c,local_ab8);
          FUN_000e4aa0(DAT_026cf670,local_578);
        }
        FUN_0075c720(0,0,local_978);
        goto switchD_00790173_default;
      }
      cVar8 = FUN_0075cd90(iVar15);
      if (cVar8 == '\0') {
        if (iVar15 != 6) {
          iVar14 = FUN_000697a0();
          if (15000 < (uint)(iVar14 - _DAT_026cf690)) {
            cVar8 = FUN_000e4d70(5,1);
            if (cVar8 != '\0') {
              if ((DAT_026cf698 == '\0') &&
                 (iVar14 = thunk_FUN_012aa7d6(&DAT_026cf698), iVar14 != 0)) {
                DAT_026cf694 = FUN_000e4a10(s_world_controller_state_manager_p_01658b6b);
                thunk_FUN_012aa7e6(&DAT_026cf698);
              }
              uVar18 = FUN_002a46b0(iVar15);
              FUN_01008290(local_578,s_world_controller_state_manager_p_01658b6b,uVar18);
              FUN_000e4aa0(DAT_026cf694,local_578);
            }
            _DAT_026cf690 = FUN_000697a0();
          }
          goto switchD_00790173_default;
        }
        cVar8 = FUN_000e4d70(5,2);
        bVar7 = true;
        if (cVar8 != '\0') {
          if ((DAT_026cf6a8 == '\0') && (iVar15 = thunk_FUN_012aa7d6(&DAT_026cf6a8), iVar15 != 0)) {
            DAT_026cf6a0 = FUN_000e4a10(s_world_controller_state_manager_p_01658bd9);
            thunk_FUN_012aa7e6(&DAT_026cf6a8);
          }
          bVar6 = false;
          FUN_01008290(local_578,s_world_controller_state_manager_p_01658bd9);
          uVar26 = DAT_026cf6a0;
          bVar7 = true;
          goto LAB_007902bb;
        }
        bVar6 = false;
      }
      else {
        cVar8 = FUN_000e4d70(5,3);
        bVar6 = true;
        if (cVar8 != '\0') {
          if ((DAT_026cf688 == '\0') && (iVar14 = thunk_FUN_012aa7d6(&DAT_026cf688), iVar14 != 0)) {
            DAT_026cf680 = FUN_000e4a10(s_world_controller_state_manager_p_01658afd);
            thunk_FUN_012aa7e6(&DAT_026cf688);
          }
          uVar18 = FUN_002a46b0(iVar15);
          FUN_01008290(local_578,s_world_controller_state_manager_p_01658afd,uVar18);
          uVar26 = DAT_026cf680;
          bVar7 = false;
          goto LAB_007902bb;
        }
        bVar7 = false;
      }
      break;
    case 0xb:
      cVar8 = FUN_00792090();
      bVar6 = true;
      if (cVar8 == '\0') {
        bVar7 = false;
      }
      else {
        cVar8 = FUN_00752290(0);
        bVar7 = true;
        bVar6 = false;
        if (cVar8 == '\0') {
          cVar8 = FUN_000e4d70(5,4);
          if (cVar8 != '\0') {
            if ((DAT_026cf6b8 == '\0') && (iVar13 = thunk_FUN_012aa7d6(&DAT_026cf6b8), iVar13 != 0))
            {
              DAT_026cf6b0 = FUN_000e4a10(s_world_controller_state_manager_p_01658c28);
              thunk_FUN_012aa7e6(&DAT_026cf6b8);
            }
            FUN_01008290(local_578,s_world_controller_state_manager_p_01658c28);
            uVar26 = DAT_026cf6b0;
            goto LAB_00791f38;
          }
          goto LAB_00791f40;
        }
      }
      break;
    case 0xc:
      cVar8 = FUN_00792090();
      bVar6 = true;
      if (cVar8 != '\0') {
        cVar8 = FUN_007526f0(9);
        if (cVar8 == '\0') {
          cVar8 = FUN_0034d0f0();
          if (cVar8 == '\0') {
            uVar18 = FUN_003409a0();
            lVar21 = FUN_00078970(uVar18);
            lVar22 = FUN_0075f070();
            if ((lVar21 == 0) || (lVar22 == 0)) {
              cVar8 = FUN_000e4d70(5,3);
              if (cVar8 != '\0') {
                if ((DAT_026cf7e8 == '\0') &&
                   (iVar13 = thunk_FUN_012aa7d6(&DAT_026cf7e8), iVar13 != 0)) {
                  DAT_026cf7e0 = FUN_000e4a10(s_world_controller_state_manager_p_01659656);
                  thunk_FUN_012aa7e6(&DAT_026cf7e8);
                }
                FUN_01008290(local_578,s_world_controller_state_manager_p_01659656);
                uVar26 = DAT_026cf7e0;
LAB_00791e47:
                FUN_000e4aa0(uVar26,local_578);
              }
            }
            else {
              iVar15 = thunk_FUN_012aab16(lVar22 + 0x628,lVar21,0x28);
              bVar7 = true;
              bVar6 = false;
              if (iVar15 == 0) break;
              cVar8 = FUN_000e4d70(5,3);
              if (cVar8 != '\0') {
                if ((DAT_026cf7f8 == '\0') &&
                   (iVar13 = thunk_FUN_012aa7d6(&DAT_026cf7f8), iVar13 != 0)) {
                  DAT_026cf7f0 = FUN_000e4a10(s_world_controller_state_manager_p_016596d3);
                  thunk_FUN_012aa7e6(&DAT_026cf7f8);
                }
                FUN_01008290(local_578,s_world_controller_state_manager_p_016596d3,lVar21,
                             lVar22 + 0x628);
                uVar26 = DAT_026cf7f0;
                goto LAB_00791e47;
              }
            }
            cVar8 = FUN_000e4d70(5,4);
            if (cVar8 != '\0') {
              if ((DAT_026cf6e8 == '\0') &&
                 (iVar13 = thunk_FUN_012aa7d6(&DAT_026cf6e8), iVar13 != 0)) {
                DAT_026cf6e0 = FUN_000e4a10(s_world_controller_state_manager_p_01658d82);
                thunk_FUN_012aa7e6(&DAT_026cf6e8);
              }
              FUN_01008290(local_578,s_world_controller_state_manager_p_01658d82);
              uVar26 = DAT_026cf6e0;
              goto LAB_00791f38;
            }
            goto LAB_00791f40;
          }
          iVar15 = FUN_000697a0();
          if (15000 < (uint)(iVar15 - _DAT_026cf6d0)) {
            cVar8 = FUN_000e4d70(5,2);
            if (cVar8 != '\0') {
              if ((DAT_026cf6d8 == '\0') &&
                 (iVar15 = thunk_FUN_012aa7d6(&DAT_026cf6d8), iVar15 != 0)) {
                DAT_026cf6d4 = FUN_000e4a10(s_world_controller_state_manager_p_01658d11);
                thunk_FUN_012aa7e6(&DAT_026cf6d8);
              }
              FUN_01008290(local_578,s_world_controller_state_manager_p_01658d11);
              FUN_000e4aa0(DAT_026cf6d4,local_578);
            }
            _DAT_026cf6d0 = FUN_000697a0();
          }
        }
        else {
          iVar15 = FUN_000697a0();
          if (15000 < (uint)(iVar15 - _DAT_026cf6c0)) {
            cVar8 = FUN_000e4d70(5,2);
            if (cVar8 != '\0') {
              if ((DAT_026cf6c8 == '\0') &&
                 (iVar15 = thunk_FUN_012aa7d6(&DAT_026cf6c8), iVar15 != 0)) {
                DAT_026cf6c4 = FUN_000e4a10(s_world_controller_state_manager_p_01658c92);
                thunk_FUN_012aa7e6(&DAT_026cf6c8);
              }
              FUN_01008290(local_578,s_world_controller_state_manager_p_01658c92);
              FUN_000e4aa0(DAT_026cf6c4,local_578);
            }
            _DAT_026cf6c0 = FUN_000697a0();
          }
        }
        goto switchD_00790173_default;
      }
      bVar7 = false;
      break;
    case 0xd:
      FUN_0076a630(1);
LAB_00790bb4:
      bVar7 = true;
      bVar6 = false;
      break;
    case 0xe:
      local_adc = 0;
      cVar8 = FUN_00792090();
      bVar6 = true;
      if (cVar8 == '\0') {
        bVar7 = false;
      }
      else {
        iVar15 = FUN_0077b730();
        if (iVar15 == 0) {
          FUN_0077b710(1);
          goto switchD_00790173_default;
        }
        FUN_0077b830(&local_adc);
        cVar8 = FUN_0077b790(local_adc);
        if (cVar8 == '\0') {
          cVar8 = FUN_0077b7b0();
          if (cVar8 == '\0') {
            iVar15 = FUN_000697a0();
            if (15000 < (uint)(iVar15 - _DAT_026cf700)) {
              cVar8 = FUN_000e4d70(5,1);
              if (cVar8 != '\0') {
                if ((DAT_026cf708 == '\0') &&
                   (iVar15 = thunk_FUN_012aa7d6(&DAT_026cf708), iVar15 != 0)) {
                  DAT_026cf704 = FUN_000e4a10(s_world_controller_state_manager_p_01658e6f);
                  thunk_FUN_012aa7e6(&DAT_026cf708);
                }
                FUN_01008290(local_578,s_world_controller_state_manager_p_01658e6f);
                FUN_000e4aa0(DAT_026cf704,local_578);
              }
              _DAT_026cf700 = FUN_000697a0();
            }
            goto switchD_00790173_default;
          }
          cVar8 = FUN_000e4d70(5,2);
          bVar7 = true;
          if (cVar8 != '\0') {
            if ((DAT_026cf718 == '\0') && (iVar15 = thunk_FUN_012aa7d6(&DAT_026cf718), iVar15 != 0))
            {
              DAT_026cf710 = FUN_000e4a10(s_world_controller_state_manager_p_01658ecc);
              thunk_FUN_012aa7e6(&DAT_026cf718);
            }
            bVar6 = false;
            FUN_01008290(local_578,s_world_controller_state_manager_p_01658ecc);
            uVar26 = DAT_026cf710;
            bVar7 = true;
            goto LAB_007902bb;
          }
          bVar6 = false;
        }
        else {
          cVar8 = FUN_000e4d70(5,4);
          if (cVar8 != '\0') {
            if ((DAT_026cf6f8 == '\0') && (iVar15 = thunk_FUN_012aa7d6(&DAT_026cf6f8), iVar15 != 0))
            {
              DAT_026cf6f0 = FUN_000e4a10(s_world_controller_state_manager_p_01658e0e);
              thunk_FUN_012aa7e6(&DAT_026cf6f8);
            }
            uVar18 = FUN_000e9fa0(local_adc);
            FUN_01008290(local_578,s_world_controller_state_manager_p_01658e0e,uVar18);
            uVar26 = DAT_026cf6f0;
            bVar7 = false;
            goto LAB_007902bb;
          }
          bVar7 = false;
        }
      }
      break;
    case 0xf:
      cVar8 = FUN_00792090();
      bVar6 = true;
      if (cVar8 != '\0') {
        iVar15 = FUN_0077b730();
        if (iVar15 == 1) {
          FUN_0077b710(2);
        }
        else {
          cVar8 = FUN_0077b8d0();
          if (cVar8 != '\0') {
            cVar8 = FUN_000e4d70(5,2);
            bVar7 = true;
            if (cVar8 != '\0') {
              if ((DAT_026cf738 == '\0') &&
                 (iVar15 = thunk_FUN_012aa7d6(&DAT_026cf738), iVar15 != 0)) {
                DAT_026cf730 = FUN_000e4a10(s_world_controller_state_manager_p_01658f82);
                thunk_FUN_012aa7e6(&DAT_026cf738);
              }
              bVar6 = false;
              FUN_01008290(local_578,s_world_controller_state_manager_p_01658f82);
              uVar26 = DAT_026cf730;
              bVar7 = true;
              goto LAB_007902bb;
            }
            bVar6 = false;
            break;
          }
          iVar15 = FUN_000697a0();
          if (15000 < (uint)(iVar15 - _DAT_026cf720)) {
            cVar8 = FUN_000e4d70(5,1);
            if (cVar8 != '\0') {
              if ((DAT_026cf728 == '\0') &&
                 (iVar15 = thunk_FUN_012aa7d6(&DAT_026cf728), iVar15 != 0)) {
                DAT_026cf724 = FUN_000e4a10(s_world_controller_state_manager_p_01658f23);
                thunk_FUN_012aa7e6(&DAT_026cf728);
              }
              FUN_01008290(local_578,s_world_controller_state_manager_p_01658f23);
              FUN_000e4aa0(DAT_026cf724,local_578);
            }
            _DAT_026cf720 = FUN_000697a0();
          }
        }
        goto switchD_00790173_default;
      }
      bVar7 = false;
      break;
    case 0x10:
      cVar8 = FUN_00792090();
      bVar6 = true;
      if (cVar8 != '\0') {
        uVar18 = 4;
        goto LAB_00790a05;
      }
      bVar7 = false;
      break;
    case 0x11:
      cVar8 = FUN_00792090();
      bVar6 = true;
      bVar7 = false;
      if (cVar8 == '\0') break;
      lVar22 = FUN_0034e5c0();
      lVar21 = *(long *)(param_1 + 0x10);
      lVar22 = *(long *)(lVar22 + 0xb8);
      lVar20 = DAT_026553b0;
      if (DAT_026553a8 == '\0') {
        lVar20 = FUN_000694d0();
      }
      iVar15 = FUN_000697a0();
      if (10000 < (uint)(iVar15 - _DAT_026cf740)) {
        cVar8 = FUN_000e4d70(5,2);
        if (cVar8 != '\0') {
          if ((DAT_026cf748 == '\0') && (iVar15 = thunk_FUN_012aa7d6(&DAT_026cf748), iVar15 != 0)) {
            DAT_026cf744 = FUN_000e4a10(s_world_controller_state_manager_p_01658fdb);
            thunk_FUN_012aa7e6(&DAT_026cf748);
          }
          FUN_01008290(local_578,s_world_controller_state_manager_p_01658fdb,lVar20 - lVar21,lVar22)
          ;
          FUN_000e4aa0(DAT_026cf744,local_578);
        }
        _DAT_026cf740 = FUN_000697a0();
      }
      *param_2 = -1;
      if (lVar22 <= lVar20 - lVar21) goto LAB_007917c9;
LAB_007919ab:
      if (*param_1 != 0) goto LAB_007900a2;
      goto LAB_00790025;
    case 0x12:
      *param_2 = -1;
      lVar16 = *(long *)pbVar3;
      lVar17 = DAT_026553b0;
      if (DAT_026553a8 == '\0') {
        lVar17 = FUN_000694d0();
      }
      cVar8 = FUN_000e4d70(5,2);
      if (cVar8 != '\0') {
        if ((DAT_026cf758 == '\0') && (iVar13 = thunk_FUN_012aa7d6(&DAT_026cf758), iVar13 != 0)) {
          DAT_026cf750 = FUN_000e4a10(s_world_controller_state_manager_p_01659046);
          thunk_FUN_012aa7e6(&DAT_026cf758);
        }
        if (*param_1 < 0x13) {
          pcVar30 = (&PTR_DAT_01945910)[(uint)(int)(char)*param_1];
        }
        else {
          pcVar30 = s_INVALID_0162318f;
        }
        FUN_01008290(local_578,s_world_controller_state_manager_p_01659046,pcVar30,
                     *(undefined4 *)pbVar2,lVar17 - lVar16);
        FUN_000e4aa0(DAT_026cf750,local_578);
      }
      FUN_00771c10(0,(int)*(short *)(param_1 + 2),*(undefined4 *)(param_1 + 0x18),param_1[0x20],
                   lVar17 - lVar16);
      goto LAB_00791a86;
    default:
switchD_00790173_default:
      bVar7 = false;
      bVar6 = false;
    }
LAB_007916d5:
    *param_2 = -1;
    lVar21 = *(long *)pbVar3;
    lVar22 = DAT_026553b0;
    if (DAT_026553a8 == '\0') {
      lVar22 = FUN_000694d0();
    }
    if (lVar1 < lVar22 - lVar21) {
      cVar8 = FUN_000e4d70(5,3);
      if (cVar8 != '\0') {
        if ((DAT_026cf778 == '\0') && (iVar13 = thunk_FUN_012aa7d6(&DAT_026cf778), iVar13 != 0)) {
          DAT_026cf770 = FUN_000e4a10(s_world_controller_state_manager_p_01659163);
          thunk_FUN_012aa7e6(&DAT_026cf778);
        }
        if (*param_1 < 0x13) {
          pcVar30 = (&PTR_DAT_01945910)[(uint)(int)(char)*param_1];
        }
        else {
          pcVar30 = s_INVALID_0162318f;
        }
        lVar21 = *(long *)pbVar3;
        lVar22 = DAT_026553b0;
        if (DAT_026553a8 == '\0') {
          lVar22 = FUN_000694d0();
        }
        FUN_01008290(local_578,s_world_controller_state_manager_p_01659163,pcVar30,lVar22 - lVar21,
                     lVar1,lVar16,lVar17);
        FUN_000e4aa0(DAT_026cf770,local_578);
      }
      lVar16 = *(long *)(param_1 + 8);
      bVar4 = param_1[0x20];
      uVar26 = *(undefined4 *)(param_1 + 0x18);
      sVar5 = *(short *)(param_1 + 2);
      lVar17 = DAT_026553b0;
      if (DAT_026553a8 == '\0') {
        lVar17 = FUN_000694d0();
      }
      FUN_00771c10(2,(int)sVar5,uVar26,bVar4,lVar17 - lVar16);
LAB_00791a77:
      *param_2 = (int)*(short *)(param_1 + 2);
LAB_00791a86:
      FUN_00792170(param_1,0);
      *(undefined2 *)(param_1 + 0x40) = *(undefined2 *)(param_1 + 2);
      *(undefined4 *)(param_1 + 0x48) = *(undefined4 *)(param_1 + 0x18);
      *(undefined4 *)(param_1 + 0x4c) = *(undefined4 *)(param_1 + 0x1c);
      *param_1 = 0;
      param_1[2] = 0xff;
      param_1[3] = 0xff;
      param_1[0x10] = 0xff;
      param_1[0x11] = 0xff;
      param_1[0x12] = 0xff;
      param_1[0x13] = 0xff;
      param_1[0x14] = 0xff;
      param_1[0x15] = 0xff;
      param_1[0x16] = 0xff;
      param_1[0x17] = 0xff;
      pbVar3[0] = 0xff;
      pbVar3[1] = 0xff;
      pbVar3[2] = 0xff;
      pbVar3[3] = 0xff;
      pbVar3[4] = 0xff;
      pbVar3[5] = 0xff;
      pbVar3[6] = 0xff;
      pbVar3[7] = 0xff;
      param_1[0x20] = 0;
      param_1[0x21] = 0;
      pbVar2[0] = 0;
      pbVar2[1] = 0;
      pbVar2[2] = 0;
      pbVar2[3] = 0;
      pbVar2[4] = 0;
      pbVar2[5] = 0;
      pbVar2[6] = 0;
      pbVar2[7] = 0;
      goto LAB_00790025;
    }
    if (bVar6) {
      cVar8 = FUN_000e4d70(5);
      if (cVar8 != '\0') {
        if ((DAT_026cf788 == '\0') && (iVar15 = thunk_FUN_012aa7d6(&DAT_026cf788), iVar15 != 0)) {
          DAT_026cf780 = FUN_000e4a10(s_world_controller_state_manager_p_0165920c);
          thunk_FUN_012aa7e6(&DAT_026cf788);
        }
        pcVar30 = s_INVALID_0162318f;
        if (*param_1 < 0x13) {
          pcVar30 = (&PTR_DAT_01945910)[(uint)(int)(char)*param_1];
        }
        lVar21 = *(long *)pbVar3;
        uVar26 = *(undefined4 *)pbVar2;
        lVar22 = DAT_026553b0;
        if (DAT_026553a8 == '\0') {
          lVar22 = FUN_000694d0();
        }
        FUN_01008290(local_578,s_world_controller_state_manager_p_0165920c,pcVar30,uVar26,
                     lVar22 - lVar21);
        FUN_000e4aa0(DAT_026cf780);
      }
      FUN_00792170(param_1);
      *(int *)(param_1 + 0x18) = *(int *)(param_1 + 0x18) + 1;
    }
    else {
      if (!bVar7) goto LAB_007919ab;
LAB_007917c9:
      bVar4 = *param_1;
      cVar8 = FUN_000e4d70(5,2);
      if (cVar8 != '\0') {
        if ((DAT_026cf798 == '\0') && (iVar15 = thunk_FUN_012aa7d6(&DAT_026cf798), iVar15 != 0)) {
          DAT_026cf790 = FUN_000e4a10(s_world_controller_state_manager_p_016592aa);
          thunk_FUN_012aa7e6(&DAT_026cf798);
        }
        pcVar30 = s_INVALID_0162318f;
        if ((int)(char)bVar4 + 1U < 0x13) {
          pcVar30 = (&PTR_DAT_01945910)[(int)(char)bVar4 + 1U];
        }
        FUN_01008290(local_578,s_world_controller_state_manager_p_016592aa,pcVar30);
        FUN_000e4aa0(DAT_026cf790,local_578);
      }
      FUN_00792170(param_1);
    }
    goto LAB_0079011f;
  }
  cVar8 = FUN_000e4d70(5,1);
  if (cVar8 != '\0') {
    if ((DAT_026cf578 == '\0') && (iVar13 = thunk_FUN_012aa7d6(&DAT_026cf578), iVar13 != 0)) {
      DAT_026cf570 = FUN_000e4a10(s_world_controller_state_manager_p_0165839c);
      thunk_FUN_012aa7e6(&DAT_026cf578);
    }
    FUN_01008290(local_578,s_world_controller_state_manager_p_0165839c);
    FUN_000e4aa0(DAT_026cf570,local_578);
  }
  *param_2 = (int)*(short *)(param_1 + 2);
  FUN_00792170(param_1,0);
  *(undefined2 *)(param_1 + 0x40) = *(undefined2 *)(param_1 + 2);
  *(undefined4 *)(param_1 + 0x48) = *(undefined4 *)(param_1 + 0x18);
  *(undefined4 *)(param_1 + 0x4c) = *(undefined4 *)(param_1 + 0x1c);
  *param_1 = 0;
  param_1[2] = 0xff;
  param_1[3] = 0xff;
  param_1[0x10] = 0xff;
  param_1[0x11] = 0xff;
  param_1[0x12] = 0xff;
  param_1[0x13] = 0xff;
  param_1[0x14] = 0xff;
  param_1[0x15] = 0xff;
  param_1[0x16] = 0xff;
  param_1[0x17] = 0xff;
  param_1[8] = 0xff;
  param_1[9] = 0xff;
  param_1[10] = 0xff;
  param_1[0xb] = 0xff;
  param_1[0xc] = 0xff;
  param_1[0xd] = 0xff;
  param_1[0xe] = 0xff;
  param_1[0xf] = 0xff;
  param_1[0x20] = 0;
  param_1[0x21] = 0;
  param_1[0x18] = 0;
  param_1[0x19] = 0;
  param_1[0x1a] = 0;
  param_1[0x1b] = 0;
  param_1[0x1c] = 0;
  param_1[0x1d] = 0;
  param_1[0x1e] = 0;
  param_1[0x1f] = 0;
LAB_00790025:
  cVar8 = FUN_000e4d70(5,2);
  if (cVar8 != '\0') {
    if ((DAT_026cf7a8 == '\0') && (iVar13 = thunk_FUN_012aa7d6(&DAT_026cf7a8), iVar13 != 0)) {
      DAT_026cf7a0 = FUN_000e4a10(s_world_controller_state_manager_p_0165930e);
      thunk_FUN_012aa7e6(&DAT_026cf7a8);
    }
    FUN_01008290(local_578,s_world_controller_state_manager_p_0165930e);
    FUN_000e4aa0(DAT_026cf7a0,local_578);
  }
  FUN_002984c0(param_1 + 0x28);
LAB_007900a2:
  if (*DAT_01a1f100 != local_38) {
    uVar12 = thunk_FUN_012aa7f6();
    return (bool)uVar12;
  }
  return *param_1 != 0;
}

