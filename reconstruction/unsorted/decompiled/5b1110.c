
bool FUN_005b1110(long param_1,undefined4 *param_2,char param_3)

{
  undefined1 *puVar1;
  uint uVar2;
  int iVar3;
  long lVar4;
  char cVar5;
  undefined1 uVar6;
  int iVar7;
  ulong uVar8;
  uint uVar9;
  long lVar10;
  long lVar11;
  long lVar12;
  long lVar13;
  undefined4 local_1120 [2];
  undefined4 local_1118 [2];
  uint local_1110 [2];
  undefined1 local_1108 [8];
  long local_1100;
  long local_10f8;
  undefined8 local_10f0;
  undefined8 local_10e8;
  undefined4 local_10e0;
  undefined1 local_10d8;
  undefined1 local_10d0 [3272];
  undefined1 auStack_408 [976];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  uVar2 = *(uint *)(param_1 + 0xb98);
  cVar5 = '\0';
  if (uVar2 != 0xffffffff) {
    local_10d8 = 0;
    uVar9 = (int)*(uint *)(param_1 + 0xb90) >> 0xd;
    lVar13 = *DAT_01a238a0;
    lVar10 = (ulong)(((uint)((int)uVar2 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar2 >> 0xd) * 0x40;
    lVar11 = (ulong)((uVar9 >> 0x12 | 0x3ff) & uVar9) * 0x40;
    lVar4 = *(long *)(lVar13 + 0x10 + lVar11);
    uVar8 = (ulong)((*(uint *)(param_1 + 0xb90) & 0x1fff) * *(int *)(lVar13 + 0x30 + lVar11));
    local_1100 = (lVar4 + uVar8) -
                 ((long)*(int *)(lVar13 + 0x34 + lVar11) & *(ulong *)(lVar4 + 8 + uVar8));
    lVar4 = *(long *)(lVar13 + 0x10 + lVar10);
    uVar8 = (ulong)((uVar2 & 0x1fff) * *(int *)(lVar13 + 0x30 + lVar10));
    local_10f8 = ((lVar4 + uVar8) -
                 ((long)*(int *)(lVar13 + 0x34 + lVar10) & *(ulong *)(lVar4 + 8 + uVar8))) +
                 *(long *)(param_1 + 0xba0);
    local_10e0 = *(undefined4 *)(param_1 + 0xba8);
    local_10f0 = *(undefined8 *)(param_1 + 0xb98);
    local_10e8 = *(undefined8 *)(param_1 + 0xba0);
    iVar7 = FUN_00913fa0(*(undefined4 *)(param_1 + 0x2c));
    if (iVar7 != -1) {
      lVar10 = FUN_0066ae60(iVar7);
      FUN_0104c3c0(local_10d0,lVar10);
      iVar3 = *(int *)(param_1 + 0x244);
      FUN_00325e30(&local_1100,local_1108,local_1110);
      lVar13 = *DAT_01a238a0;
      lVar12 = (long)iVar3 * 0x8c;
      puVar1 = auStack_408 + lVar12;
      lVar11 = (ulong)(((uint)((int)local_1110[0] >> 0xd) >> 0x12 | 0x3ff) &
                      (int)local_1110[0] >> 0xd) * 0x40;
      lVar4 = *(long *)(lVar13 + 0x10 + lVar11);
      uVar8 = (ulong)((local_1110[0] & 0x1fff) * *(int *)(lVar13 + 0x30 + lVar11));
      lVar13 = (lVar4 + uVar8) -
               ((long)*(int *)(lVar13 + 0x34 + lVar11) & *(ulong *)(lVar4 + 8 + uVar8));
      if (param_3 == '\0') {
        local_1120[0] = *param_2;
        cVar5 = FUN_00621090(lVar13,local_1120,puVar1);
      }
      else {
        local_1118[0] = *param_2;
        cVar5 = FUN_00621130(lVar13,local_1118,puVar1);
      }
      if (cVar5 != '\0') {
        FUN_005af820(param_1,lVar10 + 0xcc8 + lVar12,puVar1);
        FUN_0066ae90(iVar7,local_10d0);
      }
    }
  }
  if (*DAT_01a1f100 == local_38) {
    return cVar5 != '\0';
  }
  uVar6 = thunk_FUN_012aa7f6();
  return (bool)uVar6;
}

