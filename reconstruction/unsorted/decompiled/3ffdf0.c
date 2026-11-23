
void FUN_003ffdf0(int *param_1,long param_2)

{
  ulong uVar1;
  bool bVar2;
  int iVar3;
  int iVar4;
  long lVar5;
  float *pfVar6;
  uint uVar7;
  float fVar8;
  long lVar9;
  int *piVar10;
  int iVar11;
  float fVar12;
  ulong uVar13;
  long lVar14;
  ulong uVar15;
  long lVar16;
  float fVar17;
  undefined1 auVar18 [64];
  float fVar19;
  float local_1c0 [70];
  int local_a8;
  int aiStack_a4 [17];
  long local_60;
  
  local_60 = *DAT_01a1f100;
  uVar7 = param_1[0x1354] >> 0xd;
  lVar16 = *DAT_01a238a0;
  iVar11 = -1;
  lVar5 = (ulong)((uVar7 >> 0x12 | 0x3ff) & uVar7) * 0x40;
  lVar9 = *(long *)(lVar16 + 0x10 + lVar5);
  iVar4 = *(int *)(lVar16 + 0x34 + lVar5);
  uVar13 = (ulong)((param_1[0x1354] & 0x1fffU) * *(int *)(lVar16 + 0x30 + lVar5));
  uVar1 = *(ulong *)(lVar9 + 8 + uVar13);
  local_a8 = *param_1;
  if (0 < local_a8) {
    piVar10 = param_1 + 4;
    iVar11 = -1;
    lVar16 = 0;
    do {
      uVar7 = FUN_00303410(piVar10);
      lVar5 = DAT_02689588;
      if (uVar7 == 0xffffffff) {
        aiStack_a4[lVar16] = -1;
      }
      else {
        uVar15 = (ulong)((uVar7 & 0x1fff) * DAT_02689590);
        iVar3 = FUN_00301c80(DAT_02689588 + uVar15);
        aiStack_a4[lVar16] = iVar3;
        if ((*(byte *)(lVar5 + 0x40 + uVar15) & 1) != 0) {
          iVar11 = iVar3;
        }
      }
      piVar10 = piVar10 + 0x128;
      lVar16 = lVar16 + 1;
    } while ((int)lVar16 < *param_1);
  }
  lVar9 = (lVar9 + uVar13) - ((long)iVar4 & uVar1);
  *(undefined4 *)(param_2 + 0x47f8) = 2;
  lVar16 = 0;
  do {
    local_1c0[0x38] = 0.0;
    local_1c0[0x39] = 0.0;
    local_1c0[0x3a] = 0.0;
    local_1c0[0x3b] = 0.0;
    local_1c0[0x3c] = 0.0;
    local_1c0[0x3d] = 0.0;
    local_1c0[0x3e] = 0.0;
    local_1c0[0x3f] = 0.0;
    local_1c0[0x30] = 0.0;
    local_1c0[0x31] = 0.0;
    local_1c0[0x32] = 0.0;
    local_1c0[0x33] = 0.0;
    local_1c0[0x34] = 0.0;
    local_1c0[0x35] = 0.0;
    local_1c0[0x36] = 0.0;
    local_1c0[0x37] = 0.0;
    local_1c0[0x28] = 0.0;
    local_1c0[0x29] = 0.0;
    local_1c0[0x2a] = 0.0;
    local_1c0[0x2b] = 0.0;
    local_1c0[0x2c] = 0.0;
    local_1c0[0x2d] = 0.0;
    local_1c0[0x2e] = 0.0;
    local_1c0[0x2f] = 0.0;
    local_1c0[0x20] = 0.0;
    local_1c0[0x21] = 0.0;
    local_1c0[0x22] = 0.0;
    local_1c0[0x23] = 0.0;
    local_1c0[0x24] = 0.0;
    local_1c0[0x25] = 0.0;
    local_1c0[0x26] = 0.0;
    local_1c0[0x27] = 0.0;
    local_1c0[0x18] = 0.0;
    local_1c0[0x19] = 0.0;
    local_1c0[0x1a] = 0.0;
    local_1c0[0x1b] = 0.0;
    local_1c0[0x1c] = 0.0;
    local_1c0[0x1d] = 0.0;
    local_1c0[0x1e] = 0.0;
    local_1c0[0x1f] = 0.0;
    local_1c0[0x10] = 0.0;
    local_1c0[0x11] = 0.0;
    local_1c0[0x12] = 0.0;
    local_1c0[0x13] = 0.0;
    local_1c0[0x14] = 0.0;
    local_1c0[0x15] = 0.0;
    local_1c0[0x16] = 0.0;
    local_1c0[0x17] = 0.0;
    local_1c0[8] = 0.0;
    local_1c0[9] = 0.0;
    local_1c0[10] = 0.0;
    local_1c0[0xb] = 0.0;
    local_1c0[0xc] = 0.0;
    local_1c0[0xd] = 0.0;
    local_1c0[0xe] = 0.0;
    local_1c0[0xf] = 0.0;
    local_1c0[0] = 0.0;
    local_1c0[1] = 0.0;
    local_1c0[2] = 0.0;
    local_1c0[3] = 0.0;
    local_1c0[4] = 0.0;
    local_1c0[5] = 0.0;
    local_1c0[6] = 0.0;
    local_1c0[7] = 0.0;
    local_1c0[0x40] = 0.0;
    fVar12 = 0.0;
    iVar4 = FUN_0010c990();
    lVar5 = 0;
    iVar3 = (int)(lVar16 + 1);
    bVar2 = false;
    if (*(long *)(lVar9 + 0x40) < 1) {
      fVar17 = 0.0;
    }
    else {
      do {
        fVar17 = 0.0;
        if (*(char *)(lVar9 + 0x48 + lVar5 * 0x14 + *(long *)(lVar9 + 0x48) + 0x1d) == iVar3) {
          lVar14 = 0;
          piVar10 = param_1 + 8;
          fVar17 = DAT_0162f958;
          if (0 < *param_1) {
            do {
              if (((iVar11 == aiStack_a4[lVar14]) && ((int)lVar5 < piVar10[-1])) &&
                 (((float)piVar10[lVar5] != 0.0 || (NAN((float)piVar10[lVar5]))))) {
                fVar17 = fVar17 + DAT_0162f95c;
              }
              lVar14 = lVar14 + 1;
              piVar10 = piVar10 + 0x128;
            } while ((int)lVar14 < *param_1);
          }
        }
        lVar14 = (long)(int)local_1c0[0];
        fVar12 = (float)((int)local_1c0[0] + 1);
        local_1c0[0] = fVar12;
        local_1c0[lVar14 + 1] = fVar17;
        lVar5 = lVar5 + 1;
      } while (lVar5 < *(long *)(lVar9 + 0x40));
      auVar18 = ZEXT1664(ZEXT816(0) << 0x40);
      fVar17 = 0.0;
      if (0 < (int)fVar12) {
        lVar5 = 0;
        do {
          fVar17 = auVar18._0_4_ + local_1c0[lVar5 + 1];
          auVar18 = ZEXT464((uint)fVar17);
          lVar5 = lVar5 + 1;
          bVar2 = 0 < (int)fVar12;
        } while (fVar12 != (float)lVar5);
      }
    }
    lVar5 = 0xffffffff;
    if (bVar2) {
      fVar19 = 0.0;
      pfVar6 = local_1c0;
      fVar8 = fVar12;
      do {
        pfVar6 = pfVar6 + 1;
        fVar19 = fVar19 + *pfVar6;
        fVar8 = (float)((int)fVar8 + -1);
      } while (fVar8 != 0.0);
      if (0.0 < fVar19) {
        lVar14 = (long)(int)fVar12;
        do {
          pfVar6 = local_1c0 + lVar14;
          lVar14 = lVar14 + -1;
        } while (*pfVar6 == 0.0);
        lVar5 = 0;
        if (0 < (int)lVar14) {
          lVar5 = 0;
          fVar12 = 0.0;
          do {
            fVar19 = local_1c0[lVar5 + 1];
            if (((fVar19 != 0.0) || (NAN(fVar19))) &&
               (fVar12 = fVar12 + fVar19,
               (float)(iVar4 * 0x19660d + 0x3c6ef35fU >> 0x10) * DAT_0162f960 * fVar17 + 0.0 <=
               fVar12)) break;
            lVar5 = lVar5 + 1;
          } while ((int)lVar5 < (int)lVar14);
        }
      }
    }
    *(int *)(param_2 + 0x47fc + lVar16 * 4) = (int)lVar5;
    lVar16 = lVar16 + 1;
    if (iVar3 == 2) {
      if (*DAT_01a1f100 == local_60) {
        return;
      }
      thunk_FUN_012aa7f6();
      return;
    }
  } while( true );
}

