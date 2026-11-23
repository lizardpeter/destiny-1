
void FUN_00644d00(long param_1)

{
  uint uVar1;
  long lVar2;
  long lVar3;
  long lVar4;
  int iVar5;
  ulong uVar6;
  long lVar7;
  uint uVar8;
  uint uVar9;
  
  lVar4 = DAT_02692228;
  uVar1 = *(uint *)(param_1 + 0x2c);
  uVar9 = (uVar1 & 0x1fff) * DAT_02692230;
  if ((*(int *)(param_1 + 0x80) != *(int *)(param_1 + 0x84)) || (*(int *)(param_1 + 0x84) != -1)) {
    iVar5 = FUN_00071f60(param_1 + 0x80);
    if (iVar5 != -1) {
      uVar8 = (int)*(uint *)(param_1 + 0x84) >> 0xd;
      lVar2 = *DAT_01a238a0;
      lVar7 = (ulong)((uVar8 >> 0x12 | 0x3ff) & uVar8) * 0x40;
      lVar3 = *(long *)(lVar2 + 0x10 + lVar7);
      uVar6 = (ulong)((*(uint *)(param_1 + 0x84) & 0x1fff) * *(int *)(lVar2 + 0x30 + lVar7));
      FUN_007427a0((lVar3 + uVar6) -
                   ((long)*(int *)(lVar2 + 0x34 + lVar7) & *(ulong *)(lVar3 + 8 + uVar6)),uVar1);
      *(undefined8 *)(param_1 + 0x80) = 0xffffffffffffffff;
      if (*(int *)(param_1 + 0x2c) != -1) {
        FUN_002d94f0(*(undefined4 *)(param_1 + 0x24));
      }
    }
  }
  if ((*(byte *)((ulong)uVar9 + 4 + lVar4) & 1) != 0) {
    return;
  }
  if (*(char *)(param_1 + 0x2a8) != '\0') {
    FUN_00338280((ulong)((*(uint *)(param_1 + 0x2c) & 0x1fff) * DAT_02692230) + DAT_02692228,1);
  }
  FUN_00648530(param_1);
  return;
}

