
void FUN_007d8820(undefined8 param_1)

{
  undefined4 *puVar1;
  long lVar2;
  undefined *puVar3;
  char cVar4;
  undefined4 uVar5;
  long lVar6;
  long lVar7;
  long lVar8;
  long lVar9;
  uint uVar10;
  long lVar11;
  ulong uVar12;
  undefined1 local_c98 [16];
  long local_c88;
  long local_c80;
  ulong local_c78;
  long local_c70;
  undefined4 local_c68;
  undefined1 local_c60;
  undefined2 local_c58 [8];
  long lStack_c48;
  uint auStack_c40 [4];
  long alStack_c30 [379];
  undefined4 local_54;
  int local_4c;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  lVar6 = FUN_002fcad0();
  lVar7 = FUN_002fcb80(param_1);
  puVar1 = (undefined4 *)(lVar7 + 0x10);
  if (*(int *)(lVar7 + 0x10) != -1) {
    uVar5 = *(undefined4 *)(lVar6 + 0x2c);
    lVar6 = 8;
    do {
      *(undefined2 *)((long)local_c58 + lVar6) = 0xffff;
      lVar6 = lVar6 + 0x30;
    } while (lVar6 != 0xc08);
    local_54 = 0;
    local_4c = -1;
    lVar6 = FUN_002fcbd0(param_1);
    puVar3 = PTR_DAT_0191ab00;
    FUN_0030e1d0(local_c58,uVar5,*(undefined4 *)PTR_DAT_0191ab00,0);
    if (local_4c != -1) {
      do {
        local_c60 = 0;
        lVar8 = (long)local_4c;
        lVar7 = (&lStack_c48)[lVar8 * 6];
        lVar2 = *DAT_01a238a0;
        uVar10 = (int)*(uint *)(lVar7 + 0x20) >> 0xd;
        local_c70 = (long)*(int *)(lVar7 + 4);
        lVar11 = (ulong)((uVar10 >> 0x12 | 0x3ff) & uVar10) * 0x40;
        lVar9 = *(long *)(lVar2 + 0x10 + lVar11);
        uVar12 = (ulong)((*(uint *)(lVar7 + 0x20) & 0x1fff) * *(int *)(lVar2 + 0x30 + lVar11));
        local_c88 = (lVar9 + uVar12) -
                    ((long)*(int *)(lVar2 + 0x34 + lVar11) & *(ulong *)(lVar9 + 8 + uVar12));
        local_c80 = alStack_c30[lVar8 * 6] + local_c70;
        local_c68 = *(undefined4 *)(lVar7 + 0xc);
        local_c78 = (ulong)auStack_c40[lVar8 * 0xc];
        FUN_00353e40(&local_c88,puVar1);
        FUN_0030e7a0(local_c58);
      } while (local_4c != -1);
    }
    if (*(char *)(lVar6 + 0x24) != '\0') {
      FUN_0032bf90(local_c98,uVar5);
      FUN_0032bfa0(local_c98);
      cVar4 = FUN_0032bfd0(local_c98);
      if (cVar4 != '\0') {
        do {
          uVar5 = FUN_00078d50(local_c98);
          FUN_0030e1d0(local_c58,uVar5,*(undefined4 *)puVar3,0);
          while (local_4c != -1) {
            local_c60 = 0;
            lVar9 = (long)local_4c;
            lVar6 = (&lStack_c48)[lVar9 * 6];
            lVar7 = *DAT_01a238a0;
            uVar10 = (int)*(uint *)(lVar6 + 0x20) >> 0xd;
            local_c70 = (long)*(int *)(lVar6 + 4);
            lVar8 = (ulong)((uVar10 >> 0x12 | 0x3ff) & uVar10) * 0x40;
            lVar2 = *(long *)(lVar7 + 0x10 + lVar8);
            uVar12 = (ulong)((*(uint *)(lVar6 + 0x20) & 0x1fff) * *(int *)(lVar7 + 0x30 + lVar8));
            local_c88 = (lVar2 + uVar12) -
                        ((long)*(int *)(lVar7 + 0x34 + lVar8) & *(ulong *)(lVar2 + 8 + uVar12));
            local_c80 = alStack_c30[lVar9 * 6] + local_c70;
            local_c68 = *(undefined4 *)(lVar6 + 0xc);
            local_c78 = (ulong)auStack_c40[lVar9 * 0xc];
            FUN_00353e40(&local_c88,puVar1);
            FUN_0030e7a0(local_c58);
          }
          FUN_0032bfe0(local_c98);
          cVar4 = FUN_0032bfd0(local_c98);
        } while (cVar4 != '\0');
      }
    }
    FUN_0006ecb0(&DAT_026df1d0,*puVar1);
  }
  *puVar1 = 0xffffffff;
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

