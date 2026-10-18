
bool FUN_0010c750(void)

{
  long lVar1;
  long lVar2;
  char cVar3;
  undefined1 uVar4;
  ulong uVar5;
  char *pcVar6;
  long lVar7;
  int iVar8;
  uint local_28 [2];
  long local_20;
  long local_10;
  
  local_10 = *DAT_01a1f100;
  cVar3 = FUN_001072c0(0x10,0,local_28);
  iVar8 = -1;
  if (cVar3 != '\0') {
    if (local_28[0] != 0xffffffff) {
      lVar7 = (ulong)(((uint)((int)local_28[0] >> 0xd) >> 0x12 | 0x3ff) & (int)local_28[0] >> 0xd) *
              0x40;
      lVar1 = *DAT_01a238a0;
      lVar2 = *(long *)(lVar1 + 0x10 + lVar7);
      uVar5 = (ulong)((local_28[0] & 0x1fff) * *(int *)(lVar1 + 0x30 + lVar7));
      pcVar6 = (char *)(((lVar2 + uVar5) -
                        ((long)*(int *)(lVar1 + 0x34 + lVar7) & *(ulong *)(lVar2 + 8 + uVar5))) +
                        local_20 + 0x1ac);
      if (pcVar6 != (char *)0x0) {
        iVar8 = (int)*pcVar6;
      }
    }
  }
  if (*DAT_01a1f100 == local_10) {
    return iVar8 - 7U < 2 || iVar8 == 6;
  }
  uVar4 = thunk_FUN_012aa7f6();
  return (bool)uVar4;
}

