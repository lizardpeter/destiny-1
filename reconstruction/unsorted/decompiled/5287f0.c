
long FUN_005287f0(void)

{
  long lVar1;
  char cVar2;
  ulong uVar3;
  long lVar4;
  byte bVar5;
  long lVar6;
  long lVar7;
  long lVar8;
  long *plVar9;
  
  if (DAT_026b0a4c == 0xffffffff) {
    lVar7 = 0;
  }
  else {
    lVar4 = (ulong)(((uint)((int)DAT_026b0a4c >> 0xd) >> 0x12 | 0x3ff) & (int)DAT_026b0a4c >> 0xd) *
            0x40;
    lVar8 = *DAT_01a238a0;
    lVar7 = -0x28;
    lVar6 = -1;
    lVar1 = *(long *)(lVar8 + 0x10 + lVar4);
    uVar3 = (ulong)((DAT_026b0a4c & 0x1fff) * *(int *)(lVar8 + 0x30 + lVar4));
    lVar8 = (lVar1 + uVar3) - ((long)*(int *)(lVar8 + 0x34 + lVar4) & *(ulong *)(lVar1 + 8 + uVar3))
    ;
    cVar2 = FUN_000ae550();
    if (cVar2 == '\0') {
      bVar5 = 2;
    }
    else {
      bVar5 = 4;
    }
    plVar9 = (long *)(lVar8 + 0x10);
    do {
      lVar6 = lVar6 + 1;
      if (*(long *)(lVar8 + 8) <= lVar6) {
        return 0;
      }
      lVar1 = lVar7 + 0x38;
      lVar7 = lVar7 + 0x38;
    } while ((*(byte *)((long)plVar9 + lVar1 + *plVar9) & bVar5) == 0);
    lVar7 = (long)plVar9 + lVar7 + *plVar9;
  }
  return lVar7;
}

