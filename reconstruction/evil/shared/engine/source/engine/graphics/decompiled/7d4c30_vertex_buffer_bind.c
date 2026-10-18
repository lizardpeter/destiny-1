
undefined8 FUN_007d4c30(uint param_1,long param_2)

{
  long lVar1;
  long lVar2;
  undefined8 uVar3;
  long lVar4;
  uint *puVar5;
  ulong uVar6;
  
  uVar3 = 0;
  if ((param_1 != 0xffffffff) && (param_2 != 0)) {
    lVar4 = (ulong)(((uint)((int)param_1 >> 0xd) >> 0x12 | 0x3ff) & (int)param_1 >> 0xd) * 0x40;
    lVar1 = *DAT_01a238a0;
    lVar2 = *(long *)(lVar1 + 0x10 + lVar4);
    uVar6 = (ulong)((param_1 & 0x1fff) * *(int *)(lVar1 + 0x30 + lVar4));
    puVar5 = (uint *)((lVar2 + uVar6) -
                     ((long)*(int *)(lVar1 + 0x34 + lVar4) & *(ulong *)(lVar2 + 8 + uVar6)));
    FUN_007d64a0(puVar5);
    FUN_00162b80(puVar5,(ulong)*puVar5 / (ulong)puVar5[1],(ulong)*puVar5 % (ulong)puVar5[1]);
    uVar3 = 1;
  }
  return uVar3;
}

