
void FUN_001294c0(uint *param_1)

{
  long lVar1;
  long lVar2;
  char cVar3;
  ulong uVar4;
  long lVar5;
  uint uVar6;
  
  if (param_1[0x7c] != 0xffffffff) {
    param_1[0x7c] = 0xffffffff;
    if (((param_1[0x74] != 0) && (param_1[0x74] != 0xffffffff)) && (param_1[0x76] != 0xffffffff)) {
      uVar6 = (int)*param_1 >> 0xd;
      lVar5 = (ulong)((uVar6 >> 0x12 | 0x3ff) & uVar6) * 0x40;
      lVar1 = *DAT_01a238a0;
      lVar2 = *(long *)(lVar1 + 0x10 + lVar5);
      uVar4 = (ulong)((*param_1 & 0x1fff) * *(int *)(lVar1 + 0x30 + lVar5));
      cVar3 = FUN_00001f70(*(long *)(param_1 + 2) + 0x40 +
                           ((lVar2 + uVar4) -
                           ((long)*(int *)(lVar1 + 0x34 + lVar5) & *(ulong *)(lVar2 + 8 + uVar4))));
      if (cVar3 != '\0') {
        FUN_00352e30(param_1 + 0x74);
      }
      FUN_000f8210();
      return;
    }
  }
  return;
}

