
void FUN_008ed0f0(float param_1,long *param_2)

{
  char cVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  uint uVar7;
  undefined4 uVar8;
  ulong uVar9;
  undefined8 *puVar10;
  long *plVar11;
  long lVar12;
  long lVar13;
  long lVar14;
  undefined8 uVar15;
  long *plVar16;
  long *plVar17;
  byte bVar18;
  bool bVar19;
  byte bVar20;
  float fVar21;
  float fVar22;
  undefined1 auVar23 [16];
  undefined4 local_b0;
  int local_a8 [2];
  uint local_a0;
  undefined4 uStack_9c;
  long local_98;
  long local_40;
  long local_38;
  
  bVar20 = 0;
  local_38 = *DAT_01a1f100;
  uVar8 = (undefined4)param_2[0x69];
  uVar2 = FUN_009236b0(uVar8);
  iVar3 = FUN_009236d0(uVar8);
  if ((iVar3 != -1) && ((int)param_2[0x6b] != 0)) {
    param_2[0x6b] = 0;
  }
  FUN_004cbcc0(iVar3,local_a8);
  lVar14 = 0;
  if (local_a0 != 0xffffffff) {
    lVar12 = (ulong)(((uint)((int)local_a0 >> 0xd) >> 0x12 | 0x3ff) & (int)local_a0 >> 0xd) * 0x40;
    lVar14 = *DAT_01a238a0;
    lVar13 = *(long *)(lVar14 + 0x10 + lVar12);
    uVar9 = (ulong)((local_a0 & 0x1fff) * *(int *)(lVar14 + 0x30 + lVar12));
    lVar14 = ((lVar13 + uVar9) -
             ((long)*(int *)(lVar14 + 0x34 + lVar12) & *(ulong *)(lVar13 + 8 + uVar9))) + local_98;
  }
  cVar1 = FUN_008e3b80();
  if (cVar1 == '\0') {
    puVar10 = (undefined8 *)FUN_001c0900(param_2);
    iVar4 = (**(code **)*puVar10)(puVar10);
    if ((iVar4 != 9) && (cVar1 = FUN_000014d0(), cVar1 == '\0')) {
      if (iVar3 == -1) {
        cVar1 = FUN_009070e0();
        if (cVar1 == '\0') {
          if ((int)param_2[0x6b] == 0) {
            param_2[0x6b] = 1;
          }
        }
        else if ((int)param_2[0x6b] != 5) {
          param_2[0x6b] = 5;
        }
        *(float *)((long)param_2 + 0x35c) = param_1 + *(float *)((long)param_2 + 0x35c);
        plVar11 = (long *)FUN_001c0900(param_2);
        iVar3 = (**(code **)(*plVar11 + 0x18))(plVar11);
        if (iVar3 == -1) {
          puVar10 = (undefined8 *)FUN_001c0900(param_2);
          iVar5 = (**(code **)*puVar10)(puVar10);
          iVar4 = 1;
          bVar19 = true;
          if (iVar5 == 5) goto LAB_008ed3ae;
LAB_008ed657:
          auVar23 = FUN_008ed8d0(param_2,(int)param_2[0x6b],uVar2,iVar4);
          if ((int)param_2[0x6b] != auVar23._0_4_) {
            *(int *)(param_2 + 0x6b) = auVar23._0_4_;
            *(undefined4 *)((long)param_2 + 0x35c) = 0;
          }
          local_b0 = auVar23._8_4_;
          bVar18 = auVar23[0xc] & 1;
          iVar4 = auVar23._4_4_;
        }
        else {
          uVar6 = FUN_006ed8f0(iVar3);
          bVar19 = false;
          if (uVar6 != 0xffffffff) {
            uVar7 = FUN_00337e80((ulong)((uVar6 & 0x1fff) * DAT_02692230) + DAT_02692228);
            cVar1 = FUN_003068a0((ulong)((uVar7 & 0x1fff) * DAT_02692230) + DAT_02692228);
            iVar4 = 1;
            if ((cVar1 == '\0') || (cVar1 = FUN_008e4760(uVar6), cVar1 == '\0')) goto LAB_008ed657;
          }
LAB_008ed3ae:
          fVar21 = *(float *)((long)param_2 + 0x35c);
          iVar4 = (int)param_2[0x6b];
          puVar10 = (undefined8 *)FUN_001c0900(param_2);
          if (iVar4 == 3) {
            iVar4 = 1;
            if (!bVar19) goto LAB_008ed58f;
            goto LAB_008ed657;
          }
          if (iVar4 == 2) {
            lVar14 = FUN_00526f80();
            if (lVar14 != 0) {
              fVar22 = *(float *)(lVar14 + 0x84);
joined_r0x008ed589:
              iVar4 = 1;
              if (fVar22 < fVar21) goto LAB_008ed657;
            }
          }
          else if (iVar4 == 1) {
            lVar14 = FUN_00526f80();
            iVar4 = (**(code **)*puVar10)(puVar10);
            if (iVar4 == 5) {
              iVar4 = FUN_008e1a30(puVar10);
              fVar22 = *(float *)(lVar14 + 0x5c);
              if (iVar4 != -1) goto joined_r0x008ed589;
            }
            else {
              fVar22 = *(float *)(lVar14 + 0x5c);
            }
            fVar22 = fVar22 + *(float *)(lVar14 + 0x84);
            goto joined_r0x008ed589;
          }
LAB_008ed58f:
          if (((((int)param_2[0x6b] - 1U < 2) &&
               (fVar21 = *(float *)((long)param_2 + 0x35c), lVar14 = FUN_00526f80(),
               *(float *)(lVar14 + 0x60) < fVar21)) && (iVar4 = FUN_00945900(uVar8), iVar4 != -1))
             && (cVar1 = FUN_008de9d0(iVar4), cVar1 == '\0')) {
            lVar14 = FUN_00928560(iVar4);
            lVar13 = 0;
            iVar4 = 1;
            do {
              if (1 < (int)lVar13) goto LAB_008ed60e;
              fVar21 = *(float *)(lVar14 + 0x2ac + lVar13 * 4);
              lVar13 = lVar13 + 1;
            } while (fVar21 * fVar21 <= 0.0);
            goto LAB_008ed657;
          }
LAB_008ed60e:
          if (((1 < (int)param_2[0x6b] - 1U) ||
              (fVar21 = *(float *)((long)param_2 + 0x35c), lVar14 = FUN_00526f80(),
              *(float *)(lVar14 + 100) < fVar21)) && (iVar4 = FUN_008e5480(param_2), iVar4 != 0))
          goto LAB_008ed657;
          bVar18 = 0;
          local_b0 = 0;
          iVar4 = iVar3;
        }
        FUN_008e5c30(param_2);
        if (iVar4 == -1) {
          cVar1 = FUN_009083b0(4);
          if (cVar1 == '\0') {
            cVar1 = (**(code **)(*param_2 + 0x58))(0,param_2,5);
            if ((cVar1 != '\0') || (cVar1 = FUN_004cca20(), cVar1 == '\0')) {
              FUN_004cca10();
            }
          }
          else {
            puVar10 = (undefined8 *)FUN_001c0900(param_2);
            (**(code **)*puVar10)(puVar10);
          }
          goto LAB_008ed508;
        }
        iVar5 = (int)param_2[0x6b];
        cVar1 = FUN_00bcf9e0(iVar4);
        if (cVar1 == '\0') {
LAB_008ed708:
          uVar15 = 5;
          if ((iVar5 != 1) && (iVar5 != 5)) {
            if (iVar5 == 4) {
              uVar15 = 7;
            }
            else {
              uVar15 = 1;
            }
          }
        }
        else {
          cVar1 = FUN_00bd0ae0(iVar4);
          uVar15 = 5;
          if (cVar1 == '\0') goto LAB_008ed708;
        }
        cVar1 = (**(code **)(*param_2 + 0x58))(local_b0,param_2,uVar15);
        if ((iVar4 == iVar3) && (cVar1 != '\x01')) goto LAB_008ed508;
        puVar10 = (undefined8 *)FUN_001c0900(param_2);
        iVar5 = (**(code **)*puVar10)(puVar10);
        if (iVar5 == 6) {
          plVar11 = (long *)FUN_001c0900(param_2);
          (**(code **)(*plVar11 + 0x28))(plVar11,iVar4);
          uVar8 = FUN_006ed8f0(iVar3);
          FUN_00072050(&local_40,uVar8);
          *(long *)((long)plVar11 + 0xcc) = local_40;
LAB_008ed825:
          FUN_008f7430(*(undefined4 *)((long)param_2 + 0x17c),plVar11);
          plVar16 = param_2 + 0x58;
          plVar17 = plVar11 + 0xf;
          for (lVar14 = 0x13; lVar14 != 0; lVar14 = lVar14 + -1) {
            *(int *)plVar17 = (int)*plVar16;
            plVar16 = (long *)((long)plVar16 + (ulong)bVar20 * -8 + 4);
            plVar17 = (long *)((long)plVar17 + (ulong)bVar20 * -8 + 4);
          }
          if (bVar18 == 0) {
            (**(code **)(*plVar11 + 0x48))(plVar11,(long)param_2 + 0x18c);
            goto LAB_008ed508;
          }
        }
        else {
          if (iVar5 == 5) {
            plVar11 = (long *)FUN_001c0900(param_2);
            (**(code **)(*plVar11 + 0x28))(plVar11,iVar4);
            (**(code **)(*plVar11 + 0x48))(plVar11,(long)param_2 + 0x18c);
          }
          else if (iVar5 == 1) {
            plVar11 = (long *)FUN_001c0900(param_2);
            (**(code **)(*plVar11 + 0x28))(plVar11,iVar4);
            goto LAB_008ed825;
          }
          if (bVar18 == 0) goto LAB_008ed508;
        }
        uVar15 = FUN_001c0900(param_2);
        FUN_008ded80(uVar15);
        goto LAB_008ed508;
      }
      iVar4 = FUN_008e5e70(iVar3);
      FUN_008e3110(param_2,uVar2);
      plVar11 = (long *)FUN_001c0900(param_2);
      iVar5 = (**(code **)(*plVar11 + 0x18))(plVar11);
      if (iVar5 != iVar3) {
        plVar11 = (long *)FUN_001c0900(param_2);
        (**(code **)(*plVar11 + 0x28))(plVar11,iVar3);
      }
      if (iVar4 == 0) {
        uVar8 = DAT_0166a778;
        if (lVar14 != 0) {
          uVar8 = *(undefined4 *)(lVar14 + 0x20);
        }
        uVar2 = 0;
        if (iVar5 == iVar3) {
          uVar2 = uVar8;
        }
        lVar14 = *param_2;
        uVar15 = 4;
LAB_008ed4cc:
        (**(code **)(lVar14 + 0x58))(uVar2,param_2,uVar15);
      }
      else {
        puVar10 = (undefined8 *)FUN_001c0900(param_2);
        iVar3 = (**(code **)*puVar10)(puVar10);
        iVar4 = FUN_00071f60(param_2 + 0x6d);
        bVar19 = lVar14 != 0;
        if (((iVar4 != -1) && (bVar19 = true, iVar4 == local_a8[0])) &&
           (*(uint *)(param_2 + 0x6e) == local_a0)) {
          bVar19 = param_2[0x6f] != local_98;
        }
        uVar8 = DAT_0166a778;
        if (lVar14 != 0) {
          uVar8 = *(undefined4 *)(lVar14 + 0x20);
        }
        if (!bVar19) {
          uVar2 = 0;
          if (iVar3 != 0xc) {
            uVar2 = uVar8;
          }
          lVar14 = *param_2;
          uVar15 = 0;
          goto LAB_008ed4cc;
        }
        FUN_008e4ed0(param_2,0);
      }
      FUN_00072050(&local_40,local_a8[0]);
      param_2[0x6d] = local_40;
      param_2[0x6f] = local_98;
      param_2[0x6e] = CONCAT44(uStack_9c,local_a0);
    }
  }
  FUN_000014d0(param_2);
LAB_008ed508:
  iVar3 = FUN_0010c430();
  if ((iVar3 == 7) || (fVar21 = 0.0, iVar3 == 9)) {
    fVar21 = param_1 + *(float *)(param_2 + 0x6c);
  }
  *(float *)(param_2 + 0x6c) = fVar21;
  FUN_008e3e60(param_1,param_2);
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

