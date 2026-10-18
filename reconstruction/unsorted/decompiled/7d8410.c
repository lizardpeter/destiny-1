
void FUN_007d8410(long param_1)

{
  long lVar1;
  undefined *puVar2;
  char cVar3;
  undefined4 uVar4;
  long lVar5;
  long lVar6;
  long lVar7;
  long lVar8;
  uint uVar9;
  long lVar10;
  ulong uVar11;
  ulong uVar12;
  long lVar13;
  ulong uVar14;
  undefined4 uVar15;
  undefined8 extraout_XMM0_Qa;
  undefined1 auVar16 [16];
  undefined1 extraout_var [56];
  undefined1 local_ca0 [16];
  long local_c90;
  long local_c88;
  ulong local_c80;
  long local_c78;
  undefined4 local_c70;
  undefined1 local_c68;
  uint local_c60 [2];
  undefined2 local_c58 [8];
  long lStack_c48;
  uint auStack_c40 [4];
  long alStack_c30 [379];
  undefined4 local_54;
  int local_4c;
  long local_38;
  undefined1 auVar17 [64];
  
  lVar7 = DAT_026897f8;
  local_38 = *DAT_01a1f100;
  uVar9 = *(uint *)(param_1 + 4);
  uVar11 = (ulong)((uVar9 & 0x1fff) * DAT_02689800);
  uVar14 = (ulong)DAT_02689818;
  uVar12 = *(ulong *)(DAT_026897f8 + 8 + uVar11);
  lVar5 = FUN_002fcbd0();
  lVar6 = FUN_002fcb80(param_1);
  local_c60[0] = FUN_0006e750(&DAT_026df1d0);
  lVar1 = DAT_026df1d8;
  auVar17._8_56_ = extraout_var;
  auVar17._0_8_ = extraout_XMM0_Qa;
  if ((local_c60[0] != 0xffffffff) && (*(int *)(lVar5 + 0x20) != -1)) {
    uVar4 = *(undefined4 *)(((lVar7 + uVar11) - (uVar14 & uVar12)) + 0x2c);
    lVar7 = 8;
    do {
      *(undefined2 *)((long)local_c58 + lVar7) = 0xffff;
      lVar7 = lVar7 + 0x30;
    } while (lVar7 != 0xc08);
    local_54 = 0;
    local_4c = -1;
    uVar12 = (ulong)((local_c60[0] & 0x1fff) * DAT_026df1e0);
    *(undefined4 *)(DAT_026df1d8 + 8 + uVar12) = 0;
    auVar16._0_4_ = (float)*(int *)(lVar6 + 8);
    auVar16._4_12_ = auVar17._4_12_;
    uVar15 = thunk_FUN_005916e0(auVar16._0_8_);
    puVar2 = PTR_DAT_0191ab00;
    *(undefined4 *)(lVar1 + 0xc + uVar12) = uVar15;
    *(undefined4 *)(lVar1 + uVar12) = *(undefined4 *)(lVar5 + 0x20);
    *(uint *)(lVar1 + 4 + uVar12) = uVar9;
    FUN_0030e1d0(local_c58,uVar4,*(undefined4 *)puVar2,0);
    if (local_4c != -1) {
      do {
        local_c68 = 0;
        lVar13 = (long)local_4c;
        lVar7 = (&lStack_c48)[lVar13 * 6];
        lVar1 = *DAT_01a238a0;
        uVar9 = (int)*(uint *)(lVar7 + 0x20) >> 0xd;
        local_c78 = (long)*(int *)(lVar7 + 4);
        lVar10 = (ulong)((uVar9 >> 0x12 | 0x3ff) & uVar9) * 0x40;
        lVar8 = *(long *)(lVar1 + 0x10 + lVar10);
        uVar12 = (ulong)((*(uint *)(lVar7 + 0x20) & 0x1fff) * *(int *)(lVar1 + 0x30 + lVar10));
        local_c90 = (lVar8 + uVar12) -
                    ((long)*(int *)(lVar1 + 0x34 + lVar10) & *(ulong *)(lVar8 + 8 + uVar12));
        local_c88 = alStack_c30[lVar13 * 6] + local_c78;
        local_c70 = *(undefined4 *)(lVar7 + 0xc);
        local_c80 = (ulong)auStack_c40[lVar13 * 0xc];
        FUN_00353cf0(&local_c90,local_c60,0,*(undefined1 *)(lVar5 + 0x24));
        FUN_0030e7a0(local_c58);
      } while (local_4c != -1);
    }
    if (*(char *)(lVar5 + 0x24) != '\0') {
      FUN_0032bf90(local_ca0,uVar4);
      FUN_0032bfa0(local_ca0);
      cVar3 = FUN_0032bfd0(local_ca0);
      if (cVar3 != '\0') {
        do {
          uVar4 = FUN_00078d50(local_ca0);
          FUN_0030e1d0(local_c58,uVar4,*(undefined4 *)puVar2,0);
          while (local_4c != -1) {
            local_c68 = 0;
            lVar8 = (long)local_4c;
            lVar7 = (&lStack_c48)[lVar8 * 6];
            lVar1 = *DAT_01a238a0;
            uVar9 = (int)*(uint *)(lVar7 + 0x20) >> 0xd;
            local_c78 = (long)*(int *)(lVar7 + 4);
            lVar13 = (ulong)((uVar9 >> 0x12 | 0x3ff) & uVar9) * 0x40;
            lVar5 = *(long *)(lVar1 + 0x10 + lVar13);
            uVar12 = (ulong)((*(uint *)(lVar7 + 0x20) & 0x1fff) * *(int *)(lVar1 + 0x30 + lVar13));
            local_c90 = (lVar5 + uVar12) -
                        ((long)*(int *)(lVar1 + 0x34 + lVar13) & *(ulong *)(lVar5 + 8 + uVar12));
            local_c88 = alStack_c30[lVar8 * 6] + local_c78;
            local_c70 = *(undefined4 *)(lVar7 + 0xc);
            local_c80 = (ulong)auStack_c40[lVar8 * 0xc];
            uVar4 = FUN_00066dc0(local_ca0);
            FUN_00353cf0(&local_c90,local_c60,uVar4,1);
            FUN_0030e7a0(local_c58);
          }
          FUN_0032bfe0(local_ca0);
          cVar3 = FUN_0032bfd0(local_ca0);
        } while (cVar3 != '\0');
      }
    }
  }
  *(uint *)(lVar6 + 0x10) = local_c60[0];
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

