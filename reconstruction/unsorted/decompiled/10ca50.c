
ulong FUN_0010ca50(void)

{
  long lVar1;
  long lVar2;
  char cVar3;
  uint uVar4;
  ulong uVar5;
  long lVar6;
  long extraout_RDX;
  ulong uVar7;
  uint local_38 [2];
  long local_30;
  long local_20;
  
  local_20 = *DAT_01a1f100;
  cVar3 = FUN_001072c0(0x10,0,local_38);
  uVar7 = 0xffffffff;
  if ((cVar3 != '\0') && (local_38[0] != 0xffffffff)) {
    lVar6 = (ulong)(((uint)((int)local_38[0] >> 0xd) >> 0x12 | 0x3ff) & (int)local_38[0] >> 0xd) *
            0x40;
    lVar1 = *DAT_01a238a0;
    lVar2 = *(long *)(lVar1 + 0x10 + lVar6);
    uVar5 = (ulong)((local_38[0] & 0x1fff) * *(int *)(lVar1 + 0x30 + lVar6));
    uVar4 = FUN_0011e260(((lVar2 + uVar5) -
                         ((long)*(int *)(lVar1 + 0x34 + lVar6) & *(ulong *)(lVar2 + 8 + uVar5))) +
                         local_30);
    if (uVar4 != 0xffffffff) {
      lVar6 = (ulong)(((uint)((int)uVar4 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar4 >> 0xd) * 0x40;
      lVar1 = *DAT_01a238a0;
      lVar2 = *(long *)(lVar1 + 0x10 + lVar6);
      uVar7 = (ulong)((uVar4 & 0x1fff) * *(int *)(lVar1 + 0x30 + lVar6));
      uVar4 = FUN_0011f0a0(((lVar2 + uVar7) -
                           ((long)*(int *)(lVar1 + 0x34 + lVar6) & *(ulong *)(lVar2 + 8 + uVar7))) +
                           extraout_RDX);
      uVar7 = (ulong)uVar4;
    }
  }
  if (*DAT_01a1f100 == local_20) {
    return uVar7;
  }
  uVar7 = thunk_FUN_012aa7f6();
  return uVar7;
}

