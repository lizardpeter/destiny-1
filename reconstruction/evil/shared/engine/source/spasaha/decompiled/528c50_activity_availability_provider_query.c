
undefined8 FUN_00528c50(int param_1,undefined8 *param_2,ulong param_3,undefined8 *param_4)

{
  float fVar1;
  float fVar2;
  ulong uVar3;
  undefined8 uVar4;
  float *pfVar5;
  ulong uVar6;
  int iVar7;
  long lVar8;
  uint uVar9;
  long lVar10;
  long lVar11;
  long lVar12;
  bool bVar13;
  undefined1 auVar14 [64];
  float fVar15;
  float local_48;
  float local_44;
  float local_40;
  float local_3c;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  lVar11 = 0;
  if (DAT_026b0a78 != 0xffffffff) {
    lVar8 = (ulong)(((uint)((int)DAT_026b0a78 >> 0xd) >> 0x12 | 0x3ff) & (int)DAT_026b0a78 >> 0xd) *
            0x40;
    lVar11 = *DAT_01a238a0;
    lVar12 = *(long *)(lVar11 + 0x10 + lVar8);
    uVar3 = (ulong)((DAT_026b0a78 & 0x1fff) * *(int *)(lVar11 + 0x30 + lVar8));
    lVar11 = (lVar12 + uVar3) -
             ((long)*(int *)(lVar11 + 0x34 + lVar8) & *(ulong *)(lVar12 + 8 + uVar3));
  }
  pfVar5 = &local_44;
  FUN_00528f90(*param_2,param_2[1],*param_4,1,param_1,param_3,0,0,pfVar5,&local_48);
  iVar7 = (int)param_3;
  bVar13 = iVar7 == 1;
  uVar9 = (int)DAT_026b0a78 >> 0xd;
  if ((param_1 == 1) || (!bVar13)) {
    uVar4 = 2;
    if (DAT_026b0a78 == 0xffffffff) goto LAB_00528f67;
    lVar10 = (ulong)((uVar9 >> 0x12 | 0x3ff) & uVar9) * 0x40;
    lVar12 = *DAT_01a238a0;
    lVar8 = *(long *)(lVar12 + 0x10 + lVar10);
    uVar3 = (ulong)((DAT_026b0a78 & 0x1fff) * *(int *)(lVar12 + 0x30 + lVar10));
    lVar12 = (lVar8 + uVar3) -
             ((long)*(int *)(lVar12 + 0x34 + lVar10) & *(ulong *)(lVar8 + 8 + uVar3));
    if (lVar12 == 0) goto LAB_00528f67;
    if (param_1 == 1 && bVar13) {
      lVar12 = lVar12 + 0x40;
    }
    else if (iVar7 != 1 && param_1 == 1) {
      lVar12 = lVar12 + 0xe8;
    }
    else {
      lVar12 = lVar12 + 0x238;
    }
  }
  else {
    uVar4 = 2;
    if (DAT_026b0a78 == 0xffffffff) goto LAB_00528f67;
    lVar10 = (ulong)((uVar9 >> 0x12 | 0x3ff) & uVar9) * 0x40;
    lVar12 = *DAT_01a238a0;
    lVar8 = *(long *)(lVar12 + 0x10 + lVar10);
    uVar3 = (ulong)((DAT_026b0a78 & 0x1fff) * *(int *)(lVar12 + 0x30 + lVar10));
    lVar12 = (lVar8 + uVar3) -
             ((long)*(int *)(lVar12 + 0x34 + lVar10) & *(ulong *)(lVar8 + 8 + uVar3));
    if (lVar12 == 0) goto LAB_00528f67;
    lVar12 = lVar12 + 0xe8;
    pfVar5 = &local_48;
  }
  uVar4 = 2;
  if (lVar11 != 0) {
    fVar1 = *pfVar5;
    FUN_00528f90(*param_2,param_2[1],1,param_1,param_3 & 0xffffffff,0,0,&local_3c,&local_40);
    if ((param_1 == 1) || (iVar7 != 1)) {
      local_3c = local_40 - local_3c;
    }
    else {
      local_3c = local_3c - local_40;
    }
    uVar3 = 0;
    if (0 < *(long *)(lVar12 + 8)) {
      pfVar5 = (float *)(*(long *)(lVar12 + 0x10) + 0x28 + lVar12);
      auVar14 = ZEXT464(0) << 0x40;
      lVar8 = 0;
      fVar15 = 0.0;
      do {
        uVar3 = auVar14._0_8_;
        fVar2 = pfVar5[-2];
        if (fVar1 < fVar2) {
          if (DAT_016384a8 < fVar2 - fVar15) {
            uVar3 = (ulong)(uint)(auVar14._0_4_ +
                                 ((fVar1 - fVar15) / (fVar2 - fVar15)) * (*pfVar5 - auVar14._0_4_));
          }
          break;
        }
        auVar14 = ZEXT464((uint)*pfVar5);
        uVar3 = (ulong)(uint)*pfVar5;
        pfVar5 = pfVar5 + 3;
        lVar8 = lVar8 + 1;
        fVar15 = fVar2;
      } while (lVar8 < *(long *)(lVar12 + 8));
    }
    if (param_1 == 1 && bVar13) {
      uVar9 = *(uint *)(lVar11 + 0x2e4);
    }
    else {
      uVar9 = *(uint *)(lVar11 + 0x2e0);
    }
    bVar13 = true;
    lVar11 = 0;
    if (uVar9 != 0xffffffff) {
      lVar8 = (ulong)(((uint)((int)uVar9 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar9 >> 0xd) * 0x40;
      lVar11 = *DAT_01a238a0;
      lVar12 = *(long *)(lVar11 + 0x10 + lVar8);
      uVar6 = (ulong)((uVar9 & 0x1fff) * *(int *)(lVar11 + 0x30 + lVar8));
      lVar11 = (lVar12 + uVar6) -
               ((long)*(int *)(lVar11 + 0x34 + lVar8) & *(ulong *)(lVar12 + 8 + uVar6));
      bVar13 = lVar11 == 0;
    }
    lVar11 = lVar11 + 8;
    if (bVar13) {
      lVar11 = 0;
    }
    uVar4 = FUN_002670d0(local_3c,uVar3,lVar11);
  }
LAB_00528f67:
  if (*DAT_01a1f100 != local_38) {
    uVar4 = thunk_FUN_012aa7f6();
    return uVar4;
  }
  return uVar4;
}

