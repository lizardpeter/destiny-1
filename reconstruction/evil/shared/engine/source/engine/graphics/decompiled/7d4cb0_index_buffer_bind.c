
undefined8 FUN_007d4cb0(uint param_1,long param_2)

{
  long lVar1;
  undefined8 uVar2;
  long lVar3;
  long lVar4;
  ulong uVar5;
  
  uVar2 = 0;
  if ((param_1 != 0xffffffff) && (param_2 != 0)) {
    lVar3 = (ulong)(((uint)((int)param_1 >> 0xd) >> 0x12 | 0x3ff) & (int)param_1 >> 0xd) * 0x40;
    lVar4 = *DAT_01a238a0;
    lVar1 = *(long *)(lVar4 + 0x10 + lVar3);
    uVar5 = (ulong)((param_1 & 0x1fff) * *(int *)(lVar4 + 0x30 + lVar3));
    lVar4 = (lVar1 + uVar5) - ((long)*(int *)(lVar4 + 0x34 + lVar3) & *(ulong *)(lVar1 + 8 + uVar5))
    ;
    FUN_007d27d0(lVar4,*(long *)(lVar4 + 8) / (long)(((ulong)*(byte *)(lVar4 + 1) & 1) * 2 + 2) &
                       0xffffffff,param_2,(*(byte *)(lVar4 + 1) & 1) * '\x02' + '\x02');
    uVar2 = 1;
  }
  return uVar2;
}

