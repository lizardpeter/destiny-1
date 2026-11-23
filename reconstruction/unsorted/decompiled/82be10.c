
void FUN_0082be10(long param_1,undefined4 param_2,long *param_3)

{
  long *plVar1;
  uint uVar2;
  long lVar3;
  long lVar4;
  long lVar5;
  undefined4 uVar6;
  ulong uVar7;
  undefined8 uVar8;
  long lVar9;
  long lVar10;
  
  uVar6 = FUN_007e2c90(param_2);
  if (0 < *param_3) {
    plVar1 = param_3 + 1;
    lVar10 = 0;
    do {
      lVar3 = *plVar1;
      uVar2 = *(uint *)((long)plVar1 + lVar10 * 8 + lVar3 + 0x14);
      if (uVar2 == 0xffffffff) {
        FUN_007def10(*(undefined8 *)(param_1 + 0x15c0),uVar6,
                     *(undefined4 *)((long)plVar1 + lVar10 * 8 + lVar3 + 0x10));
      }
      else {
        lVar9 = (ulong)(((uint)((int)uVar2 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar2 >> 0xd) * 0x40;
        lVar4 = *DAT_01a238a0;
        lVar5 = *(long *)(lVar4 + 0x10 + lVar9);
        uVar7 = (ulong)((uVar2 & 0x1fff) * *(int *)(lVar4 + 0x30 + lVar9));
        uVar8 = FUN_00057f80((lVar5 + uVar7) -
                             ((long)*(int *)(lVar4 + 0x34 + lVar9) & *(ulong *)(lVar5 + 8 + uVar7)))
        ;
        FUN_007de8c0(*(undefined8 *)(param_1 + 0x15c0),uVar6,
                     *(undefined4 *)((long)plVar1 + lVar10 * 8 + lVar3 + 0x10),uVar8);
      }
      lVar10 = lVar10 + 1;
    } while (lVar10 < *param_3);
  }
  return;
}

