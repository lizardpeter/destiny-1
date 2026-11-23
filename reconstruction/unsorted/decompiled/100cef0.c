
long FUN_0100cef0(long *param_1)

{
  int iVar1;
  long lVar2;
  long lVar3;
  bool bVar4;
  bool bVar5;
  char cVar6;
  ulong uVar7;
  long lVar8;
  short sVar9;
  long lVar10;
  uint uVar11;
  int *piVar12;
  int iVar13;
  long lVar14;
  int iVar15;
  long lVar16;
  short sVar17;
  long lVar18;
  ulong in_R11;
  undefined8 local_38;
  long lStack_30;
  undefined8 local_28;
  long local_20;
  
  local_20 = *DAT_01a1f100;
  local_38 = 0;
  lStack_30 = 0;
  local_28 = 0;
  cVar6 = FUN_0100cce0(param_1,&local_38);
  if (cVar6 != '\0') {
    lVar10 = (ulong)(((uint)((int)(uint)local_38 >> 0xd) >> 0x12 | 0x3ff) &
                    (int)(uint)local_38 >> 0xd) * 0x40;
    lVar8 = *DAT_01a238a0;
    lVar16 = *(long *)(lVar8 + 0x10 + lVar10);
    uVar7 = (ulong)(((uint)local_38 & 0x1fff) * *(int *)(lVar8 + 0x30 + lVar10));
    lVar16 = (lVar16 + uVar7) -
             ((long)*(int *)(lVar8 + 0x34 + lVar10) & *(ulong *)(lVar16 + 8 + uVar7));
    lVar8 = lVar16 + lStack_30;
    if (lVar8 != 0) {
      uVar11 = (int)*(uint *)(lVar16 + lStack_30) >> 0xd;
      lVar14 = (ulong)((uVar11 >> 0x12 | 0x3ff) & uVar11) * 0x40;
      lVar10 = *param_1;
      sVar17 = (short)param_1[1];
      lVar2 = *DAT_01a238a0;
      uVar7 = (ulong)((*(uint *)(lVar16 + lStack_30) & 0x1fff) * *(int *)(lVar2 + 0x30 + lVar14));
      lVar18 = (long)*(int *)((long)param_1 + 0xc);
      lVar3 = *(long *)(lVar2 + 0x10 + lVar14);
      sVar9 = sVar17;
      if ((lVar18 != -1) && (sVar9 = -1, sVar17 < *(short *)(lVar10 + 0x2bd1e + lVar18 * 4))) {
        sVar9 = *(short *)(lVar10 + 0x2a51c +
                          ((long)*(short *)(lVar10 + 0x2bd1c + lVar18 * 4) + (long)sVar17) * 2);
      }
      sVar17 = -1;
      if (0 < *(int *)(lVar10 + 8)) {
        iVar15 = (int)sVar9;
        piVar12 = (int *)(lVar10 + 0x10);
        bVar4 = false;
        iVar13 = 0;
        do {
          sVar9 = (short)in_R11;
          if (bVar4) break;
          iVar1 = *piVar12;
          bVar5 = bVar4;
          if (iVar1 <= iVar15) {
            in_R11 = in_R11 & 0xffffffff;
            if (iVar15 < iVar1 + piVar12[-1]) {
              in_R11 = (ulong)(uint)(iVar15 - iVar1);
            }
            bVar5 = true;
            if (iVar1 + piVar12[-1] <= iVar15) {
              bVar5 = bVar4;
            }
          }
          bVar4 = bVar5;
          sVar9 = (short)in_R11;
          piVar12 = piVar12 + 5;
          iVar13 = iVar13 + 1;
        } while (iVar13 < *(int *)(lVar10 + 8));
        if (bVar4) {
          sVar17 = sVar9;
        }
      }
      if (*(short *)(*(long *)(lVar16 + 8 + lStack_30) + 0x22 +
                    ((lVar3 + uVar7) -
                    ((long)*(int *)(lVar2 + 0x34 + lVar14) & *(ulong *)(lVar3 + 8 + uVar7)))) !=
          sVar17) {
        lVar8 = 0;
      }
      if (*DAT_01a1f100 == local_20) {
        return lVar8;
      }
      goto LAB_0100d099;
    }
  }
  if (*DAT_01a1f100 == local_20) {
    return 0;
  }
LAB_0100d099:
  lVar8 = thunk_FUN_012aa7f6();
  return lVar8;
}

