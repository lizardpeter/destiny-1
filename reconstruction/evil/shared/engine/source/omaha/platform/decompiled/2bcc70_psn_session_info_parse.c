
undefined8 FUN_002bcc70(long param_1,long param_2)

{
  undefined8 *puVar1;
  undefined8 *puVar2;
  char cVar3;
  byte bVar4;
  byte bVar5;
  byte bVar6;
  byte bVar7;
  byte bVar8;
  byte bVar9;
  char cVar10;
  int iVar11;
  undefined8 uVar12;
  undefined8 uVar13;
  long lVar14;
  long *plVar15;
  long *plVar16;
  undefined8 *puVar17;
  long *plVar18;
  byte local_f8;
  long local_f0;
  long local_e8;
  undefined1 local_e0;
  undefined1 local_df [71];
  undefined1 local_98;
  undefined1 local_97 [71];
  long local_50;
  undefined8 local_48;
  undefined4 local_40;
  undefined1 local_3c [4];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  cVar3 = FUN_002c1b60(param_1 + 8);
  local_f8 = 0;
  if (cVar3 != '\0') {
    uVar12 = FUN_001c70e0(param_1 + 8);
    bVar4 = FUN_002bfb40(uVar12,s_sessionPrivacy_01625d79,param_2 + 0x5c0);
    bVar5 = FUN_002c1220(uVar12,s_sessionMaxUser_01625d88,param_2 + 0x5a0);
    local_e8 = 0;
    bVar6 = FUN_002c12e0(uVar12,s_sessionName_01625d97,&local_e8);
    plVar16 = (long *)(local_e8 + 8);
    if (0xf < *(ulong *)(local_e8 + 0x20)) {
      plVar16 = (long *)*plVar16;
    }
    FUN_00065030(param_2,plVar16,0x40);
    *(undefined4 *)(param_2 + 0x40) = 0;
    uVar13 = FUN_00f94250(uVar12,s_localizedSessionNames_01625fce);
    iVar11 = FUN_00f93d40(uVar13);
    if (iVar11 == 6) {
      lVar14 = FUN_00f93e70(uVar13);
      plVar16 = *(long **)(lVar14 + 8);
      plVar18 = (long *)*plVar16;
      if (plVar18 != plVar16) {
        do {
          if (*(int *)(param_2 + 0x40) == 10) break;
          plVar15 = plVar18 + 2;
          iVar11 = FUN_00f93d40(plVar15);
          if (iVar11 == 7) {
            local_df[0] = 0;
            bVar7 = FUN_002c0890(plVar15,s_npLanguage_01625fc3,&local_e0);
            local_50 = 0;
            bVar8 = FUN_002c12e0(plVar15,s_sessionName_01625d97,&local_50);
            plVar15 = (long *)(local_50 + 8);
            if (0xf < *(ulong *)(local_50 + 0x20)) {
              plVar15 = (long *)*plVar15;
            }
            FUN_00065030(local_df,plVar15,0x40);
            if ((bVar8 & bVar7) != 0) {
              iVar11 = *(int *)(param_2 + 0x40);
              *(int *)(param_2 + 0x40) = iVar11 + 1;
              thunk_FUN_012aa7c6(param_2 + 0x44 + (long)iVar11 * 0x41,&local_e0,0x41);
            }
          }
          plVar18 = (long *)*plVar18;
        } while (plVar18 != plVar16);
      }
    }
    local_f0 = 0;
    bVar7 = FUN_002c12e0(uVar12,s_sessionStatus_01625da3,&local_f0);
    plVar16 = (long *)(local_f0 + 8);
    if (0xf < *(ulong *)(local_f0 + 0x20)) {
      plVar16 = (long *)*plVar16;
    }
    FUN_00065030(param_2 + 0x2d0,plVar16,0x40);
    uVar13 = FUN_00f94250(uVar12,s_localizedSessionStatus_01625fe4);
    *(undefined4 *)(param_2 + 0x310) = 0;
    iVar11 = FUN_00f93d40(uVar13);
    if (iVar11 == 6) {
      lVar14 = FUN_00f93e70(uVar13);
      puVar2 = *(undefined8 **)(lVar14 + 8);
      puVar17 = (undefined8 *)*puVar2;
      while ((puVar17 != puVar2 && (*(int *)(param_2 + 0x310) != 10))) {
        puVar1 = puVar17 + 2;
        iVar11 = FUN_00f93d40(puVar1);
        if (iVar11 == 7) {
          local_97[0] = 0;
          bVar8 = FUN_002c0890(puVar1,s_npLanguage_01625fc3,&local_98);
          local_50 = 0;
          bVar9 = FUN_002c12e0(puVar1,s_sessionStatus_01625da3,&local_50);
          plVar16 = (long *)(local_50 + 8);
          if (0xf < *(ulong *)(local_50 + 0x20)) {
            plVar16 = (long *)*plVar16;
          }
          FUN_00065030(local_97,plVar16,0x40);
          if ((bVar9 & bVar8) != 0) {
            iVar11 = *(int *)(param_2 + 0x310);
            *(int *)(param_2 + 0x310) = iVar11 + 1;
            thunk_FUN_012aa7c6(param_2 + 0x314 + (long)iVar11 * 0x41,&local_98,0x41);
          }
        }
        puVar17 = (undefined8 *)*puVar17;
      }
    }
    bVar8 = FUN_002c1280(uVar12,s_sessionCreateTimestamp_01625db9,param_2 + 0x5b8);
    bVar9 = FUN_002c1330(uVar12,s_sessionCreator_01625dd0,param_2 + 0x5a4);
    uVar13 = FUN_00f94250(uVar12,s_members_01625db1);
    iVar11 = FUN_00f93d40(uVar13);
    local_f8 = 0;
    if (iVar11 == 6) {
      lVar14 = FUN_00f93e70(uVar13);
      puVar2 = *(undefined8 **)(lVar14 + 8);
      puVar17 = (undefined8 *)*puVar2;
      local_f8 = 1;
      while ((puVar17 != puVar2 && (*(int *)(param_2 + 0x5c8) != 0x100))) {
        puVar1 = puVar17 + 2;
        iVar11 = FUN_00f93d40(puVar1);
        if (iVar11 == 7) {
          cVar3 = FUN_002c1330(puVar1,s_onlineId_01625deb,&local_50);
          cVar10 = FUN_002c0780(puVar1,s_platform_016119d9,local_3c);
          if ((cVar3 == '\0') || (cVar10 == '\0')) goto LAB_002bd060;
          iVar11 = *(int *)(param_2 + 0x5c8);
          *(int *)(param_2 + 0x5c8) = iVar11 + 1;
          lVar14 = (long)iVar11 * 0x15;
          *(undefined1 *)(param_2 + 0x5e0 + lVar14) = local_3c[0];
          *(undefined4 *)(param_2 + 0x5dc + lVar14) = local_40;
          *(undefined8 *)(param_2 + 0x5d4 + lVar14) = local_48;
          *(long *)(param_2 + 0x5cc + lVar14) = local_50;
          puVar17 = (undefined8 *)*puVar17;
        }
        else {
LAB_002bd060:
          puVar17 = (undefined8 *)*puVar17;
        }
      }
    }
    cVar3 = FUN_002bfc50(uVar12,s_sessionType_01625ddf,(undefined1 *)(param_2 + 0x5c1));
    if (cVar3 == '\0') {
      *(undefined1 *)(param_2 + 0x5c1) = 1;
    }
    local_f8 = bVar6 & bVar5 & bVar4 & bVar7 & bVar8 & bVar9 & local_f8;
    cVar3 = FUN_002c0610(uVar12,s_availablePlatforms_01625d5c,param_2 + 0x5c2);
    if (cVar3 == '\0') {
      *(undefined1 *)(param_2 + 0x5c2) = 1;
    }
  }
  if (*DAT_01a1f100 == local_38) {
    return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),local_f8);
  }
  uVar12 = thunk_FUN_012aa7f6();
  return uVar12;
}

