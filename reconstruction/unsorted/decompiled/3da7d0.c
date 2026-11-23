
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_003da7d0(undefined8 param_1,long param_2)

{
  undefined4 uVar1;
  undefined1 uVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  undefined4 uVar6;
  long lVar7;
  undefined8 uVar8;
  long lVar9;
  ulong uVar10;
  byte *pbVar11;
  ulong uVar12;
  byte bVar13;
  long lVar14;
  long extraout_RDX;
  undefined8 extraout_RDX_00;
  long lVar15;
  float fVar16;
  float fVar17;
  undefined8 extraout_XMM0_Qa;
  undefined1 auVar18 [16];
  undefined1 extraout_var [56];
  undefined4 local_48 [2];
  undefined4 local_40 [2];
  long local_38;
  undefined1 auVar19 [64];
  
  local_38 = *DAT_01a1f100;
  iVar3 = FUN_009236b0(0);
  *(undefined1 *)(param_2 + 0x24) = 0;
  if (iVar3 != -1) {
    uVar4 = FUN_001320f0();
    uVar2 = FUN_00918650(iVar3);
    *(undefined1 *)(param_2 + 0x24) = uVar2;
    iVar5 = FUN_009185e0(iVar3);
    auVar19._8_56_ = extraout_var;
    auVar19._0_8_ = extraout_XMM0_Qa;
    auVar18._0_4_ = (float)iVar5;
    auVar18._4_12_ = auVar19._4_12_;
    fVar16 = (float)thunk_FUN_005916e0(auVar18._0_8_);
    *(float *)(param_2 + 0x28) = fVar16;
    *(undefined4 *)(param_2 + 0x2c) = 0x40a00000;
    if (uVar4 != 0xffffffff) {
      lVar7 = (ulong)(((uint)((int)uVar4 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar4 >> 0xd) * 0x40;
      lVar9 = *DAT_01a238a0;
      lVar15 = *(long *)(lVar9 + 0x10 + lVar7);
      uVar10 = (ulong)((uVar4 & 0x1fff) * *(int *)(lVar9 + 0x30 + lVar7));
      fVar17 = *(float *)(((lVar15 + uVar10) -
                          ((long)*(int *)(lVar9 + 0x34 + lVar7) & *(ulong *)(lVar15 + 8 + uVar10)))
                         + 8);
      if ((fVar17 != 0.0) || (NAN(fVar17))) {
        *(float *)(param_2 + 0x2c) = fVar17;
      }
    }
    if (*(char *)(param_2 + 0x24) != '\0') {
      if (fVar16 + DAT_0162e60c < 0.0) {
        fVar16 = _DAT_0162e610;
      }
      *(float *)(param_2 + 0x28) = fVar16;
    }
  }
  uVar8 = FUN_003f6020();
  fVar16 = (float)FUN_003f63a0(uVar8);
  *(undefined1 *)(param_2 + 0x30) = 0;
  if (0.0 < fVar16) {
    uVar8 = FUN_003f6020();
    fVar17 = (float)FUN_003f63c0(uVar8);
    *(float *)(param_2 + 0x38) = fVar17;
    *(float *)(param_2 + 0x34) = fVar16;
    if (fVar16 < fVar17) {
      *(undefined1 *)(param_2 + 0x30) = 1;
    }
  }
  *(undefined1 **)(param_2 + 0x48) = &DAT_811c9dc5ffffffff;
  lVar9 = FUN_0075d410();
  if ((lVar9 != 0) && (uVar4 = *(uint *)(lVar9 + 0x20), uVar4 != 0xffffffff)) {
    lVar14 = (ulong)(((uint)((int)uVar4 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar4 >> 0xd) * 0x40;
    lVar15 = *DAT_01a238a0;
    lVar7 = *(long *)(lVar15 + 0x10 + lVar14);
    uVar10 = (ulong)((uVar4 & 0x1fff) * *(int *)(lVar15 + 0x30 + lVar14));
    lVar15 = (lVar7 + uVar10) -
             ((long)*(int *)(lVar15 + 0x34 + lVar14) & *(ulong *)(lVar7 + 8 + uVar10));
    uVar1 = *(undefined4 *)(lVar15 + 0x28);
    uVar8 = FUN_003430b0();
    uVar6 = FUN_00345620(uVar8);
    FUN_002a1fb0(local_40,lVar9,uVar6);
    *(undefined4 *)(param_2 + 0x48) = uVar1;
    *(undefined4 *)(param_2 + 0x4c) = local_40[0];
    uVar6 = *(undefined4 *)(lVar15 + 0x20);
    *(undefined4 *)(param_2 + 0x50) = uVar1;
    *(undefined4 *)(param_2 + 0x54) = uVar6;
    uVar2 = FUN_0075f000();
    *(undefined1 *)(param_2 + 0x5c) = uVar2;
    uVar2 = FUN_003d5f90();
    bVar13 = 0;
    *(undefined1 *)(param_2 + 0x5d) = uVar2;
    if (iVar3 != -1) {
      pbVar11 = (byte *)FUN_00918200(iVar3);
      bVar13 = (*pbVar11 & 2) >> 1;
    }
    *(byte *)(param_2 + 0x5e) = bVar13;
    uVar2 = FUN_003d6080();
    *(undefined1 *)(param_2 + 0x5f) = uVar2;
    uVar2 = FUN_003d6340();
    *(undefined1 *)(param_2 + 0x60) = uVar2;
    *(undefined1 *)(param_2 + 0x61) = 0;
  }
  uVar4 = FUN_0010c3d0();
  if (uVar4 != 0xffffffff) {
    lVar7 = (ulong)(((uint)((int)uVar4 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar4 >> 0xd) * 0x40;
    lVar9 = *DAT_01a238a0;
    lVar15 = *(long *)(lVar9 + 0x10 + lVar7);
    iVar3 = *(int *)(lVar9 + 0x34 + lVar7);
    uVar12 = (ulong)((uVar4 & 0x1fff) * *(int *)(lVar9 + 0x30 + lVar7));
    uVar10 = *(ulong *)(lVar15 + 8 + uVar12);
    *(undefined4 *)(param_2 + 0x68) = 0;
    lVar9 = (lVar15 + uVar12) - ((long)iVar3 & uVar10);
    if (0 < *(int *)(extraout_RDX + 0x694 + lVar9)) {
      lVar15 = 0;
      do {
        local_48[0] = *(undefined4 *)(extraout_RDX + 0x698 + lVar9 + lVar15 * 4);
        iVar3 = FUN_0010d1e0(local_48);
        if (iVar3 != -1) {
          iVar5 = *(int *)(param_2 + 0x68);
          *(int *)(param_2 + 0x68) = iVar5 + 1;
          lVar7 = (long)iVar5 * 0x10;
          *(int *)(param_2 + 0x70 + lVar7) = iVar3;
          *(undefined8 *)(param_2 + 0x78 + lVar7) = extraout_RDX_00;
        }
        lVar15 = lVar15 + 1;
      } while ((int)lVar15 < *(int *)(lVar9 + 0x694 + extraout_RDX));
    }
  }
  FUN_00401180(param_2);
  lVar9 = FUN_003d7630();
  *(undefined4 *)(param_2 + 0x58) = *(undefined4 *)(lVar9 + 0x284c);
  *(undefined4 *)(param_2 + 0xf0) = 0;
  FUN_003e6f30(param_2);
  *(undefined4 *)(param_2 + 0x130) = 0;
  FUN_00404db0(param_2);
  *(undefined4 *)(param_2 + 0x44) = 0;
  *(undefined8 *)(param_2 + 0x3c) = 0;
  FUN_0040c220(param_2);
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

