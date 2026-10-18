
void FUN_001195f0(long *param_1)

{
  short sVar1;
  uint uVar2;
  long lVar3;
  char cVar4;
  ushort uVar5;
  uint uVar6;
  int iVar7;
  ulong uVar8;
  long *plVar9;
  uint uVar10;
  long lVar11;
  long lVar12;
  long lVar13;
  long lVar14;
  uint local_70 [2];
  long local_68;
  long local_58;
  short local_50;
  int iStack_4c;
  bool local_48;
  undefined8 local_40;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  local_40 = 0;
  if (*param_1 != 0) {
    uVar6 = FUN_00303410(param_1);
    local_58 = 0;
    uVar5 = FUN_00107550(0);
    lVar14 = 0;
    local_58 = 0;
    if (uVar5 != 0) {
      local_58 = *(long *)(&DAT_01ad5030 + (ulong)uVar5 * DAT_01ad5010 + DAT_01ad5000);
    }
    local_48 = false;
    if (uVar6 == 0xffffffff) {
      uVar10 = 0xffffffff;
    }
    else {
      uVar8 = (ulong)((uVar6 & 0x1fff) * DAT_02689590);
      lVar14 = DAT_02689588 + uVar8;
      uVar10 = *(uint *)(DAT_02689588 + 0x50 + uVar8);
      if (uVar10 == 0xffffffff) {
        uVar10 = 0xffffffff;
      }
      else {
        FUN_00301c70(lVar14);
      }
    }
    uVar5 = FUN_00107550(0);
    local_58 = 0;
    if (uVar5 != 0) {
      local_58 = *(long *)(&DAT_01ad5030 + (ulong)uVar5 * DAT_01ad5010 + DAT_01ad5000);
    }
    iStack_4c = 0xc;
    local_50 = 0;
    local_48 = 0 < *(short *)(local_58 + 0x2bd4e);
    if (0 < *(short *)(local_58 + 0x2bd4e)) {
      if (uVar6 == 0xffffffff) {
        do {
          cVar4 = FUN_0100cb80(&local_58,local_70);
          if (cVar4 != '\0') {
            lVar11 = (ulong)(((uint)((int)local_70[0] >> 0xd) >> 0x12 | 0x3ff) &
                            (int)local_70[0] >> 0xd) * 0x40;
            lVar3 = *DAT_01a238a0;
            plVar9 = (long *)0x0;
            lVar13 = *(long *)(lVar3 + 0x10 + lVar11);
            uVar8 = (ulong)((local_70[0] & 0x1fff) * *(int *)(lVar3 + 0x30 + lVar11));
            lVar13 = (lVar13 + uVar8) -
                     ((long)*(int *)(lVar3 + 0x34 + lVar11) & *(ulong *)(lVar13 + 8 + uVar8));
            uVar2 = *(uint *)(lVar13 + 0x208 + local_68);
            if (uVar2 != 0xffffffff) {
              lVar12 = (ulong)(((uint)((int)uVar2 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar2 >> 0xd) *
                       0x40;
              lVar11 = *(long *)(lVar3 + 0x10 + lVar12);
              uVar8 = (ulong)((uVar2 & 0x1fff) * *(int *)(lVar3 + 0x30 + lVar12));
              plVar9 = (long *)(((lVar11 + uVar8) -
                                ((long)*(int *)(lVar3 + 0x34 + lVar12) &
                                *(ulong *)(lVar11 + 8 + uVar8))) +
                               *(long *)(local_68 + 0x210 + lVar13));
            }
            if (*param_1 == *plVar9) {
              FUN_001294c0(lVar13 + local_68);
            }
          }
          local_50 = local_50 + 1;
          if (local_50 < 0) {
            local_48 = false;
            break;
          }
          if (iStack_4c == -1) {
            sVar1 = *(short *)(local_58 + 0x510);
          }
          else {
            sVar1 = *(short *)(local_58 + 0x2bd1e + (long)iStack_4c * 4);
          }
          local_48 = local_50 < sVar1;
        } while (local_50 < sVar1);
      }
      else {
        do {
          cVar4 = FUN_0100cb80(&local_58,local_70);
          if (cVar4 != '\0') {
            lVar11 = (ulong)(((uint)((int)local_70[0] >> 0xd) >> 0x12 | 0x3ff) &
                            (int)local_70[0] >> 0xd) * 0x40;
            lVar3 = *DAT_01a238a0;
            plVar9 = (long *)0x0;
            lVar13 = *(long *)(lVar3 + 0x10 + lVar11);
            uVar8 = (ulong)((local_70[0] & 0x1fff) * *(int *)(lVar3 + 0x30 + lVar11));
            lVar13 = (lVar13 + uVar8) -
                     ((long)*(int *)(lVar3 + 0x34 + lVar11) & *(ulong *)(lVar13 + 8 + uVar8));
            uVar2 = *(uint *)(lVar13 + 0x208 + local_68);
            if (uVar2 != 0xffffffff) {
              lVar12 = (ulong)(((uint)((int)uVar2 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar2 >> 0xd) *
                       0x40;
              lVar11 = *(long *)(lVar3 + 0x10 + lVar12);
              uVar8 = (ulong)((uVar2 & 0x1fff) * *(int *)(lVar3 + 0x30 + lVar12));
              plVar9 = (long *)(((lVar11 + uVar8) -
                                ((long)*(int *)(lVar3 + 0x34 + lVar12) &
                                *(ulong *)(lVar11 + 8 + uVar8))) +
                               *(long *)(local_68 + 0x210 + lVar13));
            }
            if (*param_1 == *plVar9) {
              lVar13 = lVar13 + local_68;
              iVar7 = FUN_00108470(lVar13);
              if ((iVar7 == 0) || (*(int *)(lVar14 + 0x50) == -1)) {
                FUN_00301c60(lVar14,local_70[0]);
              }
              FUN_001293f0(lVar13,uVar6);
            }
          }
          local_50 = local_50 + 1;
          if (local_50 < 0) {
            local_48 = false;
            break;
          }
          if (iStack_4c == -1) {
            sVar1 = *(short *)(local_58 + 0x510);
          }
          else {
            sVar1 = *(short *)(local_58 + 0x2bd1e + (long)iStack_4c * 4);
          }
          local_48 = local_50 < sVar1;
        } while (local_50 < sVar1);
      }
    }
    if (((uVar6 != 0xffffffff) && (uVar10 != 0xffffffff)) && (*(int *)(lVar14 + 0x50) == -1)) {
      lVar11 = (ulong)(((uint)((int)uVar10 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar10 >> 0xd) * 0x40;
      lVar3 = *DAT_01a238a0;
      plVar9 = (long *)0x0;
      lVar13 = *(long *)(lVar3 + 0x10 + lVar11);
      uVar8 = (ulong)((uVar10 & 0x1fff) * *(int *)(lVar3 + 0x30 + lVar11));
      lVar13 = (lVar13 + uVar8) -
               ((long)*(int *)(lVar3 + 0x34 + lVar11) & *(ulong *)(lVar13 + 8 + uVar8));
      uVar6 = *(uint *)(lVar13 + 0x208);
      if (uVar6 != 0xffffffff) {
        lVar12 = (ulong)(((uint)((int)uVar6 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar6 >> 0xd) * 0x40;
        lVar11 = *(long *)(lVar3 + 0x10 + lVar12);
        uVar8 = (ulong)((uVar6 & 0x1fff) * *(int *)(lVar3 + 0x30 + lVar12));
        plVar9 = (long *)(((lVar11 + uVar8) -
                          ((long)*(int *)(lVar3 + 0x34 + lVar12) & *(ulong *)(lVar11 + 8 + uVar8)))
                         + *(long *)(lVar13 + 0x210));
      }
      if (*param_1 == *plVar9) {
        FUN_00301c60(lVar14);
      }
    }
  }
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

