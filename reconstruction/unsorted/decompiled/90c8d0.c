
void FUN_0090c8d0(void)

{
  long *plVar1;
  int iVar2;
  long lVar3;
  undefined8 *puVar4;
  char cVar5;
  undefined4 uVar6;
  long lVar7;
  undefined8 uVar8;
  int *piVar9;
  long *plVar10;
  undefined8 *puVar11;
  int *piVar12;
  char *pcVar13;
  long lVar14;
  long extraout_RDX;
  long lVar15;
  long lVar16;
  long lVar17;
  undefined4 *puVar18;
  int local_208 [2];
  undefined4 local_200 [2];
  undefined4 local_1f8 [2];
  undefined4 local_1f0 [2];
  undefined4 local_1e8 [2];
  undefined4 local_1e0 [2];
  undefined1 local_1d8 [204];
  undefined4 local_10c;
  undefined4 local_108;
  undefined4 local_104;
  undefined4 local_100;
  undefined4 local_fc;
  undefined4 local_f8;
  undefined4 local_f4;
  undefined4 local_f0;
  undefined4 local_ec;
  undefined4 local_e8;
  undefined4 local_e0;
  undefined4 local_d8;
  undefined4 local_d0;
  undefined4 local_c8;
  undefined4 local_c0;
  undefined4 local_b8;
  undefined4 local_b0;
  undefined4 local_a8 [2];
  undefined4 local_a0;
  undefined4 local_98;
  undefined4 local_90;
  undefined4 local_88;
  undefined4 local_80;
  undefined4 local_78;
  undefined4 local_70 [7];
  undefined4 local_54;
  undefined4 local_50;
  undefined4 local_4c;
  undefined4 local_48;
  undefined1 local_44 [4];
  undefined1 local_40 [8];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  cVar5 = FUN_0092c710();
  if (cVar5 == '\0') {
LAB_0090c904:
    thunk_FUN_012aa986(DAT_0273ea90,0,0xb8);
    FUN_00922e00();
    FUN_00074640(DAT_0273ea80);
    *(undefined4 *)(DAT_0273ea90 + 0xb4) = 0xffffffff;
  }
  else {
    cVar5 = FUN_0092c720();
    if (cVar5 == '\0') goto LAB_0090c904;
  }
  cVar5 = FUN_0092c710();
  if (cVar5 != '\0') {
    lVar7 = FUN_0034e3c0();
    if (*(char *)(lVar7 + 0xa4) != '\0') {
      if (*(int *)(DAT_0273eaa0 + 0xe4) == 1) {
        *(undefined4 *)(DAT_0273eaa0 + 0xe4) = 2;
      }
      goto LAB_0090c987;
    }
  }
  thunk_FUN_012aa986(DAT_0273eaa0,0,0xf0);
LAB_0090c987:
  *DAT_0273ea98 = 0;
  *(undefined4 *)((long)DAT_0273ea98 + 4) = 0xffffffff;
  lVar7 = FUN_005753c0(4);
  if (lVar7 != 0) {
    cVar5 = FUN_00546f20(lVar7);
    puVar4 = DAT_0273ea98;
    if (cVar5 != '\0') {
      uVar8 = FUN_005494c0();
      piVar9 = (int *)FUN_00549d30(uVar8);
      FUN_0054b0c0(uVar8);
      uVar6 = 0xffffffff;
      if (piVar9 != (int *)0x0) {
        local_a8[0] = 0x811c9dc5;
        local_a0 = 0x811c9dc5;
        local_98 = 0x811c9dc5;
        local_90 = 0x811c9dc5;
        local_88 = 0x811c9dc5;
        local_80 = 0x811c9dc5;
        local_78 = 0x811c9dc5;
        FUN_00643fa0(local_a8);
        uVar8 = FUN_005494c0();
        lVar7 = FUN_0054c5f0(uVar8);
        plVar10 = (long *)FUN_0025a550();
        puVar11 = (undefined8 *)(**(code **)(*plVar10 + 0x268))(plVar10);
        if (((lVar7 != 0) && (puVar11 != (undefined8 *)0x0)) && (uVar8 = *puVar11, 0 < (int)uVar8))
        {
          lVar14 = 0;
          plVar10 = (long *)(lVar7 + 8);
          do {
            if (*(int *)((long)(puVar11 + 1) + lVar14 * 4 + puVar11[1] + 0x10) == piVar9[2]) {
              lVar7 = *plVar10;
              lVar15 = *(long *)((long)plVar10 + lVar14 * 0x18 + lVar7 + 0x18);
              if (0 < lVar15) {
                plVar1 = (long *)((long)plVar10 + lVar14 * 0x18 + lVar7 + 0x20);
                lVar17 = 0;
                lVar16 = 0x10;
                do {
                  lVar3 = *(long *)((long)plVar1 + lVar16 + *plVar1);
                  pcVar13 = (char *)0x0;
                  if (lVar3 != 0) {
                    pcVar13 = (char *)((long)plVar1 + lVar3 + lVar16 + *plVar1);
                  }
                  cVar5 = *pcVar13;
                  puVar18 = local_70;
                  if (((((cVar5 == *(char *)(extraout_RDX + 0xf)) ||
                        (puVar18 = local_70 + 1, cVar5 == *(char *)(extraout_RDX + 0x10))) ||
                       ((puVar18 = local_70 + 2, cVar5 == *(char *)(extraout_RDX + 0x11) ||
                        ((puVar18 = local_70 + 3, cVar5 == *(char *)(extraout_RDX + 0x12) ||
                         (puVar18 = local_70 + 4, cVar5 == *(char *)(extraout_RDX + 0x13))))))) ||
                      (puVar18 = local_70 + 5, cVar5 == *(char *)(extraout_RDX + 0x14))) ||
                     (puVar18 = local_70 + 6, cVar5 == *(char *)(extraout_RDX + 0x15))) {
                    local_1e0[0] = *(undefined4 *)(pcVar13 + *(long *)(pcVar13 + 0x10) + 0x20);
                    uVar6 = FUN_0058ea60(local_1e0);
                    *puVar18 = uVar6;
                    lVar15 = *(long *)((long)plVar10 + lVar14 * 0x18 + lVar7 + 0x18);
                  }
                  lVar16 = lVar16 + 8;
                  lVar17 = lVar17 + 1;
                } while (lVar17 < lVar15);
                uVar8 = *puVar11;
              }
            }
            lVar14 = lVar14 + 1;
          } while (lVar14 < (int)uVar8);
        }
        uVar8 = FUN_005494c0();
        lVar7 = FUN_0054c6f0(uVar8);
        plVar10 = (long *)FUN_0025a550();
        piVar12 = (int *)(**(code **)(*plVar10 + 0x278))(plVar10);
        if (((lVar7 != 0) && (piVar12 != (int *)0x0)) && (0 < *piVar12)) {
          plVar10 = (long *)(lVar7 + 8);
          lVar7 = 0;
          do {
            iVar2 = *(int *)((long)(piVar12 + 2) + lVar7 * 4 + *(long *)(piVar12 + 2) + 0x10);
            lVar14 = *plVar10;
            if (iVar2 == piVar9[3]) {
              uVar8 = FUN_0033fa20();
              local_1e8[0] = *(undefined4 *)((long)plVar10 + lVar7 * 4 + lVar14 + 0x10);
              local_54 = FUN_0033fc20(uVar8,local_1e8);
            }
            else if (iVar2 == piVar9[4]) {
              uVar8 = FUN_0033fa20();
              local_1f0[0] = *(undefined4 *)((long)plVar10 + lVar7 * 4 + lVar14 + 0x10);
              local_50 = FUN_0033fc20(uVar8,local_1f0);
            }
            else if (iVar2 == piVar9[5]) {
              uVar8 = FUN_0033fa20();
              local_1f8[0] = *(undefined4 *)((long)plVar10 + lVar7 * 4 + lVar14 + 0x10);
              local_4c = FUN_0033fc20(uVar8,local_1f8);
            }
            lVar7 = lVar7 + 1;
          } while (lVar7 < *piVar12);
        }
        uVar8 = FUN_005494c0();
        lVar7 = FUN_0054c7f0(uVar8);
        plVar10 = (long *)FUN_0025a550();
        piVar12 = (int *)(**(code **)(*plVar10 + 0x288))(plVar10);
        if ((lVar7 != 0) && (piVar12 != (int *)0x0)) {
          lVar15 = 0;
          lVar14 = -4;
          do {
            lVar16 = lVar14;
            if (*piVar12 <= lVar15) goto LAB_0090cdc6;
            lVar17 = lVar15 * 4;
            lVar15 = lVar15 + 1;
            lVar14 = lVar16 + 8;
          } while (*(int *)((long)(piVar12 + 2) + lVar17 + *(long *)(piVar12 + 2) + 0x10) != *piVar9
                  );
          lVar14 = *(long *)(lVar7 + 8);
          uVar8 = FUN_0033fa20();
          local_200[0] = *(undefined4 *)(lVar14 + lVar7 + 0x28 + lVar16 * 4);
          uVar6 = FUN_0033fc20(uVar8,local_200);
          local_208[0] = piVar9[1];
          FUN_00672cf0(uVar6,local_208,local_44,local_40);
        }
LAB_0090cdc6:
        local_48 = 0;
        local_10c = 0;
        local_108 = 0x811c9dc5;
        local_104 = 0x811c9dc5;
        local_100 = 0x811c9dc5;
        local_fc = 0x811c9dc5;
        local_f8 = 0x811c9dc5;
        local_f4 = 0x811c9dc5;
        local_f0 = 0x811c9dc5;
        local_ec = 0x811c9dc5;
        local_e8 = 0x811c9dc5;
        local_e0 = 0x811c9dc5;
        local_d8 = 0x811c9dc5;
        local_d0 = 0x811c9dc5;
        local_c8 = 0x811c9dc5;
        local_c0 = 0x811c9dc5;
        local_b8 = 0x811c9dc5;
        local_b0 = 0x811c9dc5;
        FUN_00644040(local_a8,local_1d8);
        uVar6 = FUN_0063fb20(1,local_1d8);
      }
      *(undefined4 *)((long)puVar4 + 4) = uVar6;
    }
  }
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

