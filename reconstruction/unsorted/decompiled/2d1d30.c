
void FUN_002d1d30(long param_1,int param_2)

{
  uint *puVar1;
  long *plVar2;
  long lVar3;
  bool bVar4;
  char cVar5;
  undefined4 uVar6;
  uint uVar7;
  int iVar8;
  long lVar9;
  undefined8 uVar10;
  int iVar11;
  ulong uVar12;
  int *piVar13;
  long lVar14;
  ulong uVar15;
  uint uVar16;
  long lVar17;
  uint local_ac;
  undefined8 local_a8;
  long lStack_a0;
  undefined4 local_98;
  undefined1 local_90 [32];
  long local_70;
  int local_68;
  uint uStack_64;
  undefined1 local_60 [24];
  long *local_48;
  long local_40;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  local_ac = 2;
  uVar16 = 0;
  if (((param_2 != 1) && (*(char *)(param_1 + 0x62b) != '\0')) &&
     (local_ac = *(int *)(param_1 + 0x610) + 1, uVar16 = local_ac, 1 < *(int *)(param_1 + 0x610))) {
    local_ac = 0;
    uVar16 = local_ac;
  }
  do {
    puVar1 = (uint *)(param_1 + 0x614 + (long)((int)uVar16 >> 5) * 4);
    *puVar1 = *puVar1 | 1 << ((byte)uVar16 & 0x1f);
    local_68 = 0;
    plVar2 = *(long **)(param_1 + 0x10);
    uVar10 = *(undefined8 *)(*(long *)(*plVar2 + 8) + 0x10);
    local_70 = param_1 + 0x10;
    uStack_64 = uVar16;
    uVar6 = FUN_0006f140(plVar2);
    FUN_0008f550(local_60,uVar10,uVar6);
    local_40 = *plVar2;
    if (*(int *)(local_70 + 0x5e8) <= (int)uStack_64) {
      uStack_64 = 0;
    }
    local_48 = plVar2;
    if (*(char *)(local_70 + 0x5f8) != '\0') {
      FUN_01030630();
    }
    while( true ) {
      if (uStack_64 == 0xffffffff) {
        iVar8 = *(int *)(local_70 + 8);
        iVar11 = 0;
      }
      else {
        iVar11 = 0;
        iVar8 = 0;
        if (uStack_64 < *(uint *)(local_70 + 0x5e8)) {
          iVar11 = *(int *)(local_70 + 0x5ec + (long)(int)uStack_64 * 4);
          if ((int)uStack_64 < (int)(*(uint *)(local_70 + 0x5e8) - 1)) {
            piVar13 = (int *)(local_70 + 0x5ec + (long)(int)(uStack_64 + 1) * 4);
          }
          else {
            piVar13 = (int *)(local_70 + 8);
          }
          iVar8 = *piVar13 - iVar11;
        }
      }
      if (((local_68 < 0) || (iVar8 <= local_68)) || (local_68 + iVar11 == -1)) break;
      uVar7 = FUN_010304f0(&local_70);
      lVar17 = *DAT_01a238a0;
      lVar9 = (ulong)(((uint)((int)uVar7 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar7 >> 0xd) * 0x40;
      lVar3 = *(long *)(lVar17 + 0x10 + lVar9);
      iVar8 = *(int *)(lVar17 + 0x34 + lVar9);
      uVar15 = (ulong)((uVar7 & 0x1fff) * *(int *)(lVar17 + 0x30 + lVar9));
      uVar12 = *(ulong *)(lVar3 + 8 + uVar15);
      FUN_002cebf0(local_90);
      lVar17 = (lVar3 + uVar15) - ((long)iVar8 & uVar12);
      *(undefined1 *)(lVar17 + 0x67) = 0;
      cVar5 = FUN_002cec30(local_90,lVar17);
      if (cVar5 != '\0') {
        lStack_a0 = 0;
        local_a8 = 0xffffffff;
        local_98 = 0xffffffff;
        FUN_002cf080(local_90,&local_a8);
        if ((uint)local_a8 != -1) {
          iVar8 = FUN_001d4990(*(undefined4 *)(lVar17 + 8));
          uVar10 = FUN_002cfca0(lVar17,iVar8);
          lVar14 = (ulong)(((uint)((int)(uint)local_a8 >> 0xd) >> 0x12 | 0x3ff) &
                          (int)(uint)local_a8 >> 0xd) * 0x40;
          lVar3 = *DAT_01a238a0;
          lVar9 = *(long *)(lVar3 + 0x10 + lVar14);
          uVar12 = (ulong)(((uint)local_a8 & 0x1fff) * *(int *)(lVar3 + 0x30 + lVar14));
          thunk_FUN_012aa7c6(uVar10,((lVar9 + uVar12) -
                                    ((long)*(int *)(lVar3 + 0x34 + lVar14) &
                                    *(ulong *)(lVar9 + 8 + uVar12))) + lStack_a0,(long)iVar8);
          *(undefined1 *)(lVar17 + 0x67) = 1;
        }
      }
      local_68 = local_68 + 1;
    }
    bVar4 = (int)uVar16 < (int)local_ac;
    uVar16 = uVar16 + 1;
  } while (bVar4);
  *(uint *)(param_1 + 0x610) = local_ac;
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

