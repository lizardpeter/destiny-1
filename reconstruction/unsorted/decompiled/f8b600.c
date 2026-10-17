
void FUN_00f8b600(long param_1,uint param_2,uint param_3,int param_4,long param_5)

{
  long lVar1;
  ulong uVar2;
  uint uVar3;
  
  if ((param_4 != 0) && (param_5 != 0)) {
    thunk_FUN_012aa7c6(*(long *)(param_1 + 8) +
                       (ulong)(param_2 * 0x642 + 0x4c0 + param_3 * 4 & 0xffff) * 4,param_5,
                       (ulong)(uint)(param_4 * 4) << 2);
    uVar3 = param_4 + param_3;
    if (param_3 < uVar3) {
      lVar1 = param_1 + (ulong)param_2 * 4;
      uVar2 = (ulong)param_3;
      do {
        *(byte *)((uVar2 >> 3) + 0xcd + lVar1) =
             *(byte *)((uVar2 >> 3) + 0xcd + lVar1) | (byte)(1 << ((byte)uVar2 & 7));
        uVar2 = (ulong)((int)uVar2 + 1);
        param_4 = param_4 + -1;
      } while (param_4 != 0);
    }
    param_3 = param_3 >> 5;
    uVar3 = uVar3 - 1 >> 5;
    if (param_3 <= uVar3) {
      do {
        *(byte *)((ulong)(param_3 >> 3) + 0x25 + param_1 + (ulong)param_2) =
             *(byte *)((ulong)(param_3 >> 3) + 0x25 + param_1 + (ulong)param_2) |
             (byte)(1 << ((byte)param_3 & 7));
        param_3 = param_3 + 1;
      } while (param_3 <= uVar3);
    }
  }
  return;
}

