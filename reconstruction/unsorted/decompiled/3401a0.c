
void FUN_003401a0(long param_1,long param_2)

{
  long *plVar1;
  undefined4 *puVar2;
  uint uVar3;
  char cVar4;
  int iVar5;
  undefined8 uVar6;
  long lVar7;
  ulong uVar8;
  long lVar9;
  uint uVar10;
  long lVar11;
  long lVar12;
  long lVar13;
  long local_d0;
  long alStack_c8 [18];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  (&DAT_000014d8)[param_1] = 1;
  lVar7 = 0;
  do {
    uVar3 = *(uint *)(param_2 + lVar7 * 4);
    *(uint *)(&DAT_000014dc + lVar7 * 8 + param_1) = uVar3;
    *(undefined4 *)(&DAT_000014e0 + lVar7 * 8 + param_1) = 0xffffffff;
    lVar11 = (ulong)(((uint)((int)uVar3 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar3 >> 0xd) * 0x40;
    lVar12 = lVar7 + 1;
    lVar13 = *DAT_01a238a0;
    lVar9 = *(long *)(lVar13 + 0x10 + lVar11);
    uVar8 = (ulong)((uVar3 & 0x1fff) * *(int *)(lVar13 + 0x30 + lVar11));
    alStack_c8[lVar7] =
         (lVar9 + uVar8) - ((long)*(int *)(lVar13 + 0x34 + lVar11) & *(ulong *)(lVar9 + 8 + uVar8));
    lVar7 = lVar12;
  } while ((int)lVar12 != 0x12);
  uVar6 = FUN_00346d20();
  lVar7 = (long)*(int *)(param_1 + 8);
  if (0 < lVar7) {
    local_d0 = 0;
    do {
      lVar7 = lVar7 + -1;
      uVar3 = *(uint *)(param_1 + 0xc + lVar7 * 0x14);
      uVar10 = (int)uVar3 >> 0xd;
      lVar12 = *DAT_01a238a0;
      lVar9 = (ulong)((uVar10 >> 0x12 | 0x3ff) & uVar10) * 0x40;
      lVar13 = *(long *)(lVar12 + 0x10 + lVar9);
      uVar8 = (ulong)((uVar3 & 0x1fff) * *(int *)(lVar12 + 0x30 + lVar9));
      lVar12 = (lVar13 + uVar8) -
               ((long)*(int *)(lVar12 + 0x34 + lVar9) & *(ulong *)(lVar13 + 8 + uVar8));
      if (0 < *(long *)(lVar12 + 8)) {
        plVar1 = (long *)(lVar12 + 0x10);
        lVar13 = 0;
        do {
          lVar9 = *plVar1;
          if ((*(int *)((long)plVar1 + lVar13 * 8 + lVar9 + 0x14) != -1) &&
             (iVar5 = FUN_00349c10(uVar6), iVar5 == 2)) {
            puVar2 = (undefined4 *)((long)plVar1 + lVar13 * 8 + lVar9 + 0x14);
            lVar9 = FUN_0006de00(puVar2);
            if (lVar9 != local_d0) {
              lVar11 = 0;
              do {
                local_d0 = lVar9;
                if ((*(int *)(&DAT_000014e0 + lVar11 * 8 + param_1) == -1) &&
                   (cVar4 = FUN_000e8bd0(lVar9,alStack_c8[lVar11]), cVar4 != '\0')) {
                  *(undefined4 *)(&DAT_000014e0 + lVar11 * 8 + param_1) = *puVar2;
                  break;
                }
                lVar11 = lVar11 + 1;
              } while ((int)lVar11 < 0x12);
            }
          }
          lVar13 = lVar13 + 1;
        } while (lVar13 < *(long *)(lVar12 + 8));
      }
    } while (0 < (int)lVar7);
  }
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

