
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_00783ee0(int param_1,uint param_2,undefined *param_3)

{
  byte bVar1;
  char cVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  undefined4 uVar6;
  int iVar7;
  long lVar8;
  long lVar9;
  long lVar10;
  undefined8 uVar11;
  long *plVar12;
  undefined8 uVar13;
  undefined8 uVar14;
  undefined *puVar15;
  undefined *puVar16;
  undefined *puVar17;
  undefined *puVar18;
  int iVar19;
  char *pcVar20;
  uint uVar21;
  bool bVar22;
  bool bVar23;
  undefined1 local_7f9;
  undefined8 local_7d8;
  undefined8 uStack_7d0;
  undefined8 local_7c8;
  char local_7b8 [320];
  undefined1 local_678 [256];
  undefined1 local_578 [320];
  undefined1 local_438 [256];
  undefined1 local_338 [256];
  undefined1 local_238 [256];
  uint local_138 [64];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  puVar15 = &DAT_0161597a;
  if (param_3 != (undefined *)0x0) {
    puVar15 = param_3;
  }
  lVar8 = FUN_00768050();
  bVar22 = param_2 < 0x10;
  local_678[0] = 0;
  bVar23 = param_2 == 0xffffffff;
  if ((bVar23 || bVar22) || ((bVar1 = 1, 0x107 < param_2 - 0x10 && (param_2 == 0x119)))) {
    bVar1 = 1;
    if (((0xf < param_2) || ((0xf78aU >> (param_2 & 0x1f) & 1) == 0)) &&
       (((lVar9 = FUN_00775770(0), lVar9 == 0 || (iVar3 = FUN_00b93120(lVar9), iVar3 != 0x1b)) &&
        (bVar1 = FUN_007853a0(1), bVar1 == 0)))) {
      lVar9 = FUN_007756e0(1);
      puVar16 = &DAT_01615ab5;
      puVar17 = &DAT_01615ab5;
      if (lVar9 != 0) {
        lVar9 = (long)*(int *)(lVar9 + 0x148 + (long)*(int *)(lVar9 + 0x10) * 0x168);
        puVar17 = &DAT_01615ab5;
        if (lVar9 != -1) {
          puVar17 = (&PTR_s_pregame_01945340)[lVar9];
        }
      }
      lVar9 = FUN_00768050();
      puVar18 = &DAT_01615ab5;
      if (lVar9 != 0) {
        puVar18 = &DAT_01615ab5;
        if ((long)*(int *)(lVar9 + 0x1b0) != -1) {
          puVar18 = (&PTR_s_pregame_01945340)[*(int *)(lVar9 + 0x1b0)];
        }
      }
      lVar9 = FUN_00775770(1);
      if ((lVar9 != 0) && (iVar3 = FUN_00b93120(lVar9), iVar3 != -1)) {
        puVar16 = (&PTR_s_pregame_01945340)[iVar3];
      }
      bVar1 = 0;
      FUN_010080a0(local_678,s_posse_host_state___s__not_closer_01656978,puVar17,puVar18,puVar16);
    }
    if (!bVar23 && !bVar22) goto LAB_00784085;
LAB_00784098:
    if ((param_2 < 0x10) && ((0xf382U >> (param_2 & 0x1f) & 1) != 0)) goto LAB_007840b4;
    cVar2 = FUN_00b21070(0);
    if ((cVar2 == '\0') && (cVar2 = FUN_00b210e0(0), cVar2 == '\0')) {
      cVar2 = FUN_007754d0(1);
      if ((cVar2 != '\0') || (cVar2 = FUN_007853a0(0), cVar2 != '\0')) goto LAB_007840b4;
      lVar8 = FUN_007756e0(0);
      puVar16 = &DAT_01615ab5;
      puVar17 = &DAT_01615ab5;
      if (lVar8 != 0) {
        lVar8 = (long)*(int *)(lVar8 + 0x148 + (long)*(int *)(lVar8 + 0x10) * 0x168);
        puVar17 = &DAT_01615ab5;
        if (lVar8 != -1) {
          puVar17 = (&PTR_s_pregame_01945340)[lVar8];
        }
      }
      lVar8 = FUN_00768050();
      puVar18 = &DAT_01615ab5;
      if (lVar8 != 0) {
        puVar18 = &DAT_01615ab5;
        if ((long)*(int *)(lVar8 + 0x1b0) != -1) {
          puVar18 = (&PTR_s_pregame_01945340)[*(int *)(lVar8 + 0x1b0)];
        }
      }
      lVar8 = FUN_00775770(0);
      if ((lVar8 != 0) && (iVar3 = FUN_00b93120(lVar8), iVar3 != -1)) {
        puVar16 = (&PTR_s_pregame_01945340)[iVar3];
      }
      FUN_010080a0(local_678,s_FT_host_state___s__not_closer_th_016569e0,puVar17,puVar18,puVar16);
    }
    else {
      cVar2 = FUN_00b21070(0);
      pcVar20 = s_IN_PROGRESS_0165159d;
      if (cVar2 != '\0') {
        pcVar20 = s_QUEUED_016569d9;
      }
      FUN_010080a0(local_678,s_active_outbound_FT_join___s__016569bc,pcVar20);
    }
  }
  else {
LAB_00784085:
    if ((0x107 < param_2 - 0x10) && (param_2 == 0x119)) goto LAB_00784098;
LAB_007840b4:
    if ((bVar1 & 1) != 0) {
      local_7f9 = 0;
      if (lVar8 != 0) {
        if (((*(int *)(lVar8 + 0x1b0) == param_1) && (param_1 != 0x19)) &&
           (cVar2 = FUN_000e4d70(5,3), cVar2 != '\0')) {
          if ((DAT_026cc138 == '\0') && (iVar3 = thunk_FUN_012aa7d6(&DAT_026cc138), iVar3 != 0)) {
            DAT_026cc130 = FUN_000e4a10(s_world_controller_state_manager__D_016563a1);
            thunk_FUN_012aa7e6(&DAT_026cc138);
          }
          if (param_1 == -1) {
            puVar17 = &DAT_01615ab5;
          }
          else {
            puVar17 = (&PTR_s_pregame_01945340)[param_1];
          }
          FUN_01008290(local_578,s_world_controller_state_manager__D_016563a1,puVar17);
          FUN_000e4aa0(DAT_026cc130,local_578);
        }
        *(int *)(lVar8 + 0x1c0) = param_1;
        *(uint *)(lVar8 + 0x1c4) = param_2;
        local_7f9 = 1;
        if ((!bVar23 && !bVar22) && ((param_2 - 0x10 < 0x108 || (param_2 != 0x119)))) {
          lVar9 = thunk_FUN_00768060();
          local_7d8 = 0;
          uStack_7d0 = 0;
          local_7c8 = 0;
          if ((long)*(int *)(lVar8 + 0x1b0) != -1) {
            plVar12 = *(long **)(lVar8 + 0x80 + (long)*(int *)(lVar8 + 0x1b0) * 8);
            (**(code **)(*plVar12 + 0x40))(plVar12,&local_7d8);
          }
          if ((DAT_026cc148 == '\0') && (iVar3 = thunk_FUN_012aa7d6(&DAT_026cc148), iVar3 != 0)) {
            DAT_026cc140 = FUN_000e4a10(s_world_controller_state_manager__K_016563f9);
            thunk_FUN_012aa7e6(&DAT_026cc148);
          }
          puVar16 = &DAT_01615ab5;
          puVar17 = &DAT_01615ab5;
          if ((long)*(int *)(lVar8 + 0x1b0) != -1) {
            puVar17 = (&PTR_s_pregame_01945340)[*(int *)(lVar8 + 0x1b0)];
          }
          if ((long)*(int *)(lVar8 + 0x1c0) != -1) {
            puVar16 = (&PTR_s_pregame_01945340)[*(int *)(lVar8 + 0x1c0)];
          }
          FUN_01008290(local_578,s_world_controller_state_manager__K_016563f9,
                       *(undefined8 *)(&DAT_026caf40 + (long)(int)param_2 * 0x10),puVar17,puVar16,
                       puVar15);
          FUN_000e4aa0(DAT_026cc140,local_578);
          if ((DAT_026cc158 == '\0') && (iVar3 = thunk_FUN_012aa7d6(&DAT_026cc158), iVar3 != 0)) {
            DAT_026cc150 = FUN_000e4a10(s_world_controller_state_manager__K_01656470);
            thunk_FUN_012aa7e6(&DAT_026cc158);
          }
          FUN_01008290(local_578,s_world_controller_state_manager__K_01656470,local_7d8,local_7c8,
                       uStack_7d0);
          FUN_000e4aa0(DAT_026cc150,local_578);
          iVar3 = 0;
          do {
            iVar19 = 0;
            do {
              if (iVar19 == 1) {
                lVar10 = FUN_00772ec0();
              }
              else {
                lVar10 = FUN_00775180();
              }
              if ((lVar10 != 0) && (*(int *)(lVar10 + 0x8c48) != 0)) {
                uVar11 = FUN_00b6db70(lVar10);
                uVar21 = *(uint *)(lVar10 + 0x8c48);
                puVar15 = &DAT_01621de5;
                if ((*(int *)(lVar10 + 0x628) != -1) &&
                   (puVar15 = &DAT_01621de3, *(int *)(lVar10 + 0x632c) != *(int *)(lVar10 + 0x62c)))
                {
                  puVar15 = &DAT_01621de5;
                }
                uVar6 = 0;
                if ((((uVar21 < 0xb) && ((0x7f0U >> (uVar21 & 0x1f) & 1) != 0)) &&
                    (cVar2 = FUN_00b742d0(lVar10), cVar2 != '\0')) &&
                   (cVar2 = FUN_00b742e0(lVar10), cVar2 != '\0')) {
                  lVar10 = FUN_00b74340(lVar10);
                  puVar17 = &DAT_01621de5;
                  iVar7 = 0;
                  if (lVar10 != 0) {
                    uVar6 = *(undefined4 *)(lVar10 + 0x28);
                    iVar5 = FUN_00b7e9a0(lVar10);
                    iVar7 = 0;
                    while (iVar5 != -1) {
                      iVar7 = iVar7 + (uint)(*(int *)(lVar10 + 0x5c + (long)iVar5 * 0x168) == 10);
                      iVar5 = FUN_00b7e9d0(lVar10);
                    }
                    puVar17 = &DAT_01621de3;
                  }
                }
                else {
                  puVar17 = &DAT_01621de5;
                  iVar7 = 0;
                }
                if ((DAT_026cc248 == '\0') &&
                   (iVar5 = thunk_FUN_012aa7d6(&DAT_026cc248), iVar5 != 0)) {
                  DAT_026cc240 = FUN_000e4a10(s_world_controller_state_manager__K_0165690b);
                  thunk_FUN_012aa7e6(&DAT_026cc248);
                }
                puVar16 = &DAT_01621de5;
                if (((uVar21 & 0xfffffffe) == 6 || uVar21 == 8) || uVar21 == 9) {
                  puVar16 = &DAT_01621de3;
                }
                FUN_01008290(local_578,s_world_controller_state_manager__K_0165690b,uVar11,puVar16,
                             puVar15,puVar17,uVar6,iVar7);
                FUN_000e4aa0(DAT_026cc240,local_578);
              }
              iVar19 = iVar19 + 1;
            } while (iVar19 != 2);
            iVar3 = iVar3 + 1;
          } while (iVar3 != 3);
          FUN_00b658f0();
          if ((DAT_026cc208 == '\0') && (iVar3 = thunk_FUN_012aa7d6(&DAT_026cc208), iVar3 != 0)) {
            DAT_026cc200 = FUN_000e4a10(s_world_controller_state_manager__K_01656797);
            thunk_FUN_012aa7e6(&DAT_026cc208);
          }
          uVar11 = FUN_003409a0();
          cVar2 = FUN_00340cb0(uVar11);
          if (cVar2 == '\0') {
            puVar15 = &DAT_01615ab5;
          }
          else {
            uVar11 = FUN_003409a0();
            puVar15 = (undefined *)FUN_00078970(uVar11);
          }
          uVar11 = FUN_003430b0();
          FUN_00345640(local_138,uVar11);
          FUN_01008290(local_578,s_world_controller_state_manager__K_01656797,puVar15,local_138[0]);
          FUN_000e4aa0(DAT_026cc200,local_578);
          if ((DAT_026cc218 == '\0') && (iVar3 = thunk_FUN_012aa7d6(&DAT_026cc218), iVar3 != 0)) {
            DAT_026cc210 = FUN_000e4a10(s_world_controller_state_manager__K_016567ef);
            thunk_FUN_012aa7e6(&DAT_026cc218);
          }
          lVar10 = FUN_0075e400();
          if (lVar10 == 0) {
            puVar15 = &DAT_01615ab5;
          }
          else {
            puVar15 = (undefined *)FUN_0075e400();
          }
          FUN_01008290(local_578,s_world_controller_state_manager__K_016567ef,puVar15);
          FUN_000e4aa0(DAT_026cc210,local_578);
          iVar3 = 0;
          do {
            iVar19 = 0;
            do {
              cVar2 = FUN_0075cdc0(iVar3,iVar19);
              if (cVar2 != '\0') {
                uVar6 = FUN_0075cbe0(iVar3,iVar19);
                uVar11 = FUN_0075ccb0(iVar3,iVar19);
                plVar12 = (long *)FUN_0075d560(iVar3,iVar19);
                if ((DAT_026cc228 == '\0') &&
                   (iVar7 = thunk_FUN_012aa7d6(&DAT_026cc228), iVar7 != 0)) {
                  DAT_026cc220 = FUN_000e4a10(s_world_controller_state_manager__K_01656838);
                  thunk_FUN_012aa7e6(&DAT_026cc228);
                }
                if (plVar12 == (long *)0x0) {
                  uVar13 = FUN_002a46b0(uVar6);
                  FUN_01008290(local_578,s_world_controller_state_manager__K_01656838,&DAT_01615ab5,
                               uVar13,uVar11);
                  uVar6 = DAT_026cc220;
LAB_00784ac0:
                  FUN_000e4aa0(uVar6,local_578);
                }
                else {
                  uVar13 = (**(code **)(*plVar12 + 0x30))(plVar12);
                  uVar14 = FUN_002a46b0(uVar6);
                  FUN_01008290(local_578,s_world_controller_state_manager__K_01656838,uVar13,uVar14,
                               uVar11);
                  FUN_000e4aa0(DAT_026cc220,local_578);
                  cVar2 = FUN_0029a480(plVar12);
                  if (cVar2 != '\0') {
                    lVar10 = FUN_00299af0(plVar12);
                    cVar2 = FUN_000e4d70(5,2);
                    if (cVar2 != '\0') {
                      if ((DAT_026cc238 == '\0') &&
                         (iVar7 = thunk_FUN_012aa7d6(&DAT_026cc238), iVar7 != 0)) {
                        DAT_026cc230 = FUN_000e4a10(s_world_controller_state_manager__K_01656884);
                        thunk_FUN_012aa7e6(&DAT_026cc238);
                      }
                      FUN_01008290(local_578,s_world_controller_state_manager__K_01656884,
                                   (int)*(short *)(lVar10 + 0xe),(int)*(char *)(lVar10 + 0x10),
                                   lVar10 + 0x98,lVar10 + 0x198,*(undefined4 *)(lVar10 + 0x698),
                                   *(undefined4 *)(lVar10 + 4));
                      uVar6 = DAT_026cc230;
                      goto LAB_00784ac0;
                    }
                  }
                }
              }
              iVar19 = iVar19 + 1;
            } while (iVar19 != 2);
            iVar3 = iVar3 + 1;
          } while (iVar3 != 2);
          iVar3 = 0;
          do {
            iVar19 = FUN_00559c30(iVar3);
            if (iVar19 != 0) {
              local_138[0] = local_138[0] & 0xffffff00;
              local_238[0] = 0;
              local_338[0] = 0;
              local_438[0] = 0;
              FUN_00559cc0(iVar3,local_138);
              FUN_0055a1a0(iVar3,local_238);
              FUN_0055a200(iVar3,local_338);
              FUN_0055a280(iVar3,local_438);
              if ((DAT_026cc1d8 == '\0') &&
                 (iVar19 = thunk_FUN_012aa7d6(&DAT_026cc1d8), iVar19 != 0)) {
                DAT_026cc1d0 = FUN_000e4a10(s_world_controller_state_manager__K_016566df);
                thunk_FUN_012aa7e6(&DAT_026cc1d8);
              }
              FUN_01008290(local_578,s_world_controller_state_manager__K_016566df,local_138,
                           local_238);
              FUN_000e4aa0(DAT_026cc1d0,local_578);
              if ((DAT_026cc1e8 == '\0') &&
                 (iVar19 = thunk_FUN_012aa7d6(&DAT_026cc1e8), iVar19 != 0)) {
                DAT_026cc1e0 = FUN_000e4a10(s_world_controller_state_manager__K_0165671e);
                thunk_FUN_012aa7e6(&DAT_026cc1e8);
              }
              FUN_01008290(local_578,s_world_controller_state_manager__K_0165671e,local_338);
              FUN_000e4aa0(DAT_026cc1e0,local_578);
              if ((DAT_026cc1f8 == '\0') &&
                 (iVar19 = thunk_FUN_012aa7d6(&DAT_026cc1f8), iVar19 != 0)) {
                DAT_026cc1f0 = FUN_000e4a10(s_world_controller_state_manager__K_01656759);
                thunk_FUN_012aa7e6(&DAT_026cc1f8);
              }
              FUN_01008290(local_578,s_world_controller_state_manager__K_01656759,local_438);
              FUN_000e4aa0(DAT_026cc1f0,local_578);
            }
            iVar3 = iVar3 + 1;
          } while (iVar3 != 4);
          thunk_FUN_0009de90();
          iVar3 = 0;
          do {
            lVar10 = FUN_00775180(iVar3);
            if ((((lVar10 != 0) && (uVar21 = *(uint *)(lVar10 + 0x8c48), uVar21 != 0)) &&
                (uVar21 < 0xb)) &&
               ((((0x7f0U >> (uVar21 & 0x1f) & 1) != 0 &&
                 (cVar2 = FUN_00b742d0(lVar10), cVar2 != '\0')) &&
                ((cVar2 = FUN_00b742e0(lVar10), cVar2 != '\0' &&
                 (lVar10 = FUN_00b74340(lVar10), lVar10 != 0)))))) {
              FUN_00b84eb0(lVar10,lVar10 + 8);
            }
            lVar10 = FUN_00772ec0(iVar3);
            if (((lVar10 != 0) && (uVar21 = *(uint *)(lVar10 + 0x8c48), uVar21 != 0)) &&
               (((uVar21 < 0xb &&
                 ((((0x7f0U >> (uVar21 & 0x1f) & 1) != 0 &&
                   (cVar2 = FUN_00b742d0(lVar10), cVar2 != '\0')) &&
                  (cVar2 = FUN_00b742e0(lVar10), cVar2 != '\0')))) &&
                (lVar10 = FUN_00b74340(lVar10), lVar10 != 0)))) {
              FUN_00b84eb0(lVar10,lVar10 + 8);
            }
            iVar3 = iVar3 + 1;
          } while (iVar3 != 3);
          if (lVar9 == 0) {
            cVar2 = FUN_000e4d70(5,4);
            if (cVar2 != '\0') {
              if ((DAT_026cc168 == '\0') && (iVar3 = thunk_FUN_012aa7d6(&DAT_026cc168), iVar3 != 0))
              {
                DAT_026cc160 = FUN_000e4a10(s_world_controller_state_manager__K_016564eb);
                thunk_FUN_012aa7e6(&DAT_026cc168);
              }
              FUN_01008290(local_578,s_world_controller_state_manager__K_016564eb);
              FUN_000e4aa0(DAT_026cc160,local_578);
            }
          }
          else {
            FUN_0076d2b0(lVar9,*(undefined4 *)(lVar8 + 0x1b0),param_2,&local_7d8);
            FUN_0076c830(lVar9);
            cVar2 = FUN_0076d760(lVar9);
            if (cVar2 != '\0') {
              FUN_007779d0(param_2);
            }
          }
        }
      }
      goto LAB_00784e17;
    }
  }
  puVar16 = &DAT_01615ab5;
  puVar17 = &DAT_01615ab5;
  if (param_1 != -1) {
    puVar17 = (&PTR_s_pregame_01945340)[param_1];
  }
  if (param_2 != 0xffffffff) {
    puVar16 = *(undefined **)(&DAT_026caf40 + (long)(int)param_2 * 0x10);
  }
  pcVar20 = local_7b8;
  FUN_01008290(pcVar20,s_world_controller_state_manager__S_0165633e,puVar17,puVar16,puVar15,
               local_678);
  iVar3 = FUN_00065290(pcVar20,0x140);
  uVar21 = 0x811c9dc5;
  if (iVar3 != 0) {
    lVar8 = (long)iVar3;
    uVar21 = 0x811c9dc5;
    do {
      uVar4 = FUN_00064e20((int)*pcVar20);
      uVar21 = uVar4 ^ uVar21 * 0x1000193;
      pcVar20 = pcVar20 + 1;
      lVar8 = lVar8 + -1;
    } while (lVar8 != 0);
  }
  if ((DAT_018dcad4 != 0x811c9dc5) && (uVar21 == DAT_018dcad4)) {
    iVar3 = FUN_000697a0();
    local_7f9 = 0;
    if ((uint)(iVar3 - _DAT_026cc120) < 0x7531) goto LAB_00784e17;
  }
  if ((DAT_026cc128 == '\0') && (iVar3 = thunk_FUN_012aa7d6(&DAT_026cc128), iVar3 != 0)) {
    DAT_026cc124 = FUN_000e4a10(s_world_controller_state_manager__S_0165633e);
    thunk_FUN_012aa7e6(&DAT_026cc128);
  }
  FUN_000e4aa0(DAT_026cc124,local_7b8);
  DAT_018dcad4 = uVar21;
  _DAT_026cc120 = FUN_000697a0();
  local_7f9 = 0;
LAB_00784e17:
  if (*DAT_01a1f100 == local_38) {
    return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),local_7f9);
  }
  uVar11 = thunk_FUN_012aa7f6();
  return uVar11;
}

