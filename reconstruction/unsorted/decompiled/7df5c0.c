
void FUN_007df5c0(long param_1,ulong param_2,uint param_3,long param_4)

{
  ushort uVar1;
  ulong uVar3;
  bool bVar4;
  uint uVar2;
  
  if ((short)param_3 != 0) {
    bVar4 = false;
    uVar3 = param_2 & 0xffff;
    uVar2 = param_3 & 0xffff;
    do {
      uVar3 = uVar3 & 0xffff;
      if (param_4 != *(long *)(&DAT_00002378 + uVar3 * 8 + param_1)) {
        *(long *)(&DAT_00002378 + uVar3 * 8 + param_1) = param_4;
        bVar4 = true;
      }
      param_4 = param_4 + 1;
      uVar3 = (ulong)((int)uVar3 + 1);
      uVar1 = (short)uVar2 - 1;
      uVar2 = (uint)uVar1;
    } while (uVar1 != 0);
    if (bVar4) {
      FUN_00f8b410(*(long *)(param_1 + 0x50) + 0xc0,3,param_2 & 0xffff,param_3);
      return;
    }
  }
  return;
}

