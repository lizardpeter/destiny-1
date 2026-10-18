
undefined8 FUN_007d4d40(uint param_1)

{
  long lVar1;
  long lVar2;
  long lVar3;
  ulong uVar4;
  
  lVar3 = (ulong)(((uint)((int)param_1 >> 0xd) >> 0x12 | 0x3ff) & (int)param_1 >> 0xd) * 0x40;
  lVar1 = *DAT_01a238a0;
  lVar2 = *(long *)(lVar1 + 0x10 + lVar3);
  uVar4 = (ulong)((param_1 & 0x1fff) * *(int *)(lVar1 + 0x30 + lVar3));
  FUN_007d61a0((lVar2 + uVar4) -
               ((long)*(int *)(lVar1 + 0x34 + lVar3) & *(ulong *)(lVar2 + 8 + uVar4)));
  return 1;
}

