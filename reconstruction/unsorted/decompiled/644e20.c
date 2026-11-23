
void FUN_00644e20(long param_1)

{
  long lVar1;
  long lVar2;
  int iVar3;
  ulong uVar4;
  long lVar5;
  uint uVar6;
  
  iVar3 = FUN_00071f60(param_1 + 0x80);
  if (iVar3 != -1) {
    uVar6 = (int)*(uint *)(param_1 + 0x84) >> 0xd;
    lVar5 = (ulong)((uVar6 >> 0x12 | 0x3ff) & uVar6) * 0x40;
    lVar1 = *DAT_01a238a0;
    lVar2 = *(long *)(lVar1 + 0x10 + lVar5);
    uVar4 = (ulong)((*(uint *)(param_1 + 0x84) & 0x1fff) * *(int *)(lVar1 + 0x30 + lVar5));
    FUN_007427a0((lVar2 + uVar4) -
                 ((long)*(int *)(lVar1 + 0x34 + lVar5) & *(ulong *)(lVar2 + 8 + uVar4)),
                 *(undefined4 *)(param_1 + 0x2c));
    *(undefined8 *)(param_1 + 0x80) = 0xffffffffffffffff;
    if (*(int *)(param_1 + 0x2c) != -1) {
      FUN_002d94f0(*(undefined4 *)(param_1 + 0x24));
    }
  }
  FUN_0032e340(*(undefined4 *)(param_1 + 0x2c));
  return;
}

