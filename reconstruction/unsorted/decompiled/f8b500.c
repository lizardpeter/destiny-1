
void FUN_00f8b500(long param_1,uint param_2,uint param_3,int param_4,long param_5)

{
  uint uVar1;
  long lVar2;
  ulong uVar3;
  uint uVar4;
  
  if ((param_4 != 0) && (param_5 != 0)) {
    thunk_FUN_012aa7c6(*(long *)(param_1 + 8) +
                       (ulong)(param_2 * 0x642 + 0x540 + param_3 * 4 & 0xffff) * 4,param_5,
                       (ulong)(uint)(param_4 * 4) << 2);
    uVar4 = param_4 + param_3;
    if (param_3 < uVar4) {
      lVar2 = (ulong)param_2 * 3 + param_1;
      uVar3 = (ulong)param_3;
      do {
        *(byte *)((uVar3 >> 3) + 0xe9 + lVar2) =
             *(byte *)((uVar3 >> 3) + 0xe9 + lVar2) | (byte)(1 << ((byte)uVar3 & 7));
        uVar3 = (ulong)((int)uVar3 + 1);
        param_4 = param_4 + -1;
      } while (param_4 != 0);
    }
    uVar3 = (ulong)param_3 / 0x14;
    uVar4 = uVar4 - 1;
    if (param_3 / 0x14 <= uVar4 / 0x14) {
      do {
        *(byte *)((uVar3 >> 3) + 0x2c + param_1 + (ulong)param_2) =
             *(byte *)((uVar3 >> 3) + 0x2c + param_1 + (ulong)param_2) |
             (byte)(1 << ((byte)uVar3 & 7));
        uVar1 = (int)uVar3 + 1;
        uVar3 = (ulong)uVar1;
      } while (uVar1 <= uVar4 / 0x14);
    }
  }
  return;
}

