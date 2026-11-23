
void FUN_00409370(long param_1)

{
  long lVar1;
  long lVar2;
  ulong uVar3;
  long lVar4;
  uint uVar5;
  long local_20 [3];
  
  local_20[2] = *DAT_01a1f100;
  uVar5 = (int)*(uint *)(param_1 + 0x208) >> 0xd;
  lVar4 = (ulong)((uVar5 >> 0x12 | 0x3ff) & uVar5) * 0x40;
  lVar1 = *DAT_01a238a0;
  lVar2 = *(long *)(lVar1 + 0x10 + lVar4);
  uVar3 = (ulong)((*(uint *)(param_1 + 0x208) & 0x1fff) * *(int *)(lVar1 + 0x30 + lVar4));
  local_20[0] = *(long *)(((lVar2 + uVar3) -
                          ((long)*(int *)(lVar1 + 0x34 + lVar4) & *(ulong *)(lVar2 + 8 + uVar3))) +
                         *(long *)(param_1 + 0x210));
  FUN_01040ba0(param_1 + 0x218);
  local_20[1] = 0;
  if (local_20[0] != 0) {
    FUN_001195f0(local_20);
  }
  if (*DAT_01a1f100 == local_20[2]) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

