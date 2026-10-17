
ulong FUN_0010c430(void)

{
  long lVar1;
  long lVar2;
  char cVar3;
  ulong uVar4;
  char *pcVar5;
  long lVar6;
  uint local_28 [2];
  long local_20;
  long local_10;
  
  local_10 = *DAT_01a1f100;
  cVar3 = FUN_001072c0(0x10,0,local_28);
  if ((cVar3 != '\0') && (local_28[0] != 0xffffffff)) {
    lVar6 = (ulong)(((uint)((int)local_28[0] >> 0xd) >> 0x12 | 0x3ff) & (int)local_28[0] >> 0xd) *
            0x40;
    lVar1 = *DAT_01a238a0;
    lVar2 = *(long *)(lVar1 + 0x10 + lVar6);
    uVar4 = (ulong)((local_28[0] & 0x1fff) * *(int *)(lVar1 + 0x30 + lVar6));
    pcVar5 = (char *)(((lVar2 + uVar4) -
                      ((long)*(int *)(lVar1 + 0x34 + lVar6) & *(ulong *)(lVar2 + 8 + uVar4))) +
                      local_20 + 0x1ac);
    if (pcVar5 != (char *)0x0) {
      if (*DAT_01a1f100 == local_10) {
        return (ulong)(uint)(int)*pcVar5;
      }
      goto LAB_0010c4e4;
    }
  }
  if (*DAT_01a1f100 == local_10) {
    return 0xffffffff;
  }
LAB_0010c4e4:
  uVar4 = thunk_FUN_012aa7f6();
  return uVar4;
}

