
void FUN_007d9410(uint param_1,undefined4 param_2,char param_3)

{
  byte bVar1;
  long lVar2;
  long lVar3;
  undefined *puVar4;
  char cVar5;
  undefined4 uVar6;
  int iVar7;
  long lVar8;
  ulong uVar9;
  uint uVar10;
  long lVar11;
  long lVar12;
  int *piVar13;
  int iVar14;
  undefined1 local_d68 [16];
  long local_d58;
  long local_d50;
  ulong local_d48;
  long local_d40;
  undefined4 local_d38;
  undefined1 local_d30;
  undefined1 local_d28 [16];
  long local_d18;
  long local_d10;
  long local_d00;
  undefined4 local_cf8;
  undefined1 local_cf0;
  undefined1 local_ce8 [16];
  uint local_cd8;
  uint local_cd0;
  long local_cc8;
  undefined4 local_cc0;
  char local_cb8 [4];
  undefined1 local_cb4 [4];
  char local_cb0;
  undefined1 local_cac [4];
  char local_ca8;
  undefined1 local_ca4 [4];
  char local_ca0;
  undefined1 local_c9c [4];
  byte local_c98 [4];
  undefined1 local_c94 [4];
  byte local_c90;
  undefined1 local_c8c [4];
  byte local_c88;
  undefined1 local_c84 [4];
  byte local_c80;
  undefined1 local_c7c [4];
  byte local_c78 [4];
  int local_c74 [7];
  undefined2 local_c58 [8];
  long lStack_c48;
  uint auStack_c40 [4];
  long alStack_c30 [379];
  undefined4 local_54;
  int local_4c;
  long local_38;
  
  puVar4 = PTR_DAT_0191ab00;
  local_38 = *DAT_01a1f100;
  lVar8 = 8;
  do {
    *(undefined2 *)((long)local_c58 + lVar8) = 0xffff;
    lVar8 = lVar8 + 0x30;
  } while (lVar8 != 0xc08);
  local_54 = 0;
  local_4c = -1;
  if (param_3 == '\0') {
    FUN_0032bf90(local_d68,param_2);
    FUN_0032bfa0(local_d68);
    cVar5 = FUN_0032bfd0(local_d68);
    puVar4 = PTR_DAT_0191ab00;
    if (cVar5 != '\0') {
      do {
        uVar6 = FUN_00078d50(local_d68);
        FUN_0030e1d0(local_c58,uVar6,*(undefined4 *)puVar4,0);
        while (local_4c != -1) {
          local_d30 = 0;
          lVar11 = (long)local_4c;
          lVar8 = (&lStack_c48)[lVar11 * 6];
          lVar2 = *DAT_01a238a0;
          uVar10 = (int)*(uint *)(lVar8 + 0x20) >> 0xd;
          local_d40 = (long)*(int *)(lVar8 + 4);
          lVar12 = (ulong)((uVar10 >> 0x12 | 0x3ff) & uVar10) * 0x40;
          lVar3 = *(long *)(lVar2 + 0x10 + lVar12);
          uVar9 = (ulong)((*(uint *)(lVar8 + 0x20) & 0x1fff) * *(int *)(lVar2 + 0x30 + lVar12));
          local_d58 = (lVar3 + uVar9) -
                      ((long)*(int *)(lVar2 + 0x34 + lVar12) & *(ulong *)(lVar3 + 8 + uVar9));
          local_d50 = alStack_c30[lVar11 * 6] + local_d40;
          local_d38 = *(undefined4 *)(lVar8 + 0xc);
          local_d48 = (ulong)auStack_c40[lVar11 * 0xc];
          FUN_00353610(&local_d58,local_c98);
          bVar1 = local_c98[0];
          iVar14 = FUN_00066dc0(local_d68);
          if (iVar14 < (int)(uint)bVar1) {
            FUN_00353e40(&local_d58,local_c94);
          }
          bVar1 = local_c90;
          iVar14 = FUN_00066dc0(local_d68);
          if (iVar14 < (int)(uint)bVar1) {
            FUN_00353e40(&local_d58,local_c8c);
          }
          bVar1 = local_c88;
          iVar14 = FUN_00066dc0(local_d68);
          if (iVar14 < (int)(uint)bVar1) {
            FUN_00353e40(&local_d58,local_c84);
          }
          bVar1 = local_c80;
          iVar14 = FUN_00066dc0(local_d68);
          if (iVar14 < (int)(uint)bVar1) {
            FUN_00353e40(&local_d58,local_c7c);
          }
          FUN_0030e7a0(local_c58);
        }
        FUN_0032bfe0(local_d68);
        cVar5 = FUN_0032bfd0(local_d68);
      } while (cVar5 != '\0');
    }
    FUN_0030e1d0(local_c58,param_2,*(undefined4 *)PTR_DAT_0191ab00,0);
    if (local_4c != -1) {
      do {
        local_d30 = 0;
        lVar11 = (long)local_4c;
        lVar8 = (&lStack_c48)[lVar11 * 6];
        lVar2 = *DAT_01a238a0;
        uVar10 = (int)*(uint *)(lVar8 + 0x20) >> 0xd;
        local_d40 = (long)*(int *)(lVar8 + 4);
        lVar12 = (ulong)((uVar10 >> 0x12 | 0x3ff) & uVar10) * 0x40;
        lVar3 = *(long *)(lVar2 + 0x10 + lVar12);
        uVar9 = (ulong)((*(uint *)(lVar8 + 0x20) & 0x1fff) * *(int *)(lVar2 + 0x30 + lVar12));
        local_d58 = (lVar3 + uVar9) -
                    ((long)*(int *)(lVar2 + 0x34 + lVar12) & *(ulong *)(lVar3 + 8 + uVar9));
        local_d50 = alStack_c30[lVar11 * 6] + local_d40;
        local_d38 = *(undefined4 *)(lVar8 + 0xc);
        local_d48 = (ulong)auStack_c40[lVar11 * 0xc];
        FUN_00353610(&local_d58,local_cb8);
        if (local_cb8[0] != '\0') {
          FUN_00353e40(&local_d58,local_cb4);
        }
        if (local_cb0 != '\0') {
          FUN_00353e40(&local_d58,local_cac);
        }
        if (local_ca8 != '\0') {
          FUN_00353e40(&local_d58,local_ca4);
        }
        if (local_ca0 != '\0') {
          FUN_00353e40(&local_d58,local_c9c);
        }
        FUN_0030e7a0(local_c58);
      } while (local_4c != -1);
    }
  }
  else {
    lVar8 = 0;
    cVar5 = FUN_00337fe0((ulong)((param_1 & 0x1fff) * DAT_02692230) + DAT_02692228,
                         *(undefined4 *)PTR_DAT_0191ab00,local_ce8,0);
    if (cVar5 != '\0') {
      local_cf0 = 0;
      lVar2 = *DAT_01a238a0;
      lVar11 = (ulong)(((uint)((int)local_cd8 >> 0xd) >> 0x12 | 0x3ff) & (int)local_cd8 >> 0xd) *
               0x40;
      lVar3 = *(long *)(lVar2 + 0x10 + lVar11);
      uVar9 = (ulong)((local_cd8 & 0x1fff) * *(int *)(lVar2 + 0x30 + lVar11));
      local_d18 = (lVar3 + uVar9) -
                  ((long)*(int *)(lVar2 + 0x34 + lVar11) & *(ulong *)(lVar3 + 8 + uVar9));
      lVar11 = (ulong)(((uint)((int)local_cd0 >> 0xd) >> 0x12 | 0x3ff) & (int)local_cd0 >> 0xd) *
               0x40;
      lVar3 = *(long *)(lVar2 + 0x10 + lVar11);
      uVar9 = (ulong)((local_cd0 & 0x1fff) * *(int *)(lVar2 + 0x30 + lVar11));
      local_d10 = ((lVar3 + uVar9) -
                  ((long)*(int *)(lVar2 + 0x34 + lVar11) & *(ulong *)(lVar3 + 8 + uVar9))) +
                  local_cc8;
      local_cf8 = local_cc0;
      local_d00 = local_cc8;
      FUN_00353610(&local_d18,local_c78);
      do {
        if ((local_c74[lVar8 * 2] != -1) && (local_c78[lVar8 * 8 + 1] != 0)) {
          FUN_0032bf90(local_d28,param_2);
          FUN_0032bfa0(local_d28);
          cVar5 = FUN_0032bfd0(local_d28);
          if (cVar5 != '\0') {
            do {
              uVar6 = FUN_00078d50(local_d28);
              FUN_0030e1d0(local_c58,uVar6,*(undefined4 *)puVar4,0);
              while (local_4c != -1) {
                local_d30 = 0;
                lVar11 = (long)local_4c;
                lVar8 = (&lStack_c48)[lVar11 * 6];
                uVar10 = (int)*(uint *)(lVar8 + 0x20) >> 0xd;
                lVar2 = *DAT_01a238a0;
                iVar14 = 0;
                local_d40 = (long)*(int *)(lVar8 + 4);
                lVar12 = (ulong)((uVar10 >> 0x12 | 0x3ff) & uVar10) * 0x40;
                lVar3 = *(long *)(lVar2 + 0x10 + lVar12);
                uVar9 = (ulong)((*(uint *)(lVar8 + 0x20) & 0x1fff) * *(int *)(lVar2 + 0x30 + lVar12)
                               );
                local_d58 = (lVar3 + uVar9) -
                            ((long)*(int *)(lVar2 + 0x34 + lVar12) & *(ulong *)(lVar3 + 8 + uVar9));
                local_d50 = alStack_c30[lVar11 * 6] + local_d40;
                local_d38 = *(undefined4 *)(lVar8 + 0xc);
                local_d48 = (ulong)auStack_c40[lVar11 * 0xc];
                piVar13 = local_c74;
                do {
                  if ((*piVar13 != -1) && (*(char *)((long)piVar13 + -3) != '\0')) {
                    bVar1 = *(byte *)(piVar13 + -1);
                    iVar7 = FUN_00066dc0(local_d28);
                    iVar7 = FUN_00353cf0(&local_d58,piVar13,bVar1 + 1 + iVar7);
                    if (iVar7 == -1) break;
                  }
                  piVar13 = piVar13 + 2;
                  iVar14 = iVar14 + 1;
                } while (iVar14 < 4);
                FUN_0030e7a0(local_c58);
              }
              FUN_0032bfe0(local_d28);
              cVar5 = FUN_0032bfd0(local_d28);
            } while (cVar5 != '\0');
          }
          FUN_0030e1d0(local_c58,param_2,*(undefined4 *)puVar4,0);
          if (local_4c != -1) {
            do {
              local_d30 = 0;
              lVar11 = (long)local_4c;
              lVar8 = (&lStack_c48)[lVar11 * 6];
              uVar10 = (int)*(uint *)(lVar8 + 0x20) >> 0xd;
              lVar2 = *DAT_01a238a0;
              iVar14 = 0;
              local_d40 = (long)*(int *)(lVar8 + 4);
              lVar12 = (ulong)((uVar10 >> 0x12 | 0x3ff) & uVar10) * 0x40;
              lVar3 = *(long *)(lVar2 + 0x10 + lVar12);
              uVar9 = (ulong)((*(uint *)(lVar8 + 0x20) & 0x1fff) * *(int *)(lVar2 + 0x30 + lVar12));
              local_d58 = (lVar3 + uVar9) -
                          ((long)*(int *)(lVar2 + 0x34 + lVar12) & *(ulong *)(lVar3 + 8 + uVar9));
              local_d50 = alStack_c30[lVar11 * 6] + local_d40;
              local_d38 = *(undefined4 *)(lVar8 + 0xc);
              local_d48 = (ulong)auStack_c40[lVar11 * 0xc];
              piVar13 = local_c74;
              do {
                if (((*piVar13 != -1) && (*(char *)((long)piVar13 + -3) != '\0')) &&
                   (iVar7 = FUN_00353cf0(&local_d58,piVar13,*(byte *)(piVar13 + -1) + 1,1),
                   iVar7 == -1)) break;
                piVar13 = piVar13 + 2;
                iVar14 = iVar14 + 1;
              } while (iVar14 < 4);
              FUN_0030e7a0(local_c58);
            } while (local_4c != -1);
          }
          break;
        }
        lVar8 = lVar8 + 1;
      } while ((int)lVar8 < 4);
    }
  }
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

