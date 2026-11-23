
bool FUN_003d5f90(void)

{
  long lVar1;
  long lVar2;
  char cVar3;
  undefined1 uVar4;
  int iVar5;
  int iVar6;
  ulong uVar7;
  undefined8 uVar8;
  long lVar9;
  uint local_30 [2];
  long local_28;
  long local_18;
  
  local_18 = *DAT_01a1f100;
  FUN_001072c0(0x22,0,local_30);
  cVar3 = FUN_001072c0(0x22,0,local_30);
  if ((cVar3 != '\0') && (local_30[0] != 0xffffffff)) {
    lVar9 = (ulong)(((uint)((int)local_30[0] >> 0xd) >> 0x12 | 0x3ff) & (int)local_30[0] >> 0xd) *
            0x40;
    lVar1 = *DAT_01a238a0;
    lVar2 = *(long *)(lVar1 + 0x10 + lVar9);
    uVar7 = (ulong)((local_30[0] & 0x1fff) * *(int *)(lVar1 + 0x30 + lVar9));
    cVar3 = FUN_0010bd40(((lVar2 + uVar7) -
                         ((long)*(int *)(lVar1 + 0x34 + lVar9) & *(ulong *)(lVar2 + 8 + uVar7))) +
                         local_28);
    if (cVar3 != '\0') {
      uVar8 = FUN_003430b0();
      iVar5 = FUN_00345620(uVar8);
      iVar6 = FUN_0010c690();
      if (*DAT_01a1f100 == local_18) {
        return iVar5 == iVar6;
      }
      goto LAB_003d606d;
    }
  }
  if (*DAT_01a1f100 == local_18) {
    return false;
  }
LAB_003d606d:
  uVar4 = thunk_FUN_012aa7f6();
  return (bool)uVar4;
}

