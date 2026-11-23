
undefined4 * FUN_00f90b30(long *param_1)

{
  ushort uVar1;
  long *plVar2;
  long *plVar3;
  undefined8 uVar4;
  undefined8 uVar5;
  undefined8 uVar6;
  undefined8 uVar7;
  undefined8 uVar8;
  int iVar9;
  long lVar10;
  undefined8 *puVar11;
  undefined8 *puVar12;
  long lVar13;
  undefined4 *puVar14;
  long lVar15;
  ulong uVar16;
  long lVar17;
  ulong uVar18;
  ulong uVar19;
  long *plVar20;
  ulong uVar21;
  undefined8 *puVar22;
  ulong uVar23;
  ulong uVar24;
  bool bVar25;
  byte bVar26;
  undefined8 local_e0;
  undefined8 local_d8;
  undefined8 local_d0;
  undefined8 local_c8;
  undefined8 local_c0;
  undefined2 local_b8;
  undefined8 local_b0;
  undefined8 local_a8;
  undefined8 local_a0;
  undefined8 local_98;
  undefined8 local_90;
  undefined8 local_88;
  undefined8 uStack_80;
  undefined8 local_78;
  undefined8 local_70;
  undefined8 local_68;
  undefined8 local_60;
  undefined8 local_58;
  undefined8 local_50;
  undefined4 local_48;
  undefined4 local_44;
  undefined1 local_40;
  long local_38;
  
  bVar26 = 0;
  local_38 = *DAT_01a1f100;
  if (param_1 == (long *)0x0) {
    DAT_02957cb4 = -0x7faad400;
    goto LAB_00f91180;
  }
  plVar2 = (long *)param_1[0xb];
  if (plVar2 == (long *)0x0) {
    DAT_02957cb4 = -0x7faad400;
    goto LAB_00f91180;
  }
  *(undefined1 *)(param_1 + 0x10) = 1;
  plVar3 = (long *)param_1[0xe];
  uVar19 = param_1[0xf];
  local_44 = 0;
  local_88 = 0;
  uStack_80 = 0;
  local_78 = 0;
  local_40 = 1;
  local_48 = 0;
  local_50 = 0;
  local_58 = 0;
  local_60 = 0;
  local_68 = 0;
  local_70 = 0;
  DAT_02957cb4 = (**(code **)(*plVar2 + 0x10))(plVar2);
  if ((DAT_02957cb4 == 0) &&
     (((DAT_02957cb4 = FUN_00f90440(param_1), DAT_02957cb4 == 0 || (DAT_02957cb4 == -0x7faad317)) &&
      (DAT_02957cb4 = (**(code **)(*(long *)param_1[0xd] + 0x38))(), DAT_02957cb4 == 0)))) {
    DAT_02957cb4 = FUN_00f90470(param_1);
    if (DAT_02957cb4 != 0) {
LAB_00f91144:
      (**(code **)(*(long *)param_1[0xd] + 0x40))();
      goto LAB_00f9114f;
    }
    lVar10 = (**(code **)(*param_1 + 0x30))(param_1);
    plVar20 = (long *)param_1[0xd];
    if ((char)param_1[0x10] != '\0') {
      do {
        DAT_02957cb4 = (**(code **)(*plVar20 + 0x30))(plVar20,uVar19 & 0xffffffff);
        if (DAT_02957cb4 != 0) {
          if (DAT_02957cb4 != -0x7faad314) goto LAB_00f91144;
          uVar19 = param_1[0xf];
          FUN_00f96080(plVar2);
          lVar10 = (**(code **)(*param_1 + 0x30))(param_1);
        }
LAB_00f90cbc:
        do {
          iVar9 = (**(code **)(*plVar3 + 0x10))();
          *(bool *)(param_1 + 0x10) = iVar9 == 0;
          if (iVar9 != 0) break;
          DAT_02957cb4 = FUN_00f90440(param_1);
          if ((DAT_02957cb4 != 0) && (DAT_02957cb4 != -0x7faad317)) goto LAB_00f91144;
          puVar12 = (undefined8 *)param_1[7];
          puVar11 = (undefined8 *)param_1[8];
          if (puVar12 == puVar11) {
            DAT_02957cb4 = FUN_00f90470(param_1);
            bVar25 = true;
          }
          else {
            local_d0 = puVar12[2];
            local_c8 = puVar12[3];
            local_c0 = puVar12[4];
            local_b8 = *(undefined2 *)(puVar12 + 5);
            local_e0 = *puVar12;
            local_d8 = puVar12[1];
            if (0x30 < (long)puVar11 - (long)puVar12) {
              local_a0 = puVar11[-4];
              local_98 = puVar11[-3];
              local_90 = puVar11[-2];
              local_b0 = puVar11[-6];
              local_a8 = puVar11[-5];
              lVar13 = (long)puVar11 + (-0x30 - (long)puVar12);
              uVar1 = *(ushort *)(puVar11 + -1);
              lVar15 = lVar13 >> 4;
              uVar4 = *puVar12;
              uVar5 = puVar12[1];
              uVar6 = puVar12[2];
              uVar7 = puVar12[3];
              uVar8 = puVar12[4];
              *(undefined2 *)(puVar11 + -1) = *(undefined2 *)(puVar12 + 5);
              puVar11[-2] = uVar8;
              puVar11[-3] = uVar7;
              puVar11[-4] = uVar6;
              puVar11[-5] = uVar5;
              puVar11[-6] = uVar4;
              uVar16 = lVar15 * -0x5555555555555555;
              uVar21 = 0;
              uVar18 = 2;
              uVar23 = 0;
              uVar24 = uVar23;
              if (0x60 < lVar13) {
                do {
                  uVar23 = uVar21 | 1;
                  if (*(ushort *)(puVar12 + uVar18 * 6 + 5) <=
                      *(ushort *)(puVar12 + (uVar21 | 1) * 6 + 5)) {
                    uVar23 = uVar18;
                  }
                  uVar4 = puVar12[uVar23 * 6];
                  uVar5 = puVar12[uVar23 * 6 + 1];
                  uVar6 = puVar12[uVar23 * 6 + 2];
                  uVar7 = puVar12[uVar23 * 6 + 3];
                  uVar8 = puVar12[uVar23 * 6 + 4];
                  *(undefined2 *)(puVar12 + uVar24 * 6 + 5) =
                       *(undefined2 *)(puVar12 + uVar23 * 6 + 5);
                  puVar12[uVar24 * 6 + 4] = uVar8;
                  puVar12[uVar24 * 6 + 3] = uVar7;
                  puVar12[uVar24 * 6 + 2] = uVar6;
                  puVar12[uVar24 * 6 + 1] = uVar5;
                  puVar12[uVar24 * 6] = uVar4;
                  uVar21 = uVar23 * 2;
                  uVar18 = uVar23 * 2 + 2;
                  uVar24 = uVar23;
                } while (SBORROW8(uVar18,uVar16) != (long)(uVar18 + lVar15 * 0x5555555555555555) < 0
                        );
              }
              if (uVar18 == uVar16) {
                uVar16 = uVar16 - 1;
                uVar4 = puVar12[uVar16 * 6 + 3];
                uVar5 = puVar12[uVar16 * 6 + 4];
                *(undefined2 *)(puVar12 + uVar23 * 6 + 5) =
                     *(undefined2 *)(puVar12 + uVar16 * 6 + 5);
                puVar12[uVar23 * 6 + 4] = uVar5;
                puVar12[uVar23 * 6 + 3] = uVar4;
                puVar12[uVar23 * 6 + 2] = puVar12[uVar16 * 6 + 2];
                uVar4 = puVar12[uVar16 * 6];
                puVar12[uVar23 * 6 + 1] = puVar12[uVar16 * 6 + 1];
                puVar12[uVar23 * 6] = uVar4;
                uVar23 = uVar16;
              }
              if (0 < (long)uVar23) {
                do {
                  lVar13 = uVar23 - 1;
                  puVar11 = puVar12 + uVar23 * 6;
                  uVar23 = (long)((uVar23 - 1) - (lVar13 >> 0x3f)) >> 1;
                  if (*(ushort *)(puVar12 + uVar23 * 6 + 5) <= uVar1) goto LAB_00f90fb8;
                  uVar4 = puVar12[uVar23 * 6 + 3];
                  uVar5 = puVar12[uVar23 * 6 + 4];
                  *(undefined2 *)(puVar11 + 5) = *(undefined2 *)(puVar12 + uVar23 * 6 + 5);
                  puVar11[4] = uVar5;
                  puVar11[3] = uVar4;
                  puVar11[2] = puVar12[uVar23 * 6 + 2];
                  uVar4 = puVar12[uVar23 * 6];
                  puVar11[1] = puVar12[uVar23 * 6 + 1];
                  *puVar11 = uVar4;
                } while (1 < lVar13);
              }
              puVar11 = puVar12 + uVar23 * 6;
LAB_00f90fb8:
              puVar11[4] = local_90;
              puVar11[3] = local_98;
              puVar11[2] = local_a0;
              puVar11[1] = local_a8;
              *puVar11 = local_b0;
              *(ushort *)(puVar11 + 5) = uVar1;
              puVar12 = (undefined8 *)param_1[7];
              puVar11 = (undefined8 *)param_1[8];
            }
            if (puVar12 != puVar11) {
              param_1[8] = (long)(puVar11 + -6);
            }
            DAT_02957cb4 = FUN_00f90470(param_1);
            (**(code **)(*plVar2 + 0x20))(plVar2,&local_e0);
            bVar25 = false;
          }
          DAT_02957cb4 = FUN_00f90440(param_1);
          if ((DAT_02957cb4 != 0) && (DAT_02957cb4 != -0x7faad317)) goto LAB_00f91144;
          lVar13 = param_1[5];
          if (lVar13 != 0) {
            uVar18 = param_1[4];
            puVar12 = *(undefined8 **)
                       (*(long *)(*(long *)param_1[1] + 8) +
                       (*(long *)(*(long *)param_1[1] + 0x10) - 1U & uVar18) * 8);
            lVar17 = 0;
            puVar11 = puVar12;
            puVar22 = &local_88;
            for (lVar15 = 9; lVar15 != 0; lVar15 = lVar15 + -1) {
              *puVar22 = *puVar11;
              puVar11 = puVar11 + (ulong)bVar26 * -2 + 1;
              puVar22 = puVar22 + (ulong)bVar26 * -2 + 1;
            }
            lVar13 = lVar13 + -1;
            local_40 = *(undefined1 *)(puVar12 + 9);
            param_1[5] = lVar13;
            if (lVar13 != 0) {
              lVar17 = uVar18 + 1;
            }
            param_1[4] = lVar17;
            DAT_02957cb4 = FUN_00f90470(param_1);
            FUN_00f960b0(plVar2,&local_88);
            goto LAB_00f90cbc;
          }
          DAT_02957cb4 = FUN_00f90470(param_1);
        } while (!bVar25);
        lVar13 = (**(code **)(*param_1 + 0x30))(param_1);
        bVar25 = uVar19 < (ulong)(lVar13 - lVar10);
        uVar19 = uVar19 - (lVar13 - lVar10);
        if (bVar25) {
          uVar19 = 1;
        }
        iVar9 = (**(code **)(*plVar3 + 0x10))();
        *(bool *)(param_1 + 0x10) = iVar9 == 0;
        plVar20 = (long *)param_1[0xd];
      } while (iVar9 == 0);
    }
    DAT_02957cb4 = (**(code **)(*plVar20 + 0x40))();
    DAT_02957cb4 = (**(code **)(*plVar2 + 0x18))(plVar2);
    lVar10 = *param_1;
  }
  else {
LAB_00f9114f:
    DAT_02957cb4 = (**(code **)(*plVar2 + 0x18))(plVar2);
    (**(code **)(*(long *)param_1[0xe] + 0x18))((long *)param_1[0xe],1);
    lVar10 = *param_1;
  }
  (**(code **)(lVar10 + 0x28))(param_1,(long)DAT_02957cb4);
LAB_00f91180:
  if (*DAT_01a1f100 != local_38) {
    puVar14 = (undefined4 *)thunk_FUN_012aa7f6();
    return puVar14;
  }
  return &DAT_02957cb4;
}

