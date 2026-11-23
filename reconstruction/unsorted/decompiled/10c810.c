
ulong FUN_0010c810(void)

{
  long lVar1;
  char cVar2;
  ulong uVar3;
  ulong uVar4;
  long lVar5;
  long lVar6;
  uint local_28 [2];
  long local_20;
  long local_10;
  
  local_10 = *DAT_01a1f100;
  cVar2 = FUN_001072c0(0x10,0,local_28);
  uVar3 = 0xffffffff;
  if (cVar2 != '\0') {
    if (local_28[0] != 0xffffffff) {
      lVar6 = (ulong)(((uint)((int)local_28[0] >> 0xd) >> 0x12 | 0x3ff) & (int)local_28[0] >> 0xd) *
              0x40;
      lVar5 = *DAT_01a238a0;
      lVar1 = *(long *)(lVar5 + 0x10 + lVar6);
      uVar4 = (ulong)((local_28[0] & 0x1fff) * *(int *)(lVar5 + 0x30 + lVar6));
      lVar5 = (lVar1 + uVar4) -
              ((long)*(int *)(lVar5 + 0x34 + lVar6) & *(ulong *)(lVar1 + 8 + uVar4));
      if (local_20 + lVar5 != -0x1ac) {
        uVar3 = (ulong)(uint)(int)*(char *)(local_20 + 0x1ad + lVar5);
      }
    }
  }
  if (*DAT_01a1f100 == local_10) {
    return uVar3;
  }
  uVar3 = thunk_FUN_012aa7f6();
  return uVar3;
}

