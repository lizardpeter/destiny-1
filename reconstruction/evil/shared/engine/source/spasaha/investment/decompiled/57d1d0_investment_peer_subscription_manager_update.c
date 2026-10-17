
void FUN_0057d1d0(long *param_1)

{
  long *plVar1;
  long *plVar2;
  undefined1 uVar3;
  char cVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  undefined4 uVar8;
  int iVar9;
  long *plVar10;
  undefined8 uVar11;
  long *plVar12;
  long lVar13;
  undefined8 uVar14;
  long lVar15;
  undefined8 *puVar16;
  long lVar17;
  long *plVar18;
  long *plVar19;
  bool bVar20;
  bool bVar21;
  bool bVar22;
  int local_220 [2];
  long local_218 [39];
  int local_e0;
  long local_d8 [20];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  plVar10 = (long *)FUN_0058b760();
  iVar5 = FUN_000697a0();
  iVar9 = DAT_026bc3f0;
  iVar6 = thunk_FUN_012aa826(plVar10,param_1,0x150);
  bVar22 = false;
  if (iVar6 != 0) {
    local_220[0] = 0;
    plVar1 = plVar10 + 0x2a;
    plVar2 = param_1 + 0x2a;
    local_e0 = 0;
    plVar12 = param_1 + 2;
    plVar19 = plVar10 + 2;
    bVar20 = false;
    do {
      bVar22 = plVar19 == plVar1;
      plVar18 = plVar19;
      if ((plVar12 != plVar2) && (plVar19 != plVar1)) {
        while (bVar22 = false, plVar18 = plVar19, *plVar12 == *plVar19) {
          bVar22 = plVar10 + 0x28 == plVar19;
          plVar18 = plVar19 + 2;
          bVar21 = param_1 + 0x28 == plVar12;
          plVar12 = plVar12 + 2;
          if ((bVar21) || (bVar21 = plVar10 + 0x28 == plVar19, plVar19 = plVar18, bVar21)) break;
        }
      }
      if (plVar12 != plVar2) {
        if (bVar22) {
          plVar12 = plVar12 + -0x2a;
          do {
            if (plVar12[0x2a] != 0) {
              lVar17 = (long)local_220[0];
              local_220[0] = local_220[0] + 1;
              local_218[lVar17] = plVar12[0x2a];
            }
            plVar12 = plVar12 + 2;
          } while (param_1 != plVar12);
          bVar20 = true;
        }
        else {
          do {
            bVar22 = false;
            if (*plVar18 <= *plVar12) goto LAB_0057d373;
            if (*plVar12 != 0) {
              lVar17 = (long)local_220[0];
              local_220[0] = local_220[0] + 1;
              local_218[lVar17] = *plVar12;
            }
            plVar12 = plVar12 + 2;
            bVar20 = true;
          } while (plVar2 != plVar12);
        }
      }
      bVar22 = true;
      plVar12 = plVar2;
LAB_0057d373:
      plVar19 = plVar1;
      if (plVar18 != plVar1) {
        if (bVar22) {
          plVar18 = plVar18 + -0x2a;
          do {
            if (plVar18[0x2a] != 0) {
              lVar17 = (long)local_e0;
              local_e0 = local_e0 + 1;
              local_d8[lVar17] = plVar18[0x2a];
            }
            plVar18 = plVar18 + 2;
            bVar20 = true;
          } while (plVar10 != plVar18);
        }
        else {
          do {
            plVar19 = plVar18;
            if (*plVar12 <= *plVar18) break;
            if (*plVar18 != 0) {
              lVar17 = (long)local_e0;
              local_e0 = local_e0 + 1;
              local_d8[lVar17] = *plVar18;
            }
            plVar18 = plVar18 + 2;
            bVar20 = true;
            plVar19 = plVar1;
          } while (plVar1 != plVar18);
        }
      }
    } while ((plVar12 != plVar2) || (plVar19 != plVar1));
    if (0 < local_220[0]) {
      lVar17 = 0;
      do {
        uVar11 = FUN_0056b260();
        FUN_0056bd50(uVar11,0,local_218 + lVar17);
        iVar6 = -1;
        plVar19 = param_1 + 0x27;
        do {
          iVar6 = iVar6 + 1;
          if (0x13 < iVar6) goto LAB_0057d4b6;
          plVar19 = plVar19 + 3;
          plVar12 = (long *)FUN_00057f80(plVar19);
        } while (*plVar12 != local_218[lVar17]);
        FUN_0058bcf0(plVar19);
LAB_0057d4b6:
        lVar17 = lVar17 + 1;
      } while ((int)lVar17 < local_220[0]);
    }
    if (0 < local_e0) {
      lVar17 = 0;
      do {
        uVar11 = FUN_0056b260();
        FUN_0056bcd0(uVar11,0);
        iVar6 = -1;
        plVar19 = param_1 + 0x27;
        do {
          iVar6 = iVar6 + 1;
          if (0x13 < iVar6) goto LAB_0057d55c;
          plVar19 = plVar19 + 3;
          plVar12 = (long *)FUN_00057f80(plVar19);
        } while (*plVar12 != 0);
        lVar13 = FUN_0034e490();
        iVar6 = *(int *)(lVar13 + 0x2c);
        iVar7 = FUN_001db3c0();
        FUN_0058bd10(plVar19,local_d8 + lVar17,iVar6 + iVar7);
LAB_0057d55c:
        lVar17 = lVar17 + 1;
      } while ((int)lVar17 < local_e0);
    }
    thunk_FUN_012aa7c6(param_1,plVar10,0x150);
    bVar22 = false;
    if (bVar20) {
      FUN_0006a350(param_1 + 0x2a,0x14,0x18,FUN_0058b740,0);
      uVar11 = FUN_00078970(&DAT_026bc2b8);
      FUN_00577c40(uVar11);
      bVar22 = true;
    }
  }
  if ((uint)(iVar5 - iVar9) < 0x1389) {
    lVar17 = 0;
    do {
      lVar13 = (long)param_1 + lVar17 + 0x150;
      plVar10 = (long *)FUN_00057f80(lVar13);
      if (*plVar10 != 0) {
        uVar11 = FUN_0056b260();
        uVar14 = FUN_00057f80(lVar13);
        uVar3 = FUN_0056bf10(uVar11,0,uVar14);
        lVar15 = FUN_0034e490();
        iVar9 = *(int *)(lVar15 + 0x2c);
        iVar5 = FUN_001db3c0();
        FUN_0058bd40(lVar13,uVar3,iVar9 + iVar5);
      }
      lVar17 = lVar17 + 0x18;
    } while ((int)lVar17 != 0x1e0);
  }
  else {
    lVar17 = 0;
    do {
      lVar13 = (long)param_1 + lVar17 + 0x150;
      plVar10 = (long *)FUN_00057f80(lVar13);
      if (*plVar10 != 0) {
        uVar11 = FUN_0056b260();
        uVar14 = FUN_00057f80(lVar13);
        uVar3 = FUN_0056bf10(uVar11,0,uVar14);
        lVar15 = FUN_0034e490();
        iVar9 = *(int *)(lVar15 + 0x2c);
        iVar5 = FUN_001db3c0();
        FUN_0058bd40(lVar13,uVar3,iVar9 + iVar5);
        lVar15 = FUN_0034e490();
        if ((*(char *)(lVar15 + 0x29) != '\0') && (cVar4 = FUN_0058bd30(lVar13), cVar4 != '\0')) {
          uVar11 = FUN_0056b260();
          uVar14 = FUN_00057f80(lVar13);
          uVar8 = FUN_0056c0a0(uVar11,0,uVar14);
          if ((DAT_026bc3f8 == '\0') && (iVar9 = thunk_FUN_012aa7d6(&DAT_026bc3f8), iVar9 != 0)) {
            DAT_026bc3f4 = FUN_000e4a10(s_networking_investment_peer__Fail_0163d9e6);
            thunk_FUN_012aa7e6(&DAT_026bc3f8);
          }
          uVar11 = FUN_0056ded0(uVar8);
          puVar16 = (undefined8 *)FUN_00057f80(lVar13);
          FUN_01008290(local_220,s_networking_investment_peer__Fail_0163d9e6,uVar11,*puVar16);
          FUN_000e4aa0(DAT_026bc3f4);
          DAT_026bc3f0 = FUN_000697a0();
        }
      }
      lVar17 = lVar17 + 0x18;
    } while ((int)lVar17 != 0x1e0);
  }
  if ((bVar22) || (param_1[1] == *param_1)) {
    FUN_00543ee0(param_1 + 0x66);
  }
  plVar10 = param_1 + 0x66;
  cVar4 = FUN_0012f640(plVar10);
  if ((cVar4 == '\0') && (param_1[1] != *param_1)) {
    lVar17 = FUN_0034e490();
    iVar9 = *(int *)(lVar17 + 0x2c);
    iVar5 = FUN_001db3c0();
    FUN_00543f70(plVar10,iVar9 + iVar5);
  }
  cVar4 = FUN_0012f640(plVar10);
  if (cVar4 != '\0') {
    FUN_00544000(plVar10);
  }
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

