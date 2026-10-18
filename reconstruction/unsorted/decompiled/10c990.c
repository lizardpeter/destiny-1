
ulong FUN_0010c990(void)

{
  long lVar1;
  char cVar2;
  ulong uVar3;
  long lVar4;
  long lVar5;
  uint uVar6;
  uint local_38 [2];
  long local_30;
  long local_20;
  
  local_20 = *DAT_01a1f100;
  cVar2 = FUN_001072c0(0x10,0,local_38);
  uVar6 = 0;
  if ((cVar2 != '\0') && (uVar6 = 0, local_38[0] != 0xffffffff)) {
    lVar5 = (ulong)(((uint)((int)local_38[0] >> 0xd) >> 0x12 | 0x3ff) & (int)local_38[0] >> 0xd) *
            0x40;
    lVar4 = *DAT_01a238a0;
    lVar1 = *(long *)(lVar4 + 0x10 + lVar5);
    uVar3 = (ulong)((local_38[0] & 0x1fff) * *(int *)(lVar4 + 0x30 + lVar5));
    lVar4 = (lVar1 + uVar3) - ((long)*(int *)(lVar4 + 0x34 + lVar5) & *(ulong *)(lVar1 + 8 + uVar3))
    ;
    if (local_30 + lVar4 != -0x1ac) {
      uVar6 = *(uint *)(local_30 + 0x670 + lVar4);
    }
  }
  if (*DAT_01a1f100 == local_20) {
    return (ulong)uVar6;
  }
  uVar3 = thunk_FUN_012aa7f6();
  return uVar3;
}

